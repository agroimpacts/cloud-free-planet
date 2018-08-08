from planet_client import PClientV1
from geo_utils import GeoUtils
from filter_callable import Cloud_Shadow_Stats

from sys import stdout
from shapely.geometry import shape
from pprint import pprint

import psycopg2
import ssl
import geojson
import json
import codecs
import csv
import shutil

import numpy as np
import rasterio
from rasterio import transform
from rasterio.coords import BoundingBox
from rasterio.windows import Window
from datetime import datetime
import concurrent

# AOI
# by AOI generate grid cells
# request scenes by grid cells from planet with cloud detection specified
# 1. choose the first grid cell, request
# 2. get all the gridcells inside the requested scene extent (from csv / file)
# 3. check all of the grid cells cloud coverage
# 4. download this scene
# 5. apply function to do cloud detection (take a solution to delete or not to delete scene finalluy from this s3 bucket)
# 6. create a record grid_cell | tms_uri(s3) => write into the csv file
# 7. create an unstructured cogs compatible json file to make it easier to navigate across these ids

# disable ssl
ssl._create_default_https_context = ssl._create_unverified_context

# local settings, TODO: move into config everything what is possible
APIkey = "***REMOVED***"
resolution = 0.005 / 2
master_grid_path = "/Users/daunnc/Downloads/master_grid.tif" # EPSG:4326
GS = "GS" # growing, wet season
OS = "OS" # off, dry season

# planet has limitation 5 sec per key (search queries)
neighbours_executor = concurrent.futures.ThreadPoolExecutor(5)

# pclient init
pclient = PClientV1(APIkey)
pclient.max_clouds = 0.25  # max proportion of pixels that are clouds
pclient.max_bad_pixels = 0.25 # max proportion of bad pixels (transmission errors, etc.)
pclient.asset_type = "analytic_sr"  # "udm"  #"analytic"  #analytic_sr"
pclient.maximgs = 1  # 15 #10 #20
pclient.output_encoding = 'utf-8'
pclient.output_filename = "output.csv"
pclient.threads_number = 2 # should be number of CPUs

# build a valid dt string from a month number
def dt_construct(month, day = 1, year = 2018, t = "00:00:00.000Z"):
    return "{}-{:02d}-{:02d}T{}".format(year, month, day, t)

def main():
    ext = GeoUtils.define_extent(30, -2, 0.03) # some test AOI to select a subset of extent from the master_grid.tiff

    # 1. Cell ID: this should be unique for the whole raster
    # 2. Country code: integerized country code
    # 3. Country ID: unique cell number within each country
    # 4. dry season start month
    # 5. dry season end month
    # 6. wet season start month
    # 7. wet season end month
    # 2 and 3 combined link to the unique name field in the current ***REMOVED*** database
    master_grid = rasterio.open(master_grid_path)
    rows, cols = master_grid.shape # all pixels of initial master grid
    bounds = master_grid.bounds
    # left = xmin, bottom = ymin, right = xmax, top = ymax
    actual_bounds = GeoUtils.extent_to_BoundingBox(GeoUtils.extent_intersection(GeoUtils.BoundingBox_to_extent(bounds), ext))
    actual_extent = GeoUtils.BoundingBox_to_extent(actual_bounds)

    # returns row, col
    actual_window_min = master_grid.index(actual_bounds.left, actual_bounds.bottom)
    actual_window_max = master_grid.index(actual_bounds.right, actual_bounds.top)
    start_row = min(actual_window_min[0], actual_window_max[0])
    stop_row = max(actual_window_min[0], actual_window_max[0])
    start_col = min(actual_window_min[1], actual_window_max[1])
    stop_col = max(actual_window_min[1], actual_window_max[1])
    actual_window = ((start_row, stop_row), (start_col, stop_col))
    actual_window_width, actual_window_height = stop_col - start_col, stop_row - start_row

    # transofmration for AOI
    actual_transform = transform.from_bounds(
        actual_bounds.left, 
        actual_bounds.bottom, 
        actual_bounds.right, 
        actual_bounds.top, 
        actual_window_width, 
        actual_window_height
    )

    # split bands into separate numpy arrays
    # 1, 2, 3, 4, 5, 6, 7
    cell_id_band, country_code_band, country_id_band, ds_s_band, ds_e_band, ws_s_band, ws_e_band = master_grid.read(window = actual_window)

    # extra band with information about already seen cells
    valid_band = {
        GS: np.full(cell_id_band.shape, False),
        OS: np.full(cell_id_band.shape, False)
    }

    # output CSV file
    fp = codecs.open(pclient.output_filename, "w", pclient.output_encoding)
    writer = csv.writer(fp)

    # print(range(actual_window_height))
    # print(range(actual_window_width))

    for r in range(actual_window_height):
        for c in range(actual_window_width):
            skip_gs, skip_os = valid_band[GS][r, c], valid_band[OS][r, c]
            skip_row = skip_gs & skip_os

            # print("~~~~~~")
            # print((c, r))
            # print("{} & {} = {}".format(skip_gs, skip_os, skip_row))
            # print("~~~~~~")

            if not skip_row:
                # read all metadata
                cell_id = cell_id_band[r, c]
                country_code, country_id = country_code_band[r, c], country_id_band[r, c]
                ds_start, ds_end = ds_s_band[r, c], ds_e_band[r, c]
                ws_start, ws_end = ws_s_band[r, c], ws_e_band[r, c]
                seasons = [(GS, ws_start, ws_end), (OS, ds_start, ds_end)] # dates ranges for the loop
                # GS and OS images should be of the same year
                current_year = datetime.today().year

                print("Processing cell_id {}...".format(cell_id))
                
                # cell grid centroid 
                x, y = transform.xy(actual_transform, r, c)
                
                aoi = GeoUtils.define_aoi(x, y)  # aoi by a cell grid x, y

                for (season_type, m_start, m_end) in seasons:
                    if not valid_band[season_type][r, c]:
                        print("Processing season {}...".format(season_type))

                        geom = {}
                        scene_id = ''

                        # planet analytic_sr stores imagery starting from 2016 year
                        years = list(range(2016, current_year + 1))
                        years.reverse()

                        for yr in years:
                            planet_filters = pclient.set_filters_sr(aoi, start_date = dt_construct(month = m_start, year = yr), end_date = dt_construct(month = m_end, year = yr))
                            res = pclient.request_intersecting_scenes(planet_filters)

                            # pick up scene id and its geometry
                            for item in res.items_iter(pclient.maximgs):
                                # each item is a GeoJSON feature
                                geom = shape(geojson.loads(json.dumps(item["geometry"])))
                                scene_id = item["id"]
                            # record success year
                            if(scene_id != ''):
                                current_year = yr
                                break

                        # mark the current cell grid as already seen
                        if(scene_id != ''):
                            valid_band[season_type][r, c] = True

                            # activation & download
                            # it should be sync, to allow async check of neighbours
                            # output_file = pclient.download_s3(scene_id, season = season_type)
                            local_output_file, output_file = pclient.download_localfs_s3(scene_id, season = season_type)
                            
                            # use custom cloud detection function to calculate shadows
                            cloud_perc, shadow_perc = Cloud_Shadow_Stats(local_output_file, GeoUtils.define_BoundingBox(x, y))
                            print("------------------")
                            print("Cloud_Shadow_Stats: {}".format((cloud_perc, shadow_perc)))
                            print("------------------")

                            # before this step there should be done a custom cloud detection function call
                            base_row = [cell_id, scene_id, season_type, output_file]
                            writer.writerow(base_row)
                            
                            # pprint(base_row)
                            # extent of a polygon to query neighbours
                            # (minx, miny, maxx, maxy)
                            # geom.bounds
                            base_ext = GeoUtils.extent_intersection(actual_extent, GeoUtils.polygon_to_extent(geom))
                            
                            # walk through all cellgrid neighbours
                            # get all row, cals intersection by  
                            sub_window_min = transform.rowcol(actual_transform, base_ext['xmin'], base_ext['ymin'])
                            sub_window_max = transform.rowcol(actual_transform, base_ext['xmax'], base_ext['ymax'])
                            sub_start_row = min(sub_window_min[0], sub_window_max[0])
                            sub_stop_row = max(sub_window_min[0], sub_window_max[0])
                            sub_start_col = min(sub_window_min[1], sub_window_max[1])
                            sub_stop_col = max(sub_window_min[1], sub_window_max[1])

                            # print(range(sub_start_row, sub_stop_row))
                            # print(range(sub_start_col, sub_stop_col))

                            for sr in range(sub_start_row, sub_stop_row):
                                for sc in range(sub_start_col, sub_stop_col):
                                    skip_sub_row = valid_band[season_type][sr, sc]

                                    if not skip_sub_row:
                                        # read all metadata
                                        sub_cell_id = cell_id_band[sr, sc]
                                        sub_country_code, sub_country_id = country_code_band[sr, sc], country_id_band[sr, sc]
                                        sub_ds_start, sub_ds_end = ds_s_band[sr, sc], ds_e_band[sr, sc]
                                        sub_ws_start, sub_ws_end = ws_s_band[sr, sc], ws_e_band[sr, sc]
                                        sub_seasons = [(GS, sub_ws_start, sub_ws_end), (OS, sub_ds_start, sub_ds_end)] # dates ranges for the loop

                                        # neighbours should be in the same period, otherwise we'll try to fetch them later
                                        if(seasons == sub_seasons):
                                            print("Processing sub cell_id {}...".format(sub_cell_id))

                                            sx, sy = transform.xy(actual_transform, sr, sc)

                                            sub_aoi = GeoUtils.define_aoi(sx, sy)  # aoi by a cell grid x, y
                                            
                                            # query planet api and check would this cell grid have good enough cloud coverage for this cell grid
                                            sub_planet_filters = pclient.set_filters_sr(aoi, start_date = dt_construct(month = m_start, year = current_year), end_date = dt_construct(month = m_end, year = current_year), id = scene_id)
                                            res = pclient.request_intersecting_scenes(sub_planet_filters)
                                            
                                            # flag to avoid extra lookup into array
                                            sub_valid = False
                                            # select the only one image as it's the only one
                                            for item in res.items_iter(1):
                                                valid_band[season_type][sr, sc] = True
                                                sub_valid = True
                                                
                                            if sub_valid:
                                                base_sub_row = [sub_cell_id, scene_id, season_type, output_file]
                                                writer.writerow(base_sub_row)
                                                # pprint(base_sub_row)

                        # base_row = [cell_id, scene_id, season_type, ""]
                        # writer.writerow(base_row)
    
    # await all futures
    # pclient.await_downloads()
    print("-------------------")
    print("Results:")
    print("-------------------")
    print("GS: valid {} / {}".format(np.count_nonzero(valid_band[GS]), valid_band[GS].size))
    print("OS: valid {} / {}".format(np.count_nonzero(valid_band[OS]), valid_band[OS].size))
    print("-------------------")

if __name__ == "__main__":
    main()
