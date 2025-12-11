from functools import wraps
from flask import session, jsonify
from base64 import b64decode

def requires_unlocked_vault(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if 'enc_key_b64' not in session:
            return jsonify({'error': 'vault_locked'}), 401
        return fn(*a, **kw)
    return wrapper

def get_enc_key_from_session() -> bytes:
    return b64decode(session['enc_key_b64'])