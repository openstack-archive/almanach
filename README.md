Almanach
========

[![Build Status](https://travis-ci.org/internap/almanach.svg?branch=master)](https://travis-ci.org/internap/almanach)
[![PyPI version](https://badge.fury.io/py/almanach.svg)](https://badge.fury.io/py/almanach)

Almanach stores the utilization of OpenStack resources (instances and volumes) for each tenant.

What is Almanach?
-----------------

The main purpose of this software is to bill customers based on their usage of the cloud infrastructure.

Almanach is composed of two parts:

- **Collector**: Listen for OpenStack events and store the relevant information in the database.
- **REST API**: Expose the information collected to external systems.

Requirements
------------

- OpenStack infrastructure installed (Nova, Cinder...)
- MongoDB
- Python 2.7

Command line usage
------------------

Usage:

```bash
usage: almanach [-h] [--logging LOGGING] {api,collector} config_file
```

Start the API daemon:

```bash
almanach api /path/to/almanach.cfg
```

Start the collector:

```bash
almanach collector /path/to/almanach.cfg
```

Custom logging configuration:

```bash
almanach collector /path/to/almanach.cfg --logging /path/to/logging.cfg
```

The syntax of the logging configuration file is available in the official [Python documentation](https://docs.python.org/2/library/logging.config.html). 

Environment variables
---------------------

You can override the configuration parameters by using environment variables:

```bash
export RABBITMQ_URL="amqp://openstack:openstack@hostname:5672"
almanach collector /path/to/almanach.cfg
```

Running Almanach with Docker
----------------------------

The actual Docker configuration assume that you already have RabbitMQ (mandatory for Openstack) and MongoDB configured for Almanach.

```bash
export RABBITMQ_URL="amqp://guest:guest@messaging:5672/"
export MONGODB_URL="mongodb://almanach:almanach@database:27017/almanach"

docker-compose build
docker-compose up
```

The command `docker-compose up` starts 2 containers: the collector and the API server. 
The environment variables `RABBITMQ_URL` and `MONGODB_URL` are mandatory.

RabbitMQ configuration
----------------------

Each OpenStack services (Nova, Cinder, Neutron) need to be configured to send notifications to the Almanach queue.

For example with Nova, add the topic "almanach" in the config file `/etc/nova.conf`:

```bash
notification_topics=almanach
```

Database configuration
----------------------

Almanach requires a specific user to connect to the database.
To create a new user, open a new MongoDB shell:

```javascript
m = new Mongo()
m.getDB("almanach").createUser({user: "almanach", pwd: "almanach", roles: [{role: "readWrite", db: "almanach"}]})
```

Database entities
-----------------

Each entity have at least these properties:

- `entity_id`: Unique id for the entity (UUID)
- `entity_type`: "instance" or "volume"
- `project_id`: Tenant unique ID (UUID)
- `start`: Start date of the resource usage
- `end`: End date of the resource usage or `null` if the resource still in use by the tenant
- `name`: Resource name

### Compute Object

```json
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
```

### Block Storage Object

```json
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
```

List of events handled
----------------------

Almanach will process those events:

- `compute.instance.create.end`
- `compute.instance.delete.end`
- `compute.instance.resize.confirm.end`
- `compute.instance.rebuild.end`
- `volume.create.end`
- `volume.delete.end`
- `volume.resize.end`
- `volume.attach.end`
- `volume.detach.end`
- `volume.update.end`
- `volume.exists`
- `volume_type.create`

License
-------

Almanach is distributed under Apache 2.0 LICENSE.
