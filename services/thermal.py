import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import qrcode

SITE_URL = "https://e7aac102-329f-48e9-a67b-03b5ad98498e-00-1gdvtlkjo0i55.picard.replit.dev"

def generate_thermal_receipt(receipt, client, company, settings):
    thermal_width_mm = int(settings.get('thermal_width', 58))
    
    dpi = 203
    width_px = int(thermal_width_mm * dpi / 25.4)
    
    margin = 8
    
    if thermal_width_mm <= 48:
        font_size_title = 16
        font_size_bold = 14
        font_size_normal = 12
        font_size_small = 10
        line_height = 22
        small_line_height = 18
        qr_size = 80
    elif thermal_width_mm <= 58:
        font_size_title = 20
        font_size_bold = 18
        font_size_normal = 14
        font_size_small = 12
        line_height = 28
        small_line_height = 22
        qr_size = 100
    else:
        font_size_title = 24
        font_size_bold = 22
        font_size_normal = 16
        font_size_small = 14
        line_height = 32
        small_line_height = 26
        qr_size = 120
    
    lines_needed = 35
    height_px = lines_needed * line_height + 200 + qr_size
    
    img = Image.new('RGB', (width_px, height_px), 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size_title)
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size_bold)
        font_normal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size_normal)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size_small)
    except:
        font_title = ImageFont.load_default()
        font_bold = ImageFont.load_default()
        font_normal = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    y = margin + 5
    
    company_name = company.get('name', '') if company else 'QuickReceipt'
    if company_name:
        company_name_upper = company_name.upper()
        text_bbox = draw.textbbox((0, 0), company_name_upper, font=font_title)
        text_width = text_bbox[2] - text_bbox[0]
        x = (width_px - text_width) // 2
        draw.text((x, y), company_name_upper, fill='black', font=font_title)
        y += line_height + 5
    
    if company and company.get('address'):
        address_lines = company['address'].split('\n')
        for addr_line in address_lines:
            if addr_line.strip():
                text_bbox = draw.textbbox((0, 0), addr_line.strip(), font=font_small)
                text_width = text_bbox[2] - text_bbox[0]
                x = (width_px - text_width) // 2
                draw.text((x, y), addr_line.strip(), fill='black', font=font_small)
                y += small_line_height
    
    if company and company.get('phone'):
        phone_text = f"Tel: {company['phone']}"
        text_bbox = draw.textbbox((0, 0), phone_text, font=font_small)
        text_width = text_bbox[2] - text_bbox[0]
        x = (width_px - text_width) // 2
        draw.text((x, y), phone_text, fill='black', font=font_small)
        y += small_line_height
    
    if company and company.get('tax_id'):
        tax_text = f"ICE: {company['tax_id']}"
        text_bbox = draw.textbbox((0, 0), tax_text, font=font_small)
        text_width = text_bbox[2] - text_bbox[0]
        x = (width_px - text_width) // 2
        draw.text((x, y), tax_text, fill='black', font=font_small)
        y += small_line_height
    
    y += 8
    draw.line([(margin, y), (width_px - margin, y)], fill='black', width=2)
    y += 12
    
    receipt_text = f"RECU N: {receipt.get('receipt_number', '')}"
    text_bbox = draw.textbbox((0, 0), receipt_text, font=font_title)
    text_width = text_bbox[2] - text_bbox[0]
    x = (width_px - text_width) // 2
    draw.text((x, y), receipt_text, fill='black', font=font_title)
    y += line_height
    
    date_str = receipt.get('created_at', '')[:10] if receipt.get('created_at') else ''
    date_text = f"Date: {date_str}"
    text_bbox = draw.textbbox((0, 0), date_text, font=font_normal)
    text_width = text_bbox[2] - text_bbox[0]
    x = (width_px - text_width) // 2
    draw.text((x, y), date_text, fill='black', font=font_normal)
    y += line_height
    
    y += 8
    draw.line([(margin, y), (width_px - margin, y)], fill='black', width=1)
    y += 12
    
    if client:
        client_text = f"Client: {client.get('name', '')}"
        text_bbox = draw.textbbox((0, 0), client_text, font=font_normal)
        text_width = text_bbox[2] - text_bbox[0]
        x = (width_px - text_width) // 2
        draw.text((x, y), client_text, fill='black', font=font_normal)
        y += line_height
    
    y += 8
    draw.line([(margin, y), (width_px - margin, y)], fill='black', width=1)
    y += 12
    
    description = receipt.get('description', '')
    max_chars = max(10, (width_px - 2 * margin) // (font_size_normal // 2))
    desc_lines = []
    words = description.split(' ')
    current_line = ''
    for word in words:
        test_line = current_line + ' ' + word if current_line else word
        if len(test_line) <= max_chars:
            current_line = test_line
        else:
            if current_line:
                desc_lines.append(current_line)
            current_line = word
    if current_line:
        desc_lines.append(current_line)
    
    for desc_line in desc_lines[:4]:
        text_bbox = draw.textbbox((0, 0), desc_line, font=font_normal)
        text_width = text_bbox[2] - text_bbox[0]
        x = (width_px - text_width) // 2
        draw.text((x, y), desc_line, fill='black', font=font_normal)
        y += small_line_height
    
    y += 12
    draw.line([(margin, y), (width_px - margin, y)], fill='black', width=3)
    y += 15
    
    amount_text = f"TOTAL: {receipt.get('amount', '0')} MAD"
    text_bbox = draw.textbbox((0, 0), amount_text, font=font_title)
    text_width = text_bbox[2] - text_bbox[0]
    x = (width_px - text_width) // 2
    draw.text((x, y), amount_text, fill='black', font=font_title)
    y += line_height + 5
    
    payment_methods = {
        'cash': 'Especes',
        'card': 'Carte',
        'transfer': 'Virement',
        'check': 'Cheque'
    }
    payment_text = payment_methods.get(receipt.get('payment_method', ''), receipt.get('payment_method', ''))
    pay_text = f"Paiement: {payment_text}"
    text_bbox = draw.textbbox((0, 0), pay_text, font=font_normal)
    text_width = text_bbox[2] - text_bbox[0]
    x = (width_px - text_width) // 2
    draw.text((x, y), pay_text, fill='black', font=font_normal)
    y += line_height
    
    y += 12
    draw.line([(margin, y), (width_px - margin, y)], fill='black', width=1)
    y += 15
    
    thanks = "Merci pour votre confiance!"
    text_bbox = draw.textbbox((0, 0), thanks, font=font_small)
    text_width = text_bbox[2] - text_bbox[0]
    x = (width_px - text_width) // 2
    draw.text((x, y), thanks, fill='black', font=font_small)
    y += small_line_height + 10
    
    qr = qrcode.QRCode(version=1, box_size=3, border=1)
    qr.add_data(SITE_URL)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.resize((qr_size, qr_size))
    qr_x = (width_px - qr_size) // 2
    img.paste(qr_img, (qr_x, y))
    y += qr_size + 8
    
    site_text = "quickreceipt.app"
    text_bbox = draw.textbbox((0, 0), site_text, font=font_small)
    text_width = text_bbox[2] - text_bbox[0]
    x = (width_px - text_width) // 2
    draw.text((x, y), site_text, fill='black', font=font_small)
    y += small_line_height + 15
    
    img = img.crop((0, 0, width_px, y))
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer
