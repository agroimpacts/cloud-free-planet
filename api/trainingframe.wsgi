from webob import Request, Response
import datetime
import random
import string
from MTurkMappingAfrica import MTurkMappingAfrica

def application(environ, start_response):
    req = Request(environ)
    res = Response()
    res.content_type = 'text/html'

    now = str(datetime.datetime.today())

    mtma = MTurkMappingAfrica()
    logFilePath = mtma.projectRoot + "/log"
    serverName = mtma.getConfiguration('ServerName')
    apiUrl = mtma.getConfiguration('APIUrl')
    mturkExtQuestionScript = mtma.getConfiguration('MTurkExtQuestionScript')
    hitAcceptThreshold = float(mtma.getConfiguration('HitQAcceptThreshold'))
    qualTestTfTextStart = mtma.getConfiguration('QualTest_TF_TextStart')
    qualTestTfTextMiddle = mtma.getConfiguration('QualTest_TF_TextMiddle')
    qualTestTfTextEnd = mtma.getConfiguration('QualTest_TF_TextEnd')

    kmlUrl = "https://%s%s/%s" % (serverName, apiUrl, mturkExtQuestionScript)

    k = open(logFilePath + "/OL.log", "a")
    k.write("\ntrainingframe: datetime = %s\n" % now)

    # If there's no training ID, then this is the first time for this worker.
    try:
        newWorker = False
        trainingId = req.params['trainingId']
        k.write("trainingframe: Training candidate %s has returned.\n" % trainingId)
        doneCount = int(mtma.querySingleValue("""select count(*) 
            from qual_assignment_data where training_id = '%s'
            and (completion_time is not null and score >= %s)""" % 
            (trainingId, hitAcceptThreshold)))
        mtma.cur.execute("""UPDATE qual_worker_data SET last_time = '%s'
            WHERE training_id = '%s'""" % (now, trainingId))
    except KeyError as e:
        newWorker = True
        # Generate a unique training ID.
        while True:
            trainingId = ''.join([random.choice( \
                string.ascii_letters+string.digits) for ch in range(12)])
            if mtma.querySingleValue("""select count(*) from qual_worker_data 
                    where training_id = '%s'""" % trainingId) == 0:
                break
        k.write("trainingframe: New Training candidate %s created.\n" % trainingId)
        doneCount = 0
        mtma.cur.execute("""INSERT INTO qual_worker_data 
            (training_id, first_time, last_time) 
            VALUES ('%s', '%s', '%s')""" % (trainingId, now, now))
    totCount = int(mtma.querySingleValue("""select count(*) from kml_data 
        where kml_type = 'I' """))
    if doneCount < totCount:
        mtma.cur.execute("""select name, hint from kml_data
            left outer join 
                (select * from qual_assignment_data where training_id = '%s') qad 
                using (name)
            where kml_type = 'I'
                and (completion_time is null
                    or score < %s)
            order by gid
            limit 1""" % (trainingId, hitAcceptThreshold))
        nextKml, hint = mtma.cur.fetchone()
        # Get the type for this kml.
        mtma.cur.execute("select kml_type from kml_data where name = '%s'" % nextKml)
        kmlType = mtma.cur.fetchone()[0]
        if kmlType == MTurkMappingAfrica.KmlQAQC:
            kmlType = 'QAQC'
        elif kmlType == MTurkMappingAfrica.KmlFQAQC:
            kmlType = 'FQAQC'
        elif kmlType == MTurkMappingAfrica.KmlNormal:
            kmlType = 'non-QAQC'
        elif kmlType == MTurkMappingAfrica.KmlTraining:
            kmlType = 'training'
        
        # Increment the number of tries by this worker on this map.
        tries = mtma.querySingleValue("select tries from qual_assignment_data where training_id = '%s' and name = '%s'" % (trainingId, nextKml))
        if not tries:
            tries = 0
        tries = int(tries) + 1
        if tries == 1:
            mtma.cur.execute("""INSERT INTO qual_assignment_data 
                (training_id, name, tries, start_time) 
                VALUES ('%s', '%s', %s, '%s')""" % (trainingId, nextKml, tries, now))
        else:
            mtma.cur.execute("""UPDATE qual_assignment_data SET tries = %s 
                WHERE training_id = '%s' and name = '%s'""" % 
                (tries, trainingId, nextKml))
        k.write("trainingframe: Candidate starting try %d on %s kml = %s\n" % (tries, kmlType, nextKml))
    else:
        nextKml = ''
        hint = ''
        tries = 0
    mtma.dbcon.commit()

    if newWorker:
        status = qualTestTfTextStart % { 'totCount': totCount }
    else:
        if doneCount < totCount:
            status = qualTestTfTextMiddle % { 'doneCount': doneCount, 'totCount': totCount }
        else:
            status = qualTestTfTextEnd % { 'totCount': totCount, 'trainingId': trainingId }
    if len(hint) > 0:
        mapHint = "Map %d hint: %s" % (doneCount + 1, hint)
    else:
        mapHint = ''

    mainText = u'''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Mapping Africa Training Site</title>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                <style type="text/css">
                    html, body {
                        width: 100%%;
                        margin: 0;
                        padding: 0;
                        font-size:10pt;
                        font-family:arial;
                    }
                    .trainhdr {
                        text-align:center;
                        background-color:yellow;
                        margin: 0;
                    }
                </style>
            </head>
            <body>
                <div class="trainhdr">
                    <h2>Welcome to the Mapping Africa Training Site</h2>
                    <p>%(status)s<br/>&nbsp;</p>
                    <!-- <div>%(mapHint)s</div> -->
                </div>
                <iframe height="720" width="100%%" scrolling="auto" frameborder="0" align="center" 
                    src="%(kmlUrl)s?kmlName=%(kmlName)s&trainingId=%(trainingId)s&tryNum=%(tryNum)s&submitTo=%(submitTo)s&mapHint=%(mapHint)s" 
                    name="ExternalQuestionIFrame">
                </iframe>
            </body>
        </html>
    ''' % {
        'kmlUrl': kmlUrl,
        'trainingId': trainingId,
        'kmlName': nextKml,
        'tryNum': tries,
        'status': status,
        'mapHint': mapHint,
        # Set to hard-coded constant for now. Must be same name as this file.
        'submitTo': apiUrl + '/' + 'trainingframe'
    }
    res.text = mainText

    del mtma
    k.close()
    return res(environ, start_response)
