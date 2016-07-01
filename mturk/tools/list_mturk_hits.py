from boto.mturk.connection import MTurkRequestError,MTurkConnection
from MTurkMappingAfrica import MTurkMappingAfrica

mtma = MTurkMappingAfrica(debug=0)

hits = mtma.getAllHits()
nh = 0
nah = 0
nqh = 0
nfh = 0
nnh = 0
nh = 0
print "HIT Id, kml type, reward, status, #assign rem, #assign compl, #assign pend, title"
print "Assign Ids"
for hit in hits:
        nh = nh + 1
        if hit.HITStatus == 'Assignable':
            nah = nah + 1
        # Get the KML type for this HIT.
        mtma.cur.execute("select kml_type from kml_data inner join hit_data using (name) where hit_id = '%s'" % hit.HITId)
        kmlType = mtma.cur.fetchone()
        if kmlType:
            kmlType = kmlType[0]
            if kmlType == MTurkMappingAfrica.KmlQAQC:
                nqh = nqh + 1
            elif kmlType == MTurkMappingAfrica.KmlFQAQC:
                nfh = nfh + 1
            elif kmlType == MTurkMappingAfrica.KmlNormal:
                nnh = nnh + 1
        else:
            kmlType = 'U'       # Unknown
        
        print hit.HITId, kmlType, hit.FormattedPrice, hit.HITStatus, hit.NumberOfAssignmentsAvailable, \
            hit.NumberOfAssignmentsCompleted, hit.NumberOfAssignmentsPending, \
            hit.Title
        asmts = mtma.mtcon.get_assignments(hit_id=hit.HITId, page_size=40)
        for asmt in asmts:
            print asmt.AssignmentId
print 'Total HITs: %d; # assignable HITs: %d; QAQC HITs: %d; FQAQC HITs: %d; non-QAQC HITs: %d' % (nh, nah, nqh, nfh, nnh)
