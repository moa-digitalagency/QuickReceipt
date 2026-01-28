from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Settings
from routes.auth import superadmin_required
from utils.files import save_icon

pwa_configuration_bp = Blueprint('pwa_configuration', __name__, url_prefix='/pwa-configuration')

@pwa_configuration_bp.route('/', methods=['GET', 'POST'])
@superadmin_required
def pwa_configuration_page():
    settings = Settings.get_global()

    if request.method == 'POST':
        form_data = {}

        form_data['pwa_enabled'] = 'pwa_enabled' in request.form
        form_data['pwa_app_name'] = request.form.get('pwa_app_name', 'Receipt App')
        form_data['pwa_short_name'] = request.form.get('pwa_short_name', 'Receipts')
        form_data['pwa_description'] = request.form.get('pwa_description', 'Receipt Management Application')
        form_data['pwa_theme_color'] = request.form.get('pwa_theme_color', '#3B82F6')
        form_data['pwa_background_color'] = request.form.get('pwa_background_color', '#ffffff')

        if 'pwa_icon' in request.files:
            file = request.files['pwa_icon']
            if file and file.filename:
                icon_path = save_icon(file)
                if icon_path:
                    form_data['pwa_icon_url'] = '/' + icon_path
            else:
                 form_data['pwa_icon_url'] = settings.get('pwa_icon_url')
        else:
             form_data['pwa_icon_url'] = settings.get('pwa_icon_url')

        Settings.save(None, form_data)
        flash('Configuration PWA mise à jour avec succès', 'success')
        return redirect(url_for('pwa_configuration.pwa_configuration_page'))

    return render_template('pwa_configuration.html', settings=settings)
