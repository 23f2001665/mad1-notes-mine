
#  Web Application Security

## SQL Injection
SQL Injection is a code injection attack where malicious input is used to manipulate database queries.

<SQLinjection />

## Prevention Techniques

#### 1. ORM (Object Relational Mapping)
- SQLAlchemy automatically handles query sanitization
- Use well-maintained frameworks and system updates (OS, server software latest stable version with security updates and patches)

#### 2. Input Validation
- Always validate on **server-side** (not just HTML/JS)
- Reject malformed or suspicious inputs: check for empty values, length limits and 

#### 3. Principle of Least Privilege
- DB user should have minimal permissions


## HTTPS (Secure Communication)

HTTPS secures communication between:

```text
Client ⇄ Server
```
using **TLS (Transport Layer Security)**.


### How HTTPS Works

1. Server provides a **digital certificate**
2. Certificate is verified by a trusted authority
3. A secure encrypted channel is established
4. All data is transmitted securely


:::details Other Vulnerabilities (You will learn in [9-Security.md](..week9/9-Security.md))
- **Buffer Overflow**: Memory overwrite due to excess input → crash or exploit
- **Input Overflow**: input exceeds expected size → unexpected behavior
- **XSS (Cross-Site Scripting)**: inject malicious scripts into web pages
- Encrypt sensitive data like passwords (hashing + salt)
- Use **CSRF tokens** to prevent unauthorized requests i.e. Fake requests executed on behalf of user
:::