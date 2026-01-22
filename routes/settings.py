from flask import Blueprint, render_template, request, redirect, url_for

from models import Settings, Company
from utils.files import save_logo

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET', 'POST'])
def settings_page():
    settings = Settings.get()
    companies = Company.get_all()
    
    if request.method == 'POST':
        thermal_width = int(request.form.get('thermal_width', 58))
        settings['thermal_width'] = thermal_width if thermal_width in [48, 57, 58, 80] else 58
        Settings.save(settings)
        return redirect(url_for('settings.settings_page'))
    
    return render_template('settings.html', settings=settings, companies=companies)

@settings_bp.route('/company/add', methods=['GET', 'POST'])
def add_company():
    if request.method == 'POST':
        logo_path = ''
        if 'logo' in request.files:
            logo_path = save_logo(request.files['logo'])
        
        Company.create(
            name=request.form.get('name', ''),
            address=request.form.get('address', ''),
            tax_id=request.form.get('tax_id', ''),
            phone=request.form.get('phone', ''),
            logo=logo_path or ''
        )
        return redirect(url_for('settings.settings_page'))
    
    return render_template('company_form.html', company=None)

@settings_bp.route('/company/edit/<company_id>', methods=['GET', 'POST'])
def edit_company(company_id):
    company = Company.get_by_id(company_id)
    if not company:
        return redirect(url_for('settings.settings_page'))
    
    if request.method == 'POST':
        logo_path = company.get('logo', '')
        if 'logo' in request.files and request.files['logo'].filename:
            new_logo = save_logo(request.files['logo'])
            if new_logo:
                logo_path = new_logo
        
        Company.update(
            company_id,
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
    Company.delete(company_id)
    return redirect(url_for('settings.settings_page'))
