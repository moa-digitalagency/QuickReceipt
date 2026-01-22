import os
import json

DATA_DIR = 'data'
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')

class Settings:
    @staticmethod
    def get():
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'company_name': '',
            'logo': '',
            'address': '',
            'tax_id': '',
            'phone': ''
        }
    
    @staticmethod
    def save(settings):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
