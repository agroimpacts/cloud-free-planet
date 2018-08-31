#! /bin/bash

if [ "${USER}" != "mapper" ]; then
    echo "$0 must be run as user mapper"
    exit 1
fi
echo "Do you want to migrate the AfricaSandbox DB to the Africa DB and initialize it?"
select yn in "No" "Yes"; do
    case $yn in
        No ) exit;;
        Yes ) break;;
    esac
done
read -s -p "Enter postgres password: " postgres_pw
echo
read -s -p "Enter ***REMOVED*** password: " ***REMOVED***_pw
echo

SDB=AfricaSandbox
DDB=Africa

# Script directory.
SDIR=`dirname $0`

#if false; then
# Make DB user ***REMOVED*** into a superuser temporarily.
PGPASSWORD=$postgres_pw psql -f $SDIR/role_alter_su.sql -U postgres postgres
if [[ $? != 0 ]]; then
    exit 1
fi

# Backup the sandbox and production DBs.
echo "About to backup $SDB database to $SDB.pgdump. This could take some time..."
PGPASSWORD=$***REMOVED***_pw pg_dump -Fc -f $SDIR/migration/$SDB.pgdump -U ***REMOVED*** $SDB
if [[ $? != 0 ]]; then
    exit 1
fi
echo "About to backup $DDB database to $DDB.pgdump. This could take some time..."
PGPASSWORD=$***REMOVED***_pw pg_dump -Fc -f $SDIR/migration/$DDB.pgdump -U ***REMOVED*** $DDB
if [[ $? != 0 ]]; then
    exit 1
fi

# Recreate the production DB.
PGPASSWORD=$***REMOVED***_pw psql -U ***REMOVED*** $SDB <<EOD
drop database "$DDB";
create database "$DDB";
EOD
if [[ $? != 0 ]]; then
    exit 1
fi

# Restore the AfricaSandbox DB as the Africa DB.
echo "About to restore $SDB.pgdump to $DDB database. This could take some time..."
PGPASSWORD=$***REMOVED***_pw pg_restore -d "$DDB" -U ***REMOVED*** $SDIR/migration/$SDB.pgdump
if [[ $? != 0 ]]; then
    exit 1
fi

# Edit the new Africa database in preparation for starting up a production run.
# This includes clearing out some GIS tables that will be repopulated below and in production.
$SDIR/clear_db.sh $***REMOVED***_pw
if [[ $? != 0 ]]; then
    exit 1
fi

# Import the worker_data, qual_worker_data, roles, user_invites, users, users_roles,
# incoming_names, and iteration_metrics from the most recent Africa DB backup.
pg_restore --data-only -t worker_data -f $SDIR/migration/${DDB}_worker_data.sql $SDIR/migration/$DDB.pgdump
if [[ $? != 0 ]]; then
    exit 1
fi
pg_restore --data-only -t roles -f $SDIR/migration/${DDB}_roles.sql $SDIR/migration/$DDB.pgdump
if [[ $? != 0 ]]; then
    exit 1
fi
pg_restore --data-only -t user_invites -f $SDIR/migration/${DDB}_user_invites.sql $SDIR/migration/$DDB.pgdump
if [[ $? != 0 ]]; then
    exit 1
fi
pg_restore --data-only -t users -f $SDIR/migration/${DDB}_users.sql $SDIR/migration/$DDB.pgdump
if [[ $? != 0 ]]; then
    exit 1
fi
pg_restore --data-only -t users_roles -f $SDIR/migration/${DDB}_users_roles.sql $SDIR/migration/$DDB.pgdump
if [[ $? != 0 ]]; then
    exit 1
fi
pg_restore --data-only -t incoming_names -f $SDIR/migration/${DDB}_incoming_names.sql $SDIR/migration/$DDB.pgdump
if [[ $? != 0 ]]; then
    exit 1
fi
pg_restore --data-only -t iteration_metrics -f $SDIR/migration/${DDB}_iteration_metrics.sql $SDIR/migration/$DDB.pgdump
if [[ $? != 0 ]]; then
    exit 1
fi
#fi
PGPASSWORD=$***REMOVED***_pw psql -U ***REMOVED*** $DDB <<EOD
delete from worker_data;
delete from user_invites;
delete from users_roles;
delete from users;
delete from roles;
delete from incoming_names;
delete from iteration_metrics;
\i $SDIR/migration/${DDB}_roles.sql
\i $SDIR/migration/${DDB}_users.sql
\i $SDIR/migration/${DDB}_users_roles.sql
\i $SDIR/migration/${DDB}_user_invites.sql
\i $SDIR/migration/${DDB}_worker_data.sql
\i $SDIR/migration/${DDB}_iteration_metrics.sql
\i $SDIR/migration/${DDB}_incoming_names.sql

update system_data set value = (select coalesce(max(iteration), 0) from iteration_metrics) where key = 'IterationCounter'
EOD
if [[ $? != 0 ]]; then
    exit 1
fi

# Update the configuration parameters with the production values.
PGPASSWORD=$***REMOVED***_pw psql -f $SDIR/updateConfiguration.sql -U ***REMOVED*** $DDB
if [[ $? != 0 ]]; then
    exit 1
fi

# Revoke superuser role from DB user ***REMOVED***.
PGPASSWORD=$postgres_pw psql -f $SDIR/role_normal.sql -U postgres postgres
if [[ $? != 0 ]]; then
    exit 1
fi

echo
echo "DB migration complete!"
