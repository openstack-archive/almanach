========
Almanach
========


.. image:: https://badge.fury.io/py/almanach.svg
    :target: https://badge.fury.io/py/almanach

Almanach stores the utilization of OpenStack resources (instances and volumes) for each tenant.

What is Almanach?
-----------------

The main purpose of this software is to record the usage of the cloud resources of each tenants.

Almanach is composed of two parts:

- **Collector**: Listen for OpenStack events and store the relevant information in the database.
- **REST API**: Expose the information collected to external systems.

At the moment, Almanach is only able to record the usage of instances and volumes.

Resources
---------

Launchpad Projects
~~~~~~~~~~~~~~~~~~

- https://launchpad.net/almanach

Blueprints
~~~~~~~~~~

- https://blueprints.launchpad.net/almanach

Bug Tracking
~~~~~~~~~~~~

- https://bugs.launchpad.net/almanach

License
-------

Almanach is distributed under Apache 2.0 LICENSE.
