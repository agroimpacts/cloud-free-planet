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

names = ['GH0688802', 'GH0690415', 'GH0692014'] 
# names = ['GH0688802']
source = "planet"
s3basepath = "s3://activemapper/sources/" + source + "/"
ec2basepath = "/home/lestes/geoserver/sources/" + source + "/"
awspath = "/home/lestes/.local/bin/aws"
#awspath = "/home/lestes/.local/bin/aws"
stretch = True
# false_color = False
comments = True
substring = "AnalyticMS_SR_win.tif"
stretch_name = "stretch.tif"
p1 = 0
p2 = 100

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

# Write out stretch image to GeoTiff
# def write_stretch_tif(array, imagevals, output_name, driver, 
#                       falsecolor = False):
#     driver = gdal.GetDriverByName(driver)
#     stretch_tif_out = driver.Create(output_name, imagevals["xsize"],
#                                     imagevals["xsize"], imagevals["nbands"],
#                                     gdal.GDT_Byte)
#     stretch_tif_out.SetGeoTransform(imagevals["geoinfo"])
#     stretch_tif_out.SetProjection(imagevals["srs"])
#     
#     if(imagevals["nbands"] == 4 & falsecolor == True): 
#         bandorder = [1, 2, 3, 0]
#     else: 
#         bandorder = range(imagevals["nbands"])
#         
#     for band in bandorder:
#         stretch_tif_out.GetRasterBand(band + 1).WriteArray(
#             array.astype(np.uint8))

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
    top = Element("coverage")
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

def create_wms_string():
    


geourl = "http://sandbox.crowdmapper.org"
userpw = ("admin", "bz0nCEmYoRGBBqmvmfq/zKMk")
workspace = "planet"
image_dir = "/home/lestes/geoserver/sources/planet/gh/images/"
image_name = "GH0688802_20180319_105120_1054_3B_stretch"

files = glob.glob(image_dir + "*stretch.tif")[0]

import requests
store = create_geoserver_datastore(geourl, userpw, workspace, image_name,
                                   image_dir)
# print(store)

image_path = image_dir + image_name + ".tif"
img = gdal.Open(image_path)
geoinfo = get_geo_info(img)
# print geoinfo
layer = create_geoserver_layer(geourl, userpw, workspace, image_name, image_dir,
                               geoinfo)

# https://sandbox.crowdmapper.org/geoserver/planet/wms?service=WMS&version=1.1.0&request=GetMap&layers=planet:GH0688802_20180319_105120_1054_3B_stretch&styles=&bbox=-0.6612499999999999,5.899749999999999,-0.65575,5.9052500000000006&width=767&height=768&srs=EPSG:4326&format=image%2Fpng

#s3paths = ["activemapper/sources/%s/%s" % (source, cntry) for cntry in cntrys]
for name in names:
    #s3path = s3basepath + name[0:2].lower() + "/images/ | grep " + name
    # s3path = s3basepath + name[0:2].lower() + "/images/"
    # ec2path = ec2basepath + name[0:2].lower() + "/images/"
    # merge_str1 =  "%s s3 cp %s %s " % (awspath, s3path, ec2path)
    # merge_str2 = "--recursive --exclude '*' --include %s*" % name
    # ps = subprocess.Popen(merge_str1 + merge_str2, shell = True,
    #                       stdin=subprocess.PIPE,
    #                       stdout = subprocess.PIPE,
    #                       stderr = subprocess.PIPE)
    # out, err = ps.communicate()
    # #print merge_str1 + merge_str2
    # image_name = out.split("/")[-1].strip()  # get full image name
    # image_base_name = re.sub("win.tif", "", image_name)
    # image_path = os.path.join(ec2path, image_name)
    paths_names = image_from_s3_to_ec2(s3basepath, ec2basepath, name, substring,
                                       awspath)

    if comments == True:
        print "Completed transfer of " + paths_names["image_name"]

    if(stretch == False):
        if comments == True:
            print "...no stretch applied"

    ## histogram stretch the image and write it out to disk
    if(stretch == True):
        # Get image bbox and epsg
        img = gdal.Open(paths_names["image_path"])
        imgvals = get_geo_info(img)

        # Stretch with skimage
        img_array_stretch = raster_stretch(paths_names["image_path"], p1, p2, 0)

        # Write out stretched array
        output_name = paths_names["image_name_root"] + stretch_name
        output_path = os.path.join(paths_names["ec2fullpath"], output_name)
        write_geotiff(output_path, img_array_stretch, imgvals["geoinfo"],
                      imgvals["srs"], gdal.GDT_UInt16)

        if comments == True:
            print "Completed writing " + output_name
 
