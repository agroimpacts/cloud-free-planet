#! /usr/bin/python

from datetime import datetime
from MTurkMappingAfrica import MTurkMappingAfrica

mtma = MTurkMappingAfrica()
logFilePath = mtma.projectRoot + "/log"
k = open(logFilePath + "/miscellaneous.log", "a+")

mtma.cur.execute('''
select assignment_id
from assignment_data a
inner join hit_data h using (hit_id)
inner join kml_data k using (name)
where status = 'Rejected'
and kml_type = 'N'
''')
assignment_ids=(zip(*mtma.cur.fetchall()))[0]

now = str(datetime.today())
k.write("\nreverse_rejections: datetime = %s\n" % now)
for assignment_id in assignment_ids:
    mtma.mtcon.approve_rejected_assignment(assignment_id,'''
We reversed this rejection. We apologize for the inconvenience.
''')
    # Record the assignment reversal time and status, and comment.
    assignmentStatus = MTurkMappingAfrica.HITApproved
    comment = 'Non-QAQC HIT rejection reversed'
    mtma.cur.execute("""update assignment_data set completion_time = '%s', 
        status = '%s', comment = '%s' where assignment_id = '%s'""" % 
        (now, assignmentStatus, comment, assignment_id))
    k.write("reverse_rejections: Rejected non-QAQC assignment %s has been marked as %s\n" % 
        (assignment_id, assignmentStatus.lower()))

# Commit changes
mtma.dbcon.commit()
# Destroy mtma object.
del mtma
