#! /usr/bin/python

import sys
from datetime import datetime
import re
import email
import subprocess
import smtplib
from MTurkMappingAfrica import MTurkMappingAfrica

#Subject: SANDBOX: Regarding Amazon Mechanical Turk HIT
# 2NAVQ8H88MQUCA33NK3I4RXXGUNR80
HIT_PATTERN = r"^.+ HIT\s+(?P<hitid>[a-zA-Z0-9]+)\s*$"
HIT_RE = re.compile(HIT_PATTERN)
#---------------------------------
#Customer ID: A2X5DP7XUVYR4P
#Yet another test of a sandbox worker inquiry.
#---------------------------------
WORKER_PATTERN = r"^\s*Customer ID:\s+(?P<workerid>[a-zA-Z0-9]+)\s*$"
WORKER_RE = re.compile(WORKER_PATTERN)
DASHES_PATTERN = r"^\s*-+\s*$"
DASHES_RE = re.compile(DASHES_PATTERN)

# Email function used to create worker feedback ticket.
def send_email(mtma, sender, subject, msg = None):
    receiver = 'mappingafrica_worker_feedback@trac.princeton.edu'
    #receiver = 'dmcr@princeton.edu'
    message = """From: %s
To: %s
Subject: %s

%s
""" % (sender, receiver, subject, msg)

    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receiver.split(","), message)
        smtpObj.quit()
    except smtplib.SMTPException:
        print "Error: unable to send email: %s" % message

mtma = MTurkMappingAfrica()

logFilePath = mtma.projectRoot + "/log"
k = open(logFilePath + "/notifications.log", "a")
e = open(logFilePath + "/emails.log", "a")

now = str(datetime.today())
k.write("\nworker_inquiry: datetime = %s\n" % now)
e.write("\nworker_inquiry: datetime = %s\n" % now)

hitId = None
workerId = None
message = ''

try:
    msg = email.message_from_file(sys.stdin)
    e.write(str(msg))
    sender = msg.get('from')
    subject = msg.get('subject')
    hitId = HIT_RE.search(subject)
    hitId = str(hitId.group('hitid'))
    #print("HIT ID = '%s'" % hitId)
    for part in msg.walk():
        if part.get_content_type() != 'text/plain':
            continue

        for line in part.get_payload(decode=True).split('\n'):
            # Search for MTurk Worker ID
            widl = WORKER_RE.search(line)
            # Search for dashed line
            dl = DASHES_RE.search(line)

            if widl:
                    workerId = str(widl.group('workerid'))
                    #print("Worker ID = '%s'" % workerId)
            elif workerId:
                if not dl:
                    message += line.rstrip('=')
                else:
                    #print("Worker message: '%s'" % message)
                    break
    msgOK = True
except:
    msgOK = False

k.write("worker_inquiry: Email message parsed: %s\n" % msgOK)

if msgOK:
    url = subprocess.Popen(["Rscript", "%s/R/CheckWorkerAssignment.R" % mtma.projectRoot, hitId, workerId, "N"], 
        stdout=subprocess.PIPE).communicate()[0]
    url = url.rstrip()
    k.write("worker_inquiry: HIT ID: %s\n" % hitId)
    k.write("worker_inquiry: Worker ID: %s\n" % workerId)
    k.write("worker_inquiry: Map URL: %s\n" % url)
    k.write("worker_inquiry: Worker message: %s\n" % message)
    send_email(mtma, sender, subject, """HIT ID: %s
Worker ID: %s
Map URL: %s

Worker's message:\n%s
""" % (hitId, workerId, url, message))

now = str(datetime.today())
k.write("worker_inquiry: processing completed = %s\n" % now)
e.write("worker_inquiry: processing completed = %s\n" % now)

k.close()
e.close()

# Destroy mtma object.
del mtma
