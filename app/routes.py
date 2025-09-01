from flask import request
from flask_restx import Resource, fields, Namespace
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from app.extensions import db, api
from app.models import User, Telemetry, UserRole
from datetime import datetime
from functools import wraps

user_ns = api.namespace('users', description='User operations')
telemetry_ns = api.namespace('telemetry', description='Telemetry operations')
admin_ns = api.namespace('admin', description='Admin operations')
auth_ns = api.namespace('auth', description='Authentication')

# --- Role-based decorators ---
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            user = User.query.filter_by(id=identity).first()
            if not user or user.role not in roles:
                return {'message': 'Access forbidden: insufficient role'}, 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

admin_required = role_required(UserRole.ADMIN)
researcher_required = role_required(UserRole.ADMIN, UserRole.RESEARCHER)
authenticated_required = jwt_required

# --- Swagger models ---
user_model = api.model('User', {
    'id': fields.Integer(readOnly=True, description='User ID'),
    'firstname': fields.String(required=True, description="User's first name"),
    'lastname': fields.String(required=True, description="User's last name"),
    'username': fields.String(required=True, description="User's username"),
    'email': fields.String(required=True, description="User's email"),
    'role': fields.String(description="User's role (admin/researcher/user)")
})

register_model = api.model('Register', {
    'firstname': fields.String(required=True),
    'lastname': fields.String(required=True),
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True),
})

login_model = api.model('Login', {
    'username': fields.String(required=True),
    'password': fields.String(required=True),
})

refresh_model = api.model('Refresh', {
    'refresh_token': fields.String(required=True),
})

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
    'notes': fields.String(description='Optional notes'),
    'salinity': fields.Float(description='Salinity level'),
    'ph_level': fields.Float(description='pH level'),
    'pollutants': fields.Raw(description='Pollutant levels JSON object')
})

telemetry_patch_model = api.model('TelemetryPatch', {
    'date': fields.String(description='Date in YYYY-MM-DD'),
    'time': fields.String(description='Time in HH:MM:SS'),
    'timezone': fields.String(description='Timezone'),
    'coordinates': fields.String(description='Lat, Long'),
    'temperatures': fields.Raw(description='Temperature JSON object'),
    'humidity': fields.Float(description='Humidity %'),
    'wind': fields.Raw(description='Wind JSON object'),
    'precipitation': fields.Float(description='Precipitation mm'),
    'haze': fields.Boolean(description='Haze condition'),
    'notes': fields.String(description='Optional notes'),
    'salinity': fields.Float(description='Salinity level'),
    'ph_level': fields.Float(description='pH level'),
    'pollutants': fields.Raw(description='Pollutant levels JSON object')
})

# ================= AUTH ROUTES =================
@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        if not user or not user.check_password(data['password']):
            return {'message': 'Invalid username or password'}, 401
        access_token = create_access_token(identity=user.id, additional_claims={'role': user.role})
        refresh_token = create_refresh_token(identity=user.id)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'role': user.role
        }

@auth_ns.route('/refresh')
class Refresh(Resource):
    @auth_ns.expect(refresh_model)
    def post(self):
        from flask_jwt_extended import decode_token
        data = request.json
        try:
            decoded = decode_token(data['refresh_token'])
            user_id = decoded['sub']
            user = User.query.get(user_id)
            if not user:
                return {'message': 'User not found'}, 404
            access_token = create_access_token(identity=user.id, additional_claims={'role': user.role})
            return {'access_token': access_token}
        except Exception:
            return {'message': 'Invalid refresh token'}, 401

# ================= USER ROUTES =================
@user_ns.route('/')
class UserList(Resource):
    @admin_required
    @user_ns.marshal_list_with(user_model)
    def get(self):
        """Get all users (Admin only)"""
        return User.query.all()

    @user_ns.expect(register_model)
    @user_ns.marshal_with(user_model, code=201)
    def post(self):
        """Register a new user (Public)"""
        data = request.json
        if User.query.filter_by(username=data['username']).first():
            return {'message': 'Username already exists'}, 400
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already exists'}, 400
        new_user = User(
            firstname=data.get('firstname'),
            lastname=data.get('lastname'),
            username=data['username'],
            email=data['email'],
            role=UserRole.USER
        )
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return new_user, 201

@user_ns.route('/<int:id>')
@user_ns.response(404, 'User not found')
class UserResource(Resource):
    @authenticated_required()
    @user_ns.marshal_with(user_model)
    def get(self, id):
        user = User.query.get_or_404(id)
        current_user_id = get_jwt_identity()
        user_role = get_jwt()['role']
        if user_role != UserRole.ADMIN and user.id != current_user_id:
            return {'message': 'Access denied'}, 403
        return user

    @admin_required
    def delete(self, id):
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return '', 204

# ================= ADMIN ROUTES =================
@admin_ns.route('/users/<int:user_id>/role')
@admin_ns.param('user_id', 'The user identifier')
class AdminUserRole(Resource):
    @admin_required
    @admin_ns.expect(api.model('RoleUpdate', {
        'role': fields.String(required=True, description='New role (admin/researcher/user)')
    }))
    def put(self, user_id):
        user = User.query.get_or_404(user_id)
        data = request.json
        new_role = data.get('role')
        if new_role not in [UserRole.ADMIN, UserRole.RESEARCHER, UserRole.USER]:
            return {'message': 'Invalid role'}, 400
        user.role = new_role
        db.session.commit()
        return {'message': f'User role updated to {new_role}'}

@admin_ns.route('/telemetry/stats/advanced')
class AdminAdvancedStats(Resource):
    @admin_required
    def get(self):
        from sqlalchemy import func
        stats = db.session.query(
            func.count(Telemetry.id).label('total_records'),
            func.avg(Telemetry.salinity).label('avg_salinity'),
            func.avg(Telemetry.ph_level).label('avg_ph'),
            func.max(Telemetry.salinity).label('max_salinity'),
            func.min(Telemetry.ph_level).label('min_ph')
        ).first()
        return {
            'total_records': stats.total_records,
            'average_salinity': float(stats.avg_salinity) if stats.avg_salinity is not None else 0,
            'average_ph': float(stats.avg_ph) if stats.avg_ph is not None else 0,
            'max_salinity': float(stats.max_salinity) if stats.max_salinity is not None else 0,
            'min_ph': float(stats.min_ph) if stats.min_ph is not None else 0
        }

# ================= TELEMETRY ROUTES =================
@telemetry_ns.route('/')
class TelemetryList(Resource):
    @authenticated_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        user_role = user.role if user else UserRole.USER
        query = Telemetry.query
        if user_role == UserRole.USER:
            records = query.with_entities(
                Telemetry.id, Telemetry.date, Telemetry.time,
                Telemetry.coordinates, Telemetry.temperatures, Telemetry.humidity
            ).all()
            return [{ 'id': r.id, 'date': r.date.isoformat(), 'time': r.time.isoformat(),
                'coordinates': r.coordinates, 'temperatures': r.temperatures, 'humidity': r.humidity } for r in records]
        elif user_role == UserRole.RESEARCHER:
            records = query.all()
            return [{ 'id': r.id, 'date': r.date.isoformat(), 'time': r.time.isoformat(),
                'timezone': r.timezone, 'coordinates': r.coordinates, 'temperatures': r.temperatures,
                'humidity': r.humidity, 'wind': r.wind, 'precipitation': r.precipitation,
                'haze': r.haze, 'salinity': r.salinity, 'ph_level': r.ph_level, 'pollutants': r.pollutants } for r in records]
        else:  # Admin
            return [{ 'id': r.id, 'date': r.date.isoformat(), 'time': r.time.isoformat(),
                'timezone': r.timezone, 'coordinates': r.coordinates, 'temperatures': r.temperatures,
                'humidity': r.humidity, 'wind': r.wind, 'precipitation': r.precipitation,
                'haze': r.haze, 'notes': r.notes, 'salinity': r.salinity,
                'ph_level': r.ph_level, 'pollutants': r.pollutants } for r in query.all()]

    @researcher_required
    @telemetry_ns.expect(telemetry_model)
    @telemetry_ns.marshal_with(telemetry_model, code=201)
    def post(self):
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
            notes=data.get('notes'),
            salinity=data.get('salinity'),
            ph_level=data.get('ph_level'),
            pollutants=data.get('pollutants')
        )
        db.session.add(new_record)
        db.session.commit()
        return new_record, 201

@telemetry_ns.route('/<int:id>')
@telemetry_ns.response(404, 'Telemetry record not found')
@telemetry_ns.param('id', 'The telemetry record identifier')
class TelemetryResource(Resource):
    @authenticated_required()
    def get(self, id):
        record = Telemetry.query.get_or_404(id)
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        user_role = user.role if user else UserRole.USER
        if user_role == UserRole.USER:
            return {
                'id': record.id,
                'date': record.date.isoformat(),
                'time': record.time.isoformat(),
                'coordinates': record.coordinates,
                'temperatures': record.temperatures,
                'humidity': record.humidity
            }
        elif user_role == UserRole.RESEARCHER:
            return {
                'id': record.id,
                'date': record.date.isoformat(),
                'time': record.time.isoformat(),
                'timezone': record.timezone,
                'coordinates': record.coordinates,
                'temperatures': record.temperatures,
                'humidity': record.humidity,
                'wind': record.wind,
                'precipitation': record.precipitation,
                'haze': record.haze,
                'salinity': record.salinity,
                'ph_level': record.ph_level,
                'pollutants': record.pollutants
            }
        else:  # Admin
            return {
                'id': record.id,
                'date': record.date.isoformat(),
                'time': record.time.isoformat(),
                'timezone': record.timezone,
                'coordinates': record.coordinates,
                'temperatures': record.temperatures,
                'humidity': record.humidity,
                'wind': record.wind,
                'precipitation': record.precipitation,
                'haze': record.haze,
                'notes': record.notes,
                'salinity': record.salinity,
                'ph_level': record.ph_level,
                'pollutants': record.pollutants
            }

    @researcher_required
    @telemetry_ns.expect(telemetry_model)
    def put(self, id):
        record = Telemetry.query.get_or_404(id)
        data = request.json
        record.date = datetime.strptime(data['date'], "%Y-%m-%d").date()
        record.time = datetime.strptime(data['time'], "%H:%M:%S").time()
        record.timezone = data['timezone']
        record.coordinates = data['coordinates']
        record.temperatures = data.get('temperatures')
        record.humidity = data.get('humidity')
        record.wind = data.get('wind')
        record.precipitation = data.get('precipitation')
        record.haze = data.get('haze')
        record.notes = data.get('notes')
        record.salinity = data.get('salinity')
        record.ph_level = data.get('ph_level')
        record.pollutants = data.get('pollutants')
        db.session.commit()
        return {'message': 'Record updated successfully'}

    @researcher_required
    @telemetry_ns.expect(telemetry_patch_model)
    def patch(self, id):
        record = Telemetry.query.get_or_404(id)
        data = request.json
        if 'date' in data:
            record.date = datetime.strptime(data['date'], "%Y-%m-%d").date()
        if 'time' in data:
            record.time = datetime.strptime(data['time'], "%H:%M:%S").time()
        if 'timezone' in data:
            record.timezone = data['timezone']
        if 'coordinates' in data:
            record.coordinates = data['coordinates']
        if 'temperatures' in data:
            record.temperatures = data['temperatures']
        if 'humidity' in data:
            record.humidity = data['humidity']
        if 'wind' in data:
            record.wind = data['wind']
        if 'precipitation' in data:
            record.precipitation = data['precipitation']
        if 'haze' in data:
            record.haze = data['haze']
        if 'notes' in data:
            record.notes = data['notes']
        if 'salinity' in data:
            record.salinity = data['salinity']
        if 'ph_level' in data:
            record.ph_level = data['ph_level']
        if 'pollutants' in data:
            record.pollutants = data['pollutants']
        db.session.commit()
        return {'message': 'Record updated successfully'}

    @admin_required
    def delete(self, id):
        record = Telemetry.query.get_or_404(id)
        db.session.delete(record)
        db.session.commit()
        return '', 204

# ================= RESEARCHER-SPECIFIC ROUTES =================
@telemetry_ns.route('/research/salinity')
class SalinityResearch(Resource):
    @researcher_required
    def get(self):
        records = Telemetry.query.with_entities(
            Telemetry.date,
            Telemetry.time,
            Telemetry.coordinates,
            Telemetry.salinity
        ).all()
        return [{
            'date': r.date.isoformat(),
            'time': r.time.isoformat(),
            'coordinates': r.coordinates,
            'salinity': r.salinity
        } for r in records]

@telemetry_ns.route('/research/pollutants')
class PollutantsResearch(Resource):
    @researcher_required
    def get(self):
        records = Telemetry.query.with_entities(
            Telemetry.date,
            Telemetry.time,
            Telemetry.coordinates,
            Telemetry.pollutants
        ).all()
        return [{
            'date': r.date.isoformat(),
            'time': r.time.isoformat(),
            'coordinates': r.coordinates,
            'pollutants': r.pollutants
        } for r in records]

# ================= PUBLIC ROUTES =================
@telemetry_ns.route('/public/summary')
class PublicTelemetrySummary(Resource):
    def get(self):
        from sqlalchemy import func
        stats = db.session.query(
            func.count(Telemetry.id).label('total_records'),
            func.avg(Telemetry.temperatures['avg'].astext.cast(db.Float)).label('avg_temperature'),
            func.avg(Telemetry.humidity).label('avg_humidity')
        ).first()
        return {
            'total_records': stats.total_records,
            'average_temperature': float(stats.avg_temperature) if stats.avg_temperature is not None else 0,
            'average_humidity': float(stats.avg_humidity) if stats.avg_humidity is not None else 0
        }