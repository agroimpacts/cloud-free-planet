#! /bin/bash

if [ "${USER}" == "mapper" ]; then
    dbname="SouthAfrica"
elif [ "${USER}" == "sandbox" ]; then
    dbname="SouthAfricaSandbox"
else
    echo "$0 must be run as user mapper or user sandbox"
    exit 1
fi
psql -U ***REMOVED*** $dbname </u/${USER}/afmap/pgsql/update_newqaqc_sites_fields.sql
