import os
import uuid
from PIL import Image as PILImage

UPLOAD_DIR = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024

os.makedirs(UPLOAD_DIR, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_logo(file):
    if not file or not file.filename:
        return None
    
    if not allowed_file(file.filename):
        return None
    
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    
    if size > MAX_FILE_SIZE:
        return None
    
    filename = f"logo_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    try:
        img = PILImage.open(file.stream)
        img.verify()
        file.seek(0)
        img = PILImage.open(file.stream)
        img.thumbnail((400, 200))
        img.save(filepath, 'PNG')
        return filepath
    except Exception:
        return None

def save_icon(file):
    if not file or not file.filename:
        return None

    if not allowed_file(file.filename):
        return None

    filename = f"icon_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(UPLOAD_DIR, filename)

    try:
        img = PILImage.open(file.stream)
        img.verify()
        file.seek(0)
        img = PILImage.open(file.stream)
        # Ensure it's square-ish or just resize to fit 512x512
        img.thumbnail((512, 512))
        img.save(filepath, 'PNG')
        return filepath
    except Exception:
        return None
