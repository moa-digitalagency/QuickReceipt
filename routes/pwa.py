from flask import Blueprint, jsonify, session, send_from_directory
from models import Settings

pwa_bp = Blueprint('pwa', __name__)

@pwa_bp.route('/manifest.json')
def manifest():
    user_id = session.get('user_id')
    settings = Settings.get(user_id=user_id)

    icon_url = settings.get('pwa_icon_url', '/static/favicon.svg')
    icon_type = 'image/svg+xml'
    if icon_url.lower().endswith('.png'):
        icon_type = 'image/png'
    elif icon_url.lower().endswith('.jpg') or icon_url.lower().endswith('.jpeg'):
        icon_type = 'image/jpeg'

    manifest_data = {
        "name": settings.get('pwa_app_name', 'Receipt App'),
        "short_name": settings.get('pwa_short_name', 'Receipts'),
        "start_url": "/",
        "display": "standalone",
        "background_color": settings.get('pwa_background_color', '#ffffff'),
        "theme_color": settings.get('pwa_theme_color', '#3B82F6'),
        "description": settings.get('pwa_description', 'Receipt Management Application'),
        "icons": [
            {
                "src": icon_url,
                "sizes": "any",
                "type": icon_type
            }
        ]
    }

    return jsonify(manifest_data)

@pwa_bp.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')
