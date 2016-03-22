#! /bin/bash

if [ "${USER}" == "mapper" ]; then
    dbname="Africa"
elif [ "${USER}" == "sandbox" ]; then
    dbname="AfricaSandbox"
else
    echo "$0 must be run as user mapper or user sandbox"
    exit 1
fi
if [[ "$1" != "Yes" ]]; then
    echo "Do you really want to initialize the $dbname DB for restart or migration purposes?"
    select yn in "No" "Yes"; do
        case $yn in
            No ) exit;;
            Yes ) break;;
        esac
    done
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

delete from f_select;
delete from fqaqc_sites;
delete from master_grid;
delete from master_grid_counter;
delete from n_select;

delete from kml_data;
insert into kml_data select * from kml_data_static;

update system_data set value=0 where key='CurQaqcGid';

EOD

# Initialize the kmls directory with the startup set of I and Q kml files.
rm -rf /u/${USER}/afmap/kmls/*
cp -p /u/${USER}/afmap/kmls_static/* /u/${USER}/afmap/kmls
