#####################################################################################
#This code includes a callable function that takes a GeoTiff format file, and returns
#pixel count of that file, the could percentage, and the shadow percentage.
#The workflow is
#1. take blue, green, red, and NearInfrared bands as b1,b2,b3,b4.
#2. get the max&min image.  The max image means every pixel takes the max value from b1 through b4 at that location.  
#3. apply a 7x7 max filter on max image, and a 7x7 min filter on min image.
#4. extract the cloud from min image, extract shadow(shadow plus water) from max image, land from NearInfrared.
#Arbitary threshold eas used for extracting cloud and shadows.
#5. get shadow by using land as a mask on shadow plus water image.
#6. count total pixels, cloud, shadow pixels and calculate cloud_perc and shadow_perc
########################################################################################

import numpy as np
from scipy import ndimage
import sys
import rasterio
from rasterio.warp import transform_bounds
from rasterio.coords import BoundingBox

def Cloud_Shadow_Stats(in_name, bounds, cloud_val = 2500, shadow_val = 1500, land_val = 1000):
    """
    Input parameter:
    in_name    - The full path of a Geotiff format image. e.g., r"D:\test_image\planet.tif"
    bounds     - lat lon bounds to read data from
    cloud_val  - The threshold of cloud in the min image(for more about "min image", see #2 in the following); default = 2500;  
    shadow_val - The threshold of shadow in the max image; default = 1500;
    land_val   - The threshold of land in the Near Infrared image (band 4); defalt = 1000

    Output: cloud_perc, shadow_perc
    The output is a tuple with two float numbers:  
    cloud_perc  - cloud pixels percentage in that image, 
    shadow_perc - shadow percentage in that image.
    """

    src = rasterio.open(in_name)
    # bounds in the src crs projection
    # (left, bottom, right, top)
    transformed_bounds = BoundingBox(*transform_bounds("EPSG:4326", src.crs, *bounds))

    # calculate window to read from the input tiff
    window_min = src.index(transformed_bounds.left, transformed_bounds.bottom)
    window_max = src.index(transformed_bounds.right, transformed_bounds.top)
    start_row = min(window_min[0], window_max[0])
    stop_row = max(window_min[0], window_max[0])
    start_col = min(window_min[1], window_max[1])
    stop_col = max(window_min[1], window_max[1])
    actual_window = ((start_row, stop_row), (start_col, stop_col))

    # 1 open the tif, take 4 bands, and read them as arrays
    b1_array, b2_array, b3_array, b4_array = src.read(window = actual_window)

    # 2. make max image and min image from four input bands.
    # np.dstack() takes a list of bands and makes a band stack
    # np.amax() find the max along the axis, here 2 means the axis that penetrates through bands in each pixel.
    band_list = [b1_array,b2_array,b3_array,b4_array]
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
    cloud_array = np.where(min7x7_img > 3150, 1, 0).astype(np.int16)
    shadow_and_water_array = np.where(max7x7_img < 2000, 1, 0).astype(np.int16)
    land_array = np.where(b4_array > 1000, 1, 0).astype(np.int16)

    del max7x7_img, min7x7_img, b4_array

    # 5. get shadow by masking 
    shadow_array = np.where(land_array == 1, shadow_and_water_array, 0).astype(np.int16)

    # 6. Calculate Statistics
    grid_count = np.ma.count(shadow_array) # acutally count all pixels 
    cloud_count = np.count_nonzero(cloud_array ==1)
    shadow_count = np.count_nonzero(shadow_array ==1)

    cloud_perc = cloud_count / grid_count
    shadow_perc = shadow_count / grid_count

    del cloud_array, shadow_and_water_array, land_array, shadow_array
    return cloud_perc, shadow_perc
