# pyATSA

atsa-python contains working scripts to port the original atsa-idl code written by Zhu and Helmer. But the up to date work is currently happening in notebooks/atsa-python-scratch.ipynb, since porting the code requires a lot of interactive profiling and debugging. 

The code that is so far working well is the calculation of HOT (Haze optimized transform) for each image. The IDL code implements a single kmeans model by sampling pixels across the time series of HOT indices. I've implemented both this sampling approach and an approach that runs a new kmeans model for each image. Profiling this is in the works, tentatively it seems that there is a lot of variation between images in HOT that are causing both approaches to run into different problems, see the github issues. 

Once kmeans is run, the upper threshold from the time series is calculated and the masks are refined. It helps to follow the idl code as a guide, along with the paper. Below are some notes on the IDL code to help follow along.

To compare pyatsa to IDL it is necessary to have IDL and ENVI installed. then:

  1. Start the idl ide by calling `idlde` in the terminal

  2. Run `ENVI` in the idlde, isnce ENVI functions are required to open the time series file

  3. run `CD, "<path to directory with ATSA-Planet.pro>"`

  4. Compile the ATSA-Planet.pro file with `.r ATSA-Planet.pro`

  5. Call the idl script with `ATSA-Planet`

#### notes on IDL code follow the values to determine what conditions to use in python

The mask values are as follows (everything starts as 1 and is updated) and the water mask is 0 value where water, 1 where there is not water

* 3 - background/SLC errors, missing data
* 2 - cloud (see lines 365 through 378)
* 1 - clear land (see lines 323 through 331, where idl returns 1 or 0 from ge condition)


# Planet downloader scripts

A set of scripts to download a minimal `master_grid` coverage of cloudless planet scenes.

#### TOC
- [Environment](#environment)
- [Usage](#usage)
- [Docker](#docker)
- [config.ini description](#config.ini-description)
- [scripts description](#scripts-description)
- [PSQL table description](#psql-table-description)
- [AWS](#aws)
- [Local workflow example](#local-workflow-example)
- [AWS ECS workflow example](#aws-ecs-workflow-example)
- [Test downloading for a small area](#test-downloading-for-a-small-area)
- [ A csv only, no database write example](#a-csv-only-no-database-write-example)
- [Build COG Overviews](#build-cog-overviews)

### Environment

You'll need to have installed `Python 3` on your machine and installed `AWS` credentials, or it is possible run eveyrthing through `Docker`.

Be sure that all neccesary changes were introduced into the [cfg/config.ini](./cfg/config.ini.template) file.

### Usage

- Install all python deps: `pip install -r requirements.txt`
- Run downloader script: `python planet_download_tiff.py`

### Docker

- Build a local docker image: `docker-compose build`
- Run downloader script: `docker-compose run planet-downloader`

NOTES: 
- It may also be required to introduce all necessary changes into `docker-compose.yml` file. 
- You will have to install docker locally if you don't already have it. 

[Back to TOC](#toc) 

### config.ini description

A [template](https://github.com/agroimpacts/mapperAL/blob/devel/spatial/python/planet/cfg/config.ini.template) for the `config.ini` file is provided in cfg/. You will have to rename this from `config.ini.template` to `config.ini`, save it to the same location, and fill in/change the necessary parameter values. *Do not commit config.ini*, as this can expose private credentials to the public.    

```ini
[planet] # planet settings
api_key: <none> # planet API key

[imagery] # imagery settings
local_mode: False # local mode means to download everything into local catalog without S3 uploads
s3_only: False # use only S3 without local files download, WARN: this may lead to data corruption on S3
test: False # use a small test AOI
aoi: cfg/ghana_aoi.geojson # path to a desired AOI
with_csv: True # to use ot not to use csv_points as an extra area of intrest
csv_only: True # to use input csv file as the only aoi
csv_mode: a # mode to open the output csv file (for instance a - append, w - write, etc.)
csv_points: cfg/individual_sites_needing_images.csv # path to an extra AOI file
cellgrid_buffer: 0.05 # cellgrids extent buffer
master_grid_path: s3://activemapper/grid/master_grid.tif # path to a master_grid, can be S3 or local
max_clouds_initial: 0.2 # max clouds in total scene, for initial Planet query
max_clouds: 0.01 # max clouds perc in cell
max_shadows: 0.01 # max shadows perc in cell
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
with_immediate_cleanup: True # cleanup local catalog after performing all operations on the local file

[database] # database settings
host: <none> # address of the PSQL database
dbname: AfricaSandbox # dbname
user: <none> # user
password: <none> # password
master_grid_table: master_grid # master_grid table name (optional)
scene_data_table: scenes_data # scenes data table
enabled: True # to write output into PSQL or not

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

[Back to TOC](#toc) 

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

[Back to TOC](#toc) 

### AWS

Install and confgiure AWS ECS CLI
  - https://github.com/aws/amazon-ecs-cli
  - https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_CLI_tutorial_EC2.html 

Install and configure AWS CLI and Docker
  - TIP: don't forget to add your user into `docker` user group after its installation: `sudo usermod -aG docker your-user`
  - if you still run into permissions issues it is because of past `sudo` use. Run the following and then log in/log out
  -  `sudo chown -R user:usergroup /home/user/.docker` and `sudo chown -R user:usergroup /home/user/mapperAL/spatial/python/planet`

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
[Back to TOC](#toc) 

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

# only needs to be run once per user
make configure-cluster

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
[Back to TOC](#toc) 

### Test downloading for a small area

You might find it beneficial to run a small test area.  This can be achieved in several ways: 

1. Define the test extent within the code itself: 

    - Go [here](https://github.com/agroimpacts/mapperAL/blob/a938547c2404eb470038e8ec379d6005b0d35231/spatial/python/planet/planet_download_tiff.py#L303) and set the test extent you want (provide the x, y coordinates of the centerpoint and then the buffer size in decimal degrees, e.g. 0.05, 0.1)
    - In `config.ini`, change the [test](https://github.com/agroimpacts/mapperAL/blob/a938547c2404eb470038e8ec379d6005b0d35231/spatial/python/planet/cfg/config.ini.template#L7) and [with_csv](https://github.com/agroimpacts/mapperAL/blob/a938547c2404eb470038e8ec379d6005b0d35231/spatial/python/planet/cfg/config.ini.template#L9) parameters to `False`.  
    - Also in `config.ini`, change the name of the [output_filename](https://github.com/agroimpacts/mapperAL/blob/a938547c2404eb470038e8ec379d6005b0d35231/spatial/python/planet/cfg/config.ini.template#L21) to something intelligible indicating that you are making a test catalog, e.g. planet_catalog_test.csv.  Note that you cannot use the [csv_only](https://github.com/agroimpacts/mapperAL/blob/a938547c2404eb470038e8ec379d6005b0d35231/spatial/python/planet/cfg/config.ini.template#L10) if you have set `test: False`. 
  
2. Provide your own AOI, or list of cell IDs in a csv.  
    - Example files: `ghana_aoi.geojson`; `individual_sites_needing_images.csv`
    - The second two steps above apply here. 

A note about test mode: you can only write your test output to a csv. It will not write to _scenes_data_. This helps avoid conflicts between jobs run by multiple users.

[Back to TOC](#toc) 

### A csv only, no database write example

Say you have small number of sites for which you want imagery.  These sites are not contiguous, so defining a geojson AOI is tricky, so a csv of cell id, name, and coordinates is the way to go. Let's also say that there is another downloader running concurrently that is writing its outputs to the `scenes_data` table in the database. In this case, you will want to avoid having this new job also write to the database to prevent race conditions. Such up your `config.ini` to have these options:

```
...
[imagery]
with_csv: True
csv_only: True
csv_points: cfg/<your-csv-name>.csv
...
[database]
host: ip-172-31-39-38.ec2.internal
enabled: False
```

Then run your job. After it runs, you can transfer the contents of your CSV to `scenes_data`. 

[Back to TOC](#toc) 

### Docker

List of published docker images:

- test docker image (with enabled test mode): `554330630998.dkr.ecr.us-east-1.amazonaws.com/planet-downloader:test`
- csv only docker image: `554330630998.dkr.ecr.us-east-1.amazonaws.com/planet-downloader:csv_only`
- geojson Ghana only docker image: `554330630998.dkr.ecr.us-east-1.amazonaws.com/planet-downloader:ghana_geojson_only`
- both csv and Ghana json download `554330630998.dkr.ecr.us-east-1.amazonaws.com/planet-downloader:ghana`

[Back to TOC](#toc) 

### Build COG Overviews
COGs that are created from a machine learning process will need to make a seperate call to the rfclient to create
rasterfoundry projects for the COGs and make tms uris for each COG. The program `tms_uri_from_cog.py` wraps the rfclient
to process an s3 prefix that contains COGs. Call `python tms_uri_from_cog.py --help` for a description:

```
Takes as inputs a bucket and prefix that specify
the location on s3 that contains COGs that can be 
used to make overviews, allowing COGs to be visualized 
on rasterfoundry next to planet imagery and other COGs. 
Suffix is specified as the ending chracters to filter files 
by like 'iteration12.tif'.
Example: python tms_uri_from_cog.py activemapper classified-images/GH0421189_GH0493502 iteration12.tif
```
    
[Back to TOC](#toc) 
