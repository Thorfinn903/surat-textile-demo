import os
from pathlib import Path
from PIL import Image
from werkzeug.utils import secure_filename

def optimize_image(filepath):
    """Resize to max 800px width and save as .webp (Quality=80).
    Returns the new filename (basename only)."""
    img = Image.open(filepath)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > 800:
        ratio = 800 / img.width
        new_size = (800, int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    webp_path = str(filepath).rsplit('.', 1)[0] + '.webp'
    img.save(webp_path, 'WEBP', quality=80)
    
    if str(filepath) != webp_path:
        try:
            os.remove(str(filepath))
        except OSError:
            pass
    return Path(webp_path).name

def save_uploaded_file(file, upload_folder):
    if not file or not file.filename:
        return None
    filename = secure_filename(file.filename)
    upload_path = Path(upload_folder)
    upload_path.mkdir(parents=True, exist_ok=True)
    save_path = upload_path / filename
    file.save(str(save_path))
    return save_path
