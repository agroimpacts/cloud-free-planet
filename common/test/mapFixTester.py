# for testing mapFix. Longer terms goal is to turn it into an automated tester
# pointed at bad_user_maps table

########### Inputs
# targs = ["SA90531", "33", "2", "tr"]
# targs = ["SA188774", "67", "1", "tr"]
# targs = ["SA3470", "69", "2", "tr"]
# targs = ["SA188774", "20", "1", "tr"]
# targs = ["SA90531", "9", "1", "tr"]
targs = ["U_SA3470", "69", "1", "tr"]

dTable = "badmaps"  # badmaps|normal
testing = "yes"
testpath = '/home/lestes/mapperAL/common'
run = "partial" # full|partial
###########

# dependent args
kmlid = targs[0]
assignmentid = targs[1]
tryid = targs[2]
mtype = targs[3]
dtables = ["bad_user_maps", "qual_user_maps", "user_maps"]

# functions for cleaning mapping polygons
import sys
sys.path.append(testpath)  ## allows access to MappingCommon/mapCleaners one directory up
import os, re, subprocess, glob
# from osgeo import ogr
# from osgeo import gdal
from datetime import datetime
from MappingCommon import MappingCommon

# import mapCleaners as mp
mapc = MappingCommon(projectRoot='/home/lestes/mapperAL')
cleaning_dir = mapc.projectRoot + "/laundromat/"  # directory for temporary maps

if dTable == "badmaps": 
    dt = dtables[0]
elif dTable == "normal" and mtype == "tr":
    dt = dtables[1]
elif dTable == "normal" and mtype == "ma":
    dt = dtable[2]

if run == "full":
    import mapFix as mp
    mp.mapFix(mapc, mtype, kmlid, assignmentid, testing, tryid)
    
elif run == "partial":
    import mapCleaners as mp
    fixshpnm = assignmentid.encode('utf-8')
    if tryid is not None:
        fixshpnm = "%s_%s" % (fixshpnm, tryid)

    fixshpnm1 = cleaning_dir + "temp"
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
        mapc.cur.execute("""SELECT name,ST_AsEWKT(geom),try FROM 
           %s WHERE name LIKE '%s\_%%' AND assignment_id='%s' AND
           try='%s' ORDER BY name FOR UPDATE""" % 
           (dt, kmlid, assignmentid, tryid))
    elif mtype == "ma" and tryid is None:
        mapc.cur.execute("""SELECT name,ST_AsEWKT(geom) FROM %s
           WHERE name LIKE '%s\_%%' AND assignment_id='%s' ORDER BY name
           FOR UPDATE""" % (dt, kmlid, assignmentid))
    else:
        raise Exception ("Invalid maptype or tryid passed to Mapfix")

    poly_table = mapc.cur.fetchall()
    if len(poly_table) == 0:
        raise Exception ("Invalid kmlid, assignmentid/trainingid,"
                         " or tryid passed to Mapfix")
                         
    print poly_table
    mp.polyPrepair(mapc, fixshpnm1, poly_table)
    mp.polyPPrepair(mapc, fixshpnm1, fixshpnm2)
    poly_fix = mp.shapeReader(mapc, fixshpnm2)
    poly_fix2 = mp.cleanPolyHash(mapc, poly_fix)
    mp.shapeWriter(mapc, poly_fix2, fixshpnm3)
    mp.polyPPrepair(mapc, fixshpnm3, fixshpnm4)
    poly_fixf = mp.shapeReader(mapc, fixshpnm4)
    
    print [len(poly_table), len(poly_fixf)]

    if (testing == "no" or testing == "comments"):
        mp.tempShapeDel(mapc, cleaning_dir, fixshpnm)

    del mapc

