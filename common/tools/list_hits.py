#! /usr/bin/python

import sys
from MappingCommon import MappingCommon

mapc = MappingCommon()

nh = 0
nah = 0
nqh = 0
nfh = 0
nnh = 0
nh = 0
print "HIT Id\tkml name\ttype\treward\tstatus\t\t#rem\t#asgnd\t#pend\t#compl"
for hitId, hit in sorted(mapc.getAllHits().iteritems()):
    assignmentsRemaining = hit['maxAssignments'] - \
            (hit['assignmentsAssigned'] + hit['assignmentsPending'] + hit['assignmentsCompleted'])
    nh = nh + 1
    if assignmentsRemaining > 0:
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
    
    print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (hitId, hit['kmlName'], kmlType, hit['reward'], hitStatus, assignmentsRemaining, hit['assignmentsAssigned'], hit['assignmentsPending'], hit['assignmentsCompleted'])
    found = False
    label = False
    for asgmtId, asgmt in sorted(mapc.getAssignments(hitId=hitId).iteritems()):
        found = True
        if not label:
            sys.stdout.write("Assign Id(s): %s" % asgmtId)
            label = True
        else:
            sys.stdout.write(", %s" % asgmtId)
    else:
        if found:
            print

print '\nTotal HITs: %d; QAQC HITs: %d; FQAQC HITs: %d; non-QAQC HITs: %d; # assignable HITs: %d' % (nh, nqh, nfh, nnh, nah)
