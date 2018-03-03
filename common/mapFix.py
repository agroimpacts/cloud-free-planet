#! /usr/bin/python
# Cleans polygons in database

from osgeo import ogr
import glob, sys, os, subprocess, re #getpass
from MappingCommon import MappingCommon
import mapCleaners as mp

def mapFix(mapc, mtype, kmlid, assignmentid, testing, tryid=None):
    cleaning_dir = mapc.projectRoot + "/laundromat/"  # directory for temporary maps

    fixshpnm = assignmentid.encode('utf-8')
    if tryid is not None:
        fixshpnm = "%s_%s" % (fixshpnm, tryid)
    fixshpnm1 = cleaning_dir + "temp_" + fixshpnm
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

    mp.polyPrepair(mapc, fixshpnm1, poly_table)  # first clean of individual polygons (prepair)
    mp.polyPPrepair(mapc, fixshpnm1, fixshpnm2)  # first run of pprepair
    poly_fix = mp.shapeReader(mapc, fixshpnm2)  # read cleaned polys back in
    poly_fix2 = mp.cleanPolyHash(mapc, poly_fix)  # union divided fields, name correctly
    mp.shapeWriter(mapc, poly_fix2, fixshpnm3)  # write back out
    mp.polyPPrepair(mapc, fixshpnm3, fixshpnm4)  # pass to pprepair one more time
    poly_fixf = mp.shapeReader(mapc, fixshpnm4)  # read in
    
    # Write cleaned polygons out to database, assuming numbers line up
    if(len(poly_table) == len(poly_fixf)): 
        for name in poly_fixf:
            if mtype == "tr":
                update_str = """UPDATE qual_user_maps SET geom_clean = ST_GeomFromEWKT('SRID=4326;%s')
                    WHERE name = '%s' AND training_id='%s' AND try='%s'""" % (poly_fixf[name][0], name, assignmentid, tryid)
            elif mtype == "ma":
                update_str = """UPDATE user_maps SET geom_clean = ST_GeomFromEWKT('SRID=4326;%s') 
                    WHERE name = '%s' AND assignment_id='%s'""" % (poly_fixf[name][0], name, assignmentid)
            mapc.cur.execute(update_str)
            if (testing == "yes" or testing == "comments"):
                print update_str
        mapc.dbcon.commit()
    else: 
        print "Error: The number of cleaned polygons doesn't match the number of input polygons for assignment" + assignmentid

    if (testing == "no" or testing == "comments"):
        mp.tempShapeDel(mapc, cleaning_dir, fixshpnm)

    del mapc

def main():
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        print "Error: There must be at least 4 and no more than 5 arguments: maptype, kmlid, assn id, testing option, and/or try id"
        quit()

    mtype = sys.argv[1]
    kmlid = sys.argv[2]
    assignmentid = sys.argv[3]
    assignmentid = unicode(assignmentid, "UTF-8")
    testing = sys.argv[4]
    mapc = MappingCommon()
    if len(sys.argv) == 6:
        tryid = int(sys.argv[5])
        mapFix(mapc, mtype, kmlid, assignmentid, testing, tryid)
    else:
        mapFix(mapc, mtype, kmlid, assignmentid, testing)


if __name__ == '__main__':
    main()
