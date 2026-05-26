import sqlite3
import os
from config import DB_PATH

# la username am adaugat 500 in loc de 50 (pentru lab7)
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL CHECK(length(username) BETWEEN 4 AND 500),
            email TEXT UNIQUE NOT NULL CHECK(length(email) BETWEEN 6 AND 254) CHECK(email LIKE '%@%.%'),
            password TEXT NOT NULL CHECK(length(password) >= 1),
            nume TEXT NOT NULL CHECK(length(nume) BETWEEN 2 AND 50),
            prenume TEXT NOT NULL CHECK(length(prenume) BETWEEN 2 AND 50),
            numeAfisat TEXT NOT NULL CHECK(length(numeAfisat) BETWEEN 1 AND 100),
            urlSite TEXT NOT NULL CHECK(length(urlSite) BETWEEN 10 AND 266) CHECK(urlSite LIKE 'http%' OR urlSite LIKE 'ftp%'),
            caleImagineProfil TEXT CHECK(length(caleImagineProfil) <= 104),
            tip TEXT NOT NULL DEFAULT 'user' CHECK(tip IN ('user', 'admin', 'moderator')),
            timpInregistrare DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP

        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
