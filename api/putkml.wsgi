from webob import Request, Response
import psycopg2
import datetime
from MTurkMappingAfrica import MTurkMappingAfrica

def application(environ, start_response):
    req = Request(environ)
    res = Response()

    now = str(datetime.datetime.today())

    mtma = MTurkMappingAfrica()
    logFilePath = mtma.getConfiguration('ProjectRoot') + "/log"

    k = open(logFilePath + "/OL.log", "a")
    k.write("\nputkml: datetime = %s\n" % now)

    kmlName = req.params['kmlName']
    k.write("putkml: OL reported 'save' without polygons for kml %s\n" % kmlName)

    assignmentId = req.params['assignmentId']
    trainingId = req.params['trainingId']
    if len(assignmentId) > 0:
        k.write("putkml: MTurk Assignment ID = %s\n" % assignmentId)
    elif len(trainingId) > 0:
        k.write("putkml: Training ID = %s\n" % trainingId)
    else:
        k.write("putkml: No MTurk Assignment or Training ID\n")

    # If this is a training map, then call the scoring routine and 
    # record the results here.
    if len(trainingId) > 0:
        score = 0.7

        # Record the HIT submission time and status, and user comment.
        mtma.cur.execute("""update qual_assignment_data set completion_time = '%s',
            score = '%s' where training_id = '%s' and name = '%s'""" %
            (now, score, trainingId, kmlName))
        mtma.dbcon.commit()
        hitAcceptThreshold = float(mtma.getConfiguration('HitAcceptThreshold'))
        k.write("putkml: training assignment has been scored as: %.2f/%.2f\n" %
            (score, hitAcceptThreshold))

    k.close()
    return res(environ, start_response)
