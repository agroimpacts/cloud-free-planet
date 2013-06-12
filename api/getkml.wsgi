from webob import Request, Response
import datetime
from MTurkMappingAfrica import MTurkMappingAfrica

def application(environ, start_response):
    req = Request(environ)
    res = Response()
    res.content_type = 'text/html'

    now = str(datetime.datetime.today())

    mtma = MTurkMappingAfrica()
    logFilePath = mtma.getConfiguration('ProjectRoot') + "/log"
    kmlUrl = mtma.getConfiguration('KMLUrl')
    mturkFrameHeight = int(mtma.getConfiguration('MTurkFrameHeight'))
    apiUrl = mtma.getConfiguration('APIUrl')
    mturkPostPolygonScript = mtma.getConfiguration('MTurkPostPolygonScript')
    mturkNoPolygonScript = mtma.getConfiguration('MTurkNoPolygonScript')

    polygonUrl = apiUrl + '/' + mturkPostPolygonScript
    noPolygonUrl = apiUrl + '/' + mturkNoPolygonScript
    headerHeight = 70
    mapHeight = mturkFrameHeight - headerHeight

    k = open(logFilePath + "/OL.log", "a")
    k.write("\ngetkml: datetime = %s\n" % now)
    kmlName = req.params['kmlName']
    if len(kmlName) > 0:
        # MTurk cases.
        try:
            hitId = req.params['hitId']
            assignmentId = req.params['assignmentId']
            # MTurk accept case.
            if assignmentId != 'ASSIGNMENT_ID_NOT_AVAILABLE':
                workerId = req.params['workerId']
                preview = ''
                disabled = ''
                submitTo = req.params['turkSubmitTo'] + MTurkMappingAfrica.externalSubmit
                target = '_self'
            # MTurk preview case.
            else:
                workerId = ''
                preview = '*** PREVIEW ***'
                disabled = 'disabled'
                submitTo = ''
                target = ''
            trainingId = ''
        # Training & non-MTurk cases.
        except:
            hitId = ''
            assignmentId = ''
            workerId = ''
            preview = ''
            disabled = 'disabled'
            # Training case.
            try:
                submitTo = req.params['submitTo']
                target = '_parent'
                trainingId = req.params['trainingId']
            # Non-MTurk case.
            except:
                submitTo = ''
                target = ''
                trainingId = ''

        mainText = '''
            <!DOCTYPE html>
            <html>
                <head>
                    <title>One Square Km in South Africa</title>
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                    <script type="text/javascript" src="/afmap/OL/OpenLayers-2.12/OpenLayers.js"></script>
                    <script type="text/javascript" src="https://maps.google.com/maps/api/js?v=3.8&sensor=false"></script>
                    <script type="text/javascript" src="/afmap/OL/showkml.js"></script>
                    <link rel="stylesheet" href="/afmap/OL/showkml.css" type="text/css">
                    <style>
                        html, body {
                            height: %(mturkFrameHeight)spx;
                        }
                    </style>
                </head>
                <body onload="init('%(kmlPath)s', '%(polygonPath)s', '%(noPolygonPath)s', '%(kmlName)s', '%(assignmentId)s', '%(trainingId)s')">
                    <form style='width: 100%%; height: %(headerHeight)spx;' name='mturkform' action='%(submitTo)s' target='%(target)s'>
                        <div class='instructions'>
                            %(preview)s
                            Please use the toolbar below to map all crop fields that are wholly or partially inside the white square outline (map the entire field, <br/>even the part that falls outside the box). Then save your changes by clicking on the disk icon to complete the HIT.
                            %(preview)s
                        </div>
                        <table class='comments'><tr>
                        <th>
                            For comments, problems, or questions:
                        </th>
                        <td>
                            <input type='text'  class='comments' name='comment' size=80 maxlength=2048 %(disabled)s></input>
                        </td>
                        <th>
                            &nbsp;&nbsp;&nbsp;
                            <i>Hover over the icons in the toolbar below for usage instructions.</i>
                        </th>
                        </tr></table>
                        <input type='hidden' name='assignmentId' value='%(assignmentId)s' />
                        <input type='hidden' name='trainingId' value='%(trainingId)s' />
                        <input type='hidden' name='kmlName' value='%(kmlName)s' />
                        <input type='hidden' name='save_status' />
                    </form>
                    <div id="kml_display" style="width: 100%%; height: %(mapHeight)spx;"></div>
                </body>
            </html>
        ''' % {
            'kmlPath': kmlUrl,
            'polygonPath': polygonUrl,
            'noPolygonPath': noPolygonUrl,
            'kmlName': kmlName,
            'assignmentId': assignmentId,
            'trainingId': trainingId,
            'submitTo': submitTo,
            'target': target,
            'preview': preview,
            'disabled': disabled,
            'mturkFrameHeight': mturkFrameHeight,
            'headerHeight': headerHeight,
            'mapHeight': mapHeight
        }
        res.text = mainText
        # If we are running under MTurk,
        if len(assignmentId) > 0:
            # If this is an accepted HIT,
            if assignmentId != 'ASSIGNMENT_ID_NOT_AVAILABLE':
                # If this is a new HIT,
                mtma.cur.execute("SELECT TRUE FROM assignment_data WHERE assignment_id = '%s'" % assignmentId)
                if not mtma.cur.fetchone():
                    # If this is a new worker,
                    mtma.cur.execute("SELECT TRUE FROM worker_data WHERE worker_id = '%s'" % (workerId))
                    if not mtma.cur.fetchone():
                        mtma.cur.execute("""INSERT INTO worker_data 
                            (worker_id, first_time, last_time) 
                            VALUES ('%s', '%s', '%s')""" % (workerId, now, now))
                    # Else, this is an existing worker.
                    else:
                        mtma.cur.execute("""UPDATE worker_data SET last_time = '%s'
                            WHERE worker_id = '%s'""" % (now, workerId))
                    # Insert the assignment data.
                    mtma.cur.execute("""INSERT INTO assignment_data 
                        (assignment_id, hit_id, worker_id, accept_time, status) 
                        VALUES ('%s' , '%s', '%s', '%s', '%s')""" % (assignmentId, hitId, workerId, now, MTurkMappingAfrica.HITAccepted))
                    k.write("getkml: MTurk ACCEPT request fetched kmlName = %s\n" % kmlName)
                    mtma.dbcon.commit()
                # Else, this is the continuation of a previously accepted HIT.
                else:
                    k.write("getkml: MTurk CONTINUE request fetched kmlName = %s\n" % kmlName)
                k.write("getkml: MTurk provided hitId = %s\n" % hitId)
                k.write("getkml: MTurk provided assignmentId = %s\n" % assignmentId)
                k.write("getkml: MTurk provided workerId = %s\n" % workerId)
                k.write("getkml: MTurk provided turkSubmitTo = %s\n" % submitTo)
            # else, this is a HIT preview.
            else:
                k.write("getkml: MTurk PREVIEW request fetched kmlName = %s\n" % kmlName)
                k.write("getkml: MTurk provided hitId = %s\n" % hitId)
        # Else, we are not running under MTurk.
        elif len(trainingId) > 0:
            k.write("getkml: Training request fetched kmlName = %s\n" % kmlName)
        else:
            k.write("getkml: Non-MTurk request fetched kmlName = %s\n" % kmlName)

    # No KML specified.
    else:
        mainText = '''
            <!DOCTYPE html>
            <html>
                <head>
                    <title>One Square Km in South Africa</title>
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                </head>
                <body>
                    <b></b>
                </body>
            </html>
        '''
        res.body = mainText
        k.write("getkml: No KML specified in URL.\n")
    k.close()
    mtma.dbcon.close()
    return res(environ, start_response)
