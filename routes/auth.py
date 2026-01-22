from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from models import User

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('user_role') != 'superadmin':
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if 'user_id' in session:
        return User.get_by_id(session['user_id'])
    return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.authenticate(username, password)
        if user:
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            session['username'] = user['username']
            session['company_id'] = user.get('company_id')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Identifiants incorrects', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    session.pop('username', None)
    session.pop('company_id', None)
    return redirect(url_for('auth.login'))
