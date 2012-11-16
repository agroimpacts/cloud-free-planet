from webob import Request, Response
from xml.dom.minidom import parseString
import psycopg2
import datetime

def application(environ, start_response):
    req = Request(environ)
    res = Response()

    now = str(datetime.datetime.today())

    con = psycopg2.connect("dbname=SouthAfrica user=***REMOVED*** password=***REMOVED***")
    cur = con.cursor()
    cur.execute("select value from configuration where key = 'ProjectRoot'")
    logFilePath = cur.fetchone()[0] + "/log"

    kml = parseString(req.body)

    # Use this to store name and Assignment ID of completed kml in DB.
    kmlValue = kml.getElementsByTagName('name')[0].firstChild.data.split('_')
    kmlName = kmlValue[0]
    if len(kmlValue) > 1:
        assignmentId = kmlValue[1]
    else:
        assignmentId = None

    k = open(logFilePath + "/OL.log", "a")
    k.write("\npostkml: datetime = %s\n" % now)
    k.write("postkml: OL saved polygons for kml %s\n" % kmlName)
    if assignmentId:
        k.write("postkml: MTurk Assignment ID = %s\n" % assignmentId)
    else:
        k.write("postkml: No MTurk Assignment ID\n")
    k.write("postkml: kml = %s\n" % req.body)

    # Loop over every Polygon, and store its name and data in PostGIS DB.
    for placemark in kml.getElementsByTagName('Placemark'):
        polyName = placemark.getElementsByTagName('name')[0].firstChild.data
        polygon = placemark.getElementsByTagName('Polygon')[0].toxml()
        k.write("postkml: polygon name = %s\n" % polyName)
        k.write("postkml: polygon = %s\n" % polygon)
        try:
            cur.execute("""INSERT INTO user_maps (name, geom, completion_time, assignment_id)
                SELECT %s AS name, ST_GeomFromKML(%s) AS geom, %s AS datetime, 
                %s as assignment_id""",
                (polyName, polygon, now, assignmentId))
            con.commit()
        except psycopg2.InternalError as e:
            k.write("postkml: Database error %s: %s" % (e.pgcode, e.pgerror))
            con.rollback()
            if e.pgerror.find('invalid KML representation') != -1:
                k.write("postkml: Ignoring this polygon and continuing\n")
            else:
                # Internal Server Error - catchall
                res.status_code = 500
                break
        except psycopg2.Error as e:
            k.write("postkml: General database error %s: %s" % (e.pgcode, e.pgerror))
            con.rollback()
            # Internal Server Error - catchall
            res.status_code = 500
            break
    else:
        con.commit()
    con.close()
    k.close()

    return res(environ, start_response)
