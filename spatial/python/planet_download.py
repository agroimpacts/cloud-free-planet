#This module will download data from planet.com
#Takes the following command line parameters:
#parameters may have changed.  Need to update this section...
#1=output_folder, 2=start_date, 3=end_date, 4=limit (max to download)
#5=xmin, 6=xmax, 7=ymin, 8=ymax
#9=% cloud cover allowed (as a decimal like 0.05), 10=% bad pixels allowed, 11=asset_type, e.g. "udm" or "analytic"
#12=a list containing item types, e.g. ['PSScene4Band']
#More parameters (not available via cmdln yet) : buffer_size
  
#Eventually need to replace my tabs with 4 spaces - to comply with PEP8

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

from tqdm import tqdm   # Fast, Extensible Progress Meter  (low overhead, fast performance)
                        # Instantly make your loops show a smart progress meter - just wrap any iterable with tqdm(iterable), and you’re done!
                        # Do "pip install tdqm" from cmd prompt  -- to be able to use it
                        # Used when reporting clip progress
import zipfile  # To unzip downloaded clip files
import ntpath   # Will use this to get the separate the filename (basename) from the path.  This is a robust way of getting filenames of various OS's
import logging 
   
#Initialize these variables outside of a function so that they will be global:
params = {}
apikey = "" 
aoi = {}    
#list_of_udm_files = []  #list of downloaded udm files
#list_of_items = []  #each item is a dict of info about a particular scene that is available
CAS_URL =  r"https://api.planet.com/compute/ops/clips/v1/"
Tammys_APIkey = "***REMOVED***"
global_best_percent = 0.0

ASSET_URL = 'https://api.planet.com/data/v1/item-types/{}/items/{}/assets/'
SEARCH_URL = 'https://api.planet.com/data/v1/quick-search'
ITEM_URL = 'https://api.planet.com/data/v1/item-types/{}/items/{}'

#Variables that often change for testing purposes
perfect = 1 #0.3 #1  #1 means 100% cloud free
bool_delete_tmp_files = True  

#For rasterio.transform
num_rows = 220  # 200 rows + 10 pixel buffer on left & right -- for the final output images, not the udms
num_cols = 220  # 200 cols + 10 pixel buffer on top & bottom -- for the final output images



def add_logging():
    #Add logging to screen & file:
    
    global logging

    logging.basicConfig(level=logging.DEBUG,
                        format='%(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=r'd:\PlanetTest\Data\debug.log',
                        filemode='w')

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')

    # set a format which is simpler for console use
    formatter = logging.Formatter('%(message)s')
    #formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')

    # tell the handler to use this format
    console.setFormatter(formatter)
    
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    # Now, we can log to the root logger, or any other logger. First the root...
    logging.info('Logging started...')
    logging.debug('Debug message')

    # Now, define a couple of other loggers which might represent areas in your
    # application:

    """
    logger1 = logging.getLogger('myapp.area1')
    logger2 = logging.getLogger('myapp.area2')
    
    logger1.debug('debug msg')
    logger1.info('info msg')
    logger2.warning('warning msg')
    logger2.error('error message.')
    """

def create_client():

    global apikey  

    if apikey is '':
        apikey = os.getenv('PL_API_KEY')
        if apikey is None: 
            #On Tammy's computer - since I don't have it in my path, I need these 2 lines:
            apikey = Tammys_APIkey

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

def set_filters_sr(aoi):
    #add an asset_filter for only those scenes that have an analytic_sr asset available

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
            'lte': params["max_clouds"]
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

    asset_filter = {
        "type": "PermissionFilter",
        "config": ["assets.analytic_sr:download"]
        }

    # combine filters:
    query = {
        'type': 'AndFilter',
        'config': [date_filter, cloud_filter, location_filter, bad_pixel_filter, asset_filter]
    }

    return query

def window_from_downloaded_file(fullname, xmin, xmax, ymin, ymax, dstname="", outtype='RST'):
    """
    Takes a file (downloaded scene) and windows out the desired subarea, 
    which is simultaneously projected to the output (target) ref system & window dimensions.
    (xmin, xmax, ymin & ymax, are output window bounds in latlong )
    Returns output filename of reprojected window.
    """
    try:
        dst_crs = {'init': 'EPSG:4326'}
        if dstname == "":
            dstname = sub('.tif','_win.rst',fullname)  #same as original, but ending in _win.rst   #Do I need to do lowercase first?  #re.sub
            dstpath = ""
            dstshortname = ""

        dst_bnds = (xmin, ymin, xmax, ymax) 
        
        dst_transform = rasterio.transform.from_bounds(xmin, ymin, xmax, ymax, num_rows, num_cols)  #def from_bounds(west, south, east, north, width, height):
                #Note: output resolution will probably change.  Currently 200 x 200 is 0.000025 seconds cell resolution
        dst_shape = (num_rows, num_cols)

        with rasterio.open(fullname) as src:
            kwargs = src.meta.copy()  #is this necessary
            kwargs.update({
                'crs': dst_crs,
                'width': num_rows, #width
                'height': num_cols, #height
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
    except:
        return ""

    return dstname

def calculate_percent_good_cells_in_tiff(fname):
    """
    Takes a UDM file (fname) in TIFF format 
    returns the percent of cells that are good (i.e. that have a udm cell value of 0).
    """
    try:
        #1: fill the array
        dataset = gdal.Open(fname, gdal.GA_ReadOnly)
        band = dataset.GetRasterBand(1)
        cells = band.ReadAsArray()   #what type of array will cells be?  Might not be a numpy array

        #2: count good cells
        good_cells = 0
        for cell in cells.flat:   #.flat allows you to iterate over each element of the array as if it were one dimensional
            if cell == 0:
                good_cells += 1

        percent_good = good_cells / len(cells.flat)   #num_good/total = %good
    except:
        return 0

    #Do I need to do dataset.close() or something similar?
    return percent_good

def download_and_window_specific_scene(client, session, scene_dict, prefix="", asset_type="analytic_sr"):
    """
    Given scene dict (used for scene id & more), download the scene from Planet, then window/reproject it & return the local filename.
    """
    try:
        item_type = scene_dict["properties"]["item_type"] 
        scene_id = scene_dict["id"] #error:"NoneType object is not subscriptable" - if scene_dict = None
    
        logging.info(" ")
        logging.info("id=" + scene_id)

        scene_fname = download_scene(asset_type, client, session, scene_dict)
    
        #destname = sub('.tif','_win.tif',scene_fname)
        shortname = ntpath.basename(scene_fname)
        destname = params["outdir"] + "\\" + prefix + "_" + sub('.tif','_win.tif',shortname)
        logging.info("destname = " + destname); logging.info(" ")

        window_fname = window_from_downloaded_file(scene_fname,params["xmin"], params["xmax"], params["ymin"], params["ymax"], dstname=destname, outtype='GTiff')

        if bool_delete_tmp_files:
            os.remove(scene_fname) #Delete original.  We only need the windowed image.  
    except:
        logging.info("Exception in download_and_window_specific_scene")
        return ""

    return window_fname

def download_scene_by_id(lst_item_types, asset_type, scene_id, outdir, api_key_passed="", prefix = "", window_out=False, xmin=0, xmax=0, ymin=0, ymax=0):
    #scene_id is item_id, which is 20 digits long
    #if no api_key_passed, it will check the environment for an apikey

    try:
        global params #Put the parameters into the global variables
        params["outdir"] = outdir     #\your\download\directory
        params["lst_item_types"] = lst_item_types
        params["asset_type"] = asset_type

        global apikey
        apikey = api_key_passed   #If no api key is passed, it will check your environment variable in create_client
        logging.debug("apikey="+ apikey)
    
        client = create_client()
        logging.debug("client="+str(client)); logging.info(" ")

        session = create_session()
        logging.debug("session="+str(session)); logging.info(" ")
    
        dataset = session.get(ITEM_URL.format(lst_item_types[0], scene_id))
        scene_dict = dataset.json()
        logging.info(scene_dict)

        if 'id' not in scene_dict.keys(): 
            try:
                logging.info(scene_dict["general"][0]["message"])
            except:
                logging.info("Unable to find requested item")  #Using "unable to" instead of "could not", so I can distinguish when I wrote the error or the "message" contained the error
            output_fname = ""
            return output_fname
        if window_out:
            params["xmin"] = xmin 
            params["xmax"] = xmax 
            params["ymin"] = ymin 
            params["ymax"] = ymax 
            output_fname = download_and_window_specific_scene(client, session, scene_dict, prefix, asset_type)
        else:     
            output_fname = download_scene(asset_type, client, session, scene_dict) 
    except:
        return ""

    return output_fname
    
def download_scene(asset_type, client, session, scene_dict):
    """
    Given scene_dict & asset_type, download the scene from Planet & return the local filename.
    """

    try:
        scene_id = scene_dict["id"]
        item_type = scene_dict["properties"]["item_type"]
        dataset = session.get(ASSET_URL.format(item_type, scene_id))
    
        item_activation_url = dataset.json()[asset_type]["_links"]["activate"]
        logging.info("item_activation_url=" + item_activation_url)

        response = session.post(item_activation_url)   # request activation
        logging.info(response.status_code)
        #What if response is immediately 204???

        while response.status_code!=204:  #204=No Response #202=Accepted (request has been accepted for processing, but not been completed yet. #200=ok(fulfilled)
            time.sleep(30)  #seconds
            response = session.post(item_activation_url)
            response.status_code = response.status_code
            logging.info('Waiting ...')
            logging.info('Status code =' + str(response.status_code)) #I could create a dictionary of codes & messages, to be more informative
        assets = client.get_assets(scene_dict).get()

        # download
        callback = api.write_to_file(directory=params["outdir"], callback= None, overwrite= True)
        body = client.download(assets[asset_type], callback=callback)
        body.await()
        local_filename = params["outdir"] + '\\' + body._body.name
        logging.info("local_filename="+local_filename)
    except:
        return ""

    return local_filename  

def download_planet_data_new(client,session,outdir,start_date_short,end_date_short,xmin,xmax,ymin,ymax,prefix="",asset_type="analytic_sr",maximgs=50,max_clouds=0.1,max_bad_pixels=0.1,lst_item_types=['PSScene4Band'],buffer_size=0.00025):
    """
    This is the main (outer) function that will be called.
    Download planet data from web site using date range, bounding rectangle, and cloud cover standards to filter choices.
    Should probably set defaults for maximgs, max_clouds, max_bad_pixels, asset_type & lst_item_types, so those can be optional.
    """
    
    try:
        #Put the parameters into the global variables
        global params
        global global_best_percent

        params["outdir"] = outdir     #\your\download\directory
        #params["start_date"] = str(start_date_short)    #YYYY-MM-DD format
        #params["end_date"] = str(end_date_short)    #YYYY-MM-DD format
        params["start_date"] = "%sT00:00:00.000Z" %(str(start_date_short))
        params["end_date"] = "%sT00:00:00.000Z" %(str(end_date_short))
        params["maximgs"] = int(maximgs)    #the maximum number of files you want to retrieve.
        params["xmin"] = xmin = float(xmin) - buffer_size
        params["xmax"] = xmax = float(xmax) + buffer_size
        params["ymin"] = ymin = float(ymin) - buffer_size
        params["ymax"] = ymax = float(ymax) + buffer_size
        params["max_clouds"] = float(max_clouds)
        params["max_bad_pixels"] = float(max_bad_pixels) 
        params["asset_type"] = str(asset_type)   
        params["lst_item_types"] = lst_item_types
    except:
        return "Error processing input parameters."

    try:
        
        if client == None:
            client = create_client()
        logging.debug("client="+str(client)); logging.info(" ")

        if session == None:
            session = create_session()
        logging.debug("session="+str(session)); logging.info(" ")
        
        aoi = define_aoi(xmin,ymin,xmax,ymax)
        
        # Make UDM buffer a lot bigger to prevent nearby clouds from casting shade onto our little window, without us realizing it 
        # (since UDMs only notice (thick) clouds, not shade)
        udm_buffer = buffer_size*10      #enlarge udms by buffer_size*10 on all side
        aoi_udm = define_aoi((xmin-udm_buffer),(ymin-udm_buffer),(xmax+udm_buffer),(ymax+udm_buffer))  

        percent_good = 0
        best_percent_good = 0
        
        query = set_filters_sr(aoi_udm)  #4/23 - Need to only include scenes that have an analytic_sr asset 
        #query = set_filters(aoi_udm) #5/9 see if adding the analytic_sr was what caused the problem
            
        logging.info(" ")
        logging.info("Querying scenes where cloud_cover < " + str(params["max_clouds"])) 
        logging.info(" ")
            
        #Clip, download & compare UDMs:
        if len(query)>0:
            best_scene_fname, best_scene_dict, best_percent_good = use_new_clip_and_ship_to_download_udms(query, client, session, aoi_udm, outdir) 
            if best_scene_fname != "None":
                download_and_window_specific_scene(client,session,best_scene_dict,prefix,"analytic_sr")
            else:
                logging.info('best-scene_fname = "None"'); logging.info(" ")

        logging.info("final best percent = " + str(best_percent_good))
        logging.info("best_scene_fname = " + best_scene_fname)
        
        global_best_percent = best_percent_good

    except:
        logging.info("Error encountered while communicating with Planet website or downloading files.")  
        if best_percent_good > 0:
            msg = "skipped.  " + best_scene_dict["id"] + "  " + str(best_percent_good) + " %"
            return msg
        else:
            return "Error encountered while communicating with Planet website or downloading files."

    if best_percent_good > 0:
        logging.info('best_scene_dict=')
        logging.info(best_scene_dict)
        output_fname = best_scene_fname
    else: 
        output_fname = "No scenes found"

    return output_fname
       
def Identify_intersecting_scenes(query, client):
    try:
        # build the request
        item_types = ['PSScene4Band']   #params["lst_item_types"]
        request = api.filters.build_search_request(query, item_types)
       
        # post the request
        try:
            results = client.quick_search(request)
            # "this will cause an exception if there are any API related errors", which apparently is every time I do it after the 1st time
        except:
            #How do I capture the specific error message?
            logging.info('Error doing build_search_request')
            raise Exception
                 
    except:
        logging.info('exception in Identify_intersecting_scenes')
    
    return results         

def download_scenes_from_aois_in_csv(csvname, passed_apikey, outdir,start_date_short,end_date_short,xmin,xmax,ymin,ymax,asset_type,maximgs=50,max_clouds=0.3,max_bad_pixels=0.3,lst_item_types=['PSScene4Band'],buffer_size=0.00025):
    """
    Open csv file containing scene_name, xmin, xmax, ymin & ymax values (in separate fields)
    Top row contains column headers
    Each additional row represents a scene window to be downloaded/extracted.
    Download & window each scene & place result in the outdir.
    """
    global apikey
    apikey = passed_apikey

    import csv
    try:
        f = open(csvname)
        grid_cells = list(csv.reader(f,delimiter=','))[1:]  #Read the CSV rows into grid_cells list; Skip the top row.  
    except:
        return "Error reading CSV file"

    try:
        params_local = {}
        params_local["outdir"] = outdir     #\your\download\directory
        params_local["start_date_short"] = str(start_date_short)    #YYYY-MM-DD format   ###5/9
        params_local["end_date_short"] = str(end_date_short)    #YYYY-MM-DD format     ###5/9
        params_local["maximgs"] = int(maximgs)    #the maximum number of files you want to retrieve.
        params_local["max_clouds"] = float(max_clouds)
        params_local["max_bad_pixels"] = float(max_bad_pixels)
        params_local["asset_type"] = str(asset_type)   
        params_local["lst_item_types"] = lst_item_types
        params_local["buffer_size"] = buffer_size   # a 10-pixel buffer; resolution = 0.000025        
    except:
        return "Error processing input parameters."

    try:
        outname_file = outdir + '\\scenes_downloaded.txt'
        outf = open(outname_file, 'a')
        print('GridCellName = Filename',file=outf)
        outf.close()  #Close it & use append mode each time a filename is added to it. Then if it crashes, the file will be complete up to that point.
    except:
        return "Error creating or writing to scenes_downloaded.txt"

    client = create_client()
    session = create_session()

    #download the requested scenes
    for row in grid_cells:              #Each row refers to 1 grid cell
        name = row[0]
        logging.info(" "); logging.info(" "); logging.info(name) 
        params_local["xmin"] = row[1]
        params_local["xmax"] = row[2]
        params_local["ymin"] = row[3]
        params_local["ymax"] = row[4]
        params_local["prefix"] = name            
        output_fname = download_planet_data_new(client, session, **params_local)  

        worked = (output_fname != "No scenes found") and (output_fname != "None") and (output_fname != "")
        worked = (worked and (output_fname != "Error encountered while communicating with Planet website or downloading files.")) 

        if worked:   ### Need to change this comparison

            outf = open(outname_file, 'a')
            percent_str = '{0:2f}'.format(global_best_percent * 100)
            print(name + "=" + output_fname + ",   % Good = " + percent_str + " %", file = outf)   # write list of grid cell names and their corresponding filenames to a text file
            outf.close()      
        else:
            skippedfilelog = outdir + '\\not_downloaded.txt'
            skippedf = open(skippedfilelog, 'a')
            msg = name # + global_best_percent
            print(msg,file=skippedf)
            skippedf.close()
    

####################################################################################################################
#   The following was taken from clip_and_ship_introduction.py                                                     #
####################################################################################################################

def clip(clip_payload):
    """
    clip_payload is a dict containing "aoi" & "targets"; "targets" contains item_id, item_type, asset_type
    clip_download_url will be returned
    NOTE: Clipped scene will only be available for 5 minutes after clipping (i.e. download it immediately!)
    """

    logging.debug('Before clip request')
    try:
        # Request clip of scene (This will take some time to complete)
        request = requests.post(CAS_URL, auth=(apikey, ''), json=clip_payload)      
    except:
        logging.info("Error encountered while requesting clip")
        return ""
       
    logging.debug("after clip request") 
    #logging.debug("request=" + request)

    if (request == 400):
        return ""
    elif (request == 429):
        logging.info("request denied.  Will try again in 30 seconds.")
        sleep(30)
        request = requests.post(CAS_URL, auth=(apikey, ''), json=clip_payload)
        logging.info("after retrying request")
        logging.info(request)

    """ 
    Need to identify what response is & handle it if it's 400 or higher
    if request = 400:
        skip this scene

    if request = 429:
        sleep(30)
        logging.info("request denied.  Will try again in 30 seconds.")
        request = requests.post(CAS_URL, auth=(apikey, ''), json=clip_payload)
        logging.info("after retrying request")
        logging.info(request)
    """

    logging.debug("after request")

    try:
        clip_url = request.json()['_links']['_self']
    except:
        logging.info("Unable to get clip_url from request")
        sleep(30)
        #clip_url = request.json()['_links']['_self']
        msg = request.joson()['general'][0]  #I saw an informational error message in this field once "AOI does not intersect targets".  Perhaps this is where they tell us what went wrong...?
        logging.info(msg)


    logging.info(" "); logging.info("clip_url = " + clip_url)

    # Poll API to monitor clip status. Once finished, download and upzip the scene
    clip_succeeded = False
    while not clip_succeeded:

        # Poll API
        check_state_request = requests.get(clip_url, auth=(apikey, ''))
        #logging.info(check_state_request)
    
        # If clipping process succeeded , we are done
        if check_state_request.json()['state'] == 'succeeded':
            clip_download_url = check_state_request.json()['_links']['results'][0]
            clip_succeeded = True
            logging.info("Clip of scene succeeded and is ready to download") 
    
        # Still activating. Wait 1 second and check again.
        else:
            logging.info("...Still waiting for clipping to complete...")
            time.sleep(15)

    return clip_download_url   

def download_clip(clip_download_url, outpath, scene_id):
    """
    Downloads file located at clip_download_url, then unzips it.
    Returns the filename of the output tiff file.  (An XML will be there too.  Do we need that?)
    """
    try:
        # Download clip
        outfname = outpath + scene_id + ".zip"
        response = requests.get(clip_download_url, stream=True)
        #logging.info("response=" + str(response))

        with open(outfname, "wb") as handle:
            for data in tqdm(response.iter_content()):
                handle.write(data)

        # Unzip file
        zipped_item = zipfile.ZipFile(outfname)
        names = zipped_item.namelist()
        zipped_item.extractall(outpath)   #(outpath + scene_id)  
  
        # Delete zip file
        try:
            zipped_item.close()  #The following line couldn't execute because it was still being accessed by something
            os.remove(outfname)  #deletes the zip file
        except:
            pass

        for fname in names:
            if fname.lower().endswith('.tif'):  #, re.IGNORECASE):
                outfname = outpath + fname
    except:
        logging.info("Error downloading clip")
        return ""

    return outfname

def sort_items(input_items):
    #sort by scenes by lowest cloud % & lowest anomalous pixels
    try:
        item_lst = []
        tup = ()
        for item in (input_items).items_iter(params["maximgs"]):  #items_iter is an iterative containing all the items that fit that filter's parameters       
            logging.info(item["id"])
            logging.info(item["properties"]["cloud_cover"])
            logging.info(item["properties"]["anomalous_pixels"])
            tup = (item["properties"]["cloud_cover"],item["properties"]["anomalous_pixels"],item["id"],item)
            item_lst.append(tup)
        
        item_lst.sort()
    except:
        logging.info("Error encountered in sort_items.  Will return the list unsorted.")
        return input_items

    logging.info(" ")
    return item_lst 

def use_new_clip_and_ship_to_download_udms(query, client, session, aoi, outpath):
    """
    Identify & download pre-clipped UDMs for our AOI.
    """
    
    try:
        #Step1: Identify_intersecting_scenes -> using AOI, date, filter requirements
                #udm_items: list will have item_id, item_type, and asset_type for each scene to clip & download     
        udm_items = Identify_intersecting_scenes(query, client)        
    
        #maybe should check if udm_items contains anything before continuing...

        sorted_lst = sort_items(udm_items)  # list of 3 place tuple : (item["cloud_cover"],item["anomalous_pixels"],item["id"])

        #logging.info(sorted_lst)  #can't print that.  Creates exception.

        outpath = outpath + '\\'
        best_percent_good = 0
        options = {}
        options["aoi"] = aoi
        targ = {}
        targ["item_type"] = params["lst_item_types"][0]
        targ["asset_type"] = "udm"  #params["asset_type"]  
        list_targ = []
    
    except:
        logging.info('Error encountered in "use_new_clip_and_ship_to_download_udms"')
        best_fname = "None"
        best_item = {}
        return best_fname, best_item, best_percent_good

    #for item in (udm_items).items_iter(params["maximgs"]):  #items_iter is an iterative containing all the items that fit that filter's parameters       
    for item in sorted_lst:         
        try:
            ##targ["item_id"] = item['id']
            targ["item_id"] =  item[2]  
            logging.info(item[2])
            logging.info(item)

            list_targ.append(targ)
            options["targets"] = list_targ

            #Tell Planet to clip & download clipped results:
            clip_download_url = clip(options)     
            if clip_download_url == "":
                logging.info("Unable to clip " + targ["id"] + ". Skipping this UDM.")
                continue #skip this one

            outfname = download_clip(clip_download_url, outpath, targ["item_id"])
            if outfname == "":
                logging.info("Unable to download clip for " + targ["id"] + ". Skipping this UDM.")
                continue #skip this one
        except:
            logging.info("Exception occurred. " + targ["id"] + ". Skipping this UDM.")
            continue  #skip this one

        #Compare the UDMs:
        try:
            percent_good = calculate_percent_good_cells_in_tiff(outfname)
        except:
            logging.info("Unable to calculate percent good for  " + targ["id"] + ". Skipping this UDM.")
            continue

        if percent_good >= perfect: # I'm using >= instead of == in case we temporarily lower our standards to get clouds for testing purposes; perfect is usually 1
            best_fname = outfname
            best_id = targ["item_id"]
            best_percent_good = percent_good
            best_item = item[3]
            break   #we're done. stop now.
        elif percent_good > best_percent_good:
            #save this as the best scene so far & continue to check for a better scene
            best_fname = outfname
            best_id = targ["item_id"]
            best_percent_good = percent_good
            best_item = item[3]
#        elif percent_good > 0:     #Delete the bad udm files.  For testing purposes, comment out for now so we can see them
#            filelist = list(outfname)
#            delete_udm_files(filelist, "")
            
        logging.info("percent good (this UDM) = " + str(percent_good))
        logging.info("best percent (this round) = " + str(best_percent_good)); 
        logging.info(" ")

        list_targ.clear()   

    if best_percent_good > 0:
        return best_fname, best_item, best_percent_good  #success
    else:
        logging.info("best_percent_good = 0")
        best_fname = "None"
        best_item = {}
        return best_fname, best_item, best_percent_good
    #I should put a condition in where it's >0 but < 90, and it records that as a questionable grid cell - flagged to be checked later
    

def delete_udm_files(filelist, not_this_one):
    """
    Delete the fullsized UDM files that were downloaded, and the windowed ones except the best one chosen (not_this_one)
    """

    if (len(filelist) > 1):
        for fname in filelist:
            os.remove(fname)
    elif (len(filelist) == 1):
        os.remove(fname)
        
    for fname in filelist:
        basename = fname[:len(fname)-4]
        tmp = basename + '_win.rst.aux.xml'
        os.remove(tmp)
        if fname != not_this_one:
            tmp = basename + '_win.rst'
            os.remove(tmp)
            tmp = basename + '_win.rdc'
            os.remove(tmp)




#############################################################################################################
#  The following are not used anymore, but we might need them again soon, so I'm keeping them here for now  #
#############################################################################################################

def request_activation(client, session, item_activation_url, item):
    #request activation of given item_activation_url & return assets list
    response = session.post(item_activation_url)
    
    while response.status_code!=204:  #204=No Response
        time.sleep(30)  #seconds
        response = session.post(item_activation_url)
        response.status_code = response.status_code
        logging.info('Waiting for activation ...')
        logging.info('Status code =' + str(response.status_code)) #I could create a dictionary of codes & messages, to be more informative
    assets = client.get_assets(item).get()
    return assets

def download_activated_asset(client, assets, outfolder, asset_type):
    #download an asset of asset_type from list assets to outfolder - note: asset was already activated.

    #callback = use_warp_to_download_window(output_filename, download_url, aoi, dstSRS = 'EPSG:4326')
    callback = api.write_to_file(directory=outfolder, callback= None, overwrite= True)
    
    body = client.download(assets[asset_type], callback=callback)   
    body.await()
    return body

def main():  
    """
    This only gets called if run from cmdln
    """
    #get_cmdln_parameters()
    #download_planet_data(**params)

    ryans_api_key = ryans_apikey = "***REMOVED***"
    csvname = r'D:\Users\twoodard\documents\extents_qual_sites.csv'
    outdir = r'd:\PlanetTest\Data'
    download_scenes_from_aois_in_csv(csvname,outdir, ryans_api_key)

if __name__ == '__main__':
    main()

def set_filters(aoi):

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
            'lte': params["max_clouds"]
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