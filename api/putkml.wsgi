from webob import Request, Response
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
    cur.execute("select value from configuration where key = 'KMLParameter'")
    kmlName = cur.fetchone()[0]

    k = open(logFilePath + "/OL.log", "a")
    k.write("\nputkml: datetime = %s\n" % now)
    try:
        kmlValue = req.params[kmlName]
        if len(kmlValue) > 0:
            k.write("putkml: OL reported 'save' without polygons for kml %s\n" % kmlValue)
            try:
                assignmentId = req.params['assignmentId']
                k.write("putkml: MTurk Assignment ID = %s\n" % assignmentId)
            except:
                k.write("putkml: No MTurk Assignment ID\n")
        else:
            k.write("putkml: OL missing KML name error\n")
            res.status_code = 400
    except KeyError as e:
        res.status_code = 400
        k.write("putkml: OL missing keyword error %s\n" % (e))
    k.close()
    return res(environ, start_response)
