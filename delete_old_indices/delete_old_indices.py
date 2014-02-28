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


# This script will delete any index older than X days
# Default max age is set to 8 days


import argparse
import esclient
import logging
import sys
from datetime import datetime

################################################# Set up logging #######################################
LOGGER = logging.getLogger('delete_old_indices')
LOGGER.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(process)d - %(message)s')
ch.setFormatter(formatter)

LOGGER.addHandler(ch)


################################################# Constants #######################################
INDICES_KEY = 'indices'
INDEX_SEPARATOR = '-'

MAX_AGE_IN_DAYS = 8

MAX_DELETE_RETRY = 3

def main():

  LOGGER.info("Starting application")

  parser = argparse.ArgumentParser()
  parser.add_argument("--elasticsearch", help="Base URL to contact ElasticSearch", type=str, required=True)
  parser.add_argument("--ttl", help="Maximum age in days", default=MAX_AGE_IN_DAYS, type=int)
  args = parser.parse_args()


  max_ttl_seconds = args.ttl * 24 * 3600
  elasticsearch_url = args.elasticsearch

  LOGGER.info("Contacting ElasticSearch for status: [%s]" % (elasticsearch_url))
  es_connection = esclient.ESClient(elasticsearch_url)
  status = es_connection.status()

  LOGGER.info("ElasticSearch status retrieved")

  now = datetime.utcnow()

  if INDICES_KEY in status:
    for index in status[INDICES_KEY]:
      try:
        
        LOGGER.debug("Processing index [%s]"%(index))

        split_index = index.split(INDEX_SEPARATOR)
        if split_index and len(split_index) == 3:
          (logstash, date_str, shard) = index.split(INDEX_SEPARATOR)
          date = datetime.strptime(date_str, '%Y.%m.%d')
          age_date = now - date
          age_seconds = age_date.days * 24 * 3600 + age_date.seconds

          if age_seconds > max_ttl_seconds:
            retry = 0
            success = False
            while retry < MAX_DELETE_RETRY and not success:
              try:
                LOGGER.info("Deleting index [%s] since it is older than %d days" % (index, args.ttl))
                success = es_connection.delete_index(index)
                LOGGER.debug("Done deleting index [%s]"%(index))
              except Exception, e:
                LOGGER.error('Could not delete index %s: [%s]' % (index, str(e)))
              finally:
                retry = retry + 1
        

      except Exception, e:
        LOGGER.error('Could not process index %s: [%s]' % (index, str(e)))

if __name__ == '__main__':
  ret_code = main()
  sys.exit(ret_code)
