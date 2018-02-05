#! /usr/bin/python

from MappingCommon import MappingCommon

mapc = MappingCommon()

nh = 0
nah = 0
nqh = 0
nfh = 0
nnh = 0
nh = 0
#print "HIT Id, kml name, kml type, reward, status, #assign rem, #assign compl, #assign pend, title"
print "HIT Id, kml name, kml type, reward, status, #assign rem, #assign compl"
print "Assign Ids"
for hitId, hit in mapc.getAllHits().iteritems():
    nh = nh + 1
    if hit['maxAssignments'] > hit['assignmentsCompleted']:
        nah = nah + 1
        hitStatus = 'Assignable'
    else:
        hitStatus = 'Unassignable'

    kmlType = hit['kmlType']
    if kmlType == MappingCommon.KmlQAQC:
        nqh = nqh + 1
    elif kmlType == MappingCommon.KmlFQAQC:
        nfh = nfh + 1
    elif kmlType == MappingCommon.KmlNormal:
        nnh = nnh + 1
    else:
        kmlType = 'U'       # Unknown
    
    print hitId, hit['kmlName'], kmlType, hit['reward'], hitStatus, hit['maxAssignments']-hit['assignmentsCompleted'], hit['assignmentsCompleted']
    for asgmtId, asgmt in mapc.getAssignments(hitId=hitId):
        print asgmtId

print 'Total HITs: %d; # assignable HITs: %d; QAQC HITs: %d; FQAQC HITs: %d; non-QAQC HITs: %d' % (nh, nah, nqh, nfh, nnh)
print mapc.getAssignments(hitId='3HJ1EVZS2OJ8JETZFA1EQKYGNMXR3E')
