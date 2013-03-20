from MTurkMappingAfrica import MTurkMappingAfrica

mtma = MTurkMappingAfrica()

hits = mtma.getAllHits()
nh = 0
for hit in hits:
        nh = nh + 1
        print hit.HITId, hit.HITStatus, hit.Title
        if hit.HITStatus == 'Reviewable':
            mtma.disposeHit(hit.HITId)
            print "Deleted HITId %s" % hit.HITId
print nh, 'HITs'
