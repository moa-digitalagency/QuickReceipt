import os
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from utils.i18n import t
import qrcode

SITE_URL = "https://e7aac102-329f-48e9-a67b-03b5ad98498e-00-1gdvtlkjo0i55.picard.replit.dev"

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
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=26, spaceAfter=10, alignment=1)
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=10, textColor=colors.grey, alignment=1)
    centered_style = ParagraphStyle('Centered', parent=styles['Normal'], fontSize=12, alignment=1)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=12, spaceAfter=10)
    centered_normal = ParagraphStyle('CenteredNormal', parent=styles['Normal'], fontSize=12, spaceAfter=10, alignment=1)
    receipt_title_style = ParagraphStyle('ReceiptTitle', fontSize=20, spaceAfter=15, alignment=1)
    total_style = ParagraphStyle('TotalStyle', fontSize=26, spaceAfter=10, alignment=1, textColor=colors.HexColor('#1E40AF'))
    
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
        company_name_upper = company['name'].upper()
        elements.append(Paragraph(f"<b>{company_name_upper}</b>", title_style))
    
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
    elements.append(Paragraph(f"<b>N: {receipt.get('receipt_number', '')}</b>", receipt_title_style))
    
    date_str = receipt.get('created_at', '')[:10] if receipt.get('created_at') else ''
    elements.append(Paragraph(f"Date: {date_str}", centered_style))
    elements.append(Spacer(1, 10*mm))
    
    if client:
        elements.append(Paragraph(f"<b>{t('clients.client')}:</b> {client.get('name', '')}", centered_normal))
        if client.get('email'):
            elements.append(Paragraph(f"Email: {client.get('email')}", centered_style))
        if client.get('whatsapp'):
            elements.append(Paragraph(f"WhatsApp: {client.get('whatsapp')}", centered_style))
    
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
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
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
    elements.append(Paragraph(f"<b>{t('receipts.payment_method')}:</b> {payment_text}", centered_normal))
    
    elements.append(Spacer(1, 15*mm))
    elements.append(Paragraph(t('receipts.thank_you'), ParagraphStyle('ThankYou', fontSize=14, alignment=1, textColor=colors.grey)))
    
    elements.append(Spacer(1, 10*mm))
    
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(SITE_URL)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    qr_image = Image(qr_buffer, width=30*mm, height=30*mm)
    qr_image.hAlign = 'CENTER'
    elements.append(qr_image)
    
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph("quickreceipt.app", ParagraphStyle('SiteUrl', fontSize=10, alignment=1, textColor=colors.HexColor('#3B82F6'))))
    
    doc.build(elements)
    buffer.seek(0)
    
    return buffer
