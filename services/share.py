import os
from flask import request
from utils.i18n import t

def get_site_url():
    # 1. Vérifier la variable d'environnement standard (Pour le VPS/Prod)
    if os.environ.get('SITE_URL'):
        return os.environ.get('SITE_URL').rstrip('/')

    # 2. Essayer de récupérer l'URL depuis le contexte de la requête Flask
    try:
        return request.url_root.rstrip('/')
    except Exception:
        pass

    # On retourne une chaine vide si rien n'est configuré.
    return ""

def get_share_message(receipt, client, company, settings=None):
    # On utilise l'URL des settings si fournie, sinon on cherche dans l'environnement
    if settings and settings.get('site_url'):
        site_url = settings.get('site_url').rstrip('/')
    else:
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

    # On n'ajoute la ligne du site que si une URL existe
    if site_url:
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