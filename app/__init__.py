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

def create_app(test_config: dict | None = None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    # ✅ Accept both with/without trailing slash
    app.url_map.strict_slashes = False

    # ✅ Make JWT header-only & test-friendly
    app.config.setdefault("JWT_TOKEN_LOCATION", ["headers"])
    app.config.setdefault("JWT_HEADER_NAME", "Authorization")
    app.config.setdefault("JWT_HEADER_TYPE", "Bearer")
    app.config.setdefault("JWT_COOKIE_CSRF_PROTECT", False)
    app.config.setdefault("PROPAGATE_EXCEPTIONS", True)

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=['http://localhost:8000'])  # Allow Django frontend
    api.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Optional but VERY helpful: show why 422/401 happens
    @jwt.invalid_token_loader
    def _invalid_token(msg): return ({"msg": msg}, 401)
    @jwt.unauthorized_loader
    def _missing_token(msg): return ({"msg": msg}, 401)
    @jwt.expired_token_loader
    def _expired(h, p): return ({"msg": "token expired"}, 401)
    @jwt.needs_fresh_token_loader
    def _fresh(h, p): return ({"msg": "fresh token required"}, 401)
    @jwt.revoked_token_loader
    def _revoked(h, p): return ({"msg": "token revoked"}, 401)

    # Setup Flask-Admin (admin dashboard at /admin)
    admin = Admin(app, name='MyApp Admin', template_mode='bootstrap4')

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