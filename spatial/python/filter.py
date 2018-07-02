
import gdal
import numpy as np
from scipy import ndimage

def open_tif(img_path, band_num):
    """
    This function use gdal.open() to open a tif image, then return an image as numpy array.
    img_path - the path of a tif image
    band_num - the band index in a tif. It starts from 1.
    """
    bands = gdal.Open(img_path)
    #band1 = bands.GetRasterBand(band_num)
    
    return bands.ReadAsArray()

def maxmin_img(m,*args):
    """
    This function creates a maximum or minimum image, which each pixel takes the 
    max or minimum value at that position from the input bands.
    The purpose of this funciton is to help extract shadows and clouds, assuming 
    that the shadow's maximum reflectance is low, whereas the cloud's minimum 
    reflectance is still high.
    
    m     - specify either "max" or "min"
    *args - given any numbers of bands in numpy array format.
    """
    try:
        #bands_list = []
        #for arg in args:
        #    bands_list.append(arg)

        stacked = np.dstack(args)

        if m.lower()=="max":
            return np.amax(stacked,2)
        elif m.lower() =="min":
            return np.amin(stacked,2)
    except:
        return "Failed to make max or min image from input bands."


def reclass(img_array, cd, thd_val = None, thd_perc = None):
    """
    This function creates a boolin image depends on the given threshold.

    img_array - the input image as numpy array
    cd        - condition, either ">" or "<" the threshold
    thd_val   - the absolute threshold value.  If given, the thd_perc will be ignore
    thd_perc  - the threshold as a percentile to the image value range.

    """
    try:
        if thd_val is None:
            threshold = np.min(img_array) + thd_perc*(np.max(img_array)-np.min(img_array))
        else: 
            threshold = thd_val

        if cd == ">":
            bool_img = np.where(img_array > threshold, 1, 0)
        elif cd == "<":
            bool_img = np.where(img_array < threshold, 1, 0)

        bool_img  = bool_img.astype(np.int16)
        return bool_img
    except:
        return "Failed to reclass image."

def array_to_raster(img_array, out_name, model_ds_path,):
    model_ds = gdal.Open(model_ds_path)
    model_band = model_ds.GetRasterBand(1)
    gtiff_driver = gdal.GetDriverByName('GTiff')
    out_ds = gtiff_driver.Create(out_name, model_band.XSize, model_band.YSize, 1, model_band.DataType)
    out_ds.SetProjection(model_ds.GetProjection())
    out_ds.SetGeoTransform(model_ds.GetGeoTransform())

    out_band = out_ds.GetRasterBand(1)
    #out_band.WriteArray(max_image)
    out_band.WriteArray(img_array)
    del out_ds

def mask(img_array, mask_array):
    mask = np.ma.make_mask(mask_array)
    img_masked = np.where(mask == True, img_array, 0)
    img_masked = img_masked.astype(np.int16)
    return img_masked

def filter_(img, cd, filter_size):
    """
    #In the boolin cloud image, this filter out the fragment cloud pixels,by give kernel the minimum value within its 7x7 filter.
    #The filter size can be change to any odd.
    #https://docs.scipy.org/doc/scipy-1.1.0/reference/generated/scipy.ndimage.minimum_filter.html#scipy.ndimage.minimum_filter
    #filter_size -  e.g.: 7 means 7x7 in a two dimension array;
    """
    try:
        if cd.lower() =="min":
            filtered_img = ndimage.minimum_filter(img, filter_size)
        elif cd.lower() =="max":
            filtered_img = ndimage.maximum_filter(img, filter_size)
        filtered_img = filtered_img.astype(np.int16)
        return filtered_img
    except:
        return "Failed to filter the image."


#1. Import B,G,R, NIR as b1, b2, b3, b4

b1 = open_tif(r'D:\cloud_shadow_test_tif\20180314_095229_1042_3B_AnalyticMS_SR_b1.tif',1)
b2 = open_tif(r'D:\cloud_shadow_test_tif\20180314_095229_1042_3B_AnalyticMS_SR_b2.tif',1)
b3 = open_tif(r'D:\cloud_shadow_test_tif\20180314_095229_1042_3B_AnalyticMS_SR_b3.tif',1)
b4 = open_tif(r'D:\cloud_shadow_test_tif\20180314_095229_1042_3B_AnalyticMS_SR_b4.tif',1)



#2. Get max and min image
max_image = maxmin_img('max',b1,b2,b3,b4)
min_image = maxmin_img('min',b1,b2,b3,b4)
del b1,b2,b3 

#3. Make a land mask
land = reclass(b4,">",1000)

#4. apply filter to max and min image
max_image_7x7 = filter_(max_image,cd="max", filter_size = 7) #add 7x7 max filter to max_image (shadow)
min_image_7x7 = filter_(min_image,cd = "min", filter_size = 7) #add 7x7 min filter to min_image(cloud)

#5. get cloud and shadow image from max, imn image based on threshold.
#the shadow variable actually includes water
cloud = reclass(min_image_7x7,cd=">",thd_val = 4000 )
shadow = reclass(max_image_7x7,cd="<",thd_val = 2000)

#6. use land to mask shadow thus get rid of water
shadow_masked = mask(shadow, land)
shadow_cloud = shadow_masked + cloud*2

#7.images output
out_put_dict = {"max_image":max_image,
                "min_image":min_image,
                "land":land,
                "cloud":cloud,
                "shadow":shadow,
                "min_image_7x7":min_image_7x7,
                "max_image_7x7":max_image_7x7,
                "shadow_masked":shadow_masked,
                "shadow_cloud":shadow_cloud
                }

for out_img in out_put_dict:   

    array_to_raster(out_put_dict[out_img],
                r'D:\cloud_shadow_test_II\img11\{}.tif'.format(out_img),
                r'D:\cloud_shadow_test_tif\20180314_095229_1042_3B_AnalyticMS_SR_b1.tif')


