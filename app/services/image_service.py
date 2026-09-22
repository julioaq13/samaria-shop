import os
import re
import uuid
from werkzeug.utils import secure_filename
from flask import current_app, url_for, has_request_context
from PIL import Image

class ImageService:
    @staticmethod
    def allowed_file(filename):
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in current_app.config['ALLOWED_EXTENSIONS']

    @staticmethod
    def extract_drive_id(url_or_id):
        """
        Extrae el ID único de archivo de cualquier formato de enlace de Google Drive.
        Ejemplos soportados:
          - https://drive.google.com/file/d/1ABCXYZ123/view?usp=sharing
          - https://drive.google.com/open?id=1ABCXYZ123
          - https://drive.google.com/uc?id=1ABCXYZ123
          - 1ABCXYZ123 (ID directo)
        """
        if not url_or_id:
            return None
        text = str(url_or_id).strip()

        # Patrón /file/d/<id>
        match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', text)
        if match:
            return match.group(1)

        # Patrón id=<id>
        match = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', text)
        if match:
            return match.group(1)

        # Patrón /d/<id>
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', text)
        if match:
            return match.group(1)

        # ID directo alfanumérico largo
        if re.match(r'^[a-zA-Z0-9_-]{20,}$', text) and '/' not in text:
            return text

        return text

    @staticmethod
    def save_image(file_storage, upload_folder=None):
        if not file_storage or file_storage.filename == '':
            return None

        if not ImageService.allowed_file(file_storage.filename):
            raise ValueError('Formato de imagen no permitido. Utilice JPG, JPEG, PNG o WEBP.')

        if not upload_folder:
            upload_folder = current_app.config['UPLOAD_FOLDER']

        os.makedirs(upload_folder, exist_ok=True)

        original_name = secure_filename(file_storage.filename)
        ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'jpg'
        
        unique_name = f'zapato_{uuid.uuid4().hex[:12]}.{ext}'
        target_path = os.path.join(upload_folder, unique_name)

        file_storage.seek(0)
        try:
            with Image.open(file_storage) as img:
                img.save(target_path, quality=90, optimize=True)
        except Exception:
            file_storage.seek(0)
            file_storage.save(target_path)

        return unique_name

    @staticmethod
    def delete_local_file(filename, upload_folder=None):
        if not filename:
            return
        if not upload_folder:
            upload_folder = current_app.config['UPLOAD_FOLDER']
        
        filepath = os.path.join(upload_folder, filename)
        if os.path.exists(filepath) and os.path.isfile(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass

    @staticmethod
    def get_image_url(image_record_or_path, origen='local'):
        """
        Abstracción para resolver la URL de la imagen.
        Soporta orígenes 'local', 'drive' (Google Drive) y 'url'.
        """
        default_placeholder = '/static/img/placeholder_shoe.png'
        if has_request_context():
            default_placeholder = url_for('static', filename='img/placeholder_shoe.png')

        if not image_record_or_path:
            return default_placeholder

        if isinstance(image_record_or_path, dict) or hasattr(image_record_or_path, '__getitem__'):
            try:
                ruta = image_record_or_path['ruta_o_url'] if 'ruta_o_url' in image_record_or_path else (image_record_or_path['imagen_url'] if 'imagen_url' in image_record_or_path else str(image_record_or_path))
                orig = image_record_or_path.get('origen', origen) if isinstance(image_record_or_path, dict) else (image_record_or_path['origen'] if 'origen' in image_record_or_path else origen)
            except Exception:
                ruta = str(image_record_or_path)
                orig = origen
        else:
            ruta = str(image_record_or_path)
            orig = origen

        if not ruta:
            return default_placeholder

        # Si ya es una URL web completa y origen no es 'local'
        if orig == 'drive' or ('drive.google.com' in ruta):
            file_id = ImageService.extract_drive_id(ruta)
            # Enlace de renderizado directo de Google Usercontent (rápido y sin bloqueos de redirección)
            return f'https://lh3.googleusercontent.com/d/{file_id}'
        elif orig == 'url' or ruta.startswith('http://') or ruta.startswith('https://'):
            return ruta
        elif orig == 'local':
            if has_request_context():
                return url_for('static', filename=f'img/productos/{ruta}' if not ruta.startswith('img/') else ruta)
            return f'/static/img/productos/{ruta}'
        else:
            return ruta