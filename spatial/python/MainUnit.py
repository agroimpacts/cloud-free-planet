"""This program calls download_planet_data in planet_download.py using hardcoded variables that are for testing purposes
    To run this, you should have a folder called d:\planettest\data on your computer.
    Or you can just change the hard-coded folder name below.
    Use this as an example of how to prepare your parameters to call that function
"""

import os
import sys
from planet_download import download_scenes_from_aois_in_csv
from planet_download import download_planet_data_new
from planet_download import download_scene_by_id
from planet_download import add_logging
from planet_download import calculate_percent_good_cells_in_tiff2  #temporarily here for testing purposes

#params expected are outdir,start_date,end_date,maximgs,xmin,xmax,ymin,ymax,max_clouds,max_bad_pixels,asset_type,lst_item_types
param_dict = {}
param_dict["outdir"] = r'd:\PlanetTest\Data'
param_dict["xmin"] = -122.5
param_dict["xmax"] = -122.495
param_dict["ymin"] = 37.74
param_dict["ymax"] = 37.745
param_dict["start_date_short"] =  '2017-12-15' #'2017-06-15''2017-07-01'
param_dict["end_date_short"] = '2018-03-15' #'2017-09-15' #'2017-07-30'
param_dict["max_clouds"] = 0.25  #max proportion of pixels that are clouds
param_dict["max_bad_pixels"] = 0.25 #max proportion of bad pixels (transmission errors, etc.)
param_dict["asset_type"] = "analytic_sr" #"udm"  #"analytic"  #analytic_sr"
param_dict["maximgs"] = 10 #20 
param_dict["lst_item_types"] = ['PSScene4Band']  #needs to be a list
param_dict["buffer_size"] = 0.00025  # a 10-pixel buffer; resolution = 0.000025
param_dict["suffix"] = "_SR_GS"  #analytic_sr for growing season
#param_dict["suffix"] = "_SR_OS"  #analytic_sr for off-season


#output_fname = download_planet_data(**param_dict)  
client = None
session = None
#output_fname = download_planet_data_new(client, session, **param_dict)  #5/3 added client & session as params

Tammys_APIkey = "***REMOVED***"
ryans_api_key = ryans_apikey = "***REMOVED***" #To access areas outside of California

def download_scene_for_ron_by_id():
    outdir = r'd:\PlanetTest\Data'
    asset_type = "analytic_sr"
    #asset_type = "analytic"
    #asset_type = "udm"
    item_type = ['PSScene4Band']  
    scene_id = "20170620_232623_0c79"   #Worked for analytic_sr, analytic & udm
    #scene_id = "20180314_095229_1042"  #Worked for analytic_sr, analytic & udm
        #scene_id = "20170401_071839_0e16_3B"  #"Could not find the requested item" - for analytic_sr, analytic & udm
        #scene_id = "20170905_092835_0f46_3B"   #"Could not find the requested item"
    #scene_id = "20180314_095225_1042"   #Worked for analytic_sr, analytic & udm
    #scene_id = "20180303_095157_1014"  "worked"
    #scene_id = "20180311_095230_103d" "worked.  since it was already activated from an earlier run, it took just a few seconds to download.
    #scene_id = "20180228_095154_1025" "worked"
    #scene_id = "20180303_105144_1050" "worked"
    #scene_id = "20180310_095138_102e" "worked"
    #scene_id = "20180306_095153_0f52" "worked"
    scene_id = "20180228_095050_102f" "worked"
    #The above downloads usually took 4-5 minutes each
    
    apikey = ryans_api_key
    prefix=""
    suffix="_SR"
    download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix)

def download_and_window_scene_for_ron_by_id():
    outdir = r'd:\PlanetTest\Data'
    asset_type = "analytic_sr"
    item_type = ['PSScene4Band']  
    #scene_id = "20170620_232623_0c79"
    scene_id = "20180314_095229_1042"
    apikey = ryans_api_key
    xmin = -0.575
    xmax = -0.525
    ymin = 5.7
    ymax = 5.75
    prefix=""
    suffix="_SR"
    download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix, xmin, xmax, ymin, ymax)
    
def download_and_window_manually():
    outdir = r'd:\PlanetTest\Data'
    asset_type = "analytic_sr"
    item_type = ['PSScene4Band']  
    apikey = ryans_api_key
    window_out = True
    suffix = "_SR_GS"

    prefix = "GH0700059"
    scene_id = "20180225_105315_104a"
    xmin = -3.081
    xmax = -3.076
    ymin = 6.085
    ymax = 6.09
    output_fname = download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix, window_out, xmin, xmax, ymin, ymax)

    prefix = "ProblemClip"
    #scene_id = "20180421_095029_1025"
    scene_id = "20180227_105246_1054"
    xmin = -3.081
    xmax = -3.076
    ymin = 6.085
    ymax = 6.09
    output_fname = download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix, window_out, xmin, xmax, ymin, ymax)
    
    
#download_scene_for_ron_by_id()

#csvname = r'D:\Users\twoodard\documents\ron_bigger.csv'
#download_scenes_from_aois_in_csv(csvname,ryans_api_key, **param_dict)


# I used MyGeodata Converter, a free online kml to csv converter (https://mygeodata.cloud/converter/)
# and just dragged that kml file onto it.  It took the linear rings & created a csv that 
# had the center points of each grid cell, and other info.  I removed the unnecessary fields in Excel.
# Now I had a csv file of center pts: x,y,name.  But I needed them in minx,maxx,miny,maxy,name format.
# That is what the following function & the 4 lines that follow it are for.

def copy_center_pt_csv_to_grid_cell_csv(csv_in_name, csv_out_name):
    #read a csv that has x,y,name (center point of grid cells); write one with name, minx, maxx, miny, maxy of each grid cell

    import csv
    f_in = open(csv_in_name)
    center_cells = list(csv.reader(f_in,delimiter=','))[1:]  #Read the CSV rows into grid_cells list; Skip the top row.  
    half = 0.0025  #half a cell in degrees. Will use to get min/max of cell, given center x/y.

    f_out = open(csv_out_name, 'w')
    f_out.write("name,xmin,xmax,ymin,ymax\n")

    for row in center_cells:
        centerX = float(row[0])
        centerY = float(row[1])
        name = row[2]
        f_out.write(name +"," + str(centerX-half) +"," + str(centerX+half) +"," + str(centerY-half) +"," + str(centerY+half)+"\n")

    f_out.close() 
    f_in.close()

#csv_centerpts = r'D:\Users\twoodard\pictures\ghanasites.csv'
#csvname = r'D:\Users\twoodard\documents\lyndon_sites.csv'
#copy_center_pt_csv_to_grid_cell_csv(csv_centerpts,csvname)

add_logging()

#download_and_window_manually()


csvname = r'D:\Users\twoodard\documents\extents_qual_sites.csv'
param_dict["outdir"] = r'd:\PlanetTest\Data\SA_GrowingSeason'
param_dict["start_date_short"] =  '2017-01-01' 
param_dict["end_date_short"] = '2018-03-01'
param_dict["suffix"] = "_SR_GS" 
download_scenes_from_aois_in_csv(csvname, ryans_api_key, **param_dict)

csvname = r'D:\Users\twoodard\documents\extents_qual_sites.csv'
param_dict["outdir"] = r'd:\PlanetTest\Data\SA_OffSeason'
param_dict["start_date_short"] =  '2017-06-30' 
param_dict["end_date_short"] = '2018-08-311'
param_dict["suffix"] = "_SR_OS" 
download_scenes_from_aois_in_csv(csvname, ryans_api_key, **param_dict)


#csvname = r'D:\Users\twoodard\documents\lyndon_sites_Asamankese_only.csv'
csvname = r'D:\Users\twoodard\documents\lyndon_sites_Asamankese_only - copy.csv'  #This one has completed grid cells removed.  Gets smaller as I debug & test.
param_dict["start_date_short"] =  '2018-02-01'
param_dict["end_date_short"] = '2018-03-31'
download_scenes_from_aois_in_csv(csvname,ryans_api_key, **param_dict)

#csvname = r'D:\Users\twoodard\documents\lyndon_sites_all_but_Asamankese.csv'
csvname = r'D:\Users\twoodard\documents\lyndon_sites_all_but_Asamankese-skipped.csv'  #the ones that need to be redone
param_dict["start_date_short"] =  '2018-03-01'
param_dict["end_date_short"] = '2018-04-30'
download_scenes_from_aois_in_csv(csvname,ryans_api_key, **param_dict)


#need to download this one by id later:
#20180225_105315_104a

csvname = r'D:\Users\twoodard\documents\california_sites.csv' # California is free. Use for testing.
param_dict["start_date_short"] =  '2018-02-01'
param_dict["end_date_short"] = '2018-03-31'
param_dict["maximgs"] = 1 #Lets speed up the testing process! Just do 1 image per grid cell.
param_dict["asset_type"] = "analytic_sr"
download_scenes_from_aois_in_csv(csvname,Tammys_APIkey, **param_dict)



##############################################################################################################
##                               Not needed anymore                                                         ##
##############################################################################################################
"""

    #GH0624590:
    scene_id = "20180416_095125_1021"
    xmin = 0.164  
    xmax = 0.169
    ymin = 6.285
    ymax = 6.29  
    output_fname = download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix, window_out, xmin, xmax, ymin, ymax)
        
    #GH0625426:
    scene_id = "20180416_095125_1021"
    xmin = 0.164
    xmax = 0.169
    ymin = 6.28
    ymax = 6.285
    output_fname = download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix, window_out, xmin, xmax, ymin, ymax)
    
    prefix = "GH0656874"
    scene_id = "20180411_100353_0f18"
    xmin = -3.066
    xmax = -3.061
    ymin = 6.09
    ymax = 6.095
    output_fname = download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix, window_out, xmin, xmax, ymin, ymax)
    
    prefix = "GH0659442"
    scene_id = "20180411_100353_0f18"
    xmin = -2.991
    xmax = -2.986
    ymin = 6.075
    ymax = 6.08
    output_fname = download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix, window_out, xmin, xmax, ymin, ymax)
    
    prefix = "GH0657724"
    scene_id = "20180411_100353_0f18"
    xmin = -3.081
    xmax = -3.076
    ymin = 6.085
    ymax = 6.09
    output_fname = download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix, window_out, xmin, xmax, ymin, ymax)
    
    prefix = "GH0643235"
    scene_id = "20180421_100445_0f4e"
    xmin = -3.016
    xmax = -3.011
    ymin = 6.17
    ymax = 6.175
    output_fname = download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix, window_out, xmin, xmax, ymin, ymax)
    
    """