from flask import Blueprint, render_template, redirect, url_for, session

from models import Client, Receipt, Settings
from utils.i18n import set_locale

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    receipts = Receipt.get_sorted(limit=5)
    clients = Client.get_all()
    settings = Settings.get()
    
    total_amount = Receipt.total_amount()
    total_receipts = Receipt.count()
    total_clients = len(clients)
    
    return render_template('dashboard.html', 
                         receipts=receipts, 
                         clients=clients,
                         settings=settings,
                         total_receipts=total_receipts,
                         total_clients=total_clients,
                         total_amount=total_amount)

@dashboard_bp.route('/set-locale/<locale>')
def change_locale(locale):
    set_locale(locale)
    from flask import request
    return redirect(request.referrer or url_for('dashboard.index'))
