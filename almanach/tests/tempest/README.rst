===============================================
Tempest Integration of Almanach
===============================================

This directory contains Tempest tests to cover the Almanach project.

Tempest Configuration File
--------------------------

Example of config file for devstack:

.. code:: bash

    [DEFAULT]

    [identity]
    auth_version = v3
    uri = http://192.168.50.50:5000/v2.0
    uri_v3 = http://192.168.50.50:5000/v3

    [auth]
    admin_username = admin
    admin_password = secret
    admin_project_name = admin
    admin_domain_name = Default

    use_dynamic_credentials = true

Here, :code:`192.168.50.50` is your devstack IP address.

Run tests on your local machine
-------------------------------

1. Create a virtualenv from :code:`https://git.openstack.org/openstack/tempest.git
2. Create a custom :code:`tempest.conf`, by default :code:`/etc/tempest/tempest.conf` is loaded
3. List the tests: :code:`testr list-tests`
4. Run the tests with testr or tempest:
    - :code:`testr run`
    - :code:`tempest run`

Note: you can overwrite the default folder of the configuration by setting two environment variables

.. code:: bash

    export TEMPEST_CONFIG=tempest.conf
    export TEMPEST_CONFIG_DIR=/tmp/


Run tests in devstack
---------------------

- :code:`cd /opt/stack/almanach`
- :code:`tempest run`
