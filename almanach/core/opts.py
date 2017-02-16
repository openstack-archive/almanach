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

CONF = cfg.CONF
DOMAIN = 'almanach'

database_opts = [
    cfg.StrOpt('driver',
               default='mongodb',
               help='Database driver'),
    cfg.StrOpt('connection_url',
               secret=True,
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
    cfg.ListOpt('transport_url',
                secret=True,
                default='rabbit://guest:guest@localhost:5672',
                help='AMQP connection URL'),
    cfg.StrOpt('topic',
               default='almanach',
               help='AMQP topic used for OpenStack notifications'),
    cfg.IntOpt('max_retries',
               default=5,
               help='Number of retries before to send message to critical queue'),
    cfg.IntOpt('min_retries',
               default=3,
               help='Number of retries before to use filters to discard notifications'),
    cfg.IntOpt('retry_delay',
               default=25,
               help='Delay in seconds between retries'),
]

keystone_opts = [
    cfg.StrOpt('username',
               help='Keystone service username'),
    cfg.StrOpt('password',
               secret=True,
               help='Keystone service password'),
    cfg.StrOpt('user_domain_id',
               default='default',
               help='Keystone service user domain ID'),
    cfg.StrOpt('user_domain_name',
               default='Default',
               help='Keystone service user domain name'),
    cfg.StrOpt('project_domain_name',
               default='Default',
               help='Keystone service project domain name'),
    cfg.StrOpt('project_name',
               default='service',
               help='Keystone service project name'),
    cfg.StrOpt('auth_url',
               default='http://127.0.0.1:35357/v3',
               help='Keystone API V3 admin endpoint'),
]

auth_opts = [
    cfg.StrOpt('strategy',
               default='private_key',
               help='Authentication driver for the API: private_key or keystone'),
    cfg.StrOpt('private_key',
               secret=True,
               default='secret',
               help='Private key for private key authentication'),
]

entity_opts = [
    cfg.IntOpt('instance_existence_threshold',
               default=900,
               help='Instance existence threshold'),
    cfg.IntOpt('volume_existence_threshold',
               default=60,
               help='Volume existence threshold'),
    cfg.ListOpt('instance_metadata',
                default=[],
                help='List of instance metadata to include from notifications'),
    cfg.ListOpt('instance_image_meta',
                default=[],
                help='List of instance image metadata to include from notifications'),
]

CONF.register_opts(database_opts, group='database')
CONF.register_opts(api_opts, group='api')
CONF.register_opts(collector_opts, group='collector')
CONF.register_opts(auth_opts, group='auth')
CONF.register_opts(keystone_opts, group='keystone_authtoken')
CONF.register_opts(entity_opts, group='entities')

logging.register_options(CONF)


def list_opts():
    return [
        ('database', database_opts),
        ('api', api_opts),
        ('collector', collector_opts),
        ('auth', auth_opts),
        ('keystone_authtoken', keystone_opts),
        ('entities', entity_opts),
    ]
