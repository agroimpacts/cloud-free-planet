#! /bin/bash

SDIR=/var/www/html/afmap/pgsql

$SDIR/dump_schema.sh SouthAfrica
$SDIR/dump_data.sh SouthAfrica
