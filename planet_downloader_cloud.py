from geo_utils import GeoUtils
from fixed_thread_pool_executor import FixedThreadPoolExecutor

from sys import stdout
from shapely.geometry import shape
from pprint import pprint
from geojson import Polygon, MultiPolygon
from rtree import index

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

# disable ssl
ssl._create_default_https_context = ssl._create_unverified_context

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format = '%(message)s', datefmt = '%m-%d %H:%M')

config = configparser.ConfigParser()
config.read('cfg/config.ini')
planet_config = config['planet']
imagery_config = config['imagery']
cloud_config = config['cloud_shadow']

cellgrid_buffer = 1 + float(imagery_config['cellgrid_buffer'])
master_grid_path = imagery_config['master_grid_path'] # EPSG:4326

# planet has limitation 5 sec per key (search queries)
threads_number = imagery_config['threads']
if threads_number == 'default':
    threads_number = multiprocessing.cpu_count() * 2 + 1
else:
    threads_number = int(threads_number)

neighbours_executor = FixedThreadPoolExecutor(size = threads_number)

# aoi
for geom in imagery_config['aoi_path']:

features = geojson.load(open(imagery_config['aoi_path']))['features']
actual_aoi = shape(MultiPolygon([Polygon(f['geometry']) for f in features]))
# need to setup jupyter instance on aws where I can test this out tomorrow