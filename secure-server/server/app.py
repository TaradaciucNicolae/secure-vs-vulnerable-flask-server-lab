from flask import Flask, request, g, render_template, redirect, url_for, flash, session, make_response
import sqlite3
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash # libraria pentru hash-uirea parolelor
from config import DB_PATH, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, SECRET_KEY
from init_db import init_db
import time
from datetime import datetime, timezone
import logging
from logging.config import dictConfig
import json
from flask_oidc import OpenIDConnect
import requests
from flask_wtf import CSRFProtect

# Functie pentru a curata datele sensibile din loguri
def clean_sensitive_data(form_data):
    if not form_data:
        return {}
    # Facem o copie ca sa nu modificam datele reale din request
    safe_data = dict(form_data) 
    sensitive_keys = ['password', 'parola', 'confirm_parola', 'parola_noua', 'parola_veche']
    
    for key in safe_data:
        if key in sensitive_keys:
            safe_data[key] = '***ASCUNS***'
    return safe_data


init_db() # initiere bd


os.makedirs(os.path.join(os.path.dirname(__file__), 'logs'), exist_ok=True)
dictConfig({
    'version': 1,
    'formatters': {'detailed': {'format': '%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s'}},
    'handlers': {
        'file': {'class': 'logging.FileHandler', 'filename': os.path.join(os.path.dirname(__file__), 'logs', 'app.log'), 'formatter': 'detailed'},
        'console': {'class': 'logging.StreamHandler', 'formatter': 'detailed'}
    },
    'root': {'level': 'INFO', 'handlers': ['file', 'console']}
})


app = Flask(__name__, template_folder='./templates', static_folder='../static')
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


#  Setari pentru Cookie-uri securizate
app.config['SESSION_COOKIE_HTTPONLY'] = True # JavaScript nu poate fura cookie-ul de sesiune (Anti-XSS)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' # Previne CSRF basic

app.config.update({
    'OIDC_CLIENT_SECRETS': os.path.join(os.path.dirname(__file__), 'client_secrets.json'),
    'OIDC_ID_TOKEN_COOKIE_SECURE': False, 
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': 'master',
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
})

oidc = OpenIDConnect(app, prefix="/oidc")

# Adaugam HEADERE de securitate la fiecare raspuns al serverului
@app.after_request
def add_security_headers(response):
    # Previne incarcarea site-ului in iframe (Anti-Clickjacking)
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # Protejeaza impotriva MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Activeaza protectia XSS in browserele vechi
    response.headers['X-XSS-Protection'] = '1; mode=block'

    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
    return response

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    #  Verificam extensia 
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/inregistrare', methods=['GET', 'POST'])
def inregistrare():
    if request.method == 'POST':
        # Colectam campurile
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        
        #  Preluam parola si generam HASH-ul imediat
        password_plain = request.form.get('parola', '').strip()
        password_hash = generate_password_hash(password_plain) 
        
        nume = request.form.get('nume', '').strip()
        prenume = request.form.get('prenume', '').strip()
        nume_afisat = request.form.get('nume_afisat', '').strip()
        url_site = request.form.get('url_site', '').strip()

        # log cu start proces inregistrare
        app.logger.info(f"REGISTER ATTEMPT: User '{username}' starts registration from IP {request.remote_addr}")

        # Upload imagine
        imagine = request.files.get('imagine_profil')
        cale_imagine = None

        if imagine and imagine.filename != '':
            if allowed_file(imagine.filename):
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                filename = secure_filename(f"Avatar_{username}_{int(datetime.now(timezone.utc).timestamp())}_{imagine.filename}")
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                imagine.save(filepath)
                cale_imagine = os.path.relpath(filepath, start=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
                
                #  Upload reusit
                app.logger.info(f"UPLOAD SUCCESS: User '{username}' uploaded file '{imagine.filename}'")
            else:
                # Upload suspect
                app.logger.warning(f"SUSPICIOUS UPLOAD: User '{username}' tried to upload invalid file: '{imagine.filename}' | IP: {request.remote_addr}")
                
                flash('Format imagine invalid!')
                return redirect(url_for('inregistrare'))
        
        # Salvam in DB
        conn = get_conn()
        try:
            #  Aici salvam password_hash in loc de password 
            conn.execute('''INSERT INTO users 
                            (username, email, password, nume, prenume, numeAfisat, urlSite, caleImagineProfil)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                         (username, email, password_hash, nume, prenume, nume_afisat, url_site, cale_imagine))
            conn.commit()
            
            #  Inregistrare reusita
            app.logger.info(f"REGISTER SUCCESS: New user created: '{username}' | Email: {email}")
            
            flash('Inregistrare realizata cu succes! Te rugam sa te autentifici.')
            return redirect(url_for('login_form'))

        except sqlite3.IntegrityError as e:
            #  Eroare de integritate (userul exista deja)
            app.logger.warning(f"REGISTER FAILED: Duplicate username or email for '{username}'/'{email}'. Error: {e}")
            
            flash('Username sau email deja existent!')
        except Exception as e:
            # LOG cu Alta eroare
            app.logger.error(f"REGISTER ERROR: Database error for '{username}': {e}")
            flash('Eroare la baza de date.')
        finally:
            conn.close()

        return redirect(url_for('acasa'))
    
    return render_template('reg.html')



@app.route('/cauta')
def cauta():
    termen = request.args.get('termen')
    users = []

    if termen:
        conn = get_conn()
        cur = conn.cursor()

        try:
            # aici prevenim SQL Injection 
            # Folosim interogare parametrizata
            query = """
                SELECT username, nume, prenume, email, numeAfisat FROM users 
                WHERE username LIKE ? 
                OR nume LIKE ? 
                OR prenume LIKE ? 
                OR email LIKE ? 
            """
            search_pattern = f"%{termen}%"
    
            cur.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))
            users = cur.fetchall()
            
            app.logger.info(f"SEARCH: Term '{termen}' found {len(users)} results.")

        except sqlite3.Error as e:
            app.logger.error(f"SQL ERROR: {e} | Term: {termen} | IP: {request.remote_addr}")
            users = [] # Returnam lista goala in caz de eroare
        finally:
            conn.close()

    return render_template('cauta.html', users=users, termen_cautat=termen)


#logica de logging
@app.before_request
def log_request_info():
    #  Setam timpul de start pentru a masura durata executiei
    g.start_time = time.time()
    
    # Identificam utilizatorul (Anonim sau Logat)
    current_user = session.get('username', 'ANONIM')
    
    #  Preluam datele
    params = dict(request.args)
    body_data = clean_sensitive_data(request.form)
    
    #  Detalii despre client (Browser, OS, Tool-uri de atac)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    #  Cookie-uri (Utile pentru a vedea tentative de Session Hijacking)
    # Logam doar ID-ul sesiunii
    cookie_header = request.headers.get('Cookie', 'No Cookie')

    # Scriem in log mesajul de "INCOMING REQUEST"
    app.logger.info(
        f"\n--------------------------------------------------\n"
        f" [REQUEST] {request.method} {request.path}\n"
        f" IP: {request.remote_addr} | User: {current_user}\n"
        f" User-Agent: {user_agent}\n"
        f" Cookies: {cookie_header}\n"
        f" GET Params: {params}\n"
        f" POST Data: {body_data}\n"
        f"--------------------------------------------------"
    )

@app.after_request
def log_response_info(response):
    # Calculam cat a durat executia pt atacuri de genul ->Time-Based Attacks Detection
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
    else:
        duration = 0
        
    status_code = response.status_code
    
    # Logam daca cererea a durat suspect de mult (> 2 secunde)
    # Acest lucru indica adesea un atac SQL Injection bazat pe timp (SLEEP/WAITFOR)
    if duration > 2.0:
        app.logger.warning(f"!!! SLOW REQUEST DETECTED (Time-Based SQLi?) - Duration: {duration:.2f}s !!!")

    # Logam raspunsul final
    app.logger.info(
        f" [RESPONSE] Status: {status_code} | Duration: {duration:.4f}s\n"
    )
    
    return response


@app.after_request
def sterge_fantoma(response):
    response.set_cookie('mesajEroare', value='', expires=0, secure=True, httponly=True)
    return response

# Capturam erorile 404 (Scanning) si 500 (Server Crash / Fuzzing)
@app.errorhandler(404)
def page_not_found(e):
    app.logger.warning(f" [SCANNING ATTEMPT?] 404 Not Found: {request.path} - IP: {request.remote_addr}")
    return "Pagina nu a fost gasita", 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f" [SERVER CRASH/ERROR] 500 Error la: {request.path} - Eroare: {e}")
    return "Eroare interna a serverului", 500


@app.route('/acasa')
def home():
    conn = get_conn()
    cur = conn.cursor()
    # Selectam doar campurile publice
    cur.execute("SELECT username, nume, prenume, caleImagineProfil FROM users")
    users = cur.fetchall()
    conn.close()
    return render_template('home.html', users=users)


@app.route('/')
def root():
    return redirect(url_for('home'))


"""
@app.route('/api/data', methods=['GET', 'POST'])
def apiData():
    app.logger.debug("Nivel DEBUG - mesaj tehnic pentru debugging.")
    app.logger.info("Nivel INFO - cerere procesata cu succes.")
    app.logger.warning("Nivel WARNING - ceva neobisnuit s-a intamplat.")
    app.logger.error("Nivel ERROR - a aparut o eroare, dar aplicatia continua.")
    app.logger.critical("Nivel CRITICAL - eroare severa, posibil crash.")
    
    return "Mesajele au fost logate in app.log !!! ( Hello world )"
"""


@app.route('/autentificare')
def login_form():
    return render_template('login.html')


@app.route('/verificare', methods=['POST'])
def verificare():
    # Colectare date
    username = request.form.get('username')
    password_input = request.form.get('password') 

    # Logam tentativa (doar username-ul)
    app.logger.info(f"LOGIN ATTEMPT: User '{username}' trying to login from IP {request.remote_addr}")

    conn = get_conn()
    conn.row_factory = sqlite3.Row 
    cur = conn.cursor()

    # Cautam utilizatorul in baza de date
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()

    # Verificarea Securizata
    if user:
        # Verificam daca parola introdusa se potriveste cu hash-ul din DB
        if check_password_hash(user['password'], password_input):
            # Login cu succes
            session['username'] = username
            app.logger.info(f"LOGIN SUCCESS: User '{username}' logged in.")
            
            #  Mesaj de succes
            flash("Te-ai autentificat cu succes!", "success") 
            return redirect(url_for('home'))
        else:
            # Parola gresita
            app.logger.warning(f"LOGIN FAILED: Incorrect password for user '{username}'")
            flash("Parola este incorecta!", "danger") 
            return redirect(url_for('login_form'))
    else:
        # Nu exista userul
        app.logger.warning(f"LOGIN FAILED: Username '{username}' not found.")
        flash("Utilizatorul nu exista!", "danger") 
        return redirect(url_for('login_form'))

@app.route('/contul_meu')
def contul_meu():
    if 'username' not in session:
        return redirect(url_for('login_form'))
    
    username = session['username']
    
    #  Luam datele din DB 
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()

    if not user:
         session.pop('username', None)
         return redirect(url_for('login_form'))

    return render_template('contul_meu.html', username=user['username'], user=user)

@app.route('/logout')
def logout():
    user = session.get('username', 'Guest')
    app.logger.info(f"LOGOUT: User '{user}' logged out.")
    session.clear() # Stergem toata sesiunea
    return redirect(url_for('home'))


from requests.exceptions import RequestException

@app.route('/sso')
def sso():
    if 'username' in session:
        return redirect(url_for("home"))
    return redirect(url_for("oidc_auth.login", next=url_for("private_area", _external=True)))

@app.route("/private")
@oidc.require_login
def private_area():
    info = oidc.user_getinfo(['preferred_username', 'email', 'sub'])
    username = info.get('preferred_username')
    email = info.get('email')
    user_id = info.get('sub')

    session['username'] = username

    greeting = f"Hello {username}"
    access_token = None
    
    # Incercam sa luam token-ul
    if user_id in oidc.credentials_store:
        try:
            from oauth2client.client import OAuth2Credentials
            access_token = OAuth2Credentials.from_json(oidc.credentials_store[user_id]).access_token
        except:
            pass

    return render_template("private.html", username=username, email=email, user_id=user_id, greeting=greeting, access_token=access_token)


@app.route('/pagina_schimbare_parola')
def pagina_schimbare_parola():
    if 'username' not in session:
        return redirect(url_for('login_form'))
    return render_template('schimba_parola.html')

@app.route('/procesare_schimbare_parola', methods=['POST'])
def procesare_schimbare_parola():
    if 'username' not in session:
        return redirect(url_for('login_form'))

    username = session['username']
    parola_veche_input = request.form.get('parola_veche')
    parola_noua = request.form.get('parola_noua')
    confirm_parola = request.form.get('confirm_parola')

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()

    #  Verificam parola veche folosind HASH
    if not user or not check_password_hash(user['password'], parola_veche_input):
        app.logger.warning(f"PASS CHANGE FAIL: Old pass wrong for '{username}'")
        flash("Parola veche este incorecta!")
        conn.close()
        return redirect(url_for('pagina_schimbare_parola'))

    if parola_noua != confirm_parola:
        flash("Parolele noi nu coincid!")
        conn.close()
        return redirect(url_for('pagina_schimbare_parola'))
    
    if len(parola_noua) < 6: #  Validare lungime minima
        flash("Parola noua trebuie sa aiba minim 6 caractere.")
        conn.close()
        return redirect(url_for('pagina_schimbare_parola'))

    try:
        #  Hashuim NOUA parola inainte de update
        new_hash = generate_password_hash(parola_noua)
        
        cur.execute("UPDATE users SET password = ? WHERE username = ?", (new_hash, username))
        conn.commit()
        
        app.logger.info(f"PASS CHANGE SUCCESS: User '{username}' updated password.")
        session.clear() 
        
        flash("Parola a fost schimbata! Te rugam sa te loghezi cu noua parola.")
        return redirect(url_for('login_form'))

    except Exception as e:
        app.logger.error(f"PASS CHANGE ERROR: {e}")
        flash("Eroare tehnica.")
        return redirect(url_for('pagina_schimbare_parola'))
    finally:
        conn.close()

@app.after_request
def add_cache_headers(response):
    if request.path.startswith('/inregistrare') or request.path.startswith('/cauta') \
       or request.path.startswith('/verificare') or request.path.startswith('/logout') \
        or request.path.startswith('/sso') or request.path.startswith('/private') \
            or request.path.startswith('/procesare_schimbare_parola')or request.path.startswith('/inregistrare'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.after_request
def set_hsts_header(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

@app.after_request
def remove_server_header(response):
    response.headers['Server'] = 'None'
    return response

@app.after_request
def set_csp(response):
    response.headers['Content-Security-Policy'] = (
        "script-src 'self'; "
    )
    return response

# dezactivare functii neesentiale
@app.after_request
def set_permissions_policy(response):
    response.headers['Permissions-Policy'] = (
        "accelerometer=(), ambient-light-sensor=(), autoplay=(), battery=(), camera=(), "
        "display-capture=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), "
        "payment=(), usb=(), vr=()"
    )
    return response

@app.after_request
def set_security_headers(response):
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    return response

@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500

@app.before_request
def block_options():
    if request.method == 'OPTIONS':
        return '', 405
    
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)


csrf = CSRFProtect(app)

if __name__ == '__main__':
    ssl_context = ('cert.pem', 'key.pem')
    app.run(host='0.0.0.0', port=5093,ssl_context=ssl_context, debug=False)