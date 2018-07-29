
# Cloud Shadow Extraction Algorithm Code Family

The code family including 3 codes:

1. filter_rst.py
2. filter_tif.py
3. filter_callable.py

filter_rst.py: works with .rst format; outputs are images; horizontal functions (flexible if the algorithm is going to changw), process image by block. 
filter_tif.py: works with .tif format; outputs are images; horizontal functions, process image by block.
filter_callable.py : works with numpy array; outputs are cloud-shadow fraction statistics; vertical function (work for this algorithm only, not flexible).   