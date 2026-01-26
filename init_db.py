import os
import uuid
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    companies = db.relationship('Company', backref='owner', lazy=True)
    clients = db.relationship('Client', backref='owner', lazy=True)
    receipts = db.relationship('Receipt', backref='owner', lazy=True)

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text, default='')
    tax_id = db.Column(db.String(100), default='')
    phone = db.Column(db.String(50), default='')
    logo = db.Column(db.String(255), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    whatsapp = db.Column(db.String(50), default='')
    email = db.Column(db.String(255), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Receipt(db.Model):
    __tablename__ = 'receipts'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    receipt_number = db.Column(db.String(50), unique=True, nullable=False)
    client_id = db.Column(db.String(36), nullable=True)
    company_id = db.Column(db.String(36), nullable=True)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Settings(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    thermal_width = db.Column(db.Integer, default=58)
    receipt_number_format = db.Column(db.String(50), default='REC-{YYYY}{MM}{DD}-{N}')
    timezone = db.Column(db.String(50), default='Africa/Casablanca')

def init_database(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
        existing_admin = User.query.filter_by(username=os.environ.get('ADMIN_USERNAME', 'admin')).first()
        if not existing_admin:
            admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            
            admin_user = User(
                id=str(uuid.uuid4()),
                username=admin_username,
                password_hash=generate_password_hash(admin_password),
                role='superadmin',
                created_at=datetime.utcnow(),
                is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"Super admin created: {admin_username}")
        
        print("Database tables created successfully!")

if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    init_database(app)
