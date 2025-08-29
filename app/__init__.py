from flask import Flask
from app.extensions import db, api
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

migrate = Migrate()  # create instance

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    api.init_app(app)
    migrate.init_app(app, db)  # 🔑 enable migrations

    # import routes
    from app import routes  

    return app
