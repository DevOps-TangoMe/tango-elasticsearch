#!/usr/bin/env bash

# Source virtualenv
. /local/data/virtualenv/bin/activate

DEFAULT_ES_URL='http://localhost:9200'
ES_URL=${ES_URL:-${DEFAULT_ES_URL}}

exec python /local/data/src/precreate_indices.py --elasticsearch="${ES_URL}"
