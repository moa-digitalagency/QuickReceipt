import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import qrcode
from urllib.parse import urlparse  # Ajout pour extraire le domaine proprement

def get_site_url():
    # 1. Vérifier d'abord une variable d'environnement standard pour l'URL du site
    if os.environ.get('SITE_URL'):
        return os.environ.get('SITE_URL').rstrip('/')

    # 2. Sinon, vérifier la configuration Replit
    domain = os.environ.get('REPLIT_DEV_DOMAIN', '')
    if domain:
        return f"https://{domain}"

    # 3. Fallback par défaut (ne sera utilisé que si rien d'autre n'est configuré)
    return "https://quickreceipt.app"

def generate_thermal_receipt(receipt, client, company, settings):
    # Utiliser l'URL passée dans les settings en priorité, sinon chercher dans l'environnement
    site_url = settings.get('site_url') or get_site_url()

    thermal_width_mm = int(settings.get('thermal_width', 58))

    dpi = 203
    width_px = int(thermal_width_mm * dpi / 25.4)

    margin = 8

    if thermal_width_mm <= 48:
        font_size_title = 16
        font_size_text = 14
        line_height = 24
        qr_size = 80
        logo_height = 50
    elif thermal_width_mm <= 58:
        font_size_title = 20
        font_size_text = 16
        line_height = 28
        qr_size = 100
        logo_height = 60
    else:
        font_size_title = 26
        font_size_text = 20
        line_height = 34
        qr_size = 120
        logo_height = 80

    lines_needed = 45
    height_px = lines_needed * line_height + 200 + qr_size + logo_height

    img = Image.new('RGB', (width_px, height_px), 'white')
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size_title)
        font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size_text)
        font_text_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size_text)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
        font_text_bold = ImageFont.load_default()

    y = margin + 5

    if company and company.get('logo') and os.path.exists(company['logo']):
        try:
            logo_img = Image.open(company['logo'])
            aspect = logo_img.width / logo_img.height
            logo_w = int(logo_height * aspect)
            if logo_w > width_px - 2 * margin:
                logo_w = width_px - 2 * margin
                logo_h = int(logo_w / aspect)
            else:
                logo_h = logo_height
            logo_img = logo_img.resize((logo_w, logo_h), Image.LANCZOS)
            if logo_img.mode != 'RGB':
                logo_img = logo_img.convert('RGB')
            logo_x = (width_px - logo_w) // 2
            img.paste(logo_img, (logo_x, y))
            y += logo_h + 10
        except Exception as e:
            pass

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
                text_bbox = draw.textbbox((0, 0), addr_line.strip(), font=font_text)
                text_width = text_bbox[2] - text_bbox[0]
                x = (width_px - text_width) // 2
                draw.text((x, y), addr_line.strip(), fill='black', font=font_text)
                y += line_height

    if company and company.get('phone'):
        phone_text = f"Tel: {company['phone']}"
        text_bbox = draw.textbbox((0, 0), phone_text, font=font_text)
        text_width = text_bbox[2] - text_bbox[0]
        x = (width_px - text_width) // 2
        draw.text((x, y), phone_text, fill='black', font=font_text)
        y += line_height

    if company and company.get('tax_id'):
        tax_text = f"ICE: {company['tax_id']}"
        text_bbox = draw.textbbox((0, 0), tax_text, font=font_text)
        text_width = text_bbox[2] - text_bbox[0]
        x = (width_px - text_width) // 2
        draw.text((x, y), tax_text, fill='black', font=font_text)
        y += line_height

    y += 8
    draw.line([(margin, y), (width_px - margin, y)], fill='black', width=2)
    y += 12

    receipt_text = f"RECU N: {receipt.get('receipt_number', '')}"
    text_bbox = draw.textbbox((0, 0), receipt_text, font=font_title)
    text_width = text_bbox[2] - text_bbox[0]
    x = (width_px - text_width) // 2
    draw.text((x, y), receipt_text, fill='black', font=font_title)
    y += line_height + 5

    created_at = receipt.get('created_at', '')
    if created_at:
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            months_fr = ['janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin', 
                        'juillet', 'aout', 'septembre', 'octobre', 'novembre', 'decembre']
            date_str = f"{dt.day} {months_fr[dt.month-1]} {dt.year} a {dt.strftime('%H:%M')}"
        except:
            date_str = created_at[:16]
    else:
        date_str = ''
    date_text = f"Date: {date_str}"
    text_bbox = draw.textbbox((0, 0), date_text, font=font_text)
    text_width = text_bbox[2] - text_bbox[0]
    x = (width_px - text_width) // 2
    draw.text((x, y), date_text, fill='black', font=font_text)
    y += line_height

    y += 8
    draw.line([(margin, y), (width_px - margin, y)], fill='black', width=1)
    y += 12

    if client:
        client_text = f"Client: {client.get('name', '')}"
        text_bbox = draw.textbbox((0, 0), client_text, font=font_text_bold)
        text_width = text_bbox[2] - text_bbox[0]
        x = (width_px - text_width) // 2
        draw.text((x, y), client_text, fill='black', font=font_text_bold)
        y += line_height

    y += 8
    draw.line([(margin, y), (width_px - margin, y)], fill='black', width=1)
    y += 12

    description = receipt.get('description', '')
    max_chars = max(10, (width_px - 2 * margin) // (font_size_text // 2))
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
        text_bbox = draw.textbbox((0, 0), desc_line, font=font_text)
        text_width = text_bbox[2] - text_bbox[0]
        x = (width_px - text_width) // 2
        draw.text((x, y), desc_line, fill='black', font=font_text)
        y += line_height

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
    text_bbox = draw.textbbox((0, 0), pay_text, font=font_text)
    text_width = text_bbox[2] - text_bbox[0]
    x = (width_px - text_width) // 2
    draw.text((x, y), pay_text, fill='black', font=font_text)
    y += line_height

    y += 12
    draw.line([(margin, y), (width_px - margin, y)], fill='black', width=1)
    y += 15

    thanks = "Merci pour votre confiance!"
    text_bbox = draw.textbbox((0, 0), thanks, font=font_text)
    text_width = text_bbox[2] - text_bbox[0]
    x = (width_px - text_width) // 2
    draw.text((x, y), thanks, fill='black', font=font_text)
    y += line_height + 10

    qr = qrcode.QRCode(version=1, box_size=3, border=1)
    qr.add_data(site_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.resize((qr_size, qr_size))
    qr_x = (width_px - qr_size) // 2
    img.paste(qr_img, (qr_x, y))
    y += qr_size + 8

    # Correction ICI : On extrait le domaine proprement depuis l'URL utilisée
    try:
        domain = urlparse(site_url).netloc
        # Si netloc est vide (ex: localhost sans http), on prend l'URL telle quelle
        if not domain:
            domain = site_url
    except:
        domain = os.environ.get('REPLIT_DEV_DOMAIN', 'quickreceipt.app')

    text_bbox = draw.textbbox((0, 0), domain, font=font_text)
    text_width = text_bbox[2] - text_bbox[0]
    x = (width_px - text_width) // 2
    draw.text((x, y), domain, fill='black', font=font_text)
    y += line_height + 15

    img = img.crop((0, 0, width_px, y))

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return buffer