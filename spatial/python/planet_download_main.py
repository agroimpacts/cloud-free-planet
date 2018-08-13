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
import yaml

def parse_yaml(input_file):
    """Parse yaml file of configuration parameters."""
    with open(input_file, 'r') as yaml_file:
        params = yaml.load(yaml_file)
    return params

params = parse_yaml(os.path.join(os.environ['PYTHONPATH'],"config_template.yaml"))

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
param_dict["maximgs"] = 10 #15 #10 #20 
param_dict["lst_item_types"] = ['PSScene4Band']  #needs to be a list
param_dict["buffer_size"] = 0.00025  # a 10-pixel buffer; resolution = 0.000025
param_dict["suffix"] = "_SR_GS"  #analytic_sr for growing season
#param_dict["suffix"] = "_SR_OS"  #analytic_sr for off-season

client = None
session = None
api_key = params['mapper']['PL_API_KEY'] #To access areas outside of California

add_logging()


def list_of_downloaded_files(mypath,txtfname,suffix='.TIF'):
    from os import walk

    try:
        f = []
        for (dirpath, dirnames, filenames) in walk(mypath):
            f.extend(filenames)
        f.sort() 
        final_list = []
        for fname in f:
            if fname[:9] not in final_list:
                final_list.append(fname[:9])
   
        outf = open(txtfname, 'w')
        for fname in final_list:
            print(fname,file=outf)
        outf.close()  #Close it & use append mode each time a filename is added to it. Then if it crashes, the file will be complete up to that point.
        
    except:
        return "Error creating or writing to scenes_downloaded.txt"
def remove_downloaded_scenes(scenes_downloaded,original_file,outname):

    import csv
    try:
        f = open(scenes_downloaded)
        downloaded_already = f.read().split('\n')

        f2 = open(original_file)
        original_scenes = list(csv.reader(f2,delimiter=','))[1:]  #Read the CSV rows into grid_cells list; Skip the top row.  

    except:
        return "Error reading CSV file"

    try:
        outname_file = outname #r'D:\Users\twoodard\documents\scenes_to_retry.txt'
        outf = open(outname_file, 'w')
        print('name,xmin,xmax,ymin,ymax',file=outf)
        index = 0
        for row in original_scenes:              #Each row refers to 1 grid cell
            name = row[0]
            if not (name in downloaded_already):
                row_info = row[0] + ',' + row[1] + ',' + row[2] + ',' + row[3] + ',' + row[4]
                print(row_info, file=outf)

            #try:
            #    name2 = downloaded_lst[index][0] 
            #except:
            #    name2 = ""

            #if name == name2 :
            #    index += 1
            #else:
            #    row_info = row[0] + ',' + row[1] + ',' + row[2] + ',' + row[3] + ',' + row[4]
            #    print(row_info, file=outf)

        outf.close()  #Close it & use append mode each time a filename is added to it. Then if it crashes, the file will be complete up to that point.
    except:
        return "Error"
    return outname_file

def download_scene_for_ron_by_id():
    outdir = r'd:\Pass\Ron\Clouds'
    asset_type = "analytic_sr"
    #asset_type = "analytic"
    asset_type = "udm"
    item_type = ['PSScene4Band']  
    #UDM downloads usually took 4-5 minutes each
  
    apikey = api_key
    prefix=""
    suffix="_SR"
    scene_id = "20180228_095050_102f"
    download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix)
    scene_id = "20180228_095154_1025"
    download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix)
    scene_id = "20180303_095157_1014"
    download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix)
    scene_id = "20180303_105144_1050"
    download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix)
    scene_id = "20180306_095153_0f52"
    download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix)
    scene_id = "20180310_095138_102e"
    download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix)

#download_scene_for_ron_by_id()

def download_and_window_scene_for_ron_by_id():
    outdir = r'd:\PlanetTest\Data'
    asset_type = "analytic_sr"
    item_type = ['PSScene4Band']
    scene_id = "20180521_072352_1013"
    apikey = api_key
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
    apikey = api_key
    window_out = True
    suffix = "_SR_GS"

    prefix = "ZA0649200"
    scene_id = "20180214_073031_101e"
    xmin = 30.209
    xmax = 30.214
    ymin = -25.575
    ymax = -25.57
    output_fname = download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix, window_out, xmin, xmax, ymin, ymax)
    
    prefix = "ZA1182104"
    scene_id = "20180215_085907_0f1a"
    xmin = 32.659
    xmax = 32.664
    ymin = -26.975
    ymax = -26.97
    output_fname = download_scene_by_id(item_type, asset_type, scene_id, outdir, apikey, prefix, suffix, window_out, xmin, xmax, ymin, ymax)
    
#csvname = r'D:\Users\twoodard\documents\ron_bigger.csv'
#download_scenes_from_aois_in_csv(csvname, api_key, **param_dict)


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


ppath = "D:\\PlanetTest\\data\\MatchWV2gridcells\\OS\\"
txtfname = ppath + 'already_downloaded.txt'
list_of_downloaded_files(ppath,txtfname)
original_csv = r'D:\Users\twoodard\documents\wv2_boxes_order_fixed.csv'
output_csv = ppath + 'scenes_to_be_downloaded.csv'
new_csv = remove_downloaded_scenes(txtfname,original_csv, output_csv)

csvname = r'D:\Users\twoodard\documents\wv2_boxes_order_fixed.csv'
param_dict["outdir"] = r'd:\PlanetTest\Data\MatchWV2gridcells\OS'
param_dict["start_date_short"] =  '2017-06-30' 
param_dict["end_date_short"] = '2017-08-31'
param_dict["suffix"] = "_SR_OS" 
download_scenes_from_aois_in_csv(csvname, api_key, **param_dict)

ppath = "D:\\PlanetTest\\data\\MatchWV2gridcells\\GS\\"
txtfname = ppath + 'already_downloaded.txt'
list_of_downloaded_files(ppath,txtfname)
original_csv = r'D:\Users\twoodard\documents\wv2_boxes_order_fixed.csv'
output_csv = ppath + 'scenes_to_be_downloaded.csv'
new_csv = remove_downloaded_scenes(txtfname,original_csv, output_csv)

csvname = new_csv
param_dict["outdir"] = r'd:\PlanetTest\Data\MatchWV2gridcells\GS'
param_dict["start_date_short"] =  '2018-01-01' 
param_dict["end_date_short"] = '2018-03-01'
param_dict["suffix"] = "_SR_GS" 
download_scenes_from_aois_in_csv(csvname, api_key, **param_dict)

csvname = r'D:\Users\twoodard\documents\ghana_boxes_order_fixed.csv'
param_dict["outdir"] = r'd:\PlanetTest\Data\GhanaNew'
param_dict["start_date_short"] =  '2017-06-30' 
param_dict["end_date_short"] = '2017-08-31'
param_dict["suffix"] = "_SR_OS" 
download_scenes_from_aois_in_csv(csvname, api_key, **param_dict)
param_dict["start_date_short"] =  '2018-01-01' 
param_dict["end_date_short"] = '2018-03-01'
param_dict["suffix"] = "_SR_GS" 
download_scenes_from_aois_in_csv(csvname, api_key, **param_dict)
#Note - I just found out that the growing season dates may not be the same for Ghana as they are for SA.

#originalname = r'D:\Users\twoodard\documents\wv2_boxes_order_fixed.csv'
#skip_these = r'D:\Users\twoodard\documents\GS_downloaded.txt'
#csvname = remove_downloaded_scenes(skip_these, originalname)
#if csvname == 'Error':
#     exit

#csv_centerpts = r'D:\Users\twoodard\pictures\ghanasites.csv'
#csvname = r'D:\Users\twoodard\documents\lyndon_sites.csv'
#copy_center_pt_csv_to_grid_cell_csv(csv_centerpts,csvname)

#download_and_window_manually()

#csvname = r'D:\Users\twoodard\documents\wv2_boxes_order_fixed.csv'
csvname = r'D:\Users\twoodard\documents\wv2_boxes_order_fixed.csv'
param_dict["outdir"] = r'd:\PlanetTest\Data\MatchWV2gridcells'
param_dict["start_date_short"] =  '2018-01-01' 
param_dict["end_date_short"] = '2018-03-01'
param_dict["suffix"] = "_SR_GS" 
download_scenes_from_aois_in_csv(csvname, api_key, **param_dict)


#csvname = r'D:\Users\twoodard\documents\extents_qual_sites_complete_orig_set.csv'
#csvname = r'D:\Users\twoodard\documents\extents_qual_sites_leftover.csv'
csvname = r'D:\Users\twoodard\documents\wv2_boxes_order_fixed.csv'
param_dict["outdir"] = r'd:\PlanetTest\Data\MatchWV2gridcells'
param_dict["start_date_short"] =  '2017-06-30' 
param_dict["end_date_short"] = '2017-08-31'
param_dict["suffix"] = "_SR_OS" 
download_scenes_from_aois_in_csv(csvname, api_key, **param_dict)

csvname = r'D:\Users\twoodard\documents\extents_qual_sites_complete_orig_set.csv'
param_dict["outdir"] = r'd:\PlanetTest\Data\SA_OffSeason'
param_dict["start_date_short"] =  '2017-06-30' 
param_dict["end_date_short"] = '2018-08-31'
param_dict["suffix"] = "_SR_OS" 
download_scenes_from_aois_in_csv(csvname, api_key, **param_dict)



#csvname = r'D:\Users\twoodard\documents\lyndon_sites_Asamankese_only.csv'
csvname = r'D:\Users\twoodard\documents\lyndon_sites_Asamankese_only - copy.csv'  #This one has completed grid cells removed.  Gets smaller as I debug & test.
param_dict["start_date_short"] =  '2018-02-01'
param_dict["end_date_short"] = '2018-03-31'
download_scenes_from_aois_in_csv(csvname, api_key, **param_dict)

#csvname = r'D:\Users\twoodard\documents\lyndon_sites_all_but_Asamankese.csv'
csvname = r'D:\Users\twoodard\documents\lyndon_sites_all_but_Asamankese-skipped.csv'  #the ones that need to be redone
param_dict["start_date_short"] =  '2018-03-01'
param_dict["end_date_short"] = '2018-04-30'
download_scenes_from_aois_in_csv(csvname, api_key, **param_dict)


#need to download this one by id later:
#20180225_105315_104a

csvname = r'D:\Users\twoodard\documents\california_sites.csv' # California is free. Use for testing.
param_dict["start_date_short"] =  '2018-02-01'
param_dict["end_date_short"] = '2018-03-31'
param_dict["maximgs"] = 1 #Lets speed up the testing process! Just do 1 image per grid cell.
param_dict["asset_type"] = "analytic_sr"
download_scenes_from_aois_in_csv(csvname, api_key, **param_dict)




