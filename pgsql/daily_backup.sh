#! /bin/bash

# Child scripts are in the same directory
SDIR=`dirname $0`

# Assumes we were called with '/u/${USER}/afmap/pgsql/<script_name>'.
IFS='/'
array=($0)
user=${array[2]}
IFS=' '

if [ "$user" == "mapper" ]; then
    dbname="Africa"
elif [ "$user" == "sandbox" ]; then
    dbname="AfricaSandbox"
else
    echo "$0 must be run using /u/mapper or /u/sandbox path"
    exit 1
fi
$SDIR/dump_schema.sh $dbname
$SDIR/dump_data.sh $dbname
