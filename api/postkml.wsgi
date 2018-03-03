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
        # Use this to store name and assignment ID of completed kml in DB.
        kmlName = req.params['foldersName']
        assignmentId = req.params['assignmentId']
        tryNum = int(req.params['tryNum'])

        #k.write("test: aid:%s tn:%d\n" % (assignmentId,tryNum))
        kmlTypeDescr = mapc.getKmlTypeDescription(kmlName)
        k.write("postkml: OL saved polygons for %s kml = %s\n" % (kmlTypeDescr, kmlName))
        if assignmentId:
            k.write("postkml: Assignment ID = %s\n" % assignmentId)
        else:
            k.write("postkml: No Assignment ID\n")

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
                if tryNum == 0:
                    #mapc.cur.execute("""INSERT INTO user_maps (name, geom, completion_time, 
                    #    assignment_id)
                    #    SELECT %s AS name, ST_GeomFromKML(%s) AS geom, %s AS datetime, 
                    #    %s as assignment_id""",
                    #    (polyName, polygon, now, assignmentId))
                    mapc.cur.execute("""INSERT INTO user_maps (name, geom, completion_time, 
                        assignment_id, geom_clean)
                        SELECT %s AS name, ST_GeomFromKML(%s) AS geom, %s AS datetime, 
                        %s as assignment_id, ST_MakeValid(ST_GeomFromKML(%s)) AS geom_clean""",
                        (polyName, polygon, now, assignmentId, polygon))
                # If training, store into qual_user_maps.
                else:
                    #mapc.cur.execute("""INSERT INTO qual_user_maps (name, geom, completion_time, 
                    #    assignment_id, try)
                    #    SELECT %s AS name, ST_GeomFromKML(%s) AS geom, %s AS datetime, 
                    #    %s as worker_id, %s as try""",
                    #    (polyName, polygon, now, assignmentId, tryNum))
                    geomType = mapc.querySingleValue("SELECT GeometryType(ST_MakeValid(ST_GeomFromKML('%s')))" % polygon)
                    geomValue = mapc.querySingleValue("SELECT ST_IsValidDetail(ST_MakeValid(ST_GeomFromKML('%s')))" % polygon)
                    # ST_IsValidDetail returns with format '(t/f,"reason",geometry)'
                    geomValid, geomReason, dummy = geomValue[1:-1].split(',')
                    # Convert geomValid to boolean
                    geomValid = (geomValid == 't')
                    #k.write("geomType %s, geomValid %s, geomReason %s\n" % (geomType, geomValid, geomReason))
                    if geomType == 'POLYGON' and geomValid is True:
                        mapc.cur.execute("""INSERT INTO qual_user_maps (name, geom, completion_time, 
                                assignment_id, try, geom_clean)
                                SELECT %s AS name, ST_MakeValid(ST_GeomFromKML(%s)) AS geom, %s AS datetime, 
                                %s as assignment_id, %s as try, ST_MakeValid(ST_GeomFromKML(%s)) AS geom_clean""",
                                (polyName, polygon, now, assignmentId, tryNum, polygon))
                    elif geomType != 'POLYGON':
                        k.write("postkml: Processed KML shape %s is a %s and not a polygon\n" % (polyName, geomType))
                        k.write("postkml: Ignoring this shape and continuing\n")
                    elif geomValid is False:
                        k.write("postkml: Processed KML shape %s is not valid: %s\n" % (polyName, geomReason))
                        k.write("postkml: Ignoring this shape and continuing\n")
                mapc.dbcon.commit()
            except psycopg2.InternalError as e:
                k.write("postkml: Database error %s: %s" % (e.pgcode, e.pgerror))
                mapc.dbcon.rollback()
                if e.pgerror.find('invalid KML representation') != -1:
                    k.write("postkml: Ignoring this polygon and continuing\n")
                else:
                    k.write("postkml: INternal database error %s: %s\n" % (e.pgcode, e.pgerror))
                    mapc.createAlertIssue("Postkml problem",
                            """Internal database error %s:\n%s\nkml = %s, polygon name = %s\npolygon = %s\nIgnoring this polygon and continuing. See log file for more details.\n""" %
                            (e.pgcode, e.pgerror, kmlName, polyName, polygon))
            except psycopg2.Error as e:
                k.write("postkml: General database error %s: %s\n" % (e.pgcode, e.pgerror))
                mapc.dbcon.rollback()
                mapc.createAlertIssue("Postkml problem",
                        "General database error %s:\n%s\nkml = %s, polygon name = %s\npolygon = %s\nIgnoring this polygon and continuing. See log file for more details.\n" %
                        (e.pgcode, e.pgerror, kmlName, polyName, polygon))
        # This gets executed if we did not break out of the loop: i.e., if no unexpected errors.
        else:
            pass
            #if tryNum == 0:
            #    mapFix(mapc, "ma", kmlName, assignmentId, "no")
            #else:
            #    mapFix(mapc, "tr", kmlName, assignmentId, "no", tryNum)
            #mapc.dbcon.commit()

    except:
        e = traceback.format_exc()
        k.write("postkml: Error: %s" % e)

    del mapc
    k.close()
    return res(environ, start_response)

# Uncomment two lines below for reporting tracebacks in Firebug.
#from paste.exceptions.errormiddleware import ErrorMiddleware
#application = ErrorMiddleware(application, debug=True)
