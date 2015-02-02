#! /usr/bin/python
# Batch mode for running prepair only on polygons in database (on gids)

from osgeo import ogr
import glob, sys, os, subprocess, re #getpass
from MTurkMappingAfrica import MTurkMappingAfrica
import mapCleaners as mp

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def main():
    if len(sys.argv) !=3:  # python counts the script name as an argument!
        print len(sys.argv)
        print "Error: There must be 2 arguments provided: tablename, testing option (yes or no)"
        quit()

    tablename = sys.argv[1]
    testing = sys.argv[2]
    mtma = MTurkMappingAfrica()
    #mtma.cur.execute("""SELECT gid,ST_AsEWKT(geom) FROM %s FOR UPDATE""" % (tablename))
    mtma.cur.execute("""SELECT gid FROM %s WHERE geom_clean IS NULL ORDER BY gid""" % (tablename))
    poly_gids = mtma.cur.fetchall()
    #poly_gids = range(0, 1010)
    if testing == "yes":
        poly_gids2 = [poly_gids[i] for i in range(0,100)] 
        poly_gids = poly_gids2
        pchunks = chunks(poly_gids, 10)
    elif testing == "no":
        pchunks = chunks(poly_gids, 10000)
    for i in pchunks:
        a = i[0][0]
        b = i[len(i) - 1][0]
        selstr = """SELECT gid,ST_AsEWKT(geom) FROM %s WHERE gid>=%s and gid<=%s FOR UPDATE""" % (tablename, a, b)
        if testing == "yes":
            print selstr
        mtma.cur.execute(selstr)
        poly_table = mtma.cur.fetchall()
        for j in range(0, len(poly_table)):
            #print j
            gid=poly_table[j][0]
            print gid
            srid = poly_table[j][1].split(";")[0]
            wkt = re.sub(srid + ";", "", poly_table[j][1])
            #print wkt
            wktfix = mp.wktPrepair(mtma, wkt)
            #update_str = """UPDATE %s SET geom_clean = ST_GeomFromEWKT('%s;%s')
            #    WHERE gid = %s""" % (tablename, srid, wktfix, gid)
            #print update_str
            #mtma.cur.execute(update_str)
            if testing == "yes":
                print wktfix
            mtma.dbcon.commit()
    #if testing == "yes":
    #    runrng = 5
        #for i in range(0,3):
        #    print poly_table[i]
        #return
    #elif testing == "no":
    #    runrng = len(poly_table)
    #for j in range(0, runrng):
    #    gid=poly_table[j][0]
        #mtma.cur.execute("""SELECT gid,ST_AsEWKT(geom) FROM %s WHERE gid=%s FOR UPDATE""" % (tablename,gid))
        #poly_table = mtma.cur.fetchall()
    #    srid = poly_table[j][1].split(";")[0] 
    #    wkt = re.sub(srid + ";", "", poly_table[j][1])
    #    wktfix = mp.wktPrepair(mtma, wkt)
    #    update_str = """UPDATE %s SET geom_clean = ST_GeomFromEWKT('%s;%s')
    #        WHERE gid = %s""" % (tablename, srid, wktfix, gid)
    #    mtma.cur.execute(update_str)
    #    print gid
        #print wkt
        #print update_str
    #    if testing == "yes":
    #        print wktfix

    #mtma.dbcon.commit()
    del mtma

if __name__ == '__main__':
    main()
              
