#! /bin/bash -x

umask 022
chmod o+r boto/cacerts/cacerts.txt
python setup.py install
