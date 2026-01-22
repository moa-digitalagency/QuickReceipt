import uuid
from datetime import datetime
from models.base import load_data, save_data

CLIENTS_FILE = 'clients.json'

class Client:
    @staticmethod
    def get_all():
        return load_data(CLIENTS_FILE)
    
    @staticmethod
    def get_by_id(client_id):
        clients = load_data(CLIENTS_FILE)
        return next((c for c in clients if c['id'] == client_id), None)
    
    @staticmethod
    def create(name, whatsapp='', email=''):
        clients = load_data(CLIENTS_FILE)
        new_client = {
            'id': str(uuid.uuid4()),
            'name': name,
            'whatsapp': whatsapp,
            'email': email,
            'created_at': datetime.now().isoformat()
        }
        clients.append(new_client)
        save_data(CLIENTS_FILE, clients)
        return new_client
    
    @staticmethod
    def update(client_id, name, whatsapp='', email=''):
        clients = load_data(CLIENTS_FILE)
        for client in clients:
            if client['id'] == client_id:
                client['name'] = name
                client['whatsapp'] = whatsapp
                client['email'] = email
                break
        save_data(CLIENTS_FILE, clients)
    
    @staticmethod
    def delete(client_id):
        clients = load_data(CLIENTS_FILE)
        clients = [c for c in clients if c['id'] != client_id]
        save_data(CLIENTS_FILE, clients)
    
    @staticmethod
    def get_map():
        clients = load_data(CLIENTS_FILE)
        return {c['id']: c for c in clients}
