from planet_client import PClientV1
from geo_utils import GeoUtils
from filter_callable import cloud_shadow_stats_config, nodata_stats
from fixed_thread_pool_executor import FixedThreadPoolExecutor
from psql_planet_client import PSQLPClient
from rf_client import RFClient

from sys import stdout
from shapely.geometry import shape
from pprint import pprint
from geojson import Polygon, MultiPolygon
from rtree import index

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
import logging
import concurrent
import configparser
import multiprocessing

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

# read config
config = configparser.ConfigParser()
config.read('cfg/config.ini')
planet_config = config['planet']
imagery_config = config['imagery']
cloud_config = config['cloud_shadow']
test = json.loads(imagery_config['test'].lower())

# extra csv input flags
with_csv = json.loads(imagery_config['with_csv'].lower())
csv_only = json.loads(imagery_config['csv_only'].lower())
csv_points = imagery_config['csv_points']
csv_mode = imagery_config['csv_mode']
csv_header = ["cell_id", "scene_id", "col", "row", "season", "url", "tms_url"]

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format = '%(message)s', datefmt = '%m-%d %H:%M')

api_key = planet_config['api_key']
resolution = float(imagery_config['resolution']) # 0.005 / 2
master_grid_path = imagery_config['master_grid_path'] # EPSG:4326
GS = "GS" # growing, wet season
OS = "OS" # off, dry season

# planet has limitation 5 sec per key (search queries)
threads_number = imagery_config['threads']
if threads_number == 'default':
    threads_number = multiprocessing.cpu_count() * 2 + 1
else:
    threads_number = int(threads_number)

neighbours_executor = FixedThreadPoolExecutor(size = threads_number)

# pclient init
pclient = PClientV1(api_key, config)

# rfclient init
rfclient = RFClient(config)

# psql client init
psqlclient = PSQLPClient(config)
psqlclient.connect()

# aoi
features = geojson.load(open(imagery_config['aoi']))['features']
actual_aoi = shape(MultiPolygon([Polygon(f['geometry']) for f in features]))

def main_csv():
    # sequence of cellgrids to walkthrough
    cell_grids = [ ]

    # build an SRTree
    idx = index.Index()
    reader = csv.reader(open(csv_points))
    next(reader, None)  # skip headers
    for line in reader:
        (cell_id, x, y, cell_name) = line
        typed_line = (int(cell_id), float(x), float(y), cell_name)
        extent = GeoUtils.define_extent(float(x), float(y))
        idx.insert(int(cell_id), (extent['xmin'], extent['ymin'], extent['xmax'], extent['ymax']), obj = typed_line)
        cell_grids.append(typed_line)

    master_grid = rasterio.open(master_grid_path)
    actual_extent = GeoUtils.BoundingBox_to_extent(master_grid.bounds)

    # split bands into separate numpy arrays
    # 1, 2, 3, 4, 5, 6, 7
    cell_id_band, country_code_band, country_id_band, ds_s_band, ds_e_band, ws_s_band, ws_e_band = master_grid.read()

    # valid cell_grids / already seen and valid ones
    valid_cell_grids = {
        GS: np.full(cell_id_band.shape, False),
        OS: np.full(cell_id_band.shape, False)
    }

    # output CSV file
    fp = codecs.open(filename = pclient.output_filename, mode = csv_mode, encoding = pclient.output_encoding) # buffering = 20*(1024**2)
    if csv_only:
        fp = codecs.open(filename = pclient.output_filename_csv, mode = csv_mode, encoding = pclient.output_encoding)

    writer = csv.writer(fp)
    writer.writerow(csv_header)

    for line in cell_grids:
        (cell_id, x, y, cell_name) = line
        r, c = master_grid.index(x, y)

        skip_gs, skip_os = valid_cell_grids[GS][r, c], valid_cell_grids[OS][r, c]
        skip_row = skip_gs & skip_os

        if not skip_row:
            country_code, country_id = country_code_band[r, c], country_id_band[r, c]
            ds_start, ds_end = ds_s_band[r, c], ds_e_band[r, c]
            ws_start, ws_end = ws_s_band[r, c], ws_e_band[r, c]
            seasons = [(GS, ws_start, ws_end), (OS, ds_start, ds_end)] # dates ranges for the loop
            valid_dates = (ds_start >= 0 and ds_start <= 12) and (ds_end >= 0 and ds_end <= 12) and (ws_start >= 0 and ws_start <= 12) and (ws_end >= 0 and ws_end <= 12)

            if not valid_dates:
                logger.info("cell_id {} is not valid (bad dates data, check the AOI you are querying for)".format(cell_id))
            else: 
                # GS and OS images should be of the same year
                current_year_start = datetime.today().year
                current_year_end = current_year_start

                logger.info("Processing cell_id {}...".format(cell_id))
                    
                aoi = GeoUtils.define_aoi(x, y)  # aoi by a cell grid x, y

                psql_rows = []
                for (season_type, m_start, m_end) in seasons:
                    if not valid_cell_grids[season_type][r, c]:
                        logger.info("Processing season {}...".format(season_type))

                        geom = {}
                        scene_id = ''
                        output_file = ''
                        output_localfile = ''

                        # planet analytic_sr stores imagery starting from 2016 year
                        years = list(range(2016, current_year_start + 1))
                        years.reverse()

                        for yr in years:
                            yr_start = yr
                            yr_end = yr

                            if m_start <= m_end:
                                yr_start = yr
                                yr_end = yr
                            else:
                                yr_start = yr - 1
                                yr_end = yr

                            planet_filters = pclient.set_filters_sr(aoi, start_date = dt_construct(month = m_start, year = yr_start), end_date = dt_construct(month = m_end, year = yr_end))
                            res = pclient.request_intersecting_scenes(planet_filters)

                            # pick up scene id and its geometry
                            for item in res.items_iter(pclient.maximgs):
                                # each item is a GeoJSON feature
                                geom = shape(geojson.loads(json.dumps(item["geometry"])))
                                scene_id = item["id"]
                                # activation & download
                                # it should be sync, to allow async check of neighbours
                                output_localfile, output_file = pclient.download_localfs_s3(scene_id, season = season_type)
                                # use custom cloud detection function to calculate clouds and shadows
                                cloud_perc, shadow_perc = cloud_shadow_stats_config(output_localfile, GeoUtils.define_BoundingBox(x, y), cloud_config)
                                # check if cell grid is good enough
                                if (cloud_perc <= pclient.max_clouds):
                                    break
                                else: 
                                    scene_id = ''

                            # record success year
                            if(scene_id != ''):
                                current_year_start = yr_start
                                current_year_end = yr_end
                                break

                        # mark the current cell grid as already seen
                        if(scene_id != ''):
                            valid_cell_grids[season_type][r, c] = True

                            tms_uri = rfclient.create_tms_uri(scene_id, output_file)
                            base_row = [cell_id, scene_id, c, r, season_type, output_file, tms_uri]
                            writer.writerow(base_row)
                            psql_rows.append(('planet', scene_id, str(cell_id), season_type, str(global_col), str(global_row), output_file, tms_uri))
                                
                            # logger.debug(base_row)
                            # extent of a polygon to query neighbours
                            # (minx, miny, maxx, maxy)
                            # geom.bounds
                            base_ext = GeoUtils.extent_intersection(actual_extent, GeoUtils.polygon_to_extent(geom))

                            def sync(sub_row):
                                sub_cell_id, sx, sy, sub_name = sub_row.object

                                global_sub_row, global_sub_col = master_grid.index(sx, sy)

                                # polygon to check would it intersect initial AOI
                                sub_poly = GeoUtils.define_polygon(sx, sy)

                                skip_sub_row = valid_cell_grids[season_type][sr, sc]
                                
                                if not skip_sub_row:
                                    # read all metadata
                                    sub_country_code, sub_country_id = country_code_band[sr, sc], country_id_band[sr, sc]
                                    sub_ds_start, sub_ds_end = ds_s_band[sr, sc], ds_e_band[sr, sc]
                                    sub_ws_start, sub_ws_end = ws_s_band[sr, sc], ws_e_band[sr, sc]
                                    sub_seasons = [(GS, sub_ws_start, sub_ws_end), (OS, sub_ds_start, sub_ds_end)] # dates ranges for the loop

                                    # neighbours should be in the same period, otherwise we'll try to fetch them later
                                    if(seasons == sub_seasons):
                                        logger.info("Processing sub cell_id {}...".format(sub_cell_id))

                                        sub_aoi = GeoUtils.define_aoi(sx, sy)  # aoi by a cell grid x, y
                                                    
                                        # query planet api and check would this cell grid have good enough cloud coverage for this cell grid
                                        sub_planet_filters = pclient.set_filters_sr(sub_aoi, start_date = dt_construct(month = m_start, year = current_year_start), end_date = dt_construct(month = m_end, year = current_year_end), id = scene_id)
                                        res = pclient.request_intersecting_scenes(sub_planet_filters)

                                        # use custom cloud detection function to calculate clouds and shadows
                                        sub_cloud_perc, sub_shadow_perc = cloud_shadow_stats_config(output_localfile, GeoUtils.define_BoundingBox(sx, sy), cloud_config)
                                        # check if cell grid is good enough
                                        if (sub_cloud_perc <= pclient.max_clouds):
                                            # flag to avoid extra lookup into array
                                            sub_valid = False
                                            # select the only one image as it's the only one
                                            for item in res.items_iter(1):
                                                valid_cell_grids[season_type][sr, sc] = True
                                                sub_valid = True
                                                            
                                            if sub_valid:
                                                sub_global_row, sub_global_col = master_grid.index(sx, sy)
                                                tms_uri = rfclient.create_tms_uri(scene_id, output_file)
                                                base_sub_row = [sub_cell_id, scene_id, sub_global_col, sub_global_row, season_type, output_file, tms_uri]
                                                writer.writerow(base_sub_row)
                                                psql_rows.append(('planet', scene_id, str(sub_cell_id), season_type, str(sub_global_col), str(sub_global_row), output_file, tms_uri))

                            # query cellgrid neighbours
                            # and walk through all cellgrid neighbours
                            for sub_row in idx.intersection((base_ext['xmin'], base_ext['ymin'], base_ext['xmax'], base_ext['ymax']), objects = True):
                                neighbours_executor.submit(sync, sub_row)

                            # await all neighbours
                            neighbours_executor.drain()
                            # await all downloads
                            pclient.drain()
                            # insert everything into psql
                            psqlclient.insert_rows_by_one_async(psql_rows)

    # await threadpool to stop
    neighbours_executor.close()
    fp.close()
    if csv_only:
        pclient.upload_s3_csv_csv()
        pclient.close()

    psqlclient.close()
    print("-------------------")
    print("CSV DONE")
    print("-------------------")
    

# build a valid dt string from a month number
def dt_construct(month, day = 1, year = 2018, t = "00:00:00.000Z"):
    return "{}-{:02d}-{:02d}T{}".format(year, month, day, t)

def main_json():
    ext = GeoUtils.polygon_to_extent(actual_aoi)

    if test:
        ext = GeoUtils.define_extent(30, -2, 0.03) # some test AOI to select a subset of extent from the master_grid.tiff
        # ext = GeoUtils.define_extent(27.03, -25.98, 0.05)
        # ext = {
        #     "xmin": 27.03,
        #     "ymin": -25.97,
        #     "xmax": 27.08,
        #     "ymax": -25.99
        # }
    
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
    actual_window = GeoUtils.bounds_to_windows(actual_bounds, master_grid)
    ((start_row, stop_row), (start_col, stop_col)) = actual_window
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
    fp = codecs.open(filename = pclient.output_filename, mode = csv_mode, encoding = pclient.output_encoding) # buffering = 20*(1024**2)
    writer = csv.writer(fp)
    if not (with_csv and csv_only):
        writer.writerow(csv_header)

    # logger.info(range(actual_window_height))
    # logger.info(range(actual_window_width))

    for r in range(actual_window_height):
        for c in range(actual_window_width):
            skip_gs, skip_os = valid_band[GS][r, c], valid_band[OS][r, c]

            # cell grid centroid 
            x, y = transform.xy(actual_transform, r, c)

            # polygon to check would it intersect initial AOI
            poly = GeoUtils.define_polygon(x, y)

            skip_row = skip_gs & skip_os & (actual_aoi.intersects(poly) | test)

            if not skip_row:
                # read all metadata
                cell_id = cell_id_band[r, c]
                country_code, country_id = country_code_band[r, c], country_id_band[r, c]
                ds_start, ds_end = ds_s_band[r, c], ds_e_band[r, c]
                ws_start, ws_end = ws_s_band[r, c], ws_e_band[r, c]
                seasons = [(GS, ws_start, ws_end), (OS, ds_start, ds_end)] # dates ranges for the loop
                # check if dates are months, the only way to check data
                valid_dates = (ds_start >= 0 and ds_start <= 12) and (ds_end >= 0 and ds_end <= 12) and (ws_start >= 0 and ws_start <= 12) and (ws_end >= 0 and ws_end <= 12)

                if not valid_dates:
                    logger.info("cell_id {} is not valid (bad dates data, check the AOI you are querying for)".format(cell_id))
                else:
                    # GS and OS images should be of the same year
                    current_year_start = datetime.today().year
                    current_year_end = current_year_start

                    logger.info("Processing cell_id {}...".format(cell_id))
                    
                    aoi = GeoUtils.define_aoi(x, y)  # aoi by a cell grid x, y

                    psql_rows = []
                    for (season_type, m_start, m_end) in seasons:
                        if not valid_band[season_type][r, c]:
                            logger.info("Processing season {}...".format(season_type))

                            geom = {}
                            scene_id = ''
                            output_file = ''
                            output_localfile = ''

                            # planet analytic_sr stores imagery starting from 2016 year
                            years = list(range(2016, current_year_start + 1))
                            years.reverse()

                            for yr in years:
                                yr_start = yr
                                yr_end = yr

                                if m_start <= m_end:
                                    yr_start = yr
                                    yr_end = yr
                                else:
                                    yr_start = yr - 1
                                    yr_end = yr

                                planet_filters = pclient.set_filters_sr(aoi, start_date = dt_construct(month = m_start, year = yr_start), end_date = dt_construct(month = m_end, year = yr_end))
                                res = pclient.request_intersecting_scenes(planet_filters)

                                # pick up scene id and its geometry
                                for item in res.items_iter(pclient.maximgs):
                                    # each item is a GeoJSON feature
                                    geom = shape(geojson.loads(json.dumps(item["geometry"])))
                                    scene_id = item["id"]
                                    # activation & download
                                    # it should be sync, to allow async check of neighbours
                                    output_localfile, output_file = pclient.download_localfs_s3(scene_id, season = season_type)

                                    bbox_local = GeoUtils.define_BoundingBox(x, y)
                                    # nodata percentage
                                    nodata_perc = nodata_stats(output_localfile, bbox_local)
                                    # use custom cloud detection function to calculate clouds and shadows
                                    cloud_perc, shadow_perc = cloud_shadow_stats_config(output_localfile, bbox_local, cloud_config)
                                    # check if cell grid is good enough
                                    if (cloud_perc <= pclient.max_clouds and nodata_perc <= pclient.max_nodata):
                                        break
                                    else: 
                                        scene_id = ''

                                # record success year
                                if(scene_id != ''):
                                    current_year_start = yr_start
                                    current_year_end = yr_end
                                    break

                            # mark the current cell grid as already seen
                            if(scene_id != ''):
                                valid_band[season_type][r, c] = True

                                global_row, global_col = master_grid.index(x, y)
                                tms_uri = rfclient.create_tms_uri(scene_id, output_file)
                                base_row = [cell_id, scene_id, global_col, global_row, season_type, output_file, tms_uri]
                                writer.writerow(base_row)
                                psql_rows.append(('planet', scene_id, str(cell_id), season_type, str(global_col), str(global_row), output_file, tms_uri))
                                
                                # logger.debug(base_row)
                                # extent of a polygon to query neighbours
                                # (minx, miny, maxx, maxy)
                                # geom.bounds
                                base_ext = GeoUtils.extent_intersection(actual_extent, GeoUtils.polygon_to_extent(geom))
                                
                                # walk through all cellgrid neighbours
                                # get all row, cals intersection by  
                                ((sub_start_row, sub_stop_row), (sub_start_col, sub_stop_col)) = GeoUtils.extent_to_windows(base_ext, actual_transform)

                                # logger.info(range(sub_start_row, sub_stop_row))
                                # logger.info(range(sub_start_col, sub_stop_col))

                                def sync(sr, sc):
                                    # sub centroid
                                    sx, sy = transform.xy(actual_transform, sr, sc)

                                    # polygon to check would it intersect initial AOI
                                    sub_poly = GeoUtils.define_polygon(sx, sy)

                                    skip_sub_row = valid_band[season_type][sr, sc] & (actual_aoi.intersects(sub_poly) | test)

                                    if not skip_sub_row:
                                        # read all metadata
                                        sub_cell_id = cell_id_band[sr, sc]
                                        sub_country_code, sub_country_id = country_code_band[sr, sc], country_id_band[sr, sc]
                                        sub_ds_start, sub_ds_end = ds_s_band[sr, sc], ds_e_band[sr, sc]
                                        sub_ws_start, sub_ws_end = ws_s_band[sr, sc], ws_e_band[sr, sc]
                                        sub_seasons = [(GS, sub_ws_start, sub_ws_end), (OS, sub_ds_start, sub_ds_end)] # dates ranges for the loop

                                        # neighbours should be in the same period, otherwise we'll try to fetch them later
                                        if(seasons == sub_seasons):
                                            logger.info("Processing sub cell_id {}...".format(sub_cell_id))

                                            sub_aoi = GeoUtils.define_aoi(sx, sy)  # aoi by a cell grid x, y
                                                    
                                            # query planet api and check would this cell grid have good enough cloud coverage for this cell grid
                                            sub_planet_filters = pclient.set_filters_sr(sub_aoi, start_date = dt_construct(month = m_start, year = current_year_start), end_date = dt_construct(month = m_end, year = current_year_end), id = scene_id)
                                            res = pclient.request_intersecting_scenes(sub_planet_filters)
                                            
                                            sub_bbox_local = GeoUtils.define_BoundingBox(sx, sy)
                                            # nodata percentage
                                            sub_nodata_perc = nodata_stats(output_localfile, sub_bbox_local)
                                            # use custom cloud detection function to calculate clouds and shadows
                                            sub_cloud_perc, sub_shadow_perc = cloud_shadow_stats_config(output_localfile, GeoUtils.define_BoundingBox(sx, sy), cloud_config)
                                            # check if cell grid is good enough
                                            if (sub_cloud_perc <= pclient.max_clouds and sub_nodata_perc <= pclient.max_nodata):
                                                # flag to avoid extra lookup into array
                                                sub_valid = False
                                                # select the only one image as it's the only one
                                                for item in res.items_iter(1):
                                                    valid_band[season_type][sr, sc] = True
                                                    sub_valid = True
                                                            
                                                if sub_valid:
                                                    sub_global_row, sub_global_col = master_grid.index(sx, sy)
                                                    tms_uri = rfclient.create_tms_uri(scene_id, output_file)
                                                    base_sub_row = [sub_cell_id, scene_id, sub_global_col, sub_global_row, season_type, output_file, tms_uri]
                                                    writer.writerow(base_sub_row)
                                                    psql_rows.append(('planet', scene_id, str(sub_cell_id), season_type, str(sub_global_col), str(sub_global_row), output_file, tms_uri))

                                for sr in range(sub_start_row, sub_stop_row):
                                    for sc in range(sub_start_col, sub_stop_col):
                                        neighbours_executor.submit(sync, sr, sc)
                                
                                # await all neighbours
                                neighbours_executor.drain()
                                # await all downloads
                                pclient.drain()
                                # insert everything into psql
                                psqlclient.insert_rows_by_one_async(psql_rows)

                            # base_row = [cell_id, scene_id, season_type, ""]
                            # writer.writerow(base_row)

    # await threadpool to stop
    neighbours_executor.close()
    fp.close()
    pclient.upload_s3_csv()
    pclient.close()
    psqlclient.close()
    print("-------------------")
    print("Results:")
    print("-------------------")
    print("GS: valid {} / {}".format(np.count_nonzero(valid_band[GS]), valid_band[GS].size))
    print("OS: valid {} / {}".format(np.count_nonzero(valid_band[OS]), valid_band[OS].size))
    print("-------------------")

def main():
    if csv_only and with_csv:
        main_csv()
    elif with_csv:
        main_csv() 
        main_json()
    else:
        main_json()

if __name__ == "__main__":
    main()
