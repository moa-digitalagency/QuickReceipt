import os
from flask import Blueprint, render_template, request, redirect, url_for, send_file, session

from models import Client, Receipt, Settings, Company
from services.pdf import generate_receipt_pdf
from services.thermal import generate_thermal_receipt

receipts_bp = Blueprint('receipts', __name__, url_prefix='/receipts')

@receipts_bp.route('/')
def list_receipts():
    user_id = session.get('user_id')
    receipts = Receipt.get_sorted(user_id=user_id)
    client_map = Client.get_map(user_id=user_id)
    
    for receipt in receipts:
        client = client_map.get(receipt.get('client_id'))
        receipt['client'] = client
    
    return render_template('receipts.html', receipts=receipts)

@receipts_bp.route('/add', methods=['GET', 'POST'])
def add_receipt():
    user_id = session.get('user_id')
    clients = Client.get_all(user_id=user_id)
    companies = Company.get_all(user_id=user_id)
    
    if request.method == 'POST':
        client_id = request.form.get('client_id', '')
        new_client_name = request.form.get('new_client_name', '').strip()
        company_id = request.form.get('company_id', '')
        new_company_name = request.form.get('new_company_name', '').strip()
        
        if client_id == 'new' and new_client_name:
            new_client = Client.create(
                user_id=user_id,
                name=new_client_name,
                whatsapp=request.form.get('new_client_whatsapp', ''),
                email=request.form.get('new_client_email', '')
            )
            client_id = new_client['id']
        elif client_id == 'new' and not new_client_name:
            return render_template('receipt_form.html', receipt=None, clients=clients, companies=companies,
                                 error="Veuillez entrer le nom du client")
        elif not client_id:
            return render_template('receipt_form.html', receipt=None, clients=clients, companies=companies,
                                 error="Veuillez selectionner ou ajouter un client")
        
        if company_id == 'new' and new_company_name:
            new_company = Company.create(
                user_id=user_id,
                name=new_company_name,
                address=request.form.get('new_company_address', ''),
                tax_id=request.form.get('new_company_tax_id', ''),
                phone=request.form.get('new_company_phone', '')
            )
            company_id = new_company['id']
        elif company_id == 'new' and not new_company_name:
            return render_template('receipt_form.html', receipt=None, clients=clients, companies=companies,
                                 error="Veuillez entrer le nom de l'entreprise")
        elif not company_id:
            return render_template('receipt_form.html', receipt=None, clients=clients, companies=companies,
                                 error="Veuillez selectionner ou ajouter une entreprise")
        
        settings = Settings.get(user_id=user_id)
        receipt_number_format = settings.get('receipt_number_format', 'REC-{YYYY}{MM}{DD}-{N}')
        
        new_receipt = Receipt.create(
            user_id=user_id,
            client_id=client_id,
            company_id=company_id,
            description=request.form.get('description', ''),
            amount=request.form.get('amount', '0'),
            payment_method=request.form.get('payment_method', ''),
            receipt_number_format=receipt_number_format
        )
        
        session['last_receipt_id'] = new_receipt['id']
        return redirect(url_for('receipts.receipt_saved', receipt_id=new_receipt['id']))
    
    return render_template('receipt_form.html', receipt=None, clients=clients, companies=companies)

@receipts_bp.route('/saved/<receipt_id>')
def receipt_saved(receipt_id):
    user_id = session.get('user_id')
    receipt = Receipt.get_by_id(receipt_id, user_id=user_id)
    if not receipt:
        return redirect(url_for('receipts.list_receipts'))
    
    client = Client.get_by_id(receipt.get('client_id'), user_id=user_id)
    receipt['client'] = client
    company = Company.get_by_id(receipt.get('company_id'), user_id=user_id)
    receipt['company'] = company
    settings = Settings.get(user_id=user_id)
    
    return render_template('receipt_saved.html', receipt=receipt, settings=settings)

@receipts_bp.route('/view/<receipt_id>')
def view_receipt(receipt_id):
    user_id = session.get('user_id')
    receipt = Receipt.get_by_id(receipt_id, user_id=user_id)
    if not receipt:
        return redirect(url_for('receipts.list_receipts'))
    
    # Use receipt owner's ID for fetching related data to ensure consistency for public views
    owner_id = receipt.get('user_id')

    client = Client.get_by_id(receipt.get('client_id'), user_id=owner_id)
    receipt['client'] = client
    company = Company.get_by_id(receipt.get('company_id'), user_id=owner_id)
    receipt['company'] = company
    settings = Settings.get(user_id=owner_id)
    
    return render_template('receipt_view.html', receipt=receipt, settings=settings)

@receipts_bp.route('/delete/<receipt_id>', methods=['POST'])
def delete_receipt(receipt_id):
    user_id = session.get('user_id')
    Receipt.delete(receipt_id, user_id=user_id)
    return redirect(url_for('receipts.list_receipts'))

@receipts_bp.route('/pdf/<receipt_id>')
def download_pdf(receipt_id):
    user_id = session.get('user_id')
    receipt = Receipt.get_by_id(receipt_id, user_id=user_id)
    if not receipt:
        return redirect(url_for('receipts.list_receipts'))
    
    owner_id = receipt.get('user_id')

    client = Client.get_by_id(receipt.get('client_id'), user_id=owner_id)
    company = Company.get_by_id(receipt.get('company_id'), user_id=owner_id)
    settings = Settings.get(user_id=owner_id)
    
    buffer = generate_receipt_pdf(receipt, client, company, settings)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{receipt.get('receipt_number', 'receipt')}.pdf",
        mimetype='application/pdf'
    )

@receipts_bp.route('/thermal/<receipt_id>')
def download_thermal(receipt_id):
    user_id = session.get('user_id')
    receipt = Receipt.get_by_id(receipt_id, user_id=user_id)
    if not receipt:
        return redirect(url_for('receipts.list_receipts'))
    
    owner_id = receipt.get('user_id')

    client = Client.get_by_id(receipt.get('client_id'), user_id=owner_id)
    company = Company.get_by_id(receipt.get('company_id'), user_id=owner_id)
    settings = Settings.get(user_id=owner_id)
    
    buffer = generate_thermal_receipt(receipt, client, company, settings)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{receipt.get('receipt_number', 'receipt')}_thermal.png",
        mimetype='image/png'
    )
