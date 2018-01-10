# Changes for Active Learning Project

The following is a detailed list of changes that need to be made to both the crowdsourcing (`mapper`) and computer vision/machine learning (currently `cvmlAL` but the name is horrible and has to change) side of the active learning project. This list also includes general tasks that need to be undertaken that do not requires changes to either code base. This list will appear in both repositories, and will inform the milestones and issues that are tracked in each repo. 

***

## Objective 1

Fully integrate the developed components into a stand-alone, active learning-based, land cover mapping platform, demonstrating functionality over ~20,000 km$^2$ of Ghana with PlanetScope data. 

### `mapper`

1. **Port mapper from Princeton to AWS**

2. **Remove dependence on Mechanical Turk**

    This primarily involves developing an independent task manager. The following specific tasks must be undertaken for this aspect of the project: 

    1. *Web-related tasks*: 
    
        Development of new worker interface, including authentication mechanism (including superuser, employer, employee roles)

      * `showkml.js`: 
        - Remove preview logic
        - Append comments, save_status_code to POST and PUT data
        
      * Develop static employer registration page (SU auth)
        - Create new employer DB table
        
      * Develop static employee pre-registration page (Employer auth)
        - Add employer_id and employee_id columns in `worker_data` table
            
      * Develop static employee registration page (Employee auth via  employee_id)
        - Add username and password columns to `worker_data` table
            
      * Develop dynamic worker home page (Employee auth via username/password)
        - Add link to provide "HIT type" email functionality
        - Configure apache virtual host for page
        
      * Develop worker assignment page (requires employee login and Mapping Africa qualification)
          - Query to select all available HITs for worker
          - Logic to randomize the available HITs and select next assignment for worker
          - Move `assignment_data` row-creation logic from `getkml.wsgi` to here

      * Develop static worker qualification page (requires employee login)

      * Develop worker training page (requires employee login)
          - Edit trainingframe.wsgi to automatically record success
          - Call remaining core logic of `process_qualification_requests.py`

      * Develop dynamic worker assignment history page (requires employee login)
          - Query to retrieve specified assignment history
          - Add link to provide individual HIT email functionality
<br>    
    2. *daemon changes*
    
      * `create_hit_daemon.py`
          - Add reward and duration to `hit_data` table
          - Add difficulty bonus logic to reward calculation (from
          `approveAssignment`)
          - Replace calls to `MTurkMappingAfrica.py` with DB queriesRecord HIT info entirely in `hit_data` table
          - Remove Mturk verification code
          - Remove Mturk limitation on max assignments for HITs
          
      * `process_qualifications_requests.py`
          - Replace calls to MTurkMappingAfrica.py with DB queries
          - Simplify core logic and turn into callable routine (no longer a daemon)
      
      * `cleanup_absent_worker.py`
          - Replace Mturk calls with DB queries to establish and modify status of stranded assignments
<br>      
    3. *API directory modules*
    
      * `getkml.wsgi`
          - Remove preview code
          - Remove code for assignment transfer to different worker
          - Remove hidden input tags for comments and save_status_code
          - Replace assignment_data table INSERT call with UPDATE
      
      * `putkml.wsgi`
          - Call `ProcessNotifications.py` w/ inline args (incl comments, save_status_code)
          
      * `postkml.wsgi`
          - Call ProcessNotifications.py w/ inline args (incl
          comments, save_status_code)

      * `ProcessNotifications.py`
          - Replace calls to `MTurkMappingAfrica.py` with DB queries
          - Change main function to accept inline args (incl comments, save_status_code)
          
      * `MTurkMappingAfrica.py`
          - Rename to `MappingAfrica.py` (maybe just `mapper.py`)
          - Remove all Mturk calls and keep only non-Mturk common functions (see task notes for list)
          - Add function for new pay method and new payroll table
          - Add feedback column to assignment_data table (to be displayed on worker assignment history page)
          - Remove all references to self.mtcon here and in calling functions
          - Modify `approveAssignment()` to use new pay function and new feedback column
          - Modify `rejectAssignment()` to use new pay function and new feedback column
          - Modify `revokeQualification()` to use new feedback column
          - Modify `grantBonus()` to use new pay function and new feedback column
      
      * General requirement for all payment functions
          - Enable logic to set default fixed payments (per-worker payments will initially be over-ridden)
<br>         
    4. *Utilities*

      * Minor mod to `crontabSetup.mapper` and `daemonKiller.sh` to remove one daemon
      * Modify `notify_workers.py` to email workers via their registered email address
      * Modify `reverse_rejection.py` to skip Mturk call
      * Modify `worker_inquiry.py` to support new email format from workers
      * Create new `grantQualification.py` script, primarily as a back door for testing
      * Modify `list_mturk_hits.py` to only use DB tables.
          - Rename to list_hits.py.
      * Review scripts in 'test' subdir to see what's worth keeping
<br><br>

    5. *Testing*
        
        Testing of complete independence needs to be done interactively with SpatialCollective. It is likely that this step can be done independently of most changes that need to be done to adapt `mapper` for active learning, except for 3.3 bullets 1 and 3. 

3. **Adapt `mapper` for active learning**
    1. *General*
      * Update mapping rule set
          - A new more inclusive set of rules that minimize the risk of missed detections by workers, among other concerns.  
<br><br>
    2. *Utilities/daemons*
      * `KMLgenerate.R`
          - Add logic to listen for list of new training sites passed by `cvmlAL` (or `aktivmapper`, or whatever better name we decided to call it)
          - Prioritize active learning sites in `kml_data`
          - Rewrite logic for more efficient query of rewritten `master_grid` (current structure in which `master_grid` is 1/20 sub-sample of complete Africa master grid is undesirable). `RPostgresSQL` possibly needs to be replaced by more up to date DB wrapper, or `dplyr` functionality. 
          - Or replace with new daemon as needed (python-based?)
          
      * Create `labelizer` function (rasterization of training data)
          - integrate logic to limit label production according to worker quality
          - Storage in S3 bucket or EBS volume accessible by `cvmlAL`
          - Signals `cvmlAL` when all new labels complete
<br><br>
    3. *Web-related changes*
      
      * `showkml.js`
          - replace Google Maps API with DigitalGlobe image server or appropriate WebTile server.
      * Project website update
          - With new mapping rule set (see 3.1 above), including visual examples
<br><br>
    4. *Database*      
    
      * Replace existing sampling grid (`master_grid`)
          - ~500X500 m in a GCS
          - Change design from current sub-sampled table
          - Test for compatibility with querying/presenting planet imagery
          - Test adjacency of sampled KMLs
          - Give LandMapp Ghana portion of new training grid 
          
      * Replace/augment existing Q sites with sites collected by LandMapp
          - Coordinate completion of groundtruth with SpatialCollective
          - Update `kml_data_static`, `new_qaqc_sites`, and `qaqcfields`
          
      * Replace/update existing qualification/training dataset
          - Choose and digitize new training sites to match new rule set and grid size
          - Update `qual_sites` and `qaqcfields`
      
      * Table (or new column in master_grid) storing satellite image IDs
          - Based on querying planet API to find cloud free, growing season-on, growing season-off image pairs for each grid cell (Ghana)
          - Repeat for Sentinel, Landsat 
          - Likely need is to use Earth Engine (or new Radiant Earth platform) to run cloud detection algorithm over image archives
              This will include reading in Planet data into Earth Engine using API key

### Active learning code

Currently housed under `cvmlAL`, but in need of a more catchy and meaningful name. `activemapping`, `activmapper`, `aktivmapper`, would all be unique and speak of what we are doing.  `cymapper` (hinting at `cyborgmapper`), would speak to the human-machine nature of the system. Name suggestions welcome. 

Tasks/changes here are listed by theme rather than by specific modules/functions given the higher likelihood that existing modules/functions will be changed. 

1. **Port existing code into AWS**
    * Install on EMR instance
        - Set up appropriate storage volume
    * Reproduce Stephanie's original results
<br><br>
2.  **Adapt and expand image preprocessing functionality**
    
    * Add functionality to handle irregular boundaries/NA data in imagery
    * Update code (`preprocess.py`) to pre-process (circle detection/erosion-dilation, sub-divide) images to match `mapper`'s new sampling grid.
        - Determine optimal quantity of imagery to pre-process/keep in storage per iteration (do we need to classify all of Ghana at each iteration, or does a smaller sample of train/test data that we can use to find accuracy saturation?)
        - Possible integration of this task into Apache Spark streaming process
        
    * Add logic to handle multiple image types [later timeline, add placeholder to start]
<br><br>
3. **Integrate feature extraction code into Apache Spark**

    * Determine most-efficient architecture, e.g. can we implement this with Amazon Lambda? Some ideas [here](https://github.com/onetapbeyond/lambda-spark-executor) and [here](https://www.qubole.com/blog/spark-on-aws-lambda/) 
    * `ft_extract.py`/`cython_extract.c`/`cython_extract.pyx`
        - Implement in chosen architecture 
        - Update feature templates for flexibility/adaptability to multiple image types, multiple window sizes
        - Identify and reduce features to most essential set
<br>      
3. **Accuracy assessment routine** 

    * Develop binary classification measure that factors in all error sources:
        - Training data error/uncertainty
        - Binary classification as of algorithm
            - Adjust accuracy assessment used in `run_algorithm_CV4_activelearn.py` 
<br><br>
4. **Interactivity with mapper**

    * Write send function: 
        - Pauses learning loop at end of current iteration
        - Send list of new training samples to `mapper`
    * Write receive function: 
        - Listens for next round of training labels from `mapper`
        - Runs pre-processing utility as needed
        - Signals for next iteration of learning loop to commence
<br>       
5. **Alpha test**

    * Apply in fully interactive mode for representative 5,000 km$^2$ sub-region of Ghana
    * Change model/feature selection as needed and re-run until hit accuracy target
    * Final run of 20,000 km$^2$

***

# Objective 2

Develop a post-hoc segmentation routine that can be applied to posterior probability maps of active learning code

1. **Identify segmentation approach**

    * Desirable properties: 
        - Fast 
        - Leverages training data to determine locally varying probability threshold
        - Locally correct but biased field size class distributions, i.e. i.e. shape of distribution matches that of local agro-ecosystem but mean field is necessarily over-estimated
<br><br>
2. **Implementation**

    * Runs following completion of iteration loops?
    * Or at end of each iteration loop? 
        - if so, integrate into accuracy assessment routine

*** 

# Objective 3

Create 3 maps of cropland for all of Ghana (240,000 km$^2$) for the 2015-2017 epoch using:

1. **PlanetScope** data (3-4 m)

2. **Sentinel** data (10 m)

3. **Landsat** (15-30 m)
