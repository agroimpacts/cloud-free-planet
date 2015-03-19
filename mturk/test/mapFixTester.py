kmlid = "SA717944"
assignmentid = "3LRLIPTPEQ9P3FDJO7CT00MPF2CAKY"
testing = "yes"
tryid = None
mtype = "qa"

from osgeo import ogr
import glob, sys, os, subprocess, re #getpass
from MTurkMappingAfrica import MTurkMappingAfrica
import mapCleaners as mp

mtma = MTurkMappingAfrica()
cleaning_dir = mtma.projectRoot + "/laundromat/"
fixshpnm = assignmentid.encode('utf-8')
if tryid is not None:
    fixshpnm = "%s_%s" % (fixshpnm, tryid)
    
#fixshpnm1 = cleaning_dir + "temp_" + fixshpnm
fixshpnm1 = cleaning_dir + "test"
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
    mtma.cur.execute("""SELECT name,ST_AsEWKT(geom),try FROM qual_user_maps 
        WHERE name LIKE '%s_%%' AND training_id='%s' AND try='%s' ORDER BY name 
        FOR UPDATE""" % (kmlid, assignmentid, tryid))
elif mtype == "ma" and tryid is None:
    mtma.cur.execute("""SELECT name,ST_AsEWKT(geom) FROM user_maps WHERE name LIKE '%s_%%' AND assignment_id='%s' ORDER BY name FOR UPDATE""" % (kmlid, assignmentid))
else:
    raise Exception ("Invalid maptype or tryid passed to Mapfix")

poly_table = mtma.cur.fetchall()
if len(poly_table) == 0:
    raise Exception ("Invalid kmlid, assignmentid/trainingid, or tryid passed to Mapfix")

mp.polyPrepair(mtma, fixshpnm1, poly_table)
mp.polyPPrepair(mtma, fixshpnm1, fixshpnm2)

# Failing at polyPPrepair
shape_name_in = fixshpnm1
shape_name_out = fixshpnm2
shape_in = shape_name_in + ".shp"
shape_out = shape_name_out + ".shp"
polyfix = subprocess.Popen([mtma.projectRoot + "/pprepair/pprepair", "-i", shape_in, "-o", shape_out, "-fix"], 
        stdout=subprocess.PIPE).communicate()[0]
