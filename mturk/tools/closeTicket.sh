#!/bin/bash

NOW=`/bin/date '+%m/%d/%Y %H:%M:%S'`

TICKETS=$1
if [ -z "$TICKETS" ]; then
    echo "Usage: $0 <<Trac_ticket_#>-<Trac_ticket_#> <Resolution> <Optional_comment>"
    echo "Trac_ticket_#: Individual ticket or entire range of tickets must exist or"
    echo "               new ticket will be created for any missing ticket(s)"
    echo "Resolution: fixed, invalid, wontfix, duplicate, worksforme, notaproblem"
    echo "Optional_comment: If present, must be quote-delimited"
    exit 1
fi
RESOLUTION=$2
if [ -z "$RESOLUTION" ]; then
    echo "Usage: $0 <<Trac_ticket_#>-<Trac_ticket_#> <Resolution> <Optional_comment>"
    echo "Trac_ticket_#: Individual ticket or entire range of tickets must exist or"
    echo "               new ticket will be created for any missing ticket(s)"
    echo "Resolution: fixed, invalid, wontfix, duplicate, worksforme, notaproblem"
    echo "Optional_comment: If present, must be quote-delimited"
    exit 1
fi
COMMENT=$3
if [ -z "$COMMENT" ]; then
    COMMENT="Automatically closed by $0 at $NOW."
fi

IFS=- read -r TFIRST TLAST <<< "$TICKETS"
if [ -z "$TLAST" ]; then
    TLAST=$TFIRST
fi

# This email address has been configured on trac.princeton.edu in
# /etc/aliases and /usr/local/etc/email2trac.conf to create or 
# update a ticket.
TO="mappingafrica@trac.princeton.edu"
#TO="dmcr@princeton.edu"

# Utility functions
email() {
    /bin/mail -s "$SUBJECT" "$TO" << EOEMAIL
$emailBody
EOEMAIL
}

for TICKET in $(seq $TFIRST $TLAST); do
    echo "$NOW: Closing ticket #$TICKET"
    SUBJECT="RE: [mappingafrica] #$TICKET:"
    emailBody=`/bin/cat <<EOF
@status: closed
@resolution: $RESOLUTION

$COMMENT
EOF`
    email
done
