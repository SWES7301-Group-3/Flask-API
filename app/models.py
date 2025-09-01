from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=True)
    lastname = db.Column(db.String(50), nullable=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

class Telemetry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    timezone = db.Column(db.String(50), nullable=False)
    coordinates = db.Column(db.String(100), nullable=False)
    temperatures = db.Column(db.JSON)
    humidity = db.Column(db.Float)
    wind = db.Column(db.JSON)
    precipitation = db.Column(db.Float)
    haze = db.Column(db.Boolean)
    notes = db.Column(db.Text, nullable=True)
    salinity = db.Column(db.Float)
    ph_level = db.Column(db.Float)
    pollutants = db.Column(db.JSON)

    def __repr__(self):
        return f"<Telemetry {self.date} {self.time}>"

class UserRole:
    ADMIN = 'admin'
    RESEARCHER = 'researcher'
    USER = 'user'