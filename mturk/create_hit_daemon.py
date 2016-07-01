#! /usr/bin/python

import os
import time
import smtplib
from datetime import datetime
from boto.mturk.connection import MTurkRequestError
from MTurkMappingAfrica import MTurkMappingAfrica

# Row class used in HIT validation logic.
class Row:
    def __init__(self, status=None, assignments_completed=None, create_time=None, 
            delete_time=None, max_assignments=None, kml_type=None):
        self.status = status
        self.assignments_completed = assignments_completed
        self.create_time = create_time
        self.delete_time = delete_time
        self.max_assignments = max_assignments
        self.kml_type = kml_type

# Email function used when there are validation failures.
# This email address has been configured on trac.princeton.edu in
# /etc/aliases and /usr/local/etc/email2trac.conf to create a ticket
# under the Internal Alert component.
def email(mtma, msg = None):
    sender = '%s@mapper.princeton.edu' % mtma.euser
    receiver = 'mappingafrica_internal_alert@trac.princeton.edu'
    message = """From: %s
To: %s
Subject: create_hit_daemon problem

%s
""" % (sender, receiver, msg)

    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receiver.split(","), message)
        smtpObj.quit()
    except smtplib.SMTPException:
        print "Error: unable to send email: %s" % message

#
# Main code begins here.
#
daemonStarted = False
fatalError = False
fatalErrorMsg = ""
fqaqcEmailCount = 0
nqaqcEmailCount = 0
emailFrequency = 60 * 60 * 12  # 12 hours

mtma = MTurkMappingAfrica()

logFilePath = mtma.projectRoot + "/log"
k = open(logFilePath + "/createHit.log", "a+")

now = str(datetime.today())
k.write("\ncreateHit: Daemon starting up at %s\n" % now)
k.close()

# Execute loop based on polling interval
while True:
    hitPollingInterval = int(mtma.getConfiguration('HitPollingInterval'))
    qaqcHitPercentage = int(mtma.getConfiguration('QaqcHitPercentage'))
    fqaqcHitPercentage = int(mtma.getConfiguration('FqaqcHitPercentage'))
    availHitTarget = int(mtma.getConfiguration('AvailHitTarget'))
    hitMaxAssignmentsMT = int(mtma.getConfiguration('Hit_MaxAssignmentsMT'))
    hitActiveAssignPercentF = int(mtma.getConfiguration('HitActiveAssignPercentF'))
    hitActiveAssignPercentN = int(mtma.getConfiguration('HitActiveAssignPercentN'))

    k = open(logFilePath + "/createHit.log", "a+")
    now = str(datetime.today())

    # Determine the number of QAQC, FQAQC and non-QAQC HITs that should exist.
    numAvailQaqcHits = int(round(float(availHitTarget * qaqcHitPercentage) / 100.))
    numAvailFqaqcHits = int(round(float(availHitTarget * fqaqcHitPercentage) / 100.))
    numAvailNonQaqcHits = availHitTarget - numAvailQaqcHits - numAvailFqaqcHits

    # Validate that the HITS on Mturk match the HITs recorded in the DB.
    hits = {}

    # Get serialization lock.
    mtma.getSerializationLock()

    # Get all Mturk HITs.
    mthits = mtma.getAllHits()
    for hit in mthits:
        hits[hit.HITId] = Row(status=hit.HITStatus, 
                assignments_completed=int(hit.NumberOfAssignmentsCompleted))

    # Merge in all unverified DB HITS.
    # Verified is defined as true if DB and Mturk agree HIT is deleted.
    # Note: active HITs are always unverified, 
    #       as are HITs that were deleted since the last poll cycle.
    mtma.cur.execute("""
        select hit_id, create_time, delete_time, max_assignments, kml_type
        from hit_data
        inner join kml_data using (name)
        where not hit_verified
        """)
    dbhits = mtma.cur.fetchall()
    for hit in dbhits:
        if hit[0] not in hits:
            hits[hit[0]] = Row(create_time=hit[1], delete_time=hit[2], max_assignments=hit[3], kml_type=hit[4])
        else:
            hits[hit[0]].create_time = hit[1]
            hits[hit[0]].delete_time = hit[2]
            hits[hit[0]].max_assignments = hit[3]
            hits[hit[0]].kml_type = hit[4]

    # Do the verification.
    numMturkQaqcHits = 0
    numMturkFqaqcHits = 0
    numMturkNonQaqcHits = 0
    header = False
    for hitId, row in hits.iteritems():
        #print hitId, row.status, row.assignments_completed, row.create_time, 
        #        row.delete_time, row.max_assignments, row.kml_type

        # If HIT on Mturk but not in DB: should never happen.
        if row.status and not row.create_time:
            if not header:
                k.write("\ncreateHit: datetime = %s\n" % now)
            k.write("createHit: Fatal Error: Mturk HIT '%s' not in database!\n" % hitId)
            if daemonStarted:
                if not header:
                    fatalErrorMsg += ("\r\ncreateHit: datetime = %s\r\n" % now)
                fatalErrorMsg += ("Fatal Error: Mturk HIT '%s' not in database!\r\n" % hitId)
            fatalError = True
            header = True
        # if HIT in DB but not on Mturk,
        elif not row.status and row.create_time:
            # If DB says HIT still exists: should never happen.
            if not row.delete_time:
                # Record the HIT deletion time.
                if not header:
                    k.write("\ncreateHit: datetime = %s\n" % now)
                k.write("createHit: Fatal Error: Active DB HIT '%s' not found on Mturk!\n" % hitId)
                if daemonStarted:
                    if not header:
                        fatalErrorMsg += ("\r\ncreateHit: datetime = %s\r\n" % now)
                    fatalErrorMsg += ("Fatal Error: Active DB HIT '%s' not found on Mturk!\r\n" % hitId)
                fatalError = True
                header = True
            # If DB says HIT has been deleted, then mark it as verified.
            else:
                mtma.cur.execute("""update hit_data set hit_verified = True 
                    where hit_id = '%s'""" % hitId)
        # if HIT is on Mturk and in DB,
        elif row.status and row.create_time:
            # if DB says HIT no longer exists: should never happen.
            if row.delete_time:
                if not header:
                    k.write("\ncreateHit: datetime = %s\n" % now)
                k.write("createHit: Fatal Error: Deleted DB HIT '%s' still exists on Mturk!\n" % hitId)
                if daemonStarted:
                    if not header:
                        fatalErrorMsg += ("\r\ncreateHit: datetime = %s\r\n" % now)
                    fatalErrorMsg += ("Fatal Error: Deleted DB HIT '%s' still exists on Mturk!\r\n" % hitId)
                fatalError = True
                header = True
            else:
                # Calculate the number of assignable QAQC, FQAQC, and non-QAQC HITs 
                # currently active on the MTurk server. For HITs with multiple assignments,
                # only count HITs whose number of completed assignments does not exceed
                # the configured threshold.
                if row.kml_type == MTurkMappingAfrica.KmlQAQC:
                    if row.status == 'Assignable':
                        numMturkQaqcHits = numMturkQaqcHits + 1
                elif row.kml_type == MTurkMappingAfrica.KmlFQAQC:
                    threshold = int(round(float(hitActiveAssignPercentF * row.max_assignments) / 100.))
                    if row.status == 'Assignable' and row.assignments_completed <= threshold:
                        numMturkFqaqcHits = numMturkFqaqcHits + 1
                elif row.kml_type == MTurkMappingAfrica.KmlNormal:
                    threshold = int(round(float(hitActiveAssignPercentN * row.max_assignments) / 100.))
                    if row.status == 'Assignable' and row.assignments_completed <= threshold:
                        numMturkNonQaqcHits = numMturkNonQaqcHits + 1

    # Commit any uncommitted changes
    mtma.dbcon.commit()

    # Release serialization lock.
    mtma.releaseSerializationLock()

    # Check for fatal errors found, create a ticket the first time, and exit.
    if fatalError:
        k.write("createHit: Fatal Error: create_hit_daemon will now exit!\n")
        if len(fatalErrorMsg) > 0:
            fatalErrorMsg += "Fatal Error: create_hit_daemon will now exit!\r\n"
            email(mtma, fatalErrorMsg)
        print "\nFatal Error: create_hit_daemon will now exit due to HIT validation errors."
        print "             See createHIT.log for details."
        exit(-3)

    daemonStarted = True

    # Create any needed QAQC HITs.
    kmlType = MTurkMappingAfrica.KmlQAQC
    numReqdQaqcHits = max(numAvailQaqcHits - numMturkQaqcHits, 0)
    if numReqdQaqcHits > 0:
        k.write("\ncreateHit: datetime = %s\n" % now)
        k.write("createHit: createHit sees %s QAQC HITs, and needs to create %s HITs\n" % 
            (numMturkQaqcHits, numReqdQaqcHits))

    for i in xrange(numReqdQaqcHits):
        # Retrieve the last kml gid used to create a QAQC HIT.
        curQaqcGid = mtma.getSystemData('CurQaqcGid')

        # Select the next kml for which to create a HIT. 
        # Look for all kmls of the right type whose gid is greater than the last kml chosen.
        # Exclude any kmls that currently have an active HIT on the MTurk server.
        mtma.cur.execute("""
            select name, gid, fwts 
            from kml_data k 
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
                select name, gid, fwts from kml_data k 
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
        fwts = row[2]
        mtma.setSystemData('CurQaqcGid', gid)

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

    # Create any needed FQAQC HITs.
    kmlType = MTurkMappingAfrica.KmlFQAQC
    numReqdFqaqcHits = max(numAvailFqaqcHits - numMturkFqaqcHits, 0)
    if numReqdFqaqcHits > 0:
        k.write("\ncreateHit: datetime = %s\n" % now)
        k.write("createHit: createHit sees %s FQAQC HITs, and needs to create %s HITs\n" % 
            (numMturkFqaqcHits, numReqdFqaqcHits))

    for i in xrange(numReqdFqaqcHits):
        # Select the next kml for which to create a HIT. 
        # Look for all kmls of the right type whose mapped count by a trusted worker is less than
        # the number of mappings specified by Hit_MaxAssignmentsF.
        # Exclude any kmls that currently have an active HIT on the MTurk server.
        hitMaxAssignmentsF = int(mtma.getConfiguration('Hit_MaxAssignmentsF'))
        mtma.cur.execute("""
            select name, mapped_count, fwts 
            from kml_data k 
            where not exists (select true from hit_data h 
                where h.name = k.name and delete_time is null)
            and  kml_type = '%s' 
            and post_processed = false
            and mapped_count < %s
            order by gid 
            limit 1""" % (kmlType, hitMaxAssignmentsF))
        row = mtma.cur.fetchone()
        # If we have no kmls left, all kmls in the kml_data table have been 
        # successfully processed. Notify Lyndon that more kmls are needed.
        if not row:
            if (fqaqcEmailCount % (emailFrequency / hitPollingInterval)) == 0:
                k.write("createHit: Alert: all FQAQC KMLs in kml_data table have been successfully processed. More KMLs needed to create more HITs of this type.\n")
                email(mtma, "Alert: all FQAQC KMLs in kml_data table have been successfully processed. More KMLs needed to create more HITs of this type.")
            fqaqcEmailCount += 1
            break
        else:
            if (fqaqcEmailCount % (emailFrequency / hitPollingInterval)) == 0:
                fqaqcEmailCount = 0
            else:
                fqaqcEmailCount += 1
        nextKml = row[0]
        fwts = row[2]
        remainingAssignments = hitMaxAssignmentsF - row[1]
        # Avoid the MTurk surcharge for # assignments by limiting them to hitMaxAssignmentsMT.
        limitedByMT = 0;
        if remainingAssignments > hitMaxAssignmentsMT:
            limitedByMT = remainingAssignments
            remainingAssignments = hitMaxAssignmentsMT

        # Create the FQAQC HIT
        try:
            hitId = mtma.createHit(kml=nextKml, hitType=kmlType, maxAssignments=remainingAssignments)
        except MTurkRequestError as e:
            k.write("createHit: createHit failed for KML %s:\n%s\n%s\n" %
                (nextKml, e.error_code, e.error_message))
            exit(-1)
        except AssertionError:
            k.write("createHit: Bad createHit status for KML %s:\n" % nextKml)
            exit(-2)

        # Record the HIT ID.
        mtma.cur.execute("""insert into hit_data (hit_id, name, create_time, max_assignments) 
            values ('%s', '%s', '%s', '%s')""" % (hitId, nextKml, now, remainingAssignments))
        mtma.dbcon.commit()
        k.write("createHit: Created HIT ID %s with %d assignments for FQAQC KML %s\n" % 
                (hitId, remainingAssignments, nextKml))
        if limitedByMT > 0:
            k.write("createHit: (Assignment target of %d reduced to avoid MTurk surcharge)\n" % 
                    limitedByMT)

    # Create any needed non-QAQC HITs.
    kmlType = MTurkMappingAfrica.KmlNormal
    numReqdNonQaqcHits = max(numAvailNonQaqcHits - numMturkNonQaqcHits, 0)
    if numReqdNonQaqcHits > 0:
        k.write("\ncreateHit: datetime = %s\n" % now)
        k.write("createHit: createHit sees %s non-QAQC HITs, and needs to create %s HITs\n" % 
            (numMturkNonQaqcHits, numReqdNonQaqcHits))

    for i in xrange(numReqdNonQaqcHits):
        # Select the next kml for which to create a HIT. 
        # Look for all kmls of the right type whose mapped count by a trusted worker is less than
        # the number of mappings specified by Hit_MaxAssignmentsN.
        # Exclude any kmls that currently have an active HIT on the MTurk server.
        hitMaxAssignmentsN = int(mtma.getConfiguration('Hit_MaxAssignmentsN'))
        mtma.cur.execute("""
            select name, mapped_count, fwts 
            from kml_data k 
            where not exists (select true from hit_data h 
                where h.name = k.name and delete_time is null)
            and  kml_type = '%s' 
            and post_processed = false
            and mapped_count < %s
            order by gid 
            limit 1""" % (kmlType, hitMaxAssignmentsN))
        row = mtma.cur.fetchone()
        # If we have no kmls left, all kmls in the kml_data table have been 
        # successfully processed. Notify Lyndon that more kmls are needed.
        if not row:
            if (nqaqcEmailCount % (emailFrequency / hitPollingInterval)) == 0:
                k.write("createHit: Alert: all non-QAQC KMLs in kml_data table have been successfully processed. More KMLs needed to create more HITs of this type.\n")
                email(mtma, "Alert: all non-QAQC KMLs in kml_data table have been successfully processed. More KMLs needed to create more HITs of this type.")
            nqaqcEmailCount += 1
            break
        else:
            if (nqaqcEmailCount % (emailFrequency / hitPollingInterval)) == 0:
                nqaqcEmailCount = 0
            else:
                nqaqcEmailCount += 1
        nextKml = row[0]
        fwts = row[2]
        remainingAssignments = hitMaxAssignmentsN - row[1]
        # Avoid the MTurk surcharge for # assignments by limiting them to hitMaxAssignmentsMT.
        limitedByMT = 0;
        if remainingAssignments > hitMaxAssignmentsMT:
            limitedByMT = remainingAssignments
            remainingAssignments = hitMaxAssignmentsMT

        # Create the non-QAQC HIT
        try:
            hitId = mtma.createHit(kml=nextKml, hitType=kmlType, maxAssignments=remainingAssignments)
        except MTurkRequestError as e:
            k.write("createHit: createHit failed for KML %s:\n%s\n%s\n" %
                (nextKml, e.error_code, e.error_message))
            exit(-1)
        except AssertionError:
            k.write("createHit: Bad createHit status for KML %s:\n" % nextKml)
            exit(-2)

        # Record the HIT ID.
        mtma.cur.execute("""insert into hit_data (hit_id, name, create_time, max_assignments) 
            values ('%s', '%s', '%s', '%s')""" % (hitId, nextKml, now, remainingAssignments))
        mtma.dbcon.commit()
        k.write("createHit: Created HIT ID %s with %d assignments for non-QAQC KML %s\n" % 
                (hitId, remainingAssignments, nextKml))
        if limitedByMT > 0:
            k.write("createHit: (Assignment target of %d reduced to avoid MTurk surcharge)\n" % 
                    limitedByMT)

    # Sleep for specified polling interval
    k.close()
    time.sleep(hitPollingInterval)
