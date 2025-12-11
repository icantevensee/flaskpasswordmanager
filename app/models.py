from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    auth_hash = db.Column(db.String(255), nullable=False)

    enc_salt = db.Column(db.LargeBinary(16), nullable=False, default=lambda: os.urandom(16))

    kdf_version = db.Column(db.Integer, nullable=False, default=1,)
    kdf_params = db.Column(db.String(255), nullable=False, default="scrypt:n=32768,r=8,p=1,len=32", )

class SavedAccount(db.Model):
    __tablename__ = 'saved_accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)

    username = db.Column(db.String(120), nullable=True, default=None)
    email = db.Column(db.String(120), nullable=True, default=None)
    password_ciphertext = db.Column(db.String(), nullable=False)
    