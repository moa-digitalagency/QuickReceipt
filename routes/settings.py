from flask import Blueprint, render_template, request, redirect, url_for, session
import os

from models import Settings, Company
from utils.files import save_logo, save_icon

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET', 'POST'])
def settings_page():
    user_id = session.get('user_id')
    settings = Settings.get(user_id=user_id)
    companies = Company.get_all(user_id=user_id)
    
    if request.method == 'POST':
        thermal_width = int(request.form.get('thermal_width', 58))
        settings['thermal_width'] = thermal_width if thermal_width in [48, 57, 58, 80] else 58
        settings['receipt_number_format'] = request.form.get('receipt_number_format', 'REC-{YYYY}{MM}{DD}-{N}')
        settings['timezone'] = request.form.get('timezone', 'Africa/Casablanca')

        # PWA Settings
        settings['pwa_enabled'] = 'pwa_enabled' in request.form
        settings['pwa_app_name'] = request.form.get('pwa_app_name', 'Receipt App')
        settings['pwa_short_name'] = request.form.get('pwa_short_name', 'Receipts')
        settings['pwa_description'] = request.form.get('pwa_description', 'Receipt Management Application')
        settings['pwa_theme_color'] = request.form.get('pwa_theme_color', '#3B82F6')
        settings['pwa_background_color'] = request.form.get('pwa_background_color', '#ffffff')

        if 'pwa_icon' in request.files:
            file = request.files['pwa_icon']
            if file and file.filename:
                icon_path = save_icon(file)
                if icon_path:
                    settings['pwa_icon_url'] = '/' + icon_path

        Settings.save(user_id, settings)
        return redirect(url_for('settings.settings_page'))
    
    return render_template('settings.html', settings=settings, companies=companies)

@settings_bp.route('/company/add', methods=['GET', 'POST'])
def add_company():
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        logo_path = ''
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename:
                logo_path = save_logo(file)
        
        Company.create(
            user_id=user_id,
            name=request.form.get('name', ''),
            address=request.form.get('address', ''),
            tax_id=request.form.get('tax_id', ''),
            phone=request.form.get('phone', ''),
            logo=logo_path
        )
        return redirect(url_for('settings.settings_page'))
    
    return render_template('company_form.html', company=None)

@settings_bp.route('/company/edit/<company_id>', methods=['GET', 'POST'])
def edit_company(company_id):
    user_id = session.get('user_id')
    company = Company.get_by_id(company_id, user_id=user_id)
    
    if not company:
        return redirect(url_for('settings.settings_page'))
    
    if request.method == 'POST':
        logo_path = company.get('logo', '')
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename:
                logo_path = save_logo(file)
        
        Company.update(
            company_id=company_id,
            user_id=user_id,
            name=request.form.get('name', ''),
            address=request.form.get('address', ''),
            tax_id=request.form.get('tax_id', ''),
            phone=request.form.get('phone', ''),
            logo=logo_path
        )
        return redirect(url_for('settings.settings_page'))
    
    return render_template('company_form.html', company=company)

@settings_bp.route('/company/delete/<company_id>', methods=['POST'])
def delete_company(company_id):
    user_id = session.get('user_id')
    Company.delete(company_id, user_id=user_id)
    return redirect(url_for('settings.settings_page'))
