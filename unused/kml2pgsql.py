import sys, os, json
def configure():
    with open('settings.json') as f:
        json_data = f.read()
        settings = json.loads(json_data)
        return settings
    return None

files = sys.argv[1:]
operations = open('operations.sql', 'a')

settings = configure()
create = 'CREATE TABLE schools'+' (code BIGINT NOT NULL PRIMARY KEY,name varchar(150), centroid geometry);\n'
operations.write(create)

for file in files:
    table_name = file.split("_")[4].split(".")[0]
    command = 'ogr2ogr -f \"PostgreSQL\" PG:\"host='+settings['host']+' user='+settings['user']+' password='+settings['password']+' dbname='+settings['dbname']+'\" '+file+' -nln '+'"'+table_name+'"\n'
    print command
    alter = 'ALTER TABLE '+'"'+table_name+'" '+'RENAME COLUMN description TO code;\n'
    block_table = '"'+'block_'+table_name[:-1]+'"'
    # create = 'CREATE TABLE '+block_table+' (code BIGINT NOT NULL PRIMARY KEY,name varchar(150), centroid geometry);\n'
    insert = 'INSERT INTO schools'+' SELECT CAST(code AS BIGINT), name, ST_CENTROID(ST_COLLECT(wkb_geometry))  from '+'"'+table_name+'" '+'GROUP BY code, name;\n'
    drop = 'DROP TABLE '+'"'+table_name+'";\n'
    os.popen(command)
    operations.write(alter)
    operations.write(insert)
    operations.write(drop) 
operations.close()
