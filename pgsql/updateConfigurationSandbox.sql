-- Relative URL to python scripts on Mapping Africa server
UPDATE configuration SET value = '/api' WHERE key = 'APIUrl';
-- On Mturk server: total number of available HITs to be maintained. Probably needs to be closer to 100 in production.
UPDATE configuration SET value = '20' WHERE key = 'AvailHitTarget';
-- Bonus amount in dollars.
UPDATE configuration SET value = '0.2' WHERE key = 'Bonus_Amount1';
-- Bonus amount in dollars.
UPDATE configuration SET value = '0.4' WHERE key = 'Bonus_Amount2';
-- Bonus amount in dollars.
UPDATE configuration SET value = '0.6' WHERE key = 'Bonus_Amount3';
-- Bonus amount in dollars.
UPDATE configuration SET value = '0.8' WHERE key = 'Bonus_Amount4';
-- Bonus amount in dollars.
UPDATE configuration SET value = '1.20' WHERE key = 'Bonus_AmountTraining';
-- Text provided as the reason for granting the level 1 bonus.
UPDATE configuration SET value = 'Congratulations! You have earned accuracy bonus level 1.' WHERE key = 'Bonus_Reason1';
-- Text provided as the reason for granting the level 2 bonus.
UPDATE configuration SET value = 'Congratulations! You have earned accuracy bonus level 2.' WHERE key = 'Bonus_Reason2';
-- Text provided as the reason for granting the level 3 bonus.
UPDATE configuration SET value = 'Congratulations! You have earned accuracy bonus level 3.' WHERE key = 'Bonus_Reason3';
-- Text provided as the reason for granting the level 4 bonus.
UPDATE configuration SET value = 'Congratulations! You have earned accuracy bonus level 4.' WHERE key = 'Bonus_Reason4';
-- Text provided as the reason for a bonus that varies with the estimated difficulty of each HIT.
UPDATE configuration SET value = 'This is your difficulty bonus for the above HIT. This bonus varies with the estimated difficulty of the HIT. Note that estimates may result in overpayment or underpayment for individual HITs.' WHERE key = 'Bonus_ReasonDifficulty';
-- Text provided as the reason for granting the training bonus.
UPDATE configuration SET value = 'Congratulations on your successful qualification for Mapping Africa! To thank you for your time, effort, and interest in qualifying, we are crediting this bonus to your account.' WHERE key = 'Bonus_ReasonTraining';
-- Moving average score worker must achieve to receive this bonus. May be set to 'ignore'.
UPDATE configuration SET value = '0.8' WHERE key = 'Bonus_Threshold1';
-- Moving average score worker must achieve to receive this bonus. May be set to 'ignore'.
UPDATE configuration SET value = '0.85' WHERE key = 'Bonus_Threshold2';
-- Moving average score worker must achieve to receive this bonus. May be set to 'ignore'.
UPDATE configuration SET value = '0.9' WHERE key = 'Bonus_Threshold3';
-- Moving average score worker must achieve to receive this bonus. May be set to 'ignore'.
UPDATE configuration SET value = '0.95' WHERE key = 'Bonus_Threshold4';
-- Percentage of hits on MTurk server that are Future QAQC sites
UPDATE configuration SET value = '20' WHERE key = 'FqaqcHitPercentage';
-- Percentage of completed assignments a FQAQC HIT may not exceed to be considered active on MTurk and hence not be replaced. Range=0-99
UPDATE configuration SET value = '99' WHERE key = 'HitActiveAssignPercentF';
-- Percentage of completed assignments a non-QAQC HIT may not exceed to be considered active on MTurk and hence not be replaced. Range=0-99
UPDATE configuration SET value = '0' WHERE key = 'HitActiveAssignPercentN';
-- Score a training HIT must achieve to be accepted.
UPDATE configuration SET value = '0.6' WHERE key = 'HitIAcceptThreshold';
-- (1 year) lifetime of standard Mapping Africa HIT
UPDATE configuration SET value = '31536000' WHERE key = 'Hit_Lifetime';
-- Max assignments of Future QAQC Mapping Africa HITs
UPDATE configuration SET value = '20' WHERE key = 'Hit_MaxAssignmentsF';
-- Max number of assignments a HIT can have without incurring the MTurk HIT surcharge. Limit was 9 effective 7/21/2016. To ignore this limit, set this parameter >= to Hit_MaxAssignmentsF and Hit_MaxAssignmentsN.
UPDATE configuration SET value = '20' WHERE key = 'Hit_MaxAssignmentsMT';
-- Max assignments of standard Normal Mapping Africa HITs 
UPDATE configuration SET value = '1' WHERE key = 'Hit_MaxAssignmentsN';
-- Quality score a worker must achieve to have his non-QAQC HITs be marked as 'trusted'
UPDATE configuration SET value = '0.65' WHERE key = 'HitNTrustThreshold';
-- Max time in seconds that an assignment can remain in the Pending state before assuming that the worker may have quit.
UPDATE configuration SET value = '86400' WHERE key = 'HitPendingAssignLimit';
-- In seconds: for HIT-creation and other daemons.
UPDATE configuration SET value = '10' WHERE key = 'HitPollingInterval';
-- Score a QAQC HIT must achieve to be accepted and worker paid, possibly with a warning.
UPDATE configuration SET value = '0' WHERE key = 'HitQAcceptThreshold';
-- Score a QAQC HIT meeting the accept threshold must achieve for worker to be paid without a warning.
UPDATE configuration SET value = '0.6' WHERE key = 'HitQNoWarningThreshold';
-- This is the warning workers get when their score is >= the accept threshold but < no-warning threshold.
UPDATE configuration SET value = 'Just FYI, this map is below the minimum desired accuracy, which is %s. If you submit too many maps below this level of accuracy, you will reduce your average score below the level required to maintain your qualification.' WHERE key = 'HitQWarningDescription';
-- Message sent to user in the event of a HIT assignment score below threshold
UPDATE configuration SET value = 'We are sorry, but your accuracy score was too low (<%s) to accept your results.' WHERE key = 'HitRejectDescription';
-- (3 days) Approval delay in seconds of standard Mapping Africa HIT
UPDATE configuration SET value = '259200' WHERE key = 'HitType_ApprovalDelay';
-- Description of standard Mapping Africa HIT
UPDATE configuration SET value = 'Our project aims to improve existing maps of cropland in Africa, which are based on automated analyses of satellite images.  We think your keen eyes and image interpretation skills will do a better job!' WHERE key = 'HitType_Description';
-- (24 hours) Max assignment duration in seconds of standard Mapping Africa HIT. An accepted HIT is considered abandoned if not submitted before this time elapses.
UPDATE configuration SET value = '86400' WHERE key = 'HitType_Duration';
-- Keywords of standard Mapping Africa HIT
UPDATE configuration SET value = 'Africa, Farm, Agriculture, Development, Sustainability, Princeton, Crop, Field, Map, Digitize, Satellite, Image, Border, Boundary, Cartography, Ecology, Science' WHERE key = 'HitType_Keywords';
-- Reward in dollars of standard Mapping Africa HIT
UPDATE configuration SET value = '0.05' WHERE key = 'HitType_Reward';
-- Reward increment amount based on hit type. This is the first of two terms in a linear or polynomial reward increment function.
UPDATE configuration SET value = '0.17' WHERE key = 'HitType_RewardIncrement';
-- Reward increment. This is the second of two terms in a linear or polynomial reward increment function. If linear, value should be set to 0. 
UPDATE configuration SET value = '-0.016' WHERE key = 'HitType_RewardIncrement2';
-- Title of standard Mapping Africa HIT
UPDATE configuration SET value = 'Mapping Crop Fields in Africa' WHERE key = 'HitType_Title';
-- In seconds: for Normal KML generation script.
UPDATE configuration SET value = '600' WHERE key = 'KMLPollingInterval';
-- Relative URL to KML files on Mapping Africa server
UPDATE configuration SET value = '/kmls' WHERE key = 'KMLUrl';
-- Relative URL to reference and worker maps in KML file format on Mapping Africa server
UPDATE configuration SET value = '/maps' WHERE key = 'MapUrl';
-- On mapper server: target for minimum number of available normal KMLs.
UPDATE configuration SET value = '500' WHERE key = 'MinAvailNKMLTarget';
-- Script to display MTurk External Question
UPDATE configuration SET value = 'getkml' WHERE key = 'MTurkExtQuestionScript';
-- Height in pixels of the external question frame in an MTurk HIT window
UPDATE configuration SET value = '700' WHERE key = 'MTurkFrameHeight';
-- Script to notify mapper that there were not polygons mapped at HIT submission time
UPDATE configuration SET value = 'putkml' WHERE key = 'MTurkNoPolygonScript';
-- Address for delivering MTurk email notifications to the mapper server
UPDATE configuration SET value = 'sandbox@princeton.edu' WHERE key = 'MTurkNotificationEmail';
-- Script for delivering MTurk REST notifications to the mapper server
UPDATE configuration SET value = 'process_notifications' WHERE key = 'MTurkNotificationScript';
-- Script for posting polygons at HIT submission time.
UPDATE configuration SET value = 'postkml' WHERE key = 'MTurkPostPolygonScript';
-- Number of Normal KMLs produced whenever number of available KMLs on the mapper server drops below MinAvailNKMLTarget.
UPDATE configuration SET value = '500' WHERE key = 'NKMLBatchSize';
-- For QAQC kmls, the ratio of field to non-field kmls.
UPDATE configuration SET value = '3' WHERE key = 'QaqcFieldRatio';
-- On Mturk server: percentage of total KMLs that are QAQC: default will be 20.
UPDATE configuration SET value = '20' WHERE key = 'QaqcHitPercentage';
-- Number of notifications to use for computing % return of HITs for quality score. Should be 10 in production.
UPDATE configuration SET value = '10' WHERE key = 'Quality_ReturnHistDepth';
-- Value from 0.0 to 1.0 to indicate the weight that a return should have in the quality score. Should be 1.0 in production.
UPDATE configuration SET value = '1.0' WHERE key = 'Quality_ReturnWeight';
-- Number of scores to use for computing moving average of scores for quality score. Should be 10 in production.
UPDATE configuration SET value = '5' WHERE key = 'Quality_ScoreHistDepth';
-- Qualification for standard Mapping Africa HIT: threshold number or 'ignore'. Should be set to 1000 in production.
UPDATE configuration SET value = 'ignore' WHERE key = 'Qual_NumberHitsApproved';
-- Qualification for standard Mapping Africa HIT: 0-100 or 'ignore'. Should be set to 'ignore' in production.
UPDATE configuration SET value = 'ignore' WHERE key = 'Qual_PercentAssignmentsAbandoned';
-- Qualification for standard Mapping Africa HIT: 0-100 or 'ignore'. Should be set to 95 in production.
UPDATE configuration SET value = '50' WHERE key = 'Qual_PercentAssignmentsApproved';
-- Qualification for standard Mapping Africa HIT: 0-100 or 'ignore'. Should be set to 'ignore' in production.
UPDATE configuration SET value = 'ignore' WHERE key = 'Qual_PercentAssignmentsReturned';
-- Qualification for standard Mapping Africa HIT: 1 or 'ignore'. Should be set to 1 (i.e., true) in production.
UPDATE configuration SET value = '1' WHERE key = 'Qual_QualTestRequired';
-- Message sent to user in the event of a Mapping Africa qualification revocation
UPDATE configuration SET value = 'We are sorry, but your accuracy scores have been consistently too low, so we must revoke your Mapping Africa qualification. Please feel free to review the training video and retake the qualification test.' WHERE key = 'Qual_RevocationDescription';
-- Moving average score below which a worker has their Mapping Africa qualification revoked.
UPDATE configuration SET value = '0.6' WHERE key = 'Qual_RevocationThreshold';
-- Qualification test brief description
UPDATE configuration SET value = 'This is the Mapping Africa Qualification Test. It is required to work on any Mapping Africa HITs.' WHERE key = 'QualTest_Description';
-- Qualification test duration in seconds
UPDATE configuration SET value = '3600' WHERE key = 'QualTest_Duration';
-- Instructional video file name
UPDATE configuration SET value = 'mappingafrica_tutorial.swf' WHERE key = 'QualTest_InstructionalVideo';
-- Instructional video height in pixels
UPDATE configuration SET value = '480' WHERE key = 'QualTest_InstructionalVideoHeight';
-- Instructional video width in pixels
UPDATE configuration SET value = '640' WHERE key = 'QualTest_InstructionalVideoWidth';
-- Introductory video file name
UPDATE configuration SET value = 'mapping_africa_intro.swf' WHERE key = 'QualTest_IntroVideo';
-- Intro video height in pixels
UPDATE configuration SET value = '480' WHERE key = 'QualTest_IntroVideoHeight';
-- Intro video width in pixels
UPDATE configuration SET value = '640' WHERE key = 'QualTest_IntroVideoWidth';
-- Qualification test name
UPDATE configuration SET value = 'Mapping Africa' WHERE key = 'QualTest_Name';
-- Qualification test overview text preceding the intro video.
UPDATE configuration SET value = '<p>The video below provides an overview of the Mapping Africa project and qualification test.<br/>Please click the play button to watch this video, and then watch the training video below this one.<br/> For additional information on the project, including our variable payments (beyond the fixed base rate) for <br/> mapping effort and quality, please visit the <a href="http://mappingafrica.princeton.edu" target="_blank">project website</a>. (Please wait a few moments for video to load.) </p>' WHERE key = 'QualTest_Overview1';
-- Qualification test overview text to go between the intro and instructional videos.
UPDATE configuration SET value = '<p>Please view the training video below where you will learn how to map and identify agricultural fields;<br/>then click on the qualification test link located below the video. (Please wait a few moments for video to load.)</p>' WHERE key = 'QualTest_Overview2';
-- Qualification test overview text following the instructional video. Precedes the link to the test.
UPDATE configuration SET value = '<p>Please click on the link below (which will open a new window) and map any fields present in the images shown.</p>' WHERE key = 'QualTest_Overview3';
-- Qualification test overview text following the instructional video. Follows the link to the test, and specifies the Training ID pasting instructions.
UPDATE configuration SET value = '<p>When done, copy your Training ID into the text box below before clicking Submit. You will then be qualified to map (after a very short delay).</p>' WHERE key = 'QualTest_Overview4';
-- Qualification test retry delay in seconds: time for worker to wait before retrying if denied the qualification.
UPDATE configuration SET value = '60' WHERE key = 'QualTest_RetryDelay';
-- Text presented to returning worker upon completion of the Training Frame page.
UPDATE configuration SET value = 'Congratulations! You have successfully completed all %(totCount)d training maps. Now please copy your Training ID<br/><b>%(trainingId)s</b><br/>into the qualification test window answer field, and click "Done".<br/>You will receive an email confirmation that you have earned the Mapping Africa qualification shortly afterward.' WHERE key = 'QualTest_TF_TextEnd';
-- Text presented to returning worker on the Training Frame page.
UPDATE configuration SET value = 'You have successfully completed %(doneCount)d of %(totCount)d maps.' WHERE key = 'QualTest_TF_TextMiddle';
-- Text presented to new worker on the Training Frame page.
UPDATE configuration SET value = 'You will now briefly work on %(totCount)d maps to get hands-on familiarity with identifying and labeling agricultural fields.' WHERE key = 'QualTest_TF_TextStart';
-- Qualification test title
UPDATE configuration SET value = 'Qualification Test for the Mapping Africa Project' WHERE key = 'QualTest_Title';
-- Master training script.
UPDATE configuration SET value = 'trainingframe' WHERE key = 'QualTest_TrainingScript';
-- MappingAfrica server name (for building absolute URLs)
UPDATE configuration SET value = 'sandbox.princeton.edu' WHERE key = 'ServerName';
-- Relative URL to videos on Mapping Africa server
UPDATE configuration SET value = '/videos' WHERE key = 'VideoUrl';
