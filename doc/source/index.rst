..
  Licensed under the Apache License, Version 2.0 (the "License"); you may
  not use this file except in compliance with the License. You may obtain
  a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
  License for the specific language governing permissions and limitations
  under the License.

======================================
Welcome to the Almanach documentation!
======================================

Almanach stores the utilization of OpenStack resources (instances and volumes) for each tenant.

What is Almanach?
-----------------

The main purpose of this software is to record the usage of the cloud resources of each tenants.

Almanach is composed of two parts:

- **Collector**: Listen for OpenStack events and store the relevant information in the database.
- **REST API**: Expose the information collected to external systems.

Requirements
------------

- OpenStack infrastructure installed (Nova, Cinder...)
- MongoDB
- Python 2.7, 3.4 or 3.5


Generate config file with default values
----------------------------------------

.. code:: bash

    tox -e genconfig


Command line usage
------------------

Start the API daemon:

.. code:: bash

    almanach-api --config-file /etc/almanach/almanach.conf


Start the collector:

.. code:: bash

    almanach-collector --config-file /etc/almanach/almanach.conf


Signal Handling
---------------

- :code:`SIGINT`: force instantaneous termination
- :code:`SIGTERM`: graceful termination of the service
- :code:`SIGHUP`: reload service

Authentication
--------------

Protocol
~~~~~~~~

The authentication mechanism use the HTTP header :code:`X-Auth-Token` to send a token.
This token is validated through Keystone or with the config file (private secret key).

.. code:: raw

    GET /volume_types HTTP/1.1
    X-Auth-Token: secret
    Content-Type: application/json

    {}


If the token is not valid, you will receive a :code:`401 Not Authorized` response.

Private Key Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~

The private secret key authentication is the default method.
In your config file, you have to define your private key in the field :code:`auth_token`:

.. code:: raw

    [auth]
    strategy = private_key
    private_key = secret


Keystone Authentication
~~~~~~~~~~~~~~~~~~~~~~~

The token will be validated with Keystone.
To use this authentication backend you have to define the authentication strategy to :code:`keystone`.

.. code:: raw

    [auth]
    strategy = keystone

    [keystone_authtoken]

    # Keystone service username (string value)
    username = almanach

    # Keystone service password (string value)
    password = secret

    # Keystone service user domain ID (string value)
    user_domain_id = default

    # Keystone service user domain name (string value)
    user_domain_name = Default

    # Keystone service project domain name (string value)
    project_domain_name = Default

    # Keystone service project name (string value)
    project_name = service

    # Keystone API V3 admin endpoint (string value)
    auth_url = http://127.0.0.1:35357/v3



RabbitMQ configuration
----------------------

Each OpenStack services (Nova, Cinder, Neutron) need to be configured to send notifications to the Almanach queue.

For example with Nova, add the topic "almanach" in the config file :code:`/etc/nova.conf`:

.. code:: raw

    notification_topics=almanach


MongoDB configuration
---------------------

Almanach requires a specific user to connect to the database.
To create a new user, open a new MongoDB shell:

.. code:: javascript

    m = new Mongo()
    m.getDB("almanach").createUser({user: "almanach", pwd: "almanach", roles: [{role: "readWrite", db: "almanach"}]})


Devstack configuration
----------------------

.. code:: bash

    [[local|localrc]]
    ADMIN_PASSWORD=secret
    DATABASE_PASSWORD=$ADMIN_PASSWORD
    RABBIT_PASSWORD=$ADMIN_PASSWORD
    SERVICE_PASSWORD=$ADMIN_PASSWORD

    enable_plugin almanach https://git.openstack.org/openstack/almanach


Database entities
-----------------

Each entity have at least these properties:

- :code:`entity_id`: Unique id for the entity (UUID)
- :code:`entity_type`: "instance" or "volume"
- :code:`project_id`: Tenant unique ID (UUID)
- :code:`start`: Start date of the resource usage
- :code:`end`: End date of the resource usage or :code:`null` if the resource still in use by the tenant
- :code:`name`: Resource name

Compute Object
~~~~~~~~~~~~~~

.. code:: json

    {
        "entity_id": "UUID",
        "entity_type": "instance",
        "project_id": "UUID",
        "start": "2014-01-01T06:00:00.000Z",
        "end": null,
        "last_event": "2014-01-01T06:00:00.000Z",
        "flavor": "MyFlavor1",
        "os": {
            "distro": "ubuntu",
            "version": "14.04"
        },
        "name": "my-virtual-machine.domain.tld"
    }


Block Storage Object
~~~~~~~~~~~~~~~~~~~~

.. code:: json

    {
        "entity_id": "UUID",
        "entity_type": "volume",
        "project_id": "UUID",
        "start": "2014-01-01T06:00:00.000Z",
        "end": null,
        "last_event": "2014-01-01T06:00:00.000Z",
        "volume_type": "MyVolumeType",
        "size": 50,
        "name": "my-virtual-machine.domain.tld-volume",
        "attached_to": "UUID"
    }


List of events handled
----------------------

Almanach will process those events:

- :code:`compute.instance.create.end`
- :code:`compute.instance.delete.end`
- :code:`compute.instance.resize.confirm.end`
- :code:`compute.instance.rebuild.end`
- :code:`volume.create.end`
- :code:`volume.delete.end`
- :code:`volume.resize.end`
- :code:`volume.attach.end`
- :code:`volume.detach.end`
- :code:`volume.update.end`
- :code:`volume.exists`
- :code:`volume_type.create`

API documentation
-----------------

.. autoflask:: almanach.api.main:app
    :undoc-static:
    :include-empty-docstring:
