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
    return app_ctl.get_application_info()


@api.route("/project/<project_id>/instance", methods=["POST"])
@authenticated
@to_json
def create_instance(project_id):
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
    start, end = get_period()
    LOG.info("Listing instances between %s and %s", start, end)
    return instance_ctl.list_instances(project_id, start, end)


@api.route("/project/<project_id>/volume", methods=["POST"])
@authenticated
@to_json
def create_volume(project_id):
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
    start, end = get_period()
    LOG.info("Listing volumes between %s and %s", start, end)
    return volume_ctl.list_volumes(project_id, start, end)


@api.route("/project/<project_id>/entities", methods=["GET"])
@authenticated
@to_json
def list_entity(project_id):
    start, end = get_period()
    LOG.info("Listing entities between %s and %s", start, end)
    return entity_ctl.list_entities(project_id, start, end)


@api.route("/entity/instance/<instance_id>", methods=["PUT"])
@authenticated
@to_json
def update_instance_entity(instance_id):
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
    LOG.info("Does entity with id %s exists", entity_id)
    response = flask.Response('', 404)
    if entity_ctl.entity_exists(entity_id=entity_id):
        response = flask.Response('', 200)
    return response


@api.route("/entity/<entity_id>", methods=["GET"])
@authenticated
@to_json
def get_entity(entity_id):
    return entity_ctl.get_all_entities_by_id(entity_id)


@api.route("/volume_types", methods=["GET"])
@authenticated
@to_json
def list_volume_types():
    LOG.info("Listing volumes types")
    return volume_type_ctl.list_volume_types()


@api.route("/volume_type/<volume_type_id>", methods=["GET"])
@authenticated
@to_json
def get_volume_type(volume_type_id):
    LOG.info("Get volumes type for id %s", volume_type_id)
    return volume_type_ctl.get_volume_type(volume_type_id)


@api.route("/volume_type", methods=["POST"])
@authenticated
@to_json
def create_volume_type():
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
