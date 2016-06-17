import os
import pwd
from datetime import datetime
from dateutil import tz
import psycopg2
from psycopg2.extensions import adapt
import collections
from decimal import Decimal

from lock import lock
from boto.mturk.connection import MTurkConnection, MTurkRequestError
from boto.mturk.qualification import (
    Qualifications, NumberHitsApprovedRequirement, PercentAssignmentsApprovedRequirement, 
    PercentAssignmentsReturnedRequirement,PercentAssignmentsAbandonedRequirement, 
    Requirement
)
from boto.mturk.question import ExternalQuestion,QuestionForm,Overview,Question,QuestionContent,FormattedContent,AnswerSpecification,FreeTextAnswer,NumericConstraint,LengthConstraint,EmbeddedBinary,Flash
from boto.mturk.layoutparam import LayoutParameters, LayoutParameter

# Key connection parameters.
db_production_name = 'Africa'
db_sandbox_name = 'AfricaSandbox'
db_user = '***REMOVED***'
db_password = '***REMOVED***'
mt_production_host = 'mechanicalturk.amazonaws.com'
mt_sandbox_host = 'mechanicalturk.sandbox.amazonaws.com'
aws_access_key_id = 'AKIAJDK3CO4RKHBZQU5A'
aws_secret_access_key = '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'

class MTurkMappingAfrica(object):

    # HIT assignment_data.status constants

    # QAQC and non-QAQC HIT constants
    HITAccepted = 'Accepted'                    # HIT accepted by worker
    HITAbandoned = 'Abandoned'                  # HIT abandoned by worker
    HITReturned = 'Returned'                    # HIT returned by worker
    HITApproved = 'Approved'                    # HIT submitted and approved:
                                                # a) QAQC had high score
                                                # b) non-QAQC had high trust level
    HITUnsaved = 'Unsaved'                      # HIT unsaved, hence approved
                                                # (non-QAQC KML reused in this case)
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
    KmlFQAQC = 'F'                               # FQAQC KML
    KmlTraining = 'I'                           # Initial training KML

    # MTurk external submit path
    externalSubmit = '/mturk/externalSubmit'

    # Database column name constants
    ScoresCol = 'scores'
    ReturnsCol = 'returns'

    # Serialization lock file name
    lockFile = 'serial_file.lck'

    def __init__(self, debug=0):
        
        # Determine sandbox/mapper based on effective user name.
        self.euser = pwd.getpwuid(os.getuid()).pw_name
        if self.euser == 'sandbox':
            self.sandbox = True
        elif self.euser == 'mapper':
            self.sandbox = False
        else:
           raise Exception("MTurkMappingAfrica must run under sandbox or mapper user") 
        self.projectRoot = '/u/%s/afmap' % self.euser
        if self.sandbox:
            db_name = db_sandbox_name
            self.host = mt_sandbox_host
        else:
            db_name = db_production_name
            self.host = mt_production_host
        
        self.dbcon = psycopg2.connect("dbname=%s user=%s password=%s" % 
            (db_name, db_user, db_password))
        self.cur = self.dbcon.cursor()

        self.mtcon = MTurkConnection(
            aws_access_key_id = aws_access_key_id,
            aws_secret_access_key = aws_secret_access_key,
            host = self.host,
            is_secure = True,
            debug = debug
            )

    def __del__(self):
        self.close()

    def close(self):
        self.mtcon.close()
        self.dbcon.close()

    def createHit(self, kml=None, hitType=KmlNormal, maxAssignments=1):
        self.hitMaxAssignments = maxAssignments
        self.hitLifetime = self.getConfiguration('Hit_Lifetime')

        self.createHitRS = self.mtcon.create_hit(
            hit_type = self.registerHitType(),
            question = self.externalQuestion(kml), 
            lifetime = self.hitLifetime, 
            max_assignments = self.hitMaxAssignments
        )
        assert self.createHitRS.status
        # Loop through the ResultSet looking for an HIT object.
        for r in self.createHitRS:
            if hasattr(r,'HIT'):
                self.hitId = r.HITId
        return self.hitId

    def setNotification(self, hitType):
        self.mturkNotificationEmail = self.getConfiguration('MTurkNotificationEmail')
        self.setNotificationRS = self.mtcon.set_email_notification(
            hit_type = hitType,
            email = self.mturkNotificationEmail,
            event_types = "AssignmentSubmitted,AssignmentAbandoned,AssignmentReturned,HITExpired"
        )
        assert self.setNotificationRS.status

    def sendEmailTestEventNotification(self, testEventType):
        self.mturkNotificationEmail = self.getConfiguration('MTurkNotificationEmail')
        self.sendEmailTestEventNotificationRS = self.mtcon.send_email_test_event_notification(
            email = self.mturkNotificationEmail,
            event_types = "AssignmentSubmitted,AssignmentAbandoned,AssignmentReturned,HITReviewable,HITExpired,Ping",
            test_event_type = testEventType
        )
        assert self.sendEmailTestEventNotificationRS.status

    def sendRestTestEventNotification(self, testEventType):
        self.serverName = self.getConfiguration('ServerName')
        self.apiUrl = self.getConfiguration('APIUrl')
        self.mturkNotificationScript = self.getConfiguration('MTurkNotificationScript')
        self.url = "https://%s%s/%s" % \
            (self.serverName, self.apiUrl, self.mturkNotificationScript)
        self.sendRestTestEventNotificationRS = self.mtcon.send_rest_test_event_notification(
            url = self.url,
            event_types = "AssignmentSubmitted,AssignmentAbandoned,AssignmentReturned,HITReviewable,HITExpired,Ping",
            test_event_type = testEventType
        )
        assert self.sendRestTestEventNotificationRS.status

    def getAllHits(self, response_groups=None):
        return self.mtcon.get_all_hits(response_groups)

    def getHitStatus(self, hitId):
        self.getHitRS = self.mtcon.get_hit(hitId)
        assert self.getHitRS.status
        # Loop through the ResultSet looking for an Hit object.
        for r in self.getHitRS:
            if hasattr(r,'HIT'):
                # Get the associated HIT's status.
                self.hitStatus = r.HITStatus
        return self.hitStatus

    def getAssignment(self, assignmentId):
        # Add HITDetail ResponseGroup so as to get back the HITStatus parameter.
        self.getAssignmentRS = self.mtcon.get_assignment(assignmentId, response_groups='Minimal, HITDetail')
        assert self.getAssignmentRS.status
        # Loop through the ResultSet looking for an Assignment object.
        for r in self.getAssignmentRS:
            if hasattr(r,'Assignment'):
                # Get the ID of the worker for this assignment.
                self.workerId = r.WorkerId
                # Convert MTurk's submission time (UTC timestamp) to local time.
                dtmtk = datetime.strptime(r.SubmitTime, '%Y-%m-%dT%H:%M:%SZ')
                dtloc = dtmtk.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())
                self.submitTime = dtloc.strftime('%Y-%m-%d %H:%M:%S')
                # Get all the HIT return parameters passed by MTurk.
                self.params = {}
                for kv in r.answers[0]:
                    self.params[kv.qid] = kv.fields[0]
            elif hasattr(r,'HIT'):
                # Get the associated HIT's status.
                self.hitStatus = r.HITStatus
        return (self.workerId, self.submitTime, self.params, self.hitStatus)

    def approveAssignment(self, assignmentId):
        self.approveAssignmentRS = self.mtcon.approve_assignment(
            assignment_id = assignmentId
        )
        assert self.approveAssignmentRS.status

        # Pay the difficulty bonus if KML's fwts > 1.
        self.hitTypeRewardIncrement = self.getConfiguration('HitType_RewardIncrement')
        self.hitTypeRewardIncrement2 = self.getConfiguration('HitType_RewardIncrement2')
        self.cur.execute("""select fwts, name, worker_id, bonus_paid 
            from assignment_data inner join hit_data using (hit_id) 
            inner join kml_data using (name) inner join worker_data using (worker_id) 
            where assignment_id = '%s'""" % assignmentId)
        (fwts, name, workerId, bonusPaid) = self.cur.fetchone()
        bonusAmount = Decimal("0.00")
        if fwts > 1:
            bonusAmount = round(Decimal(self.hitTypeRewardIncrement) * \
            (int(fwts) - 1) + Decimal(self.hitTypeRewardIncrement2) * \
            (int(fwts) - 1)**2, 2)
            bonusReason = self.getConfiguration('Bonus_ReasonDifficulty')
            self.grantBonus(assignmentId, workerId, bonusAmount, bonusReason)

        # Check to see if training bonus should be paid.
        # Return True if bonus paid.
        trainBonusPaid = False
        if not bonusPaid:
            trainBonusAmount = self.getConfiguration('Bonus_AmountTraining')
            trainBonusReason = self.getConfiguration('Bonus_ReasonTraining')
            self.grantBonus(assignmentId, workerId, trainBonusAmount, trainBonusReason)
            self.cur.execute("update worker_data set bonus_paid = %s where worker_id = %s", \
                (True, workerId))
            self.dbcon.commit()
            trainBonusPaid = True

        return (fwts, bonusAmount, name, trainBonusPaid)

    def rejectAssignment(self, assignmentId):
        self.rejectAssignmentRS = self.mtcon.reject_assignment(
            assignment_id = assignmentId,
            feedback = self.getConfiguration('HitRejectDescription')
        )
        assert self.rejectAssignmentRS.status

    def approveRejectedAssignment(self, assignmentId, feedback):
        self.approveRejectedAssignmentRS = self.mtcon.approve_rejected_assignment(
            assignment_id = assignmentId,
            feedback = feedback
        )
        assert self.approveRejectedAssignmentRS.status

    def disposeHit(self, hitId):
        self.disposeHitRS = self.mtcon.dispose_hit(
            hit_id = hitId
        )
        assert self.disposeHitRS.status

    def registerHitType(self):
        self.hitTypeTitle = self.getConfiguration('HitType_Title')
        self.hitTypeDescription = self.getConfiguration('HitType_Description')
        self.hitTypeKeywords = self.getConfiguration('HitType_Keywords')
        self.hitTypeReward = self.getConfiguration('HitType_Reward')
        self.hitTypeDuration = self.getConfiguration('HitType_Duration')
        self.hitTypeApprovalDelay = self.getConfiguration('HitType_ApprovalDelay')
        self.registerHitTypeRS = self.mtcon.register_hit_type(
            title=self.hitTypeTitle, 
            description=self.hitTypeDescription, 
            keywords=self.hitTypeKeywords, 
            reward = self.hitTypeReward, 
            duration=self.hitTypeDuration, 
            approval_delay=self.hitTypeApprovalDelay, 
            qual_req=self.qualifications()
        )
        assert self.registerHitTypeRS.status
        # Loop through the ResultSet looking for an HIT object.
        for r in self.registerHitTypeRS:
            if hasattr(r,'HITTypeId'):
                self.hitTypeId = r.HITTypeId
        # Set up notifications for this HIT type.
        self.setNotification(self.hitTypeId)
        return self.hitTypeId

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

    def revokeQualification(self, workerId):
        self.revokeQualificationRS = self.mtcon.revoke_qualification(
            workerId,
            # Retrieve the ID and revocation reason for the Mapping Africa qualification.
            self.getSystemData('Qual_MappingAfricaId'),
            self.getConfiguration('Qual_RevocationDescription')
        )
        assert self.revokeQualificationRS.status

    def grantBonus(self, assignmentId, workerId, bonus, reason):
        self.grantBonusRS = self.mtcon.grant_bonus(
            worker_id = workerId,
            assignment_id = assignmentId,
            bonus_price = MTurkConnection.get_price_as_price(bonus),
            reason = reason
        )
        assert self.grantBonusRS.status

    def externalQuestion(self, kml=None):
        self.serverName = self.getConfiguration('ServerName')
        self.apiUrl = self.getConfiguration('APIUrl')
        self.mturkExtQuestionScript = self.getConfiguration('MTurkExtQuestionScript')
        self.mturkFrameHeight = self.getConfiguration('MTurkFrameHeight')
        self.url = "https://%s%s/%s?kmlName=%s" % \
            (self.serverName, self.apiUrl, self.mturkExtQuestionScript, kml)
        self.extQuestion = ExternalQuestion(
            external_url=self.url, 
            frame_height=self.mturkFrameHeight
        )
        return self.extQuestion

    def notifyWorkers(self, workers, subject, body):
        self.notifyWorkersRS = self.mtcon.notify_workers(workers, subject, body)
        assert self.notifyWorkersRS.status
        return self.notifyWorkersRS

    def getConfiguration(self, key):
        self.cur.execute("select value from configuration where key = '%s'" % key)
        return self.cur.fetchone()[0]

    def getSystemData(self, key):
        self.cur.execute("select value from system_data where key = '%s'" % key)
        return self.cur.fetchone()[0]

    def setSystemData(self, key, value):
        self.cur.execute("update system_data set value = '%s' where key = '%s'" % (value, key))
        self.dbcon.commit()

    # Request a single value from a single column of a table.
    # If there is no record that matches the select criteria, return None.
    def querySingleValue(self, sql):
        self.cur.execute(sql)
        try:
            return self.cur.fetchone()[0]
        except TypeError as e:
            if str(e) == "'NoneType' object is unsubscriptable":
                return None
            else:
                raise

    # Obtain serialization lock to allow create_hit_daemon.py, cleanup_absent_worker.py, and 
    # individual ProcessNotifications.py threads to access Mturk and database records
    # without interfering with each other.
    def getSerializationLock(self):
        self.lock = lock('%s/mturk/%s' % (self.projectRoot, MTurkMappingAfrica.lockFile))

    # Release serialization lock.
    def releaseSerializationLock(self):
        del self.lock

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

    # Get moving average of scores saved. If number of scores saved is 
    # less than the required depth, return None.
    def getAvgScore(self, workerId):
        depth = int(self.getConfiguration('Quality_ScoreHistDepth'))
        scores = collections.deque(self.getCB(self.ScoresCol, workerId),maxlen=depth)
        if len(scores) < depth:
            return None
        return sum(scores)/depth

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

    # Pay bonus and return True if quality score shows worker as qualified.
    def payBonusIfQualified(self, workerId, assignmentId):
        qualityScore = self.getQualityScore(workerId)
        if qualityScore is None:
            return 0
        bonusThreshold = self.getConfiguration('Bonus_Threshold4')
        if bonusThreshold != 'ignore' and qualityScore >= float(bonusThreshold):
            bonusAmount = self.getConfiguration('Bonus_Amount4')
            bonusReason = self.getConfiguration('Bonus_Reason4')
            self.grantBonus(assignmentId, workerId, bonusAmount, bonusReason)
            return 4
        bonusThreshold = self.getConfiguration('Bonus_Threshold3')
        if bonusThreshold != 'ignore' and qualityScore >= float(bonusThreshold):
            bonusAmount = self.getConfiguration('Bonus_Amount3')
            bonusReason = self.getConfiguration('Bonus_Reason3')
            self.grantBonus(assignmentId, workerId, bonusAmount, bonusReason)
            return 3
        bonusThreshold = self.getConfiguration('Bonus_Threshold2')
        if bonusThreshold != 'ignore' and qualityScore >= float(bonusThreshold):
            bonusAmount = self.getConfiguration('Bonus_Amount2')
            bonusReason = self.getConfiguration('Bonus_Reason2')
            self.grantBonus(assignmentId, workerId, bonusAmount, bonusReason)
            return 2
        bonusThreshold = self.getConfiguration('Bonus_Threshold1')
        if bonusThreshold != 'ignore' and qualityScore >= float(bonusThreshold):
            bonusAmount = self.getConfiguration('Bonus_Amount1')
            bonusReason = self.getConfiguration('Bonus_Reason1')
            self.grantBonus(assignmentId, workerId, bonusAmount, bonusReason)
            return 1
        return 0

    # Revoke Mapping Africa qualification unconditionally unless not qualified.
    def revokeQualificationUnconditionally(self, workerId, submitTime):
        # Revoke the qualification if not already done.
        self.cur.execute("SELECT qualified FROM worker_data WHERE worker_id = '%s'" % (workerId))
        qualified = self.cur.fetchone()[0]
        if qualified:
            # Mark worker as having lost his qualification.
            self.revokeQualification(workerId)
            self.cur.execute("""update worker_data set qualified = false, last_time = '%s' 
                where worker_id = '%s'""" % (submitTime, workerId))
            self.dbcon.commit()

    # Revoke Mapping Africa qualification if quality score 
    # shows worker as no longer qualified.
    def revokeQualificationIfUnqualifed(self, workerId, submitTime):
        qualityScore = self.getQualityScore(workerId)
        if qualityScore is None:
            return False
        revocationThreshold = float(self.getConfiguration('Qual_RevocationThreshold'))
        if qualityScore >= revocationThreshold:
            return False
        self.revokeQualificationUnconditionally(workerId, submitTime)
        return True

    # Return True if worker is trusted based on quality score.
    def isWorkerTrusted(self, workerId):
        qualityScore = self.getQualityScore(workerId)
        if qualityScore is None:
            return None
        trustThreshold = float(self.getConfiguration('HitNTrustThreshold'))
        if qualityScore >= trustThreshold:
            return True
        else:
            return False
