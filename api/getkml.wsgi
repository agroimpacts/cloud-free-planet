from webob import Request, Response
import datetime
from MTurkMappingAfrica import MTurkMappingAfrica

def application(environ, start_response):
    req = Request(environ)
    res = Response()
    res.content_type = 'text/html'

    now = str(datetime.datetime.today())

    mtma = MTurkMappingAfrica()
    logFilePath = mtma.projectRoot + "/log"
    mturkFrameHeight = int(mtma.getConfiguration('MTurkFrameHeight'))
    kmlUrl = mtma.getConfiguration('KMLUrl')
    apiUrl = mtma.getConfiguration('APIUrl')
    mapUrl = mtma.getConfiguration('MapUrl')
    mturkPostPolygonScript = mtma.getConfiguration('MTurkPostPolygonScript')
    mturkNoPolygonScript = mtma.getConfiguration('MTurkNoPolygonScript')

    polygonUrl = apiUrl + '/' + mturkPostPolygonScript
    noPolygonUrl = apiUrl + '/' + mturkNoPolygonScript
    headerHeight = 75
    mapHeight = mturkFrameHeight - headerHeight

    k = open(logFilePath + "/OL.log", "a")
    k.write("\ngetkml: datetime = %s\n" % now)

    kmlName = req.params['kmlName']
    if len(kmlName) > 0:
        # Get the type for this kml.
        mtma.cur.execute("select kml_type from kml_data where name = '%s'" % kmlName)
        kmlType = mtma.cur.fetchone()[0]
        if kmlType == MTurkMappingAfrica.KmlQAQC:
            kmlType = 'QAQC'
        elif kmlType == MTurkMappingAfrica.KmlFQAQC:
            kmlType = 'FQAQC'
        elif kmlType == MTurkMappingAfrica.KmlNormal:
            kmlType = 'non-QAQC'
        elif kmlType == MTurkMappingAfrica.KmlTraining:
            kmlType = 'training'

        instructions = "Please use the toolbar below to map all crop fields that are wholly or partially inside the white square (map the entire field, even the part that falls outside the box). <br/> Then save your changes by clicking on the disk icon to complete the HIT. (Note: if you see a multi-world map, you can reset it by either zooming in (and then out)<br/> by one click, panning the map slightly, or (somewhat slower) refreshing your browser.)"

        # MTurk cases.
        try:
            hitId = req.params['hitId']
            assignmentId = req.params['assignmentId']
            # MTurk accept case.
            if assignmentId != 'ASSIGNMENT_ID_NOT_AVAILABLE':
                workerId = req.params['workerId']
                disabled = ''
                submitTo = req.params['turkSubmitTo'] + MTurkMappingAfrica.externalSubmit
                target = '_self'
            # MTurk preview case.
            else:
                # For preview case, replace the actual map with the first training map.
                instructions = '*** PREVIEW Mode Disabled - Sample Map Only ***<br/>Please click on the Accept HIT button above in order to view and work on an actual map.'
                mtma.cur.execute("""select name from kml_data where kml_type = '%s' 
                        order by gid limit 1""" % MTurkMappingAfrica.KmlTraining)
                kmlName = mtma.cur.fetchone()[0]
                workerId = ''
                disabled = 'disabled'
                submitTo = ''
                target = ''
            trainingId = ''
            tryNum = 0
            mapHint = ''
        # Training, worker feedback, and standalone cases.
        except:
            hitId = ''
            assignmentId = ''
            disabled = 'disabled'
            # Training case.
            try:
                submitTo = req.params['submitTo']
                target = '_parent'
                trainingId = req.params['trainingId']
                tryNum = int(req.params['tryNum'])
                mapHint = '<div class="hints">' + req.params['mapHint'] + '</div>'
                headerHeight = headerHeight + 35
                mapHeight = mturkFrameHeight - headerHeight
                workerId = ''
            # Worker feedback and standalone cases.
            except:
                submitTo = ''
                target = ''
                trainingId = ''
                tryNum = 0
                mapHint = ''
                # Worker feedback case.
                try:
                    workerId = req.params['workerId']
                # Standalone case.
                except:
                    workerId = ''

        mainText = '''
            <!DOCTYPE html>
            <html>
                <head>
                    <title>One Square Km in South Africa</title>
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                    <script type="text/javascript" src="/OL/OpenLayers-2.12/OpenLayers.js"></script>
                    <script type="text/javascript" src="https://maps.google.com/maps/api/js?v=3.8&sensor=false"></script>
                    <script type="text/javascript" src="/OL/showkml.js"></script>
                    <link rel="stylesheet" href="/OL/showkml.css" type="text/css">
                    <style>
                        html, body {
                            height: %(mturkFrameHeight)spx;
                        }
                        .hints {
                            font-size:10pt;
                            font-family:arial;
                        /*
                            font-weight:bold;
                        */
                            text-align:center;
                            color: blue;
                            margin: 0;
                        }
                    </style>
                </head>
                <body onload="init('%(kmlPath)s', '%(polygonPath)s', '%(noPolygonPath)s', '%(kmlName)s', '%(assignmentId)s', '%(trainingId)s', %(tryNum)s, '%(mapPath)s', '%(workerId)s')">
                    <form style='width: 100%%; height: %(headerHeight)spx;' name='mturkform' action='%(submitTo)s' method='POST' target='%(target)s'>
                        <div class='instructions'>
                            %(instructions)s
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
                        %(mapHint)s
                        <input type='hidden' name='assignmentId' value='%(assignmentId)s' />
                        <input type='hidden' name='trainingId' value='%(trainingId)s' />
                        <input type='hidden' name='kmlName' value='%(kmlName)s' />
                        <input type='hidden' name='save_status_code' />
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
            'tryNum': tryNum,
            'submitTo': submitTo,
            'target': target,
            'instructions': instructions,
            'disabled': disabled,
            'mapHint': mapHint,
            'mturkFrameHeight': mturkFrameHeight,
            'headerHeight': headerHeight,
            'mapHeight': mapHeight,
            'mapPath': mapUrl,
            'workerId': workerId
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
                    k.write("getkml: MTurk ACCEPT request fetched %s kml = %s\n" % (kmlType, kmlName))
                    mtma.dbcon.commit()
                # Else, this is the continuation of a previously accepted HIT.
                else:
                    k.write("getkml: MTurk CONTINUE request fetched %s kml = %s\n" % (kmlType, kmlName))
                k.write("getkml: MTurk provided hitId = %s\n" % hitId)
                k.write("getkml: MTurk provided assignmentId = %s\n" % assignmentId)
                k.write("getkml: MTurk provided workerId = %s\n" % workerId)
                k.write("getkml: MTurk provided turkSubmitTo = %s\n" % submitTo)
            # else, this is a HIT preview.
            else:
                k.write("getkml: MTurk PREVIEW request fetched %s kml = %s\n" % (kmlType, kmlName))
                k.write("getkml: MTurk provided hitId = %s\n" % hitId)
        # Else, we are not running under MTurk.
        elif len(trainingId) > 0:
            k.write("getkml: Training request fetched %s kml = %s\n" % (kmlType, kmlName))
        else:
            k.write("getkml: Non-MTurk request fetched %s kml = %s\n" % (kmlType, kmlName))

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
    del mtma
    k.close()
    return res(environ, start_response)
