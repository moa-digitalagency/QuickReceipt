import os
import secrets

def get_secret_key():
    key = os.environ.get('SESSION_SECRET')
    if not key:
        key = secrets.token_hex(32)
    return key
