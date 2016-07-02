#! /usr/bin/python

import sys
from datetime import datetime
from MTurkMappingAfrica import MTurkMappingAfrica
from boto.mturk.connection import MTurkRequestError

if not (len(sys.argv) == 2 or (len(sys.argv) == 3 and sys.argv[1] == '-l')):
    print "Usage: %s [-l] <HIT_ID>" % sys.argv[0]
    sys.exit(1)
if len(sys.argv) == 2:
    list_only = False
    hitId = sys.argv[1]
else:
    list_only = True
    hitId = sys.argv[2]

mtma = MTurkMappingAfrica()

logFilePath = mtma.projectRoot + "/log"
k = open(logFilePath + "/miscellaneous.log", "a")

now = str(datetime.today())
k.write("\ndispose_single_hit: datetime = %s\n" % now)
if list_only:
    k.write("dispose_single_hit: %s is running in list-only mode. No actions will be taken.\n" % sys.argv[0])
    print "%s is running in list-only mode. No actions will be taken." % sys.argv[0]

try:
    hitStatus = mtma.getHitStatus(hitId)
except MTurkRequestError as e:
    k.write("dispose_single_hit: getHitStatus failed for HIT ID %s:\n%s\n%s\n" % 
        (hitId, e.error_code, e.error_message))
    print "getHitStatus failed for HIT ID %s:\n%s\n%s" % \
        (hitId, e.error_code, e.error_message)
    sys.exit(2)
except AssertionError:
    k.write("dispose_single_hit: Bad getHitStatus status for HIT ID %s\n" % hitId)
    print "Bad getHitStatus status for HIT ID %s" % hitId
    sys.exit(2)

if hitStatus == 'Reviewable':
    nonFinalAssignCount = int(mtma.querySingleValue("""select count(*) from assignment_data
        where hit_id = '%s' and status in ('%s', '%s')""" % (hitId, MTurkMappingAfrica.HITPending, MTurkMappingAfrica.HITAccepted)))
    if nonFinalAssignCount == 0:
        if not list_only:
            try:
                mtma.disposeHit(hitId)
            except MTurkRequestError as e:
                k.write("dispose_single_hit: disposeHit failed for HIT ID %s:\n%s\n%s\n" % 
                    (hitId, e.error_code, e.error_message))
                print "disposeHit failed for HIT ID %s:\n%s\n%s" % \
                    (hitId, e.error_code, e.error_message)
                sys.exit(2)
            except AssertionError:
                k.write("dispose_single_hit: Bad disposeHit status for HIT ID %s\n" % hitId)
                print "Bad disposeHit status for HIT ID %s" % hitId
                sys.exit(2)
            # Record the HIT deletion time.
            mtma.cur.execute("""update hit_data set delete_time = '%s' where hit_id = '%s'""" % 
                    (now, hitId))
            mtma.dbcon.commit()
        k.write("dispose_single_hit: HIT %s is in a final state and has been deleted\n" % hitId)
        print "HIT %s is in a final state and has been deleted" % hitId
    else:
        k.write("dispose_single_hit: HIT %s still has %s assignment(s) in Pending/Accepted state and cannot be deleted\n" % (hitId, nonFinalAssignCount))
        k.write("dispose_single_hit: You can wait for worker/cleanup_absent_worker/manual intervention to resolve this and then try again.\n")
        print "HIT %s still has %s assignment(s) in Pending/Accepted state and cannot be deleted" % (hitId, nonFinalAssignCount)
        print "You can wait for worker/cleanup_absent_worker/manual intervention to resolve this and then try again."
else:
    k.write("dispose_single_hit: Can't delete %s Mturk HIT %s\n" % (hitStatus, hitId))
    print "Can't delete %s Mturk HIT %s" % (hitStatus, hitId)
