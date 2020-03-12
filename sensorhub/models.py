import click
from flask.cli import with_appcontext
from sensorhub import db

deployments = db.Table(
    "deployments",
    db.Column("deployment_id", db.Integer, db.ForeignKey("deployment.id"), primary_key=True),
    db.Column("sensor_id", db.Integer, db.ForeignKey("sensor.id"), primary_key=True)
)


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    altitude = db.Column(db.Float, nullable=True)
    description=db.Column(db.String(256), nullable=True)

    sensor = db.relationship("Sensor", back_populates="location", uselist=False)


class Deployment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(128), nullable=False)

    sensors = db.relationship("Sensor", secondary=deployments, back_populates="deployments")


class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    model = db.Column(db.String(128), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"), unique=True)

    location = db.relationship("Location", back_populates="sensor")
    measurements = db.relationship("Measurement", back_populates="sensor")
    deployments = db.relationship("Deployment", secondary=deployments, back_populates="sensors")

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name", "model"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Sensor's unique name",
            "type": "string"
        }
        props["model"] = {
            "description": "Name of the sensor's model",
            "type": "string"
        }
        return schema


class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensor.id", ondelete="SET NULL"))
    value = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    sensor = db.relationship("Sensor", back_populates="measurements")

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["value"]
        }
        props = schema["properties"] = {}
        props["value"] = {
            "description": "Measured value.",
            "type": "number"
        }
        props["time"] = {
            "description": "Measurement timestamp",
            "type": "string",
            "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]T[0-9]{2}:[0-5][0-9]:[0-5][0-9]Z$"
        }
        return schema


@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()

@click.command("testgen")
@with_appcontext
def generate_test_data():
    import datetime
    import random
    s = Sensor(
        name="test-sensor-1",
        model="testsensor"
    )
    now = datetime.datetime.now()
    interval = datetime.timedelta(seconds=10)
    for i in range(1000):
        m = Measurement(
            value=round(random.random() * 100, 2),
            time=now
        )
        now += interval
        s.measurements.append(m)
    
    db.session.add(s)
    db.session.commit()
