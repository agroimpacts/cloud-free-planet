import smtplib
from MTurkMappingAfrica import MTurkMappingAfrica

class row:
    def __init__(self, status=None, create_time=None, delete_time=None, kml_type = None):
        self.status = status
        self.create_time = create_time
        self.delete_time = delete_time
        self.kml_type = kml_type

def email(msg = None):
    sender = 'lestes@princeton.edu'
    receiver = 'dmcr@princeton.edu'
    message = """From: %s
To: %s
Subject: create_hit_daemon validation problem

%s
""" % (sender, receiver, msg)

    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, [receiver], message)
        smtpObj.quit()
    except smtplib.SMTPException:
        print "Error: unable to send email: %s" % message

mtma = MTurkMappingAfrica()

# Calculate the number of QAQC HITs currently active on the MTurk server.
# Also, validate that the HITS on Mturk match the HITs recorded in the DB.
hits = {}

# Get all Murk HITs.
mthits = mtma.getAllHits()
for hit in mthits:
    hits[hit.HITId] = row(status=hit.HITStatus)

# Merge in all unverified DB HITS.
# Active HITs are always unverified, as are HITs that were deleted since the last poll cycle.
mtma.cur.execute("""
    select hit_id, create_time, delete_time, kml_type
    from hit_data 
    inner join kml_data using (name) 
    where not hit_verified
    """)
dbhits = mtma.cur.fetchall()
for hit in dbhits:
    if hit[0] not in hits:
        hits[hit[0]] = row(create_time=hit[1], delete_time=hit[2], kml_type=hit[3])
    else:
        hits[hit[0]].create_time = hit[1]
        hits[hit[0]].delete_time = hit[2]
        hits[hit[0]].kml_type = hit[3]

# Scaffolding to test all 3 error cases.
#hits['abc'] = row(status='Test')
#hits['2IFERSQV66RLV6G8F6MWDVKIDWPB3R'].delete_time = '2013-02-07 16:29:50.543883'
#hits['2CEAVKI62NJQ8Q5HBY0QK6BKSG5KS4'].delete_time = None

tot = 0
nvh = 0
nth = 0
nah = 0
nahq = 0
nahn = 0
for hitId, row in hits.iteritems():
    #print hitId, row.status, row.create_time, row.delete_time, row.kml_type
    tot = tot + 1
    # If HIT on Mturk but not in DB: should never happen.
    if row.status and not row.create_time:
        email("Error: Mturk HIT '%s' not in database!" % hitId)
    # if HIT in DB but not on Mturk,
    elif not row.status and row.create_time:
        # If DB says HIT still exists: should never happen.
        if not row.delete_time:
            email("Error: Active DB HIT '%s' not found on Mturk!" % hitId)
        # If DB says HIT has been deleted, the mark it as verified.
        else:
            mtma.cur.execute("update hit_data set hit_verified = True where hit_id = '%s'" % hitId)
            mtma.dbcon.commit()
            nvh = nvh + 1
    # if HIT is on Mturk and in DB,
    elif row.status and row.create_time:
        # if DB says HIT no longer exists: should never happen.
        if row.delete_time:
            email("Error: Deleted DB HIT '%s' still exists on Mturk!" % hitId)
        else:
            nth = nth + 1
            if row.status == 'Assignable':
                nah = nah + 1
                if row.kml_type == 'Q':
                    nahq = nahq + 1
                elif row.kml_type == 'N':
                    nahn = nahn + 1

print "Grand total number of HITs: %d" % tot
print "Number of deleted HITs verified : %d" % nvh
print "Total Number of active HITs: %d" % nah
print "Number of assignable HITs: %d" % nah
print "Number of assignable QAQC HITs: %d" % nahq
print "Number of assignable non-QAQC HITs: %d" % nahn
