import os
import json
import uuid
from datetime import datetime

DATA_DIR = 'data'
COMPANIES_FILE = os.path.join(DATA_DIR, 'companies.json')

class Company:
    @staticmethod
    def get_all():
        if os.path.exists(COMPANIES_FILE):
            with open(COMPANIES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    @staticmethod
    def get_by_id(company_id):
        companies = Company.get_all()
        for company in companies:
            if company['id'] == company_id:
                return company
        return None
    
    @staticmethod
    def create(name, address='', tax_id='', phone='', logo=''):
        companies = Company.get_all()
        
        new_company = {
            'id': str(uuid.uuid4()),
            'name': name,
            'address': address,
            'tax_id': tax_id,
            'phone': phone,
            'logo': logo,
            'created_at': datetime.now().isoformat()
        }
        
        companies.append(new_company)
        Company._save(companies)
        return new_company
    
    @staticmethod
    def update(company_id, **kwargs):
        companies = Company.get_all()
        for company in companies:
            if company['id'] == company_id:
                for key, value in kwargs.items():
                    if key in ['name', 'address', 'tax_id', 'phone', 'logo']:
                        company[key] = value
                Company._save(companies)
                return company
        return None
    
    @staticmethod
    def delete(company_id):
        companies = Company.get_all()
        companies = [c for c in companies if c['id'] != company_id]
        Company._save(companies)
    
    @staticmethod
    def _save(companies):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(COMPANIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(companies, f, ensure_ascii=False, indent=2)
