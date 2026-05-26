import sqlite3
import os
from config import DB_PATH

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # [VULNERABILITATE] Weak Data Integrity
    # Am eliminat toate constrangerile
    # Acum se pot salva scriptri in campurile de nume/site/etc 
    # Se pot introduce email-uri invalide sau date fara sens.
    # Am scos si CHECK(tip IN ('user', 'admin')) -> Acum oricine poate deveni 'super-admin' prin SQL Injection
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL, 
            nume TEXT,
            prenume TEXT,
            numeAfisat TEXT,
            urlSite TEXT,
            caleImagineProfil TEXT,
            tip TEXT NOT NULL DEFAULT 'user',
            timpInregistrare DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP

        )
    ''')

    # [VULNERABILITATE] Default Credentials
    # Inseram un admin "ascuns" cu parola in clar. Oricine stie de el se poate loga.
    try:
        conn.execute('''
            INSERT INTO users (username, email, password, nume, prenume, numeAfisat, urlSite, caleImagineProfil)
            VALUES ('admin', 'admin@test.com', 'admin123', 'System', 'Admin', 'SuperUser', 'http://localhost', NULL)
        ''')
    except sqlite3.IntegrityError:
        pass # Utilizatorul exista deja

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
