[Back to README](../README.md)

# mapper's database

`mapper` connects to a postgres/***REMOVED*** database. ___AfricaSandbox___ is the name of the database used for development, and ___Africa___ is the production database. 
## Tables

- __assignment_data__: Stores information on individual assignments completed by workers, including start and completion times, accuracy, HIT ids, etc. 

- __assignment_history__: Tracks assignments and details of related payments for each worker, which is used by assignment review interface that can be accessed by individual workers. 

- __bad_user_maps__: Collection of bad geometries for testing. 

- __hit_data__: Records information about HITs (human intelligence tasks), such as creation and deletion times. Note: A HIT is defined mapping task, which can be undertaken by one or more workers, whereas an assignment is an individual worker's mapping efforts for a given HIT. 

- __incoming_names__: Table that is populated by `cvml`, which sends the names of new grid cells that need to be mapped by workers. 

- __kml_data__: Records the names of grid cells that are queued up for HIT creation, including the type of HIT (Q, F, N, or I) and how many times the HIT created for that sites has been mapped. 

- __kml_data_static__: Contains the names of cells that serve as Q (quality control) and I (initial qualification) HITs. These are in a separate table because they are unchanging, and are called on to populate the empty __kml_data__ table when moving from development to production.

- __configuration__: Parameters called on by a variety of `mapper`'s processes.

- __



[Back to README](../README.md)