from flask import Blueprint, jsonify, request
from app.models import db, SavedAccount
from app.schemas import SavedAccountSchema
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.utils import encrypt_data, decrypt_data, requires_unlocked_vault, get_enc_key_from_session

accounts = Blueprint('accounts', __name__)

@accounts.route('/accounts/add', methods=['POST'])
@jwt_required()
@requires_unlocked_vault
def add_account():
    user_id = get_jwt_identity()
    account_schema = SavedAccountSchema()

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data.'}), 400
        
    account_data = account_schema.load(data)

    title = account_data.get('title')
    username = account_data.get('username')
    email = account_data.get('email')
    password = account_data.get('password')

    saved_acc = SavedAccount(user_id=user_id, title=title, username=username, email=email, password_ciphertext='tmp')
    db.session.add(saved_acc)
    db.session.flush()

    enc_key = get_enc_key_from_session()
    ciphertext = encrypt_data(password, enc_key, user_id=user_id, saved_account_id=saved_acc.id, version=1)
    saved_acc.password_ciphertext = ciphertext

    db.session.commit()

    return jsonify({
        'id': saved_acc.id,
        'title': saved_acc.title,
        'username': saved_acc.username,
        'email': saved_acc.email,
    }), 201


@accounts.route('/accounts', methods=['GET'])
@jwt_required()
@requires_unlocked_vault
def get_accounts():
    user_id = get_jwt_identity()
    accounts = SavedAccount.query.filter_by(user_id=user_id)

    title = request.args.get('title')

    if title:
        accounts = accounts.filter(SavedAccount.title.ilike(f'%{title}%'))

    accounts = accounts.all()

    return jsonify([{
        'id': acc.id,
        'title': acc.title,
        'username': acc.username,
        'email': acc.email,
    } for acc in accounts]), 200

@accounts.route('/accounts/<int:saved_account_id>/password', methods=['GET'])
@jwt_required()
@requires_unlocked_vault
def get_password(saved_account_id):
    user_id = get_jwt_identity()

    saved_acc = SavedAccount.query.filter_by(id=saved_account_id, user_id=user_id).first()
    if saved_acc is None:
        return jsonify({'error': 'not_found'}), 404

    if saved_acc.user_id != user_id:
        return jsonify({'error': 'forbidden'}), 403

    enc_key = get_enc_key_from_session()

    raw_password = decrypt_data(saved_acc.password_ciphertext, enc_key, user_id=user_id, saved_account_id=saved_acc.id)

    return jsonify({
        'password': raw_password
    }), 200
    
@accounts.route('/accounts/<int:saved_account_id>/update', methods=['PUT'])
@jwt_required()
@requires_unlocked_vault
def update_credentials(saved_account_id):
    user_id = get_jwt_identity()

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data.'}), 400
        
    saved_acc = SavedAccount.query.filter_by(id=saved_account_id).first()
    if saved_acc is None:
        return jsonify({'error': 'not_found'}), 404


    if saved_acc.user_id != user_id:
        return jsonify({'error': 'forbidden'}), 403
        
    if 'title' in data:
        saved_acc.title = data.get('title')
    if 'username' in data:
        saved_acc.username = data.get('username')
    if 'email' in data:
        saved_acc.email = data.get('email')
    if 'password' in data:
        enc_key = get_enc_key_from_session()

        ciphertext = encrypt_data(data.get('password'), enc_key, user_id=user_id, saved_account_id=saved_acc.id, version=1)

        saved_acc.password_ciphertext = ciphertext
    
    db.session.commit()

    return jsonify({
        'id': saved_acc.id,
        'title': saved_acc.title,
        'username': saved_acc.username,
        'email': saved_acc.email,
    }), 200