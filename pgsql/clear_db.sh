#! /bin/bash

if [ "${USER}" == "mapper" ]; then
    dbname="SouthAfrica"
elif [ "${USER}" == "sandbox" ]; then
    dbname="SouthAfricaSandbox"
else
    echo "$0 must be run as user mapper or user sandbox"
    exit 1
fi
# Delete the HIT and HIT-related data in all tables in the required order, except:
# preserve worker list and status in worker_data and qual_worker_data.
# Mark all QAQC and non-QAQC KMLs as available.
psql -U ***REMOVED*** $dbname <<EOD
delete from user_maps;
delete from error_data;
delete from assignment_data;
delete from qual_user_maps;
delete from qual_error_data;
delete from qual_assignment_data;
delete from hit_data;
update system_data set value=0 where key='CurQaqcGid';
update kml_data set mapped = false;
EOD
