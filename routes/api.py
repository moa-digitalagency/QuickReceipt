from flask import Blueprint, jsonify, request

from models import Client, Receipt, Settings
from services.share import get_share_message

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/share/<receipt_id>')
def share_data(receipt_id):
    receipt = Receipt.get_by_id(receipt_id)
    if not receipt:
        return jsonify({'error': 'Receipt not found'}), 404
    
    client = Client.get_by_id(receipt.get('client_id'))
    settings = Settings.get()
    
    return jsonify(get_share_message(receipt, client, settings))

@api_bp.route('/clients/quick-add', methods=['POST'])
def quick_add_client():
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    new_client = Client.create(
        name=data.get('name', ''),
        whatsapp=data.get('whatsapp', ''),
        email=data.get('email', '')
    )
    
    return jsonify(new_client)
