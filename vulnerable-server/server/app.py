from flask import Flask, request, g, render_template, redirect, url_for, flash, session, make_response
import sqlite3
import os
# [VULNERABILITATE] Am scos secure_filename pentru a permite Path Traversal sau nume periculoase
# from werkzeug.utils import secure_filename 
# [VULNERABILITATE] Am scos hash-urile. Nu mai folosim generate_password_hash
# from werkzeug.security import generate_password_hash, check_password_hash 
from config import DB_PATH, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, SECRET_KEY
from init_db import init_db
import time
from datetime import datetime, timezone
import logging
from logging.config import dictConfig
import json
from flask_oidc import OpenIDConnect
import requests

# [VULNERABILITATE] Functia nu mai curata datele. Parolele vor aparea in loguri.
def clean_sensitive_data(form_data):
    if not form_data:
        return {}
    # Returnam datele exact asa cum sunt, inclusiv parolele
    return dict(form_data)


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


# [VULNERABILITATE] Setari nesecurizate pentru Cookie-uri
app.config['SESSION_COOKIE_HTTPONLY'] = False # JavaScript POATE fura cookie-ul (Pericol XSS)
app.config['SESSION_COOKIE_SAMESITE'] = None  # Permite CSRF

app.config.update({
    'OIDC_CLIENT_SECRETS': os.path.join(os.path.dirname(__file__), 'client_secrets.json'),
    'OIDC_ID_TOKEN_COOKIE_SECURE': False, 
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': 'master',
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
})

oidc = OpenIDConnect(app, prefix="/oidc")

# [VULNERABILITATE] Am scos functia add_security_headers complet.
# Acum site-ul este vulnerabil la Clickjacking (iframe), MIME sniffing, si nu are CSP.

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# [VULNERABILITATE] Functia accepta orice fisier acum, nu mai verifica extensia
def allowed_file(filename):
    return True 

@app.route('/inregistrare', methods=['GET', 'POST'])
def inregistrare():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        
        # [VULNERABILITATE] Preluam parola si NU ii facem hash. O salvam text-clar.
        password_plain = request.form.get('parola', '').strip()
        # password_hash = generate_password_hash(password_plain) <- SCOS
        
        nume = request.form.get('nume', '').strip()
        prenume = request.form.get('prenume', '').strip()
        nume_afisat = request.form.get('nume_afisat', '').strip()
        url_site = request.form.get('url_site', '').strip()

        app.logger.info(f"REGISTER ATTEMPT: User '{username}' starts registration from IP {request.remote_addr}")

        # Upload imagine
        imagine = request.files.get('imagine_profil')
        cale_imagine = None

        if imagine and imagine.filename != '':
            # [VULNERABILITATE] Nu mai verificam extensia (allowed_file e mereu True)
            if allowed_file(imagine.filename):
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                # [VULNERABILITATE] Nu mai folosim secure_filename.
                # Un atacator poate numi fisierul "../../../etc/passwd" sau "script.php"
                filename = f"Avatar_{username}_{imagine.filename}" 
                
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                imagine.save(filepath)
                cale_imagine = os.path.relpath(filepath, start=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
                
                app.logger.info(f"UPLOAD SUCCESS: User '{username}' uploaded file '{imagine.filename}'")
            else:
                flash('Format imagine invalid!')
                return redirect(url_for('inregistrare'))
        
        # Salvam in DB
        conn = get_conn()
        try:
            # [VULNERABILITATE] SQL Injection Posibil aici daca concatenam, dar momentan pastram ? pentru INSERT
            # Insa marea problema e salvarea password_plain in loc de hash
            conn.execute('''INSERT INTO users 
                            (username, email, password, nume, prenume, numeAfisat, urlSite, caleImagineProfil)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                         (username, email, password_plain, nume, prenume, nume_afisat, url_site, cale_imagine))
            conn.commit()
            
            app.logger.info(f"REGISTER SUCCESS: New user created: '{username}' | Email: {email}")
            
            flash('Inregistrare realizata cu succes! Te rugam sa te autentifici.')
            return redirect(url_for('login_form'))

        except sqlite3.IntegrityError as e:
            app.logger.warning(f"REGISTER FAILED: Duplicate username or email for '{username}'/'{email}'. Error: {e}")
            flash('Username sau email deja existent!')
        except Exception as e:
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
            # [VULNERABILITATE MAJORĂ] SQL INJECTION
            # Am scos parametrizarea (?). Folosim string formatting direct.
            # Daca userul introduce: ' OR '1'='1
            # Query-ul devine: ... WHERE username LIKE '%' OR '1'='1' ... (returneaza tot)
            
            query = f"SELECT username, nume, prenume, email, numeAfisat FROM users WHERE username LIKE '%{termen}%' OR nume LIKE '%{termen}%' OR prenume LIKE '%{termen}%' OR email LIKE '%{termen}%'"
            
            # Executam query-ul construit manual
            cur.execute(query)
            users = cur.fetchall()
            
            app.logger.info(f"SEARCH: Term '{termen}' found {len(users)} results.")

        except sqlite3.Error as e:
            app.logger.error(f"SQL ERROR: {e} | Term: {termen} | IP: {request.remote_addr}")
            users = [] 
        finally:
            conn.close()

    return render_template('cauta.html', users=users, termen_cautat=termen)
# [VULNERABILITATE] Am adaugat aceasta functie care simuleaza o functie admin pentru testarea retelei care poate fi folosita pentru 
# remote code execution de catre un atacator  de exemplu cu "http://localhost:5000/admin/ping?target=google.com%26dir"
@app.route('/admin/ping', methods=['GET'])
def ping_tool():
    target = request.args.get('target', 'google.com')
    
    # [VULNERABILITATE] Command Injection
    # Concatenam direct inputul utilizatorului
    command = "ping -n 1 " + target 
    
    try:
        stream = os.popen(command)
        output = stream.read()
    except Exception as e:
        output = str(e)
    
    return f"<pre>{output}</pre>"

#logica de logging
@app.before_request
def log_request_info():
    g.start_time = time.time()
    current_user = session.get('username', 'ANONIM')
    params = dict(request.args)
    
    # [VULNERABILITATE] Logam datele "murdare" (inclusiv parole in clar din POST request)
    body_data = clean_sensitive_data(request.form)
    
    user_agent = request.headers.get('User-Agent', 'Unknown')
    cookie_header = request.headers.get('Cookie', 'No Cookie')

    app.logger.info(
        f"\n--------------------------------------------------\n"
        f" [REQUEST] {request.method} {request.path}\n"
        f" IP: {request.remote_addr} | User: {current_user}\n"
        f" User-Agent: {user_agent}\n"
        f" Cookies: {cookie_header}\n"
        f" GET Params: {params}\n"
        f" POST Data (UNSAFE): {body_data}\n"
        f"--------------------------------------------------"
    )

@app.after_request
def log_response_info(response):
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
    else:
        duration = 0
        
    status_code = response.status_code
    
    # [NOTA] Pastram detectia de slow request ca e utila pentru debugging, nu e o masura de securitate activa ce blocheaza atacul
    if duration > 2.0:
        app.logger.warning(f"!!! SLOW REQUEST DETECTED - Duration: {duration:.2f}s !!!")

    app.logger.info(
        f" [RESPONSE] Status: {status_code} | Duration: {duration:.4f}s\n"
    )
    
    return response


@app.after_request
def sterge_fantoma(response):
    response.set_cookie('mesajEroare', '', expires=0)
    return response

# [VULNERABILITATE] Am scos error handlers custom. 
# Acum Flask va afisa eroarea standard, care in mod DEBUG poate expune cod sursa si variabile de mediu.
# @app.errorhandler(404) ...
# @app.errorhandler(500) ...


@app.route('/acasa')
def home():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT username, nume, prenume, caleImagineProfil FROM users")
    users = cur.fetchall()
    conn.close()
    return render_template('home.html', users=users)


@app.route('/')
def root():
    return redirect(url_for('home'))


@app.route('/api/data', methods=['GET', 'POST'])
def apiData():
    # Logs demo...
    return "Mesajele au fost logate in app.log"


@app.route('/autentificare')
def login_form():
    return render_template('login.html')


@app.route('/verificare', methods=['POST'])
def verificare():
    username = request.form.get('username')
    password_input = request.form.get('password') 

    app.logger.info(f"LOGIN ATTEMPT: User '{username}' trying to login.")

    conn = get_conn()
    conn.row_factory = sqlite3.Row 
    cur = conn.cursor()

    # [VULNERABILITATE] Si aici putem baga SQL Injection daca vrem, dar il lasam pe "cauta" principal.
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()

    if user:
        # [VULNERABILITATE] Verificare PAROLA IN CLAR
        # Comparam string-ul din baza de date direct cu ce a tastat utilizatorul
        if user['password'] == password_input:
            session['username'] = username
            app.logger.info(f"LOGIN SUCCESS: User '{username}' logged in.")
            flash("Te-ai autentificat cu succes!", "success") 
            return redirect(url_for('home'))
        else:
            app.logger.warning(f"LOGIN FAILED: Incorrect password for user '{username}'")
            flash("Parola este incorecta!", "danger") 
            return redirect(url_for('login_form'))
    else:
        app.logger.warning(f"LOGIN FAILED: Username '{username}' not found.")
        flash("Utilizatorul nu exista!", "danger") 
        return redirect(url_for('login_form'))

@app.route('/contul_meu')
def contul_meu():
    if 'username' not in session:
        return redirect(url_for('login_form'))
    
    username = session['username']
    
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
    session.clear() 
    return redirect(url_for('home'))


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

    # [VULNERABILITATE] Verificare parola veche in CLAR
    if not user or user['password'] != parola_veche_input:
        flash("Parola veche este incorecta!")
        conn.close()
        return redirect(url_for('pagina_schimbare_parola'))

    if parola_noua != confirm_parola:
        flash("Parolele noi nu coincid!")
        conn.close()
        return redirect(url_for('pagina_schimbare_parola'))
    
    # [VULNERABILITATE] Am scos validarea de lungime minima. Acceptam parole de 1 caracter.
    # if len(parola_noua) < 6: ...

    try:
        # [VULNERABILITATE] Update cu parola in CLAR
        # Nu mai facem hash
        cur.execute("UPDATE users SET password = ? WHERE username = ?", (parola_noua, username))
        conn.commit()
        
        session.clear() 
        flash("Parola a fost schimbata! Te rugam sa te loghezi cu noua parola.")
        return redirect(url_for('login_form'))

    except Exception as e:
        app.logger.error(f"PASS CHANGE ERROR: {e}")
        flash("Eroare tehnica.")
        return redirect(url_for('pagina_schimbare_parola'))
    finally:
        conn.close()

if __name__ == '__main__':
    # [VULNERABILITATE] Am scos SSL/HTTPS. Site-ul merge acum pe HTTP simplu (trafic interceptabil).
    # ssl_context = ('cert.pem', 'key.pem')
    
    # Ruleaza fara criptare
    app.run(host='0.0.0.0', port=5092, debug=True)