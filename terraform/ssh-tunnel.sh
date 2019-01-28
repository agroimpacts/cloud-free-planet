#copy paste the instance address as first argument to this script
ssh -i ~/downloader-jupyter-test.pem -NL 8157:localhost:8888 $1
