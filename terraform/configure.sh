sudo apt-get install -y -q xclip # dependency of porder
mkdir ~/.jupyter
echo "c.NotebookApp.allow_origin = '*'
c.NotebookApp.ip = '0.0.0.0'

export CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

mkdir ~/planet/
cd ~/planet/
sudo mkdir /dev/data # makes dir on this volume because other is full of anaconda stuff
sudo chmod 777 /dev/data # makes directory read and writeable

