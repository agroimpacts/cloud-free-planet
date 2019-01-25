conda create --yes --name porder_env --channel conda-forge python=2.7.15 pip planet geojson shapely $
source activate porder_env
yes | pip install porder

