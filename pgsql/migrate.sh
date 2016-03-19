#! /bin/bash -x

if [ "${USER}" != "mapper" ]; then
    echo "$0 must be run as user mapper"
    exit 1
fi
SDB=AfricaSandbox
DDB=Africa

# Script directory.
SDIR=`dirname $0`

# Make DB user ***REMOVED*** into a superuser temporarily.
psql -f $SDIR/role_alter_su.sql -U postgres postgres
if [[ $? != 0 ]]; then
    exit 1
fi

# Backup the sandbox and production DBs.
pg_dump -Fc -f $SDIR/migration/$SDB.pgdump -U ***REMOVED*** $SDB
if [[ $? != 0 ]]; then
    exit 1
fi
pg_dump -Fc -f $SDIR/migration/$DDB.pgdump -U ***REMOVED*** $DDB
if [[ $? != 0 ]]; then
    exit 1
fi

# Recreate the production DB.
psql -U ***REMOVED*** $SDB <<EOD
drop database "$DDB";
create database "$DDB";
EOD
if [[ $? != 0 ]]; then
    exit 1
fi

# Restore the AfricaSandbox DB as the Africa DB.
pg_restore -d "$DDB" -U ***REMOVED*** $SDIR/migration/$SDB.pgdump
if [[ $? != 0 ]]; then
    exit 1
fi

# Edit the new Africa database in preparation for starting up a production run.
# This includes clearing out some GIS tables that will be repopulated by KMLgenerate.R .
$SDIR/clear_db.sh
if [[ $? != 0 ]]; then
    exit 1
fi

# Import the worker_data and qual_worker_data rows from the most recent Africa DB backup.
pg_restore --data-only -t worker_data -f $SDIR/migration/${DDB}_worker_data.sql $SDIR/migration/$DDB.pgdump
if [[ $? != 0 ]]; then
    exit 1
fi
pg_restore --data-only -t qual_worker_data -f $SDIR/migration/${DDB}_qual_worker_data.sql $SDIR/migration/$DDB.pgdump
if [[ $? != 0 ]]; then
    exit 1
fi
psql -U ***REMOVED*** $DDB <<EOD
delete from qual_worker_data;
delete from worker_data;
\i $SDIR/migration/${DDB}_worker_data.sql
\i $SDIR/migration/${DDB}_qual_worker_data.sql
EOD
if [[ $? != 0 ]]; then
    exit 1
fi

# Revoke superuser role from DB user ***REMOVED***.
psql -f $SDIR/role_normal.sql -U postgres postgres
if [[ $? != 0 ]]; then
    exit 1
fi

echo
echo "DB migration complete!"
