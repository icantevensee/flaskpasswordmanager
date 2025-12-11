import logging
from logging.handlers import RotatingFileHandler
from flask import request, jsonify, g
import time
import os
from sqlalchemy.exc import SQLAlchemyError
from app.models import db
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError

os.makedirs('logs', exist_ok=True)

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.disabled = True

def create_logger(name, filename, level=logging.INFO):

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    logs_path = os.path.join('logs', filename)

    handler = RotatingFileHandler(
        logs_path,
        maxBytes=5 * 1024 * 1024,  
        backupCount=5,
        encoding="utf-8",
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    logger.propagate = False
    
    return logger

#access
access_log = create_logger('access', 'access.log', logging.INFO)

def setup_request_logging(app):

    @app.before_request
    def start_timer():
        g.start_time = time.time()

    @app.after_request
    def log_request(response):

        duration = -1
        if hasattr(g, "start_time"):
            duration = (time.time() - g.start_time) * 1000  # ms

        method = request.method
        path = request.path
        status = response.status_code
        ip = request.headers.get("X-Real-IP") or request.remote_addr
        endpoint = request.endpoint

        access_log.info(
            "REQUEST %s %s -> %s (%.2f ms, ip=%s, endpoint=%s)",
            method,
            path,
            status,
            duration,
            ip,
            endpoint
        )

        return response

#errors + 1 warning
errors_log = create_logger('errors', 'errors.log', logging.ERROR)
warnings_log = create_logger('warnings', 'warnings.log', logging.WARNING)

def setup_error_handling(app):

    @app.errorhandler(Exception)
    def global_error_handler(e):

        method = request.method
        path = request.path
        ip = request.headers.get("X-Real-IP") or request.remote_addr
        endpoint = request.endpoint
        user_id = getattr(g, 'user_id', None)

        if isinstance(e, ValidationError):
            return jsonify({
                'error': 'validation_error',
                'messages': e.messages
            }), 400

        if isinstance(e, HTTPException):

            warnings_log.warning(
                "HTTP ERROR %s at %s %s (ip=%s, user_id=%s, endpoint=%s)",
                e.code,
                method,
                path,
                ip,
                user_id,
                endpoint
            )

            return jsonify({
                'error': e.name,
                'message': e.description
            }), e.code

        errors_log.error(
            "UNHANDLED ERROR at %s %s -> [%s: %s] (ip=%s, user_id=%s, endpoint=%s)",
            method,
            path,
            type(e).__name__,
            e,
            ip,
            user_id,
            endpoint
        )
        
        if isinstance(e, SQLAlchemyError):
            db.session.rollback()
            return jsonify({
                'error': 'db_error',
                'message': 'Database error. Please try again later.'
            }), 500
        
        return jsonify({
            'error': 'internal_error',
            'message': 'Something went wrong. Please try again later.'
        }), 500