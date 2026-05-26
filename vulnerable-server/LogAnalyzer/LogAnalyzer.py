#!/usr/bin/env python3
import os
import re
import time
import csv
import json
from collections import defaultdict, Counter
from datetime import datetime, timedelta

# ────────────────────────────────
# 1. Setari de baza
# ────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # urca un nivel peste LogAnalyzer/

PRESET_PATHS = {
    "app": os.path.join(BASE_DIR, "server", "logs", "app.log"),
    "sqlmap": os.path.join(BASE_DIR, "LogAnalyzer", "logs_apache_php", "sql-map-teste.cs-log"),
    "wp_victim": os.path.join(BASE_DIR, "LogAnalyzer", "logs_apache_php", "wp-victim-access.log"),
    "wp_victim_20220417": os.path.join(BASE_DIR, "LogAnalyzer", "logs_apache_php", "wp-victim-access.log-20220417"),
    "wp_victim_20220424": os.path.join(BASE_DIR, "LogAnalyzer", "logs_apache_php", "wp-victim-access.log-20220424"),
    "apache_access_20221002": os.path.join(BASE_DIR, "LogAnalyzer", "logs_apache_php_app_admitere", "access-20221002"),
    "apache_access_20221007": os.path.join(BASE_DIR, "LogAnalyzer", "logs_apache_php_app_admitere", "access-20221007"),
    "apache_access_20221011": os.path.join(BASE_DIR, "LogAnalyzer", "logs_apache_php_app_admitere", "access-20221011"),
    "gcloud_csv": os.path.join(BASE_DIR, "LogAnalyzer", "logs_google_cloud_csv", "downloaded-logs-20221003-110537.csv"),
    "gcloud_json": os.path.join(BASE_DIR, "LogAnalyzer", "logs_google_cloud_json", "downloaded-logs-20221003-110509.json"),
}


# ────────────────────────────────
# 2. Detectare automata format log
# ────────────────────────────────
def detect_format(line):
    if "IP=" in line and "STATUS=" in line:
        return "flask"
    elif re.search(r'\d+\.\d+\.\d+\.\d+ - - \[.*\] ".*HTTP', line):
        return "apache"
    elif "sqlmap" in line.lower():
        return "sqlmap"
    elif line.strip().startswith("{") or line.strip().startswith("["):
        return "json"
    elif "," in line and "timestamp" in line.lower():
        return "csv"
    else:
        return "unknown"


# ────────────────────────────────
# 3. Functii de parsare
# ────────────────────────────────
def parse_line(line, log_type):
    if log_type == "flask":
        m = re.search(r"IP=(\S+).*PATH=([^\s]+).*STATUS=(\d{3})", line)
        if m:
            return m.groups()
    elif log_type in ("apache", "wp_victim", "sqlmap"):
        m = re.search(r'(\d+\.\d+\.\d+\.\d+).*"(?:GET|POST)\s+([^ ]+)\s+HTTP.*"\s+(\d{3})', line)
        if m:
            return m.groups()
    return None


# ────────────────────────────────
# 4. Analize principale
# ────────────────────────────────
def show_4xx(log_path):
    """Afiseaza cererile cu coduri 4xx"""
    if not os.path.exists(log_path):
        print(f"Eroare: fisierul {log_path} nu exista.")
        return

    print(f"\nAnaliza fisier: {log_path}")
    print(f"{'Cod':<5} | {'IP':<15} | {'URL'}")
    print("-" * 80)

    ext = os.path.splitext(log_path)[1].lower()

    if ext == ".csv":
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = str(row.get("status", ""))
                if code.startswith("4"):
                    ip = row.get("remoteIp", "-")
                    url = row.get("resource", "-")
                    print(f"{code:<5} | {ip:<15} | {url}")
        return

    if ext == ".json":
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
            for entry in data:
                code = str(entry.get("status", ""))
                if code.startswith("4"):
                    ip = entry.get("ip", "-")
                    url = entry.get("url", "-")
                    print(f"{code:<5} | {ip:<15} | {url}")
        return

    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        first = f.readline()
        log_type = detect_format(first)
        f.seek(0)
        for line in f:
            parsed = parse_line(line, log_type)
            if parsed:
                ip, path, code = parsed
                if code.startswith("4"):
                    print(f"{code:<5} | {ip:<15} | {path}")


def show_unique_urls(log_path):
    """Afiseaza URL-uri unice, numar accesari si coduri raspuns"""
    if not os.path.exists(log_path):
        print(f"Eroare: fisierul {log_path} nu exista.")
        return

    stats = defaultdict(lambda: {"count": 0, "codes": set()})
    ext = os.path.splitext(log_path)[1].lower()

    if ext == ".csv":
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get("resource", "-")
                code = str(row.get("status", "-"))
                stats[url]["count"] += 1
                stats[url]["codes"].add(code)
    elif ext == ".json":
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
            for row in data:
                url = row.get("url", "-")
                code = str(row.get("status", "-"))
                stats[url]["count"] += 1
                stats[url]["codes"].add(code)
    else:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            first = f.readline()
            log_type = detect_format(first)
            f.seek(0)
            for line in f:
                parsed = parse_line(line, log_type)
                if parsed:
                    ip, path, code = parsed
                    stats[path]["count"] += 1
                    stats[path]["codes"].add(code)

    print(f"\nAnaliza fisier: {log_path}")
    print(f"{'URL':45} | {'Accesari':10} | {'Coduri'}")
    print("-" * 75)
    for path, data in sorted(stats.items()):
        print(f"{path:45} | {data['count']:^10} | {', '.join(sorted(data['codes']))}")


def tail_4xx(log_path):
    """Monitorizeaza in timp real logurile pentru erori 4xx"""
    if not os.path.exists(log_path):
        print(f"Eroare: fisierul {log_path} nu exista.")
        return

    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        first = f.readline()
        log_type = detect_format(first)
        f.seek(0, 2)
        print(f"\nUrmareste log ({log_type}) in timp real. Apasa Ctrl+C pentru a opri.\n")

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            parsed = parse_line(line, log_type)
            if parsed:
                ip, path, code = parsed
                if code.startswith("4"):
                    print(f"[{time.strftime('%H:%M:%S')}] {code} | {ip} | {path}")


# ────────────────────────────────
#  Interfata interactiva
# ────────────────────────────────
def main():
    print("\n=== ANALIZA LOGURILOR SERVERULUI ===")
    print("1. Afiseaza cererile cu coduri 4xx")
    print("2. Afiseaza URL-urile unice accesate si codurile de raspuns")
    print("3. Urmareste in timp real erorile 4xx")
    print("0. Iesire\n")

    opt = input("Alege o optiune (0-3): ").strip()
    if opt == "0":
        return

    print("\nAlege fisierul de log:")
    for i, (key, val) in enumerate(PRESET_PATHS.items(), 1):
        print(f"{i}. {key} -> {val}")
    log_choice = input("Selecteaza logul (numar): ").strip()

    keys = list(PRESET_PATHS.keys())
    if not log_choice.isdigit() or int(log_choice) < 1 or int(log_choice) > len(keys):
        print("Selectie invalida.")
        return

    log_path = PRESET_PATHS[keys[int(log_choice) - 1]]

    if opt == "1":
        show_4xx(log_path)
    elif opt == "2":
        show_unique_urls(log_path)
    elif opt == "3":
        tail_4xx(log_path)
    else:
        print("Optiune invalida.")


if __name__ == "__main__":
    main()
