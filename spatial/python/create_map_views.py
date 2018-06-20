# test.py
#import glob
from osgeo import gdal, osr
from skimage import io, exposure
import numpy as np
import re
import sys, os
import subprocess
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
    srs = image.GetProjectionRef()
    srs2 = proj.ExportToPrettyWkt()
    nbands = image.RasterCount
    NDvals = []
    for i in range(nbands): 
        band = img.GetRasterBand(i + 1)
        NDvals.append(band.GetNoDataValue())
    ext = [minx, minx + geoinfo[1] * image.RasterXSize, 
           maxy + geoinfo[5] * image.RasterYSize, maxy]
    out = {"xsize": xsize, "ysize": ysize, "epsg": epsg, #"proj": proj,  
           "nbands": nbands, "ext": ext, "geoinfo": geoinfo, "srs": srs, 
           "srs2": srs2, "NDvals": NDvals}       
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

