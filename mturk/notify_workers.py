#! /usr/bin/python

import sys
import os
import re
from datetime import datetime
from MTurkMappingAfrica import MTurkMappingAfrica

if len(sys.argv) != 3:
    print "Error: Usage %s <worker_id[,...] | ALL> <filename_in_emails_directory>" % sys.argv[0]
    quit()
workerIds = sys.argv[1]
filename = os.path.dirname(sys.argv[0])
if len(filename) == 0:
    filename = '.'
filename += '/emails/' + sys.argv[2]

mtma = MTurkMappingAfrica()
logFilePath = mtma.projectRoot + "/log"
k = open(logFilePath + "/miscellaneous.log", "a+")

now = str(datetime.today())
k.write("\nnotify_workers: datetime = %s\n" % now)

if workerIds.lower() == 'all':
    mtma.cur.execute('select worker_id from worker_data')
    workers=(zip(*mtma.cur.fetchall()))[0]
else:
    workers = re.findall('[^,\s]+', workerIds)

# Read the file into a list.
try:
    lines = [line.rstrip() for line in open(filename)]
except:
    k.write("notify_workers: Error: File %s not found\n" % filename)
    print "Error: File %s not found" % filename
    k.close()
    del mtma
    quit()

# Extract the subject (assumed to be line 0).
subject = lines[0]

# Find the start of the body (1st non-blank line after the subject).
i = 1
while len(lines[i]) == 0:
    i = i + 1
body = '\n'.join(lines[i:])

k.write("notify_workers: Now sending to workers:\n")
print "Now sending to workers:"
for worker in workers:
    k.write("notify_workers: %s\n" % worker)
    print worker
k.write("notify_workers: Subject: %s\n" % subject)
k.write("notify_workers: Message from %s:\n" % filename)
k.write("notify_workers: %s\n" % body)

# Mturk can't handle a list of more than 100 workers, so we split up the list.
success = True
workerSublists = [workers[i:i+100] for i in xrange(0, len(workers), 100)]
for workerSublist in workerSublists:
    failures = mtma.notifyWorkers(workerSublist, subject, body)

    # Loop through the ResultSet looking for NotifyWorkersFailureStatus objects.
    for f in failures:
        k.write("notify_workers: Worker %s was not notified: Error reported was:\n%s\n" % 
                (f.workerId, f.failureMessage))
        print 'Worker %s was not notified: Error reported was:\n%s' % \
                (f.workerId, f.failureMessage)
        success = False
if success:
    k.write("notify_workers: All workers have been notified.\n")
    print "All workers have been notified."

k.close()

# Destroy mtma object.
del mtma
