from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Settings
from routes.auth import superadmin_required
from utils.files import save_logo, save_icon

branding_seo_bp = Blueprint('branding_seo', __name__, url_prefix='/branding-seo')

@branding_seo_bp.route('/', methods=['GET', 'POST'])
@superadmin_required
def branding_seo_page():
    settings = Settings.get_global()

    if request.method == 'POST':
        form_data = settings.copy()

        # Branding
        form_data['branding_app_name'] = request.form.get('branding_app_name', '')

        if 'branding_logo' in request.files:
            file = request.files['branding_logo']
            if file and file.filename:
                logo_path = save_logo(file)
                if logo_path:
                    form_data['branding_logo_url'] = '/' + logo_path

        if 'branding_favicon' in request.files:
            file = request.files['branding_favicon']
            if file and file.filename:
                favicon_path = save_icon(file)
                if favicon_path:
                    form_data['branding_favicon_url'] = '/' + favicon_path

        # SEO
        form_data['seo_title_suffix'] = request.form.get('seo_title_suffix', '')
        form_data['seo_meta_description'] = request.form.get('seo_meta_description', '')
        form_data['seo_keywords'] = request.form.get('seo_keywords', '')
        form_data['seo_og_title'] = request.form.get('seo_og_title', '')
        form_data['seo_og_description'] = request.form.get('seo_og_description', '')
        form_data['seo_twitter_card'] = request.form.get('seo_twitter_card', 'summary_large_image')
        form_data['site_url'] = request.form.get('site_url', '').rstrip('/')

        if 'seo_og_image' in request.files:
            file = request.files['seo_og_image']
            if file and file.filename:
                og_image_path = save_logo(file) # save_logo is fine for OG image too
                if og_image_path:
                    form_data['seo_og_image_url'] = '/' + og_image_path

        Settings.save(None, form_data)
        flash('Branding and SEO configuration updated successfully', 'success')
        return redirect(url_for('branding_seo.branding_seo_page'))

    return render_template('branding_seo.html', settings=settings)
