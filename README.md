# Secure vs Vulnerable Flask Server Lab

Educational web-security lab that compares two versions of the same Flask application:

- **`vulnerable-server/`** — intentionally weakened version used to demonstrate common web vulnerabilities.
- **`secure-server/`** — hardened version with defensive controls and safer implementation patterns.

The goal is to make the security differences easy to inspect side by side: authentication, password storage, SQL query handling, upload validation, XSS protection, CSRF protection, HTTPS, security headers, logging, and attack visibility.

> Educational use only. Run locally in an isolated environment. Do not expose the vulnerable server to the public internet.

---

## Repository Structure

```text
.
├── vulnerable-server/      # Intentionally vulnerable Flask server
├── secure-server/          # Hardened Flask server
├── docker-compose.yml      # Runs both versions from the repository root
├── SECURITY.md
└── README.md
```

Runtime data such as logs, uploaded files, local databases, `.env` files, certificates, private keys, and original client secrets are intentionally excluded from this public version.

---

## What This Project Demonstrates

| Area | Vulnerable Server | Secure Server |
|---|---|---|
| Password handling | Plaintext-style behavior for demonstration | Password hashing and safer verification |
| SQL queries | Injection-prone query construction | Parameterized queries |
| File upload | Weak filename / extension handling | Filename sanitization and restricted extensions |
| XSS | Unsafe rendering patterns | Escaping and safer template rendering |
| CSRF | Missing or incomplete protection | Anti-CSRF tokens |
| Cookies | Weaker cookie settings | Secure / HttpOnly / SameSite-oriented settings |
| Transport | HTTP / weaker demo configuration | HTTPS local demo configuration |
| Headers | Missing or weakened headers | Security headers added |
| Logging | Sensitive data exposure for demonstration | Sensitive values masked |

---

## Run Both Servers

From the repository root:

```bash
docker compose up --build
```

Open the applications:

```text
Vulnerable server: http://localhost:5092
Secure server:     https://localhost:5093
```

The secure server uses a local development HTTPS context. Your browser may show a certificate warning because this is not a production certificate.

Stop the containers:

```bash
docker compose down
```

---

## Run Only One Version

```bash
docker compose up --build vulnerable-server
```

```bash
docker compose up --build secure-server
```

---

## Main Security Topics Covered

- SQL Injection prevention with parameterized queries.
- XSS prevention through escaping and safer template rendering.
- CSRF protection for state-changing forms.
- Password hashing instead of storing passwords in plaintext.
- Safer file upload validation.
- Security-focused response headers.
- Safer cookie configuration.
- HTTPS configuration for local testing.
- Logging improvements and sensitive-data masking.
- Comparison between attack-prone and hardened implementations.

---

## Notes About the Public Version

This public repository is cleaned for sharing. It does **not** include:

- private `.env` files;
- real databases;
- uploaded user files;
- runtime logs;
- private keys or certificates;
- original OIDC client secrets;
- generated cache files;
- Python bytecode.

A placeholder `server/client_secrets.json` is included only so the app structure remains understandable. Replace it with local test values if you need OIDC functionality.

---
