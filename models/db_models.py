import uuid
from datetime import datetime
from init_db import db, Company as CompanyModel, Client as ClientModel, Receipt as ReceiptModel, Settings as SettingsModel

class Company:
    @staticmethod
    def get_all():
        companies = CompanyModel.query.order_by(CompanyModel.created_at.desc()).all()
        return [Company._to_dict(c) for c in companies]
    
    @staticmethod
    def get_by_id(company_id):
        if not company_id:
            return None
        company = CompanyModel.query.get(company_id)
        return Company._to_dict(company) if company else None
    
    @staticmethod
    def create(name, address='', tax_id='', phone='', logo=''):
        new_company = CompanyModel(
            id=str(uuid.uuid4()),
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
    def update(company_id, **kwargs):
        company = CompanyModel.query.get(company_id)
        if company:
            for key, value in kwargs.items():
                if hasattr(company, key):
                    setattr(company, key, value)
            db.session.commit()
            return Company._to_dict(company)
        return None
    
    @staticmethod
    def delete(company_id):
        company = CompanyModel.query.get(company_id)
        if company:
            db.session.delete(company)
            db.session.commit()
    
    @staticmethod
    def _to_dict(company):
        if not company:
            return None
        return {
            'id': company.id,
            'name': company.name,
            'address': company.address,
            'tax_id': company.tax_id,
            'phone': company.phone,
            'logo': company.logo,
            'created_at': company.created_at.isoformat() if company.created_at else ''
        }

class Client:
    @staticmethod
    def get_all():
        clients = ClientModel.query.order_by(ClientModel.name).all()
        return [Client._to_dict(c) for c in clients]
    
    @staticmethod
    def get_by_id(client_id):
        if not client_id:
            return None
        client = ClientModel.query.get(client_id)
        return Client._to_dict(client) if client else None
    
    @staticmethod
    def get_map():
        clients = ClientModel.query.all()
        return {c.id: Client._to_dict(c) for c in clients}
    
    @staticmethod
    def create(name, whatsapp='', email=''):
        new_client = ClientModel(
            id=str(uuid.uuid4()),
            name=name,
            whatsapp=whatsapp,
            email=email,
            created_at=datetime.utcnow()
        )
        db.session.add(new_client)
        db.session.commit()
        return Client._to_dict(new_client)
    
    @staticmethod
    def update(client_id, **kwargs):
        client = ClientModel.query.get(client_id)
        if client:
            for key, value in kwargs.items():
                if hasattr(client, key):
                    setattr(client, key, value)
            db.session.commit()
            return Client._to_dict(client)
        return None
    
    @staticmethod
    def delete(client_id):
        client = ClientModel.query.get(client_id)
        if client:
            db.session.delete(client)
            db.session.commit()
    
    @staticmethod
    def count():
        return ClientModel.query.count()
    
    @staticmethod
    def _to_dict(client):
        if not client:
            return None
        return {
            'id': client.id,
            'name': client.name,
            'whatsapp': client.whatsapp,
            'email': client.email,
            'created_at': client.created_at.isoformat() if client.created_at else ''
        }

class Receipt:
    @staticmethod
    def get_all():
        receipts = ReceiptModel.query.all()
        return [Receipt._to_dict(r) for r in receipts]
    
    @staticmethod
    def get_by_id(receipt_id):
        if not receipt_id:
            return None
        receipt = ReceiptModel.query.get(receipt_id)
        return Receipt._to_dict(receipt) if receipt else None
    
    @staticmethod
    def get_sorted(limit=None):
        query = ReceiptModel.query.order_by(ReceiptModel.created_at.desc())
        if limit:
            query = query.limit(limit)
        receipts = query.all()
        return [Receipt._to_dict(r) for r in receipts]
    
    @staticmethod
    def create(client_id, description, amount, payment_method, company_id=''):
        count = ReceiptModel.query.count()
        receipt_number = f"REC-{datetime.now().strftime('%Y%m%d')}-{count + 1:04d}"
        
        new_receipt = ReceiptModel(
            id=str(uuid.uuid4()),
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
    def delete(receipt_id):
        receipt = ReceiptModel.query.get(receipt_id)
        if receipt:
            db.session.delete(receipt)
            db.session.commit()
    
    @staticmethod
    def count():
        return ReceiptModel.query.count()
    
    @staticmethod
    def total_amount():
        from sqlalchemy import func
        result = db.session.query(func.sum(ReceiptModel.amount)).scalar()
        return float(result) if result else 0
    
    @staticmethod
    def _to_dict(receipt):
        if not receipt:
            return None
        return {
            'id': receipt.id,
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
    def get():
        settings = SettingsModel.query.first()
        if settings:
            return {'thermal_width': settings.thermal_width}
        return {'thermal_width': 58}
    
    @staticmethod
    def save(settings_dict):
        settings = SettingsModel.query.first()
        if not settings:
            settings = SettingsModel()
            db.session.add(settings)
        settings.thermal_width = settings_dict.get('thermal_width', 58)
        db.session.commit()
