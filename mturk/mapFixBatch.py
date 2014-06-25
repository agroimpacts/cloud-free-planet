#! /usr/bin/python
# Batch mode for running polygon cleaning functions in database

from osgeo import ogr
import glob, sys, os, subprocess, re #getpass
from MTurkMappingAfrica import MTurkMappingAfrica
import mapCleaners as mp

def mapFixBatch(mtma, id, tablename, testing):
    cleaning_dir = mtma.projectRoot + "/laundromat/"  # directory for temporary maps

    fixshpnm_base = id
    fixshpnm = fixshpnm_base.encode('utf-8')
    #print fixshpnm
    fixshpnm1 = cleaning_dir + "temp_" + fixshpnm
    fixshpnm2 = cleaning_dir + "temp_fix_" + fixshpnm
    fixshpnm3 = cleaning_dir + "temp_fix_2_" + fixshpnm
    fixshpnm4 = cleaning_dir + "temp_fix_3_" + fixshpnm

    if tablename == 'qaqcfields':
        sel_str = """SELECT name,gid,ST_AsEWKT(geom) FROM %s WHERE name='%s' FOR UPDATE""" % (tablename, id)
    elif tablename == 'user_maps':
        sel_str = """SELECT name,ST_AsEWKT(geom) FROM %s WHERE assignment_id='%s' FOR UPDATE""" % (tablename, id)
    #elif tablename == 'qual_user_maps':
    #    mtma.cur.execute("""SELECT name,ST_AsEWKT(geom),try FROM %s WHERE name LIKE '%s_%%' AND training_id='%s' AND
    #        try='%s' ORDER BY name FOR UPDATE""" % (id, assignmentid, tryid))
 
    if (testing == "yes" or testing == "comments"):
        print "Effective user: " + mtma.euser
        print "Root directory: " + mtma.projectRoot
        print "Map cleaning directory: " + os.getcwd()
        #print "Assignment ID: " + assignmentid
        print "Data table: " + tablename
        #print sel_str

    mtma.cur.execute(sel_str)

    poly_table = mtma.cur.fetchall()
    if len(poly_table) == 0:
        raise Exception ("Invalid kmlid passed to Mapfix")

    if tablename == 'qaqcfields':
        poly_table2 = []
        for i in range(0, len(poly_table)):
            poly_name = "%s_%s" %(poly_table[i][0], poly_table[i][1])
            poly_table2.append((poly_name, poly_table[i][2]))
    if tablename == 'user_maps':
        poly_table2 = poly_table

    mp.polyPrepair(mtma, fixshpnm1, poly_table2)
    mp.polyPPrepair(mtma, fixshpnm1, fixshpnm2)
    poly_fix = mp.shapeReader(mtma, fixshpnm2)
    poly_fix2 = mp.cleanPolyHash(mtma, poly_fix)
    mp.shapeWriter(mtma, poly_fix2, fixshpnm3)
    mp.polyPPrepair(mtma, fixshpnm3, fixshpnm4)
    poly_fixf = mp.shapeReader(mtma, fixshpnm4)
    if(len(poly_table2) == len(poly_fixf)):
        for name in poly_fixf:
            if tablename == 'qaqcfields':
                name_gid = name.split("_")
                update_str = """UPDATE %s SET geom_clean = ST_GeomFromEWKT('SRID=97490;%s') 
                    WHERE name = '%s' AND gid='%s'""" % (tablename, poly_fixf[name][0], name_gid[0], name_gid[1])
            elif tablename == 'user_maps':
                update_str = """UPDATE %s SET geom_clean = ST_GeomFromEWKT('SRID=4326;%s')
                    WHERE name = '%s' AND assignment_id='%s'""" % (tablename, poly_fixf[name][0], name, id)
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
    if len(sys.argv) !=3:  # python counts the script name as an argument!
        print len(sys.argv)
        print "Error: There must be 2 arguments provided: tablename, testing option"
        quit()

    tablename = sys.argv[1]
    testing = sys.argv[2]
    mtma = MTurkMappingAfrica()
    if tablename == 'qaqcfields':
        mtma.cur.execute("""SELECT DISTINCT name FROM %s ORDER BY name""" % (tablename))
    elif tablename == 'user_maps':
        mtma.cur.execute("""SELECT DISTINCT assignment_id FROM %s ORDER by assignment_id""" % (tablename))
    table_names = mtma.cur.fetchall()
    for j in table_names:
        print "id is " + j[0]
        id=j[0]
        mapFixBatch(mtma, id, tablename, testing)

    del mtma

if __name__ == '__main__':
    main()
              
