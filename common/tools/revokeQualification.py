#! /usr/bin/python

from MappingCommon import MappingCommon
from datetime import datetime

mapc = MappingCommon()

email = raw_input("Please enter a login email address: ")
workerId = mapc.querySingleValue("select id from users where email = '%s'" % email)
if workerId is None:
    print "Invalid email address."
    exit(1)

now = str(datetime.today())

mapc.revokeQualification(workerId, now)
print("Mapping Africa Qualification revoked from worker %s (%s)" % (workerId, email))
