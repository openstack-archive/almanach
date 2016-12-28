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

from datetime import datetime
from functools import wraps

import flask
import jsonpickle
from oslo_log import log
from oslo_serialization import jsonutils
from werkzeug import wrappers

from almanach.core import exception

LOG = log.getLogger(__name__)
api = flask.Blueprint("api", __name__)
instance_ctl = None
volume_ctl = None
volume_type_ctl = None
entity_ctl = None
app_ctl = None
auth_adapter = None


def to_json(api_call):
    def encode_result(data):
        return jsonpickle.encode(data, unpicklable=False)

    def send_response(data, status_code):
        return flask.Response(encode_result(data), status_code, {"Content-Type": "application/json"})

    @wraps(api_call)
    def decorator(*args, **kwargs):
        try:
            result = api_call(*args, **kwargs)
            return result if isinstance(result, wrappers.BaseResponse) else send_response(result, 200)
        except (exception.DateFormatException, exception.MultipleEntitiesMatchingQueryException) as e:
            LOG.warning(e.message)
            return send_response({"error": e.message}, 400)
        except KeyError as e:
            message = "The {} param is mandatory for the request you have made.".format(e)
            LOG.warning(message)
            return send_response({"error": message}, 400)
        except (TypeError, ValueError):
            message = "Invalid parameter or payload"
            LOG.warning(message)
            return send_response({"error": message}, 400)
        except exception.InvalidAttributeException as e:
            LOG.warning(e.get_error_message())
            return send_response({"error": e.get_error_message()}, 400)
        except (exception.EntityNotFoundException, exception.VolumeTypeNotFoundException) as e:
            LOG.warning(e.message)
            return send_response({"error": e.message}, 404)
        except exception.AlmanachException as e:
            LOG.exception(e)
            return send_response({"error": e.message}, 500)
        except Exception as e:
            LOG.exception(e)
            return send_response({"error": e}, 500)

    return decorator


def authenticated(api_call):
    @wraps(api_call)
    def decorator(*args, **kwargs):
        try:
            auth_adapter.validate(flask.request.headers.get('X-Auth-Token'))
            return api_call(*args, **kwargs)
        except exception.AuthenticationFailureException as e:
            LOG.error("Authentication failure: %s", e.message)
            return flask.Response('Unauthorized', 401)

    return decorator


@api.route("/info", methods=["GET"])
@to_json
def get_info():
    """Display information about the current version and counts of entities in the database.

    :code 200 OK: Service is available

    Example output:

    .. literalinclude:: ../api_examples/output/info.json
        :language: json
    """
    return app_ctl.get_application_info()


@api.route("/project/<project_id>/instance", methods=["POST"])
@authenticated
@to_json
def create_instance(project_id):
    """Create an instance for a tenant.

    :arg uuid project_id: Tenant Uuid
    :arg uuid id: The instance uuid
    :arg datetime created_at: Y-m-d H:M:S.f
    :arg uuid flavor: The flavor uuid
    :arg str os_type: The OS type
    :arg str os_distro: The OS distro
    :arg str os_version: The OS version
    :arg str name: The instance name

    :code 201 Created: Instance successfully created
    :code 400 Bad Request: If request data has an invalid or missing field
    :code 404 Not Found: If tenant does not exist

    Example input:

    .. literalinclude:: ../api_examples/input/create_instance-body.json
        :language: json
    """
    body = jsonutils.loads(flask.request.data)
    LOG.info("Creating instance for tenant %s with data %s", project_id, body)

    instance_ctl.create_instance(
        tenant_id=project_id,
        instance_id=body['id'],
        create_date=body['created_at'],
        name=body['name'],
        flavor=body['flavor'],
        image_meta=dict(distro=body['os_distro'],
                        version=body['os_version'],
                        os_type=body['os_type'])
    )

    return flask.Response(status=201)


@api.route("/instance/<instance_id>", methods=["DELETE"])
@authenticated
@to_json
def delete_instance(instance_id):
    """Delete the instance.

    :arg uuid instance_id: Instance Uuid
    :arg datetime date: Y-m-d H:M:S.f

    :code 202 Accepted: Instance successfully deleted
    :code 400 Bad Request: If request data has an invalid or missing field
    :code 404 Not Found: If instance does not exist

    Example input:

    .. literalinclude:: ../api_examples/input/delete_instance-body.json
        :language: json
    """
    data = jsonutils.loads(flask.request.data)
    LOG.info("Deleting instance with id %s with data %s", instance_id, data)
    instance_ctl.delete_instance(
        instance_id=instance_id,
        delete_date=data['date']
    )

    return flask.Response(status=202)


@api.route("/instance/<instance_id>/resize", methods=["PUT"])
@authenticated
@to_json
def resize_instance(instance_id):
    """Re-size an instance when the instance flavor was changed in OpenStack.

    :arg uuid instance_id: Instance Uuid
    :arg datetime date: Y-m-d H:M:S.f
    :arg uuid flavor: The flavor uuid

    :code 200 OK:  Instance successfully re-sized
    :code 400 Bad Request: If request data has an invalid or missing field
    :code 404 Not Found: If instance does not exist

    Example input:

    .. literalinclude:: ../api_examples/input/resize_instance-body.json
        :language: json
    """
    instance = jsonutils.loads(flask.request.data)
    LOG.info("Resizing instance with id %s with data %s", instance_id, instance)
    instance_ctl.resize_instance(
        instance_id=instance_id,
        resize_date=instance['date'],
        flavor=instance['flavor']
    )

    return flask.Response(status=200)


@api.route("/instance/<instance_id>/rebuild", methods=["PUT"])
@authenticated
@to_json
def rebuild_instance(instance_id):
    """Rebuild an instance when the instance image was changed in OpenStack.

    :arg uuid instance_id: Instance Uuid
    :arg str distro: The OS distro
    :arg str version: The OS version
    :arg str os_type: The OS type
    :arg datetime rebuild_date: Y-m-d H:M:S.f

    :code 200 OK:  Instance successfully rebuilt
    :code 400 Bad Request: If request data has an invalid or missing field
    :code 404 Not Found: If instance does not exist

    Example input:

    .. literalinclude:: ../api_examples/input/rebuild_instance-body.json
        :language: json
    """
    body = jsonutils.loads(flask.request.data)
    LOG.info("Rebuilding instance with id %s with data %s", instance_id, body)
    instance_ctl.rebuild_instance(
        instance_id=instance_id,
        rebuild_date=body['rebuild_date'],
        image_meta=dict(distro=body['distro'],
                        version=body['version'],
                        os_type=body['os_type'])
    )

    return flask.Response(status=200)


@api.route("/project/<project_id>/instances", methods=["GET"])
@authenticated
@to_json
def list_instances(project_id):
    """List instances for a tenant.

    :arg uuid project_id: Tenant Uuid
    :arg datetime start: Y-m-d H:M:S.f
    :arg datetime end: Y-m-d H:M:S.f

    :code 200 OK: instance list exists
    :code 400 Bad Request: If request data has an invalid or missing field
    :code 404 Not Found: If tenant does not exist.

    Example output:

    .. literalinclude:: ../api_examples/output/instances.json
        :language: json
    """
    start, end = get_period()
    LOG.info("Listing instances between %s and %s", start, end)
    return instance_ctl.list_instances(project_id, start, end)


@api.route("/project/<project_id>/volume", methods=["POST"])
@authenticated
@to_json
def create_volume(project_id):
    """Create a volume for a tenant.

    :arg uuid project_id: Tenant Uuid
    :arg uuid volume_id: The Volume Uuid
    :arg datetime start: Y-m-d H:M:S.f
    :arg uuid volume_type: The Volume Type Uuid
    :arg str size: The Volume Size
    :arg str volume_name: The Volume Name
    :arg uuid attached_to: The Instance Uuid the volume is attached to

    :code 201 Created:  Volume successfully created
    :code 400 Bad Request: If request data has an invalid or missing field
    :code 404 Not Found: If tenant does not exist.

    Example input:

    .. literalinclude:: ../api_examples/input/create_volume-body.json
        :language: json
    """
    volume = jsonutils.loads(flask.request.data)
    LOG.info("Creating volume for tenant %s with data %s", project_id, volume)
    volume_ctl.create_volume(
        project_id=project_id,
        volume_id=volume['volume_id'],
        start=volume['start'],
        volume_type=volume['volume_type'],
        size=volume['size'],
        volume_name=volume['volume_name'],
        attached_to=volume['attached_to']
    )

    return flask.Response(status=201)


@api.route("/volume/<volume_id>", methods=["DELETE"])
@authenticated
@to_json
def delete_volume(volume_id):
    """Delete the volume.

    :arg uuid volume_id: Volume Uuid
    :arg datetime date: Y-m-d H:M:S.f

    :code 202 Accepted: Volume successfully deleted
    :code 400 Bad Request: If data invalid or missing
    :code 404 Not Found: If volume does not exist.
    """
    data = jsonutils.loads(flask.request.data)
    LOG.info("Deleting volume with id %s with data %s", volume_id, data)
    volume_ctl.delete_volume(
        volume_id=volume_id,
        delete_date=data['date']
    )

    return flask.Response(status=202)


@api.route("/volume/<volume_id>/resize", methods=["PUT"])
@authenticated
@to_json
def resize_volume(volume_id):
    """Re-size a volume when the volume size was changed in OpenStack.

    :arg uuid volume_id: Volume Uuid
    :arg str size: The size of the volume
    :arg datetime date: Y-m-d H:M:S.f

    :code 200 OK: Volume successfully re-sized
    :code 400 Bad Request: If request data has an invalid or missing field
    :code 404 Not Found: If volume does not exist.

    Example input:

    .. literalinclude:: ../api_examples/input/resize_volume-body.json
        :language: json
    """
    volume = jsonutils.loads(flask.request.data)
    LOG.info("Resizing volume with id %s with data %s", volume_id, volume)
    volume_ctl.resize_volume(
        volume_id=volume_id,
        size=volume['size'],
        update_date=volume['date']
    )

    return flask.Response(status=200)


@api.route("/volume/<volume_id>/attach", methods=["PUT"])
@authenticated
@to_json
def attach_volume(volume_id):
    """Update the attachments for a volume when the volume attachments have been changed in OpenStack.

    :arg uuid volume_id: Volume Uuid
    :arg datetime date: Y-m-d H:M:S.f
    :arg dict attachments: The volume attachments

    :code 200 OK: Volume successfully attached
    :code 400 Bad Request: If request data has an invalid or missing field
    :code 404 Not Found: If volume does not exist.

    Example input:

    .. literalinclude:: ../api_examples/input/attach_volume-body.json
        :language: json
    """
    volume = jsonutils.loads(flask.request.data)
    LOG.info("Attaching volume with id %s with data %s", volume_id, volume)
    volume_ctl.attach_volume(
        volume_id=volume_id,
        date=volume['date'],
        attachments=volume['attachments']
    )

    return flask.Response(status=200)


@api.route("/volume/<volume_id>/detach", methods=["PUT"])
@authenticated
@to_json
def detach_volume(volume_id):
    """Detaches a volume when the volume is detached in OpenStack.

    :arg uuid volume_id: Volume Uuid

    :code 200 OK: Volume successfully detached
    :code 400 Bad Request: If request data has an invalid or missing field
    :code 404 Not Found: If volume does not exist.

    Example input:

    .. literalinclude:: ../api_examples/input/detach_volume-body.json
        :language: json
    """
    volume = jsonutils.loads(flask.request.data)
    LOG.info("Detaching volume with id %s with data %s", volume_id, volume)
    volume_ctl.detach_volume(
        volume_id=volume_id,
        date=volume['date'],
        attachments=volume['attachments']
    )

    return flask.Response(status=200)


@api.route("/project/<project_id>/volumes", methods=["GET"])
@authenticated
@to_json
def list_volumes(project_id):
    """List volumes for a tenant.

    :arg uuid project_id: Tenant Uuid
    :arg datetime start: Y-m-d H:M:S.f
    :arg datetime end: Y-m-d H:M:S.f

    :code 200 OK: volume list exists
    :code 400 Bad Request: If request data has an invalid or missing field
    :code 404 Not Found: If tenant does not exist.

    Example output:

    .. literalinclude:: ../api_examples/output/volumes.json
        :language: json
    """
    start, end = get_period()
    LOG.info("Listing volumes between %s and %s", start, end)
    return volume_ctl.list_volumes(project_id, start, end)


@api.route("/project/<project_id>/entities", methods=["GET"])
@authenticated
@to_json
def list_entity(project_id):
    """List instances and volumes for a tenant.

    :arg uuid project_id: Tenant Uuid
    :arg datetime start: Y-m-d H:M:S.f
    :arg datetime end: Y-m-d H:M:S.f

    :code 200 OK: instances and volumes list exists
    :code 400 Bad Request: If request data has an invalid or missing field
    :code 404 Not Found: If tenant does not exist.


    Example output:

    .. literalinclude:: ../api_examples/output/entities.json
        :language: json
    """
    start, end = get_period()
    LOG.info("Listing entities between %s and %s", start, end)
    return entity_ctl.list_entities(project_id, start, end)


@api.route("/entity/instance/<instance_id>", methods=["PUT"])
@authenticated
@to_json
def update_instance_entity(instance_id):
    """Update an instance entity.

    :arg uuid instance_id: Instance Uuid
    :arg datetime start: Y-m-d H:M:S.f
    :arg datetime end: Y-m-d H:M:S.f

    :code 200 OK: Entity successfully updated
    :code 400 Bad Request: If request data has an invalid or missing field
    :code 404 Not Found: If instance does not exist.

    Example input:

    .. literalinclude:: ../api_examples/input/update_instance_entity-body.json
        :language: json

    Example output:

    .. literalinclude:: ../api_examples/output/update_instance_entity.json
        :language: json
    """
    data = jsonutils.loads(flask.request.data)
    LOG.info("Updating instance entity with id %s with data %s", instance_id, data)
    if 'start' in flask.request.args:
        start, end = get_period()
        result = entity_ctl.update_inactive_entity(instance_id=instance_id, start=start, end=end, **data)
    else:
        result = entity_ctl.update_active_instance_entity(instance_id=instance_id, **data)
    return result


@api.route("/entity/<entity_id>", methods=["HEAD"])
@authenticated
def entity_exists(entity_id):
    """Verify that an entity exists.

    :arg uuid entity_id: Entity Uuid

    :code 200 OK: if the entity exists
    :code 404 Not Found: if the entity does not exist
    """
    LOG.info("Does entity with id %s exists", entity_id)
    response = flask.Response('', 404)
    if entity_ctl.entity_exists(entity_id=entity_id):
        response = flask.Response('', 200)
    return response


@api.route("/entity/<entity_id>", methods=["GET"])
@authenticated
@to_json
def get_entity(entity_id):
    """Get an entity.

    :arg uuid entity_id: Entity Uuid

    :code 200 OK: Entity exists
    :code 404 Not Found: If the entity does not exist

    Example output:

    .. literalinclude:: ../api_examples/output/entity.json
        :language: json
    """
    return entity_ctl.get_all_entities_by_id(entity_id)


@api.route("/volume_types", methods=["GET"])
@authenticated
@to_json
def list_volume_types():
    """List volume types.

    :code 200 OK: Volume types exist

    Example output:

    .. literalinclude:: ../api_examples/output/volume_types.json
        :language: json
    """
    LOG.info("Listing volumes types")
    return volume_type_ctl.list_volume_types()


@api.route("/volume_type/<volume_type_id>", methods=["GET"])
@authenticated
@to_json
def get_volume_type(volume_type_id):
    """Get a volume type.

    :arg uuid volume_type_id: Volume Type Uuid

    :code 200 OK: Volume type exists
    :code 400 Bad Request: If request data has an invalid or missing field
    :code 404 Not Found: If the volume type does not exist

    Example output:

    .. literalinclude:: ../api_examples/output/volume_type.json
        :language: json
    """
    LOG.info("Get volumes type for id %s", volume_type_id)
    return volume_type_ctl.get_volume_type(volume_type_id)


@api.route("/volume_type", methods=["POST"])
@authenticated
@to_json
def create_volume_type():
    """Create a volume type.

    :arg str type_id: The Volume Type id
    :arg str type_name: The Volume Type name

    :code 201 Created: Volume successfully created
    :code 400 Bad Request: If request data has an invalid or missing field

    Example input:

    .. literalinclude:: ../api_examples/input/create_volume_type-body.json
        :language: json
    """
    volume_type = jsonutils.loads(flask.request.data)
    LOG.info("Creating volume type with data '%s'", volume_type)
    volume_type_ctl.create_volume_type(
        volume_type_id=volume_type['type_id'],
        volume_type_name=volume_type['type_name']
    )
    return flask.Response(status=201)


@api.route("/volume_type/<volume_type_id>", methods=["DELETE"])
@authenticated
@to_json
def delete_volume_type(volume_type_id):
    """Delete the volume type.

    :arg uuid type_id: Volume Type Uuid

    :code 202 Accepted: Volume successfully deleted
    :code 404 Not Found: If volume type does not exist.
    """
    LOG.info("Deleting volume type with id '%s'", volume_type_id)
    volume_type_ctl.delete_volume_type(volume_type_id)
    return flask.Response(status=202)


def get_period():
    start = datetime.strptime(flask.request.args["start"], "%Y-%m-%d %H:%M:%S.%f")
    if "end" not in flask.request.args:
        end = datetime.now()
    else:
        end = datetime.strptime(flask.request.args["end"], "%Y-%m-%d %H:%M:%S.%f")
    return start, end
