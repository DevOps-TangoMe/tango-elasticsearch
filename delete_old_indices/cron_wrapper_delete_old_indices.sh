#!/usr/bin/env bash

# Source virtualenv
. /local/data/virtualenv/bin/activate

DEFAULT_ES_URL='http://localhost:9200'
ES_URL=${ES_URL:-${DEFAULT_ES_URL}}

rm -fv /home/ec2-user/delete_old_indices.log
exec python /local/data/src/delete_old_indices.py --elasticsearch="${ES_URL}" --ttl 2
