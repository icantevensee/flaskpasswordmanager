import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def _pack(d):
    return base64.b64encode(json.dumps(d, separators=(',', ':')).encode()).decode()

def _unpack(s):
    return json.loads(base64.b64decode(s.encode()).decode())

def encrypt_data(plaintext: str, enc_key: bytes, *, user_id: int, saved_account_id: int, version: int = 1) -> str:
    aad = f"u:{user_id};r:{saved_account_id};v:{version}".encode()
    nonce = os.urandom(12)
    ct = AESGCM(enc_key).encrypt(nonce, plaintext.encode(), aad)
    return _pack({
        'v': version, 
        'alg': 'aesgcm',          
        'n': base64.b64encode(nonce).decode(), 
        'aad': base64.b64encode(aad).decode(),  
        'ct': base64.b64encode(ct).decode()
    })

def decrypt_data(blob_b64: str, enc_key: bytes, *, user_id: int, saved_account_id: int) -> str:
    blob = _unpack(blob_b64)
    if blob.get('alg') != 'aesgcm':
        raise ValueError('unsupported alg')
    aad = f"u:{user_id};r:{saved_account_id};v:{blob['v']}".encode()
    nonce = base64.b64decode(blob['n'])
    ct = base64.b64decode(blob['ct'])
    return AESGCM(enc_key).decrypt(nonce, ct, aad).decode()