!#/bin/bash

sudo apt-get update
sudo apt-get -y install git
sudo apt-get -y install nano
sudo apt-get -y install python3 python3-pip python3-dev libspatialindex-dev ca-certificates
sudo -H pip3 install jupyter
cd /usr/local/bin
sudo ln -s /usr/bin/python3 python
sudo -H pip3 install --upgrade --user

mkdir ~/.jupyter
echo "c.NotebookApp.allow_origin = '*'
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.password = 'sha1:bf975db4a3d2:aa513de53c368b6365c6c1e433e7ad07d9528708'" | sudo tee /home/ubuntu/.jupyter/jupyter_notebook_config.py

export CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt


mkdir ~/planet/
cd ~/planet/

#pip3 install -U setuptools
#sudo -H pip3 install awscli
#pip3 install -U numpy shapely pprint geojson planet requests boto3 scipy scikit-image rasterfoundry$
#pip3 install -U rasterio==1.0.7

cd /tmp
curl -O https://repo.anaconda.com/archive/Anaconda3-5.2.0-Linux-x86_64.sh
bash Anaconda3-5.2.0-Linux-x86_64.sh -b
source ~/.bashrc
conda create --name porder_env python=2.7.15
source activate my_env
conda install -y Shapely-1.6.4.post1-cp27-cp27m-win32.whl numpy shapely pprint geojson planet requests boto3 scipy scikit-image
sudo pip2 install -y  porder
