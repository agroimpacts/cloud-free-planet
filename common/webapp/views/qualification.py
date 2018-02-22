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
    qualification_form = QualificationForm(request.form)
    now = str(datetime.datetime.today())

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
    qualification_form.kmlFrameUrl.data = kmlFrameUrl
    # Set submit path to be this script.
    submitTo = url_for('qualification_blueprint.qualification')
    qualification_form.submitTo.data = submitTo

    k = open(logFilePath + "/OL.log", "a")
    k.write("\nqualification: datetime = %s\n" % now)

    # Use the logged-in user's id as the worker id.
    cu = current_user
    workerId = cu.id
    qualification_form.workerId.data = workerId

    # Check if new or returning worker.
    qualified = mapc.querySingleValue("""select qualified from worker_data 
            where worker_id = '%s'""" % workerId)
    # First time for worker.
    if qualified is None:
        newWorker = True
        k.write("qualification: New training candidate %s (%s %s - %s) created.\n" % 
                (workerId, cu.first_name, cu.last_name, cu.email))
        # Initialize number of training maps successfully completed.
        doneCount = 0
        # INSERT new row if worker not in table.
        mapc.cur.execute("""INSERT INTO worker_data (worker_id, first_time, last_time) 
                VALUES ('%s', '%s', '%s')""" % (workerId, now, now))

    # Returning worker.
    else:
        # Check if worker already qualified.
        if qualified:
            flash("You have already passed the qualification test. You may now map agricultural fields.")
            return redirect(url_for('main.employee'))

        newWorker = False
        k.write("qualification: Training candidate %s (%s %s - %s) has returned.\n" % 
                (workerId, cu.first_name, cu.last_name, cu.email))

        # Calculate number of training maps worker has successfully completed.
        doneCount = int(mapc.querySingleValue("""select count(*) 
                from qual_assignment_data where worker_id = '%s'
                and (completion_time is not null and score >= %s)""" %
                (workerId, hitAcceptThreshold)))
        mapc.cur.execute("""UPDATE worker_data SET last_time = '%s'
                WHERE worker_id = '%s'""" % (now, workerId))

    # Get total number of training maps to complete.
    totCount = int(mapc.querySingleValue("""select count(*) from kml_data 
        where kml_type = '%s'""" % MappingCommon.KmlTraining))

    # If worker is not done yet,
    if doneCount < totCount:
        # Fetch the next training map for them to work on.
        mapc.cur.execute("""select name, hint from kml_data
            left outer join 
                (select * from qual_assignment_data where worker_id = '%s') qad 
                using (name)
            where kml_type = '%s'
                and (completion_time is null
                    or score < %s)
            order by gid
            limit 1""" % (workerId, MappingCommon.KmlTraining, hitAcceptThreshold))
        nextKml, hint = mapc.cur.fetchone()
        qualification_form.kmlName.data = nextKml
        kmlType = 'training'
        
        # Increment the number of tries by this worker on this map.
        tries = mapc.querySingleValue("select tries from qual_assignment_data where worker_id = '%s' and name = '%s'" % (workerId, nextKml))
        if not tries:
            tries = 0
        tries = int(tries) + 1
        if tries == 1:
            mapc.cur.execute("""INSERT INTO qual_assignment_data 
                (worker_id, name, tries, start_time) 
                VALUES ('%s', '%s', %s, '%s')""" % (workerId, nextKml, tries, now))
        else:
            mapc.cur.execute("""UPDATE qual_assignment_data SET tries = %s 
                WHERE worker_id = '%s' and name = '%s'""" % 
                (tries, workerId, nextKml))
        qualification_form.tryNum.data = tries
        k.write("qualification: Candidate starting try %d on %s kml = %s\n" % (tries, kmlType, nextKml))

    # Worker is done with training.
    else:
        hint = ''
        mtma.cur.execute("""UPDATE worker_data SET last_time = %s, qualified = true,
                scores = %s, returns = %s
                WHERE worker_id = %s""", (now, [], [], workerId))
    mapc.dbcon.commit()

    # Complete building the HTTP response.
    if newWorker:
        status = qualTestTfTextStart % { 'totCount': totCount }
    else:
        if doneCount < totCount:
            status = qualTestTfTextMiddle % { 'doneCount': doneCount, 'totCount': totCount }
        else:
            status = qualTestTfTextEnd % { 'totCount': totCount, 'workerId': workerId }
    qualification_form.status.data = status

    if len(hint) > 0:
        mapHint = "Map %d hint: %s" % (doneCount + 1, hint)
    else:
        mapHint = ''
    qualification_form.mapHint.data = mapHint

    del mapc
    k.close()

    qualification_form.reqMethod.data = request.method
    return render_template('pages/qualification_page.html', form=qualification_form)
