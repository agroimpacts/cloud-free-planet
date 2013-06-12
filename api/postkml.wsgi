from webob import Request, Response
from xml.dom.minidom import parseString
import psycopg2
import datetime
from MTurkMappingAfrica import MTurkMappingAfrica

def application(environ, start_response):
    req = Request(environ)
    res = Response()

    now = str(datetime.datetime.today())

    mtma = MTurkMappingAfrica()
    logFilePath = mtma.getConfiguration('ProjectRoot') + "/log"

    kml = parseString(req.body)

    # Use this to store name and Assignment ID of completed kml in DB.
    kmlValue = kml.getElementsByTagName('name')[0].firstChild.data.split('_')
    kmlName = kmlValue[0]
    if len(kmlValue) == 2:
        assignmentId = kmlValue[1]
        trainingId = none
    elif len(kmlValue) == 3:
        assignmentId = None
        trainingId = kmlValue[2]
    else:
        assignmentId = None
        trainingId = None

    k = open(logFilePath + "/OL.log", "a")
    k.write("\npostkml: datetime = %s\n" % now)
    k.write("postkml: OL saved polygons for kml %s\n" % kmlName)
    if assignmentId:
        k.write("postkml: MTurk Assignment ID = %s\n" % assignmentId)
    elif trainingId:
        k.write("postkml: Training ID = %s\n" % trainingId)
    else:
        k.write("postkml: No MTurk Assignment or Training ID\n")
    k.write("postkml: kml = %s\n" % req.body)

    # Loop over every Polygon, and store its name and data in PostGIS DB.
    for placemark in kml.getElementsByTagName('Placemark'):
        polyName = placemark.getElementsByTagName('name')[0].firstChild.data
        polygon = placemark.getElementsByTagName('Polygon')[0].toxml()
        k.write("postkml: polygon name = %s\n" % polyName)
        k.write("postkml: polygon = %s\n" % polygon)
        try:
            mtma.cur.execute("""INSERT INTO user_maps (name, geom, completion_time, 
                assignment_id, training_id)
                SELECT %s AS name, ST_GeomFromKML(%s) AS geom, %s AS datetime, 
                %s as assignment_id, %s as training_id""",
                (polyName, polygon, now, assignmentId, trainingId))
            mtma.dbcon.commit()
        except psycopg2.InternalError as e:
            k.write("postkml: Database error %s: %s" % (e.pgcode, e.pgerror))
            mtma.dbcon.rollback()
            if e.pgerror.find('invalid KML representation') != -1:
                k.write("postkml: Ignoring this polygon and continuing\n")
            else:
                # Internal Server Error - catchall
                res.status_code = 500
                break
        except psycopg2.Error as e:
            k.write("postkml: General database error %s: %s" % (e.pgcode, e.pgerror))
            mtma.dbcon.rollback()
            # Internal Server Error - catchall
            res.status_code = 500
            break
    else:
        mtma.dbcon.commit()

    # If this is a training map, then call the scoring routine and 
    # record the results here.
    if trainingId:
        score = 0.5

        # Record the HIT submission time and status, and user comment.
        mtma.cur.execute("""update qual_assignment_data set completion_time = '%s',
            score = '%s' where training_id = '%s' and name = '%s'""" %
            (now, score, trainingId, kmlName))
        mtma.dbcon.commit()
        hitAcceptThreshold = float(mtma.getConfiguration('HitAcceptThreshold'))
        k.write("postkml: training assignment has been scored as: %.2f/%.2f\n" %
            (score, hitAcceptThreshold))

    k.close()
    return res(environ, start_response)
