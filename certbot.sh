#! /bin/bash -x

certbot certonly --webroot -w /home/sandbox/mapper -d sandbox.crowdmapper.org

# To renew, use a root crontab job to execute 'certbot renew' every week (fllowed by an apache restart).
