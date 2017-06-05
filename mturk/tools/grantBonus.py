#! /usr/bin/python
## Grant bonuses to workers
## Based on the revokeQualification.py script

from boto.mturk.connection import MTurkRequestError,MTurkConnection
from MTurkMappingAfrica import MTurkMappingAfrica
from datetime import datetime

mtma = MTurkMappingAfrica(debug=0)

## Get information
workerId = raw_input("Please enter a Worker ID: ")
assignmentId = raw_input("Enter the Assignment ID: ")
bonus = raw_input("Enter the bonus amount: ")
reason = raw_input("Enter the reason for this bonus: ")

## Check to make sure that workerID and assignmentID match
workerIdChk, _, _, _ = mtma.getAssignment(assignmentId);
if (workerIdChk != workerId):
	print("Assignment %s was not completed by worker %s\n", 
			assignmentId, workerId)
else:
	now = str(datetime.today())

	mtma.grantBonus(self, assignmentId, workerId, bonus, reason)
	print("Bonus granted to worker %s" % workerId)

	## Write to log file
	logFilePath = mtma.projectRoot + "/log"
	k = open(logFilePath + "/bonuses.log", "a")
	k.write("Bonus amount %s granted to worker %s for assignment %s at %s "
			"for the following reason: %s\n", 
			bonus, workerId, assignmentId, now, reason) 
	k.close()

## Destroy the mtma object
del mtma
