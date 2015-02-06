#! /bin/bash -x

make clean

export LD_LIBRARY_PATH="/usr/local/lib:/usr/lib64:/usr/pgsql-9.1/lib"
cmake .
make
