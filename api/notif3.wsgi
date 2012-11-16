import sys
import psycopg2
import datetime
from webob import Request, Response
from boto.mturk.notification import NotificationMessage, Event

def application(environ, start_response):
    req = Request(environ)
    res = Response()

    sys.path.append('/var/www/html/afmap/mturk')
    from MTurkMappingAfrica import aws_secret_access_key

    now = str(datetime.datetime.today())

    con = psycopg2.connect("dbname=SouthAfrica user=***REMOVED*** password=***REMOVED***")
    cur = con.cursor()
    cur.execute("select value from configuration where key = 'ProjectRoot'")
    logFilePath = cur.fetchone()[0] + "/log"

    k = open(logFilePath + "/notifications.log", "a")
    k.write("\nnotif3: datetime = %s\n" % now)

    lines = []
    k.write('WSGI Query String\n')
    for key, v in sorted(req.params.items()):
        k.write('%s: %r\n' % (key, v))

    k.close()

    return res(environ, start_response)
