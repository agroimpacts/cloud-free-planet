import datetime
import random
import string
from flask import current_app, flash
from flask import Blueprint, redirect, render_template
from flask import request, url_for
from flask_user import current_user, login_required, roles_accepted
from flask_user.views import _get_safe_next_param, render, _send_registered_email, _endpoint_url, _do_login_user
from flask_user import signals
from webapp.models.user_models import QualificationForm
from MappingCommon import MappingCommon

qualification_blueprint = Blueprint('qualification_blueprint', __name__)

# This is the employee qualification test page builder.
# The Employee submenu is accessible to authenticated users with the 'employee' role
@qualification_blueprint.route('/employee/qualification', methods=['GET', 'POST'])
@roles_accepted('employee')
@login_required  # Limits access to authenticated users
def qualification():
    now = str(datetime.datetime.today())
    qualForm = QualificationForm(request.form)

    mapc = MappingCommon()
    logFilePath = mapc.projectRoot + "/log"
    serverName = mapc.getConfiguration('ServerName')
    apiUrl = mapc.getConfiguration('APIUrl')
    kmlFrameScript = mapc.getConfiguration('KMLFrameScript')
    hitAcceptThreshold = float(mapc.getConfiguration('HitI_AcceptThreshold'))
    qualTestTfTextStart = mapc.getConfiguration('QualTest_TF_TextStart')
    qualTestTfTextMiddle = mapc.getConfiguration('QualTest_TF_TextMiddle')
    qualTestTfTextEnd = mapc.getConfiguration('QualTest_TF_TextEnd')

    kmlFrameUrl = "https://%s%s/%s" % (serverName, apiUrl, kmlFrameScript)
    qualForm.kmlFrameUrl.data = kmlFrameUrl
    # Set submit path to be this script.
    submitTo = url_for('qualification_blueprint.qualification')
    qualForm.submitTo.data = submitTo

    k = open(logFilePath + "/OL.log", "a")
    k.write("\nqualification: datetime = %s\n" % now)

    # Use the logged-in user's id as the worker id.
    cu = current_user
    workerId = cu.id

    # If this is a POST request, then check the mapping accuracy and either retry KML or move on to next KML.
    if request.method == 'POST':
        saveStatusCode = int(qualForm.saveStatusCode.data)
        resultsSaved = (saveStatusCode >= 200 and saveStatusCode < 300)
        kmlName = qualForm.kmlName.data
        assignmentId = qualForm.assignmentId.data
        tryNum = str(qualForm.tryNum.data)

        # If the worker's results were saved, compute the worker's score on this KML.
        assignmentStatus = None
        if resultsSaved:
            score, scoreString = mapc.kmlAccuracyCheck(MappingCommon.KmlTraining, kmlName, assignmentId, tryNum)
            # Reward the worker if we couldn't score his work properly.
            if score is None:
                assignmentStatus = MappingCommon.HITUnscored
                qualForm.resultsAccepted.data = 1
                score = 1.          # Give worker the benefit of the doubt
                k.write("qualification: Invalid value returned from R scoring script for KML %s, assignment ID %s, try %s; assigning a score of %.2f\nReturned value:\n%s\n" % 
                        (kmlName, assignmentId, tryNum, score, scoreString)) 
                #mapc.createAlertIssue("Qualification problem", 
                #        "Invalid value returned from R scoring script for KML %s, assignment ID %s, try %s; assigning a score of %.2f\nReturned value:\n%s\n" %
                #        (kmlName, assignmentId, tryNum, score, scoreString))
        # Reward the worker if we couldn't save his work.
        else:
            assignmentStatus = MappingCommon.HITUnsaved
            qualForm.resultsAccepted.data = 3
            score = 1.              # Give worker the benefit of the doubt
            k.write("qualification: Unable to save worker's results for KML %s, assignment ID %s, try %s; assigning a score of %.2f\n" % 
                    (kmlName, assignmentId, tryNum, score))
            #mapc.createAlertIssue("Qualification problem", 
            #        "Unable to save worker's results for KML %s, assignment ID %s, try %s; assigning a score of %.2f\n" %
            #        (kmlName, assignmentId, tryNum, score))
        # Results have been saved and scored successfuly.
        # See if score exceeds the Accept threshold
        hitAcceptThreshold = float(mapc.getConfiguration('HitI_AcceptThreshold'))
        k.write("qualification: training assignment has been scored as: %.2f/%.2f\n" %
                (score, hitAcceptThreshold))
        if assignmentStatus is None:
            if score < hitAcceptThreshold:
                assignmentStatus = MappingCommon.HITRejected
                qualForm.resultsAccepted.data = 2
            else:
                assignmentStatus = MappingCommon.HITApproved
                qualForm.resultsAccepted.data = 1

        # Record the assignment submission time and score.
        mapc.cur.execute("""update qual_assignment_data set completion_time = '%s', status = '%s', 
            score = '%s', save_status_code = %s where assignment_id = '%s'""" %
            (now, assignmentStatus, score, saveStatusCode, assignmentId))
        mapc.dbcon.commit()
    # If GET request, tell showkml.js to not issue any alerts.
    else:
        qualForm.resultsAccepted.data = 0

    # Check if new or returning worker.
    qualified = mapc.querySingleValue("""select qualified from worker_data 
            where worker_id = '%s'""" % workerId)

    # First time for worker.
    if qualified is None:
        newWorker = True
        mapc.cur.execute("""INSERT INTO worker_data (worker_id, first_time, last_time) 
                VALUES ('%s', '%s', '%s')""" % (workerId, now, now))
        # Initialize number of training maps successfully completed.
        k.write("qualification: New training candidate %s (%s %s - %s) created.\n" % 
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
        k.write("qualification: Training candidate %s (%s %s - %s) has returned.\n" % 
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
        qualForm.kmlName.data = kmlName
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
            assignmentId = mapc.querySingleValue("""SELECT assignment_id FROM qual_assignment_data 
                WHERE worker_id = '%s' and name = '%s'""" %
                (workerId, kmlName))

        qualForm.tryNum.data = tries
        qualForm.assignmentId.data = assignmentId
        k.write("qualification: Candidate starting try %d on %s kml #%s: %s\n" % (tries, kmlType, doneCount + 1, kmlName))

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
    qualForm.progressStatus.data = progressStatus

    del mapc
    k.close()

    # Pass GET/POST method last used for use by menu JS.
    qualForm.reqMethod.data = request.method

    return render_template('pages/qualification_page.html', form=qualForm)
