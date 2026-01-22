import os
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from utils.i18n import t

def generate_receipt_pdf(receipt, client, settings):
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
    
    return buffer
