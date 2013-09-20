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
delete from qual_user_maps;
delete from qual_error_data;
delete from qual_assignment_data;
delete from qual_worker_data;
update system_data set value=0 where key='Qual_MappingAfricaId';
update system_data set value=0 where key='CurNonQaqcGid';
update system_data set value=0 where key='CurQaqcGid';
update system_data set value=0 where key='SumPendingNonQaqcs';
update system_data set value=0 where key='NumQaqcs';
update system_data set value=0 where key='AvgPendingNonQaqcs';
EOD
