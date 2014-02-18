#script

from osgeo import ogr    
import glob, sys, os, subprocess, re, getpass
import psycopg2 as psy

# Hard coded for now, replace with arguments
mtype = 'ma'  # args[0], 'tr' for training case, 'ma' for test case, and maybe 'qa' if this script gets built out for cleaning qaqc maps. 
assignmentid = '24DF395SW6NG74QIZNEJEYF1HHKFTN'  #  args[1] 
testing = "yes"  # args[2]  yes = print comments, keep temp shps; no = no comments and remove temp shps; comments = print comments but remove temp shapes
tryid = 0  #args[3]  # try id for qualification maps

# Specify whether qual or production maps being cleaned
if mtype == 'ma':
    #exstring = "SELECT for update from "
    map_table = 'user_maps'
    assignment_type = 'assignment_id'
    trystr = "" 
elif mtype == 'tr':
    map_table = 'qual_user_maps'
    assignment_type = 'training_id'
    trystr = ',try'

# turn on script for checking where we are working here
euname = getpass.getuser()
if euname == "sandbox":
    sandbox = True
    uname = "sandbox"
elif euname == "mapper":
    sandbox = False
    uname = "mapper"
elif euname == "lestes":  # comment this out in production
    sandbox = True
    uname = "sandbox"
else: 
   sys.exit("Always run under mapper or sandbox users")

# Set up some file paths
project_root = "/u/" + uname + "/afmap"  # project root
cleaning_dir = project_root + "/laundromat"  # directory for temporary maps
os.chdir(cleaning_dir)  # change into cleaning directory

if (testing == "yes" or testing == "comments"): 
    print "Effective user: " + euname
    print "Root directory: " + project_root
    print "Map cleaning directory: " + os.getcwd()
    print sandbox    

if sandbox == True:
    db = 'SouthAfricaSandbox'
elif sandbox == False:
    db = 'SouthAfrica'

fixshp1 = "temp_" + assignmentid
fixshp2 = "temp_f_" + assignmentid

driver = ogr.GetDriverByName('ESRI Shapefile') 
if os.path.exists(fixshp1 + ".shp"):
    driver.DeleteDataSource(fixshp1 + ".shp") #-- if it exists, overwrite it
ds = driver.CreateDataSource(fixshp1 + ".shp")
#print ds
layer = ds.CreateLayer(fixshp1, geom_type=ogr.wkbPolygon) #-- we create a SHP with polygons
layer_defn = layer.GetLayerDefn()
fd = ogr.FieldDefn('name', ogr.OFTString)
layer.CreateField(fd)
#feature = ogr.Feature(layer_defn)

# Create connection
conn = psy.connect("dbname=%s user = '***REMOVED***' password = '***REMOVED***'" % (db))
cur = conn.cursor()

if mtype == "tr": 
    cur.execute("""SELECT name,ST_AsEWKT(geom)%s from %s where %s='%s' and try='%s' order by name for update""" 
        % (trystr, map_table, assignment_type, assignmentid, tryid))
if mtype == "ma": 
    cur.execute("""SELECT name,ST_AsEWKT(geom)%s from %s where %s='%s' order by name for update""" 
        % (trystr, map_table, assignment_type, assignmentid))
rows = cur.fetchall()
for i in range(0, len(rows)): 
    name = rows[i][0]
    wkt = re.sub("^SRID=*.*;", "", rows[i][1])
    #wktfix = subprocess.Popen(["/u/sandbox/afmap/prepair/prepair", "--wkt", wkt], stdout=subprocess.PIPE).communicate()[0]
    wktfix = subprocess.Popen([project_root + "/prepair/prepair", "--wkt", wkt, "--minarea", "0.000000001"], 
        stdout=subprocess.PIPE).communicate()[0]
    #wktfix = subprocess.Popen(["/u/sandbox/afmap/prepair/prepair", "--isr", "0.000000000001", "--wkt", wkt], stdout=subprocess.PIPE).communicate()[0]
    geom = ogr.CreateGeometryFromWkt(wktfix)
    #print wktfix
    featureIndex = i
    feature = ogr.Feature(layer_defn)    
    feature.SetGeometry(geom) 
    feature.SetFID(featureIndex)
    feature.SetField('name', name) 
    layer.CreateFeature(feature)         

feature.Destroy()
ds.Destroy()

# Run pprepair
wthfix2 = subprocess.Popen([project_root + "/pprepair/pprepair", "-i", fixshp1 + ".shp", "-o", fixshp2 + ".shp", 
    "-fix"], stdout=subprocess.PIPE).communicate() 
#print wktfixall 

# Read it in again and pass through prepair one more time
fixpoly = ogr.Open(fixshp2 + ".shp")
#fixlyr = fixpoly.GetLayer()
fixlyr = fixpoly.GetLayer(0)
#fixlyr.ResetReading()
nFeatures = fixlyr.GetFeatureCount()
names = []
polys = []

#for f in fixlyr:
for f in range(nFeatures):
    feature = fixlyr.GetFeature(f)
    fname = feature.GetField("name")
    #geom = f.GetGeometryRef()
    geom = feature.GetGeometryRef()
    area = geom.GetArea()
    #geom_name = geom.GetGeometryName()
    wkt = geom.ExportToWkt()
    
    if (testing == "yes" or testing == "comments"):
        print "Fieldname: " + fname
        print "Field area: %s" % area
    
    # Filter out very small sliver polygons
    if area > 0.000000001:
        if (testing == "yes" or testing == "comments"):        
            print "Updating this one: " + fname
        names.append(fname)
        polys.append(wkt)

# Combine names and geometries into strings fo insertion into SQL
#namestr = "(" + ",".join(names) + ")"
#geomstr = "(" + ",".join(polys) + ")"

for n in range(0, len(names)): 
    update_str = """UPDATE %s SET geom_clean = ST_GeomFromEWKT('SRID=4326;%s') WHERE name = '%s'""" % (map_table, polys[n], names[n])
    cur.execute(update_str)
    #conn.commit()
    if (testing == "yes" or testing == "comments"):
        print update_str

#conn.commit()
#cur.close()
#conn.close()

#if (testing == "yes" or testing == "comments"):
    #print namestr
    #print geomstr
    #print update_str

if (testing == "no" or testing == "comments"):
    tempfilelist = glob.glob("*" + assignmentid + "*")
    try: 
        for f in tempfilelist:
            print(f)
            os.remove(f)
    except Exception,e:
        print e

conn.commit()
cur.close()
conn.close()
