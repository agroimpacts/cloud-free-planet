#!/bin/bash
## This needs to be sourced from the account's .bashrc file
# Mapper Terraform vars
export TF_VAR_subnet=subnet-638f0c39
export TF_VAR_s3_log_uri=s3://azavea-africa-test/logs
export TF_VAR_key_name=azavea-mapping-africa
export TF_VAR_s3_rpm_uri=s3://azavea-africa-test/rpms/4ff6e43910188a1215a1474cd2e5152e200c5702
export TF_VAR_s3_notebook_uri=s3://azavea-africa-test/notebooks
export TF_VAR_bs_bucket=activemapper
export TF_VAR_bs_prefix=bootstrap-cluster-test
export PATH=~/mapperAL/terraform:$PATH
