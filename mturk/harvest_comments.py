#! /usr/bin/python

import sys
import textwrap
from MTurkMappingAfrica import MTurkMappingAfrica

if len(sys.argv) != 2:
    print "Error: Usage %s (<since_date> | ALL)" % sys.argv[0]
    quit()

sinceDate = sys.argv[1]
if sinceDate.lower() == 'all':
    sinceDate = "1/1/2013"

mtma = MTurkMappingAfrica()

mtma.cur.execute("""select worker_id, kml_type, completion_time, name as kml_name, 
        status, score, assignment_id, comment
        from assignment_data
        inner join hit_data using (hit_id)
        inner join kml_data using (name)
        where comment <> ''
        and comment <> 'Non-QAQC HIT rejection reversed'
        and comment <> 'Non-QAQC pending HIT approved'
        and completion_time >= '%s'
        order by worker_id, completion_time DESC""" % sinceDate)

workerIdPrev = ''
for row in mtma.cur:
    (workerId, kmlType, CompletionTime, kmlName, status, score, assignmentId, comment) = row
    if workerId != workerIdPrev:
        print("\nWorker ID: %s" % workerId)
        workerIdPrev = workerId
    print("%s: (%s)%-9s %-9s %4.02f %s" % (CompletionTime, kmlType, kmlName, status, score, assignmentId))
    lines = textwrap.wrap(comment, 65)
    first = "Comment:"
    for line in lines:
        print("     %s %s" % (first, line))
        first = "        "
