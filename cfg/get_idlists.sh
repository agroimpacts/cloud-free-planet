porder idlist --input /home/rave/cloud-free-planet/cfg/paper-aois/city-smaller-utm-wgs84.geojson --cmin 0 --cmax .75 --overlap 100 --asset udm2 --filters range:view_angle:-3:3 string:ground_control:"True" --outfile /home/rave/cloud-free-planet/cfg/paper-aois/city_tile_ids_udm2.csv  --start "2018-08-01" --end "2019-06-01" --number 1000 --item "PSScene4Band"

porder idlist --input /home/rave/cloud-free-planet/cfg/paper-aois/city-smaller-utm-wgs84.geojson --cmin 0 --cmax .75 --overlap 100 --asset analytic_sr --filters range:view_angle:-3:3 string:ground_control:"True" --outfile /home/rave/cloud-free-planet/cfg/paper-aois/city_tile_ids.csv  --start "2018-08-01" --end "2019-06-01" --number 1000 --item "PSScene4Band"

porder idlist --input /home/rave/cloud-free-planet/cfg/paper-aois/ag-savanna-smaller-utm-wgs84.geojson --cmin 0 --cmax .75 --overlap 100 --asset udm2 --filters range:view_angle:-3:3 string:ground_control:"True" --outfile /home/rave/cloud-free-planet/cfg/paper-aois/ag_savanna_tile_ids_udm2.csv  --start "2018-08-01" --end "2019-06-01" --number 1000 --item "PSScene4Band"

porder idlist --input /home/rave/cloud-free-planet/cfg/paper-aois/ag-savanna-smaller-utm-wgs84.geojson --cmin 0 --cmax .75 --overlap 100 --asset analytic_sr --filters range:view_angle:-3:3 string:ground_control:"True" --outfile /home/rave/cloud-free-planet/cfg/paper-aois/ag_savanna_tile_ids.csv  --start "2018-08-01" --end "2019-06-01" --number 1000 --item "PSScene4Band"

porder idlist --input /home/rave/cloud-free-planet/cfg/paper-aois/ag-forestry-smaller-utm-wgs84.geojson --cmin 0 --cmax .75 --overlap 100 --asset udm2 --filters range:view_angle:-3:3 string:ground_control:"True" --outfile /home/rave/cloud-free-planet/cfg/paper-aois/ag_forest_tile_ids_udm2.csv  --start "2018-08-01" --end "2019-06-01" --number 1000 --item "PSScene4Band"

porder idlist --input /home/rave/cloud-free-planet/cfg/paper-aois/ag-forestry-smaller-utm-wgs84.geojson --cmin 0 --cmax .75 --overlap 100 --asset analytic_sr --filters range:view_angle:-3:3 string:ground_control:"True" --outfile /home/rave/cloud-free-planet/cfg/paper-aois/ag_forest_tile_ids.csv  --start "2018-08-01" --end "2019-06-01" --number 1000 --item "PSScene4Band"

porder idlist --input /home/rave/cloud-free-planet/cfg/paper-aois/forest-cleared-smaller-utm-wgs84.geojson --cmin 0 --cmax .75 --overlap 100 --asset udm2 --filters range:view_angle:-3:3 string:ground_control:"True" --outfile /home/rave/cloud-free-planet/cfg/paper-aois/forest_cleared_tile_ids_udm2.csv  --start "2018-08-01" --end "2019-06-01" --number 1000 --item "PSScene4Band"

porder idlist --input /home/rave/cloud-free-planet/cfg/paper-aois/forest-cleared-smaller-utm-wgs84.geojson --cmin 0 --cmax .75 --overlap 100 --asset analytic_sr --filters range:view_angle:-3:3 string:ground_control:"True" --outfile /home/rave/cloud-free-planet/cfg/paper-aois/forest_cleared_tile_ids.csv  --start "2018-08-01" --end "2019-06-01" --number 1000 --item "PSScene4Band"

porder idlist --input /home/rave/cloud-free-planet/cfg/paper-aois/water-smaller-utm-wgs84.geojson --cmin 0 --cmax .75 --overlap 100 --asset udm2 --filters range:view_angle:-3:3 string:ground_control:"True" --outfile /home/rave/cloud-free-planet/cfg/paper-aois/water_tile_ids_udm2.csv  --start "2018-08-01" --end "2019-06-01" --number 1000 --item "PSScene4Band"

porder idlist --input /home/rave/cloud-free-planet/cfg/paper-aois/water-smaller-utm-wgs84.geojson --cmin 0 --cmax .75 --overlap 100 --asset analytic_sr --filters range:view_angle:-3:3 string:ground_control:"True" --outfile /home/rave/cloud-free-planet/cfg/paper-aois/water_tile_ids.csv  --start "2018-08-01" --end "2019-06-01" --number 1000 --item "PSScene4Band"
