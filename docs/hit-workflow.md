## HIT Types and the Active Learning Workflow

There are four types of assignments that can be considered by `mapper`:

- I: These are a small number (currently 8) of initial qualification sites that any worker joining `mapper` has to pass before mapping the other three kinds.
- F: Training sites for `cvml`. These are either selected at random by `mapper` (from the total pool of sites to be classified) for `cvml`'s initial training, or by `cvml` itself on subsequent iterations, based on classification uncertainty. ___Etmyology:___ Originally the letter stood for Future under the old Mechanical Turk system (sites to be mapped by multiple workers so that they could eventually be merged to create new reference maps for Q HITs). 
- N: Sites given to workers when all F sites are complete, while waiting for the next batch of F sites to come back from `cvml`. ___Etmyology:___ Originally standing for normal (under the old Mechanical Turk system) mapping jobs, these were served out to just a single worker.    
- Q: Quality assessment sites, where workers' mapping accuracy is scored. 

Workers are served F/N/Q sites at a frequency determined by the parameters "Hit_QaqcPercentage" and "Hit_FqaqcPercentage" in mapper's __config__ table. There are two modes: 

1. Hit_Standalone = True: `mapper` operates in the original standalone way and serves up a randomly selected F, Q, or N sites based on the ratio: 

    -  Hit_FaqcPercentage/(100-Hit_FaqcPercentage-Hit_QaqcPercentage)/Hit_QaqcPercentage
<br><br>

2. Hit_Standalone = False: `mapper` prioritizes F sites (the mode for working with `cvml`). An F or Q is randomly selected and served to the worker based on the ratio: 

    - (100-Hit_QaqcPercentage)/Hit_QaqcPercentage
    <br><br>

    Thus F sites are prioritized, and N sites are only offered to a worker once the worker has completed all F sites in the system.  