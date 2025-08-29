import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class Telemetry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    timezone = db.Column(db.String(50), nullable=False)
    coordinates = db.Column(db.String(100), nullable=False)
    temperatures = db.Column(db.JSON)  # e.g., {"C": 22, "F": 72}
    humidity = db.Column(db.Float)  # percentage
    wind = db.Column(db.JSON)  # e.g., {"speed": 10, "direction": "N"}
    precipitation = db.Column(db.Float)  # mm
    haze = db.Column(db.Boolean)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Telemetry {self.date} {self.time}>"
    def __str__(self):
        return f"WeatherRecord on {self.date} at {self.time}"
 