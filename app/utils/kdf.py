from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

def derive_enc_key(master_password: bytes, enc_salt: bytes) -> bytes:
    kdf = Scrypt(salt=enc_salt, length=32, n=2**15, r=8, p=1)     
    material = kdf.derive(master_password)
    enc_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"enc-key-v1").derive(material)
    return enc_key