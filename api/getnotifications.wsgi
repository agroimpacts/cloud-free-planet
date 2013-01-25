import sys
import psycopg2
from psycopg2.extensions import adapt
import subprocess
from datetime import datetime
from dateutil import tz
from webob import Request, Response
from boto.mturk.connection import MTurkRequestError
from boto.mturk.notification import NotificationMessage, Event
from MTurkMappingAfrica import MTurkMappingAfrica, aws_secret_access_key

def application(environ, start_response):
    req = Request(environ)
    res = Response()

    eventTypes = {
        "AssignmentSubmitted": AssignmentSubmitted,
        "AssignmentAbandoned": AssignmentAbandoned,
        "AssignmentReturned": AssignmentReturned,
        "HITReviewable": HITReviewable,
        "HITExpired": HITExpired
    }
    now = str(datetime.today())

    mtma = MTurkMappingAfrica()
    mtma.cur.execute("select value from configuration where key = 'ProjectRoot'")
    logFilePath = mtma.cur.fetchone()[0] + "/log"

    k = open(logFilePath + "/notifications.log", "a")
    k.write("\ngetnotifications: datetime = %s\n" % now)

    notifMsg = NotificationMessage(req.params)
    #msgOK = notifMsg.verify(aws_secret_access_key)
    msgOK = True
    k.write("getnotifications: Message (no longer) verified: %s\n" % msgOK)

    if msgOK:
        numMsgs = len(notifMsg.events)
        k.write("getnotifications: received %d event(s):\n" % numMsgs)
        
        for i in range(numMsgs):
            event = notifMsg.events[i]
            eventType = event.event_type
            # Convert MTurk's notification time (UTC timestamp) to local time.
            dtmtk = datetime.strptime(event.event_time_str, '%Y-%m-%dT%H:%M:%SZ')
            dtloc = dtmtk.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())
            eventTime = dtloc.strftime('%Y-%m-%d %H:%M:%S')
            hitId = event.hit_id
            if hasattr(event, 'assignment_id'):
                assignmentId = event.assignment_id
            else:
                assignmentId = ''
            k.write("getnotifications: event_type = %s\n" % eventType)
            k.write("getnotifications: event_time_str = %s\n" % eventTime)
            k.write("getnotifications: hit_id = %s\n" % hitId)
            if len(assignmentId) > 0:
                k.write("getnotifications: assignmentId = %s\n" % assignmentId)

            # Process the event type.
            eventTypes[eventType](mtma, k, hitId, assignmentId, eventTime)
            mtma.dbcon.commit()
        
    k.close()
    mtma.close()
    return res(environ, start_response)

def AssignmentAbandoned(mtma, k, hitId, assignmentId, eventTime):
    # Mark the assignment as abandoned.
    mtma.cur.execute("""update assignment_data set completion_time = '%s', completion_status = '%s'
        where assignment_id = '%s'""" % (eventTime, MTurkMappingAfrica.HITAbandoned, assignmentId))
    k.write("getnotifications: assignment has been marked as abandoned\n")

def AssignmentReturned(mtma, k, hitId, assignmentId, eventTime):
    # Mark the assignment as returned.
    mtma.cur.execute("""update assignment_data set completion_time = '%s', completion_status = '%s'
        where assignment_id = '%s'""" % (eventTime, MTurkMappingAfrica.HITReturned, assignmentId))
    k.write("getnotifications: assignment has been marked as returned\n")

def AssignmentSubmitted(mtma, k, hitId, assignmentId, eventTime):
    # Get the assignment and HIT data we need.
    try:
        workerId, submitTime, params, hitStatus = mtma.getAssignment(assignmentId)
    except MTurkRequestError as e:
        k.write("getnotifications: getAssignment failed for assignment ID %s:\n%s\n%s\n" % 
            (assignmentId, e.error_code, e.error_message))
        return
    except AssertionError:
        k.write("getnotifications: Bad getAssignment status for assignment ID %s:\n" % assignmentId)
        return
    # Get the submission status, kml name, and worker comment.
    try:
        kmlName = params['kmlName']
        results_saved = (params['save_status'] == 'true')
        comment = params['comment'].strip()
    except:
        k.write("getnotifications: Missing getAssignment parameter(s) for assignment ID %s:\n" % assignmentId)
        return
    if len(comment) > 2048:
        comment = comment[:2048]

    # If the worker's results were saved, compute the worker's score on this KML.
    if results_saved:
        mtma.cur.execute("select value from configuration where key = 'ProjectRoot'")
        projectRoot = mtma.cur.fetchone()[0]
        scoreString = subprocess.Popen(["Rscript", "%s/R/KMLAccuracyCheck.R" % projectRoot, kmlName, assignmentId], 
            stdout=subprocess.PIPE).communicate()[0]
        try:
            score = float(scoreString)
        # Pay the worker if we couldn't score his work properly.
        except:
            score = 1.
            k.write("getnotifications: Invalid value '%s' returned from R scoring script; assigning a score of %.2f\n" % 
                (scoreString, score))
    # Pay the worker if we couldn't save his work.
    else:
        score = 1.
        k.write("getnotifications: Unable to save worker's results; assigning a score of %.2f\n" %
            score)
    mtma.cur.execute("select value from configuration where key = 'HitAcceptThreshold'")
    hitAcceptThreshold = float(mtma.cur.fetchone()[0])

    # If the worker's results could not be saved or if their score meets the acceptance threshold, 
    # notify worker that his HIT was accepted.
    if not results_saved or score >= hitAcceptThreshold:
        try:
            mtma.approveAssignment(assignmentId)
        except MTurkRequestError as e:
            k.write("getnotifications: approveAssignment failed for assignment ID %s:\n%s\n%s\n" % 
                (assignmentId, e.error_code, e.error_message))
            return
        except AssertionError:
            k.write("getnotifications: Bad approveAssignment status for assignment ID %s:\n" % assignmentId)
            return
        if results_saved:
            completion_status = MTurkMappingAfrica.HITApproved
        else:
            completion_status = MTurkMappingAfrica.HITUnsaved
    # Only if the worker's results were saved and their score did not meet the threshold
    # do we reject the HIT.
    else:
        try:
            # TODO: *** Put reject feedback into configuration table, or have more sophisticated code
            #       to guide what the text should say: e.g., were they close or far? Use different feedback. ***
            mtma.rejectAssignment(assignmentId, "We're sorry, but your score was too low to accept your results.")
        except MTurkRequestError as e:
            k.write("getnotifications: rejectAssignment failed for assignment ID %s:\n%s\n%s\n" % 
                (assignmentId, e.error_code, e.error_message))
            return
        except AssertionError:
            k.write("getnotifications: Bad rejectAssignment status for assignment ID %s:\n" % assignmentId)
            return
        completion_status = MTurkMappingAfrica.HITRejected
    # Record the HIT submission time and status, and user comment.
    mtma.cur.execute("""update assignment_data set completion_time = '%s', completion_status = '%s', 
        comment = %s, score = '%s' where assignment_id = '%s'""" % 
        (submitTime, completion_status, adapt(comment), score, assignmentId))
    k.write("getnotifications: assignment has been marked as %s: %.2f/%.2f\n" % 
        (completion_status.lower(), score, hitAcceptThreshold))

    # TODO: *** If this is a QAQC HIT, set non-QAQC HIT scores since last QAQC HIT to this QAQC HIT's score ***
    # TODO: *** To determine bonus or disqualification, compute cumulative score.
    #           Note that count of QAQC HITs submitted must be at least 3 ***
    #mtma.cur.execute("""select count(score), avg(score) from assignment_data 
    #    where completion_status = '%s' and worker_id = '%s'""" %
    #    (MTurkMappingAfrica.HITSubmitted, workerId)
    #submitCount, cumAvg = mtma.cur.fetchone()

    # Delete the HIT if all assignments have been submitted.
    if hitStatus == 'Reviewable':
        try:
            mtma.disposeHit(hitId)
        except MTurkRequestError as e:
            k.write("getnotifications: disposeHit failed for HIT ID %s:\n%s\n%s\n" % 
                (hitId, e.error_code, e.error_message))
            return
        except AssertionError:
            k.write("getnotifications: Bad disposeHit status for HIT ID %s:\n" % hitId)
            return
        # Record the HIT deletion time.
        mtma.cur.execute("""update hit_data set delete_time = '%s' where hit_id = '%s'""" % (eventTime, hitId))
        k.write("getnotifications: hit has no remaining assignments and has been deleted\n")
    else:
        k.write("getnotifications: hit still has remaining assignments and cannot be deleted\n")

    # TODO: *** Select next KML to create (of same type) and create it ***

# Delete HIT if it expires with outstanding assignments left unsubmitted.
def HITExpired(mtma, k, hitId, assignmentId, eventTime):
    try:
        mtma.disposeHit(hitId)
    except MTurkRequestError as e:
        k.write("getnotifications: disposeHit failed for HIT ID %s:\n%s\n%s\n" % 
            (hitId, e.error_code, e.error_message))
        return
    except AssertionError:
        k.write("getnotifications: Bad disposeHit status for HIT ID %s:\n" % hitId)
        return
    # Record the HIT deletion time and expiration status.
    mtma.cur.execute("""update hit_data set delete_time = '%s', hit_expired = %s where hit_id = '%s'""" % 
        (eventTime, 'true', hitId))
    k.write("getnotifications: hit has expired and has been deleted\n")

def HITReviewable(mtma, k, hitId, assignmentId, eventTime):
    pass
