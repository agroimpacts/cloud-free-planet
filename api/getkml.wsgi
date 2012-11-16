from webob import Request, Response
import psycopg2
import datetime
from MTurkMappingAfrica import MTurkMappingAfrica

def application(environ, start_response):
    req = Request(environ)
    res = Response()
    res.content_type = 'text/html'

    now = str(datetime.datetime.today())

    con = psycopg2.connect("dbname=SouthAfrica user=***REMOVED*** password=***REMOVED***")
    cur = con.cursor()
    cur.execute("select value from configuration where key = 'ProjectRoot'")
    logFilePath = cur.fetchone()[0] + "/log"
    cur.execute("select value from configuration where key = 'KMLUrl'")
    kmlUrl = cur.fetchone()[0]
    cur.execute("select value from configuration where key = 'KMLParameter'")
    kmlName = cur.fetchone()[0]

    k = open(logFilePath + "/OL.log", "a")
    k.write("\ngetkml: datetime = %s\n" % now)
    try:
        kmlValue = req.params[kmlName]
        try:
            hitId = req.params['hitId']
            assignmentId = req.params['assignmentId']
            if assignmentId != 'ASSIGNMENT_ID_NOT_AVAILABLE':
                workerId = req.params['workerId']
                turkSubmitTo = req.params['turkSubmitTo']
                preview = ''
            else:
                workerId = ''
                turkSubmitTo = ''
                preview = '*** PREVIEW ***<br/>'
        except:
            hitId = ''
            assignmentId = ''
            workerId = ''
            turkSubmitTo = ''
            preview = ''
        mainText = '''
            <!DOCTYPE html>
            <html>
                <head>
                    <title>One Square Km in South Africa</title>
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                    <script type="text/javascript" src="/afmap/OL/OpenLayers-2.12/OpenLayers.js"></script>
                    <script type="text/javascript" src="http://maps.google.com/maps/api/js?v=3.7&sensor=false"></script>
                    <script type="text/javascript" src="/afmap/OL/showkml.js"></script>
                    <link rel="stylesheet" href="/afmap/OL/showkml.css" type="text/css">
                </head>
                <body onload="init('%(path)s', '%(kmlValue)s', '%(assignmentId)s')">
                    <form name='mturkform' action='%(turkSubmitTo)s/mturk/externalSubmit'>
                        <div class='instructions'>
                            %(preview)s
                            Please use the toolbar below to map all crop fields that are wholly or partially inside the white square outline (map the entire field, <br/>even the part that falls outside the box). Then save your changes by clicking on the disk icon to complete the HIT.
                        </div>
                        <table class='comments'><tr>
                        <th>
                            Please use this space to send comments, <br/>problems, or questions to the Requester:
                        </th>
                        <td>
                            <textarea class='comments' name='comment' cols=80 rows=2></textarea>
                        </td>
                        </tr></table>
                        <input type='hidden' name='assignmentId' value='%(assignmentId)s' />
                        <input type='hidden' name='kmlName' value='%(kmlValue)s' />
                        <input type='hidden' name='save_status' />
                    </form>
                    <div id="kml_display" style="width: 100%%; height: 100%%;"></div>
                </body>
            </html>
        ''' % {
            'path': kmlUrl,
            'kmlValue': kmlValue,
            'assignmentId': assignmentId,
            'turkSubmitTo': turkSubmitTo,
            'preview': preview
        }
        res.text = mainText
        # If we are running under MTurk,
        if len(assignmentId) > 0:
            # If this is an accepted HIT,
            if assignmentId != 'ASSIGNMENT_ID_NOT_AVAILABLE':
                # If this is a new HIT,
                cur.execute("SELECT TRUE FROM assignment_data WHERE assignment_id = '%s'" % assignmentId)
                if not cur.fetchone():
                    # If this is a new worker,
                    cur.execute("SELECT TRUE FROM worker_data WHERE worker_id = '%s'" % (workerId))
                    if not cur.fetchone():
                        cur.execute("""INSERT INTO worker_data 
                            (worker_id, first_time, last_time) 
                            VALUES ('%s', '%s', '%s')""" % (workerId, now, now))
                    # Else, this is an existing worker.
                    else:
                        cur.execute("""UPDATE worker_data SET last_time = '%s'
                            WHERE worker_id = '%s'""" % (now, workerId))
                    # Insert the assignment data.
                    cur.execute("""INSERT INTO assignment_data 
                        (assignment_id, hit_id, worker_id, accept_time, completion_status) 
                        VALUES ('%s' , '%s', '%s', '%s', '%s')""" % (assignmentId, hitId, workerId, now, MTurkMappingAfrica.HITAccepted))
                    k.write("getkml: MTurk ACCEPT request fetched kmlValue = %s\n" % kmlValue)
                    con.commit()
                # Else, this is the continuation of a previously accepted HIT.
                else:
                    k.write("getkml: MTurk CONTINUE request fetched kmlValue = %s\n" % kmlValue)
                k.write("getkml: MTurk provided hitId = %s\n" % hitId)
                k.write("getkml: MTurk provided assignmentId = %s\n" % assignmentId)
                k.write("getkml: MTurk provided workerId = %s\n" % workerId)
                k.write("getkml: MTurk provided turkSubmitTo = %s\n" % turkSubmitTo)
            # else, this is a HIT preview.
            else:
                k.write("getkml: MTurk PREVIEW request fetched kmlValue = %s\n" % kmlValue)
                k.write("getkml: MTurk provided hitId = %s\n" % hitId)
        # Else, we are not running under MTurk.
        else:
            k.write("getkml: Non-MTurk request fetched kmlValue = %s\n" % kmlValue)
    except KeyError as e:
        mainText = '''
            <!DOCTYPE html>
            <html>
                <head>
                    <title>One Square Km in South Africa</title>
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                </head>
                <body>
                    <b>Invalid or missing keyword: '%(kmlName)s' required.</b>
                </body>
            </html>
        ''' % {
            'kmlName': kmlName
        }
        res.body = mainText
        k.write("getkml: Missing keyword error %s\n" % (e))
    k.close()
    con.close()
    return res(environ, start_response)
