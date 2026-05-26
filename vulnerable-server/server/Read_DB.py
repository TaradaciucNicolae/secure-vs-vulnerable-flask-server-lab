import sqlite3
from config import DB_PATH

# Conexiune la baza de date
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row  # ca sa accesam coloanele ca dict

cursor = conn.cursor()

# Citim toate inregistrarile din tabela utilizatori
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

# Afisam rezultatele

print("Lista users:")
for row in rows:
    print(f"ID: {row['id']}")
    print(f"Username: {row['username']}")
    print(f"Email: {row['email']}")
    print(f"Password: {row['password']}")
    print(f"Nume: {row['nume']}")
    print(f"Prenume: {row['prenume']}")
    print(f"Nume afisat: {row['numeAfisat']}")
    print(f"URL site: {row['urlSite']}")
    print(f"Cale imagine profil: {row['caleImagineProfil']}")
    print(f"Tip user: {row['tip']}")
    print(f"Inregistrat la: {row['timpInregistrare']}")
    print("-" * 100)

# inchidem conexiunea
conn.close()
