from flask import Blueprint, render_template, request, redirect, url_for, send_file, jsonify, session

from models import Client, Receipt, Settings
from services.pdf import generate_receipt_pdf
from services.thermal import generate_thermal_receipt

receipts_bp = Blueprint('receipts', __name__, url_prefix='/receipts')

@receipts_bp.route('/')
def list_receipts():
    receipts = Receipt.get_sorted()
    client_map = Client.get_map()
    
    for receipt in receipts:
        client = client_map.get(receipt.get('client_id'))
        receipt['client'] = client
    
    return render_template('receipts.html', receipts=receipts)

@receipts_bp.route('/add', methods=['GET', 'POST'])
def add_receipt():
    clients = Client.get_all()
    
    if request.method == 'POST':
        client_id = request.form.get('client_id', '')
        new_client_name = request.form.get('new_client_name', '').strip()
        
        if client_id == 'new' and new_client_name:
            new_client = Client.create(
                name=new_client_name,
                whatsapp=request.form.get('new_client_whatsapp', ''),
                email=request.form.get('new_client_email', '')
            )
            client_id = new_client['id']
        elif client_id == 'new' and not new_client_name:
            return render_template('receipt_form.html', receipt=None, clients=clients, 
                                 error="Veuillez entrer le nom du client")
        elif not client_id:
            return render_template('receipt_form.html', receipt=None, clients=clients,
                                 error="Veuillez sélectionner ou ajouter un client")
        
        new_receipt = Receipt.create(
            client_id=client_id,
            description=request.form.get('description', ''),
            amount=request.form.get('amount', '0'),
            payment_method=request.form.get('payment_method', '')
        )
        
        session['last_receipt_id'] = new_receipt['id']
        return redirect(url_for('receipts.receipt_saved', receipt_id=new_receipt['id']))
    
    return render_template('receipt_form.html', receipt=None, clients=clients)

@receipts_bp.route('/saved/<receipt_id>')
def receipt_saved(receipt_id):
    receipt = Receipt.get_by_id(receipt_id)
    if not receipt:
        return redirect(url_for('receipts.list_receipts'))
    
    client = Client.get_by_id(receipt.get('client_id'))
    receipt['client'] = client
    settings = Settings.get()
    
    return render_template('receipt_saved.html', receipt=receipt, settings=settings)

@receipts_bp.route('/view/<receipt_id>')
def view_receipt(receipt_id):
    receipt = Receipt.get_by_id(receipt_id)
    if not receipt:
        return redirect(url_for('receipts.list_receipts'))
    
    client = Client.get_by_id(receipt.get('client_id'))
    receipt['client'] = client
    settings = Settings.get()
    
    return render_template('receipt_view.html', receipt=receipt, settings=settings)

@receipts_bp.route('/delete/<receipt_id>', methods=['POST'])
def delete_receipt(receipt_id):
    Receipt.delete(receipt_id)
    return redirect(url_for('receipts.list_receipts'))

@receipts_bp.route('/pdf/<receipt_id>')
def download_pdf(receipt_id):
    receipt = Receipt.get_by_id(receipt_id)
    if not receipt:
        return redirect(url_for('receipts.list_receipts'))
    
    client = Client.get_by_id(receipt.get('client_id'))
    settings = Settings.get()
    
    buffer = generate_receipt_pdf(receipt, client, settings)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{receipt.get('receipt_number', 'receipt')}.pdf",
        mimetype='application/pdf'
    )

@receipts_bp.route('/thermal/<receipt_id>')
def download_thermal(receipt_id):
    receipt = Receipt.get_by_id(receipt_id)
    if not receipt:
        return redirect(url_for('receipts.list_receipts'))
    
    client = Client.get_by_id(receipt.get('client_id'))
    settings = Settings.get()
    
    buffer = generate_thermal_receipt(receipt, client, settings)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{receipt.get('receipt_number', 'receipt')}_thermal.png",
        mimetype='image/png'
    )
