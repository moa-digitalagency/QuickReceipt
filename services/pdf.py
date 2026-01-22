import os
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from utils.i18n import t

def generate_receipt_pdf(receipt, client, company, settings):
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
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, spaceAfter=10, alignment=1)
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=10, textColor=colors.grey, alignment=1)
    centered_style = ParagraphStyle('Centered', parent=styles['Normal'], fontSize=12, alignment=1)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=12, spaceAfter=10)
    receipt_title_style = ParagraphStyle('ReceiptTitle', fontSize=18, spaceAfter=15, alignment=1)
    
    elements = []
    
    if company and company.get('logo') and os.path.exists(company['logo']):
        try:
            from reportlab.lib.utils import ImageReader
            img = Image(company['logo'], width=50*mm, height=25*mm)
            img.hAlign = 'CENTER'
            elements.append(img)
            elements.append(Spacer(1, 5*mm))
        except:
            pass
    
    if company and company.get('name'):
        elements.append(Paragraph(company['name'], title_style))
    
    if company:
        if company.get('address'):
            address_text = company['address'].replace('\n', '<br/>')
            elements.append(Paragraph(address_text, header_style))
        if company.get('phone'):
            elements.append(Paragraph(f"Tel: {company['phone']}", header_style))
        if company.get('tax_id'):
            elements.append(Paragraph(f"ICE/SIRET: {company['tax_id']}", header_style))
    
    elements.append(Spacer(1, 15*mm))
    
    elements.append(Paragraph(f"<b>{t('receipts.receipt')}</b>", receipt_title_style))
    elements.append(Paragraph(f"N: {receipt.get('receipt_number', '')}", centered_style))
    
    date_str = receipt.get('created_at', '')[:10] if receipt.get('created_at') else ''
    elements.append(Paragraph(f"Date: {date_str}", centered_style))
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
