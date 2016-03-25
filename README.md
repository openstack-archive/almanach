Almanach
========

[![Build Status](https://travis-ci.org/internap/almanach.svg?branch=master)](https://travis-ci.org/internap/almanach)
[![PyPI version](https://badge.fury.io/py/almanach.svg)](https://badge.fury.io/py/almanach)

Almanach stores the utilization of OpenStack resources (instances and volumes) for each tenant.

What is Almanach?
-----------------

The main purpose of this software is to bill customers based on their usage of the cloud infrastructure.

Almanach is composed of two parts:

- **Collector**: listen for OpenStack events and store the relevant information in the database.
- **REST API**: Expose the information collected to external systems.

License
-------

Almanach is distributed under Apache 2.0 LICENSE.
