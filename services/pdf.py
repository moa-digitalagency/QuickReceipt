import os
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from utils.i18n import t
import qrcode
from urllib.parse import urlparse

def generate_receipt_pdf(receipt, client, company, settings):
    site_url = settings.get('site_url', '')

    try:
        domain = urlparse(site_url).netloc
        if not domain:
            domain = site_url
    except:
        domain = site_url
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=20*mm, 
        leftMargin=20*mm, 
        topMargin=20*mm, 
        bottomMargin=20*mm
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=26, spaceAfter=10, alignment=1)
    text_style = ParagraphStyle('Text', parent=styles['Normal'], fontSize=14, alignment=1, spaceAfter=8)
    text_style_left = ParagraphStyle('TextLeft', parent=styles['Normal'], fontSize=14, spaceAfter=8)
    receipt_title_style = ParagraphStyle('ReceiptTitle', fontSize=22, spaceAfter=10, alignment=1)
    total_style = ParagraphStyle('TotalStyle', fontSize=26, spaceAfter=10, alignment=1, textColor=colors.HexColor('#1E40AF'))
    
    elements = []
    
    if company and company.get('logo') and os.path.exists(company['logo']):
        try:
            img = Image(company['logo'], width=50*mm, height=25*mm)
            img.hAlign = 'CENTER'
            elements.append(img)
            elements.append(Spacer(1, 5*mm))
        except:
            pass
    
    if company and company.get('name'):
        company_name_upper = company['name'].upper()
        elements.append(Paragraph(f"<b>{company_name_upper}</b>", title_style))
    
    if company:
        if company.get('address'):
            address_text = company['address'].replace('\n', '<br/>')
            elements.append(Paragraph(address_text, text_style))
        if company.get('phone'):
            elements.append(Paragraph(f"Tel: {company['phone']}", text_style))
        if company.get('tax_id'):
            elements.append(Paragraph(f"ICE/SIRET: {company['tax_id']}", text_style))
    
    elements.append(Spacer(1, 15*mm))
    
    elements.append(Paragraph(f"<b>{t('receipts.receipt')}</b>", receipt_title_style))
    elements.append(Paragraph(f"<b>N: {receipt.get('receipt_number', '')}</b>", receipt_title_style))
    
    created_at = receipt.get('created_at', '')
    if created_at:
        from datetime import datetime as dt_module
        try:
            dt = dt_module.fromisoformat(created_at.replace('Z', '+00:00'))
            months_fr = ['janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin', 
                        'juillet', 'aout', 'septembre', 'octobre', 'novembre', 'decembre']
            date_str = f"{dt.day} {months_fr[dt.month-1]} {dt.year} a {dt.strftime('%H:%M')}"
        except:
            date_str = created_at[:16]
    else:
        date_str = ''
    elements.append(Paragraph(f"Date: {date_str}", text_style))
    elements.append(Spacer(1, 10*mm))
    
    if client:
        elements.append(Paragraph(f"<b>{t('clients.client')}:</b> {client.get('name', '')}", text_style))
        if client.get('email'):
            elements.append(Paragraph(f"Email: {client.get('email')}", text_style))
        if client.get('whatsapp'):
            elements.append(Paragraph(f"WhatsApp: {client.get('whatsapp')}", text_style))
    
    elements.append(Spacer(1, 10*mm))
    
    table_data = [
        [t('receipts.description'), t('receipts.amount')]
    ]
    table_data.append([receipt.get('description', ''), f"{receipt.get('amount', '0')} MAD"])
    
    table = Table(table_data, colWidths=[120*mm, 40*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('FONTSIZE', (0, 1), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
    ]))
    elements.append(table)
    
    elements.append(Spacer(1, 8*mm))
    
    elements.append(Paragraph(f"<b>TOTAL: {receipt.get('amount', '0')} MAD</b>", total_style))
    
    elements.append(Spacer(1, 5*mm))
    
    payment_methods = {
        'cash': t('receipts.payment_methods.cash'),
        'card': t('receipts.payment_methods.card'),
        'transfer': t('receipts.payment_methods.transfer'),
        'check': t('receipts.payment_methods.check')
    }
    payment_text = payment_methods.get(receipt.get('payment_method', ''), receipt.get('payment_method', ''))
    elements.append(Paragraph(f"<b>{t('receipts.payment_method')}:</b> {payment_text}", text_style))
    
    elements.append(Spacer(1, 15*mm))
    elements.append(Paragraph(t('receipts.thank_you'), ParagraphStyle('ThankYou', fontSize=14, alignment=1, textColor=colors.grey)))
    
    elements.append(Spacer(1, 10*mm))
    
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(site_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    qr_image = Image(qr_buffer, width=30*mm, height=30*mm)
    qr_image.hAlign = 'CENTER'
    elements.append(qr_image)
    
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph(domain, ParagraphStyle('SiteUrl', fontSize=14, alignment=1, textColor=colors.HexColor('#3B82F6'))))
    
    doc.build(elements)
    buffer.seek(0)
    
    return buffer
