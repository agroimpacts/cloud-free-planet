#This module will download data from planet.com
#Takes the following command line parameters:
#1=output_folder, 2=start_date, 3=end_date, 4=limit (max to download)
#5=xmin, 6=xmax, 7=ymin, 8=ymax
#9=% cloud cover allowed (as a decimal like 0.05), 10=% bad pixels allowed, 11=asset_type, e.g. "udm" or "analytic"
#12=a list containing item types, e.g. ['PSScene4Band']
  
import os
import sys #for sys.argv
import requests
import time
from planet import api
import numpy as np
import rasterio
from rasterio import Affine as A
from rasterio.warp import reproject, Resampling, transform_geom  
from rasterio import transform

import subprocess   #to call gdalwarp
from re import sub  #regular expressions module - good for string matches, searches, etc.

from osgeo import gdal
from requests.auth import HTTPBasicAuth  #new way to download subarea
      
#Initialize these variables outside of a function so that they will be global:
params = {}
apikey = "" 
aoi = {}    
list_of_files = []  #list of downloaded udm files
list_of_items = []  #each item is a dict of info about a particular scene that is available

def create_client():
    global apikey
    apikey = os.getenv('PL_API_KEY')
    if apikey is None: 
        #On Tammy's computer - since I don't have it in my path, I need these 2 lines:
        PL_API_KEY="***REMOVED***"  
        apikey = PL_API_KEY
    client = api.ClientV1(api_key=apikey)
    return client

def create_session():
    # establish a "requests" session to facilitate http requests
    session = requests.Session()
    session.auth = (apikey, '')
    return session

def define_aoi(xmin,ymin,xmax,ymax):
# establish aoi given bounding coords
    
    aoi = {
            'type': 'Polygon',
            'coordinates': [
                [
                [
                    xmin,
                    ymin
                ],
                [
                    xmax,
                    ymin
                ],
                [
                    xmax,
                    ymax
                ],
                [
                    xmin,
                    ymax
                ],
                [
                    xmin,
                    ymin
                ]
                ]
            ]
            }
    return aoi

def set_filters(client, aoi):

    date_filter = {
        'type': 'DateRangeFilter',
        'field_name': 'acquired',
        'config': {
            'gte': params["start_date"],
            'lte': params["end_date"]
        }   
    }    

    cloud_filter = {
        'type': 'RangeFilter',
        'field_name': 'cloud_cover',
        'config': {
            'lte': params["max_cloud_cover"]
        }    
    }

    bad_pixel_filter = {
        'type': 'RangeFilter',
        'field_name': 'anomalous_pixels',
        'config': {
            'lte': params["max_bad_pixels"]
        }    
    }

    location_filter = api.filters.geom_filter(aoi)

    # combine filters:
    query = {
        'type': 'AndFilter',
        'config': [date_filter, cloud_filter, location_filter, bad_pixel_filter]
    }

    return query

def activate_and_download(query, client, session):
    try:
        logfilename = params["output_folder"] + 'logfile.txt'
        logfile = open(logfilename, 'w') #'w'=write mode, 'a'= append, 'r'=read
    
        # build the request
        request = api.filters.build_search_request(query,params["item_types"]);

        # post the request
        try:
            results = client.quick_search(request)
        except:
            #if not results = None:
              print('Error doing build_search_request')
              raise Exception
             
        for item in (results).items_iter(params["results_limit"]):
            print('Downloading : '+item['id'] ) # + ' cloud_cover=' + str(item.items[2][1]))
            item_type = params["item_types"][0]
            dataset = session.get(("https://api.planet.com/data/v1/item-types/" + "{}/items/{}/assets/").format(item_type, item['id']))
    
            #print (dataset) #it was <Response [401]> ==> Unauthorized when my apikey wasn't working (wasn't global).  
                             #Now is <Response [200]>, which means OK.
                             #Maybe I should figure out how to check it & exit gracefully if <> 200.
        
            # extract the activation url from the item for the desired asset
            item_activation_url = dataset.json()[params["asset_type"]]["_links"]["activate"]

            # request activation
            response = session.post(item_activation_url)
    
            while response.status_code!=204:  #204=No Response
                time.sleep(30)  #seconds
                response = session.post(item_activation_url)
                response.status_code = response.status_code
                print('Waiting ...')
                print('Status code =' + str(response.status_code)) #I could create a dictionary of codes & messages, to be more informative
            assets = client.get_assets(item).get()

            # download
            callback = api.write_to_file(directory=params["output_folder"], callback= None, overwrite= True)
            body = client.download(assets[params["asset_type"]], callback=callback)
    
            body.await()

            print (params["output_folder"] + '\\' + body._body.name, file=logfile) #body._body.name = name of file downloaded, w.o. path
            if not list_of_files.count(params["output_folder"] + '\\' +body._body.name): #Need to only add if not a duplicate!
                list_of_files.append(params["output_folder"] + '\\' + body._body.name) 
                list_of_items.append(item)
            
    except:
        print(Exception)
        logfile.close()
        return False  #there was an exception

    logfile.close()
    print("list_of_files=")
    print(list_of_files)

    return True  #successful

def activate_and_download_subarea(query, client, session):
    try:
        logfilename = params["output_folder"] + 'logfile.txt'
        logfile = open(logfilename, 'a') #'w'=write mode, 'a'= append, 'r'=read
    
        # build the request
        request = api.filters.build_search_request(query,params["item_types"]);
        print('request='+str(request));print()

        # post the request
        try:
            results = client.quick_search(request)
        except:
            #if not results = None:
              print('Error doing build_search_request')
              raise Exception
             # print(results)  #there is nothing in results, not even "None"  #Why doesn't this print even tho it gets here?

        for item in (results).items_iter(params["results_limit"]):
            print('Downloading : '+item['id'] ) # + ' cloud_cover=' + str(item.items[2][1]))
            item_type = params["item_types"][0]
            dataset = session.get(("https://api.planet.com/data/v1/item-types/" + "{}/items/{}/assets/").format(item_type, item['id']))
    
            #print (dataset) #it was <Response [401]> ==> Unauthorized when my apikey wasn't working (wasn't global).  
                             #Now is <Response [200]>, which means OK.
                             #Maybe I should figure out how to check it & exit gracefully if <> 200.
        
            # extract the activation url from the item for the desired asset
            item_activation_url = dataset.json()[params["asset_type"]]["_links"]["activate"]

            # request activation
            response = session.post(item_activation_url)
    
            while response.status_code!=204:  #204=No Response
                time.sleep(30)  #seconds
                response = session.post(item_activation_url)
                response.status_code = response.status_code
                print('Waiting ...')
                print('Status code =' + str(response.status_code)) #I could create a dictionary of codes & messages, to be more informative
            assets = client.get_assets(item).get()

            # download
            callback = api.write_to_file(directory=params["output_folder"], callback= None, overwrite= True)
            body = client.download(assets[params["asset_type"]], callback=callback)
    
            body.await()

            print (params["output_folder"] + '\\' + body._body.name, file=logfile) #body._body.name = name of file downloaded, w.o. path
            if not list_of_files.count(params["output_folder"] + '\\' +body._body.name): #Need to only add if not a duplicate!
                list_of_files.append(params["output_folder"] + '\\' + body._body.name) 
                list_of_items.append(item)
    except:
        print(Exception)
        logfile.close()
        return False  #there was an exception

    logfile.close()
    print("list_of_files=")
    print(list_of_files)
    return True  #successful

def window_from_downloaded_file(fullname, xmin, xmax, ymin, ymax, dstname="", outtype='RST'):
    """
    Takes a file (downloaded scene) and windows out the desired subarea, 
    which is simultaneously projected to the output (target) ref system & window dimensions.
    (xmin, xmax, ymin & ymax, are output window bounds in latlong )
    Returns output filename of reprojected window.
    """

    dst_crs = {'init': 'EPSG:4326'}
    if dstname == "":
        dstname = sub('.tif','_win.rst',fullname)  #same as original, but ending in _win.rst   #Do I need to do lowercase first?  #re.sub
    dst_bnds = (xmin, ymin, xmax, ymax) 
        
    dst_transform = rasterio.transform.from_bounds(xmin, ymin, xmax, ymax, 200, 200)  #def from_bounds(west, south, east, north, width, height):
            #Note: output resolution will probably change.  Currently 200 x 200 is 0.000025 seconds cell resolution
    dst_shape = (200, 200)

    with rasterio.open(fullname) as src:
        kwargs = src.meta.copy()  #is this necessary
        kwargs.update({
            'crs': dst_crs,
            'width': 200, #width
            'height': 200, #height
            'transform': dst_transform,  #affine,
            'driver': outtype       #note - outtype should be either 'RST' or 'GTiff'
            })

        with rasterio.open(dstname, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=dst_transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)   #What resampling type should we use?

    return dstname

def calculate_percent_good_cells(fname):
    """
    Takes a UDM file (fname) in RST format (byte binary straight raster) and 
    returns the percent of cells that are good (i.e. that have a cell value of 0).
    """

    #1: create an empty array
    #cells = np.zeros(win_shape,win_dtype)  #need to know shape to do this.  I could hard-code it in, or have it passed to this function as parameter


    #3: fill the array
    cells = np.fromfile(fname,dtype=np.int8)  #uint8?

    #4: count good cells
    good_cells = 0
    for cell in cells.flat:   #.flat allows you to iterate over each element of the array as if it were one dimensional
        if cell == 0:
            good_cells += 1

    percent_good = good_cells / len(cells)   #num_good/total = %good

    return percent_good

def choose_best(list_of_files):
    """
    Windows out UDMs & calculates which has the highest % of good cells. 
    Returns name & ID of best UDM image, and itemdict for that scene.  
    Will later use that name to choose the scene to download & window.
    """

    best_percent = 0

    for index, fname in enumerate(list_of_files):
        
        window_name = window_from_downloaded_file(fname,params["xmin"], params["xmax"], params["ymin"], params["ymax"]) #outtype = 'RST', not 'GTiff' by default

        #window_name = window_from_downloaded_file_calling_gdal_via_subprocess(fname,params["xmin"], params["xmax"], params["ymin"], params["ymax"])
       
        percent_good = calculate_percent_good_cells(window_name)
        if percent_good > best_percent:
            best_scene_fname = fname
            best_percent = percent_good
            best_scene_index = index
                 
    print('best_percent (good_cells) = ', best_percent)
    
    best_scene_dict = list_of_items[best_scene_index]

    return best_scene_fname, best_scene_dict 

def download_and_window_specific_scene(client, session, scene_dict):
    """
    Given scene id, download the scene from Planet & return the local filename.
    """
    scene_fname = download_scene("PSScene4Band", "analytic", client, session, scene_dict)
    destname = sub('.tif','_win.tif',scene_fname)
    window_fname = window_from_downloaded_file(scene_fname,params["xmin"], params["xmax"], params["ymin"], params["ymax"], outtype='GTiff', dstname=destname)

    return window_fname

def download_scene(item_type, asset_type, client, session, scene_dict):
    """
    Given scene id, item_type & asset_type, download the scene from Planet & return the local filename.
    """

    item_type = params["item_types"][0]

    dataset = session.get(("https://api.planet.com/data/v1/item-types/" + "{}/items/{}/assets/").format(item_type, scene_dict["id"]))
    
    item_activation_url = dataset.json()[asset_type]["_links"]["activate"]

    # request activation
    response = session.post(item_activation_url)
    
    while response.status_code!=204:  #204=No Response
        time.sleep(30)  #seconds
        response = session.post(item_activation_url)
        response.status_code = response.status_code
        print('Waiting ...')
        print('Status code =' + str(response.status_code)) #I could create a dictionary of codes & messages, to be more informative
    assets = client.get_assets(scene_dict).get()

    # download
    callback = api.write_to_file(directory=params["output_folder"], callback= None, overwrite= True)
    body = client.download(assets[asset_type], callback=callback)
    body.await()
    local_filename = params["output_folder"] + '\\' + body._body.name

    return local_filename  

def download_planet_data(outdir,sdate,edate,maximgs,xmin1,xmax1,ymin1,ymax1,max_clouds,bad_pixels,assettype,lst_item_types):
    """
    This is the main (outer) function that will be called.
    Download planet data from web site using date range, bounding rectangle, and cloud cover standards to filter choices.
    Should probably set defaults for maximgs, max_clouds, bad_pixels, assettype & lst_item_types, so those can be optional.
    """
    
    try:
        #Put the parameters into the global variables
        global params

        params["output_folder"] = outdir     #\your\download\directory
        params["start_date"] = str(sdate)    #YYYY-MM-DD format
        params["end_date"] = str(edate)    #YYYY-MM-DD format
        params["start_date"] = "%sT00:00:00.000Z" %(params["start_date"])
        params["end_date"] = "%sT00:00:00.000Z" %(params["end_date"])
        params["results_limit"] = int(maximgs)    #the maximum number of files you want to retrieve.

        params["xmin"] = xmin = float(xmin1)
        params["xmax"] = xmax = float(xmax1)
        params["ymin"] = ymin = float(ymin1)
        params["ymax"] = ymax = float(ymax1)

        params["max_cloud_cover"] = float(max_clouds)
        params["max_bad_pixels"] = float(bad_pixels)
        params["asset_type"] = str(assettype)
     
        params["item_types"] = lst_item_types
    except:
        return "Error processing input parameters."
   

    try:
        #Call the functions to process everything (same functions called by main()
        client = create_client()
        print("client="+str(client)); print()

        session = create_session()
        print("session="+str(session)); print()

        aoi = define_aoi(xmin,ymin,xmax,ymax)
        query = set_filters(client, aoi)
        print("query="+str(query)); print()

        if len(query)>0:
            success = activate_and_download(query, client, session)
        if success:
#            for fname in list_of_files:
#                fullname = params["output_folder"] + '\\' + fname
#                win_data = window_from_downloaded_file(fullname,xmin, xmax, ymin, ymax)
            pass
        else:
            print('There was an exception in activate_and_download')
            return('There was an exception in activate_and_download')
    except:
       return "Error encountered while communicating with Planet website or downloading files."

    best_scene_fname, best_scene_dict = choose_best(list_of_files)  

    output_fname = download_and_window_specific_scene(client, session, best_scene_dict)

    return output_fname

def get_cmdln_parameters():  #This function will probably not be used. It would only be used if this program were called via cmdln
    #Take the cmdln parameters (4,8,11 or 12 of them)
    #1=output_folder, 2=start_date, 3=end_date, 4=limit (max to download)
    #5=xmin, 6=xmax, 7=ymin, 8=ymax
    #9=% cloud cover allowed (as a decimal like 0.05), 10=% bad pixels allowed, 11=asset_type, e.g. "udm" or "analytic"
    #12=a list containing item types, e.g. ['PSScene4Band']
    
    #initialize_default_parameters() #This is in case not all the parameters are specified.  allows user to only do 1st or second grp of args

    global params

    if len(sys.argv) > 3:
        params["output_folder"] = str(sys.argv[1])     #\your\download\directory
            #We need to check if that folder exists & if it doesn't, create it or choose a different folder!!
        params["start_date"] = str(sys.argv[2])    #YYYY-MM-DD format
        params["end_date"] = str(sys.argv[3])    #YYYY-MM-DD format
        #Have to make sure the dates are valid dates!!  e.g. "2017-06-31" caused an error later on because there are only 30 days in June.
        params["start_date"] = "%sT00:00:00.000Z" %(params["start_date"])
        params["end_date"] = "%sT00:00:00.000Z" %(params["end_date"])
        params["results_limit"] = int(sys.argv[4])    #the maximum number of files you want to retrieve.
    else:
        print("No command line parameters given.  Unable to run.")
        return

    if len(sys.argv) > 7:
        params["xmin"] = float(sys.argv[5])
        params["xmax"] = float(sys.argv[6])
        params["ymin"] = float(sys.argv[7])
        params["ymax"] = float(sys.argv[8])
    else:
        params["xmin"] = -122.5
        params["xmax"] = -122.495
        params["ymin"] = 37.74
        params["ymax"] = 37.745

    if len(sys.argv) > 10:
        params["max_cloud_cover"] = float(sys.argv[9])
        params["max_bad_pixels"] = float(sys.argv[10])
        params["asset_type"] = fstr(sys.argv[11])
    else:
        params["max_cloud_cover"] = 0.05
        params["max_bad_pixels"] = 0.05
        params["asset_type"] ='analytic'

    if len(sys.argv) > 11:        
        params["item_types"] = list(sys.argv[9])
    else:
        params["item_types"] = ['PSScene4Band']

def main():  
    """
    This only gets called if run from cmdln
    """
    get_cmdln_parameters()
    download_planet_data(**params)

if __name__ == '__main__':
    main()

#Eventually need to replace my tabs with 4 spaces - to comply with PEP8

"""
Http status_code's :
https://www.w3.org/Protocols/HTTP/HTRESP.html
200=OK (request was fulfilled
201=Created (if follows a POST command, this = success)
202=Accepted (request has been accepted for processing, but the processing has not been completed.
203=Partial info
204=No response
300's=Redirection
    301=Moved
    302=Found (under a diff URL)
    304=Not Modified
400's-500's=Error
    400=Bad request
    401=Unauthorized
    402=PaymentRequired 
    403=Forbidden 
    404=Not found
    429=Too Many Requests (perhaps > 20?)
        The HTTP 429 Too Many Requests response status code indicates the user has sent too many requests in a given amount of time ("rate limiting").
        A Retry-After header might be included to this response indicating how long to wait before making a new request.
    500=Internal Error
    501=Not implemented
    502=Service temporarily overloaded
    503=Gateway timeout


Robust clients should be prepared for 429 responses from any endpoint and to retry after a backoff period.

There are a few rate-limits classes currently in place:
    For most endpoints, the rate limit is 10 requests per second, per API key.
    For activation endpoints, the rate limit is 5 requests per second, per API key.
    For operation endpoints at /compute/ops, the rate limit is 5 requests per second, per API key.
    For download endpoints, the rate limit is 15 requests per second, per API key.


UDM file:
0 = good data
1 = background values
2 = clouds
>=4 = missing or suspect data (downlink problems in >=1 band(s)

"""
   
def download_a_subarea(item_id, asset_type="udm", item_type="PSScene4Band", ):
    """
    This function is not working yet.  It's just pieces of test code... ideas in progress.
    """
    #item_id = "20161109_173041_0e0e"
    #item_type = "PSScene3Band"

    asset_type = "asset_type="+asset_type
    item_url = 'https://api.planet.com/data/v1/item-types/{}/items/{}/assets'.format(item_type, item_id)

    client = create_client()
    session = create_session()

    # Request a new download URL
    result = requests.get(item_url, auth=HTTPBasicAuth(apikey, ''))
    download_url = result.json()[asset_type]['location']
    #Prefix the download URL with '/vsicurl/' to use the VSI Curl driver. Then call GDAL Warp, passing it an output file name, this URL, our subarea GeoJSON, a projection (in this case, the one used by GeoJSON.io), and 'cropToCutline = True'.
    vsicurl_url = '/vsicurl/' + download_url
    output_file = item_id + '_subarea.tif'

    # GDAL Warp crops the image by our AOI, and saves it
    gdal.Warp(output_file, vsicurl_url, dstSRS = 'EPSG:4326', cutlineDSName = 'subarea.geojson', cropToCutline = True)

def download_planet_data_subarea(outdir,sdate,edate,maximgs,xmin1,xmax1,ymin1,ymax1,max_clouds,bad_pixels,assettype,lst_item_types):
    """
    This function is not complete yet.
    Still need to add the part where it windows/reprojects/chooses the subarea -- BEFORE downloading.

    This is the main (outer) function that will be called.
    Download planet data from web site using date range, bounding rectangle, and cloud cover standards to filter choices.
    Should probably set defaults for maximgs, max_clouds, bad_pixels, assettype & lst_item_types, so those can be optional.
    """
    
    try:
        #Put the parameters into the global variables
        global params

        params["output_folder"] = outdir     #\your\download\directory
        params["start_date"] = str(sdate)    #YYYY-MM-DD format
        params["end_date"] = str(edate)    #YYYY-MM-DD format
        params["start_date"] = "%sT00:00:00.000Z" %(params["start_date"])
        params["end_date"] = "%sT00:00:00.000Z" %(params["end_date"])
        params["results_limit"] = int(maximgs)    #the maximum number of files you want to retrieve.

        params["xmin"] = xmin = float(xmin1)
        params["xmax"] = xmax = float(xmax1)
        params["ymin"] = ymin = float(ymin1)
        params["ymax"] = ymax = float(ymax1)

        params["max_cloud_cover"] = float(max_clouds)
        params["max_bad_pixels"] = float(bad_pixels)
        params["asset_type"] = str(assettype)
     
        params["item_types"] = lst_item_types
    except:
        return "Error processing input parameters."
   

    try:
        #Call the functions to process everything (same functions called by main()
        client = create_client()
        print("client="+str(client)); print()

        session = create_session()
        print("session="+str(session)); print()

        aoi = define_aoi(xmin,ymin,xmax,ymax)
        query = set_filters(client, aoi)
        print("query="+str(query)); print()

        if len(query)>0:
            success = activate_and_download(query, client, session)
        if success:
#            for fname in list_of_files:
#                fullname = params["output_folder"] + '\\' + fname
#                win_data = window_from_downloaded_file(fullname,xmin, xmax, ymin, ymax)
            pass
        else:
            print('There was an exception in activate_and_download')
            return('There was an exception in activate_and_download')
    except:
       return "Error encountered while communicating with Planet website or downloading files."

    best_scene_fname, best_scene_dict = choose_best(list_of_files)  

    output_fname = download_and_window_specific_scene(client, session, best_scene_dict)

    return output_fname
