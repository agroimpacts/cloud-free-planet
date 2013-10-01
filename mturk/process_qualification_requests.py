#! /usr/bin/python

import os
import time
from datetime import datetime
from boto.mturk.connection import MTurkRequestError
from MTurkMappingAfrica import MTurkMappingAfrica

#
# Main code begins here.
#
mtma = MTurkMappingAfrica()

logFilePath = mtma.projectRoot + "/log"
k = open(logFilePath + "/processQualReqs.log", "a+")

pid = os.getpid()
pf = open(logFilePath + "/process_qualification_requests.pid", 'wb')
pf.write(repr(pid))
pf.close()

now = str(datetime.today())
k.write("\nprocessQualReqs: Daemon starting up at %s (pid %d)\n" % 
        (now, pid))
k.close()

# Execute loop based on polling interval
while True:
    hitPollingInterval = int(mtma.getConfiguration('HitPollingInterval'))
    hitAcceptThreshold = float(mtma.getConfiguration('HitAcceptThreshold'))

    k = open(logFilePath + "/processQualReqs.log", "a+")
    now = str(datetime.today())

    # Check for any pending qualification requests.
    qrs = mtma.getQualificationRequests()
    # Loop through them.
    for qr in qrs:
        (qualificationRequestId, workerId, trainingId) = qr

        # If this is a new worker,
        mtma.cur.execute("SELECT TRUE FROM worker_data WHERE worker_id = '%s'" 
% (workerId))
        if not mtma.cur.fetchone():
            mtma.cur.execute("""INSERT INTO worker_data
                (worker_id, first_time, last_time)
                VALUES ('%s', '%s', '%s')""" % (workerId, now, now))
        # Else, this is an existing worker.
        else:
            mtma.cur.execute("""UPDATE worker_data SET last_time = '%s'
                            WHERE worker_id = '%s'""" % (now, workerId))

        # Record the Worker ID for the specified Training ID.
        mtma.cur.execute("""UPDATE qual_worker_data SET last_time = '%s', 
            worker_id = '%s' WHERE training_id = '%s'""" % 
            (now, workerId, trainingId))
        k.write("\nprocessQualReqs: datetime = %s\n" % now)
        k.write("processQualReqs: Worker ID %s provided Training ID %s.\n" %
            (workerId, trainingId))

        doneCount = int(mtma.querySingleValue("""select count(*)
            from qual_assignment_data where training_id = '%s'
            and (completion_time is not null and score >= %s)""" %
            (trainingId, hitAcceptThreshold)))

        # Check if Training ID is bogus.
        if doneCount == 0:
            mtma.rejectQualificationRequest(qualificationRequestId, "Invalid training ID")
            k.write("processQualReqs: Training ID %s has no completed assignments.\n" % 
                trainingId)
            k.write("processQualReqs: Mapping Africa qualification rejected.\n")
            continue

        # Check if user is trying to get qualification before completing all the training maps.
        totCount = int(mtma.querySingleValue("""select count(*) from kml_data
            where kml_type = 'I'"""))
        if doneCount < totCount:
            mtma.rejectQualificationRequest(qualificationRequestId, "Incomplete test")
            k.write("processQualReqs: Training ID %s successfully completed only %d of %d maps.\n" %
                (trainingId, doneCount, totCount))
            k.write("processQualReqs: Mapping Africa qualification rejected.\n")
            continue

        # Grant the qualification and notify user via email.
        mtma.grantQualification(qualificationRequestId)
        k.write("processQualReqs: Training ID %s successfully completed all %d maps.\n" %
            (trainingId, totCount))
        k.write("processQualReqs: Mapping Africa qualification granted.\n")

    # Sleep for specified polling interval
    k.close()
    time.sleep(hitPollingInterval)
