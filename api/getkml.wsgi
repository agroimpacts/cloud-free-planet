from webob import Request, Response
import datetime
from MappingCommon import MappingCommon

def application(environ, start_response):
    req = Request(environ)
    res = Response()
    res.content_type = 'text/html'

    now = str(datetime.datetime.today())

    mapc = MappingCommon()
    logFilePath = mapc.projectRoot + "/log"
    mturkFrameHeight = int(mapc.getConfiguration('MTurkFrameHeight'))
    kmlUrl = mapc.getConfiguration('KMLUrl')
    apiUrl = mapc.getConfiguration('APIUrl')
    mapUrl = mapc.getConfiguration('MapUrl')
    mturkPostPolygonScript = mapc.getConfiguration('MTurkPostPolygonScript')
    mturkNoPolygonScript = mapc.getConfiguration('MTurkNoPolygonScript')

    polygonUrl = apiUrl + '/' + mturkPostPolygonScript
    noPolygonUrl = apiUrl + '/' + mturkNoPolygonScript
    headerHeight = 80
    mapHeight = mturkFrameHeight - headerHeight

    k = open(logFilePath + "/OL.log", "a")
    k.write("\ngetkml: datetime = %s\n" % now)

    kmlName = req.params['kmlName']
    if len(kmlName) > 0:
        # Get the type for this kml.
        mapc.cur.execute("select kml_type from kml_data where name = '%s'" % kmlName)
        kmlType = mapc.cur.fetchone()[0]
        if kmlType == MappingCommon.KmlQAQC:
            kmlType = 'QAQC'
        elif kmlType == MappingCommon.KmlFQAQC:
            kmlType = 'FQAQC'
        elif kmlType == MappingCommon.KmlNormal:
            kmlType = 'non-QAQC'
        elif kmlType == MappingCommon.KmlTraining:
            kmlType = 'training'

        instructions = 'Please use the toolbar below to map all crop fields that are wholly or partially inside the white square (map the entire field, even the part that falls outside the box). <br/> Then save your changes by clicking on the disk icon to complete the HIT. Please visit our <a href="http://mappingafrica.princeton.edu/blog.html#!/blog/posts/Frequently-Asked-Questions/6" target="_blank">FAQ</a> for tips on dealing with no imagery and for other advice.'

        # MTurk cases.
        try:
            hitId = req.params['hitId']
            assignmentId = req.params['assignmentId']
            # MTurk accept case.
            if assignmentId != 'ASSIGNMENT_ID_NOT_AVAILABLE':
                workerId = req.params['workerId']
                disabled = ''
                submitTo = req.params['turkSubmitTo'] + MappingCommon.externalSubmit
                target = '_self'
            # MTurk preview case.
            else:
                # For preview case, replace the actual map with the first training map.
                instructions = '*** PREVIEW Mode Disabled - Sample Map Only ***<br/>Please click on the Accept HIT button above in order to view and work on an actual map.'
                mapc.cur.execute("""select name from kml_data where kml_type = '%s' 
                        order by gid limit 1""" % MappingCommon.KmlTraining)
                kmlName = mapc.cur.fetchone()[0]
                workerId = ''
                disabled = 'disabled'
                submitTo = ''
                target = ''
            trainingId = ''
            tryNum = 0
            mapHint = ''
            csrfToken = req.params['csrfToken']
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
                headerHeight = headerHeight + 20
                mapHeight = mturkFrameHeight - headerHeight
                workerId = ''
                csrfToken = req.params['csrfToken']
            # Worker feedback and standalone cases.
            except:
                submitTo = ''
                target = ''
                trainingId = ''
                tryNum = 0
                mapHint = ''
                csrfToken = ''
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
                    <title>One Square Km in Africa</title>
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                    <link rel="stylesheet" href="https://openlayers.org/en/v3.18.2/css/ol.css" type="text/css">
                    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Lato:300,400">
                    <link rel="stylesheet" href="/OL/fontello-799a171d/css/fontello.css" type="text/css" />
                    <link rel="stylesheet" href="/OL/ol3-layerswitcher.css" type="text/css">
                    <link rel="stylesheet" href="/OL/controlbar.css" type="text/css">
                    <link rel="stylesheet" href="/OL/showkml.css" type="text/css">
                    <script src="https://openlayers.org/en/v3.18.2/build/ol.js" type="text/javascript"></script>
                    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
                    <script type="text/javascript" src="/OL/ol3-layerswitcher.js"></script>
                    <script type="text/javascript" src="/OL/controlbar.js"></script>
                    <script type="text/javascript" src="/OL/buttoncontrol.js"></script>
                    <script type="text/javascript" src="/OL/togglecontrol.js"></script>
                    <script type="text/javascript" src="/OL/showkml.js"></script>
                    <style>
                        html, body {
                            height: %(mturkFrameHeight)spx;
                        }
                    </style>
                </head>
                <body onload="init('%(kmlPath)s', '%(polygonPath)s', '%(noPolygonPath)s', '%(kmlName)s', '%(assignmentId)s', '%(trainingId)s', %(tryNum)s, '%(mapPath)s', '%(workerId)s')">
                    <form style='width: 100%%; height: %(headerHeight)spx;' name='mturkform' action='%(submitTo)s' method='POST' target='%(target)s'>
                        %(csrfToken)s
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
                            <i>Hover over the icons in the toolbars below for usage instructions.</i>
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
            'workerId': workerId,
            'csrfToken': csrfToken
        }
        res.text = mainText
        # If we are running under MTurk,
        if len(assignmentId) > 0:
            # If this is an accepted HIT,
            if assignmentId != 'ASSIGNMENT_ID_NOT_AVAILABLE':
                # If this is a new HIT,
                mapc.cur.execute("SELECT TRUE FROM assignment_data WHERE assignment_id = '%s'" % assignmentId)
                if not mapc.cur.fetchone():
                    # Perform an UPSERT to handle the rare case where worker skipped the qualification test.
                    mapc.cur.execute("""UPDATE worker_data SET last_time = '%s' WHERE worker_id = '%s';
                            INSERT INTO worker_data (worker_id, first_time, last_time)
                            SELECT '%s', '%s', '%s' WHERE NOT EXISTS
                            (SELECT true FROM worker_data WHERE worker_id = '%s')"""
                            % (now, workerId, workerId, now, now, workerId))
                    # Insert the assignment data.
                    mapc.cur.execute("""INSERT INTO assignment_data 
                        (assignment_id, hit_id, worker_id, accept_time, status) 
                        VALUES ('%s' , '%s', '%s', '%s', '%s')""" % \
                        (assignmentId, hitId, workerId, now, MappingCommon.HITAccepted))
                    k.write("getkml: MTurk ACCEPT request fetched %s kml = %s\n" % \
                            (kmlType, kmlName))
                    mapc.dbcon.commit()
                # Else, this might be the continuation of a previously accepted HIT,
                # or a handoff of a returned or abandoned assignment to another worker.
                else:
                    mapc.cur.execute("SELECT worker_id FROM assignment_data WHERE assignment_id = '%s'" % assignmentId)
                    prevWorkerId = mapc.cur.fetchone()[0]
                    # If same worker, then its just a continuation.
                    if workerId == prevWorkerId:
                        k.write("getkml: MTurk CONTINUE request fetched %s kml = %s\n" % \
                                (kmlType, kmlName))
                    # Otherwise, it's an assignment transfer to a new worker.
                    else:
                        mapc.cur.execute("""UPDATE assignment_data 
                            SET worker_id = '%s', accept_time = '%s', status = '%s' 
                            WHERE assignment_id = '%s'""" % \
                            (workerId, now, MappingCommon.HITAccepted, assignmentId))
                        k.write("getkml: MTurk ACCEPT request fetched %s kml = %s\n" % \
                                (kmlType, kmlName))
                        k.write("getkml: *** Assignment transfer to new worker ***\n")
                        mapc.dbcon.commit()

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
                    <b>No KML specified in URL.</b>
                </body>
            </html>
        '''
        res.body = mainText
        k.write("getkml: No KML specified in URL.\n")
    del mapc
    k.close()
    return res(environ, start_response)
