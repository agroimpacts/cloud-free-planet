#! /bin/bash

if [ "${USER}" == "mapper" ]; then
    dbname="SouthAfrica"
elif [ "${USER}" == "sandbox" ]; then
    dbname="SouthAfricaSandbox"
else
    echo "$0 must be run as user mapper or user sandbox"
    exit 1
fi
psql -U ***REMOVED*** $dbname <<EOD
delete from user_maps;
delete from error_data;
delete from assignment_data;
delete from worker_data;
delete from hit_data;
EOD
