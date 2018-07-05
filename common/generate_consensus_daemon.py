# A daemon which is used to watch the incoming fsites, generate consensus maps
# and trigger cvml when all fsites have been processed
# Author: Su Ye


from MappingCommon import MappingCommon
from datetime import datetime
import psycopg2
import time
import os

# the below is for debugging under SuYe's project root
# mapc = MappingCommon(projectRoot='/home/sye/github/mapperAL/')

mapc = MappingCommon()

# using 10% as risk threshold for warning, if risky pixel percentage is larger
# than 10% for a kml, the system will yield a warning (but won't stop)
risk_warning_thres = 0.1

logFilePath = mapc.projectRoot + "/log"
k = open(logFilePath + "/generateConsensus.log", "a+")

# daemon start
now = str(datetime.today())
k.write("\ngenerateConsensus: Daemon starting up at %s\n" % now)
k.close()

# Execute loop based on FKMLCheckingInterval
while True:

    # Query checking interval
    checking_interval = int(mapc.getConfiguration('FKMLCheckingInterval'))
    print(checking_interval)

    # minimum mapping count to create consensus maps
    min_map_count = int(mapc.getConfiguration('MinimumMappedCount'))

    # Obtain serialization lock to allow the daemon to access Sandbox and
    # database records without interfering with daemon.
    mapc.getSerializationLock()

    # read Fsites that are not processed from incoming_name table
    mapc.cur.execute("select name, iteration from incoming_names where "
                     "processed = false")
    fkml_row = mapc.cur.fetchall()
    num_unprocessed = len(fkml_row)

    # current_iteration_time is used to record the ongoing iteration time
    current_iteration = -1

    # total number of succeed and fail and total valid for the current iteration
    num_success = 0
    num_fail = 0

    # if there is any new incoming kmls, daemon starts generating consensus
    if num_unprocessed != 0:

        # use the max of iteration as the ongoing interation time
        iteration_list = list(row[1] for row in fkml_row)
        iteration = max(iteration_list)
        if current_iteration != iteration:
            current_iteration = iteration
            k = open(logFilePath + "/generateConsensus.log", "a+")
            k.write("\ngenerateConsensus: iteration_%s starting up at %s\n" %
                    (current_iteration, datetime.now()))
            k.close()

        # num_procssed is used to record kml that has been processed
        num_processed = 0
        for i in range(0, num_unprocessed - 1):
            mapc.cur.execute("""select name, mapped_count, consensus_conflict 
            from kml_data where kml_type = '%s' and name = '%s'""" %
                             (mapc.KmlFQAQC, fkml_row[i][0]))
            kmldata_row = mapc.cur.fetchall()

            # if kml has enough mapped count, do merging
            if kmldata_row[0][1] >= min_map_count:
                num_processed = num_processed + 1
                k = open(logFilePath + "/generateConsensus.log", "a+")

                # starting call consensus creation procedure
                if mapc.generateConsensusMap(k=k, kmlName=kmldata_row[i][0],
                                             minMapCount=min_map_count,
                                             riskWarningThres=risk_warning_thres):
                    num_success = num_success + 1
                else:
                    num_fail = num_fail + 1
                k.close()

                # no matter success or failed, update processed in incoming_names
                # to be TRUE
                try:
                    mapc.cur.execute("""update incoming_names set 
                    processed='TRUE' where name = '%s'""" % kmldata_row[i][0])
                except psycopg2.InternalError as e:
                    mapc.createAlertIssue("generateConsensus: kml %s internal "
                                          "database error %s\n%s" %
                                          (kmldata_row[i][0], e.pgcode, e.pgerror))
                    exit(1)

        # when all fkml are processed, write processing info into log, and
        # wake up cvml
        if num_processed == num_unprocessed:
            k = open(logFilePath + "/generateConsensus.log", "a+")

            # checking if iterations for all incoming kml are the identical
            k.write("\ngenerateConsensus: the iteration_%s has %s successful "
                    "and %s failed consensus creation\n" %
                    (current_iteration, num_success, num_fail))
            k.write("\ngenerateConsensus: the iteration_%s finishing up at "
                    "%s\n" %
                    (current_iteration, datetime.now()))
            k.close()

            # reset count to be zero
            num_success = 0
            num_fail = 0

            # wake up cvml
            if os.system('python execute_commands.py'):
                k.write("\ngenerateConsensus: the iteration_%s cvml starts "
                        "off...\n"
                        % current_iteration)
            else:
                mapc.createAlertIssue("\ngenerateConsensus: the iteration_%s "
                                      "starting off cvml fails\n" %
                                      current_iteration)
                break

            # call KMLgenerate_F.py to generate F sites for the next
            # iteration
            if os.system('python KMLgenerate_F.py'):
                k.write("\ngenerateConsensus: the iteration_%s KMLgenerate_F "
                        "starts off...\n"
                        % current_iteration)
            else:
                mapc.createAlertIssue("\ngenerateConsensus: the iteration_%s "
                                      "KMLgenerate_F fails\n" %
                                      current_iteration)
                break


    # Release serialization lock.
    mapc.releaseSerializationLock()

    # Sleep for specified checking interval
    time.sleep(checking_interval)
