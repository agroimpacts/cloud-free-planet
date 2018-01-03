#! /bin/bash -x

make -f Makefile.linux.new clean

#export LD_LIBRARY_PATH="/usr/pgsql-9.4/lib:/usr/local/lib"
PGSQLPATH="/usr/pgsql-9.4/lib"
#GDALPATH="/usr/local/lib"
cmake .
if [ "$1" != "-d" ]; then
    make -f Makefile.linux.new PGSQLPATH=${PGSQLPATH} GDALPATH=${GDALPATH}
else
    make -f Makefile.linux.new PGSQLPATH=${PGSQLPATH} GDALPATH=${GDALPATH} OPTFLAGS="-g -O0"
fi

