#! /usr/bin/python

import os
import time
import smtplib
from datetime import datetime
from boto.mturk.connection import MTurkRequestError
from MTurkMappingAfrica import MTurkMappingAfrica

# Row class used in HIT validation logic.
class Row:
    def __init__(self, status=None, create_time=None, delete_time=None, kml_type=None):
        self.status = status
        self.create_time = create_time
        self.delete_time = delete_time
        self.kml_type = kml_type

# Email function used when there are validation failures.
def email(msg = None):
    sender = 'mapper@princeton.edu'
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

#
# Main code begins here.
#
mtma = MTurkMappingAfrica()

mtma.cur.execute("select value from configuration where key = 'ProjectRoot'")
logFilePath = mtma.cur.fetchone()[0] + "/log"
k = open(logFilePath + "/createHit.log", "a+")

pid = os.getpid()
pf = open(logFilePath + "/create_hit_daemon.pid", 'wb')
pf.write(repr(pid))
pf.close()

now = str(datetime.today())
k.write("\ncreateHit: Daemon starting up at %s (pid %d)\n" % (now, pid))
k.close()

# Execute loop based on polling interval
while True:
    mtma.cur.execute("select value from configuration where key = 'HitPollingInterval'")
    hitPollingInterval = int(mtma.cur.fetchone()[0])
    mtma.cur.execute("select value from configuration where key = 'QaqcHitPercentage'")
    qaqcHitPercentage = int(mtma.cur.fetchone()[0])
    mtma.cur.execute("select value from configuration where key = 'AvailHitTarget'")
    availHitTarget = int(mtma.cur.fetchone()[0])

    k = open(logFilePath + "/createHit.log", "a+")
    now = str(datetime.today())

    # Determine the number of QAQC and non-QAQC HITs that should exist.
    numAvailQaqcHits = int(round(float(availHitTarget * qaqcHitPercentage) / 100.))
    numAvailNonQaqcHits = availHitTarget - numAvailQaqcHits

    # Validate that the HITS on Mturk match the HITs recorded in the DB.
    hits = {}

    # Get all Murk HITs.
    mthits = mtma.getAllHits()
    for hit in mthits:
        hits[hit.HITId] = Row(status=hit.HITStatus)

    # Merge in all unverified DB HITS.
    # Note: active HITs are always unverified, 
    #       as are HITs that were deleted since the last poll cycle.
    mtma.cur.execute("""
        select hit_id, create_time, delete_time, kml_type
        from hit_data
        inner join kml_data using (name)
        where not hit_verified
        """)
    dbhits = mtma.cur.fetchall()
    for hit in dbhits:
        if hit[0] not in hits:
            hits[hit[0]] = Row(create_time=hit[1], delete_time=hit[2], kml_type=hit[3])
        else:
            hits[hit[0]].create_time = hit[1]
            hits[hit[0]].delete_time = hit[2]
            hits[hit[0]].kml_type = hit[3]

    # Do the verification.
    numMturkQaqcHits = 0
    numMturkNonQaqcHits = 0
    for hitId, row in hits.iteritems():
        #print hitId, row.status, row.create_time, row.delete_time, row.kml_type

        # If HIT on Mturk but not in DB: should never happen.
        if row.status and not row.create_time:
            k.write("createHit: Error: Mturk HIT '%s' not in database!\n" % hitId)
            email("Error: Mturk HIT '%s' not in database!" % hitId)
        # if HIT in DB but not on Mturk,
        elif not row.status and row.create_time:
            # If DB says HIT still exists: should never happen.
            if not row.delete_time:
                # Record the HIT deletion time.
                mtma.cur.execute("""update hit_data set hit_verified = True, delete_time = '%s' 
                    where hit_id = '%s'""" % (now, hitId))
                k.write("createHit: Error: Active DB HIT '%s' not found on Mturk!\ncreateHit: Now marked as deleted in DB.\n" % hitId)
                email("Error: Active DB HIT '%s' not found on Mturk!\r\nNow marked as deleted in DB." % hitId)
            # If DB says HIT has been deleted, then mark it as verified.
            else:
                mtma.cur.execute("""update hit_data set hit_verified = True 
                    where hit_id = '%s'""" % hitId)
                mtma.dbcon.commit()
        # if HIT is on Mturk and in DB,
        elif row.status and row.create_time:
            # if DB says HIT no longer exists: should never happen.
            if row.delete_time:
                k.write("createHit: Error: Deleted DB HIT '%s' still exists on Mturk!\n" % hitId)
                email("Error: Deleted DB HIT '%s' still exists on Mturk!" % hitId)
            else:
                # Calculate the current number of assignable QAQC and non-QAQC HITs 
                # currently active on the MTurk server.
                if row.status == 'Assignable':
                    if row.kml_type == MTurkMappingAfrica.KmlQAQC:
                        numMturkQaqcHits = numMturkQaqcHits + 1
                    elif row.kml_type == MTurkMappingAfrica.KmlNormal:
                        numMturkNonQaqcHits = numMturkNonQaqcHits + 1

    # Create any needed QAQC HITs.
    kmlType = MTurkMappingAfrica.KmlQAQC
    numReqdQaqcHits = max(numAvailQaqcHits - numMturkQaqcHits, 0)
    if numReqdQaqcHits > 0:
        k.write("\ncreateHit: datetime = %s\n" % now)
        k.write("createHit: createHit sees %s QAQC HITs, and needs to create %s HITs\n" % 
            (numMturkQaqcHits, numReqdQaqcHits))

    for i in xrange(numReqdQaqcHits):
        # Retrieve the last kml gid used to create a QAQC HIT.
        mtma.cur.execute("select value from system_data where key = 'CurQaqcGid'")
        curQaqcGid = mtma.cur.fetchone()[0]

        # Select the next kml for which to create a HIT. 
        # Look for all kmls of the right type whose gid is greater than the last kml chosen.
        # Exclude any kmls that currently have an active HIT on the MTurk server.
        mtma.cur.execute("""
            select name, gid from kml_data k 
            where not exists (select true from hit_data h 
                where h.name = k.name and delete_time is null)
            and  kml_type = '%s' 
            and gid > %s 
            order by gid 
            limit 1""" % (kmlType, curQaqcGid))
        row = mtma.cur.fetchone()
        # If we have no kmls left, loop back to the beginning of the table.
        if not row:
            curQaqcGid = 0
            mtma.cur.execute("""
                select name, gid from kml_data k 
                where not exists (select true from hit_data h 
                    where h.name = k.name and delete_time is null)
                and  kml_type = '%s' 
                and gid > %s 
                order by gid 
                limit 1""" % (kmlType, curQaqcGid))
            row = mtma.cur.fetchone()
            # If we still have no kmls left, all kmls are in use as HITs.
            # Try again later.
            if not row:
                break
        nextKml = row[0]
        gid = row[1]
        mtma.cur.execute("update system_data set value = '%s' where key = 'CurQaqcGid'" % gid)
        mtma.dbcon.commit()

        # Create the QAQC HIT
        try:
            hitId = mtma.createHit(kml=nextKml, hitType=kmlType)
        except MTurkRequestError as e:
            k.write("createHit: createHit failed for KML %s:\n%s\n%s\n" %
                (nextKml, e.error_code, e.error_message))
            exit(-1)
        except AssertionError:
            k.write("createHit: Bad createHit status for KML %s:\n" % nextKml)
            exit(-2)

        # Record the HIT ID.
        mtma.cur.execute("""insert into hit_data (hit_id, name, create_time) 
            values ('%s' , '%s', '%s')""" % (hitId, nextKml, now))
        mtma.dbcon.commit()
        k.write("createHit: Created HIT ID %s for QAQC KML %s\n" % (hitId, nextKml))

    # Create any needed non-QAQC HITs.
    kmlType = MTurkMappingAfrica.KmlNormal
    numReqdNonQaqcHits = max(numAvailNonQaqcHits - numMturkNonQaqcHits, 0)
    if numReqdNonQaqcHits > 0:
        k.write("\ncreateHit: datetime = %s\n" % now)
        k.write("createHit: createHit sees %s non-QAQC HITs, and needs to create %s HITs\n" % 
            (numMturkNonQaqcHits, numReqdNonQaqcHits))

    for i in xrange(numReqdNonQaqcHits):
        # Retrieve the last kml gid used to create a non-QAQC HIT.
        mtma.cur.execute("select value from system_data where key = 'CurNonQaqcGid'")
        curNonQaqcGid = mtma.cur.fetchone()[0]

        # Select the next kml for which to create a HIT. 
        # Look for all kmls of the right type whose gid is greater than the last kml chosen.
        # Exclude any kmls that currently have an active HIT on the MTurk server, or
        # that are deleted but previously approved.
        mtma.cur.execute("""
            select name, gid from kml_data k 
            where not exists
                (select true from hit_data h 
                left outer join assignment_data a using (hit_id)
                where h.name = k.name 
                and (h.delete_time is null or a.status = 'Approved'))
            and  kml_type = '%s' 
            and gid > %s 
            order by gid 
            limit 1""" % (kmlType, curQaqcGid))
        row = mtma.cur.fetchone()
        # If we have no kmls left, all kmls in the kml_data table have been 
        # successfully processed. Notify Lyndon that more kmls are needed.
        if not row:
            # Set notification delay to 1 hour.
            hitPollingInterval = 3600
            k.write("createHit: Alert: all KMLs in kml_data table have been successfully processed. More KMLs needed to create more HITs.")
            email("Alert: all KMLs in kml_data table have been successfully processed. More KMLs needed to create more HITs.")
            break
        nextKml = row[0]
        gid = row[1]
        mtma.cur.execute("update system_data set value = '%s' where key = 'CurNonQaqcGid'" % gid)
        mtma.dbcon.commit()

        # Create the non-QAQC HIT
        try:
            hitId = mtma.createHit(kml=nextKml, hitType=kmlType)
        except MTurkRequestError as e:
            k.write("createHit: createHit failed for KML %s:\n%s\n%s\n" %
                (nextKml, e.error_code, e.error_message))
            exit(-1)
        except AssertionError:
            k.write("createHit: Bad createHit status for KML %s:\n" % nextKml)
            exit(-2)

        # Record the HIT ID.
        mtma.cur.execute("""insert into hit_data (hit_id, name, create_time) 
            values ('%s' , '%s', '%s')""" % (hitId, nextKml, now))
        mtma.dbcon.commit()
        k.write("createHit: Created HIT ID %s for non-QAQC KML %s\n" % (hitId, nextKml))

    # Sleep for specified polling interval
    k.close()
    time.sleep(hitPollingInterval)
