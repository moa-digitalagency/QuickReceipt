from flask import Blueprint

from routes.dashboard import dashboard_bp
from routes.clients import clients_bp
from routes.receipts import receipts_bp
from routes.settings import settings_bp
from routes.api import api_bp
from routes.auth import auth_bp
from routes.users import users_bp
from routes.pwa import pwa_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(receipts_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(pwa_bp)
