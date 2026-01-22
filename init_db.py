import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text, default='')
    tax_id = db.Column(db.String(100), default='')
    phone = db.Column(db.String(50), default='')
    logo = db.Column(db.String(255), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    receipts = db.relationship('Receipt', backref='company', lazy=True)

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    whatsapp = db.Column(db.String(50), default='')
    email = db.Column(db.String(255), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    receipts = db.relationship('Receipt', backref='client', lazy=True)

class Receipt(db.Model):
    __tablename__ = 'receipts'
    
    id = db.Column(db.String(36), primary_key=True)
    receipt_number = db.Column(db.String(50), unique=True, nullable=False)
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=True)
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id'), nullable=True)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Settings(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    thermal_width = db.Column(db.Integer, default=58)

def init_database(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
        existing_settings = Settings.query.first()
        if not existing_settings:
            default_settings = Settings(thermal_width=58)
            db.session.add(default_settings)
            db.session.commit()
        
        print("Database tables created successfully!")

if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    init_database(app)
