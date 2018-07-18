from planet_client import PClientV1
from geo_utils import GeoUtils

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

# pclient init
pclient = PClientV1(APIkey)
pclient.max_clouds = 0.25  # max proportion of pixels that are clouds
pclient.max_bad_pixels = 0.25 # max proportion of bad pixels (transmission errors, etc.)
pclient.asset_type = "analytic_sr"  # "udm"  #"analytic"  #analytic_sr"
pclient.maximgs = 1  # 15 #10 #20
pclient.output_encoding = 'utf-8'
pclient.output_filename = "output.csv"

def main():
    # psql connection // TODO: abstracted out?
    conn = psycopg2.connect('host=sandbox.crowdmapper.org dbname=AfricaSandbox user=***REMOVED*** password=***REMOVED***')
    curs = conn.cursor()
    ext = GeoUtils.define_extent(30, -2, 10) # some test AOI to select a subset of extent from psql

    # query for test purposes only, limits all results by 10
    query_template = """SELECT * FROM public.master_grid
    WHERE x >= %s AND x <= %s AND y >= %s AND y <= %s
    ORDER BY gid LIMIT 10"""

    query = query_template % (ext['xmin'], ext['xmax'], ext['ymin'], ext['ymax'])
    curs.execute(query)

    valid_arr = []

    # should be uploaded into s3 bucket afterall
    with codecs.open(pclient.output_filename, "w", pclient.output_encoding) as fp:
        writer = csv.writer(fp)
        # (grid_cell_id, scene_id, COG URI)
        # writer.writerow(row)
        # (gid, id, x, y, name, fwts, avail)
        for row in curs:
            if len(valid_arr) == 1000:
                valid_arr = []
            # skip flag
            skip_row = False

            # find valid if present 
            try:
                idx = valid_arr.index(row[1])
                skip_row = True
                del valid_arr[idx]
            except:
                pprint("Processing {}...".format(row[1]))

            if not skip_row:
                aoi = GeoUtils.define_aoi(row[2], row[3])  # aoi by a cell grid x, y
                planet_filters = pclient.set_filters_sr(aoi)
                res = pclient.request_intersecting_scenes(planet_filters)
                geom = {}
                scene_id = ''

                # pick up scene id and its geometry
                for item in res.items_iter(pclient.maximgs):
                    # each item is a GeoJSON feature
                    geom = shape(geojson.loads(json.dumps(item["geometry"])))
                    scene_id = item["id"]

                # activation & download
                output_file = pclient.download_s3(scene_id)
                # before this step there should be done a custom cloud detection function call
                base_row = [row[1], scene_id, output_file]
                writer.writerow(base_row)
                # pprint(base_row)
                # extent of a polygon to query by
                # (minx, miny, maxx, maxy)
                base_ext = geom.bounds
                # query all cellgrid neighbours
                sub_query = query_template % (base_ext[0], base_ext[2], base_ext[1], base_ext[3])
                # sub cursor
                sub_curs = conn.cursor()
                sub_curs.execute(sub_query)
                # (gid, id, x, y, name, fwts, avail)
                for sub_row in sub_curs:
                    # skip flag
                    skip_sub_row = False
                    
                    # find valid if present 
                    try:
                        valid_arr.index(sub_row[1])
                        skip_sub_row = True
                    except:
                        pprint("Processing sub row {}...".format(sub_row[1]))

                    if not skip_sub_row:
                        sub_aoi = GeoUtils.define_aoi(row[2], row[3])  # aoi by a cell grid x, y
                        # query planet api and check would this cell grid have good enough cloud coverage for this cell grid
                        sub_planet_filters = pclient.set_filters_sr(aoi, id = scene_id)
                        res = pclient.request_intersecting_scenes(planet_filters)

                        # if valid than add into array of valid items
                        sub_valid = False
                        # select the only one image as it's the only one
                        for item in res.items_iter(1):
                            sub_valid = True

                        if sub_valid:
                            valid_arr.append(row[1])
                            base_sub_row = [sub_row[1], scene_id, output_file]
                            writer.writerow(base_sub_row)
                            # pprint(base_sub_row)

if __name__ == "__main__":
    main()
