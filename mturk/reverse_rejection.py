#! /usr/bin/python

import sys
from datetime import datetime
from MTurkMappingAfrica import MTurkMappingAfrica

if len(sys.argv) != 4:
    print "Error: Usage %s <hit_id> <worker_id> <feedback_text>" % sys.argv[0]
    quit()
hitId = sys.argv[1]
workerId = sys.argv[2]
feedback = sys.argv[3]

mtma = MTurkMappingAfrica()
logFilePath = mtma.projectRoot + "/log"
k = open(logFilePath + "/miscellaneous.log", "a+")

now = str(datetime.today())
k.write("\nreverse_rejection: datetime = %s\n" % now)

# Verify that this is a rejected HIT.
mtma.cur.execute("""select status, assignment_id from assignment_data
    where hit_id = '%s' and worker_id = '%s'""" % (hitId, workerId))
row = mtma.cur.fetchone()
if not row:
    k.write("reverse_rejection: HIT ID/Worker ID combination %s/%s doesn't exist\n" % (hitId, workerId))
    print "HIT ID/Worker ID combination %s/%s doesn't exist" % (hitId, workerId)
    quit()
status = row[0]
assignmentId = row[1]
if status != MTurkMappingAfrica.HITRejected:
    k.write("reverse_rejection: Assignment ID %s has status '%s' and cannot be reversed\n" %
        (assignmentId, status))
    print "Assignment ID %s has status '%s' and cannot be reversed" % \
        (assignmentId, status)
    quit()
        
# Reverse the rejection.
mtma.approveRejectedAssignment(assignmentId, feedback)

# Record the assignment reversal time and status.
mtma.cur.execute("""update assignment_data set completion_time = '%s', 
    status = '%s' where assignment_id = '%s'""" % 
    (now, MTurkMappingAfrica.HITReversed, assignmentId))
k.write("reverse_rejection: Rejected assignment %s has been marked as reversed\n" % 
    assignmentId)
k.write("reverse_rejection: Feedback to worker: %s\n" % feedback)
print "Rejected assignment %s has been marked as reversed" % assignmentId

# Commit changes
mtma.dbcon.commit()
# Destroy mtma object.
del mtma
