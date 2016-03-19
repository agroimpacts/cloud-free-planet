#! /bin/bash

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

psql -U ***REMOVED*** Africa <<EOD
drop database "$db";
create database "$db";
EOD

pg_restore -d "$db" -U ***REMOVED*** $dump

# Revoke superuser role from DB user ***REMOVED***.
psql -f $SDIR/role_normal.sql -U postgres postgres
if [[ $? != 0 ]]; then
    exit 1
fi

echo "Done! You will need to edit pg_hba.conf in the pgsql directory to support"
echo "the new database name, copy it to the postgresql data directory, and restart"
echo "the postgresql server, as described in the .../pgsql/README file."
