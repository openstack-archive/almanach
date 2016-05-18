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

import logging
import json
from datetime import datetime
from functools import wraps

import jsonpickle

from flask import Blueprint, Response, request

from werkzeug.wrappers import BaseResponse

from almanach.common.exceptions.almanach_entity_not_found_exception import AlmanachEntityNotFoundException
from almanach.common.exceptions.multiple_entities_matching_query import MultipleEntitiesMatchingQuery
from almanach.common.exceptions.validation_exception import InvalidAttributeException
from almanach import config
from almanach.common.exceptions.date_format_exception import DateFormatException

api = Blueprint("api", __name__)
controller = None


def to_json(api_call):
    def encode(data):
        return jsonpickle.encode(data, unpicklable=False)

    @wraps(api_call)
    def decorator(*args, **kwargs):
        try:
            result = api_call(*args, **kwargs)
            return result if isinstance(result, BaseResponse) \
                else Response(encode(result), 200, {"Content-Type": "application/json"})
        except DateFormatException as e:
            logging.warning(e.message)
            return Response(encode({"error": e.message}), 400, {"Content-Type": "application/json"})
        except KeyError as e:
            message = "The '{param}' param is mandatory for the request you have made.".format(param=e.message)
            logging.warning(message)
            return encode({"error": message}), 400, {"Content-Type": "application/json"}
        except TypeError:
            message = "The request you have made must have data. None was given."
            logging.warning(message)
            return encode({"error": message}), 400, {"Content-Type": "application/json"}
        except InvalidAttributeException as e:
            logging.warning(e.get_error_message())
            return encode({"error": e.get_error_message()}), 400, {"Content-Type": "application/json"}
        except MultipleEntitiesMatchingQuery as e:
            logging.warning(e.message)
            return encode({"error": "Multiple entities found while updating closed"}), 400, {
                "Content-Type": "application/json"}
        except AlmanachEntityNotFoundException as e:
            logging.warning(e.message)
            return encode({"error": "Entity not found for updating closed"}), 400, {"Content-Type": "application/json"}

        except Exception as e:
            logging.exception(e)
            return Response(encode({"error": e.message}), 500, {"Content-Type": "application/json"})

    return decorator


def authenticated(api_call):
    @wraps(api_call)
    def decorator(*args, **kwargs):
        auth_token = request.headers.get('X-Auth-Token')
        if auth_token == config.api_auth_token():
            return api_call(*args, **kwargs)
        else:
            return Response('Unauthorized', 401)

    return decorator


@api.route("/info", methods=["GET"])
@to_json
def get_info():
    logging.info("Get application info")
    return controller.get_application_info()


@api.route("/project/<project_id>/instance", methods=["POST"])
@authenticated
@to_json
def create_instance(project_id):
    instance = json.loads(request.data)
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

    return Response(status=201)


@api.route("/instance/<instance_id>", methods=["DELETE"])
@authenticated
@to_json
def delete_instance(instance_id):
    data = json.loads(request.data)
    logging.info("Deleting instance with id %s with data %s", instance_id, data)
    controller.delete_instance(
        instance_id=instance_id,
        delete_date=data['date']
    )

    return Response(status=202)


@api.route("/instance/<instance_id>/resize", methods=["PUT"])
@authenticated
@to_json
def resize_instance(instance_id):
    instance = json.loads(request.data)
    logging.info("Resizing instance with id %s with data %s", instance_id, instance)
    controller.resize_instance(
        instance_id=instance_id,
        resize_date=instance['date'],
        flavor=instance['flavor']
    )

    return Response(status=200)


@api.route("/instance/<instance_id>/rebuild", methods=["PUT"])
@authenticated
@to_json
def rebuild_instance(instance_id):
    instance = json.loads(request.data)
    logging.info("Rebuilding instance with id %s with data %s", instance_id, instance)
    controller.rebuild_instance(
        instance_id=instance_id,
        distro=instance['distro'],
        version=instance['version'],
        os_type=instance['os_type'],
        rebuild_date=instance['rebuild_date'],
    )

    return Response(status=200)


@api.route("/project/<project_id>/instances", methods=["GET"])
@authenticated
@to_json
def list_instances(project_id):
    start, end = get_period()
    logging.info("Listing instances between %s and %s", start, end)
    return controller.list_instances(project_id, start, end)


@api.route("/project/<project_id>/volume", methods=["POST"])
@authenticated
@to_json
def create_volume(project_id):
    volume = json.loads(request.data)
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

    return Response(status=201)


@api.route("/volume/<volume_id>", methods=["DELETE"])
@authenticated
@to_json
def delete_volume(volume_id):
    data = json.loads(request.data)
    logging.info("Deleting volume with id %s with data %s", volume_id, data)
    controller.delete_volume(
        volume_id=volume_id,
        delete_date=data['date']
    )

    return Response(status=202)


@api.route("/volume/<volume_id>/resize", methods=["PUT"])
@authenticated
@to_json
def resize_volume(volume_id):
    volume = json.loads(request.data)
    logging.info("Resizing volume with id %s with data %s", volume_id, volume)
    controller.resize_volume(
        volume_id=volume_id,
        size=volume['size'],
        update_date=volume['date']
    )

    return Response(status=200)


@api.route("/volume/<volume_id>/attach", methods=["PUT"])
@authenticated
@to_json
def attach_volume(volume_id):
    volume = json.loads(request.data)
    logging.info("Attaching volume with id %s with data %s", volume_id, volume)
    controller.attach_volume(
        volume_id=volume_id,
        date=volume['date'],
        attachments=volume['attachments']
    )

    return Response(status=200)


@api.route("/volume/<volume_id>/detach", methods=["PUT"])
@authenticated
@to_json
def detach_volume(volume_id):
    volume = json.loads(request.data)
    logging.info("Detaching volume with id %s with data %s", volume_id, volume)
    controller.detach_volume(
        volume_id=volume_id,
        date=volume['date'],
        attachments=volume['attachments']
    )

    return Response(status=200)


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
    data = json.loads(request.data)
    logging.info("Updating instance entity with id %s with data %s", instance_id, data)
    if 'start' in request.args:
        start, end = get_period()
        result = controller.update_inactive_entity(instance_id=instance_id, start=start, end=end, **data)
    else:
        result = controller.update_active_instance_entity(instance_id=instance_id, **data)
    return result


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
    volume_type = json.loads(request.data)
    logging.info("Creating volume type with data '%s'", volume_type)
    controller.create_volume_type(
        volume_type_id=volume_type['type_id'],
        volume_type_name=volume_type['type_name']
    )
    return Response(status=201)


@api.route("/volume_type/<type_id>", methods=["DELETE"])
@authenticated
@to_json
def delete_volume_type(type_id):
    logging.info("Deleting volume type with id '%s'", type_id)
    controller.delete_volume_type(type_id)
    return Response(status=202)


def get_period():
    start = datetime.strptime(request.args["start"], "%Y-%m-%d %H:%M:%S.%f")
    if "end" not in request.args:
        end = datetime.now()
    else:
        end = datetime.strptime(request.args["end"], "%Y-%m-%d %H:%M:%S.%f")
    return start, end
