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
k = open(logFilePath + "/cleanupAbsentWorker.log", "a+")

now = str(datetime.today())
k.write("\ncleanupAbsentWorker: Daemon starting up at %s\n" % now)
k.close()

# Execute loop based on polling interval
while True:
    hitPollingInterval = int(mtma.getConfiguration('HitPollingInterval'))
    hitPendingAssignLimit = int(mtma.getConfiguration('HitPendingAssignLimit'))

    k = open(logFilePath + "/cleanupAbsentWorker.log", "a+")
    now = str(datetime.today())

    # Get serialization lock.
    mtma.getSerializationLock()

    # Commit the transaction just to refresh the value of localtimestamp below.
    mtma.dbcon.commit()
    # Search for all Pending assignments that have been in that state longer than 
    # the permitted threshold.
    mtma.cur.execute("""select hit_id, assignment_id, worker_id, completion_time 
        from assignment_data 
        where status = %s 
            and completion_time + interval '%s seconds' < localtimestamp(0)
        order by completion_time""", 
        (MTurkMappingAfrica.HITPending, hitPendingAssignLimit,))
    assignments = mtma.cur.fetchall()

    # If none then there's nothing to do for this polling cycle.
    if len(assignments) > 0:
        k.write("\ncleanupAbsentWorker: datetime = %s\n" % now)
        k.write("cleanupAbsentWorker: Checking for abandoned Pending assignments: found %d\n" % 
                len(assignments))

        # Loop on all the abadoned Pending assignments, and set their status to Untrusted;
        # then delete their associated HIT if appropriate.
        for assignment in assignments:
            hitId = assignment[0]
            assignmentId = assignment[1]
            workerId = assignment[2]
            completionTime = assignment[3];

            k.write("\ncleanupAbsentWorker: Cleaning up Pending assignmentId = %s\n" % assignmentId)
            k.write("cleanupAbsentWorker: Abandoned by workerId %s on %s\n" % 
                    (workerId, completionTime))

            # Record the final FQAQC or non-QAQC HIT status.
            assignmentStatus = MTurkMappingAfrica.HITUntrusted
            mtma.cur.execute("""update assignment_data set status = '%s' where assignment_id = '%s'""" %
                (assignmentStatus, assignmentId))
            mtma.dbcon.commit()
            k.write("cleanupAbsentWorker: FQAQC or non-QAQC assignment marked in DB as %s\n" %
                assignmentStatus.lower())

            # Delete the HIT if all assignments have been submitted and have a final status
            # (i.e., there are no assignments in pending or accepted status).
            try:
                hitStatus = mtma.getHitStatus(hitId)
            except MTurkRequestError as e:
                k.write("cleanupAbsentWorker: getHitStatus failed for HIT ID %s:\n%s\n%s\n" % 
                    (hitId, e.error_code, e.error_message))
                k.write("cleanupAbsentWorker: Fatal Error: cleanup_absent_worker daemon will now exit!\n")
                exit(-3)
            except AssertionError:
                k.write("cleanupAbsentWorker: Bad getHitStatus status for HIT ID %s:\n" % hitId)
                k.write("cleanupAbsentWorker: Fatal Error: cleanup_absent_worker daemon will now exit!\n")
                exit(-3)
            if hitStatus == 'Reviewable':
                nonFinalAssignCount = int(mtma.querySingleValue("""select count(*) from assignment_data
                    where hit_id = '%s' and status in ('%s','%s')""" %
                    (hitId, MTurkMappingAfrica.HITPending, MTurkMappingAfrica.HITAccepted)))
                if nonFinalAssignCount == 0:
                    try:
                        mtma.disposeHit(hitId)
                    except MTurkRequestError as e:
                        k.write("cleanupAbsentWorker: disposeHit failed for HIT ID %s:\n%s\n%s\n" % 
                            (hitId, e.error_code, e.error_message))
                        k.write("cleanupAbsentWorker: Fatal Error: cleanup_absent_worker daemon will now exit!\n")
                        exit(-3)
                    except AssertionError:
                        k.write("cleanupAbsentWorker: Bad disposeHit status for HIT ID %s:\n" % hitId)
                        k.write("cleanupAbsentWorker: Fatal Error: cleanup_absent_worker daemon will now exit!\n")
                        exit(-3)
                    # Record the HIT deletion time.
                    mtma.cur.execute("""update hit_data set delete_time = '%s' where hit_id = '%s'""" % 
                            (now, hitId))
                    mtma.dbcon.commit()
                    k.write("cleanupAbsentWorker: HIT %s has no remaining assignments and has been deleted\n" % hitId)
                else:
                    k.write("cleanupAbsentWorker: HIT %s still has remaining Mturk or pending assignments and cannot be deleted\n % hitId")
            else:
                k.write("cleanupAbsentWorker: HIT %s still has remaining Mturk or pending assignments and cannot be deleted\n" % hitId)

    # Release serialization lock.
    mtma.releaseSerializationLock()

    # Sleep for specified polling interval
    k.close()
    time.sleep(hitPollingInterval)
