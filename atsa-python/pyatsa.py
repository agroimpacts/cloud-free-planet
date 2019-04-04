import numpy as np
import rasterio as rio
from rasterio import fill
import skimage as ski
import matplotlib.pyplot as plt
import glob
import os
from rasterio.plot import reshape_as_raster, reshape_as_image
import json
import scipy.stats as stats
import statsmodels.formula.api
from skimage import exposure
from sklearn.cluster import KMeans
from skimage import morphology as morph
from math import ceil

# below are plotting and vis functions
def percentile_rescale(arr, plow=1, phigh=99):
    '''
    Rescales and applies other exposure functions to improve image vis. 
    http://scikit-image.org/docs/dev/api/skimage.exposure.html#skimage.exposure.rescale_intensity
    '''
    rescaled_arr = np.zeros_like(arr)
    for i in range(0,arr.shape[-1]):
        val_range = (np.percentile(arr[:,:,i], plow), np.percentile(arr[:,:,i], phigh))
        rescaled_channel = exposure.rescale_intensity(arr[:,:,i], val_range)
        rescaled_arr[:,:,i] = rescaled_channel
#     rescaled_arr= exposure.adjust_gamma(rescaled_arr, gamma=1) #adjust from 1 either way
#     rescaled_arr= exposure.adjust_sigmoid(rescaled_arr, cutoff=.50) #adjust from .5 either way 
    return rescaled_arr
def normalize(arr):
    ''' Function to normalize an input array to 0-1 '''
    arr_max = arr.max()
    return arr / arr_max

def reorder_to_rgb(image):
    '''reorders  bands ordered like BGRNIR
    to blue, red, green for imshow
    '''
    blue = normalize(image[:,:,0])
    green = normalize(image[:,:,1])
    red = normalize(image[:,:,2])
    nir = normalize(image[:,:,3])
    return np.stack([red, green, blue], axis=-1) 

def plot_series(series, n, title, save=False):
    """
    Plots n number of images in a series with shape
    [number of images, rows, columns].
    """
    i = 0
    while i < n:

        plt.figure()
        ski.io.imshow(series[i,:,:])
        plt.title(title+': image '+str(i))
        
        if save ==True:
            
            plt.savefig(title+str(series[i,:,:].min())+'_imagemin_'+str(i)+".png")
        i+=1

###porting code from original idl written by Xiaolin Zhu
    
ATSA_DIR="/home/rave/cloud-free-planet/atsa-test-unzipped/"
img_path = os.path.join(ATSA_DIR, "planet-pyatsa-test/stacked_larger_utm.tif")
img = ski.io.imread(img_path)
#set the following parameters
dn_max=10000  #maximum value of DN, e.g. 7-bit data is 127, 8-bit is 255
tempfolder=os.path.join(ATSA_DIR, 'temp') # folder for storing intermediate results
background=0  #DN value of background or missing values, such as SLC-off gaps
buffer=1    #width of buffer applied to detected cloud and shadow, recommend 1 or 2 

#parameters for HOT caculation and cloud detection
#------------------------------
n_band=4     # number of bands of each image
n_image=img.shape[2]/n_band   # number of images in the time-series
blue_b=0    # band index of blue band, note: MSS does not have blue, use green as blue
green_b=1   # band index of green band
red_b=2     # band index of red band
nir_b=3     # band index of nir band

A_cloud=0.5 # threshold to identify cloud (mean+A_cloud*sd), recommend 0.5-1.5, smaller values can detect thinner clouds
maxblue_clearland=dn_max*0.15 # estimated maximum blue band value for clear land surface
maxnir_clearwater=dn_max*0.05 # estimated maximum nir band value for clear water surface
rmax = maxblue_clearland # max value for blue band for computing clear line
rmin = .01*dn_max # min DN value for flue band for computing clear line
n_bin = 50 # number of bins between rmin and rmax

#parameters for shadow detection
#------------------------------
shortest_d=7.0       #shortest distance between shadow and cloud, unit is pixel resolution
longest_d=50.0  #longest distance between shadow and its corresponding cloud, unit is "pixel",can be set empirically by inspecting images
B_shadow=1.5   #threshold to identify shadow (mean-B_shadow*sd), recommend 1-3, smaller values can detect lighter shadows
#------------------------------

#we reshape our images that were stacked on the band axis into a 4D array
t_series = np.reshape(img,(img.shape[0],img.shape[1],n_band,int(n_image)), order='F')

#Computing the Clear Sky Line for Planet Images in T Series
#Zhu set to 1.5 if it was less than 1.5 but this might not be a good idea for Planet 
#due to poorer calibration?
def reject_outliers_by_med(data, m = 2.):
    """
    Reject outliers based on median deviation (unused currently but might be worth trying out)
    https://stackoverflow.com/questions/11686720/is-there-a-numpy-builtin-to-reject-outliers-from-a-list
    """
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    return data[s<m].flatten()

def reject_outliers_by_mean(data_red, data_blue, m = 3.):
    """
    Reject outliers based on deviation from mean
    This is the method used in Zhu and Elmer 2018
    """
    return (data_red[abs(data_red - np.mean(data_red)) < m * np.std(data_red)], \
            data_blue[abs(data_red - np.mean(data_red)) < m * np.std(data_red)])

def get_clear_skyline(img, rmin0, rmax, nbins=50):
    """
    Computes the clear sky line for a single image using the
    automatic bin based approach used by Zhen and Elmer 2018.
    Returns the slope and intercept of the clear sky line.
    Larger images are easier to compute a clear sky line, 
    smaller images with more clouds are more difficult and may
    need to take an assumed slope or both slope and intercept.
    """
    # make 3D arrays for blue and red bands to compute clear sky lines
    blue = img[:,:,0]
    red = img[:,:,2]
    # finding samples, there should be at least 500 values to 
    # compute clear sky line
    good_histo_values = np.where((blue<rmax)&(blue>rmin0), blue, 0)
    if np.count_nonzero(good_histo_values) > 500:
        rmin = np.min(good_histo_values[good_histo_values!=0]) # starts binning where we have good data
        # computes the histogram for a single blue image
        (means, edges, numbers)=stats.binned_statistic(blue.flatten(), 
                blue.flatten(), statistic='mean', 
                bins=50, range=(int(rmin),int(rmax)))
        
        histo_numbers_reshaped = np.reshape(numbers, (blue.shape[0],blue.shape[1]))
        red_means=[]
        blue_means=[]
        # don't include 0 values in the mean calculations
        for i in np.unique(histo_numbers_reshaped):
            
            red_vals = red[histo_numbers_reshaped==i]
            blue_vals = blue[histo_numbers_reshaped==i]
            # Zhu set this thresh for number of values needed in bin to compute mean
            if len(blue_vals) > 20: 
                # before selecting top 20, reject outliers based on 
                # red values and pair with corresponding blue values as per Zhu code
                # TO DO have function return indices of the good values or take both as args
                (red_vals, blue_vals) = reject_outliers_by_mean(red_vals, blue_vals)

                ## added these steps from Zhu code, but not sure if/why they are necessary
                # they result in fewer values being averaged in each bin sometimes
                red_vals = sorted(red_vals)
                blue_vals = sorted(blue_vals)
                n = 20 # zhu used this hardcoded value
                select_n = min([n, ceil(.01*len(blue_vals))])
                red_selected = red_vals[-select_n:]
                blue_selected = blue_vals[-select_n:]
                ##

                
                #finds the highest red values and takes mean
                red_means.append(
                    np.mean(
                        red_vals[-select_n:]
                    )
                )
                blue_means.append(
                    np.mean(
                        blue_vals[-select_n:]
                    )
                )
        # we want at least half of our ideal data points to construct the clear sky line
        if len(np.unique(histo_numbers_reshaped)) > .5 * nbins:
            
            #followed structure of this example: https://www.statsmodels.org/dev/generated/statsmodels.regression.linear_model.OLS.html
            model = statsmodels.formula.api.quantreg('reds~blues', {'reds':red_means, 'blues':blue_means})

            result = model.fit()

            intercept = result.params[0]
            slope = result.params[1]
            # hardcode if slope too low NEED TO TEST
            if slope < 1.5:
                slope = 1.5
                intercept = np.mean(red_means) - slope*np.mean(blue_means)

            return (intercept,slope)
        # if we don't have even half the ideal amount of bin means...
        # assume slope and use available data to compute intercept.
        else: 
            slope = 1.5
            intercept = np.mean(red_means)-slope*np.mean(blue_means)
            return (intercept, slope)
    else:
        # we return nan here to signal that we need to use the 
        # mean slope and intercept for the good clear skylines
        return (np.nan,np.nan) 
    

def compute_hot_series(t_series, rmin, rmax, n_bin=50):
    """Haze Optimized Transformation (HOT) test
    Equation 3 (Zhu and Woodcock, 2012)
    Based on the premise that the visible bands for most land surfaces
    are highly correlated, but the spectral response to haze and thin cloud
    is different between the blue and red wavelengths.
    Zhang et al. (2002)
    In this implementation, the slope (a) and intercept(b)
    of the clear sky line are computed automatically using a bin based approach.

    Parameters
    ----------
    t_series: a 4D array with the band index as the third axis, image index as
    the fourth axis (counting from 1st).

    Output
    ------
    ndarray: The values of the HOT index for the image, a 3D array
    """
    blues = t_series[:,:,0,:]
    reds = t_series[:,:, 2,:]
    intercepts_slopes = np.array(
        list(map(lambda x: get_clear_skyline(x,rmin,rmax),
                np.moveaxis(t_series,3,0)))
        )
    # assigns slope and intercept if an image is too cloudy (doesn't have 500 pixels in rmin, rmax range)
    if np.isnan(intercepts_slopes).all():
        # extreme case where no images can get a clear sky line
        intercepts_slopes[:,1] = 1.5
        intercepts_slopes[:,0] = 0
    if np.isnan(intercepts_slopes).any():
        # case where some images can't get a clear skyline
        intercepts_slopes[:,1][np.isnan(intercepts_slopes[:,1])] = np.nanmean(intercepts_slopes[:,1])
        intercepts_slopes[:,0][np.isnan(intercepts_slopes[:,0])] = np.nanmean(intercepts_slopes[:,0])
    def helper(blue, red, ba):
        b,a = ba
        return abs(a*blue - (b+red))/np.sqrt(1+a**2)
    # map uses the first axis as the axis to step along
    # need to use lambda to use multiple args
    hot_t_series = np.array(list(map(lambda x,y,z: helper(x,y,z), 
                    np.moveaxis(blues,2,0), 
                    np.moveaxis(reds,2,0), 
                    intercepts_slopes)))
    return hot_t_series, intercepts_slopes

def reassign_labels(class_img, cluster_centers, k=3):
    """Reassigns mask labels of t series
    based on magnitude of the cluster centers.
    This assumes land will always be less than thin
    cloud which will always be less than thick cloud,
    in HOT units"""
    idx = np.argsort(cluster_centers.sum(axis=1))
    lut = np.zeros_like(idx)
    lut[idx] = np.arange(k)
    return lut[class_img]

def fit_predict_reassign(x, km):
    """returns the reassigned prediction for a single image"""
    model = km.fit(x.reshape((-1,1)))
    return reassign_labels(model.labels_.reshape(x.shape), model.cluster_centers_)

def create_cloud_masks(hot_t_series):
    """Runs kmeans with 3 clusters and returns an array
    with 3 labels, where the cluster with the smallest
    kmeans center is assigned as land (0), then the next to
    thin clouds (1), and the next to thick clouds (2)"""
    km = KMeans(n_clusters=3, n_init=10, max_iter=100, tol=1e-4, n_jobs=-1, 
                      verbose=False, random_state=4)

    cloud_masks = np.array(list(map(
        lambda x: fit_predict_reassign(x, km),
        hot_t_series
        )))
    return cloud_masks

def sample_and_kmeans(hot_t_series, hard_hot=3000000, sample_size=1000000):
    """Trains a kmeans model on a sample of the time series
    and runs prediction on the time series.
    A hard coded threshold for the hot index, hard_hot, is
    for allowing the kmeans model to capture more variation 
    throughout the time series. Without it, kmeans is skewed toward
    extremely high HOT values and classifies most of the time series
    as not cloudy."""
    
    km = KMeans(n_clusters=3, n_init=50, max_iter=100, tol=1e-4, n_jobs=-1, 
                      verbose=False, random_state=4)

    sample_values = np.random.choice(
        hot_t_series.flatten()[hot_t_series.flatten()<hard_hot], 
        size=sample_size).reshape(-1,1)
    
    fit_result = km.fit(sample_values)
    
    predicted_series = fit_result.predict(hot_t_series.flatten().reshape(-1,1)).reshape(hot_t_series.shape)
    
    return reassign_labels(predicted_series, fit_result.cluster_centers_, k=3)

def calculate_upper_thresh(hot_t_series, cloud_masks, A_cloud):
    """Uses temporal refinement as defined by Zhu and Elmer 2018
    to catch thin clouds by defining the upper boundary, U for clear 
    pixels. Later we might want to compute a neighborhood std 
    through the t_series."""
    hot_potential_clear = np.array(list(map(
        lambda x, y: np.where(x>0, np.nan, y),
        cloud_masks, hot_t_series))) # set cloud to nan
    hot_potential_cloudy = np.array(list(map(
        lambda x, y: np.where(x==0, np.nan, y),
        cloud_masks, hot_t_series))) # set non cloud to nan
    t_series_std = np.nanstd(hot_potential_clear, axis=0)
    t_series_mean = np.nanmean(hot_potential_clear, axis=0)
    t_series_min = np.nanmin(hot_potential_clear, axis=0)
    t_series_max = np.nanmax(hot_potential_clear, axis=0)
    range_arr = t_series_max - t_series_min
    
    # cloud_series_min can be computed more efficiently using k means centers 
    # if a single k means model is used
    # according to Zhu in personal communciation. This is done in IDL code
    
    # NRDI (adjust_T in the IDL code) is a problem here because the HOT indices 
    # vary a lot in the planet images. if we train a kmeans model for each image
    # Th_initial will have a very low initial value, if we train one kmeans model
    # then the model will produce innacurate initial masks because of extremely high
    # HOT values. Need to find a work around.
    
    # the sticky point is how cloud_series_min is calculated. if it is the minimum
    # of all cloudy areas calculated by multiple kmeans models, it is not correct for 
    # the whole t series
    
    #calcualting with multiple kmeans
    cloud_series_min = np.nanmin(hot_potential_cloudy.flatten(), axis=0)
    
    NRDI = (cloud_series_min - range_arr)/(cloud_series_min + range_arr)
    upper_thresh_arr = t_series_mean + (A_cloud+NRDI)*t_series_std
    
    return (upper_thresh_arr, hot_potential_clear, hot_potential_cloudy)

hot_t_series, intercepts_slopes = compute_hot_series(t_series, rmin, rmax)
cloud_masks = create_cloud_masks(hot_t_series) # this runs very slow since I fit a new kmeans model to each image