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

from datetime import datetime, timedelta

import dateutil.parser
import pytz

DEFAULT_VOLUME_TYPE = "5dadd67f-e21e-4c13-b278-c07b73b21250"


def get_instance_create_end_sample(instance_id=None, tenant_id=None, flavor_name=None,
                                   creation_timestamp=None, name=None, os_distro=None, os_version=None, metadata={}):
    kwargs = {
        "instance_id": instance_id or "e7d44dea-21c1-452c-b50c-cbab0d07d7d3",
        "tenant_id": tenant_id or "0be9215b503b43279ae585d50a33aed8",
        "hostname": name or "to.to",
        "display_name": name or "to.to",
        "instance_type": flavor_name or "myflavor",
        "os_distro": os_distro or "CentOS",
        "os_version": os_version or "6.4",
        "created_at": creation_timestamp if creation_timestamp else datetime(2014, 2, 14, 16, 29, 58, tzinfo=pytz.utc),
        "launched_at": creation_timestamp + timedelta(seconds=1) if creation_timestamp else datetime(2014, 2, 14, 16,
                                                                                                     30, 02,
                                                                                                     tzinfo=pytz.utc),
        "terminated_at": None,
        "deleted_at": None,
        "state": "active",
        "metadata": metadata
    }
    kwargs["timestamp"] = kwargs["launched_at"] + timedelta(microseconds=200000)
    return _get_instance_payload("compute.instance.create.end", **kwargs)


def get_instance_delete_end_sample(instance_id=None, tenant_id=None, flavor_name=None, os_distro=None, os_version=None,
                                   creation_timestamp=None, deletion_timestamp=None, name=None):
    kwargs = {
        "instance_id": instance_id,
        "tenant_id": tenant_id,
        "hostname": name,
        "display_name": name,
        "instance_type": flavor_name,
        "os_distro": os_distro or "centos",
        "os_version": os_version or "6.4",
        "created_at": creation_timestamp if creation_timestamp else datetime(2014, 2, 14, 16, 29, 58, tzinfo=pytz.utc),
        "launched_at": creation_timestamp + timedelta(seconds=1) if creation_timestamp else datetime(2014, 2, 14, 16,
                                                                                                     30, 02,
                                                                                                     tzinfo=pytz.utc),
        "terminated_at": deletion_timestamp if deletion_timestamp else datetime(2014, 2, 18, 12, 5, 23,
                                                                                tzinfo=pytz.utc),
        "deleted_at": deletion_timestamp if deletion_timestamp else datetime(2014, 2, 18, 12, 5, 23, tzinfo=pytz.utc),
        "state": "deleted"
    }
    kwargs["timestamp"] = kwargs["terminated_at"] + timedelta(microseconds=200000)
    return _get_instance_payload("compute.instance.delete.end", **kwargs)


def get_volume_create_end_sample(volume_id=None, tenant_id=None, volume_type=None, volume_size=None,
                                 creation_timestamp=None, name=None):
    kwargs = {
        "volume_id": volume_id or "64a0ca7f-5f5a-4dc5-a1e1-e04e89eb95ed",
        "tenant_id": tenant_id or "46eeb8e44298460899cf4b3554bfe11f",
        "display_name": name or "mytenant-0001-myvolume",
        "volume_type": volume_type or DEFAULT_VOLUME_TYPE,
        "volume_size": volume_size or 50,
        "created_at": creation_timestamp if creation_timestamp else datetime(2014, 2, 14, 17, 18, 35, tzinfo=pytz.utc),
        "launched_at": creation_timestamp + timedelta(seconds=1) if creation_timestamp else datetime(2014, 2, 14, 17,
                                                                                                     18, 40,
                                                                                                     tzinfo=pytz.utc),
        "status": "available"
    }
    kwargs["timestamp"] = kwargs["launched_at"] + timedelta(microseconds=200000)
    return _get_volume_icehouse_payload("volume.create.end", **kwargs)


def get_volume_delete_end_sample(volume_id=None, tenant_id=None, volume_type=None, volume_size=None,
                                 creation_timestamp=None, deletion_timestamp=None, name=None):
    kwargs = {
        "volume_id": volume_id or "64a0ca7f-5f5a-4dc5-a1e1-e04e89eb95ed",
        "tenant_id": tenant_id or "46eeb8e44298460899cf4b3554bfe11f",
        "display_name": name or "mytenant-0001-myvolume",
        "volume_type": volume_type or DEFAULT_VOLUME_TYPE,
        "volume_size": volume_size or 50,
        "created_at": creation_timestamp if creation_timestamp else datetime(2014, 2, 14, 17, 18, 35, tzinfo=pytz.utc),
        "launched_at": deletion_timestamp if deletion_timestamp else datetime(2014, 2, 14, 17, 18, 40, tzinfo=pytz.utc),
        "timestamp": deletion_timestamp if deletion_timestamp else datetime(2014, 2, 23, 8, 1, 58, tzinfo=pytz.utc),
        "status": "deleting"
    }
    return _get_volume_icehouse_payload("volume.delete.end", **kwargs)


def get_volume_attach_icehouse_end_sample(volume_id=None, tenant_id=None, volume_type=None, volume_size=None,
                                          creation_timestamp=None, name=None, attached_to=None):
    kwargs = {
        "volume_id": volume_id or "64a0ca7f-5f5a-4dc5-a1e1-e04e89eb95ed",
        "tenant_id": tenant_id or "46eeb8e44298460899cf4b3554bfe11f",
        "display_name": name or "mytenant-0001-myvolume",
        "volume_type": volume_type or DEFAULT_VOLUME_TYPE,
        "volume_size": volume_size or 50,
        "attached_to": attached_to or "e7d44dea-21c1-452c-b50c-cbab0d07d7d3",
        "created_at": creation_timestamp if creation_timestamp else datetime(2014, 2, 14, 17, 18, 35, tzinfo=pytz.utc),
        "launched_at": creation_timestamp + timedelta(seconds=1) if creation_timestamp else datetime(2014, 2, 14, 17,
                                                                                                     18, 40,
                                                                                                     tzinfo=pytz.utc),
        "timestamp": creation_timestamp + timedelta(seconds=1) if creation_timestamp else datetime(2014, 2, 14, 17, 18,
                                                                                                   40, tzinfo=pytz.utc),
    }
    return _get_volume_icehouse_payload("volume.attach.end", **kwargs)


def get_volume_attach_kilo_end_sample(volume_id=None, tenant_id=None, volume_type=None, volume_size=None,
                                      timestamp=None, name=None, attached_to=None):
    kwargs = {
        "volume_id": volume_id or "64a0ca7f-5f5a-4dc5-a1e1-e04e89eb95ed",
        "tenant_id": tenant_id or "46eeb8e44298460899cf4b3554bfe11f",
        "display_name": name or "mytenant-0001-myvolume",
        "volume_type": volume_type or DEFAULT_VOLUME_TYPE,
        "volume_size": volume_size or 50,
        "attached_to": attached_to,
        "timestamp": timestamp + timedelta(seconds=1) if timestamp else datetime(2014, 2, 14, 17, 18, 40,
                                                                                 tzinfo=pytz.utc),
    }
    return _get_volume_kilo_payload("volume.attach.end", **kwargs)


def get_volume_detach_kilo_end_sample(volume_id=None, tenant_id=None, volume_type=None, volume_size=None,
                                      timestamp=None, name=None, attached_to=None):
    kwargs = {
        "volume_id": volume_id or "64a0ca7f-5f5a-4dc5-a1e1-e04e89eb95ed",
        "tenant_id": tenant_id or "46eeb8e44298460899cf4b3554bfe11f",
        "display_name": name or "mytenant-0001-myvolume",
        "volume_type": volume_type or DEFAULT_VOLUME_TYPE,
        "volume_size": volume_size or 50,
        "attached_to": attached_to,
        "timestamp": timestamp + timedelta(seconds=1) if timestamp else datetime(2014, 2, 14, 17, 18, 40,
                                                                                 tzinfo=pytz.utc),
    }
    return _get_volume_kilo_payload("volume.detach.end", **kwargs)


def get_volume_detach_end_sample(volume_id=None, tenant_id=None, volume_type=None, volume_size=None,
                                 creation_timestamp=None, deletion_timestamp=None, name=None):
    kwargs = {
        "volume_id": volume_id or "64a0ca7f-5f5a-4dc5-a1e1-e04e89eb95ed",
        "tenant_id": tenant_id or "46eeb8e44298460899cf4b3554bfe11f",
        "display_name": name or "mytenant-0001-myvolume",
        "volume_type": volume_type or DEFAULT_VOLUME_TYPE,
        "volume_size": volume_size or 50,
        "attached_to": None,
        "created_at": creation_timestamp if creation_timestamp else datetime(2014, 2, 14, 17, 18, 35, tzinfo=pytz.utc),
        "launched_at": creation_timestamp + timedelta(seconds=1) if creation_timestamp else datetime(2014, 2, 14, 17,
                                                                                                     18, 40,
                                                                                                     tzinfo=pytz.utc),
        "timestamp": deletion_timestamp if deletion_timestamp else datetime(2014, 2, 23, 8, 1, 58, tzinfo=pytz.utc),
        "status": "detach"
    }
    return _get_volume_icehouse_payload("volume.detach.end", **kwargs)


def get_volume_rename_end_sample(volume_id=None, tenant_id=None, volume_type=None, volume_size=None,
                                 creation_timestamp=None, deletion_timestamp=None, name=None):
    kwargs = {
        "volume_id": volume_id or "64a0ca7f-5f5a-4dc5-a1e1-e04e89eb95ed",
        "tenant_id": tenant_id or "46eeb8e44298460899cf4b3554bfe11f",
        "display_name": name or "mytenant-0001-mysnapshot01",
        "volume_type": volume_type or DEFAULT_VOLUME_TYPE,
        "volume_size": volume_size or 50,
        "attached_to": None,
        "created_at": creation_timestamp if creation_timestamp else datetime(2014, 2, 14, 17, 18, 35, tzinfo=pytz.utc),
        "launched_at": creation_timestamp + timedelta(seconds=1) if creation_timestamp else datetime(2014, 2, 14, 17,
                                                                                                     18, 40,
                                                                                                     tzinfo=pytz.utc),
        "timestamp": deletion_timestamp if deletion_timestamp else datetime(2014, 2, 23, 8, 1, 58, tzinfo=pytz.utc),
        "status": "detach"
    }
    return _get_volume_icehouse_payload("volume.update.end", **kwargs)


def get_volume_exists_sample(volume_id=None, tenant_id=None, volume_type=None, volume_size=None,
                             creation_timestamp=None, deletion_timestamp=None, name=None):
    kwargs = {
        "volume_id": volume_id or "64a0ca7f-5f5a-4dc5-a1e1-e04e89eb95ed",
        "tenant_id": tenant_id or "46eeb8e44298460899cf4b3554bfe11f",
        "display_name": name or "mytenant-0001-mysnapshot",
        "volume_type": volume_type or DEFAULT_VOLUME_TYPE,
        "volume_size": volume_size or 50,
        "attached_to": None,
        "created_at": creation_timestamp if creation_timestamp else datetime(2014, 2, 14, 17, 18, 35, tzinfo=pytz.utc),
        "launched_at": creation_timestamp + timedelta(seconds=1) if creation_timestamp else datetime(2014, 2, 14, 17,
                                                                                                     18, 40,
                                                                                                     tzinfo=pytz.utc),
        "timestamp": deletion_timestamp if deletion_timestamp else datetime(2014, 2, 23, 8, 1, 58, tzinfo=pytz.utc),
        "status": "detach"
    }
    return _get_volume_icehouse_payload("volume.exists", **kwargs)


def _format_date(datetime_obj):
    return datetime_obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _get_instance_payload(event_type, instance_id=None, tenant_id=None, hostname=None, display_name=None,
                          instance_type=None,
                          instance_flavor_id=None, timestamp=None, created_at=None, launched_at=None,
                          deleted_at=None, terminated_at=None, state=None, os_type=None, os_distro=None,
                          os_version=None, metadata={}):
    instance_id = instance_id or "e7d44dea-21c1-452c-b50c-cbab0d07d7d3"
    os_type = os_type or "linux"
    os_distro = os_distro or "centos"
    os_version = os_version or "6.4"
    hostname = hostname or "to.to"
    display_name = display_name or "to.to"
    tenant_id = tenant_id or "0be9215b503b43279ae585d50a33aed8"
    instance_type = instance_type or "myflavor"
    instance_flavor_id = instance_flavor_id or "201"
    timestamp = timestamp if timestamp else "2014-02-14T16:30:10.453532Z"
    created_at = _format_date(created_at) if created_at else "2014-02-14T16:29:58.000000Z"
    launched_at = _format_date(launched_at) if launched_at else "2014-02-14T16:30:10.221171Z"
    deleted_at = _format_date(deleted_at) if deleted_at else ""
    terminated_at = _format_date(terminated_at) if terminated_at else ""
    state = state or "active"
    metadata = metadata

    if not isinstance(timestamp, datetime):
        timestamp = dateutil.parser.parse(timestamp)

    return {
        "event_type": event_type,
        "payload": {
            "state_description": "",
            "availability_zone": None,
            "terminated_at": terminated_at,
            "ephemeral_gb": 0,
            "instance_type_id": 12,
            "message": "Success",
            "deleted_at": deleted_at,
            "memory_mb": 1024,
            "user_id": "2525317304464dc3a03f2a63e99200c8",
            "reservation_id": "r-7e68nhfk",
            "hostname": hostname,
            "state": state,
            "launched_at": launched_at,
            "metadata": [],
            "node": "mynode.domain.tld",
            "ramdisk_id": "",
            "access_ip_v6": None,
            "disk_gb": 50,
            "access_ip_v4": None,
            "kernel_id": "",
            "image_name": "CentOS 6.4 x86_64",
            "host": "node02",
            "display_name": display_name,
            "root_gb": 50,
            "tenant_id": tenant_id,
            "created_at": created_at,
            "instance_id": instance_id,
            "instance_type": instance_type,
            "vcpus": 1,
            "image_meta": {
                "min_disk": "50",
                "container_format": "bare",
                "min_ram": "256",
                "disk_format": "qcow2",
                "build_version": "68",
                "version": os_version,
                "architecture": "x86_64",
                "auto_disk_config": "True",
                "os_type": os_type,
                "base_image_ref": "ea0d5e26-a272-462a-9333-1e38813bac7b",
                "distro": os_distro
            },
            "architecture": "x86_64",
            "os_type": "linux",
            "instance_flavor_id": instance_flavor_id,
            "metadata": metadata
        },
        "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "updated_at": _format_date(timestamp - timedelta(seconds=10)),
    }


def _get_volume_icehouse_payload(event_type, volume_id=None, tenant_id=None, display_name=None, volume_type=None,
                                 volume_size=None, timestamp=None, created_at=None, launched_at=None, status=None,
                                 attached_to=None):
    volume_id = volume_id or "64a0ca7f-5f5a-4dc5-a1e1-e04e89eb95ed"
    tenant_id = tenant_id or "46eeb8e44298460899cf4b3554bfe11f"
    display_name = display_name or "mytenant-0001-myvolume"
    volume_type = volume_type or DEFAULT_VOLUME_TYPE
    volume_size = volume_size or 50
    timestamp = timestamp if timestamp else "2014-02-14T17:18:40.888401Z"
    created_at = _format_date(created_at) if created_at else "2014-02-14T17:18:35.000000Z"
    launched_at = _format_date(launched_at) if launched_at else "2014-02-14T17:18:40.765844Z"
    status = status or "available"
    attached_to = attached_to or "e7d44dea-21c1-452c-b50c-cbab0d07d7d3"

    if not isinstance(timestamp, datetime):
        timestamp = dateutil.parser.parse(timestamp)

    return {
        "event_type": event_type,
        "timestamp": launched_at,
        "publisher_id": "volume.cinder01",
        "payload": {
            "instance_uuid": attached_to,
            "status": status,
            "display_name": display_name,
            "availability_zone": "nova",
            "tenant_id": tenant_id,
            "created_at": created_at,
            "snapshot_id": None,
            "volume_type": volume_type,
            "volume_id": volume_id,
            "user_id": "ebc0d5a5ecf3417ca0d4f8c90d682f6e",
            "launched_at": launched_at,
            "size": volume_size,
        },
        "priority": "INFO",
        "updated_at": _format_date(timestamp - timedelta(seconds=10)),

    }


def _get_volume_kilo_payload(event_type, volume_id=None, tenant_id=None, display_name=None, volume_type=None,
                             timestamp=None, attached_to=None, volume_size=1):
    volume_id = volume_id or "64a0ca7f-5f5a-4dc5-a1e1-e04e89eb95ed"
    tenant_id = tenant_id or "46eeb8e44298460899cf4b3554bfe11f"
    display_name = display_name or "mytenant-0001-myvolume"
    volume_type = volume_type or DEFAULT_VOLUME_TYPE
    timestamp = timestamp if timestamp else "2014-02-14T17:18:40.888401Z"
    attached_to = attached_to
    volume_attachment = []

    if not isinstance(timestamp, datetime):
        timestamp = dateutil.parser.parse(timestamp)

    for instance_id in attached_to:
        volume_attachment.append({
            "instance_uuid": instance_id,
            "attach_time": _format_date(timestamp - timedelta(seconds=10)),
            "deleted": False,
            "attach_mode": "ro",
            "created_at": _format_date(timestamp - timedelta(seconds=10)),
            "attached_host": "",
            "updated_at": _format_date(timestamp - timedelta(seconds=10)),
            "attach_status": 'available',
            "detach_time": "",
            "volume_id": volume_id,
            "mountpoint": "/dev/vdd",
            "deleted_at": "",
            "id": "228345ee-0520-4d45-86fa-1e4c9f8d057d"
        })

    return {
        "event_type": event_type,
        "timestamp": _format_date(timestamp),
        "publisher_id": "volume.cinder01",
        "payload": {
            "status": "in-use",
            "display_name": display_name,
            "volume_attachment": volume_attachment,
            "availability_zone": "nova",
            "tenant_id": tenant_id,
            "created_at": "2015-07-27T16:11:07Z",
            "volume_id": volume_id,
            "volume_type": volume_type,
            "host": "web@lvmdriver-1#lvmdriver-1",
            "replication_status": "disabled",
            "user_id": "aa518ac79d4c4d61b806e64600fcad21",
            "metadata": [],
            "launched_at": "2015-07-27T16:11:08Z",
            "size": volume_size
        },
        "priority": "INFO",
        "updated_at": _format_date(timestamp - timedelta(seconds=10)),
    }


def get_instance_rebuild_end_sample():
    return _get_instance_payload("compute.instance.rebuild.end")


def get_instance_resized_end_sample():
    return _get_instance_payload("compute.instance.resize.confirm.end")


def get_volume_update_end_sample(volume_id=None, tenant_id=None, volume_type=None, volume_size=None,
                                 creation_timestamp=None, deletion_timestamp=None, name=None):
    kwargs = {
        "volume_id": volume_id or "64a0ca7f-5f5a-4dc5-a1e1-e04e89eb95ed",
        "tenant_id": tenant_id or "46eeb8e44298460899cf4b3554bfe11f",
        "display_name": name or "mytenant-0001-myvolume",
        "volume_type": volume_type or DEFAULT_VOLUME_TYPE,
        "volume_size": volume_size or 50,
        "created_at": creation_timestamp if creation_timestamp else datetime(2014, 2, 14, 17, 18, 35, tzinfo=pytz.utc),
        "launched_at": deletion_timestamp if deletion_timestamp else datetime(2014, 2, 23, 8, 1, 58, tzinfo=pytz.utc),
        "timestamp": deletion_timestamp if deletion_timestamp else datetime(2014, 2, 23, 8, 1, 58, tzinfo=pytz.utc),
        "status": "deleting"
    }
    return _get_volume_icehouse_payload("volume.resize.end", **kwargs)


def get_volume_type_create_sample(volume_type_id, volume_type_name):
    return {
        "event_type": "volume_type.create",
        "publisher_id": "volume.cinder01",
        "payload": {
            "volume_types": {
                "name": volume_type_name,
                "qos_specs_id": None,
                "deleted": False,
                "created_at": "2014-02-14T17:18:35.036186Z",
                "extra_specs": {},
                "deleted_at": None,
                "id": volume_type_id,
            }
        },
        "updated_at": "2014-02-14T17:18:35.036186Z",
    }
