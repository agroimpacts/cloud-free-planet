import subprocess
from webob import Request, Response
from xml.dom.minidom import parseString
import psycopg2
import datetime
from MappingCommon import MappingCommon
from mapFix import mapFix
import traceback

def application(environ, start_response):
    req = Request(environ)
    res = Response()

    now = str(datetime.datetime.today())

    mapc = MappingCommon()
    logFilePath = mapc.projectRoot + "/log"

    k = open(logFilePath + "/OL.log", "a")
    k.write("\npostkml: datetime = %s\n" % now)

    try:
        # Use this to store name and Assignment ID of completed kml in DB.
        kmlValue = req.params['foldersName'].split('_')
        #k.write("test: kmlvalue: %s\n" % kmlValue)
        kmlName = kmlValue[0]

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

        # If regular assignment, then there will be two components to foldersName.
        if len(kmlValue) == 2:
            assignmentId = kmlValue[1]
            trainingId = None
            tryNum = None
        # If training assignment, then there will be three components to foldersName.
        elif len(kmlValue) == 3:
            assignmentId = None
            trainingId = kmlValue[1]
            tryNum = int(kmlValue[2])
        # If standalone invocation, then there will be no splits.
        else:
            assignmentId = None
            trainingId = None
            tryNum = None

        #k.write("test: aid:%s tid:%s tn:%d\n" % (assignmentId,trainingId,tryNum))
        k.write("postkml: OL saved polygons for %s kml = %s\n" % (kmlType, kmlName))
        if assignmentId:
            k.write("postkml: MTurk Assignment ID = %s\n" % assignmentId)
        elif trainingId:
            k.write("postkml: Training ID = %s; try %d\n" % (trainingId, tryNum))
        else:
            k.write("postkml: No MTurk Assignment or Training ID\n")

        # Loop over every Polygon, and store its name and data in PostGIS DB.
        kml = req.params['kmlData']
        k.write("postkml: kml = %s\n" % kml)
        kml = parseString(kml)
        for placemark in kml.getElementsByTagName('Placemark'):
            polyName = placemark.getElementsByTagName('name')[0].firstChild.data
            polygon = placemark.getElementsByTagName('Polygon')[0].toxml()
            k.write("postkml: polygon name = %s\n" % polyName)
            k.write("postkml: polygon = %s\n" % polygon)

            # Attempt to convert from KML to ***REMOVED*** geom format.
            try:
                # If regular or standalone, store into user_maps.
                if not trainingId:
                    mapc.cur.execute("""INSERT INTO user_maps (name, geom, completion_time, 
                        assignment_id)
                        SELECT %s AS name, ST_GeomFromKML(%s) AS geom, %s AS datetime, 
                        %s as assignment_id""",
                        (polyName, polygon, now, assignmentId))
                # If training, store into qual_user_maps.
                else:
                    mapc.cur.execute("""INSERT INTO qual_user_maps (name, geom, completion_time, 
                        worker_id, try)
                        SELECT %s AS name, ST_GeomFromKML(%s) AS geom, %s AS datetime, 
                        %s as worker_id, %s as try""",
                        (polyName, polygon, now, trainingId, tryNum))
                mapc.dbcon.commit()
            except psycopg2.InternalError as e:
                k.write("postkml: Database error %s: %s" % (e.pgcode, e.pgerror))
                mapc.dbcon.rollback()
                if e.pgerror.find('invalid KML representation') != -1:
                    k.write("postkml: Ignoring this polygon and continuing\n")
                else:
                    mapc.dbcon.rollback()
                    raise
                    break
            except psycopg2.Error as e:
                k.write("postkml: General database error %s: %s" % (e.pgcode, e.pgerror))
                mapc.dbcon.rollback()
                raise
                break
        # This gets executed if we did not break out of the loop: i.e., if no errors.
        else:
            if assignmentId:
                mapFix(mapc, "ma", kmlName, assignmentId, "no")
            elif trainingId:
                mapFix(mapc, "tr", kmlName, trainingId, "no", tryNum)
            mapc.dbcon.commit()

        # If this is a training map, then call the scoring routine and 
        # record the results here.
        if trainingId:
            scoreString = subprocess.Popen(["Rscript", "%s/spatial/R/KMLAccuracyCheck.R" % mapc.projectRoot, "tr", kmlName, trainingId, str(tryNum)], 
                stdout=subprocess.PIPE).communicate()[0]
            try:
                score = float(scoreString)
            # Pay the worker if we couldn't score his work properly.
            except:
                score = 1.          # Give worker the benefit of the doubt
                k.write("postkml: Invalid value '%s' returned from R scoring script; assigning a score of %.2f\n" % 
                    (scoreString, score))
            hitAcceptThreshold = float(mapc.getConfiguration('HitIAcceptThreshold'))
            k.write("postkml: training assignment has been scored as: %.2f/%.2f\n" %
                (score, hitAcceptThreshold))
            if score < hitAcceptThreshold:
                res.status = '460 Low Score'

            # Record the assignment submission time and score.
            mapc.cur.execute("""update qual_assignment_data set completion_time = '%s',
                score = '%s' where training_id = '%s' and name = '%s'""" %
                (now, score, trainingId, kmlName))
            mapc.dbcon.commit()
    except:
        e = traceback.format_exc()
        k.write("postkml: Error: %s" % e)

    del mapc
    k.close()
    return res(environ, start_response)

# Uncomment two lines below for reporting tracebacks in Firebug.
#from paste.exceptions.errormiddleware import ErrorMiddleware
#application = ErrorMiddleware(application, debug=True)
