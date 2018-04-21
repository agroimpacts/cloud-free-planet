import datetime
import random
import string
import cgi
import psycopg2
from urllib import quote_plus
from flask import current_app, flash
from flask import Blueprint, redirect, render_template
from flask import request, url_for
from flask_user import current_user, login_required, roles_accepted
from flask_user.views import _get_safe_next_param, render, _send_registered_email, _endpoint_url, _do_login_user
from flask_user import signals
from webapp.models.user_models import HistoryForm
from MappingCommon import MappingCommon

hist_blueprint = Blueprint('hist_blueprint', __name__)

# This is the employee assignment history page builder.
# The Employee submenu is accessible to authenticated users with the 'employee' role
@hist_blueprint.route('/employee/assignment_history', methods=['GET', 'POST'])
@roles_accepted('employee')
@login_required  # Limits access to authenticated users
def assignment_history():
    now = str(datetime.datetime.today())
    histForm = HistoryForm(request.form)

    mapc = MappingCommon()
    logFilePath = mapc.projectRoot + "/log"

    # Set submit path to be this script.
    submitTo = url_for('hist_blueprint.assignment_history')
    histForm.submitTo.data = submitTo

    k = open(logFilePath + "/miscellaneous.log", "a")
    k.write("\nhistory: datetime = %s\n" % now)

    # Use the logged-in user's id as the worker id.
    cu = current_user
    workerId = cu.id

    # If this is a POST request, then handle worker inquiry or pagination request.
    if request.method == 'POST':
        pass

    # If GET request, show 20 rows of history based on current pagination parameter.
    mapc.cur.execute("""SELECT event_time, event_type, amount, feedback FROM assignment_history 
            WHERE event_type IN ('%s', '%s') AND worker_id = %s ORDER BY event_time DESC""" %
            (MappingCommon.EVTQualityBonus, MappingCommon.EVTTrainingBonus, workerId))
    histForm.bonusData.data = mapc.cur.fetchall()
    histForm.pageNum.data = 1

    k.write("history: Worker requested history.\n")

    del mapc
    k.close()

    # Pass GET/POST method last used for use by JS running the website menu.
    histForm.reqMethod.data = request.method

    return render_template('pages/assignment_history_page.html', form=histForm)
