#!/bin/bash
#
# daemonNanny - make sure specified daemon is running
#               Intended to be run from cron
#
PROGRAM=$1
if [ -z "$PROGRAM" ]; then
    echo "`date`: Usage: $0 <daemon_name>"
    exit 1
fi
AFMAP_HOME=`dirname $0`/..
PIDFILE=${AFMAP_HOME}/log/${PROGRAM}.pid
COMMAND=${AFMAP_HOME}/mturk/${PROGRAM}.py
LOGFILE=${AFMAP_HOME}/log/${PROGRAM}.log

if [ ! -x "$COMMAND" ]; then
    echo "`date`: $COMMAND does not exist or is not executable"
    exit 2
fi

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
        sleep 5
        checkrestart
        if [ $restart == 1 ]; then
             echo "`date`: Failed to restart $PROGRAM"
             exit 2
        else
             echo "`date`: $PROGRAM restarted"
        fi
else
        echo "`date`: $PROGRAM already running"
fi

