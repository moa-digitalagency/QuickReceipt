import os
from flask import Flask, session, redirect, url_for, request

from security import get_secret_key
from routes import register_routes
from utils.i18n import t, get_locale
from init_db import db, init_database

app = Flask(__name__)
app.secret_key = get_secret_key()
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,
    'pool_pre_ping': True,
}

os.makedirs('static/uploads', exist_ok=True)

init_database(app)
register_routes(app)

PUBLIC_ROUTES = ['auth.login', 'auth.logout', 'static']

@app.before_request
def check_login():
    if request.endpoint in PUBLIC_ROUTES or (request.endpoint and request.endpoint.startswith('static')):
        return
    if 'user_id' not in session and request.endpoint != 'auth.login':
        return redirect(url_for('auth.login'))

@app.context_processor
def inject_globals():
    locale = get_locale()
    return {
        't': t,
        'locale': locale,
        'is_rtl': locale == 'ar',
        'current_user': {
            'id': session.get('user_id'),
            'username': session.get('username'),
            'role': session.get('user_role'),
            'company_id': session.get('company_id')
        } if 'user_id' in session else None,
        'is_superadmin': session.get('user_role') == 'superadmin'
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
