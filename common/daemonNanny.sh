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
if [ ! -x "$COMMAND" ]; then
    echo "`date`: $COMMAND does not exist or is not executable"
    exit 2
fi

# Notification skip count: set this to the number of crontab intervals to skip
# before reporting the same notification again. E.g., setting notifSkipCount to 12
# would imply that identical notifications would be generated only once an hour
# assuming 5-minute crontab check intervals.
NotifSkipCount=144          # 12 hours

AFMAP_HOME=`dirname $0`/..
PROGRAM=`basename $COMMAND`
BASEPROGRAM=${PROGRAM%.*}
PIDFILE=${AFMAP_HOME}/log/${BASEPROGRAM}.pid
LOGFILE=${AFMAP_HOME}/log/${BASEPROGRAM}.oe.log
VARFILE=${AFMAP_HOME}/log/${BASEPROGRAM}.var

NOW=`/bin/date '+%m/%d/%Y %H:%M:%S'`

# This email address has been configured on trac.princeton.edu in
# /etc/aliases and /usr/local/etc/email2trac.conf to create a ticket
# under the Internal Alert component.
TO="lestes@clarku.edu,dmcr@princeton.edu"

# Utility functions
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

# Retrieve the variable values:
# varArray[0]: 'failed to restart' count
# varArray[1]: 'restarted' count
# varArray[2]: 'already running' count
#
if [ -e $VARFILE ]; then
    varArray=(`cat $VARFILE`)
else
    varArray=(0 0 0)
fi


# Main path starts here
checkrestart
if [ $restart == 1 ]; then
    nohup $COMMAND >>$LOGFILE 2>&1 &
    echo $! >$PIDFILE
    sleep 20
    checkrestart
    if [ $restart == 1 ]; then
        if [[ ${varArray[0]} == 0 ]]; then
            varArray[1]=0
            varArray[2]=0
            echo "`date`: Failed to restart $PROGRAM"
            SUBJECT="Daemon nanny has failed to restart a daemon"
            emailBody=`/bin/cat <<EOF
$SUBJECT

Daemon $PROGRAM failed to restart at $NOW.
Please check $LOGFILE for details.
EOF`
            email
        fi
        let varArray[0]=${varArray[0]}+1
        if [[ ${varArray[0]} -ge $NotifSkipCount ]]; then
            varArray[0]=0
        fi
    else
        if [[ ${varArray[1]} == 0 ]]; then
            varArray[0]=0
            varArray[2]=0
            echo "`date`: $PROGRAM restarted"
            SUBJECT="Daemon nanny has restarted a daemon"
            emailBody=`/bin/cat <<EOF
$SUBJECT

Daemon $PROGRAM restarted at $NOW.
Please check $LOGFILE for details.
EOF`
            email
        fi
        let varArray[1]=${varArray[1]}+1
        if [[ ${varArray[1]} -ge $NotifSkipCount ]]; then
            varArray[1]=0
        fi
    fi
else
    if [[ ${varArray[2]} == 0 ]]; then
        varArray[0]=0
        varArray[1]=0
        echo "`date`: $PROGRAM already running"
    fi
    let varArray[2]=${varArray[2]}+1
    if [[ ${varArray[2]} -ge $NotifSkipCount ]]; then
        varArray[2]=0
    fi
fi
echo ${varArray[@]} >$VARFILE