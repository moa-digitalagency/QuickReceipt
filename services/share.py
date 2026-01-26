import os
from utils.i18n import t

def get_site_url():
    domain = os.environ.get('REPLIT_DEV_DOMAIN', '')
    if domain:
        return f"https://{domain}"
    return "https://quickreceipt.app"

def get_share_message(receipt, client, company):
    site_url = get_site_url()
    company_name = company.get('name', 'QuickReceipt') if company else 'QuickReceipt'
    client_name = client.get('name', '') if client else ''
    amount = receipt.get('amount', '0')
    receipt_number = receipt.get('receipt_number', '')
    description = receipt.get('description', '')
    date_str = receipt.get('created_at', '')[:10] if receipt.get('created_at') else ''
    
    payment_methods = {
        'cash': 'Especes',
        'card': 'Carte bancaire',
        'transfer': 'Virement',
        'check': 'Cheque'
    }
    payment_text = payment_methods.get(receipt.get('payment_method', ''), receipt.get('payment_method', ''))
    
    lines = []
    lines.append(f"*{company_name}*")
    
    if company:
        if company.get('address'):
            lines.append(company['address'].replace('\n', ', '))
        if company.get('phone'):
            lines.append(f"Tel: {company['phone']}")
        if company.get('tax_id'):
            lines.append(f"ICE/SIRET: {company['tax_id']}")
    
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"*RECU N° {receipt_number}*")
    lines.append(f"Date: {date_str}")
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(f"Client: *{client_name}*")
    lines.append("")
    lines.append(f"Description:")
    lines.append(description)
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"*TOTAL: {amount} MAD*")
    lines.append(f"Paiement: {payment_text}")
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("_Merci pour votre confiance!_")
    lines.append("")
    lines.append(f"🌐 {site_url}")
    
    message = '\n'.join(lines)
    
    return {
        'message': message,
        'whatsapp_number': client.get('whatsapp', '') if client else '',
        'email': client.get('email', '') if client else '',
        'subject': f"{t('receipts.receipt')} {receipt_number}",
        'receipt_id': receipt.get('id', ''),
        'site_url': site_url
    }
