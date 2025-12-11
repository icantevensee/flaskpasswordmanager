# 🔐 Flask Password Manager

This is a backend-only password manager API built with **Flask**, focused on authentication, encryption, and clean architecture.  
It includes **authentication**, **encryption**, **validation**, **logging**, and **tests**.


## 🛡️ Security Overview

- Passwords are authenticated **via hashing** (no plaintext stored).
- Each user has a **unique** `enc_salt`, so the encryption key is **derived per user**.
- All vault items are encrypted with **AES-GCM** and protected with **AAD**.
- Decryption works only when the **derived key** is present in the **session** (vault unlocked).


## 🔗 API Routes

### 🔐 Auth

---

1. #### **POST** `/register`
- Creates a new user.  
- Validates input -> checks email uniqueness -> stores the master password **as a hash** (no plaintext).

**JSON BODY:**

```json
{
  "email": "user@example.com",
  "master_password": "MyStrongPassword123"
}
```
---

2. #### **POST** `/login`
- Validates credentials -> verifies password -> **derives encryption key** using the user's `enc_salt` -> stores key in session -> returns a JWT.

**JSON BODY:**

```json
{
  "email": "user@example.com",
  "master_password": "MyStrongPassword123"
}
```
**RESPONSE EXAMPLE:**

```json
{
  "access_token": "<jwt token>"
}
```

---

### 🗄️ Vault / Accounts

1. #### **POST** `/accounts/add`
- (JWT + unlocked vault) -> validate data -> **encrypt password with AES-GCM** -> store ciphertext.

**JSON BODY:**

```json
{
  "title": "GitHub",
  "username": "myuser",
  "email": "myuser@example.com",
  "password": "supersecret123"
}
```

---

2. #### **GET** `/accounts`
- (JWT + unlocked vault) -> return list of accounts (metadata only, **no passwords**).

**RESPONSE EXAMPLE:**

```json
[
  {
    "id": 1,
    "title": "GitHub",
    "username": "myuser",
    "email": "myuser@example.com"
  }
]
```

---

3. #### **GET** `/accounts/<id>/password`
- (JWT + unlocked vault) -> check ownership -> decrypt stored password -> return plaintext.

**RESPONSE EXAMPLE:**

```json
{
  "password": "supersecret123"
}
```

---

4. #### **PUT** `/accounts/<id>/update`
- (JWT + unlocked vault) -> update metadata -> if password changed -> **re-encrypt new password**.

**JSON BODY (any field optional):**

```json
{
  "title": "GitHub Work",
  "username": "workuser",
  "email": "work@example.com",
  "password": "newpassword456"
}
```

---

## 📁 Project Structure
```
flaskpasswordmanager/
├── app/
│   ├── routes/  
│   │   ├── __init__.py         		
│   │   ├── auth.py       		
│   │   └── passwords.py  		
│   ├── utils/
│   │   ├── __init__.py            		
│   │   ├── encryption.py 
│   │   ├── kdf.py
│   │   └── vault.py
│   ├── __init__.py       		
│   ├── config.py
│   ├── logging.py    		
│   ├── models.py         		
│   └── schemas.py        		
├── tests/                		
│   ├── conftest.py       		
│   ├── t/
│   │   ├── test_auth.py  		
│   │   └── test_passwords.py           
├── pytest.ini            		
├── run.py                		
└──  .env                  		
```
---

## 🧰 Technologies

- **Backend:** Flask, Flask-JWT-Extended, Flask-Migrate, SQLAlchemy
- **Database:** PostgreSQL, SQLite
- **Validation:** Marshmallow
- **Encryption:** Cryptography (AES-GCM), Scrypt + HKDF key derivation
- **Logging:** Python logging (structured request/error logging)
- **Testing:** Pytest

---

## ⚙️ Environment Variables (.env)

Your `.env` file should contain:

```py
    SECRET_KEY=
    DATABASE_URL=              # PostgreSQL or SQLite connection string
    JWT_SECRET_KEY=

    TEST_DATABASE_URL=         # Database URL used for tests
    TEST_JWT_SECRET_KEY=       # JWT secret used for tests

    SESSION_TYPE=              # "filesystem" or "redis"
    REDIS_URL=                 # required only if SESSION_TYPE=redis
```

Example for local development (SQLite + filesystem sessions):

```py
    SECRET_KEY=dev_secret
    JWT_SECRET_KEY=jwt_secret
    DATABASE_URL=sqlite:///app.db

    TEST_DATABASE_URL=sqlite:///test.db
    TEST_JWT_SECRET_KEY=test_jwt

    SESSION_TYPE=filesystem
```

Example for PostgreSQL + Redis sessions:

```py
    SECRET_KEY=prod_secret
    JWT_SECRET_KEY=prod_jwt
    DATABASE_URL=postgresql://user:pass@localhost:5432/password_manager

    TEST_DATABASE_URL=postgresql://user:pass@localhost:5432/password_manager_test
    TEST_JWT_SECRET_KEY=test_jwt

    SESSION_TYPE=redis
    REDIS_URL=redis://localhost:6379/0
```

## 🚀 Running the Project

1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Create `.env` (see **Environment Variables** section).
3. Apply migrations:
```bash
flask db upgrade
```
4. (Optional) If using Redis sessions:
```bash
docker run -p 6379:6379 redis
```
5. Start the app:
```bash
python run.py
```