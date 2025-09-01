from app.extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=True)
    lastname = db.Column(db.String(50), nullable=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # Added role field

    def __repr__(self):
        return f"<User {self.username}>"

class Telemetry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    timezone = db.Column(db.String(50), nullable=False)
    coordinates = db.Column(db.String(100), nullable=False)
    temperatures = db.Column(db.JSON)  # {"C": 22, "F": 72, "avg": 23.5} (avg is used in stats)
    humidity = db.Column(db.Float)
    wind = db.Column(db.JSON)  # {"speed": 10, "direction": "N"}
    precipitation = db.Column(db.Float)
    haze = db.Column(db.Boolean)
    notes = db.Column(db.Text, nullable=True)
    salinity = db.Column(db.Float)  # Added for research/statistics
    ph_level = db.Column(db.Float)  # Added for research/statistics
    pollutants = db.Column(db.JSON)  # {"NO2": 0.1, "SO2": 0.05, ...}

    def __repr__(self):
        return f"<Telemetry {self.date} {self.time}>"

    def __str__(self):
        return f"WeatherRecord on {self.date} at {self.time}"

# Optional: Add a UserRole enumeration helper if you want to use it in routes for validation, though it's not strictly required in SQLAlchemy.
class UserRole:
    ADMIN = 'admin'
    RESEARCHER = 'researcher'
    USER = 'user'