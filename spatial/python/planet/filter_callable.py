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
    """
    Takes a cloud mask array from the minimum filter and caluclates the
    eccentricity and are aof each object that was identified as cloud.
    Objects with eccentricity near 1 are more thin and linear (Roads or 
    strips of bright soil). Objects of small area are typically bright roofs. 
    Values selected by hand from visualizing growing season planet scenes over ghana.
    """

    # identify objects, label each with unique id
    possible_cloud_labels = measure.label(cloud_array_initial)

    # if the cloud_array really contains something, then do the following, otherwise return
    if np.count_nonzero(cloud_array) > 0:
        cloud_info = measure.regionprops(possible_cloud_labels)
        
        #iterate objects in the cloud_info
        j = 0
        cloud_labels = []
        while j < len(cloud_info):
            if int(cloud_info[j]['area'] )> object_size_thresh:
                if cloud_info[j]['eccentricity'] < eccentricity_thresh:
                    obj_array = np.where(possible_cloud_labels == j+1, 1, 0)
                    cloud_labels.apped(obj_array)
            j+=1
        # returns the union of all objects that made it through size and shape (eccentricity) filter
        return np.logical_or(*cloud_labels)

    else:
        return cloud_array_initial

def cloud_shadow_stats_config(in_name, bounds, config):
    return cloud_shadow_stats(in_name, bounds, int(config['cloud_val']), int(config['eccentricity_val']), int(config['area_val']))

def cloud_shadow_stats(in_name, bounds, cloud_val = 1500, eccentricity_val = .95, area_val = 200):
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

    # 3. make max 7x7 filtered max and min image
    max7x7_img = ndimage.maximum_filter(max_img, 7)
    min7x7_img = ndimage.minimum_filter(min_img, 7)

    del max_img, min_img

    # 4. extract cloud, shadow&water, land
    # The threshold here is based on Sitian and Tammy's test on 11 planet scenes.  It may not welly work for every AOI.
    # Apparently np.where() method will change or lost the datatype, so .astype(np.int16) is used to make sure the datatype is the same as original
    cloud_array_initial = np.where(min7x7_img > cloud_val, 1, 0).astype(np.int16)

    del max7x7_img, min7x7_img, b4_array
    
    # 5. Object oriented filtering to deal with buildings and roads misclassed as clouds
    cloud_array = size_shape_filter(cloud_array_initial, eccentricity_val, area_val)
    
    # 6. Calculate Statistics
    grid_count = np.ma.count(cloud_array) # acutally count all pixels 
    cloud_count = np.count_nonzero(cloud_array ==1)

    cloud_perc = cloud_count / grid_count

    del cloud_array
    return cloud_perc
