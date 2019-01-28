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

make sure to also add your planet credentials. You can do so by running 

```
planet init
```

or by creating a file at `~/.planet.json` with the following specification (not a real api key)

```
{"key": "a98f17b67fe84272a7aa658738829e942"}
```

You also need a cloud provider credential file (see porder github). The format for aws is as follows


amazon_s3:
        bucket:
        aws_region:
        aws_access_key_id:
        aws_secret_access_key:
        path_prefix: 

