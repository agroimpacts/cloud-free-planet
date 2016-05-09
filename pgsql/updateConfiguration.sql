*** The parameters in this section have been changed for production. ***

-- Address for delivering MTurk email notifications to the mapper server
UPDATE configuration SET value = 'mapper@princeton.edu' WHERE key = 'MTurkNotificationEmail'
-- MappingAfrica server name (for building absolute URLs)
UPDATE configuration SET value = 'mapper.princeton.edu' WHERE key = 'ServerName'

*** Please review parameters below to determine if they should be 1) changed on AfricaSandbox 
    (and later migrated to Africa), 2) just be changed on Africa, or 3) be left as is.
    For the first case, leave the pair of lines where they are below, 
    edited to have the modified value.
    For the second case, move the pair of lines to the first section in this file above,
    edited to have the production value.
    For the 3rd case, just delete the appropriate pair of lines from this file. ***


-- On Mturk server: total number of available HITs to be maintained. Probably needs to be closer to 100 in production.
UPDATE configuration SET value = '8' WHERE key = 'AvailHitTarget'
-- Bonus amount in dollars.
UPDATE configuration SET value = '0.03' WHERE key = 'Bonus_Amount1'
-- Bonus amount in dollars.
UPDATE configuration SET value = '0.06' WHERE key = 'Bonus_Amount2'
-- Bonus amount in dollars.
UPDATE configuration SET value = '0.09' WHERE key = 'Bonus_Amount3'
-- Bonus amount in dollars.
UPDATE configuration SET value = '0.12' WHERE key = 'Bonus_Amount4'
-- Bonus amount in dollars.
UPDATE configuration SET value = '1.20' WHERE key = 'Bonus_AmountTraining'
-- Text provided as the reason for granting the level 1 bonus.
UPDATE configuration SET value = 'Congratulations! You have earned accuracy bonus level 1.' WHERE key = 'Bonus_Reason1'
-- Text provided as the reason for granting the level 2 bonus.
UPDATE configuration SET value = 'Congratulations! You have earned accuracy bonus level 2.' WHERE key = 'Bonus_Reason2'
-- Text provided as the reason for granting the level 3 bonus.
UPDATE configuration SET value = 'Congratulations! You have earned accuracy bonus level 3.' WHERE key = 'Bonus_Reason3'
-- Text provided as the reason for granting the level 4 bonus.
UPDATE configuration SET value = 'Congratulations! You have earned accuracy bonus level 4.' WHERE key = 'Bonus_Reason4'
-- Text provided as the reason for a bonus that varies with the estimated difficulty of each HIT.
UPDATE configuration SET value = 'This is your difficulty bonus for the above HIT. This bonus varies with the estimated difficulty of the HIT. Note that estimates may result in overpayment or underpayment for individual HITs, but should average out over a day's work.' WHERE key = 'Bonus_ReasonDifficulty'
-- Text provided as the reason for granting the training bonus.
UPDATE configuration SET value = 'Congratulations on your successful qualification for Mapping Africa! To thank you for your time, effort, and interest in qualifying, we are crediting this bonus to your account.' WHERE key = 'Bonus_ReasonTraining'
-- Moving average score worker must achieve to receive this bonus. May be set to 'ignore'.
UPDATE configuration SET value = '0.85' WHERE key = 'Bonus_Threshold1'
-- Moving average score worker must achieve to receive this bonus. May be set to 'ignore'.
UPDATE configuration SET value = '0.95' WHERE key = 'Bonus_Threshold2'
-- Moving average score worker must achieve to receive this bonus. May be set to 'ignore'.
UPDATE configuration SET value = '0.975' WHERE key = 'Bonus_Threshold3'
-- Moving average score worker must achieve to receive this bonus. May be set to 'ignore'.
UPDATE configuration SET value = '0.99' WHERE key = 'Bonus_Threshold4'
-- Percentage of hits on MTurk server that are Future QAQC sites
UPDATE configuration SET value = '25' WHERE key = 'FqaqcHitPercentage'
-- Max assignments of Future QAQC Mapping Africa HITs
UPDATE configuration SET value = '3' WHERE key = 'Hit_MaxAssignmentsF'
-- Max assignments of standard Normal Mapping Africa HITs 
UPDATE configuration SET value = '2' WHERE key = 'Hit_MaxAssignmentsN'
-- Quality score a worker must achieve to have his non-QAQC HITs be marked as 'trusted'
UPDATE configuration SET value = '0.65' WHERE key = 'HitNTrustThreshold'
-- Score a QAQC HIT must achieve to be accepted and worker paid
UPDATE configuration SET value = '0.6' WHERE key = 'HitQAcceptThreshold'
-- Message sent to user in the event of a HIT assignment score below threshold
UPDATE configuration SET value = 'We're sorry, but your accuracy score was too low to accept your results.' WHERE key = 'HitRejectDescription'
-- Reward in dollars of standard Mapping Africa HIT
UPDATE configuration SET value = '0.1' WHERE key = 'HitType_Reward'
-- Reward increment amount based on hit type
UPDATE configuration SET value = '0.05' WHERE key = 'HitType_RewardIncrement'
-- On mapper server: target for minimum number of available normal KMLs.
UPDATE configuration SET value = '500' WHERE key = 'MinAvailNKMLTarget'
-- Number of Normal KMLs produced whenever number of available KMLs on the mapper server drops below MinAvailNKMLTarget.
UPDATE configuration SET value = '500' WHERE key = 'NKMLBatchSize'
-- For QAQC kmls, the ratio of field to non-field kmls.
UPDATE configuration SET value = '3' WHERE key = 'QaqcFieldRatio'
-- On Mturk server: percentage of total KMLs that are QAQC: default will be 20.
UPDATE configuration SET value = '25' WHERE key = 'QaqcHitPercentage'
-- Number of notifications to use for computing % return of HITs for quality score. Should be 10 in production.
UPDATE configuration SET value = '10' WHERE key = 'Quality_ReturnHistDepth'
-- Value from 0.0 to 1.0 to indicate the weight that a return should have in the quality score. Should be 1.0 in production.
UPDATE configuration SET value = '1.0' WHERE key = 'Quality_ReturnWeight'
-- Number of scores to use for computing moving average of scores for quality score. Should be 10 in production.
UPDATE configuration SET value = '4' WHERE key = 'Quality_ScoreHistDepth'
-- Qualification for standard Mapping Africa HIT: threshold number or 'ignore'. Should be set to 1000 in production.
UPDATE configuration SET value = 'ignore' WHERE key = 'Qual_NumberHitsApproved'
-- Qualification for standard Mapping Africa HIT: 0-100 or 'ignore'. Should be set to 'ignore' in production.
UPDATE configuration SET value = 'ignore' WHERE key = 'Qual_PercentAssignmentsAbandoned'
-- Qualification for standard Mapping Africa HIT: 0-100 or 'ignore'. Should be set to 95 in production.
UPDATE configuration SET value = '0' WHERE key = 'Qual_PercentAssignmentsApproved'
-- Qualification for standard Mapping Africa HIT: 0-100 or 'ignore'. Should be set to 'ignore' in production.
UPDATE configuration SET value = 'ignore' WHERE key = 'Qual_PercentAssignmentsReturned'
-- Qualification for standard Mapping Africa HIT: 1 or 'ignore'. Should be set to 1 (i.e., true) in production.
UPDATE configuration SET value = '1' WHERE key = 'Qual_QualTestRequired'
-- Message sent to user in the event of a Mapping Africa qualification revocation
UPDATE configuration SET value = 'We're sorry, but your accuracy scores have been consistently too low, so we must revoke your Mapping Africa qualification. Please feel free to review the training video and retake the qualification test.' WHERE key = 'Qual_RevocationDescription'
-- Moving average score below which a worker has their Mapping Africa qualification revoked.
UPDATE configuration SET value = '0.6' WHERE key = 'Qual_RevocationThreshold'
-- Instructional video file name
UPDATE configuration SET value = 'Mapping_09102013.swf' WHERE key = 'QualTest_InstructionalVideo'
-- Introductory video file name
UPDATE configuration SET value = 'Mapping_Africa_Lyndon_10102013.swf' WHERE key = 'QualTest_IntroVideo'