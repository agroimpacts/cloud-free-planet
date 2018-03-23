"""This program calls download_planet_data in planet_download.py using hardcoded variables that are for testing purposes
    To run this, you should have a folder called d:\planettest\data on your computer.
    Or you can just change the hard-coded folder name below.
    Use this as an example of how to prepare your parameters to call that function
"""

import os
import sys
from planet_download import download_planet_data


#params expected are outdir,sdate,edate,maximgs,xmin1,xmax1,ymin1,ymax1,max_clouds,bad_pixels,assettype,lst_item_types
param_dict = {}
param_dict["outdir"] = r'd:\PlanetTest\Data'
param_dict["xmin1"] = -122.5
param_dict["xmax1"] = -122.495
param_dict["ymin1"] = 37.74
param_dict["ymax1"] = 37.745
param_dict["sdate"] = '2017-07-01'
param_dict["edate"] = '2017-07-30'
param_dict["max_clouds"] = 0.04  #max proportion of pixels that are clouds
param_dict["bad_pixels"] = 0.04  #max proportion of bad pixels (transmission errors, etc.)
param_dict["assettype"] = "udm"  #"analytic"
param_dict["maximgs"] = 20        #This will be higher, e.g. 20, 50, 100, 200.  Right now it is low for testing purposes
param_dict["lst_item_types"] = ['PSScene4Band']  #needs to be a list

output_fname = download_planet_data(**param_dict)
print('Output file = ', output_fname)


