#! /bin/bash

# Child scripts are in the same directory
SDIR=`dirname $0`
DATADIR=$SDIR/data

# Assumes we were called with '/home/${USER}/afmap/pgsql/<script_name>'.
IFS='/'
array=($0)
user=${array[2]}
IFS=' '

if [ "$user" == "mapper" ]; then
    dbname="Africa"
elif [ "$user" == "sandbox" ]; then
    dbname="AfricaSandbox"
else
    echo "$0 must be run using /home/mapper or /home/sandbox path"
    exit 1
fi
if [ -f $DATADIR/$dbname.pgdump.2 ]; then
        mv $DATADIR/$dbname.pgdump.2 $DATADIR/$dbname.pgdump.3
fi
if [ -f $DATADIR/$dbname.pgdump.1 ]; then
        mv $DATADIR/$dbname.pgdump.1 $DATADIR/$dbname.pgdump.2
fi
if [ -f $DATADIR/$dbname.pgdump ]; then
        mv $DATADIR/$dbname.pgdump $DATADIR/$dbname.pgdump.1
fi
pg_dump -Fc -f $DATADIR/$dbname.pgdump -U postgres $dbname
