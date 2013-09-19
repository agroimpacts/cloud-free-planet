#! /bin/bash

# Child scripts are in the same directory
SDIR=`dirname $0`

# Assumes we were called with '/u/${USER}/afmap/pgsql/<script_name'.
IFS='/'
array=($0)
user=${array[2]}

if [ "$user" == "mapper" ]; then
    dbname="SouthAfrica"
elif [ "$user" == "sandbox" ]; then
    dbname="SouthAfricaSandbox"
else
    exit 1
fi
$SDIR/dump_schema.sh $dbname
$SDIR/dump_data.sh $dbname
