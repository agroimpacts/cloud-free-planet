#! /usr/bin/python
# Cleans polygons in database

from osgeo import ogr
import glob, sys, os, subprocess, re #getpass
from MTurkMappingAfrica import MTurkMappingAfrica
import mapCleaners as mp

def mapFix(mtma, mtype, kmlid, assignmentid, testing, tryid=None):
    cleaning_dir = mtma.projectRoot + "/laundromat/"  # directory for temporary maps

    fixshpnm = assignmentid.encode('utf-8')
    if tryid is not None:
        fixshpnm = "%s_%s" % (fixshpnm, tryid)
    fixshpnm1 = cleaning_dir + "temp_" + fixshpnm
    fixshpnm2 = cleaning_dir + "temp_fix_" + fixshpnm
    fixshpnm3 = cleaning_dir + "temp_fix_2_" + fixshpnm
    fixshpnm4 = cleaning_dir + "temp_fix_3_" + fixshpnm

    if (testing == "yes" or testing == "comments"):
        print "Effective user: " + mtma.euser
        print "Root directory: " + mtma.projectRoot
        print "Map cleaning directory: " + os.getcwd()
        print "Assignment ID: " + assignmentid
        if tryid is not None:
            print "Try ID: %s" % tryid

    if mtype == "tr" and tryid is not None:
        mtma.cur.execute("""SELECT name,ST_AsEWKT(geom),try FROM qual_user_maps WHERE name LIKE '%s_%%' AND training_id='%s' AND 
            try='%s' ORDER BY name FOR UPDATE""" % (kmlid, assignmentid, tryid))
    elif mtype == "ma" and tryid is None:
        mtma.cur.execute("""SELECT name,ST_AsEWKT(geom) FROM user_maps WHERE name LIKE '%s_%%' AND assignment_id='%s' ORDER BY name 
            FOR UPDATE""" % (kmlid, assignmentid))
    else:
        raise Exception ("Invalid maptype or tryid passed to Mapfix")

    poly_table = mtma.cur.fetchall()
    if len(poly_table) == 0:
        raise Exception ("Invalid kmlid, assignmentid/trainingid, or tryid passed to Mapfix")

    mp.polyPrepair(mtma, fixshpnm1, poly_table)
    mp.polyPPrepair(mtma, fixshpnm1, fixshpnm2)
    poly_fix = mp.shapeReader(mtma, fixshpnm2)
    poly_fix2 = mp.cleanPolyHash(mtma, poly_fix)
    mp.shapeWriter(mtma, poly_fix2, fixshpnm3) 
    mp.polyPPrepair(mtma, fixshpnm3, fixshpnm4)
    poly_fixf = mp.shapeReader(mtma, fixshpnm4)
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
        mp.tempShapeDel(mtma, cleaning_dir, fixshpnm)

    del mtma

def main():
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        print "Error: There must be at least 4 and no more than 5 arguments: maptype, kmlid, assn id, testing option, and/or try id"
        quit()

    mtype = sys.argv[1]
    kmlid = sys.argv[2]
    assignmentid = sys.argv[3]
    assignmentid = unicode(assignmentid, "UTF-8")
    testing = sys.argv[4]
    mtma = MTurkMappingAfrica()
    if len(sys.argv) == 6:
        tryid = int(sys.argv[5])
        mapFix(mtma, mtype, kmlid, assignmentid, testing, tryid)
    else:
        mapFix(mtma, mtype, kmlid, assignmentid, testing)


if __name__ == '__main__':
    main()
