from flask import Flask
from app.extensions import db, api, jwt
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from app import routes 

migrate = Migrate()  # create instance

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    api.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Import namespaces from routes and register them
    from app.routes import user_ns, telemetry_ns, admin_ns, auth_ns
    api.add_namespace(user_ns)
    api.add_namespace(telemetry_ns)
    api.add_namespace(admin_ns)
    api.add_namespace(auth_ns)

    return app