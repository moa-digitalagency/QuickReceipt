from flask import Blueprint, render_template, request, redirect, url_for
from models import User, Company
from routes.auth import superadmin_required

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/')
@superadmin_required
def list_users():
    users = User.get_all()
    companies = Company.get_all()
    company_map = {c['id']: c for c in companies}
    return render_template('users.html', users=users, company_map=company_map)

@users_bp.route('/add', methods=['GET', 'POST'])
@superadmin_required
def add_user():
    companies = Company.get_all()
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'company')
        company_id = request.form.get('company_id', '')
        
        if username and password:
            existing = User.get_by_username(username)
            if not existing:
                User.create(
                    username=username,
                    password=password,
                    role=role,
                    company_id=company_id if company_id else None
                )
        return redirect(url_for('users.list_users'))
    
    return render_template('user_form.html', user=None, companies=companies)

@users_bp.route('/edit/<user_id>', methods=['GET', 'POST'])
@superadmin_required
def edit_user(user_id):
    user = User.get_by_id(user_id)
    companies = Company.get_all()
    
    if not user:
        return redirect(url_for('users.list_users'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'company')
        company_id = request.form.get('company_id', '')
        is_active = request.form.get('is_active') == 'on'
        
        update_data = {
            'username': username,
            'role': role,
            'company_id': company_id if company_id else None,
            'is_active': is_active
        }
        
        if password:
            update_data['password'] = password
        
        User.update(user_id, **update_data)
        return redirect(url_for('users.list_users'))
    
    return render_template('user_form.html', user=user, companies=companies)

@users_bp.route('/delete/<user_id>', methods=['POST'])
@superadmin_required
def delete_user(user_id):
    User.delete(user_id)
    return redirect(url_for('users.list_users'))
