#! /usr/bin/python

import sys
import os
import re
from MTurkMappingAfrica import MTurkMappingAfrica

if len(sys.argv) != 3:
    print "Error: Usage %s <worker_id[,...] | ALL> <filename_in_emails_directory>" % sys.argv[0]
    quit()
workerIds = sys.argv[1]
filename = os.path.dirname(sys.argv[0]) + '/emails/' + sys.argv[2]

mtma = MTurkMappingAfrica()

if workerIds.lower() == 'all':
    mtma.cur.execute('select worker_id from worker_data')
    workers=(zip(*mtma.cur.fetchall()))[0]
else:
    workers = re.findall('[^,\s]+', workerIds)

# Read the file into a list.
try:
    lines = [line.rstrip() for line in open(filename)]
except:
    print "Error: File %s not found" % filename
    quit()

# Extract the subject (assumed to be line 0).
subject = lines[0]

# Find the start of the body (1st non-blank line after the subject).
i = 1
while len(lines[i]) == 0:
    i = i + 1
body = '\n'.join(lines[i:])

print "Now sending to workers:"
for worker in workers:
    print worker
failures = mtma.notifyWorkers(workers, subject, body)

# Loop through the ResultSet looking for NotifyWorkersFailureStatus objects.
success = True
for f in failures:
    print 'Worker %s was not notified: Error reported was:\n%s' % (f.workerId, f.failureMessage)
    success = False
if success:
    print "All workers have been notified."
