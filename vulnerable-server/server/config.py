import os

# BASE_DIR: directorul proiectului

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# DB_PATH: calea spre baza de date SQLite
DB_PATH = os.path.join(BASE_DIR, 'db/users.db')

# UPLOAD_FOLDER: directorul se vor salva fisierel incarcate
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# [VULNERABILITATE] Permitem orice extensie, inclusiv executabile (.php, .exe, .py)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'php', 'exe', 'sh', 'py'}

# MAX_CONTENT_LENGTH: dimensiunea maxima a unui fisier uploadat
MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB

# [VULNERABILITATE] Cheie secreta slaba si hardcodata.
# Un atacator o poate ghici si poate falsifica cookie-urile de sesiune (Session Forging).
SECRET_KEY = '123456'


# [VULNERABILITATE] Cookie-urile nu sunt protejate.
# Javascript poate citi cookie-ul de sesiune (document.cookie), permitand Session Hijacking prin XSS.
SESSION_COOKIE_HTTPONLY = False 
SESSION_COOKIE_SECURE = False   # Se trimit si prin HTTP (nu doar HTTPS)