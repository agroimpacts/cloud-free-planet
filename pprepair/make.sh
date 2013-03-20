#! /bin/bash -x

export LD_LIBRARY_PATH="/usr/pgsql-9.1/lib"
make -f Makefile.linux
