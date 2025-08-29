from flask import request
from flask_restx import Resource, fields, Namespace
from app.extensions import db, api
from app.models import User, Telemetry
from datetime import datetime

# Namespaces
user_ns = api.namespace('users', description='User operations')
telemetry_ns = api.namespace('telemetry', description='Telemetry operations')

# User model schema for Swagger
user_model = api.model('User', {
    'id': fields.Integer(readOnly=True, description='User ID'),
    'firstname': fields.String(required=True, description="User's first name"),
    'lastname': fields.String(required=True, description="User's last name"),
    'username': fields.String(required=True, description="User's username"),
    'email': fields.String(required=True, description="User's email")
})

# Telemetry model schema for Swagger
telemetry_model = api.model('Telemetry', {
    'id': fields.Integer(readOnly=True, description='Telemetry ID'),
    'date': fields.String(required=True, description='Date in YYYY-MM-DD'),
    'time': fields.String(required=True, description='Time in HH:MM:SS'),
    'timezone': fields.String(required=True, description='Timezone'),
    'coordinates': fields.String(required=True, description='Lat, Long'),
    'temperatures': fields.Raw(description='Temperature JSON object'),
    'humidity': fields.Float(description='Humidity %'),
    'wind': fields.Raw(description='Wind JSON object'),
    'precipitation': fields.Float(description='Precipitation mm'),
    'haze': fields.Boolean(description='Haze condition'),
    'notes': fields.String(description='Optional notes')
})

# ================= USER ROUTES =================
@user_ns.route('/')
class UserList(Resource):
    @user_ns.marshal_list_with(user_model)
    def get(self):
        """Get all users"""
        return User.query.all()

    @user_ns.expect(user_model)
    @user_ns.marshal_with(user_model, code=201)
    def post(self):
        """Register a new user"""
        data = request.json
        new_user = User(
            firstname=data.get('firstname'),
            lastname=data.get('lastname'),
            username=data['username'],
        email=data['email']
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user, 201


@user_ns.route('/<int:id>')
@user_ns.response(404, 'User not found')
class UserResource(Resource):
    @user_ns.marshal_with(user_model)
    def get(self, id):
        """Get a user by ID"""
        user = User.query.get_or_404(id)
        return user

    def delete(self, id):
        """Delete a user"""
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return '', 204


# ================= TELEMETRY ROUTES =================
@telemetry_ns.route('/')
class TelemetryList(Resource):
    @telemetry_ns.marshal_list_with(telemetry_model)
    def get(self):
        """Get all telemetry records"""
        return Telemetry.query.all()

    @telemetry_ns.expect(telemetry_model)
    @telemetry_ns.marshal_with(telemetry_model, code=201)
    def post(self):
        """Add a new telemetry record"""
        data = request.json
        new_record = Telemetry(
            date=datetime.strptime(data['date'], "%Y-%m-%d").date(),
            time=datetime.strptime(data['time'], "%H:%M:%S").time(),
            timezone=data['timezone'],
            coordinates=data['coordinates'],
            temperatures=data.get('temperatures'),
            humidity=data.get('humidity'),
            wind=data.get('wind'),
            precipitation=data.get('precipitation'),
            haze=data.get('haze'),
            notes=data.get('notes')
        )
        db.session.add(new_record)
        db.session.commit()
        return new_record, 201
