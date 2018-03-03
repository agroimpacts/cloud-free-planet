import subprocess
from webob import Request, Response
import psycopg2
import datetime
from MappingCommon import MappingCommon

def application(environ, start_response):
    req = Request(environ)
    res = Response()

    now = str(datetime.datetime.today())

    mapc = MappingCommon()
    logFilePath = mapc.projectRoot + "/log"

    k = open(logFilePath + "/OL.log", "a")
    k.write("\nputkml: datetime = %s\n" % now)

    kmlName = req.params['kmlName']
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
    k.write("putkml: OL reported 'save' without polygons for %s kml = %s\n" % (kmlType, kmlName))

    assignmentId = req.params['assignmentId']
    trainingId = req.params['trainingId']
    tryNum = int(req.params['tryNum'])
    if len(assignmentId) > 0:
        k.write("putkml: MTurk Assignment ID = %s\n" % assignmentId)
    elif len(trainingId) > 0:
        k.write("putkml: Training ID = %s; try %d\n" % (trainingId, tryNum))
    else:
        k.write("putkml: No MTurk Assignment or Training ID\n")

    # If this is a training map, then call the scoring routine and 
    # record the results here.
    if len(trainingId) > 0:
        scoreString = subprocess.Popen(["Rscript", "%s/spatial/R/KMLAccuracyCheck.R" % mapc.projectRoot, "tr", kmlName, trainingId, str(tryNum)], 
            stdout=subprocess.PIPE).communicate()[0]
        try:
            score = float(scoreString)
        # Pay the worker if we couldn't score his work properly.
        except:
            score = 1.          # Give worker the benefit of the doubt
            k.write("putkml: Invalid value '%s' returned from R scoring script; assigning a score of %.2f\n" % 
                (scoreString, score))
        hitAcceptThreshold = float(mapc.getConfiguration('HitI_AcceptThreshold'))
        k.write("putkml: training assignment has been scored as: %.2f/%.2f\n" %
            (score, hitAcceptThreshold))
        if score < hitAcceptThreshold:
            res.status = '460 Low Score'

        # Record the assignment submission time and score.
        mapc.cur.execute("""update qual_assignment_data set completion_time = '%s',
            score = '%s' where training_id = '%s' and name = '%s'""" %
            (now, score, trainingId, kmlName))
        mapc.dbcon.commit()

    del mapc
    k.close()
    return res(environ, start_response)
