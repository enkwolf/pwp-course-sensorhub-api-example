import json
from flask import request, Response, url_for
from flask_restful import Resource
from sensorhub import cache
from sensorhub.constants import *
from sensorhub.models import Measurement, Sensor
from sensorhub.utils import SensorhubBuilder, create_error_response, page_key, require_sensor_key


class MeasurementItem(Resource):

    def get(self, sensor, measurement):
        pass


class MeasurementCollection(Resource):

    @cache.cached(timeout=None, make_cache_key=page_key, response_filter=lambda r: False)
    def get(self, sensor):
        print("Not Cached")

        try:
            start = int(request.args.get("start", 0))
        except ValueError:
            return create_error_response(400, "Invalid query string value")

        remaining = Measurement.query.filter_by(sensor=sensor).order_by("time").offset(start)

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

        response = Response(json.dumps(body), 200, mimetype=MASON)
        if len(body["items"]) == MEASUREMENT_PAGE_SIZE:
            cache.set(page_key(), response, timeout=None)
        return response

    @require_sensor_key
    def post(self, sensor):
        return Response(501)
        