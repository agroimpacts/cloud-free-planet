# Insert proj4 strings into PostGIS projections database

# Import Packages
import os
import psycopg2
import yaml

def parse_yaml(input_file):
    """Parse yaml file of configuration parameters."""
    with open(input_file, 'r') as yaml_file:
        params = yaml.load(yaml_file)
    return params

params = parse_yaml(os.path.join(os.environ['PYTHONPATH'],"config_template.yaml"))

# Define functions
def find_between(s, start, end):
  return (s.split(start))[1].split(end)[0]

# Connect to Postgres Database
conn = psycopg2.connect(dbname=['mapper']['db_sandbox_name'], user=params['mapper']['db_username'], password=params['mapper']['db_password'])
curs = conn.cursor()

# Define insert template
template = """INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) \
values ( 9%s, 'map_af', %s, '%s ', 'PROJCS["Albers_Equal_Area_Conic_Africa_%s",\
GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563],TOWGS84[0,0,0]],\
PRIMEM["Greenwich",0],UNIT["Degree",0.01745329251994328]],PROJECTION["Albers_Conic_Equal_Area"],\
PARAMETER["Standard_Parallel_1",%s],PARAMETER["Standard_Parallel_2",%s],\
PARAMETER["Latitude_of_Center",%s],PARAMETER["Longitude_of_Center",%s],\
PARAMETER["False_Easting",%s],PARAMETER["False_Northing",%s],UNIT["Meter",1]]');"""

# Import proj4 strings
with open("proj4_strings.txt",'r') as f:
    proj4_strings = f.read().splitlines()

# Loop over all items
for i in range(len(proj4_strings)):
    proj4 = proj4_strings[i]
    
    # Find values in proj4 strings
    num = str(i+1)
    sp1 = find_between(proj4, "lat_1=", " +lat_2")
    sp2 = find_between(proj4, "lat_2=", " +lat_0")
    lac = find_between(proj4, "lat_0=", " +lon_0")
    loc = find_between(proj4, "lon_0=", " +x_0")
    fae = find_between(proj4, "x_0=", " +y_0")
    fan = find_between(proj4, "y_0=", " +datum")
    
    # Insert values into template
    sql=(template%(num,num,proj4,num,sp1,sp2,lac,loc,fae,fan))
    curs.execute(sql)
    conn.commit()

# Close database connection
conn.close
