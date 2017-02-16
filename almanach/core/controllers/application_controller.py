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

from pkg_resources import get_distribution

from almanach.core.controllers import base_controller


class ApplicationController(base_controller.BaseController):

    def __init__(self, database_adapter):
        self.database_adapter = database_adapter

    def get_application_info(self):
        return {
            "info": {"version": get_distribution("almanach").version},
            "database": {"all_entities": self.database_adapter.count_entities(),
                         "active_entities": self.database_adapter.count_active_entities()}
        }
