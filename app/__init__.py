from flask import Flask
from app.extensions import db, api, jwt
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app.models import User, Telemetry
import logging

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=['http://localhost:8000'])  # Allow Django frontend
    api.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Setup Flask-Admin (optional for internal management)
    admin = Admin(app, name='Environmental Data Admin', template_mode='bootstrap4')
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Telemetry, db.session))

    # Import and register namespaces
    from app.routes import public_ns, basic_ns, research_ns, premium_ns, subscription_ns
    api.add_namespace(public_ns)
    api.add_namespace(basic_ns)
    api.add_namespace(research_ns)
    api.add_namespace(premium_ns)
    api.add_namespace(subscription_ns)

    return app