#! /usr/bin/python

import sys
from datetime import datetime
from ProcessNotifications import ParseEmailNotification, ProcessNotifications
from MTurkMappingAfrica import MTurkMappingAfrica

now = str(datetime.today())

mtma = MTurkMappingAfrica()
logFilePath = mtma.projectRoot + "/log"
k = open(logFilePath + "/notifications.log", "a")

# Get serialization lock.
mtma.getSerializationLock()

k.write("\ngetnotifications: datetime = %s\n" % now)

try:
    emailNotification = ParseEmailNotification(sys.stdin)
    msgOK = True
except:
    msgOK = False

k.write("getnotifications: Email message parsed: %s\n" % msgOK)

if msgOK:
    ProcessNotifications(mtma, k, emailNotification.notifMsg)

# Release serialization lock.
mtma.dbcon.commit()
# Destroy mtma object.
del mtma
k.close()
