#! /bin/bash

if [ "${USER}" == "mapper" ]; then
    dbname="Africa"
elif [ "${USER}" == "sandbox" ]; then
    dbname="AfricaSandbox"
else
    echo "$0 must be run as user mapper or user sandbox"
    exit 1
fi
if [[ -z "$1" ]]; then
    echo "Do you really want to initialize the $dbname DB for restart or migration purposes?"
    echo "WARNING: Do not run unless the crontab has been removed and ALL daemons have been killed!"
    select yn in "No" "Yes"; do
        case $yn in
            No ) exit;;
            Yes ) break;;
        esac
    done
    read -s -p "Enter ***REMOVED*** password: " ***REMOVED***_pw
    echo
else
    ***REMOVED***_pw=$1
fi

# Delete the HIT and HIT-related data in all tables in the required order, except:
# preserve worker list and status in worker_data and qual_worker_data.
# Mark all QAQC and non-QAQC KMLs as available.
PGPASSWORD=$***REMOVED***_pw psql -U ***REMOVED*** $dbname <<EOD
delete from user_maps;
delete from accuracy_data;
delete from assignment_history;
delete from assignment_data;
delete from qual_user_maps;
delete from qual_accuracy_data;
delete from qual_assignment_data;
delete from hit_data;

delete from kml_data;
alter sequence kml_data_gid_seq restart;
insert into kml_data (kml_type, name, hint) select kml_type, name, hint from kml_data_static order by gid;

update system_data set value=0 where key='CurQaqcGid';
update system_data set value=1 where key='firstAvailLine';
EOD
