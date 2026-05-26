import os

# BASE_DIR: directorul proiectului

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# DB_PATH: calea spre baza de date SQLite
DB_PATH = os.path.join(BASE_DIR, 'db/users.db')

# UPLOAD_FOLDER: directorul se vor salva fisierel incarcate
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# ALLOWED_EXTENSIONS: extensiile permise pentru upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# MAX_CONTENT_LENGTH: dimensiunea maxima a unui fisier uploadat
MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB

# SECRET_KEY: folosit de Flask pentru securitate
SECRET_KEY = '123456'
