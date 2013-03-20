#! /bin/bash
# Script to find out postfix's uid.
# 1) Copy this file /tmp so postfix will have permission to execute it.
# 2) Change /etc/aliases to have a line like this:
#    test_email: "| /tmp/processmail_test.sh"
# 3) Run newaliases
# 4) Send email to test_email@<this_server>.princeton.edu

id >/tmp/id.test
