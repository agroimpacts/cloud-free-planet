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
import pyatsa_configs
import pytest


ATSA_DIR="/home/rave/cloud-free-planet/atsa-test-unzipped/"
img_path = os.path.join(ATSA_DIR, "planet-pyatsa-test/stacked_larger_utm.tif")

@pytest.fixture
def configs():
    return pyatsa_configs.ATSA_Configs(img_path, ATSA_DIR)



def test_t_series_shape(configs):
    assert len(configs.t_series.shape) > 0
