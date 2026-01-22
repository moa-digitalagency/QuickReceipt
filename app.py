import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, session
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key')

DATA_DIR = 'data'
UPLOAD_DIR = 'static/uploads'

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

def load_data(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(filename, data):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_settings():
    filepath = os.path.join(DATA_DIR, 'settings.json')
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'company_name': '',
        'logo': '',
        'address': '',
        'tax_id': '',
        'phone': ''
    }

def save_settings(settings):
    filepath = os.path.join(DATA_DIR, 'settings.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def get_translations():
    with open('translations.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_locale():
    return session.get('locale', 'fr')

def t(key):
    translations = get_translations()
    locale = get_locale()
    keys = key.split('.')
    value = translations.get(locale, translations['fr'])
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k, key)
        else:
            return key
    return value if isinstance(value, str) else key

@app.context_processor
def inject_globals():
    locale = get_locale()
    return {
        't': t,
        'locale': locale,
        'is_rtl': locale == 'ar'
    }

@app.route('/set-locale/<locale>')
def set_locale(locale):
    if locale in ['fr', 'en', 'ar']:
        session['locale'] = locale
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/')
def dashboard():
    receipts = load_data('receipts.json')
    recent_receipts = sorted(receipts, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
    clients = load_data('clients.json')
    settings = load_settings()
    
    total_amount = sum(float(r.get('amount', 0)) for r in receipts)
    
    return render_template('dashboard.html', 
                         receipts=recent_receipts, 
                         clients=clients,
                         settings=settings,
                         total_receipts=len(receipts),
                         total_clients=len(clients),
                         total_amount=total_amount)

@app.route('/clients')
def clients_list():
    clients = load_data('clients.json')
    return render_template('clients.html', clients=clients)

@app.route('/clients/add', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        clients = load_data('clients.json')
        new_client = {
            'id': str(uuid.uuid4()),
            'name': request.form.get('name', ''),
            'whatsapp': request.form.get('whatsapp', ''),
            'email': request.form.get('email', ''),
            'created_at': datetime.now().isoformat()
        }
        clients.append(new_client)
        save_data('clients.json', clients)
        return redirect(url_for('clients_list'))
    return render_template('client_form.html', client=None)

@app.route('/clients/edit/<client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    clients = load_data('clients.json')
    client = next((c for c in clients if c['id'] == client_id), None)
    
    if not client:
        return redirect(url_for('clients_list'))
    
    if request.method == 'POST':
        client['name'] = request.form.get('name', '')
        client['whatsapp'] = request.form.get('whatsapp', '')
        client['email'] = request.form.get('email', '')
        save_data('clients.json', clients)
        return redirect(url_for('clients_list'))
    
    return render_template('client_form.html', client=client)

@app.route('/clients/delete/<client_id>', methods=['POST'])
def delete_client(client_id):
    clients = load_data('clients.json')
    clients = [c for c in clients if c['id'] != client_id]
    save_data('clients.json', clients)
    return redirect(url_for('clients_list'))

@app.route('/receipts')
def receipts_list():
    receipts = load_data('receipts.json')
    clients = load_data('clients.json')
    client_map = {c['id']: c for c in clients}
    
    for receipt in receipts:
        client = client_map.get(receipt.get('client_id'))
        receipt['client'] = client
    
    receipts = sorted(receipts, key=lambda x: x.get('created_at', ''), reverse=True)
    return render_template('receipts.html', receipts=receipts)

@app.route('/receipts/add', methods=['GET', 'POST'])
def add_receipt():
    clients = load_data('clients.json')
    
    if request.method == 'POST':
        receipts = load_data('receipts.json')
        receipt_number = f"REC-{datetime.now().strftime('%Y%m%d')}-{len(receipts) + 1:04d}"
        
        new_receipt = {
            'id': str(uuid.uuid4()),
            'receipt_number': receipt_number,
            'client_id': request.form.get('client_id', ''),
            'description': request.form.get('description', ''),
            'amount': request.form.get('amount', '0'),
            'payment_method': request.form.get('payment_method', ''),
            'created_at': datetime.now().isoformat()
        }
        receipts.append(new_receipt)
        save_data('receipts.json', receipts)
        return redirect(url_for('receipts_list'))
    
    return render_template('receipt_form.html', receipt=None, clients=clients)

@app.route('/receipts/view/<receipt_id>')
def view_receipt(receipt_id):
    receipts = load_data('receipts.json')
    clients = load_data('clients.json')
    settings = load_settings()
    
    receipt = next((r for r in receipts if r['id'] == receipt_id), None)
    if not receipt:
        return redirect(url_for('receipts_list'))
    
    client = next((c for c in clients if c['id'] == receipt.get('client_id')), None)
    receipt['client'] = client
    
    return render_template('receipt_view.html', receipt=receipt, settings=settings)

@app.route('/receipts/delete/<receipt_id>', methods=['POST'])
def delete_receipt(receipt_id):
    receipts = load_data('receipts.json')
    receipts = [r for r in receipts if r['id'] != receipt_id]
    save_data('receipts.json', receipts)
    return redirect(url_for('receipts_list'))

@app.route('/receipts/pdf/<receipt_id>')
def download_pdf(receipt_id):
    receipts = load_data('receipts.json')
    clients = load_data('clients.json')
    settings = load_settings()
    
    receipt = next((r for r in receipts if r['id'] == receipt_id), None)
    if not receipt:
        return redirect(url_for('receipts_list'))
    
    client = next((c for c in clients if c['id'] == receipt.get('client_id')), None)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, spaceAfter=20, alignment=1)
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=12, spaceAfter=10)
    
    elements = []
    
    if settings.get('logo') and os.path.exists(settings['logo']):
        try:
            img = Image(settings['logo'], width=50*mm, height=25*mm)
            elements.append(img)
            elements.append(Spacer(1, 10*mm))
        except:
            pass
    
    if settings.get('company_name'):
        elements.append(Paragraph(settings['company_name'], title_style))
    
    company_info = []
    if settings.get('address'):
        company_info.append(settings['address'])
    if settings.get('phone'):
        company_info.append(f"Tel: {settings['phone']}")
    if settings.get('tax_id'):
        company_info.append(f"ICE/SIRET: {settings['tax_id']}")
    
    if company_info:
        elements.append(Paragraph(' | '.join(company_info), header_style))
        elements.append(Spacer(1, 10*mm))
    
    elements.append(Paragraph(f"<b>{t('receipts.receipt')}</b>", ParagraphStyle('ReceiptTitle', fontSize=18, spaceAfter=15)))
    elements.append(Paragraph(f"N°: {receipt.get('receipt_number', '')}", normal_style))
    
    date_str = receipt.get('created_at', '')[:10] if receipt.get('created_at') else ''
    elements.append(Paragraph(f"Date: {date_str}", normal_style))
    elements.append(Spacer(1, 10*mm))
    
    if client:
        elements.append(Paragraph(f"<b>{t('clients.client')}:</b> {client.get('name', '')}", normal_style))
        if client.get('email'):
            elements.append(Paragraph(f"Email: {client.get('email')}", normal_style))
        if client.get('whatsapp'):
            elements.append(Paragraph(f"WhatsApp: {client.get('whatsapp')}", normal_style))
    
    elements.append(Spacer(1, 10*mm))
    
    table_data = [
        [t('receipts.description'), t('receipts.amount')]
    ]
    table_data.append([receipt.get('description', ''), f"{receipt.get('amount', '0')} MAD"])
    
    table = Table(table_data, colWidths=[120*mm, 40*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
    ]))
    elements.append(table)
    
    elements.append(Spacer(1, 5*mm))
    
    payment_methods = {
        'cash': t('receipts.payment_methods.cash'),
        'card': t('receipts.payment_methods.card'),
        'transfer': t('receipts.payment_methods.transfer'),
        'check': t('receipts.payment_methods.check')
    }
    payment_text = payment_methods.get(receipt.get('payment_method', ''), receipt.get('payment_method', ''))
    elements.append(Paragraph(f"<b>{t('receipts.payment_method')}:</b> {payment_text}", normal_style))
    
    elements.append(Spacer(1, 20*mm))
    elements.append(Paragraph(t('receipts.thank_you'), ParagraphStyle('ThankYou', fontSize=12, alignment=1, textColor=colors.grey)))
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{receipt.get('receipt_number', 'receipt')}.pdf",
        mimetype='application/pdf'
    )

@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
    settings = load_settings()
    
    if request.method == 'POST':
        settings['company_name'] = request.form.get('company_name', '')
        settings['address'] = request.form.get('address', '')
        settings['tax_id'] = request.form.get('tax_id', '')
        settings['phone'] = request.form.get('phone', '')
        
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename:
                filename = f"logo_{uuid.uuid4().hex[:8]}.png"
                filepath = os.path.join(UPLOAD_DIR, filename)
                
                img = PILImage.open(file)
                img.thumbnail((400, 200))
                img.save(filepath, 'PNG')
                
                settings['logo'] = filepath
        
        save_settings(settings)
        return redirect(url_for('settings_page'))
    
    return render_template('settings.html', settings=settings)

@app.route('/api/share/<receipt_id>')
def get_share_data(receipt_id):
    receipts = load_data('receipts.json')
    clients = load_data('clients.json')
    settings = load_settings()
    
    receipt = next((r for r in receipts if r['id'] == receipt_id), None)
    if not receipt:
        return jsonify({'error': 'Receipt not found'}), 404
    
    client = next((c for c in clients if c['id'] == receipt.get('client_id')), None)
    
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
    
    whatsapp_number = client.get('whatsapp', '') if client else ''
    email = client.get('email', '') if client else ''
    
    return jsonify({
        'message': message,
        'whatsapp_number': whatsapp_number,
        'email': email,
        'subject': f"{t('receipts.receipt')} {receipt_number}"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
