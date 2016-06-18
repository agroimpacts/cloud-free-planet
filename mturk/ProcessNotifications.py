import smtplib
import subprocess
from psycopg2.extensions import adapt
from boto.mturk.notification import NotificationMessage, NotificationEmail, Event
from boto.mturk.connection import MTurkRequestError
from MTurkMappingAfrica import MTurkMappingAfrica, aws_secret_access_key

# Email function used when there are validation failures.
# This email address has been configured on trac.princeton.edu in
# /etc/aliases and /usr/local/etc/email2trac.conf to create a ticket
# under the Internal Alert component.
def email(mtma, msg = None):
    sender = '%s@mapper.princeton.edu' % mtma.euser
    receiver = 'mappingafrica_internal_alert@trac.princeton.edu'
    message = """From: %s
To: %s
Subject: ProcessNotifications problem

%s
""" % (sender, receiver, msg)

    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receiver.split(","), message)
        smtpObj.quit()
    except smtplib.SMTPException:
        print "Error: unable to send email: %s" % message

class ParseEmailNotification(object):
    def __init__(self, fp):
        self.notifMsg = NotificationEmail(fp)

class ParseRestNotification(object):
    def __init__(self, requestObject):
        self.notifMsg = NotificationMessage(requestObject)
        # If signature does not verify, raise exception
        if not self.notifMsg.verify(aws_secret_access_key):
            raise ValueError

class ProcessNotifications(object):

    def __init__(self, mtma, k, notifMsg):
        #
        # HIT notificaton transfer table
        #
        eventTypes = {
            "AssignmentSubmitted": self.AssignmentSubmitted,
            "AssignmentAbandoned": self.AssignmentAbandoned,
            "AssignmentReturned": self.AssignmentReturned,
            "HITReviewable": self.HITReviewable,
            "HITExpired": self.HITExpired
        }
        numMsgs = len(notifMsg.events)
        k.write("ProcessNotifications: received %d event(s):\n" % numMsgs)
        
        for i in range(numMsgs):
            event = notifMsg.events[i]
            eventType = event.event_type
            # Convert local datetime object to string.
            eventTime = event.event_time.strftime('%Y-%m-%d %H:%M:%S')
            hitId = event.hit_id
            if hasattr(event, 'assignment_id'):
                assignmentId = event.assignment_id
            else:
                assignmentId = ''
            k.write("ProcessNotifications: event_type = %s\n" % eventType)
            k.write("ProcessNotifications: event_time_str = %s\n" % eventTime)
            k.write("ProcessNotifications: hit_id = %s\n" % hitId)
            if len(assignmentId) > 0:
                k.write("ProcessNotifications: assignmentId = %s\n" % assignmentId)

            # Process the event type.
            if eventType in eventTypes:
                eventTypes[eventType](mtma, k, hitId, assignmentId, eventTime)

    def AssignmentAbandoned(self, mtma, k, hitId, assignmentId, eventTime):
        # Mark the assignment as abandoned.
        mtma.cur.execute("""update assignment_data set completion_time = '%s', status = '%s'
            where assignment_id = '%s'""" % (eventTime, MTurkMappingAfrica.HITAbandoned, assignmentId))
        k.write("ProcessNotifications: assignment has been marked as abandoned\n")

        # Delete the HIT if all assignments have been submitted and have a final status
        # (i.e., there are no assignments in pending or accepted status).
        try:
            hitStatus = mtma.getHitStatus(hitId)
        except MTurkRequestError as e:
            k.write("ProcessNotifications: getHitStatus failed for HIT ID %s:\n%s\n%s\n" % 
                (hitId, e.error_code, e.error_message))
            return
        except AssertionError:
            k.write("ProcessNotifications: Bad getHitStatus status for HIT ID %s:\n" % hitId)
            return
        if hitStatus == 'Reviewable':
            nonFinalAssignCount = int(mtma.querySingleValue("""select count(*) from assignment_data
                where hit_id = '%s' and status in ('%s','%s')""" %
                (hitId, MTurkMappingAfrica.HITPending, MTurkMappingAfrica.HITAccepted)))
            if nonFinalAssignCount == 0:
                try:
                    mtma.disposeHit(hitId)
                except MTurkRequestError as e:
                    k.write("ProcessNotifications: disposeHit failed for HIT ID %s:\n%s\n%s\n" % 
                        (hitId, e.error_code, e.error_message))
                    return
                except AssertionError:
                    k.write("ProcessNotifications: Bad disposeHit status for HIT ID %s:\n" % hitId)
                    return
                # Record the HIT deletion time.
                mtma.cur.execute("""update hit_data set delete_time = '%s' where hit_id = '%s'""" % 
                        (eventTime, hitId))
                mtma.dbcon.commit()
                k.write("ProcessNotifications: hit has no remaining assignments and has been deleted\n")
            else:
                k.write("ProcessNotifications: hit still has remaining Mturk or pending assignments and cannot be deleted\n")
        else:
            k.write("ProcessNotifications: hit still has remaining Mturk or pending assignments and cannot be deleted\n")

    def AssignmentReturned(self, mtma, k, hitId, assignmentId, eventTime):
        # Record the return in order to compute a return rate.
        mtma.pushReturn(assignmentId, True)

        # Mark the assignment as returned.
        mtma.cur.execute("""update assignment_data set completion_time = '%s', status = '%s'
            where assignment_id = '%s'""" % (eventTime, MTurkMappingAfrica.HITReturned, assignmentId))
        k.write("ProcessNotifications: assignment has been marked as returned\n")

        # Delete the HIT if all assignments have been submitted and have a final status
        # (i.e., there are no assignments in pending or accepted status).
        try:
            hitStatus = mtma.getHitStatus(hitId)
        except MTurkRequestError as e:
            k.write("ProcessNotifications: getHitStatus failed for HIT ID %s:\n%s\n%s\n" % 
                (hitId, e.error_code, e.error_message))
            return
        except AssertionError:
            k.write("ProcessNotifications: Bad getHitStatus status for HIT ID %s:\n" % hitId)
            return
        if hitStatus == 'Reviewable':
            nonFinalAssignCount = int(mtma.querySingleValue("""select count(*) from assignment_data
                where hit_id = '%s' and status in ('%s','%s')""" %
                (hitId, MTurkMappingAfrica.HITPending, MTurkMappingAfrica.HITAccepted)))
            if nonFinalAssignCount == 0:
                try:
                    mtma.disposeHit(hitId)
                except MTurkRequestError as e:
                    k.write("ProcessNotifications: disposeHit failed for HIT ID %s:\n%s\n%s\n" % 
                        (hitId, e.error_code, e.error_message))
                    return
                except AssertionError:
                    k.write("ProcessNotifications: Bad disposeHit status for HIT ID %s:\n" % hitId)
                    return
                # Record the HIT deletion time.
                mtma.cur.execute("""update hit_data set delete_time = '%s' where hit_id = '%s'""" % 
                        (eventTime, hitId))
                mtma.dbcon.commit()
                k.write("ProcessNotifications: hit has no remaining assignments and has been deleted\n")
            else:
                k.write("ProcessNotifications: hit still has remaining Mturk or pending assignments and cannot be deleted\n")
        else:
            k.write("ProcessNotifications: hit still has remaining Mturk or pending assignments and cannot be deleted\n")

    def AssignmentSubmitted(self, mtma, k, hitId, assignmentId, eventTime):
        # Record the submission in order to compute a return rate.
        mtma.pushReturn(assignmentId, False)

        # Get the assignment and HIT data we need.
        try:
            workerId, submitTime, params, hitStatus = mtma.getAssignment(assignmentId)
        except MTurkRequestError as e:
            k.write("ProcessNotifications: getAssignment failed for assignment ID %s:\n%s\n%s\n" % 
                (assignmentId, e.error_code, e.error_message))
            return
        except AssertionError:
            k.write("ProcessNotifications: Bad getAssignment status for assignment ID %s:\n" % assignmentId)
            return
        k.write("ProcessNotifications: workerId = %s\n" % workerId)

        # Get the KML type for this assignment's associated HIT.
        mtma.cur.execute("select kml_type from kml_data inner join hit_data using (name) where hit_id = '%s'" % hitId)
        kmlType = mtma.cur.fetchone()[0]

        # If QAQC HIT, then score it and post-process any preceding FQAQC or non-QAQC HITs for this worker.
        if kmlType == MTurkMappingAfrica.KmlQAQC:
            self.QAQCSubmission(mtma, k, hitId, assignmentId, eventTime, workerId, submitTime, params, hitStatus)
        # Else, if FQAQC HIT or non-QAQC HIT, then post-process it or mark it as pending post-processing.
        elif kmlType == MTurkMappingAfrica.KmlNormal or kmlType == MTurkMappingAfrica.KmlFQAQC:
            self.NormalSubmission(mtma, k, hitId, assignmentId, eventTime, workerId, submitTime, params, hitStatus)

    def QAQCSubmission(self, mtma, k, hitId, assignmentId, eventTime, workerId, submitTime, params, hitStatus):
        # Get the kml name, save status, and worker comment.
        try:
            kmlName = params['kmlName']
            saveStatusCode = params['save_status_code']
            if len(saveStatusCode) == 0:
                saveStatusCode = 0
            saveStatusCode = int(saveStatusCode)
            resultsSaved = (saveStatusCode >= 200 and saveStatusCode < 300)
            comment = params['comment'].strip()
        except:
            k.write("ProcessNotifications: Missing getAssignment parameter(s) for assignment ID %s:\n" % assignmentId)
            return
        k.write("ProcessNotifications: POST/PUT of mapping results returned HTTP status code %s\n" % saveStatusCode)
        if len(comment) > 2048:
            comment = comment[:2048]

        # If the worker's results were saved, compute the worker's score on this KML.
        assignmentStatus = None
        if resultsSaved:
            scoreString = subprocess.Popen(["Rscript", "%s/spatial/R/KMLAccuracyCheck.R" % mtma.projectRoot, 
                "qa", kmlName, assignmentId], 
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]
            try:
                score = float(scoreString)
            # Pay the worker if we couldn't score his work properly.
            except:
                assignmentStatus = MTurkMappingAfrica.HITUnscored
                score = 1.          # Give worker the benefit of the doubt
                k.write("ProcessNotifications: Invalid value returned from R scoring script; assigning a score of %.2f\nReturned value:\n%s\n" % 
                    (score, scoreString))
                email(mtma, "ProcessNotifications: Invalid value returned from R scoring script for KML %s and assignment ID %s; assigning a score of %.2f\nReturned value:\n%s\n" % 
                    (kmlName, assignmentId, score, scoreString))
        # Pay the worker if we couldn't save his work.
        else:
            assignmentStatus = MTurkMappingAfrica.HITUnsaved
            score = 1.              # Give worker the benefit of the doubt
            k.write("ProcessNotifications: Unable to save worker's results; assigning a score of %.2f\n" %
                score)
            email(mtma, "ProcessNotifications: Unable to save worker's results for KML %s and assignment ID %s; assigning a score of %.2f\n" % 
                (kmlName, assignmentId, score))
        # Record score (actual or assumed) to compute moving average.
        mtma.pushScore(workerId, score)

        # Check if Mapping Africa qualification should be revoked
        # (needs to be done for both the approved and rejection cases because a worker may
        #  earn a quality score for the first time at the revocation level)
        if mtma.revokeQualificationIfUnqualifed(workerId, submitTime):
            k.write("ProcessNotifications: Mapping Africa Qualification revoked from worker %s\n" % workerId)

        hitAcceptThreshold = float(mtma.getConfiguration('HitQAcceptThreshold'))
        hitNoWarningThreshold = float(mtma.getConfiguration('HitQNoWarningThreshold'))

        # If the worker's results could not be saved or scored, or if their score meets 
        # the acceptance threshold, notify worker that his HIT was accepted.
        if assignmentStatus != None or score >= hitAcceptThreshold:
            try:
                # if score was above the no-warning thresholdm, then don't include a warning.
                if score >= hitNoWarningThreshold:
                    (fwts, bonusAmount, kmlName, trainBonusPaid) = mtma.approveAssignment(assignmentId)
                else:
                    (fwts, bonusAmount, kmlName, trainBonusPaid) = mtma.approveAssignment(assignmentId, warning=True)
                if fwts > 1:
                    k.write("ProcessNotifications: Difficulty bonus of $%s paid for level %s KML %s to worker %s\n" % (bonusAmount, fwts, kmlName, workerId))
                if trainBonusPaid:
                    k.write("ProcessNotifications: Training bonus paid to worker %s\n" % workerId)
            except MTurkRequestError as e:
                k.write("ProcessNotifications: approveAssignment failed for assignment ID %s:\n%s\n%s\n" % 
                    (assignmentId, e.error_code, e.error_message))
                return
            except AssertionError:
                k.write("ProcessNotifications: Bad approveAssignment status for assignment ID %s:\n" % assignmentId)
                return
            assignmentStatus = MTurkMappingAfrica.HITApproved

            # Also, check if the worker merits a bonus for approved assignment.
            bonusStatus = mtma.payBonusIfQualified(workerId, assignmentId)
            if bonusStatus > 0:
                k.write("ProcessNotifications: Accuracy bonus level %s paid to worker %s\n" % (bonusStatus, workerId))

        # Only if the worker's results were saved and scored, and their score did not meet 
        # the threshold do we reject the HIT.
        else:
            try:
                mtma.rejectAssignment(assignmentId)
            except MTurkRequestError as e:
                k.write("ProcessNotifications: rejectAssignment failed for assignment ID %s:\n%s\n%s\n" % 
                    (assignmentId, e.error_code, e.error_message))
                return
            except AssertionError:
                k.write("ProcessNotifications: Bad rejectAssignment status for assignment ID %s:\n" % assignmentId)
                return
            assignmentStatus = MTurkMappingAfrica.HITRejected

        # Record the HIT submission time and status, user comment, score, and save status code.
        mtma.cur.execute("""update assignment_data set completion_time = '%s', status = '%s', 
            comment = %s, score = '%s', save_status_code = %s where assignment_id = '%s'""" % 
            (submitTime, assignmentStatus, adapt(comment), score, saveStatusCode, assignmentId))
        mtma.dbcon.commit()
        k.write("ProcessNotifications: QAQC assignment has been marked on Mturk and DB as %s: %.2f/%.2f/%.2f\n" % 
            (assignmentStatus.lower(), score, hitAcceptThreshold, hitNoWarningThreshold))

        # Delete the HIT if all assignments have been submitted.
        if hitStatus == 'Reviewable':
            try:
                mtma.disposeHit(hitId)
            except MTurkRequestError as e:
                k.write("ProcessNotifications: disposeHit failed for HIT ID %s:\n%s\n%s\n" % 
                    (hitId, e.error_code, e.error_message))
                return
            except AssertionError:
                k.write("ProcessNotifications: Bad disposeHit status for HIT ID %s:\n" % hitId)
                return
            # Record the HIT deletion time.
            mtma.cur.execute("""update hit_data set delete_time = '%s' where hit_id = '%s'""" % (eventTime, hitId))
            mtma.dbcon.commit()
            k.write("ProcessNotifications: QAQC hit has no remaining assignments and has been deleted\n")
        else:
            k.write("ProcessNotifications: Error: QAQC hit is in %s state and cannot be deleted\n" %
                    hitStatus)

        # Post-process any pending FQAQC or non-QAQC HITs for this worker.
        self.NormalPostProcessing(mtma, k, eventTime, workerId)

    def NormalSubmission(self, mtma, k, hitId, assignmentId, eventTime, workerId, submitTime, params, hitStatus):
        # Get the save status and worker comment.
        try:
            kmlName = params['kmlName']
            saveStatusCode = params['save_status_code']
            if len(saveStatusCode) == 0:
                saveStatusCode = 0
            saveStatusCode = int(saveStatusCode)
            resultsSaved = (saveStatusCode >= 200 and saveStatusCode < 300)
            comment = params['comment'].strip()
        except:
            k.write("ProcessNotifications: Missing getAssignment parameter(s) for assignment ID %s:\n" % assignmentId)
            return
        k.write("ProcessNotifications: POST/PUT of mapping results returned HTTP status code %s\n" % saveStatusCode)
        if len(comment) > 2048:
            comment = comment[:2048]

        # Set the assignment status per the save status.
        if resultsSaved:
            workerTrusted = mtma.isWorkerTrusted(workerId)
            if workerTrusted is None:
                # If not enough history, mark HIT as pending in order to save for post-processing.
                assignmentStatus = MTurkMappingAfrica.HITPending
            elif workerTrusted:
                assignmentStatus = MTurkMappingAfrica.HITApproved

                # Since results trusted, mark this KML as mapped.
                mtma.cur.execute("update kml_data set mapped_count = mapped_count + 1 where name = '%s'" % kmlName)
                k.write("ProcessNotifications: incremented mapped count by trusted worker for KML %s\n" % kmlName)
            else:
                assignmentStatus = MTurkMappingAfrica.HITUntrusted
        else:
            assignmentStatus = MTurkMappingAfrica.HITUnsaved

        # Record the HIT submission time and status, user comment, and save status code.
        mtma.cur.execute("""update assignment_data set completion_time = '%s', status = '%s', 
            comment = %s, save_status_code = %s where assignment_id = '%s'""" % 
            (submitTime, assignmentStatus, adapt(comment), saveStatusCode, assignmentId))

        # In all cases, notify worker that his HIT was accepted.
        try:
            (fwts, bonusAmount, kmlName, trainBonusPaid) = mtma.approveAssignment(assignmentId)
            if fwts > 1:
                k.write("ProcessNotifications: Difficulty bonus of $%s paid for level %s KML %s to worker %s\n" % (bonusAmount, fwts, kmlName, workerId))
            if trainBonusPaid:
                k.write("ProcessNotifications: Training bonus paid to worker %s\n" % workerId)
        except MTurkRequestError as e:
            k.write("ProcessNotifications: approveAssignment failed for assignment ID %s:\n%s\n%s\n" %
                (assignmentId, e.error_code, e.error_message))
            return
        except AssertionError:
            k.write("ProcessNotifications: Bad approveAssignment status for assignment ID %s:\n" % assignmentId)
            return
        k.write("ProcessNotifications: FQAQC or non-QAQC assignment has been approved on Mturk and marked in DB as %s\n" % 
            assignmentStatus.lower())
        mtma.dbcon.commit()

        # Delete the HIT if all assignments have been submitted and have a final status
        # (i.e., there are no assignments in pending or accepted status).
        if hitStatus == 'Reviewable':
            nonFinalAssignCount = int(mtma.querySingleValue("""select count(*) from assignment_data
                where hit_id = '%s' and status in ('%s','%s')""" %
                (hitId, MTurkMappingAfrica.HITPending, MTurkMappingAfrica.HITAccepted)))
            if nonFinalAssignCount == 0:
                try:
                    mtma.disposeHit(hitId)
                except MTurkRequestError as e:
                    k.write("ProcessNotifications: disposeHit failed for HIT ID %s:\n%s\n%s\n" % 
                        (hitId, e.error_code, e.error_message))
                    return
                except AssertionError:
                    k.write("ProcessNotifications: Bad disposeHit status for HIT ID %s:\n" % hitId)
                    return
                # Record the HIT deletion time.
                mtma.cur.execute("""update hit_data set delete_time = '%s' where hit_id = '%s'""" % 
                        (eventTime, hitId))
                mtma.dbcon.commit()
                k.write("ProcessNotifications: hit has no remaining assignments and has been deleted\n")
            else:
                k.write("ProcessNotifications: hit still has remaining Mturk or pending assignments and cannot be deleted\n")
        else:
            k.write("ProcessNotifications: hit still has remaining Mturk or pending assignments and cannot be deleted\n")

    def NormalPostProcessing(self, mtma, k, eventTime, workerId):
        # Determine this worker's trust level.
        workerTrusted = mtma.isWorkerTrusted(workerId)
        if workerTrusted is None:
            k.write("ProcessNotifications: Worker %s has insufficient history for evaluating FQAQC or non-QAQC HITs\n" %
                    workerId)
            return

        # Get the the key data for this worker's pending FQAQC or non-QAQC submitted HITs.
        mtma.cur.execute("""select name, assignment_id, hit_id
            from assignment_data inner join hit_data using (hit_id)
            where worker_id = %s and status = %s order by completion_time""", 
            (workerId, MTurkMappingAfrica.HITPending,))
        assignments = mtma.cur.fetchall()

        # If none then there's nothing to do.
        if len(assignments) == 0:
            return

        k.write("ProcessNotifications: Checking for pending FQAQC or non-QAQC assignments: found %d\n" % len(assignments))

        # Loop on all the pending FQAQC or non-QAQC HITs for this worker, and finalize their status.
        for assignment in assignments:
            kmlName = assignment[0]
            assignmentId = assignment[1]
            hitId = assignment[2]

            k.write("ProcessNotifications: Post-processing assignmentId = %s\n" % assignmentId)

            # If the worker's results are reliable, we will mark the HIT as approved.
            if workerTrusted:
                assignmentStatus = MTurkMappingAfrica.HITApproved

                # Since results trusted, mark this KML as mapped.
                mtma.cur.execute("update kml_data set mapped_count = mapped_count + 1 where name = '%s'" % kmlName)
                k.write("ProcessNotifications: incremented mapped count by trusted worker for KML %s\n" % kmlName)
            else:
                assignmentStatus = MTurkMappingAfrica.HITUntrusted

            # Record the final FQAQC or non-QAQC HIT status.
            mtma.cur.execute("""update assignment_data set status = '%s' where assignment_id = '%s'""" %
                (assignmentStatus, assignmentId))
            mtma.dbcon.commit()
            k.write("ProcessNotifications: FQAQC or non-QAQC assignment marked in DB as %s\n" %
                assignmentStatus.lower())

            # Delete the HIT if all assignments have been submitted and have a final status
            # (i.e., there are no assignments in pending or accepted status).
            try:
                hitStatus = mtma.getHitStatus(hitId)
            except MTurkRequestError as e:
                k.write("ProcessNotifications: getHitStatus failed for HIT ID %s:\n%s\n%s\n" % 
                    (hitId, e.error_code, e.error_message))
                return
            except AssertionError:
                k.write("ProcessNotifications: Bad getHitStatus status for HIT ID %s:\n" % hitId)
                return
            if hitStatus == 'Reviewable':
                nonFinalAssignCount = int(mtma.querySingleValue("""select count(*) from assignment_data
                    where hit_id = '%s' and status in ('%s','%s')""" %
                    (hitId, MTurkMappingAfrica.HITPending, MTurkMappingAfrica.HITAccepted)))
                if nonFinalAssignCount == 0:
                    try:
                        mtma.disposeHit(hitId)
                    except MTurkRequestError as e:
                        k.write("ProcessNotifications: disposeHit failed for HIT ID %s:\n%s\n%s\n" % 
                            (hitId, e.error_code, e.error_message))
                        return
                    except AssertionError:
                        k.write("ProcessNotifications: Bad disposeHit status for HIT ID %s:\n" % hitId)
                        return
                    # Record the HIT deletion time.
                    mtma.cur.execute("""update hit_data set delete_time = '%s' where hit_id = '%s'""" % 
                            (eventTime, hitId))
                    mtma.dbcon.commit()
                    k.write("ProcessNotifications: hit has no remaining assignments and has been deleted\n")
                else:
                    k.write("ProcessNotifications: hit still has remaining Mturk or pending assignments and cannot be deleted\n")
            else:
                k.write("ProcessNotifications: hit still has remaining Mturk or pending assignments and cannot be deleted\n")

    # Delete HIT if it expires with no assignments in the Pending or Accepted state.
    def HITExpired(self, mtma, k, hitId, assignmentId, eventTime):
        # Record the HIT expiration status.
        mtma.cur.execute("""update hit_data set hit_expired = True where hit_id = '%s'""" % 
                hitId)
        k.write("ProcessNotifications: hit has been marked as expired\n")

        # Delete the HIT if all assignments have been submitted and have a final status
        # (i.e., there are no assignments in pending or accepted status).
        try:
            hitStatus = mtma.getHitStatus(hitId)
        except MTurkRequestError as e:
            k.write("ProcessNotifications: getHitStatus failed for HIT ID %s:\n%s\n%s\n" % 
                (hitId, e.error_code, e.error_message))
            return
        except AssertionError:
            k.write("ProcessNotifications: Bad getHitStatus status for HIT ID %s:\n" % hitId)
            return
        if hitStatus == 'Reviewable':
            nonFinalAssignCount = int(mtma.querySingleValue("""select count(*) from assignment_data
                where hit_id = '%s' and status in ('%s','%s')""" %
                (hitId, MTurkMappingAfrica.HITPending, MTurkMappingAfrica.HITAccepted)))
            if nonFinalAssignCount == 0:
                try:
                    mtma.disposeHit(hitId)
                except MTurkRequestError as e:
                    k.write("ProcessNotifications: disposeHit failed for HIT ID %s:\n%s\n%s\n" % 
                        (hitId, e.error_code, e.error_message))
                    return
                except AssertionError:
                    k.write("ProcessNotifications: Bad disposeHit status for HIT ID %s:\n" % hitId)
                    return
                # Record the HIT deletion time.
                mtma.cur.execute("""update hit_data set delete_time = '%s' where hit_id = '%s'""" % 
                        (eventTime, hitId))
                mtma.dbcon.commit()
                k.write("ProcessNotifications: hit has no remaining assignments and has been deleted\n")
            else:
                k.write("ProcessNotifications: hit still has remaining Mturk or pending assignments and cannot be deleted\n")
        else:
            k.write("ProcessNotifications: hit still has remaining Mturk or pending assignments and cannot be deleted\n")

    def HITReviewable(self, mtma, k, hitId, assignmentId, eventTime):
        pass
