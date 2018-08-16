#####################################################################################
# This code includes a callable function that takes a GeoTiff format file, and returns
# pixel count of that file, the could percentage, and the shadow percentage.
# The workflow is
# 1. take blue, green, red, and NearInfrared bands as b1,b2,b3,b4.
# 2. get the max&min image.  The max image means every pixel takes the max value from b1 through b4 at that location.  
# 3. apply a 7x7 max filter on max image, and a 7x7 min filter on min image.
# 4. extract the cloud from min image, extract shadow(shadow plus water) from max image, land from NearInfrared.
# Arbitary threshold eas used for extracting cloud and shadows.
# 5. get shadow by using land as a mask on shadow plus water image.
# 6. count total pixels, cloud, shadow pixels and calculate cloud_perc and shadow_perc
########################################################################################

from geo_utils import GeoUtils

import numpy as np
from scipy import ndimage
from skimage import measure
import sys
import rasterio
from rasterio.warp import transform_bounds
from rasterio.coords import BoundingBox
import configparser

# returns nodata percentage
def nodata_stats(in_name, bounds):
    src = rasterio.open(in_name)
    nodata = src.nodata

    # bounds in the src crs projection
    # (left, bottom, right, top)
    transformed_bounds = BoundingBox(*transform_bounds("EPSG:4326", src.crs, *bounds))

    # calculate window to read from the input tiff
    actual_window = GeoUtils.bounds_to_windows(transformed_bounds, src)

    bands = src.read(window = actual_window)
    
    return sum([np.count_nonzero(band == nodata) for band in bands]) / src.count

def size_shape_filter(cloud_array_initial, cloud_reflectance_thresh = 1500, object_size_thresh = 200, eccentricity_thresh=.95):

    # if the cloud_array really contains something, then do the following, otherwise return
    if np.count_nonzero(cloud_array_initial) > 0:
        
        # identify objects, label each with unique id
        possible_cloud_labels = measure.label(cloud_array_initial)
        # get metrics
        cloud_info = measure.regionprops(possible_cloud_labels)
        
        #iterate objects in the cloud_info
        j = 0
        cloud_labels = []
        while j < len(cloud_info):
            if int(cloud_info[j]['area'] )> object_size_thresh:
                if cloud_info[j]['eccentricity'] < eccentricity_thresh:
                    obj_array = np.where(possible_cloud_labels == j+1, 1, 0)
                    cloud_labels.append(obj_array)
            j+=1
        # check if there are any labels identified as having clouds left
        
        if len(cloud_labels) > 1:
            return np.logical_or(*cloud_labels)
        elif len(cloud_labels) == 1:
            return cloud_labels[0]
        else:
            return np.zeros(cloud_array_initial.shape)

    else:
        return np.zeros(cloud_array_initial.shape)

def cloud_shadow_stats_config(in_name, bounds, config):
    return cloud_shadow_stats(in_name, bounds, int(config['cloud_val']), int(config['eccentricity_val']), int(config['area_val']))

def cloud_shadow_stats(in_name, bounds, cloud_val = 1500):
    """
    Input parameter:
    in_name    - The full path of a Geotiff format image. e.g., r"D:\test_image\planet.tif"
    bounds     - lat lon bounds to read data from
    cloud_val  - The threshold of cloud in the min image(for more about "min image", see #2 in the following);  
    Output: cloud_perc
    The output is a tuple with two float numbers:  
    cloud_perc  - cloud pixels percentage in that image, 
    """

    src = rasterio.open(in_name)

    # bounds in the src crs projection
    # (left, bottom, right, top)
    transformed_bounds = BoundingBox(*transform_bounds("EPSG:4326", src.crs, *bounds))

    # calculate window to read from the input tiff
    actual_window = GeoUtils.bounds_to_windows(transformed_bounds, src)

    # 1 open the tif, take 4 bands, and read them as arrays
    b1_array, b2_array, b3_array, b4_array = src.read(window = actual_window)

    # 2. make max image and min image from four input bands.
    # np.dstack() takes a list of bands and makes a band stack
    # np.amax() find the max along the axis, here 2 means the axis that penetrates through bands in each pixel.
    band_list = [b1_array ,b2_array, b3_array, b4_array]
    stacked = np.dstack(band_list)
    max_img = np.amax(stacked,2)
    min_img = np.amin(stacked,2)

    del b1_array, b2_array, b3_array, band_list

    del max_img, min_img

    # 4. extract cloud, shadow&water, land
    # The threshold here is based on Sitian and Tammy's test on 11 planet scenes.  It may not welly work for every AOI.
    # Apparently np.where() method will change or lost the datatype, so .astype(np.int16) is used to make sure the datatype is the same as original
    cloud_array_initial = np.where(min_img > cloud_val, 1, 0).astype(np.int16)
    
    cloud_array = size_shape_filter(cloud_array_initial)
    
    # 6. Calculate Statistics
    grid_count = np.ma.count(cloud_array) # acutally count all pixels 
    cloud_count = np.count_nonzero(cloud_array ==1)

    cloud_perc = cloud_count / grid_count

    del cloud_array
    return cloud_perc