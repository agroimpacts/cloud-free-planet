from datetime import datetime
from dateutil import tz
import psycopg2
from psycopg2.extensions import adapt

from boto.mturk.connection import MTurkConnection, MTurkRequestError
from boto.mturk.qualification import (
    Qualifications, NumberHitsApprovedRequirement, PercentAssignmentsApprovedRequirement, 
    PercentAssignmentsReturnedRequirement,PercentAssignmentsAbandonedRequirement, 
    Requirement
)
from boto.mturk.question import ExternalQuestion,QuestionForm,Overview,Question,QuestionContent,FormattedContent,AnswerSpecification,FreeTextAnswer,NumericConstraint,LengthConstraint
from boto.mturk.layoutparam import LayoutParameters, LayoutParameter

# Key connection parameters.
db_name = 'SouthAfrica'
db_user = '***REMOVED***'
db_password = '***REMOVED***'
mt_sandbox_host = 'mechanicalturk.sandbox.amazonaws.com'
mt_public_host = 'mechanicalturk.amazonaws.com'
aws_access_key_id = 'AKIAJDK3CO4RKHBZQU5A'
aws_secret_access_key = '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'

class MTurkMappingAfrica(object):

    # HIT assignment_data.status constants
    HITAccepted = 'Accepted'                    # HIT accepted by worker
    HITAbandoned = 'Abandoned'                  # HIT abandoned by worker
    HITReturned = 'Returned'                    # HIT returned by worker
    HITApproved = 'Approved'                    # HIT scored and approved
    HITRejected = 'Rejected'                    # HIT scored and rejected
    HITUnsaved = 'Unsaved'                      # HIT unsaved, hence approved & non-QAQC reused

    # QAQC status only
    HITUnscored = 'Unscored'                    # HIT not scorable, hence approved

    # non-QAQC statuses only
    HITPending = 'Pending'                      # Approved/Rejected/UnsavedQAQC/
                                                # UnscoredQAQC status 
                                                # pending next QAQC score
    HITPendingUnsaved = 'PendingUnsaved'        # HITUnsaved status pending next QAQC score
    HITUnsavedQAQC = 'UnsavedQAQC'              # QAQC HIT unsaved, hence non-QAQC HIT approved & reused
    HITUnscoredQAQC = 'UnscoredQAQC'            # QAQC HIT unscored, hence non-QAQC HIT approved & reused

    # KML kml_data.kml_type constants
    KmlNormal = 'N'                             # Normal (non-QAQC) KML
    KmlQAQC = 'Q'                               # QAQC KML
    KmlInitial = 'I'                            # Initial training KML

    # MTurk external submit path
    externalSubmit = '/mturk/externalSubmit'

    def __init__(self, debug=0):
        self.dbcon = psycopg2.connect("dbname=%s user=%s password=%s" % 
            (db_name, db_user, db_password))
        self.cur = self.dbcon.cursor()

        self.sandbox = self.getConfiguration('MTurkSandbox')
        if self.sandbox:
            self.host = mt_sandbox_host
        else:
            self.host = mt_public_host
        self.mtcon = MTurkConnection(
            aws_access_key_id = aws_access_key_id,
            aws_secret_access_key = aws_secret_access_key,
            host = self.host,
            is_secure = True,
            debug = debug
            )

    def close(self):
        self.mtcon.close()
        self.dbcon.close()

    def createHit(self, kml=None, hitType=KmlNormal):
        self.hitLifetime = self.getConfiguration('Hit_Lifetime')
        if hitType == MTurkMappingAfrica.KmlNormal:
            self.hitMaxAssignments = self.getConfiguration('Hit_MaxAssignmentsN')
        else:
            self.hitMaxAssignments = self.getConfiguration('Hit_MaxAssignmentsQ')

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

    def rejectAssignment(self, assignmentId, feedback=None):
        self.rejectAssignmentRS = self.mtcon.reject_assignment(
            assignment_id = assignmentId,
            feedback = feedback
        )
        assert self.rejectAssignmentRS.status

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
        self.quals = Qualifications()
        if self.hitsApproved != 'ignore':
            self.quals.add(NumberHitsApprovedRequirement(
                    comparator="GreaterThan", 
                    integer_value=self.hitsApproved,
                    required_to_preview=True)
            )
        if self.percentApproved != 'ignore':
            self.quals.add(PercentAssignmentsApprovedRequirement(
                    comparator="GreaterThan", 
                    integer_value=self.percentApproved,
                    required_to_preview=True)
            )
        if self.percentReturned != 'ignore':
            self.quals.add(PercentAssignmentsReturnedRequirement(
                    comparator="LessThan", 
                    integer_value=self.percentReturned,
                    required_to_preview=True)
            )
        if self.percentAbandoned != 'ignore':
            self.quals.add(PercentAssignmentsAbandonedRequirement(
                    comparator="LessThan", 
                    integer_value=self.percentAbandoned,
                    required_to_preview=True)
            )
        self.quals.add(Requirement(
                # Retrieve the ID for the Mapping Africa qualification.
                qualification_type_id=self.getSystemData('Qual_MappingAfricaId'),
                comparator='Exists')
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

    def qualTestQuestionForm(self):
        self.qualTestTitle = self.getConfiguration('QualTest_Title')
        self.qualTestOverview = self.getConfiguration('QualTest_Overview')
        self.qualTestText = self.getConfiguration('QualTest_Text')
        #print(self.qualTestText)
        self.questForm = QuestionForm()
        overview = Overview()
        overview.append_field('Title', self.qualTestTitle)
        overview.append(FormattedContent(self.qualTestOverview))
        self.questForm.append(overview)
        content1 = QuestionContent()
        content1.append(FormattedContent(self.qualTestText))
        answer = AnswerSpecification(FreeTextAnswer(num_lines=1))
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

    def getConfiguration(self, key):
        self.cur.execute("select value from configuration where key = '%s'" % key)
        return self.cur.fetchone()[0]

    def getSystemData(self, key):
        self.cur.execute("select value from system_data where key = '%s'" % key)
        return self.cur.fetchone()[0]

    def setSystemData(self, key, value):
        self.cur.execute("update system_data set value = '%s' where key = '%s'" % (value, key))
        self.dbcon.commit()

    def querySingleValue(self, sql):
        self.cur.execute(sql)
        return self.cur.fetchone()[0]
