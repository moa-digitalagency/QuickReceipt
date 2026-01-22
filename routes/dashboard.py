from flask import Blueprint, render_template, redirect, url_for, session

from models import Client, Receipt, Settings
from utils.i18n import set_locale

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    user_id = session.get('user_id')
    
    receipts = Receipt.get_sorted(user_id=user_id, limit=5)
    clients = Client.get_all(user_id=user_id)
    settings = Settings.get(user_id=user_id)
    
    total_amount = Receipt.total_amount(user_id=user_id)
    total_receipts = Receipt.count(user_id=user_id)
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
