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
from scipy.signal import medfilt
from skimage import measure
import sys
import rasterio
from rasterio.warp import transform_bounds
from rasterio.coords import BoundingBox
import configparser
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format = '%(message)s', datefmt = '%m-%d %H:%M')

def nodata_stats_wrapped(in_name, bounds):
    try:
        return nodata_stats(in_name, bounds)
    except IOError:
        logger.exception('Error Encountered')
        logger.info("rasterio.IOError arised...")
        return 1

# returns nodata percentage
def nodata_stats(in_name, bounds):
    src = rasterio.open(in_name)
    nodata = src.nodata

    src_ext = GeoUtils.BoundingBox_to_extent(src.bounds)
    bounds_ext = GeoUtils.BoundingBox_to_extent(BoundingBox(*transform_bounds("EPSG:4326", src.crs, *bounds)))

    if not GeoUtils.extents_intersects(src_ext, bounds_ext):
        return 1

    # bounds in the src crs projection
    # (left, bottom, right, top)
    # double check that bounds belong to image
    transformed_bounds = GeoUtils.extent_to_BoundingBox(GeoUtils.extent_intersection(src_ext, bounds_ext))

    # calculate window to read from the input tiff
    actual_window = GeoUtils.bounds_to_windows(transformed_bounds, src)

    bands = src.read(window = actual_window)
    
    return sum([np.count_nonzero(band == nodata) for band in bands]) / src.count


def cloud_size_shape_filter(cloud_array_initial, object_size_thresh = 200, eccentricity_thresh=.95):

    # if the cloud_array really contains something, then do the following, otherwise return
    if np.count_nonzero(cloud_array_initial) > 0:
        
        # identify objects, label each with unique id
        possible_cloud_labels = measure.label(cloud_array_initial)
        # get metrics
        cloud_info = measure.regionprops(possible_cloud_labels, coordinates='rc')
        
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
            return np.logical_or.reduce(cloud_labels)
        elif len(cloud_labels) == 1:
            return cloud_labels[0]
        else:
            return np.zeros(cloud_array_initial.shape)

    else:
        return np.zeros(cloud_array_initial.shape)

def shadow_size_shape_filter(shadow_array_initial, object_size_thresh = 200, eccentricity_thresh=.95, peri_to_area_ratio = 0.3):

    # if the shadow_array really contains something, then do the following, otherwise return
    if np.count_nonzero(shadow_array_initial) > 0:
        
        # identify objects, label each with unique id
        possible_shadow_labels = measure.label(shadow_array_initial)
        # get metrics
        shadow_info = measure.regionprops(possible_shadow_labels, coordinates='rc')
        
        #iterate objects in the cloud_info
        j = 0
        shadow_labels = []
        while j < len(shadow_info):
            if int(shadow_info[j]['area'] )> object_size_thresh:
                if shadow_info[j]['eccentricity'] < eccentricity_thresh:
                    if shadow_info[j]['perimeter']/shadow_info[j]['area'] < peri_to_area_ratio:
                        obj_array = np.where(possible_shadow_labels == j+1, 1, 0).astype(np.int16)
                        shadow_labels.append(obj_array)
            j+=1
            
        # check if there are any labels identified as having shadows left
        if len(shadow_labels) > 1:
            return np.logical_or.reduce(shadow_labels)
        elif len(shadow_labels) == 1:
            return shadow_labels[0]
        else:
            return np.zeros(shadow_array_initial.shape)

    else:
        return np.zeros(shadow_array_initial.shape)
    
def initial_shadow_filter(stacked, shadow_reflectance_thresh = 1500, land_reflectance_thresh = 1000):
    max_img = np.amax(stacked,2)
    nir = stacked[:,:,-1]
    shadow_and_water_array = np.where(max_img < shadow_reflectance_thresh, 1, 0).astype(np.int16)
    land_array = np.where(nir > land_reflectance_thresh, 1, 0).astype(np.int16)
    shadow_array_initial = np.where(land_array == 1, shadow_and_water_array, 0).astype(np.int16)
    
    del nir, max_img
    return shadow_array_initial

def cloud_shadow_stats_config_wrapped(in_name, bounds, config):
    try:
        return cloud_shadow_stats_config(in_name, bounds, config)
    except IOError:
        logger.exception('Error Encountered')
        logger.warn("rasterio.IOError arised...")
        return 1, 1

def cloud_shadow_stats_config(in_name, bounds, config):
    return cloud_shadow_stats(in_name, bounds, int(config['cloud_val']), int(config['area_val']), float(config['eccentricity_val']), float(config['peri_to_area_val']), int(config['shadow_val']), int(config['land_val']))

def cloud_shadow_stats(in_name, cloud_val = 1500, object_size_thresh = 400, eccentricity_thresh = 0.95, peri_to_area_ratio = 0.3, shadow_reflectance_thresh = 1500, land_reflectance_thresh = 1000):
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

    # 1 open the tif, take 4 bands, and read them as arrays
    b1_array, b2_array, b3_array, b4_array = src.read()

    # 2. make max image and min image from four input bands.
    # np.dstack() takes a list of bands and makes a band stack
    # np.amax() find the max along the axis, here 2 means the axis that penetrates through bands in each pixel.
    band_list = [b1_array ,b2_array, b3_array, b4_array]
    stacked = np.dstack(band_list)
    min_img = np.amin(stacked,2)

    del b1_array, b2_array, b3_array, band_list

    # 4. extract cloud, shadow&water, land
    # The threshold here is based on Sitian and Tammy's test on 11 planet scenes.  It may not welly work for every AOI.
    # Apparently np.where() method will change or lost the datatype, so .astype(np.int16) is used to make sure the datatype is the same as original
    cloud_array_initial = np.where(min_img > cloud_val, 1, 0).astype(np.int16)
    shadow_array_initial = initial_shadow_filter(stacked, shadow_reflectance_thresh, land_reflectance_thresh)
    del min_img

    cloud_array = cloud_size_shape_filter(cloud_array_initial, object_size_thresh, eccentricity_thresh)
    shadow_array = shadow_size_shape_filter(shadow_array_initial, object_size_thresh, eccentricity_thresh, peri_to_area_ratio)
    # 6. Calculate Statistics
    grid_count = np.ma.count(cloud_array) # acutally count all pixels 
    cloud_count = np.count_nonzero(cloud_array == 1)
    shadow_count = np.count_nonzero(shadow_array == 1)
    cloud_perc = cloud_count / grid_count
    shadow_perc = shadow_count / grid_count
    print("Percentage of scene that is cloudy: " + str(cloud_perc), "Percentage of scene with shadows" + str(shadow_perc))
    return cloud_array, shadow_array

def cloud_stats_zhen(in_name, ci_thresh_one = .01, ci_coef_two = 1/7, med_kernel=5, object_size_thresh = 400, eccentricity_thresh = 0.90, peri_to_area_ratio = 0.3):
    
    """
    Input parameter:
    in_name    - The full path of a Geotiff format image. e.g., r"D:\test_image\planet.tif"
    bounds     - lat lon bounds to read data from
    cloud_thesh_one  - The threshold of cloud index one from Zhen et al. 2018 {0.01, 0.1, 1, 10, 100};
    ci_coef_two  - The coefficient for cloud index two from Zhen et al. 2018, it ranges from 0 to 1 and suggested values are {1/10, 1/9, 1/8, 1/7, 1/6, 1/5, 1/4, 1/3,1/2}; 
    Print Output: cloud_perc
    Return Output: cloud_array - cloud pixels (bool?)
    """

    src = rasterio.open(in_name)

    # 1 open the tif, take 4 bands, and read them as arrays
    b1_array, b2_array, b3_array, b4_array = src.read()

    # 2. compute index 1 and 2 and use conditional to create cloud mask
    
    ci_one_arr = (b4_array*3)/(b1_array+b2_array+b3_array)
    ci_two_arr = (b4_array+b1_array+b2_array+b3_array)/4
    # authors suggest range for coef of 
    ci_thresh_two = np.mean(ci_two_arr) + ci_coef_two*(np.max(ci_two_arr)-np.mean(ci_two_arr))
    cloud_array_initial = np.logical_or(np.less_equal(ci_one_arr-1, ci_thresh_one),
                  np.greater_equal(ci_two_arr, ci_thresh_two))
    
    cloud_array_initial = medfilt(cloud_array_initial, med_kernel)
    
    cloud_array = cloud_size_shape_filter(cloud_array_initial, object_size_thresh, eccentricity_thresh)
    
    # 6. Calculate Statistics
    grid_count = np.ma.count(cloud_array) # acutally count all pixels 
    cloud_count = np.count_nonzero(cloud_array == 1)
    #shadow_count = np.count_nonzero(shadow_array == 1)
    cloud_perc = cloud_count / grid_count
    #shadow_perc = shadow_count / grid_count
    print("Percentage of scene that is cloudy: " + str(cloud_perc))
    return cloud_array

def shadow_stats_zhen(in_name, cloud_mask, csi_coef_three = .5, csi_thresh_three = 1, object_size_thresh = 200, eccentricity_thresh = 0.95, peri_to_area_ratio = 0.3, shadow_reflectance_thresh = 1500, land_reflectance_thresh = 1000):
    """
    Input parameter:
    in_name    - The full path of a Geotiff format image. e.g., r"D:\test_image\planet.tif"
    bounds     - lat lon bounds to read data from
    cloud_thesh_one  - The threshold of cloud index one from Zhen et al. 2018;
    cloud_thesh_two  - The threshold of cloud index two from Zhen et al. 2018; 
    Output: cloud_perc
    The output is a tuple with two arrays:  
    cloud_array - cloud pixels (bool?), 
    shadow_array - shadow pixels (bool?)
    """

    src = rasterio.open(in_name)

    # 1 open the tif, take 4 bands, and read them as arrays
    b1_array, b2_array, b3_array, b4_array = src.read()

    # 2. compute index 1 and 2 and use conditional to create cloud mask
    
    csi_three_arr = b4_array
    csi_four_arr = b1_array
    
    csi_thresh_three = np.min(csi_three_arr) + csi_coef_three*(np.mean(csi_three_arr)-np.min(csi_three_arr))
    
    csi_thresh_four = np.min(csi_four_arr) + csi_coef_four*(np.mean(csi_four_arr)-np.min(csi_four_arr))
    
    shadow_array_initial = np.logical_and(np.less_equal(csi_three_arr, ci_thresh_three),
                  np.less_equal(csi_four_arr, csi_thresh_four))

    shadow_array = shadow_size_shape_filter(shadow_array_initial, object_size_thresh, eccentricity_thresh)

    # 6. Calculate Statistics
    grid_count = np.ma.count(shadow_array) # count all pixels 
    shadow_count = np.count_nonzero(shadow_array == 1)
    #shadow_count = np.count_nonzero(shadow_array == 1)
    shadow_perc = shadow_count / grid_count
    #shadow_perc = shadow_count / grid_count
    print("Percentage of scene that is shadowy: " + str(shadow_perc))
    return shadow_array

