#! /bin/bash -x

make -f Makefile.linux clean

export LD_LIBRARY_PATH="/usr/pgsql-9.1/lib"
if [ "$1" != "-d" ]; then
    make -f Makefile.linux
else
    make -f Makefile.linux OPTFLAGS="-g -O0"
fi

