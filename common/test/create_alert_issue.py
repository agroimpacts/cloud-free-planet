#! /usr/bin/python

import sys
sys.path.append("..")  # search one directory up
from MappingCommon import MappingCommon

if  not (len(sys.argv) == 3):
    print "Usage: %s <issue_title> <issue_description>" % sys.argv[0]
    sys.exit(1)

title = sys.argv[1]
desc = sys.argv[2]

mapc = MappingCommon()
mapc.createAlertIssue(title, desc)
