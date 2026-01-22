import uuid
from datetime import datetime
from models.base import load_data, save_data

RECEIPTS_FILE = 'receipts.json'

class Receipt:
    @staticmethod
    def get_all():
        return load_data(RECEIPTS_FILE)
    
    @staticmethod
    def get_by_id(receipt_id):
        receipts = load_data(RECEIPTS_FILE)
        return next((r for r in receipts if r['id'] == receipt_id), None)
    
    @staticmethod
    def get_sorted(limit=None):
        receipts = load_data(RECEIPTS_FILE)
        sorted_receipts = sorted(receipts, key=lambda x: x.get('created_at', ''), reverse=True)
        if limit:
            return sorted_receipts[:limit]
        return sorted_receipts
    
    @staticmethod
    def create(client_id, description, amount, payment_method, company_id=''):
        receipts = load_data(RECEIPTS_FILE)
        receipt_number = f"REC-{datetime.now().strftime('%Y%m%d')}-{len(receipts) + 1:04d}"
        
        new_receipt = {
            'id': str(uuid.uuid4()),
            'receipt_number': receipt_number,
            'client_id': client_id,
            'company_id': company_id,
            'description': description,
            'amount': amount,
            'payment_method': payment_method,
            'created_at': datetime.now().isoformat()
        }
        receipts.append(new_receipt)
        save_data(RECEIPTS_FILE, receipts)
        return new_receipt
    
    @staticmethod
    def delete(receipt_id):
        receipts = load_data(RECEIPTS_FILE)
        receipts = [r for r in receipts if r['id'] != receipt_id]
        save_data(RECEIPTS_FILE, receipts)
    
    @staticmethod
    def count():
        return len(load_data(RECEIPTS_FILE))
    
    @staticmethod
    def total_amount():
        receipts = load_data(RECEIPTS_FILE)
        return sum(float(r.get('amount', 0)) for r in receipts)
