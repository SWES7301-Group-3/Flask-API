from flask import Flask
from app.extensions import db, api, jwt
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app.models import User, Telemetry

migrate = Migrate()  # create instance

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    CORS(app)
    api.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Setup Flask-Admin (admin dashboard at /admin)
    admin = Admin(app, name='MyApp Admin', template_mode='bootstrap4')
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Telemetry, db.session))

    # Import namespaces from routes and register them
    from app.routes import user_ns, telemetry_ns, admin_ns, auth_ns
    api.add_namespace(user_ns)
    api.add_namespace(telemetry_ns)
    api.add_namespace(admin_ns)
    api.add_namespace(auth_ns)

    return app