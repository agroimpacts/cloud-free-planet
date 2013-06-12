#! /bin/bash

psql -U ***REMOVED*** SouthAfrica <<EOD
delete from user_maps;
delete from error_data;
delete from assignment_data;
delete from worker_data;
delete from hit_data;
delete from kml_data;
EOD
