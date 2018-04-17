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
for hitId, hit in sorted(mapc.getHitInfo().iteritems()):
    nh = nh + 1
    if hit['status'] == 'Assignable':
        nah = nah + 1
    kmlType = hit['kmlType']
    if kmlType == MappingCommon.KmlQAQC:
        nqh = nqh + 1
    elif kmlType == MappingCommon.KmlFQAQC:
        nfh = nfh + 1
    elif kmlType == MappingCommon.KmlNormal:
        nnh = nnh + 1
    
    print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (hitId, hit['kmlName'], kmlType, hit['reward'], hit['status'], hit['assignmentsRemaining'], hit['assignmentsAssigned'], hit['assignmentsPending'], hit['assignmentsCompleted'])
    found = False
    label = False
    for asgmtId, asgmt in sorted(mapc.getAssignments(hitId=hitId).iteritems()):
        found = True
        if not label:
            sys.stdout.write("Assign ID/Worker ID: %s/%s" % (asgmtId, asgmt['workerId']))
            label = True
        else:
            sys.stdout.write(", %s/%s" % (asgmtId, asgmt['workerId']))
    else:
        if found:
            print

print '\nTotal HITs: %d; QAQC HITs: %d; FQAQC HITs: %d; non-QAQC HITs: %d; # assignable HITs: %d' % (nh, nqh, nfh, nnh, nah)
