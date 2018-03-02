kmlid = "SA90531"#"SA188774"
assignmentid = "33"
testing = "yes"
tryid = 2#1
mtype = "tr"
testpath = '/home/lestes/mapperAL/common'

# functions for cleaning mapping polygons
import sys
sys.path.append(testpath)  ## allows access to MappingCommon/mapCleaners one directory up
import os, re, subprocess, glob
from osgeo import ogr
from datetime import datetime
from MappingCommon import MappingCommon
import mapCleaners as mp


mapc = MappingCommon(projectRoot='/home/lestes/mapperAL')
cleaning_dir = mapc.projectRoot + "/laundromat/"  # directory for temporary maps
fixshpnm = assignmentid.encode('utf-8')
if tryid is not None:
    fixshpnm = "%s_%s" % (fixshpnm, tryid)
    
#fixshpnm1 = cleaning_dir + "temp_" + fixshpnm
fixshpnm1 = cleaning_dir + "test"
fixshpnm2 = cleaning_dir + "temp_fix_" + fixshpnm
fixshpnm3 = cleaning_dir + "temp_fix_2_" + fixshpnm
fixshpnm4 = cleaning_dir + "temp_fix_3_" + fixshpnm

if (testing == "yes" or testing == "comments"):
    print "Effective user: " + mapc.euser
    print "Root directory: " + mapc.projectRoot
    print "Map cleaning directory: " + os.getcwd()
    print "Assignment ID: " + assignmentid
    if tryid is not None:
        print "Try ID: %s" % tryid

if mtype == "tr" and tryid is not None:
    mapc.cur.execute("""SELECT name,ST_AsEWKT(geom),try FROM qual_user_maps WHERE name LIKE '%s\_%%' AND assignment_id='%s' AND 
        try='%s' ORDER BY name FOR UPDATE""" % (kmlid, assignmentid, tryid))
elif mtype == "ma" and tryid is None:
    mapc.cur.execute("""SELECT name,ST_AsEWKT(geom) FROM user_maps WHERE name LIKE '%s\_%%' AND assignment_id='%s' ORDER BY name 
        FOR UPDATE""" % (kmlid, assignmentid))
else:
   raise Exception ("Invalid maptype or tryid passed to Mapfix")

poly_table = mapc.cur.fetchall()
if len(poly_table) == 0:
    raise Exception ("Invalid kmlid, assignmentid/trainingid, or tryid passed to Mapfix")

mp.polyPrepair(mapc, fixshpnm1, poly_table)
mp.polyPPrepair(mapc, fixshpnm1, fixshpnm2)
poly_fix = mp.shapeReader(mapc, fixshpnm2)
poly_fix2 = mp.cleanPolyHash(mapc, poly_fix)
mp.shapeWriter(mapc, poly_fix2, fixshpnm3) 
mp.polyPPrepair(mapc, fixshpnm3, fixshpnm4)
poly_fixf = mp.shapeReader(mapc, fixshpnm4)

if (testing == "no" or testing == "comments"):
    mp.tempShapeDel(mapc, cleaning_dir, fixshpnm)

del mapc

