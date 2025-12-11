from flask import Flask, Blueprint, jsonify, request, session
from app.schemas import UserSchema
from app.models import db, User
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token
from app.utils.kdf import derive_enc_key
from base64 import b64encode
from app.logging import errors_log

authb = Blueprint('auth', __name__)

@authb.route('/register', methods=['POST'])
def register():
    user_schema = UserSchema()

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data'}), 400
        
    user_data = user_schema.load(data)
    master_password = user_data.get('master_password')
    email = user_data.get('email')

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'error': 'An account with this email already exists. Please log in or use a different email to sign up.'}), 400

    auth_hash = generate_password_hash(master_password)
    user = User(email=email, auth_hash=auth_hash)

    db.session.add(user)
    db.session.flush()

    db.session.commit()
    
    return jsonify({
        'id': user.id,
        'email': user.email
    }), 200


@authb.route('/login', methods=['POST'])
def login():
    user_schema = UserSchema(partial=True)

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data'}), 400
        
    user_data = user_schema.load(data)
    email = user_data.get('email')
    master_password = user_data.get('master_password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.auth_hash, master_password):
        return jsonify({'error': 'Invalid credentials'}), 401
        
    enc_key = derive_enc_key(master_password.encode(), user.enc_salt)
    session['enc_key_b64'] = b64encode(enc_key).decode()
        
    access_token = create_access_token(identity=user.id)

    return jsonify(access_token=access_token), 200