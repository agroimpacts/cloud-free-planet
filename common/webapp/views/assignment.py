import datetime
import random
import string
import cgi
import psycopg2
from urllib import quote_plus
from xml.dom.minidom import parseString
from flask import current_app, flash
from flask import Blueprint, redirect, render_template
from flask import request, url_for
from flask_user import current_user, login_required, roles_accepted
from flask_user.views import _get_safe_next_param, render, _send_registered_email, _endpoint_url, _do_login_user
from flask_user import signals
from webapp.models.user_models import MappingForm
from MappingCommon import MappingCommon
from mapFix import mapFix

map_blueprint = Blueprint('map_blueprint', __name__)

# This is the employee agricultural fields mapping page builder.
# The Employee submenu is accessible to authenticated users with the 'employee' role
@map_blueprint.route('/employee/assignment', methods=['GET', 'POST'])
@roles_accepted('employee')
@login_required  # Limits access to authenticated users
def assignment():
    now = str(datetime.datetime.today())
    mapForm = MappingForm(request.form)

    mapc = MappingCommon()
    logFilePath = mapc.projectRoot + "/log"
    serverName = mapc.getConfiguration('ServerName')
    apiUrl = mapc.getConfiguration('APIUrl')
    kmlFrameScript = mapc.getConfiguration('KMLFrameScript')
    hitAcceptThreshold = float(mapc.getConfiguration('HitI_AcceptThreshold'))

    kmlFrameUrl = "https://%s%s/%s" % (serverName, apiUrl, kmlFrameScript)
    mapForm.kmlFrameUrl.data = kmlFrameUrl
    # Set submit path to be this script.
    submitTo = url_for('map_blueprint.assignment')
    mapForm.submitTo.data = submitTo

    k = open(logFilePath + "/OL.log", "a")
    k.write("\nassignment: datetime = %s\n" % now)

    # Use the logged-in user's id as the worker id.
    cu = current_user
    workerId = cu.id

    # If this is a POST request, then save any worker maps, and check the mapping accuracy. 
    # Then either retry the KML or move on to next KML.
    if request.method == 'POST':
        kmlName = mapForm.kmlName.data
        assignmentId = mapForm.assignmentId.data
        comment = mapForm.comment.data
        kmlData = mapForm.kmlData.data
        kmlTypeDescr = mapc.getKmlTypeDescription(kmlName)
        score = None
        assignmentStatus = None

        # If no kmlData, then no fields were mapped.
        if len(kmlData) == 0:
            k.write("assignment: OL reported 'save' without polygons for %s kml = %s\n" % (kmlTypeDescr, kmlName))
            k.write("assignment: Worker ID %s\nAssignment ID = %s\n" % (workerId, assignmentId))
        else:
            k.write("assignment: OL saved polygons for %s kml = %s\n" % (kmlTypeDescr, kmlName))
            k.write("assignment: Worker ID %s\nAssignment ID = %s\n" % (workerId, assignmentId))

            # Loop over every Polygon, and store its name and data in PostGIS DB.
            numPoly = 0
            numFail = 0
            errorString = ''
            k.write("assignment: kmlData = %s\n" % kmlData)
            kmlData = parseString(kmlData)
            for placemark in kmlData.getElementsByTagName('Placemark'):
                numPoly += 1
                # Get shape name, type, and XML description.
                children = placemark.childNodes
                polyName = children[0].firstChild.data
                k.write("assignment: Shape name = %s\n" % polyName)
                polyType = children[1].tagName
                k.write("assignment: Shape type = %s\n" % polyType)
                polygon = children[1].toxml()
                k.write("assignment: Shape KML = %s\n" % polygon)

                # Attempt to convert from KML to ***REMOVED*** geom format.
                try:
                    # Report type and validity of this shape.
                    geomType = mapc.querySingleValue("SELECT GeometryType(ST_GeomFromKML('%s'))" % polygon)
                    geomValue = mapc.querySingleValue("SELECT ST_IsValidDetail(ST_GeomFromKML('%s'))" % polygon)
                    # ST_IsValidDetail returns with format '(t/f,"reason",geometry)'
                    geomValid, geomReason, dummy = geomValue[1:-1].split(',')
                    # Convert geomValid to boolean
                    geomValid = (geomValid == 't')
                    if geomValid:
                        k.write("assignment: Shape is a valid %s\n" % geomType)
                    else:
                        k.write("assignment: Shape is an invalid %s due to '%s'\n" % (geomType, geomReason))
                    mapc.cur.execute("""INSERT INTO qual_user_maps (name, geom, completion_time, assignment_id, try)
                            SELECT %s AS name, ST_GeomFromKML(%s) AS geom, %s AS datetime, %s as assignment_id, %s as try""",
                            (polyName, polygon, now, assignmentId, tryNum))
                    mapc.dbcon.commit()
                except psycopg2.InternalError as e:
                    numFail += 1
                    mapc.dbcon.rollback()
                    errorString += "\nKML shape %s raised an internal datatase exception: %s\n%s%s\n" % (polyName, e.pgcode, e.pgerror, cgi.escape(polygon))
                    k.write("assignment: Internal database error %s\n%s" % (e.pgcode, e.pgerror))
                    k.write("assignment: Ignoring this polygon and continuing\n")
                except psycopg2.Error as e:
                    numFail += 1
                    mapc.dbcon.rollback()
                    errorString += "\nKML shape %s raised a general datatase exception: %s\n%s%s\n" % (polyName, e.pgcode, e.pgerror, cgi.escape(polygon))
                    k.write("assignment: General database error %s\n%s" % (e.pgcode, e.pgerror))
                    k.write("assignment: Ignoring this polygon and continuing\n")

            # If we have at least one invalid shape.
            if numFail > 0:
                k.write("NOTE: %s shape(s) out of %s were invalid\n" % (numFail, numPoly))
                mapc.createAlertIssue("Database geometry problem",
                        "Worker ID = %s\nAssignment ID = %s; try %s\nNOTE: %s shape(s) out of %s were invalid\n%s" % 
                        (workerId, assignmentId, tryNum, numFail, numPoly, errorString))

            # If we have at least one valid polygon.
            if numPoly > numFail:
                try:
                    mapFix(mapc, "tr", kmlName, assignmentId, "no", tryNum)
                    mapc.dbcon.commit()
                except Exception as e:
                    assignmentStatus = MappingCommon.HITUnscored
                    score = mapc.getQualityScore(workerId)
                    if score is None:
                        score = 1.          # Give new worker the max score
                    mapForm.resultsAccepted.data = 1
                    k.write("assignment: mapfix raised an exception: %s\n" % e.message)
                    #mapc.createAlertIssue("mapFix problem", "Mapfix raised an exception: %s\n" % e.message)

            else:
                assignmentStatus = MappingCommon.HITUnsaved
                score = 0.                          # Give new worker the min score
                mapForm.resultsAccepted.data = 3   # Indicate unsaved results.

        # Compute the worker's score on this KML.
        if score is None:
            score, scoreString = mapc.kmlAccuracyCheck(MappingCommon.KmlTraining, kmlName, assignmentId, tryNum)
            # Reward the worker if we couldn't score his work properly.
            if score is None:
                assignmentStatus = MappingCommon.HITUnscored
                score = mapc.getQualityScore(workerId)
                if score is None:
                    score = 1.          # Give new worker the max score
                mapForm.resultsAccepted.data = 1
                k.write("assignment: Invalid value returned from R scoring script for:\nKML %s, worker ID %s, assignment ID %s, try %s; assigning a score of %.2f\nReturned value:\n%s\n" % 
                        (kmlName, workerId, assignmentId, tryNum, score, scoreString)) 
                mapc.createAlertIssue("KMLAccuracyCheck problem", 
                        "Invalid value returned from R scoring script for:\nKML %s, worker ID %s, assignment ID %s, try %s; assigning a score of %.2f\nReturned value:\n%s\n" %
                        (kmlName, workerId, assignmentId, tryNum, score, scoreString))
        # See if score exceeds the Accept threshold
        hitAcceptThreshold = float(mapc.getConfiguration('HitI_AcceptThreshold'))
        k.write("assignment: training assignment has been scored as: %.2f/%.2f\n" %
                (score, hitAcceptThreshold))

        if assignmentStatus is None:
            if score < hitAcceptThreshold:
                assignmentStatus = MappingCommon.HITRejected
                mapForm.resultsAccepted.data = 2   # Indicate rejected results.
            else:
                assignmentStatus = MappingCommon.HITApproved
                mapForm.resultsAccepted.data = 1   # Indicate approved results.

        # Record the assignment submission time and score.
        mapc.cur.execute("""update assignment_data set completion_time = '%s', status = '%s', 
            score = '%s' where assignment_id = '%s'""" %
            (now, assignmentStatus, score, assignmentId))
        mapc.dbcon.commit()

    # If GET request, tell showkml.js to not issue any alerts.
    else:
        mapForm.resultsAccepted.data = 0   # Indicate GET (i.e., no results alert in showkml)

    # Check if new or returning worker.
    qualified = mapc.querySingleValue("""select qualified from worker_data 
            where worker_id = '%s'""" % workerId)

    # First time for worker.
    if qualified is None:
        newWorker = True
        mapc.cur.execute("""INSERT INTO worker_data (worker_id, first_time, last_time) 
                VALUES ('%s', '%s', '%s')""" % (workerId, now, now))
        # Initialize number of training maps successfully completed.
        k.write("assignment: New training candidate %s (%s %s - %s) created.\n" % 
                (workerId, cu.first_name, cu.last_name, cu.email))
        doneCount = 0

    # Returning worker.
    else:
        # Check if worker already qualified.
        if qualified:
            flash("You have already passed the qualification test. You may now map agricultural fields.")
            return redirect(url_for('main.employee_page'))

        newWorker = False
        mapc.cur.execute("""UPDATE worker_data SET last_time = '%s'
                WHERE worker_id = '%s'""" % (now, workerId))
        k.write("assignment: Training candidate %s (%s %s - %s) has returned.\n" % 
                (workerId, cu.first_name, cu.last_name, cu.email))

        # Calculate number of training maps worker has successfully completed.
        doneCount = int(mapc.querySingleValue("""select count(*) 
                from qual_assignment_data where worker_id = '%s'
                and (completion_time is not null and score >= %s)""" %
                (workerId, hitAcceptThreshold)))

    # Get total number of training maps to complete.
    totCount = int(mapc.querySingleValue("""select count(*) from kml_data 
        where kml_type = '%s'""" % MappingCommon.KmlTraining))

    # If worker is not done yet,
    if doneCount < totCount:
        # Fetch the next training map for them to work on.
        mapc.cur.execute("""select name from kml_data
            left outer join 
                (select * from qual_assignment_data where worker_id = '%s') qad 
                using (name)
            where kml_type = '%s'
                and (completion_time is null
                    or score < %s)
            order by gid
            limit 1""" % (workerId, MappingCommon.KmlTraining, hitAcceptThreshold))
        kmlName = mapc.cur.fetchone()[0]
        mapForm.kmlName.data = kmlName
        kmlType = 'training'
        
        # Check the number of tries by this worker on this map.
        tries = mapc.querySingleValue("select tries from qual_assignment_data where worker_id = '%s' and name = '%s'" % (workerId, kmlName))

        # If no assignment for this KML, then worker is just starting the qual test,
        # or has successfully mapped the previous KML.
        if not tries:
            tries = 1
            mapc.cur.execute("""INSERT INTO qual_assignment_data 
                (worker_id, name, tries, start_time, status) 
                VALUES ('%s', '%s', %s, '%s', '%s') RETURNING assignment_id""" % (workerId, kmlName, tries, now, MappingCommon.HITAccepted))
            assignmentId = mapc.cur.fetchone()[0]
        # Else, the user tried and failed to successfully map the previous KML, 
        # and must try again.
        elif request.method == 'POST':
            tries = int(tries) + 1
            mapc.cur.execute("""UPDATE qual_assignment_data SET tries = %s 
                WHERE worker_id = '%s' and name = '%s' RETURNING assignment_id""" % 
                (tries, workerId, kmlName))
            assignmentId = mapc.cur.fetchone()[0]
        # Or user has simply returned (via the menu or refresh) to continue to the test. 
        else:
            assignmentId = mapc.querySingleValue("""SELECT assignment_id FROM assignment_data 
                WHERE worker_id = '%s' and name = '%s'""" %
                (workerId, kmlName))

        mapForm.tryNum.data = tries
        mapForm.assignmentId.data = assignmentId
        k.write("assignment: Candidate starting try %d on %s kml #%s: %s\n" % (tries, kmlType, doneCount + 1, kmlName))

    # Worker is done with training.
    else:
        mapc.cur.execute("""UPDATE worker_data SET last_time = %s, qualified = true,
                scores = %s, returns = %s
                WHERE worker_id = %s""", (now, [], [], workerId))
    mapc.dbcon.commit()

    # Complete building the HTTP response.
    if newWorker:
        progressStatus = qualTestTfTextStart % { 'totCount': totCount }
    else:
        if doneCount < totCount:
            progressStatus = qualTestTfTextMiddle % { 'doneCount': doneCount, 'totCount': totCount }
        else:
            progressStatus = qualTestTfTextEnd % { 'totCount': totCount }
    mapForm.progressStatus.data = progressStatus

    del mapc
    k.close()

    # Pass GET/POST method last used for use by JS running the website menu.
    mapForm.reqMethod.data = request.method

    return render_template('pages/assignment_page.html', form=mapForm)
