#! /bin/bash
nohup /var/www/html/afmap/mturk/create_hit_daemon.py >/var/www/html/afmap/log/daemon.log 2>&1 &
