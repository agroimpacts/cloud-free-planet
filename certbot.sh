#! /bin/bash -x

certbot certonly --webroot -w /home/sandbox/afmap -d sandbox.crowdmapper.org

# To renew, use a crontab job to execute 'certbot renew' every few weeks.
