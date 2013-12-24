#! /bin/bash -x

make -f Makefile.linux.new clean

export LD_LIBRARY_PATH="/usr/pgsql-9.1/lib"
if [ "$1" != "-d" ]; then
    make -f Makefile.linux.new
else
    make -f Makefile.linux.new OPTFLAGS="-g -O0"
fi

