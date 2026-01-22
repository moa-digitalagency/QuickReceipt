from utils.i18n import t

def get_share_message(receipt, client, settings):
    company_name = settings.get('company_name', 'QuickReceipt')
    client_name = client.get('name', '') if client else ''
    amount = receipt.get('amount', '0')
    receipt_number = receipt.get('receipt_number', '')
    
    message = t('receipts.share_message').format(
        client_name=client_name,
        company_name=company_name,
        receipt_number=receipt_number,
        amount=amount
    )
    
    return {
        'message': message,
        'whatsapp_number': client.get('whatsapp', '') if client else '',
        'email': client.get('email', '') if client else '',
        'subject': f"{t('receipts.receipt')} {receipt_number}"
    }
