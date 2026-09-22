import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'samaria-dev-secret-key-2026'
    DATABASE = os.path.join(basedir, os.environ.get('DATABASE_PATH') or 'instance/samaria.db')
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'img', 'productos')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH') or 10 * 1024 * 1024)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'
    ADMIN_NAME = os.environ.get('ADMIN_NAME') or 'Administrador Samaria'