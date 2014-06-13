#!/bin/bash
#
# daemonNanny - make sure specified daemon is running.
#               Intended to be run from cron.
#
COMMAND=$1
if [ -z "$COMMAND" ]; then
    echo "`date`: Usage: $0 <full_daemon_path>"
    exit 1
fi
AFMAP_HOME=`dirname $0`/..
PROGRAM=`basename $COMMAND`
BASEPROGRAM=${PROGRAM%.*}
PIDFILE=${AFMAP_HOME}/log/${BASEPROGRAM}.pid
LOGFILE=${AFMAP_HOME}/log/${BASEPROGRAM}.oe.log

NOW=`/bin/date '+%m/%d/%Y %H:%M:%S'`
TO="mappingafrica_internal_alert@trac.princeton.edu"
#TO="dmcr@princeton.edu"

if [ ! -x "$COMMAND" ]; then
    echo "`date`: $COMMAND does not exist or is not executable"
    exit 2
fi

# Utility function
email() {
    /bin/mail -s "$SUBJECT" "$TO" << EOEMAIL
$emailBody
EOEMAIL
}

checkrestart() {
        restart=0
        if [ -e $PIDFILE ]; then
            PID=`cat $PIDFILE`
            ps $PID > /dev/null 2>&1
            restart=$?
        else
            restart=1
        fi
}

checkrestart
if [ $restart == 1 ]; then
        nohup $COMMAND >>$LOGFILE 2>&1 &
        sleep 15
        checkrestart
        if [ $restart == 1 ]; then
            echo "`date`: Failed to restart $PROGRAM"
            SUBJECT="Daemon nanny has failed to restart a daemon"
            emailBody=`/bin/cat <<EOF
$SUBJECT

Daemon $PROGRAM failed to restart at $NOW.
Please check $LOGFILE for details.
EOF`
            email
            exit 2
        else
            echo "`date`: $PROGRAM restarted"
            SUBJECT="Daemon nanny has restarted a daemon"
            emailBody=`/bin/cat <<EOF
$SUBJECT

Daemon $PROGRAM restarted at $NOW.
Please check $LOGFILE for details.
EOF`
            email
        fi
else
        echo "`date`: $PROGRAM already running"
fi

