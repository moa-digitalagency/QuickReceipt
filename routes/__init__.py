from flask import Blueprint

from routes.dashboard import dashboard_bp
from routes.clients import clients_bp
from routes.receipts import receipts_bp
from routes.settings import settings_bp
from routes.api import api_bp

def register_routes(app):
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(receipts_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(api_bp)
