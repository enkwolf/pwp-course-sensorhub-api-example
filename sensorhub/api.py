from flask import Blueprint
from flask_restful import Api

from sensorhub.resources.sensor import SensorCollection, SensorItem
from sensorhub.resources.location import LocationItem, LocationSensorPairing
from sensorhub.resources.measurement import MeasurementCollection

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(SensorCollection, "/sensors/")
api.add_resource(SensorItem, "/sensors/<sensor>/")
api.add_resource(LocationItem, "/locations/<location>/")
api.add_resource(MeasurementCollection, "/sensors/<sensor>/measurements/")
api.add_resource(LocationSensorPairing, "/locations/<location>/<sensor>/")