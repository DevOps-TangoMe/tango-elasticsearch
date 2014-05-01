#!/usr/bin/env python
#  Copyright 2014 TangoMe Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


# This script precreates indices in advance
# This prevents ElasticSearch cluster from being overloaded in requests while creating a new index


import argparse
import esclient
import logging
import sys
from datetime import datetime
from datetime import timedelta

################################################# Set up logging #######################################
LOGGER = logging.getLogger('pre-create_indices')
LOGGER.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(process)d - %(message)s')
ch.setFormatter(formatter)

LOGGER.addHandler(ch)


################################################# Constants #######################################
INDICES_KEY = 'indices'
INDEX_SEPARATOR = '-'
INDEX_PREFIX = 'logstash-'

MAX_AGE_IN_HOURS = 8

MAX_CREATE_RETRY = 3

def main():

  LOGGER.info("Starting application")

  parser = argparse.ArgumentParser()
  parser.add_argument("--elasticsearch", help="Base URL to contact ElasticSearch", type=str, required=True)
  parser.add_argument("--hours-ahead", help="How many hours in advance", default=MAX_AGE_IN_HOURS, type=int)
  args = parser.parse_args()


  elasticsearch_url = args.elasticsearch
  hours_ahead = args.hours_ahead

  LOGGER.info("Contacting ElasticSearch for status: [%s]" % (elasticsearch_url))
  es_connection = esclient.ESClient(elasticsearch_url)

  now = datetime.utcnow()
  for hour in xrange(hours_ahead):
    hour_delta = timedelta(hours=hour)
    hour_date = now + hour_delta
    index_name = INDEX_PREFIX + "%.4d.%.2d.%.2d-%.2d" % (hour_date.year, hour_date.month, hour_date.day, hour_date.hour)

    retry = 0
    success = False
    while retry < MAX_CREATE_RETRY and not success:
      try:
        LOGGER.info("Creating index [%s]"%(index_name))
        es_connection.create_index(index_name)
        LOGGER.debug("Done creating index [%s]"%(index_name))
        success = True
      except Exception, e:
        LOGGER.error('Could not create index %s: [%s]' % (index_name, str(e)))
      finally:
        retry = retry + 1


if __name__ == '__main__':
  ret_code = main()
  sys.exit(ret_code)
