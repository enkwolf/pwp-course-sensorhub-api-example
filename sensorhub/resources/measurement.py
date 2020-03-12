import json
from flask import request, Response, url_for
from flask_restful import Resource
from sensorhub.constants import *
from sensorhub.models import Measurement, Sensor
from sensorhub.utils import SensorhubBuilder, create_error_response

class MeasurementItem(Resource):

    def get(self, sensor, measurement):
        pass


class MeasurementCollection(Resource):

    def get(self, sensor):
        db_sensor = Sensor.query.filter_by(name=sensor).first()
        if db_sensor is None:
            return create_error_response(
                404, "Not found",
                "No sensor was found with the name {}".format(sensor)
            )

        try:
            start = int(request.args.get("start", 0))
        except ValueError:
            return create_error_response(400, "Invalid query string value")

        remaining = Measurement.query.filter_by(sensor=db_sensor).order_by("time").offset(start)

        body = SensorhubBuilder(
            items=[]
        )
        body.add_namespace("senhub", LINK_RELATIONS_URL)
        base_uri = url_for("api.measurementcollection", sensor=sensor)
        body.add_control("up", url_for("api.sensoritem", sensor=sensor))
        if start >= 50:
            body.add_control("self", base_uri + "?start={}".format(start))
            body.add_control("prev", base_uri + "?start={}".format(start - MEASUREMENT_PAGE_SIZE))
        else:
            body.add_control("self", base_uri)
        if remaining.count() > 50:
            body.add_control("next", base_uri + "?start={}".format(start + MEASUREMENT_PAGE_SIZE))

        for meas in remaining.limit(MEASUREMENT_PAGE_SIZE):
            item = SensorhubBuilder(
                value=meas.value,
                time=meas.time.isoformat()
            )
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)
