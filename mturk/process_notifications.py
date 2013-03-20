#! /usr/bin/python

import sys
from datetime import datetime
from webob import Request, Response
from ProcessNotifications import ParseEmailNotification, ProcessNotifications
from MTurkMappingAfrica import MTurkMappingAfrica

now = str(datetime.today())

mtma = MTurkMappingAfrica()
mtma.cur.execute("select value from configuration where key = 'ProjectRoot'")
logFilePath = mtma.cur.fetchone()[0] + "/log"
mtma.close()
k = open(logFilePath + "/notifications.log", "a")
k.write("\ngetnotifications: datetime = %s\n" % now)

try:
    emailNotification = ParseEmailNotification(sys.stdin)
    msgOK = True
except:
    msgOK = False

k.write("getnotifications: Email message parsed: %s\n" % msgOK)
k.close()

if msgOK:
    ProcessNotifications(emailNotification.notifMsg)
