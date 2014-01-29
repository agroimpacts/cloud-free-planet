#! /usr/bin/python

import sys
from datetime import datetime
from ProcessNotifications import ParseEmailNotification, ProcessNotifications
from MTurkMappingAfrica import MTurkMappingAfrica

notiftime = str(datetime.today())
mtma = MTurkMappingAfrica()

# Get serialization lock.
mtma.getSerializationLock()

logFilePath = mtma.projectRoot + "/log"
k = open(logFilePath + "/notifications.log", "a")

now = str(datetime.today())
k.write("\ngetnotifications: datetime = %s\n" % now)
k.write("getnotifications: notification arrived = %s\n" % notiftime)

try:
    emailNotification = ParseEmailNotification(sys.stdin)
    msgOK = True
except:
    msgOK = False

k.write("getnotifications: Email message parsed: %s\n" % msgOK)

if msgOK:
    ProcessNotifications(mtma, k, emailNotification.notifMsg)

now = str(datetime.today())
k.write("getnotifications: processing completed = %s\n" % now)

k.close()

# Commit any uncommitted changes
mtma.dbcon.commit()

# Release serialization lock.
mtma.releaseSerializationLock()

# Destroy mtma object.
del mtma
