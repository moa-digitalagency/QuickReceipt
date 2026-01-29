from flask import Blueprint, jsonify, request, session

from models import Client, Receipt, Company, Settings
from services.share import get_share_message

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/share/<receipt_id>')
def share_data(receipt_id):
    user_id = session.get('user_id')
    receipt = Receipt.get_by_id(receipt_id, user_id=user_id)
    if not receipt:
        return jsonify({'error': 'Receipt not found'}), 404
    
    client = Client.get_by_id(receipt.get('client_id'), user_id=user_id)
    company = Company.get_by_id(receipt.get('company_id'), user_id=user_id)
    
    settings = Settings.get(user_id=user_id)

    return jsonify(get_share_message(receipt, client, company, settings))

@api_bp.route('/clients/quick-add', methods=['POST'])
def quick_add_client():
    user_id = session.get('user_id')
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    new_client = Client.create(
        user_id=user_id,
        name=data.get('name', ''),
        whatsapp=data.get('whatsapp', ''),
        email=data.get('email', '')
    )
    
    return jsonify(new_client)
