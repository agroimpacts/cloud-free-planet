#! /usr/bin/python

import os
import time
from datetime import datetime
from boto.mturk.connection import MTurkRequestError
from MTurkMappingAfrica import MTurkMappingAfrica

mtma = MTurkMappingAfrica()

mtma.cur.execute("select value from configuration where key = 'ProjectRoot'")
logFilePath = mtma.cur.fetchone()[0] + "/log"
k = open(logFilePath + "/createHit.log", "a")

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

    k = open(logFilePath + "/createHit.log", "a")
    now = str(datetime.today())

    # Determine the number of QAQC and non-QAQC HITs to create.
    numAvailQaqcHits = int(round(float(availHitTarget * qaqcHitPercentage) / 100.))
    numAvailNonQaqcHits = availHitTarget - numAvailQaqcHits

    # Calculate the number of QAQC HITs currently active on the MTurk server.
    kmlType = 'Q'
    mtma.cur.execute("""
        select count(*) from kml_data k 
        where exists (select true from hit_data h 
            where h.name = k.name and delete_time is null)
        and kml_type = '%s' 
        """ % kmlType)

    numMturkQaqcHits = int(mtma.cur.fetchone()[0])
    numReqdQaqcHits = max(numAvailQaqcHits - numMturkQaqcHits, 0)
    if numReqdQaqcHits > 0:
        k.write("\ncreateHit: datetime = %s\n" % now)
        k.write("createHit: createHit sees %s HITs, and needs to create %s HITs\n" % 
            (numMturkQaqcHits, numReqdQaqcHits))

    for i in xrange(numReqdQaqcHits):

        # Get next KML of the right type that is not current a HIT.
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

        # Create the HIT
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
        k.write("createHit: Created HIT ID %s for KML %s\n" % (hitId, nextKml))

    # Sleep for specified polling interval
    k.close()
    time.sleep(hitPollingInterval)
