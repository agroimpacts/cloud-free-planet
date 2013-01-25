from boto.mturk.connection import MTurkRequestError
from MTurkMappingAfrica import MTurkMappingAfrica

mtma = MTurkMappingAfrica()

hits = mtma.mtcon.get_all_hits()
nh = 0
for hit in hits:
        nh = nh + 1
        print hit.HITId, hit.HITStatus, hit.Title
        if hit.HITStatus == 'Assignable':
            mtma.mtcon.expire_hit(hit.HITId)
            mtma.mtcon.dispose_hit(hit.HITId)
            print "Expired and deleted HITId %s" % hit.HITId
print nh, 'HITs'
