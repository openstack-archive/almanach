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
import logging

import flask
import jsonpickle
from oslo_serialization import jsonutils
from werkzeug import wrappers

from almanach.common.exceptions import almanach_entity_not_found_exception
from almanach.common.exceptions import almanach_exception
from almanach.common.exceptions import authentication_failure_exception
from almanach.common.exceptions import date_format_exception
from almanach.common.exceptions import multiple_entities_matching_query
from almanach.common.exceptions import validation_exception

api = flask.Blueprint("api", __name__)
controller = None
auth_adapter = None


def to_json(api_call):
    def encode(data):
        return jsonpickle.encode(data, unpicklable=False)

    @wraps(api_call)
    def decorator(*args, **kwargs):
        try:
            result = api_call(*args, **kwargs)
            return result if isinstance(result, wrappers.BaseResponse) \
                else flask.Response(encode(result), 200, {"Content-Type": "application/json"})
        except date_format_exception.DateFormatException as e:
            logging.warning(e.message)
            return flask.Response(encode({"error": e.message}), 400, {"Content-Type": "application/json"})
        except KeyError as e:
            message = "The {param} param is mandatory for the request you have made.".format(param=e)
            logging.warning(message)
            return encode({"error": message}), 400, {"Content-Type": "application/json"}
        except TypeError:
            message = "The request you have made must have data. None was given."
            logging.warning(message)
            return encode({"error": message}), 400, {"Content-Type": "application/json"}
        except validation_exception.InvalidAttributeException as e:
            logging.warning(e.get_error_message())
            return encode({"error": e.get_error_message()}), 400, {"Content-Type": "application/json"}
        except multiple_entities_matching_query.MultipleEntitiesMatchingQuery as e:
            logging.warning(e.message)
            return encode({"error": "Multiple entities found while updating closed"}), 400, {
                "Content-Type": "application/json"}
        except almanach_entity_not_found_exception.AlmanachEntityNotFoundException as e:
            logging.warning(e.message)
            return encode({"error": "Entity not found"}), 404, {"Content-Type": "application/json"}
        except almanach_exception.AlmanachException as e:
            logging.exception(e)
            return flask.Response(encode({"error": e.message}), 500, {"Content-Type": "application/json"})
        except Exception as e:
            logging.exception(e)
            return flask.Response(encode({"error": e}), 500, {"Content-Type": "application/json"})

    return decorator


def authenticated(api_call):
    @wraps(api_call)
    def decorator(*args, **kwargs):
        try:
            auth_adapter.validate(flask.request.headers.get('X-Auth-Token'))
            return api_call(*args, **kwargs)
        except authentication_failure_exception.AuthenticationFailureException as e:
            logging.error("Authentication failure: {0}".format(e))
            return flask.Response('Unauthorized', 401)

    return decorator


@api.route("/info", methods=["GET"])
@to_json
def get_info():
    """Displays information about the current version and counts of entities in the database.

    :return: version and database counts of entities
    """
    logging.info("Get application info")
    return controller.get_application_info()


@api.route("/project/<project_id>/instance", methods=["POST"])
@authenticated
@to_json
def create_instance(project_id):
    """Create an instance for a tenant.

    :arg uuid project_id: Tenant Uuid

    :code 201 Created:

    :return:
    """
    instance = jsonutils.loads(flask.request.data)
    logging.info("Creating instance for tenant %s with data %s", project_id, instance)
    controller.create_instance(
        tenant_id=project_id,
        instance_id=instance['id'],
        create_date=instance['created_at'],
        flavor=instance['flavor'],
        os_type=instance['os_type'],
        distro=instance['os_distro'],
        version=instance['os_version'],
        name=instance['name'],
        metadata={}
    )

    return flask.Response(status=201)


@api.route("/instance/<instance_id>", methods=["DELETE"])
@authenticated
@to_json
def delete_instance(instance_id):
    """Deletes the instance.

    :arg uuid instance_id: Instance Uuid

    :raises: AlmanachEntityNotFoundException if instance not found

    :code 202 Accepted:

    :return:
    """
    data = jsonutils.loads(flask.request.data)
    logging.info("Deleting instance with id %s with data %s", instance_id, data)
    controller.delete_instance(
        instance_id=instance_id,
        delete_date=data['date']
    )

    return flask.Response(status=202)


@api.route("/instance/<instance_id>/resize", methods=["PUT"])
@authenticated
@to_json
def resize_instance(instance_id):
    """Resizes an instance when the instance flavor was changed in OpenStack.

    :arg uuid instance_id: Instance Uuid

    :raises: KeyError if instance does not exist

    :code 200 OK:

    :return:
    """
    instance = jsonutils.loads(flask.request.data)
    logging.info("Resizing instance with id %s with data %s", instance_id, instance)
    controller.resize_instance(
        instance_id=instance_id,
        resize_date=instance['date'],
        flavor=instance['flavor']
    )

    return flask.Response(status=200)


@api.route("/instance/<instance_id>/rebuild", methods=["PUT"])
@authenticated
@to_json
def rebuild_instance(instance_id):
    """Rebuilds an instance when the instance image was changed in OpenStack.

    :arg uuid instance_id: Instance Uuid

    :code 200 OK:

    :return:
    """
    instance = jsonutils.loads(flask.request.data)
    logging.info("Rebuilding instance with id %s with data %s", instance_id, instance)
    controller.rebuild_instance(
        instance_id=instance_id,
        distro=instance['distro'],
        version=instance['version'],
        os_type=instance['os_type'],
        rebuild_date=instance['rebuild_date'],
    )

    return flask.Response(status=200)


@api.route("/project/<project_id>/instances", methods=["GET"])
@authenticated
@to_json
def list_instances(project_id):
    """Lists instances for a tenant.

    :arg uuid project_id: Tenant Uuid
    :arg datetime start: Y-m-d H:M:S.f
    :arg datetime end: Y-m-d H:M:S.f


    :return: a list of instances
    """
    start, end = get_period()
    logging.info("Listing instances between %s and %s", start, end)
    return controller.list_instances(project_id, start, end)


@api.route("/project/<project_id>/volume", methods=["POST"])
@authenticated
@to_json
def create_volume(project_id):
    volume = jsonutils.loads(flask.request.data)
    logging.info("Creating volume for tenant %s with data %s", project_id, volume)
    controller.create_volume(
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
    logging.info("Deleting volume with id %s with data %s", volume_id, data)
    controller.delete_volume(
        volume_id=volume_id,
        delete_date=data['date']
    )

    return flask.Response(status=202)


@api.route("/volume/<volume_id>/resize", methods=["PUT"])
@authenticated
@to_json
def resize_volume(volume_id):
    volume = jsonutils.loads(flask.request.data)
    logging.info("Resizing volume with id %s with data %s", volume_id, volume)
    controller.resize_volume(
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
    logging.info("Attaching volume with id %s with data %s", volume_id, volume)
    controller.attach_volume(
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
    logging.info("Detaching volume with id %s with data %s", volume_id, volume)
    controller.detach_volume(
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
    logging.info("Listing volumes between %s and %s", start, end)
    return controller.list_volumes(project_id, start, end)


@api.route("/project/<project_id>/entities", methods=["GET"])
@authenticated
@to_json
def list_entity(project_id):
    start, end = get_period()
    logging.info("Listing entities between %s and %s", start, end)
    return controller.list_entities(project_id, start, end)


@api.route("/entity/instance/<instance_id>", methods=["PUT"])
@authenticated
@to_json
def update_instance_entity(instance_id):
    data = jsonutils.loads(flask.request.data)
    logging.info("Updating instance entity with id %s with data %s", instance_id, data)
    if 'start' in flask.request.args:
        start, end = get_period()
        result = controller.update_inactive_entity(instance_id=instance_id, start=start, end=end, **data)
    else:
        result = controller.update_active_instance_entity(instance_id=instance_id, **data)
    return result


@api.route("/entity/<entity_id>", methods=["HEAD"])
@authenticated
def entity_exists(entity_id):
    logging.info("Does entity with id %s exists", entity_id)
    response = flask.Response('', 404)
    if controller.entity_exists(entity_id=entity_id):
        response = flask.Response('', 200)
    return response


@api.route("/entity/<entity_id>", methods=["GET"])
@authenticated
@to_json
def get_entity(entity_id):
    return controller.get_all_entities_by_id(entity_id)


@api.route("/volume_types", methods=["GET"])
@authenticated
@to_json
def list_volume_types():
    logging.info("Listing volumes types")
    return controller.list_volume_types()


@api.route("/volume_type/<type_id>", methods=["GET"])
@authenticated
@to_json
def get_volume_type(type_id):
    logging.info("Get volumes type for id %s", type_id)
    return controller.get_volume_type(type_id)


@api.route("/volume_type", methods=["POST"])
@authenticated
@to_json
def create_volume_type():
    volume_type = jsonutils.loads(flask.request.data)
    logging.info("Creating volume type with data '%s'", volume_type)
    controller.create_volume_type(
        volume_type_id=volume_type['type_id'],
        volume_type_name=volume_type['type_name']
    )
    return flask.Response(status=201)


@api.route("/volume_type/<type_id>", methods=["DELETE"])
@authenticated
@to_json
def delete_volume_type(type_id):
    logging.info("Deleting volume type with id '%s'", type_id)
    controller.delete_volume_type(type_id)
    return flask.Response(status=202)


def get_period():
    start = datetime.strptime(flask.request.args["start"], "%Y-%m-%d %H:%M:%S.%f")
    if "end" not in flask.request.args:
        end = datetime.now()
    else:
        end = datetime.strptime(flask.request.args["end"], "%Y-%m-%d %H:%M:%S.%f")
    return start, end
