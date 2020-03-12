import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sensorhub import db
from sensorhub.models import Location, Sensor
from sensorhub.constants import *
from sensorhub.utils import SensorhubBuilder, create_error_response


class LocationCollection(Resource):

    def get(self):
        pass


class LocationItem(Resource):

    def get(self, location):
        db_loc = Location.query.filter_by(name=location).first()
        if db_loc is None:
            return create_error_response(
                404, "Not found",
                "No location was found with the name {}".format(location)
            )

        body = SensorhubBuilder(
            name=db_loc.name,
            latitude=db_loc.latitude,
            longitude=db_loc.longitude,
            altitude=db_loc.altitude,
            description=db_loc.description
        )
        body.add_namespace("senhub", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.locationitem", location=location))
        body.add_control("profile", LOCATION_PROFILE)
        body.add_control("collection", url_for("api.locationcollection"))
        if db_loc.sensor is not None:
            body.add_control(
                "senhub:sensor",
                url_for("api.sensoritem", sensor=db_loc.sensor)
            )
            body.add_control_change_sensor(location)
            body.add_control_remove_sensor(location)
        else:
            body.add_control_assign_sensor(location)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, location):
        db_loc = Location.query.filter_by(name=location).first()
        if db_loc is None:
            return create_error_response(
                404, "Not found",
                "No location was found with the name {}".format(location)
            )

        if db_loc.sensor is not None:
            return create_error_response(
                409, "Location '{}' already contains a sensor.",
                "Use the 'senhub:change-sensor' control to change to another sensor."
            )

        try:
            validate(request.json, Location.get_pairing_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        sensor = request.json["sensor_name"]
        db_sensor = Sensor.query.filter_by(name=sensor).first()
        if db_sensor is None:
            return create_error_response(
                404, "Not found",
                "No sensor was found with the name {}".format(sensor)
            )

        db_loc.sensor = db_sensor
        try:
            db.session.commit()
        except IntegrityError as e:
            return create_error_response(
                409, "Sensor already assigned",
                "Sensor with name '{}' has already been assigned to another location.".format(sensor)
            )

        return Response(status=201, headers={
            "Location": url_for("locationsensorpairing", location=location, sensor=sensor)
        })


class LocationSensorPairing(Resource):

    def put(self, location, sensor):
        raise NotImplementedError
