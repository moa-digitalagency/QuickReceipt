import os
import uuid
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text, inspect
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
    __table_args__ = (
        db.Index('idx_receipts_user_created', 'user_id', 'created_at'),
    )
    
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

    # PWA Settings
    pwa_enabled = db.Column(db.Boolean, default=True)
    pwa_app_name = db.Column(db.String(100), default='Receipt App')
    pwa_short_name = db.Column(db.String(50), default='Receipts')
    pwa_icon_url = db.Column(db.String(255), default='/static/favicon.svg')
    pwa_theme_color = db.Column(db.String(20), default='#3B82F6')
    pwa_background_color = db.Column(db.String(20), default='#ffffff')
    pwa_description = db.Column(db.String(255), default='Receipt Management Application')

    # Global App Settings
    site_url = db.Column(db.String(255), default='')

def migrate_database(app):
    """Run migrations to add missing columns to existing tables"""
    with app.app_context():
        inspector = inspect(db.engine)
        
        handled_columns = set()

        # 1. Manual/Historical Migrations
        migrations = [
            {
                'table': 'settings',
                'column': 'user_id',
                'sql': "ALTER TABLE settings ADD COLUMN IF NOT EXISTS user_id VARCHAR(36) REFERENCES users(id)"
            },
            {
                'table': 'settings',
                'column': 'thermal_width',
                'sql': "ALTER TABLE settings ADD COLUMN IF NOT EXISTS thermal_width INTEGER DEFAULT 58"
            },
            {
                'table': 'settings',
                'column': 'receipt_number_format',
                'sql': "ALTER TABLE settings ADD COLUMN IF NOT EXISTS receipt_number_format VARCHAR(50) DEFAULT 'REC-{YYYY}{MM}{DD}-{N}'"
            },
            {
                'table': 'settings',
                'column': 'timezone',
                'sql': "ALTER TABLE settings ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'Africa/Casablanca'"
            },
            {
                'table': 'companies',
                'column': 'user_id',
                'sql': "ALTER TABLE companies ADD COLUMN IF NOT EXISTS user_id VARCHAR(36) REFERENCES users(id)"
            },
            {
                'table': 'companies',
                'column': 'logo',
                'sql': "ALTER TABLE companies ADD COLUMN IF NOT EXISTS logo VARCHAR(255) DEFAULT ''"
            },
            {
                'table': 'clients',
                'column': 'user_id',
                'sql': "ALTER TABLE clients ADD COLUMN IF NOT EXISTS user_id VARCHAR(36) REFERENCES users(id)"
            },
            {
                'table': 'receipts',
                'column': 'user_id',
                'sql': "ALTER TABLE receipts ADD COLUMN IF NOT EXISTS user_id VARCHAR(36) REFERENCES users(id)"
            },
            {
                'table': 'receipts',
                'column': 'company_id',
                'sql': "ALTER TABLE receipts ADD COLUMN IF NOT EXISTS company_id VARCHAR(36)"
            },
            {
                'table': 'users',
                'column': 'is_active',
                'sql': "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE"
            },
            # PWA Migrations
            {
                'table': 'settings',
                'column': 'pwa_enabled',
                'sql': "ALTER TABLE settings ADD COLUMN IF NOT EXISTS pwa_enabled BOOLEAN DEFAULT TRUE"
            },
            {
                'table': 'settings',
                'column': 'pwa_app_name',
                'sql': "ALTER TABLE settings ADD COLUMN IF NOT EXISTS pwa_app_name VARCHAR(100) DEFAULT 'Receipt App'"
            },
            {
                'table': 'settings',
                'column': 'pwa_short_name',
                'sql': "ALTER TABLE settings ADD COLUMN IF NOT EXISTS pwa_short_name VARCHAR(50) DEFAULT 'Receipts'"
            },
            {
                'table': 'settings',
                'column': 'pwa_icon_url',
                'sql': "ALTER TABLE settings ADD COLUMN IF NOT EXISTS pwa_icon_url VARCHAR(255) DEFAULT '/static/favicon.svg'"
            },
            {
                'table': 'settings',
                'column': 'pwa_theme_color',
                'sql': "ALTER TABLE settings ADD COLUMN IF NOT EXISTS pwa_theme_color VARCHAR(20) DEFAULT '#3B82F6'"
            },
            {
                'table': 'settings',
                'column': 'pwa_background_color',
                'sql': "ALTER TABLE settings ADD COLUMN IF NOT EXISTS pwa_background_color VARCHAR(20) DEFAULT '#ffffff'"
            },
            {
                'table': 'settings',
                'column': 'pwa_description',
                'sql': "ALTER TABLE settings ADD COLUMN IF NOT EXISTS pwa_description VARCHAR(255) DEFAULT 'Receipt Management Application'"
            },
            {
                'table': 'settings',
                'column': 'site_url',
                'sql': "ALTER TABLE settings ADD COLUMN IF NOT EXISTS site_url VARCHAR(255) DEFAULT ''"
            },
        ]
        
        for migration in migrations:
            table_name = migration['table']
            column_name = migration['column']
            
            # Track as handled regardless of whether it exists (to avoid duplicate checks)
            handled_columns.add((table_name, column_name))

            if table_name in inspector.get_table_names():
                existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
                
                if column_name not in existing_columns:
                    try:
                        db.session.execute(text(migration['sql']))
                        db.session.commit()
                        print(f"Migration: Added column '{column_name}' to table '{table_name}'")
                    except Exception as e:
                        db.session.rollback()
                        print(f"Migration warning for {table_name}.{column_name}: {e}")

        # 2. Dynamic/Auto Migrations
        # Iterates through all defined models and checks if columns exist in the database
        print("Running dynamic migration check...")
        for table_name, table in db.metadata.tables.items():
            if table_name in inspector.get_table_names():
                existing_columns = [col['name'] for col in inspector.get_columns(table_name)]

                for column in table.columns:
                    if (table_name, column.name) in handled_columns:
                        continue

                    if column.name not in existing_columns:
                        # Determine column type
                        col_type = str(column.type)

                        # Normalize type for SQL
                        if 'String' in str(type(column.type)):
                            length = column.type.length
                            col_type = f"VARCHAR({length})" if length else "TEXT"
                        elif 'Integer' in str(type(column.type)):
                            col_type = "INTEGER"
                        elif 'Boolean' in str(type(column.type)):
                            col_type = "BOOLEAN"
                        elif 'DateTime' in str(type(column.type)):
                            col_type = "TIMESTAMP"
                        elif 'Numeric' in str(type(column.type)):
                             col_type = f"NUMERIC({column.type.precision}, {column.type.scale})"
                        elif 'Text' in str(type(column.type)):
                            col_type = "TEXT"

                        # Handle Default Values
                        default_clause = ""
                        if column.default is not None:
                            if hasattr(column.default, 'arg'):
                                if isinstance(column.default.arg, str):
                                    # Escape single quotes for SQL safety
                                    escaped_arg = column.default.arg.replace("'", "''")
                                    default_clause = f" DEFAULT '{escaped_arg}'"
                                elif isinstance(column.default.arg, (int, float)):
                                     default_clause = f" DEFAULT {column.default.arg}"
                                elif isinstance(column.default.arg, bool):
                                     default_clause = f" DEFAULT {'TRUE' if column.default.arg else 'FALSE'}"

                        # Handle Foreign Keys
                        fk_clause = ""
                        if column.foreign_keys:
                            fk = list(column.foreign_keys)[0]
                            # fk.target_fullname is usually 'tablename.columnname'
                            try:
                                target_table, target_col = fk.target_fullname.split('.')
                                fk_clause = f" REFERENCES {target_table}({target_col})"
                            except ValueError:
                                # Fallback if split fails
                                pass

                        # Construct SQL
                        # IF NOT EXISTS is redundant since we check in Python, and removing it improves compatibility (e.g. SQLite)
                        sql = f"ALTER TABLE {table_name} ADD COLUMN {column.name} {col_type}{fk_clause}{default_clause}"

                        try:
                            db.session.execute(text(sql))
                            db.session.commit()
                            print(f"Dynamic Migration: Added column '{column.name}' to table '{table_name}'")
                        except Exception as e:
                            db.session.rollback()
                            print(f"Dynamic Migration warning for {table_name}.{column.name}: {e}")

        # Check for missing indexes
        index_migrations = [
            {
                'table': 'receipts',
                'index': 'idx_receipts_user_created',
                'sql': "CREATE INDEX IF NOT EXISTS idx_receipts_user_created ON receipts (user_id, created_at)"
            }
        ]

        for migration in index_migrations:
            table_name = migration['table']
            index_name = migration['index']

            if table_name in inspector.get_table_names():
                indexes = inspector.get_indexes(table_name)
                existing_indexes = [idx['name'] for idx in indexes]

                if index_name not in existing_indexes:
                    try:
                        db.session.execute(text(migration['sql']))
                        db.session.commit()
                        print(f"Migration: Added index '{index_name}' to table '{table_name}'")
                    except Exception as e:
                        db.session.rollback()
                        print(f"Migration warning for {table_name}.{index_name}: {e}")

def init_database(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
        migrate_database(app)
        
        # Force SITE_URL from environment if present (as requested for deployment)
        site_url_env = os.environ.get('SITE_URL')
        if site_url_env:
            global_settings = Settings.query.filter(Settings.user_id.is_(None)).first()
            if not global_settings:
                global_settings = Settings(user_id=None)
                db.session.add(global_settings)

            # Update site_url
            global_settings.site_url = site_url_env.rstrip('/')
            db.session.commit()
            print(f"Deployment: Forced site_url to '{global_settings.site_url}'")

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
        
        print("Database initialization completed!")

if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    init_database(app)
