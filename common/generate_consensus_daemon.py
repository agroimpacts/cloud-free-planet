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

logFilePath = mapc.projectRoot + "/log"
k = open(logFilePath + "/generateConsensus.log", "a+")

# daemon start
now = str(datetime.today())
k.write("\ngenerateConsensus: Daemon starting up at %s\n" % now)
k.close()

# record the ongoing iteration time in the daemon
iteration_counter = -1

n_success = None
n_fail = None

# Execute loop based on FKMLCheckingInterval
while True:

    # Obtain serialization lock to allow the daemon to access Sandbox and
    # database records without interfering with daemon.
    mapc.getSerializationLock()

    # read Fsites that are not processed from incoming_name table
    mapc.cur.execute("SELECT name, run, iteration, iteration_time "
                     "FROM incoming_names "
                     "INNER JOIN iteration_metrics USING (run, iteration) "
                     "WHERE processed = false")
    fkml_row = mapc.cur.fetchall()
    n_notprocessed = len(fkml_row)
    index_name = 0
    index_run = 1
    index_iteration = 2
    index_iteration_time = 3

    # check if any new incoming kmls that is not processed
    if n_notprocessed != 0:
        k = open(logFilePath + "/generateConsensus.log", "a+")

        it = iter(fkml_row)
        first = next(it)

        # check if run and iterations of incoming kml are identical
        if n_notprocessed != 1:
            if (all(first[index_run] == rest[index_run] and
                    first[index_iteration] == rest[index_iteration] for rest in
                    it) == False):
                    mapc.createAlertIssue("generateConsensus: runs or "
                                          "iterations of incoming F kmls "
                                          "for iteration_%s "
                                          "are not identical"
                                          % iteration_counter + 1)
                    exit(1)

        # check if it is a new iteration
        # if it is a new iteration, initialize counter variables
        if first[index_iteration] - iteration_counter == 1:
            n_success = 0
            n_fail = 0
            iteration_counter = iteration_counter + 1
            k.write("\ngenerateConsensus: iteration_%s starting up at %s\n" %
                    (iteration_counter, first[index_iteration_time]))

        # check if the iteration from cvml is correct
        if first[index_iteration] != iteration_counter and first[
            index_iteration] - iteration_counter != 1:
           mapc.createAlertIssue("generateConsensus: cvml has processed %s "
                                 "iterations, but generate_consensus_daemon "
                                 "only received %s iterations"
                                 % (first[index_iteration], iteration_counter
                                    + 1))

        # record kmls that are actually processed among kml to be processed
        # for this processing time
        n_processed = 0

        for i in range(0, n_notprocessed - 1):

            mapc.cur.execute("""select name, mapped_count, mappers_needed 
            from kml_data where kml_type = '%s' and name = '%s'""" %
                             (mapc.KmlFQAQC, fkml_row[i][index_name]))
            kmldata_row = mapc.cur.fetchall()
            index_mappedcount = 1
            index_mappersneeded = 2

            # check if kml has been succussfully retrieved from kml_data
            if len(kmldata_row) == 0:
                 mapc.createAlertIssue("generateConsensus: fail to retrieve "
                                       "kml %s in the kml_data table"
                                           % fkml_row[i][index_name])

            # check if not processed kmls has enough mappers
            if kmldata_row[0][index_mappersneeded] is not None and kmldata_row[
                0][index_mappedcount] == kmldata_row[0][index_mappersneeded]:

                # call a kml consensus generation
                if mapc.generateConsensusMap(k=k,
                                             kmlName=kmldata_row[0][index_name],
                                             minMapCount=
                                             kmldata_row[0][index_mappedcount]):
                    n_success = n_success + 1
                else:
                    n_fail = n_fail + 1

                n_processed = n_processed + 1

                # no matter success or failed, update processed in incoming_names
                # to be TRUE
                try:
                    mapc.cur.execute("""update incoming_names set 
                    processed='TRUE' where name = '%s'""" % kmldata_row[i][0])
                    mapc.dbcon.commit()

                except psycopg2.InternalError as e:
                    mapc.createAlertIssue("generateConsensus: kml %s internal "
                                          "database error %s\n%s" %
                                          (kmldata_row[0][index_name],
                                           e.pgcode, e.pgerror))
                    exit(1)

        # when all fkml are processed, write processing info into log, 
        # wake up cvml, and call register_f_sites
        if n_processed == n_notprocessed:
            k.write("\ngenerateConsensus: the iteration_%s has %s successful "
                    "and %s failed consensus creation\n" %
                    (iteration_counter, n_success, n_fail))
            k.write("\ngenerateConsensus: the iteration_%s finishing up at "
                    "%s\n" %
                    (iteration_counter, datetime.now()))


            # wake up cvml
            if os.system('python run_cvml.py'):
                k.write("\ngenerateConsensus: the iteration_%s cvml starts "
                        "off...\n"
                        % iteration_counter)
            else:
                mapc.createAlertIssue("\ngenerateConsensus: the iteration_%s "
                                      "fails in waking up cvml\n" %
                                      iteration_counter)
                break

            # call register_f_sites to generate F sites for the next
            # iteration
            if os.system('python register_f_sites.py'):
                k.write("\ngenerateConsensus: the iteration_%s register_f_sites "
                        "starts off...\n"
                        % iteration_counter)
            else:
                mapc.createAlertIssue("\ngenerateConsensus: the iteration_%s "
                                      "register_f_sites fails\n" %
                                      iteration_counter)
                break


    # Release serialization lock.
    mapc.releaseSerializationLock()

    # Sleep for specified checking interval
    time.sleep(int(mapc.getConfiguration('FKMLCheckingInterval')))
