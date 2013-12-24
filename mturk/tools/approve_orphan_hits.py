from boto.mturk.connection import MTurkRequestError
from MTurkMappingAfrica import MTurkMappingAfrica

mtma = MTurkMappingAfrica()

hits = mtma.mtcon.get_all_hits()
for hit in hits:
    if hit.HITStatus == 'Reviewable' and "Crop Fields" in hit.Title:
        print hit.HITId, hit.HITStatus, hit.Title
        asmts = mtma.mtcon.get_assignments(hit_id=hit.HITId, status='Submitted')
        for asmt in asmts:
            mtma.approveAssignment(asmt.AssignmentId)
            print "Approved AssignmentId %s" % asmt.AssignmentId
        mtma.mtcon.expire_hit(hit.HITId)
        print "Expired HITId %s" % hit.HITId
