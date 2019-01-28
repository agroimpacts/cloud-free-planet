mkdir ~/.jupyter
echo "c.NotebookApp.allow_origin = '*'
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.password = 'sha1:bf975db4a3d2:aa513de53c368b6365c6c1e433e7ad07d9528708'" | sudo tee /h$

export CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

mkdir ~/planet/
cd ~/planet/
sudo mkdir /dev/data # makes dir on this volume because other is full of anaconda stuff
sudo chmod 777 /dev/data # makes directory read and writeable
#conda create --yes --name porder_env --channel conda-forge python=2.7.15 pip planet geojson shapely $
#source activate porder_env
#yes | pip install porder

