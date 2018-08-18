#! /usr/bin/python

# This script is called by scripts running under crontab, and that environment 
# does not have PYHTHONPATH defined, so we need to add it to sys.path here.

import sys
import os
home = os.environ['HOME']
sys.path.append("%s/mapper/common" % home)

from MappingCommon import MappingCommon

if  not (len(sys.argv) == 3):
    print "Usage: %s <issue_title> <issue_description>" % sys.argv[0]
    sys.exit(1)

title = sys.argv[1]
desc = sys.argv[2]

mapc = MappingCommon()
mapc.createAlertIssue(title, desc)
