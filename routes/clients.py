from flask import Blueprint, render_template, request, redirect, url_for, session

from models import Client

clients_bp = Blueprint('clients', __name__, url_prefix='/clients')

@clients_bp.route('/')
def list_clients():
    user_id = session.get('user_id')
    clients = Client.get_all(user_id=user_id)
    return render_template('clients.html', clients=clients)

@clients_bp.route('/add', methods=['GET', 'POST'])
def add_client():
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        Client.create(
            user_id=user_id,
            name=request.form.get('name', ''),
            whatsapp=request.form.get('whatsapp', ''),
            email=request.form.get('email', '')
        )
        return redirect(url_for('clients.list_clients'))
    return render_template('client_form.html', client=None)

@clients_bp.route('/edit/<client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    user_id = session.get('user_id')
    client = Client.get_by_id(client_id, user_id=user_id)
    
    if not client:
        return redirect(url_for('clients.list_clients'))
    
    if request.method == 'POST':
        Client.update(
            client_id=client_id,
            user_id=user_id,
            name=request.form.get('name', ''),
            whatsapp=request.form.get('whatsapp', ''),
            email=request.form.get('email', '')
        )
        return redirect(url_for('clients.list_clients'))
    
    return render_template('client_form.html', client=client)

@clients_bp.route('/delete/<client_id>', methods=['POST'])
def delete_client(client_id):
    user_id = session.get('user_id')
    Client.delete(client_id, user_id=user_id)
    return redirect(url_for('clients.list_clients'))
