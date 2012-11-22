from datetime import datetime
from boto.mturk.connection import MTurkRequestError
from MTurkMappingAfrica import MTurkMappingAfrica

from pprint import pprint

mtma = MTurkMappingAfrica()

# sleep loop goes here.
# for loop in number of hits to create goes here.

mtma.cur.execute("select value from configuration where key = 'ProjectRoot'")
logFilePath = mtma.cur.fetchone()[0] + "/log"

now = str(datetime.today())

k = open(logFilePath + "/createHit.log", "a")
k.write("\ncreateHit: datetime = %s\n" % now)

# Get next KML of the right type to process.
kmlType = 'Q'
mtma.cur.execute("select name, gid from kml_data left outer join hit_data using (name) where kml_type = '%s' and hit_id is null order by gid limit 1" % kmlType)
row = mtma.cur.fetchone()
nextKml = row[0]
gid = row[1]

# Create the HIT
try:
    hitId = mtma.createHit(kml=nextKml, hitType='Q')
except MTurkRequestError as e:
    k.write("createHit: CreateHIT failed for KML %s:\n%s\n%s\n" %
        (nextKml, e.error_code, e.error_message))
    exit(-1)
except AssertionError:
    k.write("createHit: Bad CreateHIT status for KML %s:\n" % nextKml)
    exit(-2)

# Record the HIT ID.
k.write("createHit: Created HIT for KML %s\n" % nextKml)
mtma.cur.execute("insert into hit_data (hit_id, name, create_time) values ('%s' , '%s', '%s')" % (hitId, nextKml, now))
mtma.dbcon.commit()

k.close()
pprint(vars(mtma))
