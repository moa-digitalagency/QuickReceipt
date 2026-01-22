from flask import Blueprint, render_template, request, redirect, url_for
from models import User
from routes.auth import superadmin_required

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/')
@superadmin_required
def list_users():
    users = User.get_all()
    return render_template('users.html', users=users)

@users_bp.route('/add', methods=['GET', 'POST'])
@superadmin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'user')
        
        if username and password:
            existing = User.get_by_username(username)
            if not existing:
                User.create(
                    username=username,
                    password=password,
                    role=role
                )
        return redirect(url_for('users.list_users'))
    
    return render_template('user_form.html', user=None)

@users_bp.route('/edit/<user_id>', methods=['GET', 'POST'])
@superadmin_required
def edit_user(user_id):
    user = User.get_by_id(user_id)
    
    if not user:
        return redirect(url_for('users.list_users'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'user')
        is_active = request.form.get('is_active') == 'on'
        
        update_data = {
            'username': username,
            'role': role,
            'is_active': is_active
        }
        
        if password:
            update_data['password'] = password
        
        User.update(user_id, **update_data)
        return redirect(url_for('users.list_users'))
    
    return render_template('user_form.html', user=user)

@users_bp.route('/delete/<user_id>', methods=['POST'])
@superadmin_required
def delete_user(user_id):
    User.delete(user_id)
    return redirect(url_for('users.list_users'))
