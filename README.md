tango-elasticsearch
===================

Collection of tools used at Tango for ElasticSearch


License
-------

This is released under Apache License v2


delete_old_indices/delete_old_indices.py
----------------------------------------

Python script to delete logstash indices older than X days.
Assumes indices are using the following format: logstash-YYYY.MM.DD-HH
Where:
* YYYY is the 4 digit year

* MM is the 2 digit month

* DD is the 2 digit day

* HH is the 2 digit hour


