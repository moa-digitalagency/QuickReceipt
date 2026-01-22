import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def generate_thermal_receipt(receipt, client, settings):
    thermal_width_mm = int(settings.get('thermal_width', 58))
    
    dpi = 203
    width_px = int(thermal_width_mm * dpi / 25.4)
    
    margin = 10
    line_height = 24
    small_line_height = 20
    
    lines_needed = 20
    height_px = lines_needed * line_height + 100
    
    img = Image.new('RGB', (width_px, height_px), 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        font_normal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except:
        font_bold = ImageFont.load_default()
        font_normal = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    y = margin
    
    company_name = settings.get('company_name', 'QuickReceipt')
    if company_name:
        text_bbox = draw.textbbox((0, 0), company_name, font=font_bold)
        text_width = text_bbox[2] - text_bbox[0]
        x = (width_px - text_width) // 2
        draw.text((x, y), company_name, fill='black', font=font_bold)
        y += line_height
    
    if settings.get('address'):
        address_lines = settings['address'].split('\n')
        for addr_line in address_lines:
            if addr_line.strip():
                text_bbox = draw.textbbox((0, 0), addr_line.strip(), font=font_small)
                text_width = text_bbox[2] - text_bbox[0]
                x = (width_px - text_width) // 2
                draw.text((x, y), addr_line.strip(), fill='black', font=font_small)
                y += small_line_height
    
    if settings.get('phone'):
        phone_text = f"Tel: {settings['phone']}"
        text_bbox = draw.textbbox((0, 0), phone_text, font=font_small)
        text_width = text_bbox[2] - text_bbox[0]
        x = (width_px - text_width) // 2
        draw.text((x, y), phone_text, fill='black', font=font_small)
        y += small_line_height
    
    y += 5
    draw.line([(margin, y), (width_px - margin, y)], fill='black', width=1)
    y += 10
    
    receipt_text = f"RECU N: {receipt.get('receipt_number', '')}"
    text_bbox = draw.textbbox((0, 0), receipt_text, font=font_bold)
    text_width = text_bbox[2] - text_bbox[0]
    x = (width_px - text_width) // 2
    draw.text((x, y), receipt_text, fill='black', font=font_bold)
    y += line_height
    
    date_str = receipt.get('created_at', '')[:10] if receipt.get('created_at') else ''
    date_text = f"Date: {date_str}"
    text_bbox = draw.textbbox((0, 0), date_text, font=font_normal)
    text_width = text_bbox[2] - text_bbox[0]
    x = (width_px - text_width) // 2
    draw.text((x, y), date_text, fill='black', font=font_normal)
    y += line_height
    
    y += 5
    draw.line([(margin, y), (width_px - margin, y)], fill='black', width=1)
    y += 10
    
    if client:
        draw.text((margin, y), f"Client: {client.get('name', '')}", fill='black', font=font_normal)
        y += line_height
    
    y += 5
    draw.line([(margin, y), (width_px - margin, y)], fill='black', width=1)
    y += 10
    
    description = receipt.get('description', '')
    max_chars = (width_px - 2 * margin) // 7
    desc_lines = [description[i:i+max_chars] for i in range(0, len(description), max_chars)]
    for desc_line in desc_lines[:3]:
        draw.text((margin, y), desc_line, fill='black', font=font_normal)
        y += small_line_height
    
    y += 10
    draw.line([(margin, y), (width_px - margin, y)], fill='black', width=2)
    y += 10
    
    amount_text = f"TOTAL: {receipt.get('amount', '0')} MAD"
    text_bbox = draw.textbbox((0, 0), amount_text, font=font_bold)
    text_width = text_bbox[2] - text_bbox[0]
    x = (width_px - text_width) // 2
    draw.text((x, y), amount_text, fill='black', font=font_bold)
    y += line_height
    
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
    
    y += 10
    draw.line([(margin, y), (width_px - margin, y)], fill='black', width=1)
    y += 10
    
    thanks = "Merci pour votre confiance!"
    text_bbox = draw.textbbox((0, 0), thanks, font=font_small)
    text_width = text_bbox[2] - text_bbox[0]
    x = (width_px - text_width) // 2
    draw.text((x, y), thanks, fill='black', font=font_small)
    y += small_line_height + 10
    
    img = img.crop((0, 0, width_px, y))
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer
