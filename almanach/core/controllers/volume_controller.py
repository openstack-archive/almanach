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

from datetime import timedelta

from oslo_log import log

from almanach.core.controllers import base_controller
from almanach.core import exception
from almanach.core import model

LOG = log.getLogger(__name__)


class VolumeController(base_controller.BaseController):

    def __init__(self, config, database_adapter):
        self.database_adapter = database_adapter
        self.volume_existence_threshold = timedelta(0, config.entities.volume_existence_threshold)

    def list_volumes(self, project_id, start, end):
        return self.database_adapter.get_all_entities_by_project(project_id, start, end, model.Volume.TYPE)

    def create_volume(self, volume_id, project_id, start, volume_type, size, volume_name, attached_to=None):
        start = self._validate_and_parse_date(start)
        LOG.info("volume %s created in project %s to size %s on %s", volume_id, project_id, size, start)
        if self._fresher_entity_exists(volume_id, start):
            return

        volume_type_name = self._get_volume_type_name(volume_type)

        entity = model.Volume(volume_id, project_id, start, None, volume_type_name, size, start, volume_name,
                              attached_to)
        self.database_adapter.insert_entity(entity)

    def detach_volume(self, volume_id, date, attachments):
        date = self._validate_and_parse_date(date)
        LOG.info("volume %s detached on %s", volume_id, date)
        try:
            self._volume_detach_instance(volume_id, date, attachments)
        except exception.EntityNotFoundException as e:
            LOG.error("Trying to detach a volume with id '%s' not in the database yet.", volume_id)
            raise e

    def attach_volume(self, volume_id, date, attachments):
        date = self._validate_and_parse_date(date)
        LOG.info("Volume %s attached to %s on %s", volume_id, attachments, date)
        try:
            self._volume_attach_instance(volume_id, date, attachments)
        except exception.EntityNotFoundException as e:
            LOG.error("Trying to attach a volume with id '%s' not in the database yet.", volume_id)
            raise e

    def rename_volume(self, volume_id, volume_name):
        try:
            volume = self.database_adapter.get_active_entity(volume_id)
            if volume and volume.name != volume_name:
                LOG.info("volume %s renamed from %s to %s", volume_id, volume.name, volume_name)
                volume.name = volume_name
                self.database_adapter.update_active_entity(volume)
        except exception.EntityNotFoundException:
            LOG.error("Trying to update a volume with id '%s' not in the database yet.", volume_id)

    def resize_volume(self, volume_id, size, update_date):
        update_date = self._validate_and_parse_date(update_date)
        try:
            volume = self.database_adapter.get_active_entity(volume_id)
            LOG.info("volume %s updated in project %s to size %s on %s",
                     volume_id, volume.project_id, size, update_date)

            self.database_adapter.close_active_entity(volume_id, update_date)

            volume.size = size
            volume.start = update_date
            volume.end = None
            volume.last_event = update_date
            self.database_adapter.insert_entity(volume)
        except exception.EntityNotFoundException as e:
            LOG.error("Trying to update a volume with id '%s' not in the database yet.", volume_id)
            raise e

    def delete_volume(self, volume_id, delete_date):
        delete_date = self._localize_date(self._validate_and_parse_date(delete_date))
        LOG.info("volume %s deleted on %s", volume_id, delete_date)
        try:
            if self.database_adapter.count_entity_entries(volume_id) > 1:
                volume = self.database_adapter.get_active_entity(volume_id)
                if delete_date - volume.start < self.volume_existence_threshold:
                    self.database_adapter.delete_active_entity(volume_id)
                    return
            self.database_adapter.close_active_entity(volume_id, delete_date)
        except exception.EntityNotFoundException as e:
            LOG.error("Trying to delete a volume with id '%s' not in the database yet.", volume_id)
            raise e

    def _volume_attach_instance(self, volume_id, date, attachments):
        volume = self.database_adapter.get_active_entity(volume_id)
        date = self._localize_date(date)
        volume.last_event = date
        existing_attachments = volume.attached_to
        volume.attached_to = attachments

        if existing_attachments or self._is_within_threshold(date, volume):
            self.database_adapter.update_active_entity(volume)
        else:
            self._close_volume(volume_id, volume, date)

    def _volume_detach_instance(self, volume_id, date, attachments):
        volume = self.database_adapter.get_active_entity(volume_id)
        date = self._localize_date(date)
        volume.last_event = date
        volume.attached_to = attachments

        if attachments or self._is_within_threshold(date, volume):
            self.database_adapter.update_active_entity(volume)
        else:
            self._close_volume(volume_id, volume, date)

    def _close_volume(self, volume_id, volume, date):
        self.database_adapter.close_active_entity(volume_id, date)
        volume.start = date
        volume.end = None
        self.database_adapter.insert_entity(volume)

    def _is_within_threshold(self, date, volume):
        return date - volume.start < self.volume_existence_threshold

    def _get_volume_type_name(self, volume_type_id):
        if volume_type_id is None:
            return None

        volume_type = self.database_adapter.get_volume_type(volume_type_id)
        return volume_type.volume_type_name
