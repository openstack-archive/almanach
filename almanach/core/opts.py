# Copyright 2016 Internap.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_config import cfg
from oslo_log import log as logging

LOG = logging.getLogger(__name__)
CONF = cfg.CONF
DOMAIN = 'almanach'

database_opts = [
    cfg.StrOpt('driver',
               default='mongodb',
               help='Database driver'),
    cfg.StrOpt('connection_url',
               default='mongodb://almanach:almanach@localhost:27017/almanach',
               help='Database connection URL'),
]

api_opts = [
    cfg.IPOpt('bind_ip',
              default='127.0.0.1',
              help='IP address to listen on'),
    cfg.PortOpt('bind_port',
                default=8000,
                help='TCP port number to listen on'),
]

collector_opts = [
    cfg.HostnameOpt('rabbit_host',
                    default='localhost',
                    help='RabbitMQ Hostname'),
    cfg.PortOpt('rabbit_port',
                default=5672,
                help='RabbitMQ TCP port'),
    cfg.StrOpt('rabbit_username',
               help='RabbitMQ Username'),
    cfg.StrOpt('rabbit_password',
               help='RabbitMQ Password'),
    cfg.StrOpt('queue',
               default='almanach.info',
               help='Default queue name'),
    cfg.StrOpt('exchange',
               default='almanach.info',
               help='Default exchange name'),
    cfg.StrOpt('routing_key',
               default='almanach.info',
               help='Default queue routing key'),
    cfg.StrOpt('retry_queue',
               default='almanach.retry',
               help='Retry queue name'),
    cfg.StrOpt('retry_exchange',
               default='almanach.retry',
               help='Retry exchange name'),
    cfg.StrOpt('retry_return_exchange',
               default='almanach',
               help='Retry return exchange name'),
    cfg.IntOpt('retry_ttl',
               default=10,
               help='Time to live value of messages sent on the retry queue'),
    cfg.IntOpt('max_retries',
               default=3,
               help='Maximal number of message retries'),
    cfg.StrOpt('dead_queue',
               default='almanach.dead',
               help='Dead queue name'),
    cfg.StrOpt('dead_exchange',
               default='almanach.dead',
               help='Dead exchange name'),
]

auth_opts = [
    cfg.StrOpt('strategy',
               default='private_key',
               help='Authentication driver for the API'),
    cfg.StrOpt('private_key',
               default='secret',
               help='Private key for private key authentication'),
    cfg.StrOpt('keystone_username',
               help='Keystone service username'),
    cfg.StrOpt('keystone_password',
               help='Keystone service password'),
    cfg.StrOpt('keystone_tenant',
               help='Keystone service tenant'),
    cfg.StrOpt('keystone_url',
               default='http://keystone_url:5000/v2.0',
               help='Keystone URL'),
]

resource_opts = [
    cfg.IntOpt('volume_existence_threshold',
               default=60,
               help='Volume existence threshold'),
    cfg.ListOpt('device_metadata_whitelist',
                default=[],
                deprecated_for_removal=True,
                help='Metadata to include in entity'),
]

CONF.register_opts(database_opts, group='database')
CONF.register_opts(api_opts, group='api')
CONF.register_opts(collector_opts, group='collector')
CONF.register_opts(auth_opts, group='auth')
CONF.register_opts(resource_opts, group='resources')

logging.register_options(CONF)
logging.setup(CONF, DOMAIN)


def list_opts():
    return [
        ('database', database_opts),
        ('api', api_opts),
        ('collector', collector_opts),
        ('api.auth', auth_opts),
        ('resources', resource_opts),
    ]
