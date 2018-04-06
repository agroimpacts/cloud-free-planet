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
#from mapFix import mapFix

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
    kmlFrameHeight = mapc.getConfiguration('KMLFrameHeight')
    kmlFrameScript = mapc.getConfiguration('KMLFrameScript')
    #hitAcceptThreshold = float(mapc.getConfiguration('HitI_AcceptThreshold'))

    mapForm.kmlFrameHeight.data = kmlFrameHeight
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
        hitId = mapForm.hitId.data
        assignmentId = mapForm.assignmentId.data
        comment = mapForm.comment.data
        if len(comment) > 2048:
            comment = comment[:2048]
        kmlData = mapForm.kmlData.data
        (kmlType, kmlTypeDescr) = mapc.getKmlType(kmlName)
        score = None
        assignmentStatus = None

        # If no kmlData, then no fields were mapped.
        if len(kmlData) == 0:
            k.write("assignment: OL reported 'save' without mappings for %s kml = %s\n" % (kmlTypeDescr, kmlName))
            k.write("assignment: Worker ID %s\nHIT ID = %s\nAssignment ID = %s\n" % (workerId, hitId, assignmentId))
            # Post-process this worker's results.
            mapc.AssignmentSubmitted(k, hitId, assignmentId, workerId, now, kmlName, kmlType, comment)
        else:
            k.write("assignment: OL saved mapping(s) for %s kml = %s\n" % (kmlTypeDescr, kmlName))
            k.write("assignment: Worker ID %s\nHIT ID = %s\nAssignment ID = %s\n" % (workerId, hitId, assignmentId))

            # Loop over every Polygon, and store its name and data in PostGIS DB.
            numGeom = 0
            numFail = 0
            errorString = ''
            k.write("assignment: kmlData = %s\n" % kmlData)
            kmlData = parseString(kmlData)
            for placemark in kmlData.getElementsByTagName('Placemark'):
                numGeom += 1
                # Get mapping name, type, and XML description.
                children = placemark.childNodes
                geomName = children[0].firstChild.data
                k.write("assignment: Shape name = %s\n" % geomName)
                geomType = children[1].tagName
                k.write("assignment: Shape type = %s\n" % geomType)
                geometry = children[1].toxml()
                k.write("assignment: Shape KML = %s\n" % geometry)

                # Attempt to convert from KML to ***REMOVED*** geom format.
                try:
                    # Report type and validity of this mapping.
                    geomValue = mapc.querySingleValue("SELECT ST_IsValidDetail(ST_GeomFromKML('%s'))" % geometry)
                    # ST_IsValidDetail returns with format '(t/f,"reason",geometry)'
                    geomValid, geomReason, dummy = geomValue[1:-1].split(',')
                    geomValid = (geomValid == 't')
                    if geomValid:
                        k.write("assignment: Shape is a valid %s\n" % geomType)
                    else:
                        k.write("assignment: Shape is an invalid %s due to '%s'\n" % (geomType, geomReason))
                    mapc.cur.execute("""INSERT INTO user_maps (name, geom, completion_time, assignment_id, geom_clean)
                            SELECT %s AS name, ST_GeomFromKML(%s) AS geom, %s AS datetime, %s as assignment_id, 
                            ST_MakeValid(ST_GeomFromKML(%s)) as geom_clean""",
                            (geomName, geometry, now, assignmentId, geometry))
                    mapc.dbcon.commit()
                except psycopg2.InternalError as e:
                    numFail += 1
                    mapc.dbcon.rollback()
                    errorString += "\nKML mapping %s raised an internal datatase exception: %s\n%s%s\n" % (geomName, e.pgcode, e.pgerror, cgi.escape(geometry))
                    k.write("assignment: Internal database error %s\n%s" % (e.pgcode, e.pgerror))
                    k.write("assignment: Ignoring this mapping and continuing\n")
                except psycopg2.Error as e:
                    numFail += 1
                    mapc.dbcon.rollback()
                    errorString += "\nKML mapping %s raised a general datatase exception: %s\n%s%s\n" % (geomName, e.pgcode, e.pgerror, cgi.escape(geometry))
                    k.write("assignment: General database error %s\n%s" % (e.pgcode, e.pgerror))
                    k.write("assignment: Ignoring this mapping and continuing\n")

            # If we have at least one invalid mapping.
            if numFail > 0:
                k.write("NOTE: %s mapping(s) out of %s were invalid\n" % (numFail, numGeom))
                mapc.createAlertIssue("Database geometry problem",
                        "Worker ID = %s\nAssignment ID = %s\nNOTE: %s mapping(s) out of %s were invalid\n%s" % 
                        (workerId, assignmentId, numFail, numGeom, errorString))

            # If we have at least one valid mapping.
            if numGeom > numFail:
                # Post-process this worker's results.
                mapc.AssignmentSubmitted(k, hitId, assignmentId, workerId, now, kmlName, kmlType, comment)
                mapForm.resultsAccepted.data = 0   # Display no results alert in showkml
            else:
                assignmentStatus = MappingCommon.HITUnsaved
                score = 0.                         # Give new worker the min score
                mapForm.resultsAccepted.data = 3   # Indicate unsaved results.

    # If GET request, tell showkml.js to not issue any alerts.
    else:
        mapForm.resultsAccepted.data = 0   # Indicate GET (i.e., no results alert in showkml)

    # Check if new or returning worker.
    qualified = mapc.querySingleValue("""select qualified from worker_data 
            where worker_id = '%s'""" % workerId)

    # Check if worker is qualified.
    if qualified is None or not qualified:
        k.write("assignment: Worker %s tried to map agricultural fields without passing the qualification test.\nNotified and redirected.\n" % workerId)
        flash("You have not passed the qualification test. You may not map agricultural fields. Please hover on the EMPLOYEE menu and click on 'View Training Video' and then 'Take Qualification Test'")
        return redirect(url_for('main.employee_page'))

    # Record the return of this worker.
    mapc.cur.execute("""UPDATE worker_data SET last_time = '%s'
            WHERE worker_id = '%s'""" % (now, workerId))
    k.write("assignment: Worker %s (%s %s - %s) has returned.\n" % 
            (workerId, cu.first_name, cu.last_name, cu.email))

    # Select the next KML for this worker: an active HIT that this worker
    # has not yet been assigned to, and in random order.
    mapc.cur.execute("""select name, hit_id from kml_data k
        inner join hit_data h using (name)
        where delete_time is null
        and not exists (select true from assignment_data a
        where a.hit_id = h.hit_id and worker_id = '%s')
        order by random()
        limit 1""" % workerId)
    row = mapc.cur.fetchone()
    # Check if there are any KMLs to hand out.
    if row is None:
        mapc.createAlertIssue("No available HITs in hit_data table",
                """There are no HITs in the hit_data table that are available to worker %s\n
                Ensure create_hit_daemon is running, and check its log file.""" % 
                workerId)
        k.write("assignment: Worker %s tried to map agricultural fields but there were none to map.\nNotified and redirected.\n" % workerId)
        flash("We apologize, but there are currently no maps for you to work on. We are aware of the problem and will fix it as soon as possible. Please try again later.")
        return redirect(url_for('main.employee_page'))
    kmlName = row[0]
    hitId = row[1]
    mapForm.kmlName.data = kmlName
    (kmlType, kmlTypeDescr) = mapc.getKmlType(kmlName)
        
    mapc.cur.execute("""INSERT INTO assignment_data 
        (hit_id, worker_id, start_time, status) 
        VALUES ('%s', '%s', '%s', '%s') RETURNING assignment_id""" % (hitId, workerId, now, MappingCommon.HITAccepted))
    assignmentId = mapc.cur.fetchone()[0]
    mapc.dbcon.commit()

    mapForm.hitId.data = hitId
    mapForm.assignmentId.data = assignmentId
    k.write("assignment: Worker starting on %s kml %s\n" % (kmlType, kmlName))

    del mapc
    k.close()

    # Pass GET/POST method last used for use by JS running the website menu.
    mapForm.reqMethod.data = request.method

    return render_template('pages/assignment_page.html', form=mapForm)
