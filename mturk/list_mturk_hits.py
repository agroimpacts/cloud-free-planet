from boto.mturk.connection import MTurkRequestError
from MTurkMappingAfrica import MTurkMappingAfrica

mtma = MTurkMappingAfrica()

#hits = mtma.mtcon.get_all_hits(response_groups='HITDetail, Minimal, HITAssignmentSummary')
hits = mtma.mtcon.get_all_hits()
nh = 0
print "HIT Id, status, #assign rem, #assign compl, #assign pend, title"
print "Assign Ids"
for hit in hits:
        nh = nh + 1
        print hit.HITId, hit.HITStatus, hit.NumberOfAssignmentsAvailable, \
            hit.NumberOfAssignmentsCompleted, hit.NumberOfAssignmentsPending, \
            hit.Title
        asmts = mtma.mtcon.get_assignments(hit_id=hit.HITId)
        for asmt in asmts:
            print asmt.AssignmentId
print nh, 'HITs'
