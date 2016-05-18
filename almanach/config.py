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

import ConfigParser
import os
import os.path as os_path

from almanach.common.exceptions.almanach_exception import AlmanachException

configuration = ConfigParser.RawConfigParser()


def read(filename):
    if not os_path.isfile(filename):
        raise AlmanachException("Config file '{0}' not found".format(filename))

    print("Loading configuration file {0}".format(filename))
    configuration.read(filename)


def get(section, option, default=None):
    value = os.environ.get(section + "_" + option.upper())

    if value:
        return value

    try:
        return configuration.get(section, option)
    except:
        return default


def volume_existence_threshold():
    return int(get("ALMANACH", "volume_existence_threshold"))


def api_auth_token():
    return get("ALMANACH", "auth_token")


def device_metadata_whitelist():
    return get("ALMANACH", "device_metadata_whitelist").split(',')


def mongodb_url():
    return get("MONGODB", "url", default=None)


def mongodb_database():
    return get("MONGODB", "database", default="almanach")


def mongodb_indexes():
    return get('MONGODB', 'indexes').split(',')


def rabbitmq_url():
    return get("RABBITMQ", "url", default=None)


def rabbitmq_queue():
    return get("RABBITMQ", "queue", default=None)


def rabbitmq_exchange():
    return get("RABBITMQ", "exchange", default=None)


def rabbitmq_routing_key():
    return get("RABBITMQ", "routing.key", default=None)


def rabbitmq_retry():
    return int(get("RABBITMQ", "retry.maximum", default=None))


def rabbitmq_retry_exchange():
    return get("RABBITMQ", "retry.exchange", default=None)


def rabbitmq_retry_return_exchange():
    return get("RABBITMQ", "retry.return.exchange", default=None)


def rabbitmq_retry_queue():
    return get("RABBITMQ", "retry.queue", default=None)


def rabbitmq_dead_queue():
    return get("RABBITMQ", "dead.queue", default=None)


def rabbitmq_dead_exchange():
    return get("RABBITMQ", "dead.exchange", default=None)


def rabbitmq_time_to_live():
    return int(get("RABBITMQ", "retry.time.to.live", default=None))


def _read_file(filename):
    f = open(filename, "r")
    content = f.read()
    f.close()
    return content
