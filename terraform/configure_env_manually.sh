conda install nb_conda_kernels
conda create --yes --name porder_env --channel conda-forge python=2.7.15 pip ipykernel planet geojson shapely gdal rasterio rasterstats geopy cartopy geopandas contextily pysal pyproj folium scikit-image gdal libgdal kealib geocoder
source activate porder_env
yes | pip install porder
source deactivate
jupyter notebook
