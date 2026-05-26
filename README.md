# Secure vs Vulnerable Flask Server Lab

A practical web-security lab that compares two versions of the same Flask application:

- an intentionally vulnerable server used to demonstrate common web application weaknesses;
- a hardened server that applies defensive coding practices and security controls.

The project is designed for educational use, cybersecurity training, secure development practice, and Blue Team analysis. It shows how insecure implementation choices can affect a web application, and how the same features can be improved through validation, sanitization, secure session handling, logging, and HTTP security controls.

---

## Overview

This repository contains two related Flask server implementations built around the same application idea. The vulnerable version exposes security issues on purpose, while the secure version demonstrates how those issues can be mitigated.

The project focuses on realistic web security topics such as:

- SQL injection prevention;
- cross-site scripting mitigation;
- CSRF protection;
- password hashing;
- secure cookie configuration;
- safe file upload handling;
- HTTPS configuration for local testing;
- security headers;
- sensitive-data filtering in logs;
- custom error handling;
- cache-control for sensitive pages;
- attack detection through application logs.

This makes the repository useful both from a Software Engineering perspective and from a Cybersecurity / Blue Team perspective.

---

## Repository Structure

```text
.
├── vulnerable-server/      # Intentionally insecure Flask implementation
├── secure-server/          # Hardened Flask implementation
└── README.md
```

---

## Vulnerable Server

The vulnerable server is intentionally built with insecure patterns so they can be studied, tested, and compared against the secure implementation.

It demonstrates issues such as:

- unsafe SQL query construction;
- weak or missing input validation;
- unsafe template rendering patterns;
- insecure password handling;
- weak session configuration;
- missing or incomplete security headers;
- insufficient CSRF protection;
- unsafe file-upload behavior;
- information leakage through logs or error messages.

This version should only be used in a local, isolated environment.

---

## Secure Server

The secure server applies defensive improvements to the same application flow.

The hardened version includes:

- parameterized SQL queries;
- password hashing and verification;
- safer template rendering and output escaping;
- CSRF token protection for forms;
- stricter file upload validation;
- secure cookie settings;
- HTTPS support for local testing;
- security headers such as `X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`, and HSTS-related configuration;
- reduced information disclosure in errors;
- sensitive field redaction in logs;
- improved cache-control for sensitive pages.

The goal is to show how vulnerable code can be transformed into a more secure implementation without changing the core application purpose.

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
- general reconnaissance and crawling.

This makes the project useful for understanding not only how vulnerabilities are introduced and fixed, but also how attacks appear from the monitoring and detection side.

---

## Security Testing Tools

The secure version was reviewed with a combination of manual checks and automated tools, including:

- Nmap;
- curl;
- sslscan;
- OWASP ZAP;
- Nikto.

These tools helped identify missing headers, cookie issues, TLS behavior, cache-control problems, and other web security findings that were then reviewed and addressed where applicable.

---

## Technologies Used

- Python
- Flask
- SQLite
- Jinja2 templates
- Flask-WTF / CSRF protection
- Werkzeug password hashing
- HTTPS with local/self-signed certificate support
- Docker / Docker Compose
- Nmap
- OWASP ZAP
- Nikto
- sslscan
- curl

---

## Educational Purpose

This repository is intended for:

- learning secure web development;
- comparing vulnerable and hardened implementations;
- understanding common web application vulnerabilities;
- practicing Blue Team log analysis;
- documenting remediation techniques;
- demonstrating security awareness in a portfolio project.

The vulnerable server is not intended for production use and should never be exposed to the public internet.

---

## Disclaimer

This project is for educational and defensive security purposes only.

The vulnerable server is intentionally insecure and must be used only in an isolated local lab environment. Do not deploy it publicly and do not use the techniques demonstrated here against systems that you do not own or have explicit permission to test.
