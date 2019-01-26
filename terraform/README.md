To start testing the downloader with a notebook server on aws:

```
terraform apply

ssh -i downloader-jupyter-test.pem ubuntu@ec2-3-81-82-19.compute-1.amazonaws.com

# then on the instance

bash /tmp/configure_env_manually.sh
```

Copy the link that comes from the notebook output. Then run this on your local machine to open up
an ssh tunnel so that you can log into the notebook

```

ssh -i ~/downloader-jupyter-test.pem -NL 8157:localhost:8888 ubuntu@ec2-3-81-82-19.compute-1.amazonaws.com

```

the user (ubuntu) host (ec2-3-81...) will differ by the instance
