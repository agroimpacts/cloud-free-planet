# Planet downloader scripts

A set of scripts to download a minimal `master_gird` coverage of cloudless planet scenes.

- [Environment](#environment)
- [Usage](#usage)
- [Docker](#docker)
- [config.ini description](#configini-description)
- [scripts description](#scripts-description)
- [PSQL table description](#psql-table-description)
- [AWS](#aws)
- [Local workflow example](#local-workflow-example)
- [AWS ECS workflow example](#aws-ecs-workflow-example)

### Environment

You'd need to have installed `Python 3` on your machine and installed `AWS` credentials, 
or is is possible run eveyrthing through `Docker`.

Be sure that all neccesary changes were introduced into the [cfg/confing.ini](./cfg/config.ini.template) file.

### Usage

- Install all python deps: `pip install -r requirements.txt`
- Run downloader script: `python planet_download_tiff.py`

### Docker

- Build a local docker image: `docker-compose build`
- Run downloader script: `docker-compose run planet-downloader`

NOTICE: It can be also required to introduce all necessary changes into `docker-compose.yml` file.

### config.ini description

```ini
[planet] # planet settings
api_key: <none> # planet API key

[imagery] # imagery settings
local_mode: False # local mode means to donwload everything into local catalog without S3 uploads
test: false # use a small test AOI
aoi: cfg/ghana_aoi.geojson # path to a desired AOI
with_csv: True # to use ot not to use csv_points as an extra area of intrest
csv_only: True # to use input csv file as the only aoi
csv_mode: a # mode to open the output csv file (for instane a - append, w - write, etc.)
csv_points: cfg/individual_sites_needing_images.csv # path to an extra AOI file
resolution: 0.025 # master_grid cells resolution
master_grid_path: s3://activemapper/grid/master_grid.tif # path to a master_grid, can be S3 or local
max_clouds: 0.01 # max clouds perc 
max_shadows: 0.01 # max shadows perc
max_bad_pixels: 0.03 # max bad pixels perc
max_nodata: 0.01 # max nodata perc
maximgs: 10 # max images to try per cell grid
output_encoding: utf-8 # output csv files encoding
output_filename: catalog/planet_catalog.csv # output catalog file path
output_filename_csv: catalog/planet_catalog_csv.csv # output csv file path
threads: default # number of threads
catalog_path: catalog/ # local catalog path
s3_catalog_bucket: activemapper # s3 target bucket
s3_catalog_prefix: planet # s3 target prefix
with_analytic: False # download analytic product in addition to a default analytic_sr
with_analytic_xml: False # download analytic_xml product in addition to a default analytic_sr
with_visual: False # download visual product in addition to a default analytic_sr

[database] # database settings
host: <none> # address of the PSQL database
dbname: AfricaSandbox # dbname
user: <none> # user
password: <none> # password
master_grid_table: master_grid # master_grid table name (optional)
scene_data_table: scenes_data # scenes data table
enabled: Flase # to write output into PSQL or not

[cloud_shadow] # cloud detection function settings
cloud_val: 1500
eccentricity_val: 0.95
area_val: 200
shadow_val: 1500
land_val: 1000
peri_to_area_val: 0.3

[rasterfoundry] # RF credentials
enabled: False # to generate or not to generate TMS link
api_key: <none> # api key 
api_uri: app.rasterfoundry.com # uri to rf
visibility: PRIVATE # project visibility 
tileVisibility: PRIVATE # tile visibility
```

### Scripts description

- [filter_callable.py](./filter-callable.py) - cloud detection function implementation
- [fixed_thread_pool_executor.py](./fixed_thread_pool_executor.py) - fixed thread pool executor
- [geo_utils.py](./geo-utils.py) - differnet GIS helper functions to produce operations on extents
- [planet_client.py](./planet_client.py) - planet client script
- [planet_download_tiff.py](./planet_download_tiff.py) - the main script to populate catalog
- [psql_planet_client.py](./psql_planet_client.py) - script to interact with PSQL
- [rf_client.py](./rf_client.py) - script to interact with RF API
- [radiantearth_register.py](./radiantearth_register.py) - script to generate TMS URIs for the input CSV catalog (required in case TMS uris were not generated via `planet_download_tiff.py`).

### PSQL table description

```sql
CREATE TABLE scenes_data (
    provider VARCHAR(24) NOT NULL,
    scene_id VARCHAR(128) NOT NULL,
    cell_id INTEGER NOT NULL,
    season VARCHAR(2) NOT NULL,
    global_col INTEGER NULL,
    global_row INTEGER NULL,
    url VARCHAR(255) NULL,
    tms_url TEXT NULL,
    date_time TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY(provider, cell_id, season)
);
```

### AWS

Install and confgiure AWS ECS CLI
  - https://github.com/aws/amazon-ecs-cli
  - https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_CLI_tutorial_EC2.html 

Usual commands descriptions you would have to use:
- `make login-aws-registry` to authorize in ECS AWS Registry to push docker image
- `docker-compose build` to build docker image and after that push it via `docker push 554330630998.dkr.ecr.us-east-1.amazonaws.com/planet-downloader`
- `make configure-cluster` to configure cluster
- `make cluster-up` to run ECS cluster
- `make run-task` to start planet downloader task
- `make stop-task` to stop task
- `make cluster-down` to kill the cluster
- `make run-local` to run docker-compose locally

### Local workflow example

Don't forget to introdcue all the changes into config files before building the image or running the script!

```bash
# build an image
docker-compose build

# run through docker
make run-local

# OR
# in case you want to run it without docker
python planet_download_tiff.py
```

### AWS ECS workflow example

Don't forget to introdcue all the changes into config files before building the image or running the script!

```bash
# login into AWS ECS registry
make login-aws-registry

# build an image
docker-compose build

# tag latest image with any tag you want
docker tag 554330630998.dkr.ecr.us-east-1.amazonaws.com/planet-downloader:latest 554330630998.dkr.ecr.us-east-1.amazonaws.com/planet-downloader:my-fancy-tag

# push it into AWS ECS registry
docker push 554330630998.dkr.ecr.us-east-1.amazonaws.com/planet-downloader:my-fancy-tag

# introduce changes into deployment/docker-compose.yml file
# change the tag of the image

# run cluster
make cluster-up

# run ECS task
make run-task

# find logs here (AWS CloudWatch): 
# https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logEventViewer:group=ecs;stream=planet-downloader/planet-downloader/e677ac0d-2440-4ab3-bc1e-a45280476bae;start=2018-08-27T15:38:08Z
# WARN: this is the example URL

# after finishing your work kill the cluster
make cluster-down
```

### Docker

List of published docker images:

- test docker image (with enabled test mode): `554330630998.dkr.ecr.us-east-1.amazonaws.com/planet-downloader:test`
- csv only docker image: `554330630998.dkr.ecr.us-east-1.amazonaws.com/planet-downloader:csv_only`
- geojson Ghana only docker image: `554330630998.dkr.ecr.us-east-1.amazonaws.com/planet-downloader:ghana_geojson_only`
- both csv and Ghana json download `554330630998.dkr.ecr.us-east-1.amazonaws.com/planet-downloader:ghana`
