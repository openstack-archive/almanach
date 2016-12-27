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

from oslo_log import log

from almanach.core.controllers import base_controller
from almanach.core import model

LOG = log.getLogger(__name__)


class VolumeTypeController(base_controller.BaseController):

    def __init__(self, database_adapter):
        self.database_adapter = database_adapter

    def create_volume_type(self, volume_type_id, volume_type_name):
        LOG.info("volume type %s with name %s created", volume_type_id, volume_type_name)
        volume_type = model.VolumeType(volume_type_id, volume_type_name)
        self.database_adapter.insert_volume_type(volume_type)

    def get_volume_type(self, volume_type_id):
        return self.database_adapter.get_volume_type(volume_type_id)

    def delete_volume_type(self, volume_type_id):
        self.database_adapter.delete_volume_type(volume_type_id)

    def list_volume_types(self):
        return self.database_adapter.list_volume_types()
