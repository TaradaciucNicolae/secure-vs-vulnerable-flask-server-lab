# Secure vs Vulnerable Flask Server Lab

A practical web-security lab that compares two versions of the same Flask application:

- **`vulnerable-server/`** — an intentionally vulnerable implementation used to demonstrate common web application weaknesses.
- **`secure-server/`** — a hardened implementation that applies defensive coding practices and security controls.

The project is designed for educational use, cybersecurity training, secure development practice, and Blue Team analysis. It shows how insecure implementation choices affect a web application and how the same features can be improved through validation, sanitization, secure session handling, logging, and HTTP security controls.

> **Educational use only.** Run locally in an isolated environment. Do not expose the vulnerable server to the public internet.

> Each server has its own Docker setup, so the two versions can be started separately from their own folders.

---

## What This Project Demonstrates

| Area | Vulnerable Server | Secure Server |
|---|---|---|
| SQL queries | Injection-prone query construction | Parameterized queries |
| Password handling | Insecure password behavior for demonstration | Password hashing and safer verification |
| XSS protection | Unsafe rendering patterns | Escaping and safer template rendering |
| CSRF | Missing or weak protection | CSRF token protection |
| File upload | Weak filename / extension handling | Safer filename and extension validation |
| Cookies | Weak session/cookie configuration | Secure cookie settings |
| HTTP security | Missing or incomplete security headers | Security headers and safer browser policies |
| Error handling | More information exposure | Custom error handling |
| Logging | Sensitive data may appear in logs | Sensitive-data redaction |
| Cache control | Sensitive pages may be cached | Cache-control on sensitive pages |

---

## Vulnerable Server

The vulnerable server intentionally contains insecure implementation patterns so they can be studied, tested, and compared with the secure version.

It demonstrates issues such as:

- SQL injection;
- cross-site scripting;
- weak input validation;
- unsafe template rendering;
- insecure password handling;
- unsafe file upload behavior;
- missing or weak CSRF protection;
- weak session and cookie configuration;
- missing security headers;
- information leakage through logs or error messages.

Run it only in a local lab environment.

```bash
cd vulnerable-server
docker compose up --build -d
```

Open:

```text
http://localhost:5092
```

Stop it with:

```bash
docker compose down
```

---

## Secure Server

The secure server applies defensive improvements to the same application flow. It shows how vulnerable code can be hardened without changing the core idea of the application.

The hardened version includes:

- parameterized SQL queries;
- password hashing and verification;
- safer template rendering and output escaping;
- CSRF token protection;
- stricter file upload validation;
- secure cookie configuration;
- HTTPS support for local testing;
- HTTP security headers;
- reduced information disclosure in errors;
- sensitive field redaction in logs;
- cache-control for sensitive pages.

Run it locally with:

```bash
cd secure-server
docker compose up --build -d
```

Open:

```text
https://localhost:5093
```

Because the secure server uses a local/self-signed certificate, the browser may show a certificate warning during local testing.

Stop it with:

```bash
docker compose down
```

---

## Blue Team and Log Analysis

The project also includes a defensive analysis angle. Application logs were used to identify and classify suspicious activity against the vulnerable and secured versions of the server.

Examples of analyzed activity include:

- SQL injection attempts;
- XSS attempts;
- directory and file enumeration;
- login and credential-guessing attempts;
- session manipulation attempts;
- malformed requests and protocol fuzzing;
- reconnaissance and crawling.

This makes the project useful for understanding not only how vulnerabilities are introduced and fixed, but also how attacks appear from the monitoring and detection side.

---

## Security Testing Tools

The project was reviewed with a combination of manual checks and automated tools, including:

- Nmap;
- curl;
- sslscan;
- OWASP ZAP;
- Nikto.

These tools helped identify missing headers, cookie issues, TLS behavior, cache-control problems, and other web security findings.

---

## Technologies Used

- Python
- Flask
- SQLite
- Jinja2 templates
- Flask-WTF / CSRF protection
- Werkzeug password hashing
- Docker
- Docker Compose
- Nmap
- OWASP ZAP
- Nikto
- sslscan
- curl

---

## Recommended Learning Flow

1. Start with the vulnerable server.
2. Review the exposed weaknesses and test them locally.
3. Compare the same application flow in the secure server.
4. Review the security controls added in the hardened version.
5. Analyze logs to understand how suspicious behavior appears in practice.
6. Use the project as a reference for secure coding and defensive monitoring.

---

## Disclaimer

This repository is for educational and defensive security purposes only.

The vulnerable server is intentionally insecure and must only be used in an isolated local lab environment. Do not deploy it publicly and do not use the techniques demonstrated here against systems that you do not own or do not have explicit permission to test.
