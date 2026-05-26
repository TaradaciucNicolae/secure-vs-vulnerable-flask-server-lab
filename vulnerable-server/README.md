# Vulnerable Flask Server

Intentionally insecure version of the Flask application from the Secure vs Vulnerable Flask Server Lab.

This server contains deliberately introduced weaknesses so they can be tested, analyzed, and compared with the hardened implementation.

---

## Demonstrated Vulnerabilities

- SQL injection
- Cross-site scripting
- Weak input validation
- Unsafe template rendering
- Insecure password handling
- Unsafe file upload behavior
- Missing or weak CSRF protection
- Weak session and cookie configuration
- Missing security headers
- Information leakage through logs or errors

---

## Run with Docker

From this folder:

```bash
docker compose up --build -d
```

Open:

```text
http://localhost:5092
```

Stop the container:

```bash
docker compose down
```

View live logs:

```bash
docker logs -f SW_Server_With_Vulnerabilities
```

---

## Purpose

This server is designed for local cybersecurity training and comparison with the secure version.

It helps demonstrate how insecure code behaves, how attacks appear in logs, and how the same application can be improved in the hardened server.

---

## Technologies

- Python
- Flask
- SQLite
- Jinja2
- HTML / CSS / JavaScript
- Docker
- Docker Compose

---

## Warning

This server is intentionally vulnerable.

Run it only in a local, isolated lab environment. Do not deploy it publicly and do not use the techniques demonstrated here against systems that you do not own or do not have explicit permission to test.
