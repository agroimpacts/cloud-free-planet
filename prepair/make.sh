#! /bin/bash -x

make clean

export LD_LIBRARY_PATH="/usr/pgsql-9.4/lib"
cmake .
make
