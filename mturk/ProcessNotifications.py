import subprocess
from psycopg2.extensions import adapt
from boto.mturk.notification import NotificationMessage, NotificationEmail, Event
from boto.mturk.connection import MTurkRequestError
from MTurkMappingAfrica import MTurkMappingAfrica, aws_secret_access_key

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

    def __init__(self, notifMsg):
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
        mtma = MTurkMappingAfrica()
        logFilePath = mtma.getConfiguration('ProjectRoot') + "/log"
        k = open(logFilePath + "/notifications.log", "a")

        numMsgs = len(notifMsg.events)
        k.write("getnotifications: received %d event(s):\n" % numMsgs)
        
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
            k.write("getnotifications: event_type = %s\n" % eventType)
            k.write("getnotifications: event_time_str = %s\n" % eventTime)
            k.write("getnotifications: hit_id = %s\n" % hitId)
            if len(assignmentId) > 0:
                k.write("getnotifications: assignmentId = %s\n" % assignmentId)

            # Process the event type.
            if eventType in eventTypes:
                eventTypes[eventType](mtma, k, hitId, assignmentId, eventTime)
                mtma.dbcon.commit()
        
        k.close()
        mtma.close()

    def AssignmentAbandoned(self, mtma, k, hitId, assignmentId, eventTime):
        # Mark the assignment as abandoned.
        mtma.cur.execute("""update assignment_data set completion_time = '%s', status = '%s'
            where assignment_id = '%s'""" % (eventTime, MTurkMappingAfrica.HITAbandoned, assignmentId))
        k.write("getnotifications: assignment has been marked as abandoned\n")

    def AssignmentReturned(self, mtma, k, hitId, assignmentId, eventTime):
        # Mark the assignment as returned.
        mtma.cur.execute("""update assignment_data set completion_time = '%s', status = '%s'
            where assignment_id = '%s'""" % (eventTime, MTurkMappingAfrica.HITReturned, assignmentId))
        k.write("getnotifications: assignment has been marked as returned\n")

    def AssignmentSubmitted(self, mtma, k, hitId, assignmentId, eventTime):
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

        # Get the KML type for this assignment.
        mtma.cur.execute("select kml_type from kml_data inner join hit_data using (name) where hit_id = '%s'" % hitId)
        kmlType = mtma.cur.fetchone()[0]

        # If QAQC HIT, then score it and post-process any preceding non-QAQC HITs for this worker.
        if kmlType == MTurkMappingAfrica.KmlQAQC:
            self.QAQCSubmission(mtma, k, hitId, assignmentId, eventTime, workerId, submitTime, params, hitStatus)
        # Else, if non-QAQC HIT, then mark it as pending post-processing.
        elif kmlType == MTurkMappingAfrica.KmlNormal:
            self.NormalSubmission(mtma, k, assignmentId, workerId, submitTime, params)

    def QAQCSubmission(self, mtma, k, hitId, assignmentId, eventTime, workerId, submitTime, params, hitStatus):
        # Get the kml name, save status, and worker comment.
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
        assignmentStatus = None
        if results_saved:
            projectRoot = mtma.getConfiguration('ProjectRoot')
            scoreString = subprocess.Popen(["Rscript", "%s/R/KMLAccuracyCheck.R" % projectRoot, kmlName, assignmentId], 
                stdout=subprocess.PIPE).communicate()[0]
            try:
                score = float(scoreString)
            # Pay the worker if we couldn't score his work properly.
            except:
                assignmentStatus = MTurkMappingAfrica.HITUnscored
                score = 1.          # Give worker the benefit of the doubt
                k.write("getnotifications: Invalid value '%s' returned from R scoring script; assigning a score of %.2f\n" % 
                    (scoreString, score))
        # Pay the worker if we couldn't save his work.
        else:
            assignmentStatus = MTurkMappingAfrica.HITUnsaved
            score = 1.              # Give worker the benefit of the doubt
            k.write("getnotifications: Unable to save worker's results; assigning a score of %.2f\n" %
                score)
        hitAcceptThreshold = float(mtma.getConfiguration('HitAcceptThreshold'))

        # If the worker's results could not be saved or scored, or if their score meets 
        # the acceptance threshold, notify worker that his HIT was accepted.
        if assignmentStatus != None or score >= hitAcceptThreshold:
            try:
                mtma.approveAssignment(assignmentId)
            except MTurkRequestError as e:
                k.write("getnotifications: approveAssignment failed for assignment ID %s:\n%s\n%s\n" % 
                    (assignmentId, e.error_code, e.error_message))
                return
            except AssertionError:
                k.write("getnotifications: Bad approveAssignment status for assignment ID %s:\n" % assignmentId)
                return
            assignmentStatus = MTurkMappingAfrica.HITApproved
        # Only if the worker's results were saved and scored, and their score did not meet 
        # the threshold do we reject the HIT.
        else:
            try:
                # TODO: *** Put reject feedback into configuration table, or have more sophisticated code
                #       to guide what the text should say: e.g., were they close or far? Use different feedback. ***
                mtma.rejectAssignment(assignmentId, mtma.getConfiguration('HitRejection_Description'))
            except MTurkRequestError as e:
                k.write("getnotifications: rejectAssignment failed for assignment ID %s:\n%s\n%s\n" % 
                    (assignmentId, e.error_code, e.error_message))
                return
            except AssertionError:
                k.write("getnotifications: Bad rejectAssignment status for assignment ID %s:\n" % assignmentId)
                return
            assignmentStatus = MTurkMappingAfrica.HITRejected

        # Record the HIT submission time and status, and user comment.
        mtma.cur.execute("""update assignment_data set completion_time = '%s', status = '%s', 
            comment = %s, score = '%s' where assignment_id = '%s'""" % 
            (submitTime, assignmentStatus, adapt(comment), score, assignmentId))
        k.write("getnotifications: assignment has been marked as %s: %.2f/%.2f\n" % 
            (assignmentStatus.lower(), score, hitAcceptThreshold))

        # TODO: *** To determine bonus or disqualification, compute cumulative score.
        #           Note that count of QAQC HITs submitted must be at least 3 ***
        #mtma.cur.execute("""select count(score), avg(score) from assignment_data 
        #    where status = '%s' and worker_id = '%s'""" %
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

        # Post-process any pending non-QAQC HITs for this worker.
        self.NormalPostProcessing(mtma, k, eventTime, workerId, score, hitAcceptThreshold, assignmentStatus)

    def NormalSubmission(self, mtma, k, assignmentId, workerId, submitTime, params):
        # Get the save status and worker comment.
        try:
            results_saved = (params['save_status'] == 'true')
            comment = params['comment'].strip()
        except:
            k.write("getnotifications: Missing getAssignment parameter(s) for assignment ID %s:\n" % assignmentId)
            return
        if len(comment) > 2048:
            comment = comment[:2048]

        # Set the assignment status per the save status.
        if results_saved:
            assignmentStatus = MTurkMappingAfrica.HITPending
        else:
            assignmentStatus = MTurkMappingAfrica.HITPendingUnsaved

        # Record the HIT submission time and status, and user comment.
        mtma.cur.execute("""update assignment_data set completion_time = '%s', status = '%s', 
            comment = %s where assignment_id = '%s'""" % 
            (submitTime, assignmentStatus, adapt(comment), assignmentId))
        k.write("getnotifications: non-QAQC assignment has been marked as %s" % 
            assignmentStatus.lower())

    def NormalPostProcessing(self, mtma, k, eventTime, workerId, score, hitAcceptThreshold, qaqcAssignmentStatus):
        # Get the the key data for this worker's pending non-QAQC submitted HITs.
        mtma.cur.execute("""select gid, assignment_id, hit_id, status from kml_data
            inner join hit_data using (name) inner join assignment_data using(hit_id)
            where worker_id = %s and status in %s order by gid""", 
            (workerId, (MTurkMappingAfrica.HITPending, MTurkMappingAfrica.HITPendingUnsaved),))
        assignments = mtma.cur.fetchall()
        k.write("getnotifications: Checking for pending non-QAQC assignments: found %d\n" % len(assignments))

        # If none since the last QAQC HIT, then there's nothing to do.
        if len(assignments) == 0:
            return

        # Save the oldest gid for use below.
        oldestGid = assignments[0][0]

        # Loop on all the pending non-QAQC HITs for this worker, and finalize their status.
        for assignment in assignments:
            assignmentId = assignment[1]
            hitId = assignment[2]
            assignmentStatus = assignment[3]

            k.write("getnotifications: Post-processing assignmentId = %s\n" % assignmentId)

            # Get the HIT status we need.
            try:
                dummy, dummy, dummy, hitStatus = mtma.getAssignment(assignmentId)
            except MTurkRequestError as e:
                k.write("getnotifications: getAssignment failed for assignment ID %s:\n%s\n%s\n" % 
                    (assignmentId, e.error_code, e.error_message))
                return
            except AssertionError:
                k.write("getnotifications: Bad getAssignment status for assignment ID %s:\n" % assignmentId)
                return

            # If the worker's results could not be saved, or the following QAQC could not be saved or scored, 
            # or the following QAQC was approved, notify worker that his HIT was accepted.
            if qaqcAssignmentStatus != MTurkMappingAfrica.HITRejected:
                try:
                    mtma.approveAssignment(assignmentId)
                except MTurkRequestError as e:
                    k.write("getnotifications: approveAssignment failed for assignment ID %s:\n%s\n%s\n" %
                        (assignmentId, e.error_code, e.error_message))
                    return
                except AssertionError:
                    k.write("getnotifications: Bad approveAssignment status for assignment ID %s:\n" % assignmentId)
                    return
                mturkAssignmentStatus = MTurkMappingAfrica.HITApproved
            # Only if the worker's following QAQC results were rejected do we reject the current non-QAQC HIT.
            else:
                try:
                    # TODO: *** Put reject feedback into configuration table, or have more sophisticated code
                    #       to guide what the text should say: e.g., were they close or far? Use different feedback. ***
                    mtma.rejectAssignment(assignmentId, mtma.getConfiguration('HitRejection_Description'))
                except MTurkRequestError as e:
                    k.write("getnotifications: rejectAssignment failed for assignment ID %s:\n%s\n%s\n" %
                        (assignmentId, e.error_code, e.error_message))
                    return
                except AssertionError:
                    k.write("getnotifications: Bad rejectAssignment status for assignment ID %s:\n" % assignmentId)
                    return
                mturkAssignmentStatus = MTurkMappingAfrica.HITRejected

            # Figure out what the final non-QAQC assignment status should be.
            if assignmentStatus == MTurkMappingAfrica.HITPendingUnsaved:
                dbAssignmentStatus = MTurkMappingAfrica.HITUnsaved
            elif qaqcAssignmentStatus == MTurkMappingAfrica.HITUnsaved:
                dbAssignmentStatus = MTurkMappingAfrica.HITUnsavedQAQC
            elif qaqcAssignmentStatus == MTurkMappingAfrica.HITUnscored:
                dbAssignmentStatus = MTurkMappingAfrica.HITUnscoredQAQC
            # Else, normal approved or rejected status.
            else:
                dbAssignmentStatus = qaqcAssignmentStatus

            # Record the HIT submission time and status, and user comment.
            mtma.cur.execute("""update assignment_data set status = '%s',
                score = '%s' where assignment_id = '%s'""" %
                (dbAssignmentStatus, score, assignmentId))
            k.write("getnotifications: assignment has been %s, but marked in DB as %s: %.2f/%.2f\n" %
                (mturkAssignmentStatus.lower(), dbAssignmentStatus.lower(), score, hitAcceptThreshold))

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

    # Delete HIT if it expires with outstanding assignments left unsubmitted.
    def HITExpired(self, mtma, k, hitId, assignmentId, eventTime):
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
        mtma.cur.execute("""update hit_data set delete_time = '%s', hit_expired = True where hit_id = '%s'""" % 
            (eventTime, hitId))
        k.write("getnotifications: hit has expired and has been deleted\n")

    def HITReviewable(self, mtma, k, hitId, assignmentId, eventTime):
        pass
