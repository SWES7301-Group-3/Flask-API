from flask import Flask
from flask_restx import Api

# Create the Flask application instance
app = Flask(__name__)

# Configure the API
api = Api(
    app,
    version='1.0',
    title='Flask API for SWES7301-Group-3',
    description='A simple API with Swagger documentation by Group 3',
    doc='/swagger/',  # This enables Swagger UI at /swagger/
    default='Users',
    default_label='User operations'
)

# Import routes after creating app and api to avoid circular imports
from app import routes