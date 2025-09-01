from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_jwt_extended import JWTManager


db = SQLAlchemy()
api = Api(
    version='1.0',
    title='Flask API for SWES7301-Group-3',
    description='A simple API with Swagger documentation by Group 3',
    doc='/swagger/',  # Swagger UI at /swagger/
    default='Users',
    default_label='User operations'
)

jwt = JWTManager()