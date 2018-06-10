# test.py
#import glob
from osgeo import gdal, osr
from skimage import io, exposure
import numpy as np
import re
import sys, os
import subprocess
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import glob   
import requests

#from matplotlib import plt

def check_geoserver(ec2basepath, name, substring): 
    """
    Checks image by name to see if it is on already on the EC2 geoserver, to 
    determine if it needs to pulled in from s3.  
    :param ec2basepath: ec2 path up to first folder variable 
    :param name: Root name of image (here grid id which is always first)
    :param substring: Part of full image name to remove
    """
    
    ec2fullpath = ec2basepath + name[0:2].lower() + "/images/"
    image = glob.glob(ec2fullpath + name + "*" + substring)
    if len(image) == 1:  # assumes only one image matches name
        # print image
        out = os.path.basename(os.path.normpath(image[0]))
    elif len(image) > 1:
        print "More than 1 file name matches--shouldn't be a duplicate"
        return 
    else: 
        out = None

    return out

def image_from_s3_to_ec2(s3basepath, ec2basepath, name, substring, 
                         awspath = "aws"):
    """
    Uses aws cli cp to find an image on s3 bucket by grid id & move it to ec2 
    :param s3basepath: s3 bucket plus prefixes up to first directory variable
    :param ec2basepath: ec2 path up to first folder variable 
    :param name: Root name of image (here grid id which is always first)
    :param substring: Part of full image name to remove
    :param awspath: aws, with folder it is in case not in shell's path
    """
    s3fullpath = s3basepath + name[0:2].lower() + "/images/"
    ec2fullpath = ec2basepath + name[0:2].lower() + "/images/"
    str1 =  "%s s3 cp %s %s " % (awspath, s3fullpath, ec2fullpath)
    str2 = "--recursive --exclude '*' --include %s*" % name
    ps = subprocess.Popen(str1 + str2, shell = True,
                          stdin = subprocess.PIPE,
                          stdout = subprocess.PIPE, 
                          stderr = subprocess.PIPE)
    out, err = ps.communicate()
    image_name = out.split("/")[-1].strip()  # get full image name
    image_name_root = re.sub(substring, "", image_name)
    image_path = os.path.join(ec2fullpath, image_name)
    out_dict = {"image_name": image_name,  "image_name_root": image_name_root, 
                "image_path": image_path, "image_name_root": image_name_root,
                "ec2fullpath": ec2fullpath}
    return(out_dict)
    

def get_geo_info(image):
    """
    Collect geographic information from rasters
    :param image: Input raster
    """
    geoinfo = image.GetGeoTransform()
    minx = geoinfo[0]
    maxy = geoinfo[3]
    xsize = image.RasterXSize
    ysize = image.RasterYSize
    proj = osr.SpatialReference(wkt = image.GetProjection())
    epsg = proj.GetAttrValue('AUTHORITY', 1)  # epsg
    crs = image.GetProjectionRef()
    crs2 = proj.ExportToPrettyWkt()
    nbands = image.RasterCount
    NDvals = []
    for i in range(nbands): 
        band = img.GetRasterBand(i + 1)
        NDvals.append(band.GetNoDataValue())
    ext = [minx, minx + geoinfo[1] * image.RasterXSize, 
           maxy + geoinfo[5] * image.RasterYSize, maxy]
    out = {"xsize": xsize, "ysize": ysize, "epsg": epsg, #"proj": proj,  
           "nbands": nbands, "ext": ext, "geoinfo": geoinfo, "crs": crs, 
           "crs2": crs2, "NDvals": NDvals}       
    return out

def raster_stretch(image_path, p1, p2, NDV):
     """
     Use skimage to read in and stretch a gdal raster to specific percentiles
     :param image_path: Full path to raster with name
     :param p1: Lower percentile as a percent
     :param p2: Upper percentile as a percent
     :param NDV: No data value
     """
     array = io.imread(image_path)
     nodatamask = array == NDV
     array[nodatamask] = NDV
     P1, P2 = np.percentile(array, (p1, p2))
     stretch = exposure.rescale_intensity(array, in_range=(P1, P2))
     return stretch

def write_geotiff(Name, Array, GeoT, Projection, DataType, driver = "GTiff", 
                  NDV = -1):
    """
    Write a numpy array to a single or multiband geotiff. Note that this is 
    designed for arrays that are produced by scikit image (specifically 
    rescale_intensity), so the band dimension is last (see Array argument). 
    Code adapted from here: https://bit.ly/2LsFXHC
    :param Name: Output name including path
    :param Array: Input numpy array, with [x, y, z] arrangement
    :param GeoT: Information resulting from gdal.GetGeoTransform()
    :param Projection: Result of gdal.GetProjectionRef()
    :param DataType: One of the gdal data types, e.g. gdal.GDT_UInt16
    :param driver: Defaults to "GTiff"
    :param NDV: No data value, defaults to 0. 
    """
    Array[np.isnan(Array)] = NDV
    driver = gdal.GetDriverByName(driver)
    raster = driver.Create(Name, 
                           Array.shape[1],  # x dimension 
                           Array.shape[0],  # y dimension
                           Array.shape[2], # note band position
                           DataType)
    raster.SetGeoTransform(GeoT)
    raster.SetProjection(Projection)
    for i in range(Array.shape[2]):
        image = Array[:,:,i]
        raster.GetRasterBand(i + 1).WriteArray(image)
        raster.GetRasterBand(i + 1).SetNoDataValue(NDV)
    raster.FlushCache()
    return Name

    
def create_geoserver_datastore(geourl, userpw, workspace, image_name, 
                               image_dir):
    """
    Create geoserver geotiff datastore, using requests library
    :param geourl: url of geoserver 
    :param userpw: geoserver user name and password as an array
    :param workspace: relevant workspace
    :param image_name: Extensionless name of image from which to make store 
    :param image_dir: Directory of image from which to fetch image
    """

    url1 = "%s:8080/geoserver/rest/workspaces/%s" % (geourl, workspace)
    url2 = url1 + "/coveragestores?configure=all"
    
    image_path = image_dir + image_name + ".tif"

    # xml payload
    top = Element("coverageStore")
    nm = SubElement(top, "name")
    nm.text = image_name
    wkspace = SubElement(top, "workspace")
    wkspace.text = workspace
    enabled = SubElement(top, "enabled")
    enabled.text = "true"
    typ = SubElement(top, "type")
    typ.text = "GeoTIFF"
    urlstr = SubElement(top, "url")
    urlstr.text = image_path
    payload = tostring(top)

    # store_str = "<coverageStore><name>%s</name>" % (image_name)
    # workspace_str = "<workspace>%s</workspace>" % (workspace)
    # opt_str = "<enabled>true</enabled><type>GeoTIFF</type>"
    # image_path_str = "<url>%s</url></coverageStore>" % (image_path)
    # payload = store_str + workspace_str + opt_str + image_path_str
    # print payload

    headers = {'content-type': 'text/xml'}
    # print url2
    # print (user, pwd)
    r = requests.post(url2, auth = userpw, data = payload,
                      headers = headers)
    return(r)

def create_geoserver_layer(geourl, userpw, workspace, image_name, image_dir, 
                           geoinfo): 
    """
    Create geoserver geotiff layer, using requests library
    :param geourl: url of geoserver 
    :param userpw: geoserver user name and password as an array
    :param workspace: relevant workspace
    :param image_name: Extensionless name of image from which to make store 
    :param image_dir: Directory of image from which to fetch image
    :param geoinfo: Output of get_geo_info()
    """

    # url
    url1 = "%s:8080/geoserver/rest/workspaces/%s" % (geourl, workspace)
    url2 = "%s/coveragestores/%s/coverages" % (url1, image_name)
  
    g = geoinfo  # rename geoinfo
    
    # payload
    top = Element("coverage")
    nm = SubElement(top, "name")
    nm.text = image_name
    title = SubElement(top, "title")
    title.text = image_name
    natcrs = SubElement(top, "nativeCRS")
    natcrs.text = g["crs"]
    srs = SubElement(top, "srs")
    srs.text = "EPSG:" + g["epsg"]
    ll = SubElement(top, "latLongBoundingBox")
    llxmin = SubElement(ll, "minx")
    llxmin.text = str(g["ext"][0])
    llxmax = SubElement(ll, "maxx")
    llxmax.text = str(g["ext"][1])
    llymin = SubElement(ll, "miny")
    llymin.text = str(g["ext"][2])
    llymax = SubElement(ll, "maxy")
    llymax.text = str(g["ext"][3])
    payload = tostring(top)
    
    # create and post request
    headers = {'content-type': 'text/xml'}
    r = requests.post(url2, auth = userpw, data = payload,
                      headers = headers)
    
    return(r)
