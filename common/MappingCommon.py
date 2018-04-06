import os
import subprocess
import pwd
from datetime import datetime
from dateutil import tz
import psycopg2
from psycopg2.extensions import adapt
import collections
from decimal import Decimal
from github import Github
from lock import lock

# Key connection parameters.
db_production_name = 'Africa'
db_sandbox_name = 'AfricaSandbox'
db_user = '***REMOVED***'
db_password = '***REMOVED***'
# GitHub user maphelp's token
github_token = '5f3031c885d40fd1fd54d914f0331dc8f4e4574b'
github_repo = 'agroimpacts/mapperAL'

class MappingCommon(object):

    # HIT assignment_data.status constants

    # QAQC and non-QAQC HIT constants
    HITAssigned = 'Assigned'                    # HIT assigned to worker
    HITAbandoned = 'Abandoned'                  # HIT abandoned by worker
    HITReturned = 'Returned'                    # HIT returned by worker
    HITApproved = 'Approved'                    # HIT submitted and approved:
                                                # a) QAQC had high score
                                                # b) non-QAQC had high trust level
    # QAQC constants
    HITRejected = 'Rejected'                    # HIT submitted and rejected
    HITUnscored = 'Unscored'                    # HIT not scorable, hence approved
    HITReversed = 'Reversed'                    # HIT was originally rejected and then reversed.

    # non-QAQC constants (HIT always approved)
    HITPending = 'Pending'                      # Awaiting enough trust history to calculate trust level
    HITUntrusted = 'Untrusted'                  # Insufficiently high trust level
                                                # (non-QAQC KML reused in this case)

    # KML kml_data.kml_type constants
    KmlNormal = 'N'                             # Normal (non-QAQC) KML
    KmlQAQC = 'Q'                               # QAQC KML
    KmlFQAQC = 'F'                              # FQAQC KML
    KmlTraining = 'I'                           # Initial training KML

    # HIT assignment_history.event_type constants
    EVTApprovedAssignment = 'Approved Assignment' # Assignment was approved
    EVTRejectedAssignment = 'Rejected Assignment' # Assignment was rejected
    EVTQualityBonus = 'Quality Bonus'           # Worker rewarded for high quality
    EVTTrainingBonus = 'Training Bonus'         # Worker rewarded for completing qualification test

    # Defined constants for GitHub issues
    AlertIssue = 'IssueAlertLabel'
    GeneralInquiryIssue = 'IssueGeneralInquiryLabel'
    WorkerInquiryIssue = 'IssueWorkerInquiryLabel'
    IssueTags = [(AlertIssue, 'IssueAlertAssignee'), 
                    (GeneralInquiryIssue, 'IssueGeneralInquiryAssignee'), 
                    (WorkerInquiryIssue, 'IssueWorkerInquiryAssignee')]
    
    # Database column name constants
    ScoresCol = 'scores'
    ReturnsCol = 'returns'

    # Serialization lock file name
    lockFile = 'serial_file.lck'

    def __init__(self, projectRoot=None):
        
        # Determine sandbox/mapper based on effective user name.
        self.euser = pwd.getpwuid(os.getuid()).pw_name
        if self.euser == 'mapper':
            self.mapper = True
            self.projectRoot = '/home/mapper/afmap'
        else:
            if projectRoot is None:
                if self.euser == 'sandbox':
                    self.mapper = False
                    self.projectRoot = '/home/sandbox/afmap'
                else:
                   raise Exception("Mapping server must run under sandbox or mapper user") 
            else:
                self.mapper = False
                self.projectRoot = projectRoot

        if self.mapper:
            self.db_name = db_production_name
        else:
            self.db_name = db_sandbox_name
        
        self.dbcon = psycopg2.connect("dbname=%s user=%s password=%s" % 
            (self.db_name, db_user, db_password))
        self.cur = self.dbcon.cursor()

        self.ghrepo = Github(github_token).get_repo(github_repo)

    def __del__(self):
        self.close()

    def close(self):
        self.dbcon.close()

    #
    # *** Utility Functions ***
    #

    # Retrieve a tunable parameter from the configuration table.
    def getConfiguration(self, key):
        self.cur.execute("select value from configuration where key = '%s'" % key)
        return self.cur.fetchone()[0]

    # Retrieve a runtime parameter from the system_data table.
    def getSystemData(self, key):
        self.cur.execute("select value from system_data where key = '%s'" % key)
        return self.cur.fetchone()[0]

    # Set a runtime parameter in the system_data table.
    def setSystemData(self, key, value):
        self.cur.execute("update system_data set value = '%s' where key = '%s'" % (value, key))
        self.dbcon.commit()

    # Obtain serialization lock to allow create_hit_daemon.py, cleanup_absent_worker.py, and 
    # individual ProcessNotifications.py threads to access Mturk and database records
    # without interfering with each other.
    def getSerializationLock(self):
        self.lock = lock('%s/common/%s' % (self.projectRoot, MappingCommon.lockFile))

    # Release serialization lock.
    def releaseSerializationLock(self):
        del self.lock

    # Request a single value from a single column of a table.
    # If there is no record that matches the select criteria, return None.
    def querySingleValue(self, sql):
        self.cur.execute(sql)
        try:
            return self.cur.fetchone()[0]
        except TypeError as e:
            if str(e).startswith("'NoneType'"):
                return None
            else:
                raise

    # Retrieve the KML type and its description for a  given KML name.
    def getKmlType(self, kmlName):
        self.cur.execute("select kml_type from kml_data where name = '%s'" % kmlName)
        kmlType = self.cur.fetchone()[0]
        if kmlType == MappingCommon.KmlQAQC:
            kmlTypeDescr = 'QAQC'
        elif kmlType == MappingCommon.KmlFQAQC:
            kmlTypeDescr = 'FQAQC'
        elif kmlType == MappingCommon.KmlNormal:
            kmlTypeDescr = 'non-QAQC'
        elif kmlType == MappingCommon.KmlTraining:
            kmlTypeDescr = 'training'
        return (kmlType, kmlTypeDescr)

    # Save and retrieve circular buffer into database.
    # NOTE: assumes that rightmost entry is most recent. 
    # Works well with collections.deque().
    # Store circular buffer array into specified column for specified worker.
    def putCB(self, array, dbField, workerId):
        self.cur.execute("update worker_data set %s=%s where worker_id = %s" % (dbField,'%s','%s'), (array,workerId,))
        self.dbcon.commit()

    # Retrieve circular buffer from specified column for specified worker.
    def getCB(self, dbField, workerId):
        self.cur.execute("select %s from worker_data where worker_id = %s" % (dbField,'%s'), (workerId,))
        return self.cur.fetchone()[0]

    # Add new value to circular buffer for scores.
    def pushScore(self, workerId, value):
        depth = int(self.getConfiguration('Quality_ScoreHistDepth'))
        scores = self.getCB(self.ScoresCol, workerId)
        if scores is None:
            scores = collections.deque(maxlen=depth)
        else:
            scores = collections.deque(scores,maxlen=depth)
        scores.append(value)
        self.putCB(list(scores), self.ScoresCol, workerId)

    # Add new return state to circular buffer for returns.
    # State must be True for returns and False for submissions.
    def pushReturn(self, assignmentId, state):
        # Get the worker ID for this assignment.
        self.cur.execute("select worker_id from assignment_data where assignment_id = '%s'" % assignmentId)
        workerId = self.cur.fetchone()[0]
        depth = int(self.getConfiguration('Quality_ReturnHistDepth'))
        returns = self.getCB(self.ReturnsCol, workerId)
        if returns is None:
            returns = collections.deque(maxlen=depth)
        else:
            returns = collections.deque(returns,maxlen=depth)
        if state:
            value = 1.0
        else:
            value = 0.0
        returns.append(value)
        self.putCB(list(returns), self.ReturnsCol, workerId)

    # Get moving average of scores saved. If number of scores saved is 
    # less than the required depth, return None.
    def getAvgScore(self, workerId):
        depth = int(self.getConfiguration('Quality_ScoreHistDepth'))
        scores = collections.deque(self.getCB(self.ScoresCol, workerId),maxlen=depth)
        if len(scores) < depth:
            return None
        return sum(scores)/depth

    # Get moving average of scores saved. If number of scores saved is 
    # less than the required depth, return None.
    def getReturnRate(self, workerId):
        depth = int(self.getConfiguration('Quality_ReturnHistDepth'))
        returns = collections.deque(self.getCB(self.ReturnsCol, workerId),maxlen=depth)
        if len(returns) < depth:
            return None
        return sum(returns)/depth

    # Calculate quality score.
    def getQualityScore(self, workerId):
        weight = float(self.getConfiguration('Quality_ReturnWeight'))
        avgScore = self.getAvgScore(workerId)
        if avgScore is None:
            return None
        returnRate = self.getReturnRate(workerId)
        if returnRate is None:
            return None
        qScore = avgScore - (returnRate * weight)
        return qScore

    # Return True if worker is trusted based on quality score.
    def isWorkerTrusted(self, workerId):
        qualityScore = self.getQualityScore(workerId)
        if qualityScore is None:
            return None
        trustThreshold = float(self.getConfiguration('HitN_TrustThreshold'))
        if qualityScore >= trustThreshold:
            return True
        else:
            return False

    # Create a GitHub issue, specifying its title, body, and one of three
    #     predefined labels: MappingCommon.AlertIssue, MappingCommon.GeneralInquiryIssue, or
    #     MappingCommon.WorkerInquiryIssue
    def createIssue(self, title=None, body=None, label=None):
        for llabel, assignee in MappingCommon.IssueTags:
            if label == llabel:
                break
        else:
            assert False
        issueLabel = self.getConfiguration(llabel)
        issueAssignee = self.getConfiguration(assignee)
        self.ghrepo.create_issue(title=title, body=body, labels=[issueLabel], assignee=issueAssignee)
    
    # Create an Alert-type GitHub issue.
    def createAlertIssue(self, title=None, body=None):
        self.createIssue(title, body, MappingCommon.AlertIssue)

    #
    # *** HIT-Related Functions ***
    #

    # Retrieve all HITs created by the createHit() function.
    def getAllHits(self):
        self.cur.execute("""
            select hit_id, name, kml_type, max_assignments, reward
            from hit_data
            inner join kml_data using (name)
            where delete_time is null
            """)
        hits = {}
        for hit in self.cur.fetchall():
            assignmentsCompleted = 0
            assignmentsPending = 0
            for asgmtId, asgmt in self.getAssignments(hit[0]).iteritems():
                if asgmt['status'] not in (MappingCommon.HITAbandoned, MappingCommon.HITReturned):
                    if asgmt['status'] in (MappingCommon.HITAssigned, MappingCommon.HITPending):
                        assignmentsPending += 1
                    else:
                        assignmentsCompleted += 1
            hits[hit[0]] = {'kmlName': hit[1], 'kmlType': hit[2], 'maxAssignments': hit[3], 
                    'reward': hit[4], 'assignmentsCompleted': assignmentsCompleted, 
                    'assignmentsPending': assignmentsPending}
        return hits

    # Retrieve all assignments for the specified HIT ID.
    def getAssignments(self, hitId):
        self.cur.execute("""
            select assignment_id, worker_id, completion_time, status
            from assignment_data
            where hit_id = '%s'
            """ % hitId)
        assignments = {}
        for asgmt in self.cur.fetchall():
            assignments[asgmt[0]] = {'workerId': asgmt[1], 'completionTime': asgmt[2], 'status': asgmt[3]}
        return assignments
        
    # Create a HIT for the specified KML ID.
    def createHit(self, kml=None, fwts=1, maxAssignments=1):
        self.fwts = int(fwts)
        duration = self.getConfiguration('Hit_Duration')
        reward = int(self.getConfiguration('Hit_Reward'))
        # Add the difficulty reward increment if KML's fwts > 1.
        self.hitRewardIncrement = Decimal(self.getConfiguration('Hit_RewardIncrement'))
        self.hitRewardIncrement2 = Decimal(self.getConfiguration('Hit_RewardIncrement2'))
        if self.fwts > 1:
            reward += int(round(self.hitRewardIncrement * (self.fwts - 1) + \
                self.hitRewardIncrement2 * (self.fwts - 1)**2, 2) * 100)

        now = str(datetime.today())
        self.cur.execute("""INSERT INTO hit_data 
                (name, create_time, max_assignments, duration, reward) 
                values ('%s', '%s', '%s', '%s', '%s')
                RETURNING hit_id""" % 
                (kml, now, maxAssignments, duration, reward))
        hitId = self.cur.fetchone()[0]
        self.dbcon.commit()
        return hitId

    # Delete a HIT if all assignments have been submitted and have a final status
    # (i.e., there are no assignments in pending or accepted status).
    def deleteFinalizedHit(self, hitId, submitTime):
        # Count if there are any available assignments left for this HIT.
        nonFinalAssignCount = self.querySingleValue("""SELECT
                (SELECT max_assignments FROM hit_data WHERE hit_id = '%s') -
                (SELECT count(*) FROM assignment_data WHERE hit_id ='%s' AND
                        status NOT IN ('%s', '%s'))""" %
                (hitId, hitId, MappingCommon.HITAssigned, MappingCommon.HITPending))
        try:
            nonFinalAssignCount = int(nonFinalAssignCount)
        except:
            # If a problem with the return from this query, don't delete.
            nonFinalAssignCount = -1
            self.createAlertIssue("deleteFinalizedHit problem", 
                    "Invalid value returned from nonFinalAssignCount query for: HIT ID %s\n" % hitId)
        if nonFinalAssignCount == 0:
            # Record the HIT deletion time.
            self.cur.execute("""UPDATE hit_data SET delete_time = '%s' WHERE hit_id = '%s'""" % (submitTime, hitId))
            self.dbcon.commit()
            return True
        else:
            return False

    #
    # *** Accuracy-Related Functions ***
    #

    # Score worker mapping of an 'I' or 'Q' KML.
    # Return floating point score (0.0-1.0), or None if could not be scored.
    def kmlAccuracyCheck(self, kmlType, kmlName, assignmentId, tryNum=None):
        if kmlType == MappingCommon.KmlTraining:
            scoreString = subprocess.Popen(["Rscript", "%s/spatial/R/KMLAccuracyCheck.R" % self.projectRoot, "tr", kmlName, assignmentId, str(tryNum)],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]
        elif kmlType == MappingCommon.KmlQAQC:
            scoreString = subprocess.Popen(["Rscript", "%s/spatial/R/KMLAccuracyCheck.R" % self.projectRoot, "qa", kmlName, assignmentId],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]
        else:
            assert False
        try:
            score = float(scoreString)
            return score, scoreString
        except:
            return None, scoreString

    # Save all the worker's drawm maps.
    # Note: if tryNum is zero, then this is not a training case.
    def saveWorkerMaps(self, k, kmlData, workerId, assignmentId, tryNum=0):
        # Loop over every Polygon, and store its name and data in PostGIS DB.
        numGeom = 0
        numFail = 0
        errorString = ''
        k.write("saveWorkerMaps: kmlData = %s\n" % kmlData)
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
                geomValue = self.querySingleValue("SELECT ST_IsValidDetail(ST_GeomFromKML('%s'))" % geometry)
                # ST_IsValidDetail returns with format '(t/f,"reason",geometry)'
                geomValid, geomReason, dummy = geomValue[1:-1].split(',')
                geomValid = (geomValid == 't')
                if geomValid:
                    k.write("saveWorkerMaps: Shape is a valid %s\n" % geomType)
                else:
                    k.write("saveWorkerMaps: Shape is an invalid %s due to '%s'\n" % (geomType, geomReason))
                if tryNum > 0:
                    self.cur.execute("""INSERT INTO qual_user_maps (name, geom, completion_time, assignment_id, try, geom_clean)
                            SELECT %s AS name, ST_GeomFromKML(%s) AS geom, %s AS datetime, %s as assignment_id, %s as try,
                            ST_MakeValid(ST_GeomFromKML(%s)) as geom_clean""",
                            (geomName, geometry, now, assignmentId, tryNum, geometry))
                else:
                    self.cur.execute("""INSERT INTO user_maps (name, geom, completion_time, assignment_id, geom_clean)
                            SELECT %s AS name, ST_GeomFromKML(%s) AS geom, %s AS datetime, %s as assignment_id, 
                            ST_MakeValid(ST_GeomFromKML(%s)) as geom_clean""",
                            (geomName, geometry, now, assignmentId, geometry))
                self.dbcon.commit()
            except psycopg2.InternalError as e:
                numFail += 1
                self.dbcon.rollback()
                errorString += "\nKML mapping %s raised an internal datatase exception: %s\n%s%s\n" % (geomName, e.pgcode, e.pgerror, cgi.escape(geometry))
                k.write("saveWorkerMaps: Internal database error %s\n%s" % (e.pgcode, e.pgerror))
                k.write("saveWorkerMaps: Ignoring this mapping and continuing\n")
            except psycopg2.Error as e:
                numFail += 1
                self.dbcon.rollback()
                errorString += "\nKML mapping %s raised a general datatase exception: %s\n%s%s\n" % (geomName, e.pgcode, e.pgerror, cgi.escape(geometry))
                k.write("saveWorkerMaps: General database error %s\n%s" % (e.pgcode, e.pgerror))
                k.write("saveWorkerMaps: Ignoring this mapping and continuing\n")

        # If we have at least one invalid mapping.
        if numFail > 0:
            k.write("saveWorkerMaps: NOTE: %s mapping(s) out of %s were invalid\n" % (numFail, numGeom))
            if tryNum > 0:
                self.createAlertIssue("Database geometry problem",
                    "Worker ID = %s\nAssignment ID = %s; try %s\nNOTE: %s mapping(s) out of %s were invalid\n%s" %
                    (workerId, assignmentId, tryNum, numFail, numGeom, errorString))
            else:
                self.createAlertIssue("Database geometry problem",
                        "Worker ID = %s\nAssignment ID = %s\nNOTE: %s mapping(s) out of %s were invalid\n%s" % 
                        (workerId, assignmentId, numFail, numGeom, errorString))

        # If we have at least one valid mapping, return success.
        if numGeom > numFail:
            return True
        else:
            return False

    # Do post-processing for a training worker's submitted assignment.
    def trainingAssignmentSubmitted(self, k, hitId, assignmentId, tryNum, workerId, submitTime, kmlName, kmlType):
        # Compute the worker's score on this KML.
        score, scoreString = self.kmlAccuracyCheck(MappingCommon.KmlTraining, kmlName, assignmentId, tryNum)
        # Reward the worker if we couldn't score his work properly.
        if score is None:
            assignmentStatus = MappingCommon.HITUnscored
            score = self.getQualityScore(workerId)
            if score is None:
                score = 1.          # Give new worker the max score
            k.write("qualification: Invalid value returned from R scoring script for:\nKML %s, worker ID %s, assignment ID %s, try %s; assigning a score of %.2f\nReturned value:\n%s\n" %
                    (kmlName, workerId, assignmentId, tryNum, score, scoreString))
            self.createAlertIssue("KMLAccuracyCheck problem",
                    "Invalid value returned from R scoring script for:\nKML %s, worker ID %s, assignment ID %s, try %s; assigning a score of %.2f\nReturned value:\n%s\n" %
                    (kmlName, workerId, assignmentId, tryNum, score, scoreString))

        # See if score exceeds the Accept threshold
        hitAcceptThreshold = float(self.getConfiguration('HitI_AcceptThreshold'))
        k.write("qualification: training assignment has been scored as: %.2f/%.2f\n" %
                (score, hitAcceptThreshold))

        if assignmentStatus is None:
            if score >= hitAcceptThreshold:
                assignmentStatus = MappingCommon.HITApproved
                approved = True
            else:
                assignmentStatus = MappingCommon.HITRejected
                approved = False
        return approved

        # Record the assignment submission time and score (unless results were unsaved).
        self.cur.execute("""update qual_assignment_data set completion_time = '%s', status = '%s',
            score = '%s' where assignment_id = '%s'""" %
            (now, assignmentStatus, score, assignmentId))
        self.dbcon.commit()

    # Do all post-processing for a worker's submitted assignment.
    def assignmentSubmitted(self, k, hitId, assignmentId, workerId, submitTime, kmlName, kmlType, comment):
        # Record the submission in order to compute a return rate.
        self.pushReturn(assignmentId, False)

        # If QAQC HIT, then score it and post-process any preceding FQAQC or non-QAQC HITs for this worker.
        if kmlType == MappingCommon.KmlQAQC:
            self.qaqcSubmission(k, hitId, assignmentId, workerId, submitTime, kmlName, kmlType, comment)
        # Else, if FQAQC HIT or non-QAQC HIT, then post-process it or mark it as pending post-processing.
        elif kmlType == MappingCommon.KmlNormal or kmlType == MappingCommon.KmlFQAQC:
            self.normalSubmission(k, hitId, assignmentId, workerId, submitTime, kmlName, kmlType, comment)

    def qaqcSubmission(self, k, hitId, assignmentId, workerId, submitTime, kmlName, kmlType, comment):
        # Compute the worker's score on this KML.
        # NOTE: We used to call mapFix before calling KMLAccuracyCheck.
        score, scoreString = self.kmlAccuracyCheck(kmlType, kmlName, assignmentId)

        # Reward the worker if we couldn't score his work properly.
        if score is None:
            assignmentStatus = MappingCommon.HITUnscored
            score = self.getQualityScore(workerId)
            if score is None:
                score = 1.          # Give new worker the max score
            k.write("assignment: Invalid value returned from R scoring script for:\nQAQC KML %s, HIT ID %s, assignment ID %s, worker ID %s; assigning a score of %.2f\nReturned value:\n%s\n" % 
                    (kmlName, hitId, assignmentId, workerId, score, scoreString)) 
            self.createAlertIssue("KMLAccuracyCheck problem", 
                    "Invalid value returned from R scoring script for:\nQAQC KML %s, HIT ID %s, assignment ID %s, worker ID %s; assigning a score of %.2f\nReturned value:\n%s\n" %
                    (kmlName, hitId, assignmentId, workerId, score, scoreString))

        # Record score (actual or assumed) to compute moving average.
        self.pushScore(workerId, score)

        # Check if Mapping Africa qualification should be revoked
        # (needs to be done for both the approved and rejection cases because a worker may
        #  earn a quality score for the first time at the revocation level)
        if self.revokeQualificationIfUnqualifed(workerId, submitTime):
            k.write("assignment: Mapping Africa Qualification revoked from worker %s\n" % workerId)

        hitAcceptThreshold = float(self.getConfiguration('HitQ_AcceptThreshold'))
        hitNoWarningThreshold = float(self.getConfiguration('HitQ_NoWarningThreshold'))

        # If the worker's results could not be scored, or if their score meets 
        # the acceptance threshold, notify worker that his HIT was accepted.
        if assignmentStatus is not None or score >= hitAcceptThreshold:
            # if score was above the no-warning threshold, then don't include a warning.
            warning = False
            if score < hitNoWarningThreshold:
                warning = True
            self.approveAssignment(workerId, assignmentId, submitTime, warning)
            if assignmentStatus is None:
                assignmentStatus = MappingCommon.HITApproved

            # Also, check if the worker merits a quality bonus for approved assignment.
            bonusStatus = self.payBonusIfQualified(workerId)
            if bonusStatus > 0:
                k.write("assignment: Accuracy bonus level %s paid to worker %s\n" % (bonusStatus, workerId))

        # Only if the worker's results were saved and scored, and their score did not meet 
        # the threshold do we reject the HIT.
        else:
            self.rejectAssignment(workerId, assignmentId, submitTime)
            assignmentStatus = MappingCommon.HITRejected

        # Record the assignment submission time and status, user comment, and score.
        self.cur.execute("""UPDATE assignment_data SET completion_time = '%s', status = '%s', 
            comment = %s, score = '%s' WHERE assignment_id = '%s'""" % 
            (submitTime, assignmentStatus, adapt(comment), score, assignmentId))
        self.dbcon.commit()
        k.write("assignment: QAQC assignment has been marked in DB as %s: %.2f/%.2f/%.2f\n" % 
            (assignmentStatus.lower(), score, hitAcceptThreshold, hitNoWarningThreshold))

        # Delete the HIT if all assignments have been submitted and have a final status
        # (i.e., there are no assignments in pending or accepted status).
        if self.deleteFinalizedHit(hitId, submitTime):
            k.write("assignment: QAQC hit has no remaining assignments and has been deleted\n")
        else:
            k.write("assignment: QAQC hit still has remaining accepted or pending assignments and cannot be deleted\n")

        # Post-process any pending FQAQC or non-QAQC HITs for this worker.
        self.NormalPostProcessing(k, workerId, submitTime)

    def normalSubmission(self, k, hitId, assignmentId, workerId, submitTime, kmlName, kmlType, comment):
        workerTrusted = self.isWorkerTrusted(workerId)
        if workerTrusted is None:
            # If not enough history, mark assignment as pending in order to save for post-processing.
            assignmentStatus = MappingCommon.HITPending
        elif workerTrusted:
            assignmentStatus = MappingCommon.HITApproved
            # Since results are trusted, mark this KML as mapped.
            self.cur.execute("UPDATE kml_data SET mapped_count = mapped_count + 1 WHERE name = '%s'" % kmlName)
            k.write("assignment: incremented mapped count by trusted worker for %s KML %s\n" % (kmlType, kmlName))
        else:
            assignmentStatus = MappingCommon.HITUntrusted

        # In all cases, notify worker that his HIT was accepted.
        self.approveAssignment(workerId, assignmentId, submitTime)
        k.write("assignment: FQAQC or non-QAQC assignment has been approved and marked in DB as %s\n" % 
            assignmentStatus.lower())

        # Record the assignment submission time and status, and user comment.
        self.cur.execute("""UPDATE assignment_data SET completion_time = '%s', status = '%s', 
            comment = %s WHERE assignment_id = '%s'""" % 
            (submitTime, assignmentStatus, adapt(comment), assignmentId))
        self.dbcon.commit()

        # Delete the HIT if all assignments have been submitted and have a final status
        # (i.e., there are no assignments in pending or accepted status).
        if self.deleteFinalizedHit(hitId, submitTime):
            k.write("assignment: hit has no remaining assignments and has been deleted\n")
        else:
            k.write("assignment: hit still has remaining accepted or pending assignments and cannot be deleted\n")

    def NormalPostProcessing(self, k, workerId, submitTime):
        # Determine this worker's trust level.
        workerTrusted = self.isWorkerTrusted(workerId)
        if workerTrusted is None:
            k.write("assignment: Worker %s has insufficient history for evaluating FQAQC or non-QAQC HITs\n" %
                    workerId)
            return

        # Get the the key data for this worker's pending FQAQC or non-QAQC submitted HITs.
        self.cur.execute("""select name, assignment_id, hit_id
            from assignment_data inner join hit_data using (hit_id)
            where worker_id = %s and status = %s order by completion_time""", 
            (workerId, MappingCommon.HITPending,))
        assignments = self.cur.fetchall()

        # If none then there's nothing to do.
        if len(assignments) == 0:
            return

        k.write("assignment: Checking for pending FQAQC or non-QAQC assignments: found %d\n" % len(assignments))

        # Loop on all the pending FQAQC or non-QAQC HITs for this worker, and finalize their status.
        for assignment in assignments:
            kmlName = assignment[0]
            assignmentId = assignment[1]
            hitId = assignment[2]

            k.write("assignment: Post-processing assignmentId = %s\n" % assignmentId)

            # If the worker's results are reliable, we will mark the HIT as approved.
            if workerTrusted:
                assignmentStatus = MappingCommon.HITApproved

                # Since results trusted, mark this KML as mapped.
                self.cur.execute("update kml_data set mapped_count = mapped_count + 1 where name = '%s'" % kmlName)
                k.write("assignment: incremented mapped count by trusted worker for KML %s\n" % kmlName)
            else:
                assignmentStatus = MappingCommon.HITUntrusted

            # Record the final FQAQC or non-QAQC HIT status.
            self.cur.execute("""update assignment_data set status = '%s' where assignment_id = '%s'""" %
                (assignmentStatus, assignmentId))
            self.dbcon.commit()
            k.write("assignment: FQAQC or non-QAQC assignment marked in DB as %s\n" %
                assignmentStatus.lower())

            # Delete the HIT if all assignments have been submitted and have a final status
            # (i.e., there are no assignments in pending or accepted status).
            try:
                hitStatus = self.getHitStatus(hitId)
            except MTurkRequestError as e:
                k.write("assignment: getHitStatus failed for HIT ID %s:\n%s\n%s\n" % 
                    (hitId, e.error_code, e.error_message))
                return
            except AssertionError:
                k.write("assignment: Bad getHitStatus status for HIT ID %s:\n" % hitId)
                return
            if hitStatus == 'Reviewable':
                nonFinalAssignCount = int(self.querySingleValue("""select count(*) from assignment_data
                    where hit_id = '%s' and status in ('%s','%s')""" %
                    (hitId, MappingCommon.HITPending, MappingCommon.HITAssigned)))
                if nonFinalAssignCount == 0:
                    try:
                        self.disposeHit(hitId)
                    except MTurkRequestError as e:
                        k.write("assignment: disposeHit failed for HIT ID %s:\n%s\n%s\n" % 
                            (hitId, e.error_code, e.error_message))
                        return
                    except AssertionError:
                        k.write("assignment: Bad disposeHit status for HIT ID %s:\n" % hitId)
                        return
                    # Record the HIT deletion time.
                    self.cur.execute("""update hit_data set delete_time = '%s' where hit_id = '%s'""" % 
                            (submitTime, hitId))
                    self.dbcon.commit()
                    k.write("assignment: hit has no remaining assignments and has been deleted\n")
                else:
                    k.write("assignment: hit still has remaining Mturk or pending assignments and cannot be deleted\n")
            else:
                k.write("assignment: hit still has remaining Mturk or pending assignments and cannot be deleted\n")

    # Revoke Mapping Africa qualification unconditionally unless not qualified.
    # Returns True if worker was qualified and qualification was revoked; False otherwise.
    def revokeQualification(self, workerId, submitTime, force=False):
        # Revoke the qualification if not already done.
        qualified = self.querySingleValue("SELECT qualified FROM worker_data WHERE worker_id = '%s'" % (workerId))
        if qualified or force:
            # Remove all user maps and training assignments for this worker.
            self.cur.execute("""DELETE FROM qual_user_maps WHERE assignment_id IN 
                    (SELECT assignment_id FROM qual_assignment_data WHERE worker_id = %s)""" %
                    workerId)
            self.cur.execute("DELETE FROM qual_assignment_data WHERE worker_id = %s" % workerId)
            # Mark worker as having lost his qualification.
            self.cur.execute("""UPDATE worker_data SET qualified = false, last_time = '%s' 
                    WHERE worker_id = %s""" % (submitTime, workerId))
            self.dbcon.commit()
            return True
        else:
            return False

    # Revoke Mapping Africa qualification if quality score 
    # shows worker as no longer qualified.
    def revokeQualificationIfUnqualifed(self, workerId, submitTime):
        qualityScore = self.getQualityScore(workerId)
        if qualityScore is None:
            return False
        revocationThreshold = float(self.getConfiguration('Qual_RevocationThreshold'))
        if qualityScore >= revocationThreshold:
            return False
        self.revokeQualification(workerId, submitTime)
        return True

    # Record worker as qualified and pay training bonus.
    def approveTraining(self, workerId, completionTime):
        # Mark worker as qualified.
        self.cur.execute("""UPDATE worker_data SET last_time = %s, qualified = true,
                scores = %s, returns = %s
                WHERE worker_id = %s""", (completionTime, [], [], workerId))

        # Check to see if training bonus should be paid.
        # NOTE: this will only be paid the first time the worker qualifies.
        bonusPaid = self.querySingleValue("""select bonus_paid from worker_data
                where worker_id = '%s'""" % workerId)
        if not bonusPaid:
            trainBonusAmount = self.getConfiguration('Bonus_AmountTraining')
            trainBonusReason = self.getConfiguration('Bonus_ReasonTraining')
            self.grantBonus(MappingCommon.EVTTrainingBonus, workerId, trainBonusAmount, trainBonusReason)
            self.cur.execute("UPDATE worker_data SET bonus_paid = true WHERE worker_id = %s" % \
                workerId)
        self.dbcon.commit()


    # Record assignment approval.
    def approveAssignment(self, workerId, assignmentId, submitTime, warning=False):
        if warning:
            hitWarningDescription = self.getConfiguration('HitQ_WarningDescription')
            hitNoWarningThreshold = float(self.getConfiguration('HitQ_NoWarningThreshold'))
            feedback = (hitWarningDescription % hitNoWarningThreshold)
        else:
            feedback = ''
        reward = self.querySingleValue("""select reward from hit_data
                inner join assignment_data using (hit_id)
                where assignment_id = '%s'""" % assignmentId)
        self.cur.execute("""INSERT INTO assignment_history (event_time, event_type, worker_id, assignment_id, amount, feedback)
               VALUES ('%s', '%s', %s, %s, %s, '%s')""" % \
               (submitTime, MappingCommon.EVTApprovedAssignment, workerId, assignmentId, reward, feedback))
        self.dbcon.commit()

    # Record assignment rejection.
    def rejectAssignment(self, workerId, assignmentId, submitTime):
        hitAcceptThreshold = float(self.getConfiguration('HitQ_AcceptThreshold'))
        feedback = (self.getConfiguration('Hit_RejectDescription') % hitAcceptThreshold)
        self.cur.execute("""INSERT INTO assignment_history (event_time, event_type, worker_id, assignment_id, amount, feedback)
               VALUES ('%s', '%s', %s, %s, %s, '%s')""" % \
               (submitTime, MappingCommon.EVTRejectedAssignment, workerId, assignmentId, '0', feedback))
        self.dbcon.commit()

    # Records bonuses for training completion and quality work.
    # Automatically inserts current time into row.
    def grantBonus(self, bonusType, workerId, bonus, reason):
        self.cur.execute("""INSERT INTO assignment_history (event_type, worker_id, amount, feedback)
               VALUES ('%s', %s, %s, '%s')""" % \
               (bonusType, workerId, bonus, reason))
        self.dbcon.commit()

    # Pay bonus and return True if quality score shows worker as qualified.
    def payBonusIfQualified(self, workerId):
        qualityScore = self.getQualityScore(workerId)
        if qualityScore is None:
            return 0
        bonusThreshold = self.getConfiguration('Bonus_Threshold4')
        if bonusThreshold != 'ignore' and qualityScore >= float(bonusThreshold):
            bonusAmount = self.getConfiguration('Bonus_Amount4')
            bonusReason = self.getConfiguration('Bonus_Reason4')
            self.grantBonus(MappingCommon.EVTQualityBonus, workerId, bonusAmount, bonusReason)
            return 4
        bonusThreshold = self.getConfiguration('Bonus_Threshold3')
        if bonusThreshold != 'ignore' and qualityScore >= float(bonusThreshold):
            bonusAmount = self.getConfiguration('Bonus_Amount3')
            bonusReason = self.getConfiguration('Bonus_Reason3')
            self.grantBonus(MappingCommon.EVTQualityBonus, workerId, bonusAmount, bonusReason)
            return 3
        bonusThreshold = self.getConfiguration('Bonus_Threshold2')
        if bonusThreshold != 'ignore' and qualityScore >= float(bonusThreshold):
            bonusAmount = self.getConfiguration('Bonus_Amount2')
            bonusReason = self.getConfiguration('Bonus_Reason2')
            self.grantBonus(MappingCommon.EVTQualityBonus, workerId, bonusAmount, bonusReason)
            return 2
        bonusThreshold = self.getConfiguration('Bonus_Threshold1')
        if bonusThreshold != 'ignore' and qualityScore >= float(bonusThreshold):
            bonusAmount = self.getConfiguration('Bonus_Amount1')
            bonusReason = self.getConfiguration('Bonus_Reason1')
            self.grantBonus(MappingCommon.EVTQualityBonus, workerId, bonusAmount, bonusReason)
            return 1
        return 0

    if 0:
        def getHitStatus(self, hitId):
            self.getHitRS = self.mtcon.get_hit(hitId)
            assert self.getHitRS.status
            # Loop through the ResultSet looking for an Hit object.
            for r in self.getHitRS:
                if hasattr(r,'HIT'):
                    # Get the associated HIT's status.
                    self.hitStatus = r.HITStatus
            return self.hitStatus

        def approveRejectedAssignment(self, assignmentId, feedback):
            self.approveRejectedAssignmentRS = self.mtcon.approve_rejected_assignment(
                assignment_id = assignmentId,
                feedback = feedback
            )
            assert self.approveRejectedAssignmentRS.status

        def qualifications(self):
            self.hitsApproved = self.getConfiguration('Qual_NumberHitsApproved')
            self.percentApproved = self.getConfiguration('Qual_PercentAssignmentsApproved')
            self.percentReturned = self.getConfiguration('Qual_PercentAssignmentsReturned')
            self.percentAbandoned = self.getConfiguration('Qual_PercentAssignmentsAbandoned')
            self.QTRequired = self.getConfiguration('Qual_QualTestRequired')
            self.quals = Qualifications()
            if self.hitsApproved != 'ignore':
                self.quals.add(NumberHitsApprovedRequirement(
                    comparator="GreaterThan", 
                    integer_value=self.hitsApproved,
                    required_to_preview=False)
                )
            if self.percentApproved != 'ignore':
                self.quals.add(PercentAssignmentsApprovedRequirement(
                    comparator="GreaterThan", 
                    integer_value=self.percentApproved,
                    required_to_preview=False)
                )
            if self.percentReturned != 'ignore':
                self.quals.add(PercentAssignmentsReturnedRequirement(
                    comparator="LessThan", 
                    integer_value=self.percentReturned,
                    required_to_preview=False)
                )
            if self.percentAbandoned != 'ignore':
                self.quals.add(PercentAssignmentsAbandonedRequirement(
                    comparator="LessThan", 
                    integer_value=self.percentAbandoned,
                    required_to_preview=False)
                )
            if self.QTRequired != 'ignore':
                self.quals.add(Requirement(
                    # Retrieve the ID for the Mapping Africa qualification.
                    qualification_type_id=self.getSystemData('Qual_MappingAfricaId'),
                    comparator="Exists",
                    required_to_preview=False)
                )
            return self.quals

        def createQualificationType(self):
            self.qualTestName = self.getConfiguration('QualTest_Name')
            self.qualTestDescription = self.getConfiguration('QualTest_Description')
            self.qualTestRetryDelay = self.getConfiguration('QualTest_RetryDelay')
            self.qualTestDuration = self.getConfiguration('QualTest_Duration')
            self.createQualificationTypeRS = self.mtcon.create_qualification_type(
                name=self.qualTestName, 
                description=self.qualTestDescription, 
                status='Active', 
                retry_delay=self.qualTestRetryDelay, 
                test=self.qualTestQuestionForm(), 
                test_duration=self.qualTestDuration
            )
            assert self.createQualificationTypeRS.status
            # Loop through the ResultSet looking for an QualificationType object.
            for r in self.createQualificationTypeRS:
                if hasattr(r,'QualificationType'):
                    self.qualificationTypeId = r.QualificationTypeId
            # Save this value in the system_table.
            self.setSystemData('Qual_MappingAfricaId', self.qualificationTypeId)
            self.dbcon.commit()

        def qualTestQuestionForm(self):
            self.qualTestTitle = self.getConfiguration('QualTest_Title')
            self.qualTestOverview1 = self.getConfiguration('QualTest_Overview1')
            self.qualTestOverview2 = self.getConfiguration('QualTest_Overview2')
            self.qualTestOverview3 = self.getConfiguration('QualTest_Overview3')
            self.qualTestOverview4 = self.getConfiguration('QualTest_Overview4')
            self.serverName = self.getConfiguration('ServerName')
            self.apiUrl = self.getConfiguration('APIUrl')
            self.qualTest_TrainingScript = self.getConfiguration('QualTest_TrainingScript')
            self.videoUrl = self.getConfiguration('VideoUrl')
            self.qualTestIntroVideo = self.getConfiguration('QualTest_IntroVideo')
            self.qualTestIntroVideoWidth = self.getConfiguration('QualTest_IntroVideoWidth')
            self.qualTestIntroVideoHeight = self.getConfiguration('QualTest_IntroVideoHeight')
            self.qualTestInstructionalVideo = self.getConfiguration('QualTest_InstructionalVideo')
            self.qualTestInstructionalVideoWidth = self.getConfiguration('QualTest_InstructionalVideoWidth')
            self.qualTestInstructionalVideoHeight = self.getConfiguration('QualTest_InstructionalVideoHeight')
            self.introUrl = "https://%s%s/%s" % \
                (self.serverName, self.videoUrl, self.qualTestIntroVideo)
            self.instructionalUrl = "https://%s%s/%s" % \
                (self.serverName, self.videoUrl, self.qualTestInstructionalVideo)
            self.trainingUrl = "<p><a href=\"https://%s%s/%s\" target=\"_blank\">Click here to take the qualification test</a></p>" % \
                (self.serverName, self.apiUrl, self.qualTest_TrainingScript)

            self.questForm = QuestionForm()
            overview = Overview()
            overview.append_field('Title', self.qualTestTitle)
            overview.append(FormattedContent(self.qualTestOverview1))
            overview.append(Flash(self.introUrl,self.qualTestIntroVideoWidth,self.qualTestIntroVideoHeight))
            overview.append(FormattedContent(self.qualTestOverview2))
            overview.append(Flash(self.instructionalUrl,self.qualTestInstructionalVideoWidth,self.qualTestInstructionalVideoHeight))
            self.questForm.append(overview)
            content1 = QuestionContent()
            content1.append(FormattedContent(self.qualTestOverview3))
            content1.append(FormattedContent(self.trainingUrl))
            content1.append(FormattedContent(self.qualTestOverview4))
            answer = AnswerSpecification(FreeTextAnswer(num_lines=1))
            # identifier must match qid in getQualificationRequests()
            self.questForm.append(Question(identifier=1, is_required=True, content=content1, answer_spec=answer))
            return self.questForm

        def disposeQualificationType(self):
            self.disposeQualificationTypeRS = self.mtcon.dispose_qualification_type(
                # Retrieve the ID for the Mapping Africa qualification.
                self.getSystemData('Qual_MappingAfricaId')
            )
            assert self.disposeQualificationTypeRS.status
            # Clear this value in the system_table.
            self.setSystemData('Qual_MappingAfricaId', '')
            self.dbcon.commit()
            
        def getQualificationRequests(self):
            self.getQualificationRequestsRS = self.mtcon.get_qualification_requests(
                # Retrieve the ID for the Mapping Africa qualification.
                self.getSystemData('Qual_MappingAfricaId')
            )
            assert self.getQualificationRequestsRS.status
            # Loop through the ResultSet looking for an QualificationRequest object.
            self.qualificationRequests = []
            for r in self.getQualificationRequestsRS:
                if hasattr(r,'QualificationRequest'):
                    # Get the Qualification Request ID of the prospective worker.
                    qualificationRequestId = r.QualificationRequestId
                    # Get the ID of the worker making the request.
                    workerId = r.SubjectId
                    # Get the Training ID entered by the worker.
                    params = {}
                    for kv in r.answers[0]:
                        # qid must match identifier in qualTestQuestionForm().
                        if kv.qid == '1':
                            trainingId = kv.fields[0]
                    self.qualificationRequests.append((qualificationRequestId, workerId, trainingId))
            return self.qualificationRequests

        def grantQualification(self, qualificationRequestId):
            self.grantQualificationRS = self.mtcon.grant_qualification(qualificationRequestId)
            assert self.grantQualificationRS.status

        def rejectQualificationRequest(self, qualificationRequestId, reason):
            self.rejectQualificationRequestRS = self.mtcon.reject_qualification_request(
                qualificationRequestId,
                reason
            )
            assert self.rejectQualificationRequestRS.status

        def notifyWorkers(self, workers, subject, body):
            self.notifyWorkersRS = self.mtcon.notify_workers(workers, subject, body)
            assert self.notifyWorkersRS.status
            return self.notifyWorkersRS

