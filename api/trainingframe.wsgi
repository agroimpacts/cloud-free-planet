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
    logFilePath = mtma.getConfiguration('ProjectRoot') + "/log"
    apiUrl = mtma.getConfiguration('APIUrl')
    hitAcceptThreshold = float(mtma.getConfiguration('HitAcceptThreshold'))

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
                string.ascii_letters+string.digits+'-_') for ch in range(12)])
            if mtma.querySingleValue("""select count(*) from qual_worker_data 
                    where training_id = '%s'""" % trainingId) == 0:
                break
        k.write("trainingframe: New Training candidate %s created.\n" % trainingId)
        doneCount = 0
        mtma.cur.execute("""INSERT INTO qual_worker_data 
            (training_id, first_time, last_time) 
            VALUES ('%s', '%s', '%s')""" % (trainingId, now, now))
    totCount = int(mtma.querySingleValue("""select count(*) from kml_data 
        where kml_type = 'I'"""))
    if doneCount < totCount:
        nextKml = mtma.querySingleValue("""select name from kml_data
            left outer join 
                (select * from qual_assignment_data where training_id = '%s') qad 
                using (name)
            where kml_type = 'I'
                and (completion_time is null
                    or score < %s)
            order by gid
            limit 1""" % (trainingId, hitAcceptThreshold))
                # Allow skipping of incomplete training KMLs.
                # If the clause below is added to the above query, the last
                # kml name must be returned in the req onject, and if no row 
                # is returned, the query must be issued without this clause
                # to handle the wrap-around case.
                #and gid > (select gid from kml_data where name = '%s')
        if mtma.querySingleValue("select count(*) from qual_assignment_data where training_id = '%s' and name = '%s'" % (trainingId, nextKml)) == 0:
            mtma.cur.execute("""INSERT INTO qual_assignment_data 
                (training_id, name, start_time) 
                VALUES ('%s' , '%s', '%s')""" % (trainingId, nextKml, now))
            ps = ''
        else:
            ps = 'Please complete the current map before moving on to the next.'
        k.write("trainingframe: Candidate starting on KML %s\n" % nextKml)
        mtma.dbcon.commit()
    else:
        nextKml = ''
        ps = ''
    if newWorker:
        greeting = '''Welcome to the Mapping Africa Training site.<br/>
As described in the training video, here you'll be briefly working 
on %d maps to get hands-on familiarity with identifying and labeling 
agricultural fields.''' % totCount
    else:
        if totCount > doneCount:
            greeting = 'You have successfully completed %d of %d maps.' % \
                (doneCount, totCount)
        else:
            greeting = """Congratulations! You have successfully completed all %d training maps. Now please copy-and-paste<br/><b>%s</b><br/>into the qualification test window's answer field, and click 'Done'.<br/>You will receive an email confirmation that you have earned the Mapping Africa qualification shortly afterward.""" % (totCount, trainingId)
    mainText = u'''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Mapping Africa Training</title>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                <style type="text/css">
                    html, body {
                        width: 100%%;
                        margin: 0;
                        padding: 0;
                        font-size:10pt;
                        font-family:arial;
                    }
                    form {
                        background-color:yellow;
                    }
                </style>
            </head>
            <body>
                <form style='width: 100%%' name="hitForm" method="POST" action="%(submitTo)s">
                    <div align="center">
                        <h2>The Mapping Africa Training Site</h2>
                        <p>%(greeting)s</p>
                        <p>%(ps)s</p>
                        <input type="hidden" name="trainingId" value="%(trainingId)s">
                        <input type="submit" value="Next Uncompleted Training Map">
                        <p></p>
                    </div>
                </form>
                <iframe height="720" width="100%%" scrolling="auto" frameborder="0" align="center" 
                    src="https://mapper.princeton.edu/afmap/api/getkml?kmlName=%(kmlName)s&trainingId=%(trainingId)s&submitTo=%(submitTo)s" 
                    name="ExternalQuestionIFrame">
                </iframe>
            </body>
        </html>
    ''' % {
        'trainingId': trainingId,
        'kmlName': nextKml,
        'greeting': greeting,
        'ps': ps,
        # Set to hard-coded constant for now. Must be same name as this file.
        'submitTo': apiUrl + '/' + 'trainingframe'
    }
    res.text = mainText
    #res.body = mainText

    return res(environ, start_response)
