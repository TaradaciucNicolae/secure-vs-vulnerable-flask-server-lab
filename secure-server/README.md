# Secure Flask Server

Hardened version of the Flask application from the Secure vs Vulnerable Flask Server Lab.

This server applies defensive coding practices and security controls to the same application flow used in the vulnerable version.

---

## What It Includes

- Parameterized SQL queries
- Password hashing and verification
- CSRF protection for forms
- Safer template rendering and output escaping
- Secure cookie configuration
- Input validation and upload restrictions
- HTTPS support for local testing
- HTTP security headers
- Sensitive-data redaction in logs
- Custom error handling
- Cache-control for sensitive pages

---

## Run with Docker

From this folder:

```bash
docker compose up --build -d
```

Open:

```text
https://localhost:5093
```

Because this version uses a local/self-signed certificate, the browser may show a certificate warning.

Stop the container:

```bash
docker compose down
```

View live logs:

```bash
docker logs -f SW_Server_Secure
```

---

## Purpose

This server is used to demonstrate how common web vulnerabilities can be mitigated through secure implementation choices.

It is intended for secure development practice, cybersecurity training, and Blue Team analysis.

---

## Technologies

- Python
- Flask
- SQLite
- Jinja2
- Flask-WTF
- Werkzeug security utilities
- Docker
- Docker Compose

---

## Note

This project is educational and defensive. It is not a production-ready application without additional deployment hardening, production certificates, secret management, and infrastructure review.
