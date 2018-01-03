#! /bin/bash
  
echo "Ensure that pg_hba.conf will allow user '***REMOVED***' to connect to DB 'postgres'."
read -n1 -r -p "Press any key to continue..." key

read -p "Name of new database to create and restore into: " db
read -p "Path of pgdump file to restore from: " dump
if [[ "$db" == "" || "$dump" == "" ]]; then
    echo "You must specify both a DB name and a dump filename."
    exit 1
fi

# Script directory.
SDIR=`dirname $0`

# Make DB user ***REMOVED*** into a superuser temporarily.
psql -f $SDIR/role_alter_su.sql -U postgres postgres
if [[ $? != 0 ]]; then
    exit 1
fi

psql -U ***REMOVED*** postgres <<EOD
drop database "$db";
create database "$db";
EOD

echo "Enter ***REMOVED*** password at the next prompt."
pg_restore -d "$db" -U ***REMOVED*** $dump

# Revoke superuser role from DB user ***REMOVED***.
psql -f $SDIR/role_normal.sql -U postgres postgres
if [[ $? != 0 ]]; then
    exit 1
fi

echo "Done! You will need to edit postgresql's pg_hba.conf to support the new DB name,"
echo "copy it back to the .../pgsql directory, and restart the postgresql server,"
echo "as described in the .../pgsql/README file."
