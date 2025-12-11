from flask import Flask
from flask_migrate import Migrate
from .config import Config
from .models import db
from .routes import jwt, register_routes
from flask_session import Session
from .logging import setup_request_logging, setup_error_handling
import os

migrate = Migrate()
session_ext = Session()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs('logs', exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    session_ext.init_app(app)
    
    register_routes(app)

    setup_request_logging(app)
    setup_error_handling(app)

    return app