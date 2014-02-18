#! /usr/bin/python
# Cleans polygons in database

from osgeo import ogr
import glob, sys, os, subprocess, re #getpass
from MTurkMappingAfrica import MTurkMappingAfrica
import mapCleaners as mp

if(len(sys.argv) < 4 or len(sys.argv) > 6):
    print "Error: There must be at least 5 and no more than 6 arguments: maptype, kmlid, assn id, testing option, and/or try id"
    quit()

mtype = sys.argv[1]
kmlid = sys.argv[2]
assignmentid = sys.argv[3]
testing = sys.argv[4] 
if(len(sys.argv) == 6): 
    tryid = sys.argv[5]
else: 
    tryid = 'NA'

mtma = MTurkMappingAfrica()

cleaning_dir = mtma.projectRoot + "/laundromat"  # directory for temporary maps
os.chdir(cleaning_dir)  # change into cleaning directory

fixshpnm1 = "temp_" + assignmentid
fixshpnm2 = "temp_fix_" + assignmentid
fixshpnm3 = "temp_fix_2_" + assignmentid
fixshpnm4 = "temp_fix_3_" + assignmentid

if (testing == "yes" or testing == "comments"):
    print "Effective user: " + mtma.euser
    print "Root directory: " + mtma.projectRoot
    print "Map cleaning directory: " + os.getcwd()
    print "Assignment ID: " + assignmentid
    print "Try ID: " + tryid
    print fixshpnm1, fixshpnm2

if mtype == "tr":
    mtma.cur.execute("""SELECT name,ST_AsEWKT(geom),try FROM qual_user_maps WHERE name LIKE '%s_%%' AND training_id='%s' AND 
        try='%s' ORDER BY name FOR UPDATE""" % (kmlid, assignmentid, tryid))
elif mtype == "ma":
    mtma.cur.execute("""SELECT name,ST_AsEWKT(geom) FROM user_maps WHERE name LIKE '%s_%%' AND assignment_id='%s' ORDER BY name 
        FOR UPDATE""" % (kmlid, assignmentid))
poly_table = mtma.cur.fetchall()

mp.polyPrepair(fixshpnm1, poly_table)
mp.polyPPrepair(fixshpnm1, fixshpnm2)
poly_fix = mp.shapeReader(fixshpnm2)
poly_fix2 = mp.cleanPolyHash(poly_fix)
mp.shapeWriter(poly_fix2, fixshpnm3) 
mp.polyPPrepair(fixshpnm3, fixshpnm4)
poly_fixf = mp.shapeReader(fixshpnm4)
if(len(poly_table) == len(poly_fixf)): 
    for name in poly_fixf:
        if mtype == "tr":
            update_str = """UPDATE qual_user_maps SET geom_clean = ST_GeomFromEWKT('SRID=4326;%s')
                WHERE name = '%s' AND training_id='%s' AND try='%s'""" % (poly_fixf[name][0], name, assignmentid, tryid)
        elif mtype == "ma":
            update_str = """UPDATE user_maps SET geom_clean = ST_GeomFromEWKT('SRID=4326;%s') 
                WHERE name = '%s' AND assignment_id='%s'""" % (poly_fixf[name][0], name, assignmentid)
        mtma.cur.execute(update_str)
        if (testing == "yes" or testing == "comments"):
            print update_str
    mtma.dbcon.commit()
else: 
    print "Error: The number of cleaned polygons doesn't match the number of input polygons for assignment" + assignmentid

if (testing == "no" or testing == "comments"):
    mp.tempShapeDel(assignmentid)

del mtma
