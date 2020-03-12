import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from sensorhub.models import Sensor
from sensorhub import db
from sensorhub.utils import SensorhubBuilder, create_error_response
from sensorhub.constants import *


class SensorCollection(Resource):

    def get(self):
        body = SensorhubBuilder()

        body.add_namespace("senhub", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.sensorcollection"))
        body.add_control_add_sensor()
        body["items"] = []
        for db_sensor in Sensor.query.all():
            item = SensorhubBuilder(
                name=db_sensor.name,
                model=db_sensor.model,
                location=db_sensor.location and db_sensor.location.name
            )
            item.add_control("self", url_for("api.sensoritem", sensor=db_sensor.name))
            item.add_control("profile", SENSOR_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Sensor.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        sensor = Sensor(
            name=request.json["name"],
            model=request.json["model"],
        )

        try:
            db.session.add(sensor)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Sensor with name '{}' already exists.".format(request.json["name"])
            )

        return Response(status=201, headers={
            "Location": url_for("api.sensoritem", sensor=request.json["name"])
        })


class SensorItem(Resource):

    def get(self, sensor):
        db_sensor = Sensor.query.filter_by(name=sensor).first()
        if db_sensor is None:
            return create_error_response(
                404, "Not found",
                "No sensor was found with the name {}".format(sensor)
            )

        body = SensorhubBuilder(
            name=db_sensor.name,
            model=db_sensor.model,
            location=db_sensor.location and db_sensor.location.name
        )
        body.add_namespace("senhub", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.sensoritem", sensor=sensor))
        body.add_control("profile", SENSOR_PROFILE)
        body.add_control("collection", url_for("api.sensorcollection"))
        body.add_control_delete_sensor(sensor)
        body.add_control_modify_sensor(sensor)
        body.add_control_add_measurement(sensor)
        body.add_control_get_measurements(sensor)
        body.add_control(
            "senhub:measurements-first",
            url_for("api.measurementcollection", sensor=sensor)
        )
        if db_sensor.location is not None:
            body.add_control(
                "senhub:location",
                url_for("api.locationitem", location=db_sensor.location.sensor)
            )

        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, sensor):
        db_sensor = Sensor.query.filter_by(name=sensor).first()
        if db_sensor is None:
            return create_error_response(
                404, "Not found",
                "No sensor was found with the name {}".format(sensor)
            )

        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Sensor.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        db_sensor.name = request.json["name"]
        db_sensor.model = request.json["model"]

        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Sensor with name '{}' already exists.".format(request.json["name"])
            )

        return Response(status=204)

    def delete(self, sensor):
        db_sensor = Sensor.query.filter_by(name=sensor).first()
        if db_sensor is None:
            return create_error_response(
                404, "Not found",
                "No sensor was found with the name {}".format(sensor)
            )

        db.session.delete(db_sensor)
        db.session.commit()

        return Response(status=204)
