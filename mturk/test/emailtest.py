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
    receiver = 'lestes@princeton.edu,dmcr@princeton.edu'
    message = """From: %s
To: %s
Subject: create_hit_daemon validation problem

%s
""" % (sender, receiver, msg)

    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receiver.split(","), message)
        smtpObj.quit()
    except smtplib.SMTPException:
        print "Error: unable to send email: %s" % message

email("This is a test. Please ignore.")
