import uuid
from datetime import datetime
from init_db import db, Company as CompanyModel, Client as ClientModel, Receipt as ReceiptModel, Settings as SettingsModel, User as UserModel
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    @staticmethod
    def get_all():
        users = UserModel.query.order_by(UserModel.created_at.desc()).all()
        return [User._to_dict(u) for u in users]
    
    @staticmethod
    def get_by_id(user_id):
        if not user_id:
            return None
        user = UserModel.query.get(user_id)
        return User._to_dict(user) if user else None
    
    @staticmethod
    def get_by_username(username):
        if not username:
            return None
        user = UserModel.query.filter_by(username=username).first()
        return User._to_dict(user) if user else None
    
    @staticmethod
    def authenticate(username, password):
        user = UserModel.query.filter_by(username=username, is_active=True).first()
        if user and check_password_hash(user.password_hash, password):
            return User._to_dict(user)
        return None
    
    @staticmethod
    def create(username, password, role='user'):
        new_user = UserModel(
            id=str(uuid.uuid4()),
            username=username,
            password_hash=generate_password_hash(password),
            role=role,
            created_at=datetime.utcnow(),
            is_active=True
        )
        db.session.add(new_user)
        db.session.commit()
        return User._to_dict(new_user)
    
    @staticmethod
    def update(user_id, **kwargs):
        user = UserModel.query.get(user_id)
        if user:
            if 'password' in kwargs and kwargs['password']:
                user.password_hash = generate_password_hash(kwargs.pop('password'))
            for key, value in kwargs.items():
                if hasattr(user, key) and key != 'password_hash':
                    setattr(user, key, value)
            db.session.commit()
            return User._to_dict(user)
        return None
    
    @staticmethod
    def delete(user_id):
        user = UserModel.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
    
    @staticmethod
    def _to_dict(user):
        if not user:
            return None
        return {
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else ''
        }

class Company:
    @staticmethod
    def get_all(user_id=None):
        query = CompanyModel.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        companies = query.order_by(CompanyModel.created_at.desc()).all()
        return [Company._to_dict(c) for c in companies]
    
    @staticmethod
    def get_by_id(company_id, user_id=None):
        if not company_id:
            return None
        query = CompanyModel.query.filter_by(id=company_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        company = query.first()
        return Company._to_dict(company) if company else None
    
    @staticmethod
    def create(user_id, name, address='', tax_id='', phone='', logo=''):
        new_company = CompanyModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            address=address,
            tax_id=tax_id,
            phone=phone,
            logo=logo,
            created_at=datetime.utcnow()
        )
        db.session.add(new_company)
        db.session.commit()
        return Company._to_dict(new_company)
    
    @staticmethod
    def update(company_id, user_id=None, **kwargs):
        query = CompanyModel.query.filter_by(id=company_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        company = query.first()
        if company:
            for key, value in kwargs.items():
                if hasattr(company, key) and key not in ['id', 'user_id']:
                    setattr(company, key, value)
            db.session.commit()
            return Company._to_dict(company)
        return None
    
    @staticmethod
    def delete(company_id, user_id=None):
        query = CompanyModel.query.filter_by(id=company_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        company = query.first()
        if company:
            db.session.delete(company)
            db.session.commit()
    
    @staticmethod
    def _to_dict(company):
        if not company:
            return None
        return {
            'id': company.id,
            'user_id': company.user_id,
            'name': company.name,
            'address': company.address,
            'tax_id': company.tax_id,
            'phone': company.phone,
            'logo': company.logo,
            'created_at': company.created_at.isoformat() if company.created_at else ''
        }

class Client:
    @staticmethod
    def get_all(user_id=None):
        query = ClientModel.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        clients = query.order_by(ClientModel.name).all()
        return [Client._to_dict(c) for c in clients]
    
    @staticmethod
    def get_by_id(client_id, user_id=None):
        if not client_id:
            return None
        query = ClientModel.query.filter_by(id=client_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        client = query.first()
        return Client._to_dict(client) if client else None
    
    @staticmethod
    def get_map(user_id=None):
        query = ClientModel.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        clients = query.all()
        return {c.id: Client._to_dict(c) for c in clients}
    
    @staticmethod
    def create(user_id, name, whatsapp='', email=''):
        new_client = ClientModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            whatsapp=whatsapp,
            email=email,
            created_at=datetime.utcnow()
        )
        db.session.add(new_client)
        db.session.commit()
        return Client._to_dict(new_client)
    
    @staticmethod
    def update(client_id, user_id=None, **kwargs):
        query = ClientModel.query.filter_by(id=client_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        client = query.first()
        if client:
            for key, value in kwargs.items():
                if hasattr(client, key) and key not in ['id', 'user_id']:
                    setattr(client, key, value)
            db.session.commit()
            return Client._to_dict(client)
        return None
    
    @staticmethod
    def delete(client_id, user_id=None):
        query = ClientModel.query.filter_by(id=client_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        client = query.first()
        if client:
            db.session.delete(client)
            db.session.commit()
    
    @staticmethod
    def count(user_id=None):
        query = ClientModel.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.count()
    
    @staticmethod
    def _to_dict(client):
        if not client:
            return None
        return {
            'id': client.id,
            'user_id': client.user_id,
            'name': client.name,
            'whatsapp': client.whatsapp,
            'email': client.email,
            'created_at': client.created_at.isoformat() if client.created_at else ''
        }

class Receipt:
    @staticmethod
    def get_all(user_id=None):
        query = ReceiptModel.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        receipts = query.all()
        return [Receipt._to_dict(r) for r in receipts]
    
    @staticmethod
    def get_by_id(receipt_id, user_id=None):
        if not receipt_id:
            return None
        query = ReceiptModel.query.filter_by(id=receipt_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        receipt = query.first()
        return Receipt._to_dict(receipt) if receipt else None
    
    @staticmethod
    def get_sorted(user_id=None, limit=None):
        query = ReceiptModel.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        query = query.order_by(ReceiptModel.created_at.desc())
        if limit:
            query = query.limit(limit)
        receipts = query.all()
        return [Receipt._to_dict(r) for r in receipts]
    
    @staticmethod
    def generate_receipt_number(user_id, format_template=None):
        if not format_template:
            format_template = 'REC-{YYYY}{MM}{DD}-{N}'
        
        count = ReceiptModel.query.filter_by(user_id=user_id).count() + 1
        now = datetime.now()
        
        receipt_number = format_template
        receipt_number = receipt_number.replace('{YYYY}', now.strftime('%Y'))
        receipt_number = receipt_number.replace('{MM}', now.strftime('%m'))
        receipt_number = receipt_number.replace('{DD}', now.strftime('%d'))
        receipt_number = receipt_number.replace('{N}', f'{count:04d}')
        
        return receipt_number
    
    @staticmethod
    def create(user_id, client_id, description, amount, payment_method, company_id='', receipt_number_format=None):
        receipt_number = Receipt.generate_receipt_number(user_id, receipt_number_format)
        
        new_receipt = ReceiptModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            receipt_number=receipt_number,
            client_id=client_id if client_id else None,
            company_id=company_id if company_id else None,
            description=description,
            amount=float(amount) if amount else 0,
            payment_method=payment_method,
            created_at=datetime.utcnow()
        )
        db.session.add(new_receipt)
        db.session.commit()
        return Receipt._to_dict(new_receipt)
    
    @staticmethod
    def delete(receipt_id, user_id=None):
        query = ReceiptModel.query.filter_by(id=receipt_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        receipt = query.first()
        if receipt:
            db.session.delete(receipt)
            db.session.commit()
    
    @staticmethod
    def count(user_id=None):
        query = ReceiptModel.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.count()
    
    @staticmethod
    def total_amount(user_id=None):
        from sqlalchemy import func
        query = db.session.query(func.sum(ReceiptModel.amount))
        if user_id:
            query = query.filter(ReceiptModel.user_id == user_id)
        result = query.scalar()
        return float(result) if result else 0
    
    @staticmethod
    def _to_dict(receipt):
        if not receipt:
            return None
        return {
            'id': receipt.id,
            'user_id': receipt.user_id,
            'receipt_number': receipt.receipt_number,
            'client_id': receipt.client_id,
            'company_id': receipt.company_id,
            'description': receipt.description,
            'amount': str(receipt.amount) if receipt.amount else '0',
            'payment_method': receipt.payment_method,
            'created_at': receipt.created_at.isoformat() if receipt.created_at else ''
        }

class Settings:
    @staticmethod
    def get(user_id=None):
        query = SettingsModel.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        settings = query.first()
        if settings:
            return {
                'thermal_width': settings.thermal_width,
                'receipt_number_format': getattr(settings, 'receipt_number_format', 'REC-{YYYY}{MM}{DD}-{N}') or 'REC-{YYYY}{MM}{DD}-{N}',
                'timezone': getattr(settings, 'timezone', 'Africa/Casablanca') or 'Africa/Casablanca'
            }
        return {'thermal_width': 58, 'receipt_number_format': 'REC-{YYYY}{MM}{DD}-{N}', 'timezone': 'Africa/Casablanca'}
    
    @staticmethod
    def save(user_id, settings_dict):
        settings = SettingsModel.query.filter_by(user_id=user_id).first()
        if not settings:
            settings = SettingsModel(user_id=user_id)
            db.session.add(settings)
        settings.thermal_width = settings_dict.get('thermal_width', 58)
        if hasattr(settings, 'receipt_number_format'):
            settings.receipt_number_format = settings_dict.get('receipt_number_format', 'REC-{YYYY}{MM}{DD}-{N}')
        if hasattr(settings, 'timezone'):
            settings.timezone = settings_dict.get('timezone', 'Africa/Casablanca')
        db.session.commit()
