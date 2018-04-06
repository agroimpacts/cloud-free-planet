#!/bin/bash
#
# List and kill daemons used in running Mapping Africa
# 

# check if crontab is running. Exit if it is
croncheck=`crontab -l`
if [ -n "$croncheck" ]; then 
   echo "ERROR: crontab is running."
   echo "       Do not kill daemons unless you first stop crontab."
   echo "       Run 'crontab -r' first"
   exit 1 
fi

AFMAP_HOME=`basename $HOME`
CREATEHIT=`pgrep -f /home/${AFMAP_HOME}*.*create_hit_daemon.py`
CLEANUP=`pgrep -f /home/${AFMAP_HOME}*.*cleanup_absent_worker.py`
KMLGENERATE=`pgrep -f /home/${AFMAP_HOME}*.*KMLgenerate.R`

if [ -n "$CREATEHIT" ]; then
    echo "create_hit_daemon.py PID on $AFMAP_HOME: $CREATEHIT"
    echo "kill $CREATEHIT"
    kill $CREATEHIT
else
    echo "create_hit_daemon.py not running"
fi
if [ -n "$CLEANUP" ]; then
    echo "cleanup_absent_worker.py PID on $AFMAP_HOME: $CLEANUP"
    echo "kill $CLEANUP"
    kill $CLEANUP
else
    echo "cleanup_absent_worker.py not running"
fi
if [ -n "$KMLGENERATE" ]; then
    echo "KMLgenerate.R PID on $AFMAP_HOME: $KMLGENERATE"
    echo "kill $KMLGENERATE"
    kill $KMLGENERATE
else
    echo "KMLgenerate.R not running"
fi



