from flask import Blueprint, render_template, request, redirect, url_for

from models import Settings
from utils.files import save_logo

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET', 'POST'])
def settings_page():
    settings = Settings.get()
    
    if request.method == 'POST':
        settings['company_name'] = request.form.get('company_name', '')
        settings['address'] = request.form.get('address', '')
        settings['tax_id'] = request.form.get('tax_id', '')
        settings['phone'] = request.form.get('phone', '')
        
        if 'logo' in request.files:
            logo_path = save_logo(request.files['logo'])
            if logo_path:
                settings['logo'] = logo_path
        
        Settings.save(settings)
        return redirect(url_for('settings.settings_page'))
    
    return render_template('settings.html', settings=settings)
