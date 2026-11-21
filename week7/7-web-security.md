# Web Application Security

A web application accepts text from strangers (forms, URLs, headers) and passes it to a database and to other users. If that text is trusted blindly, an attacker can use the application against itself. The possible outcomes of an attack are:

- **loss of data**: deletion
- **exposure of data**: sensitive information leaks
- **manipulation of data**: data is changed

This page covers the most important attack on database-backed applications (**SQL injection**), the basic defences, and **HTTPS**. The other attacks are introduced at the end and covered in [Week 9](../week9/9-week-index.md).

> [!NOTE]
> The attacks and defences below were run for real against an SQLite database, Flask, SQLAlchemy and a local TLS server in [`verify_week7_claims.py`](verify_week7_claims.py). Only try attacks on applications you own.

## SQL injection

**SQL injection** is a code-injection attack: the application builds an SQL query by **gluing user input into the query text**, so the user's input can change the *meaning* of the query, not just its values.

### A login form that is vulnerable

```html
<form method="post" action="/login">
  Username: <input type="text" name="name"><br>
  Password: <input type="password" name="password">
</form>
```

```python
@app.route("/login", methods=["POST"])
def login():
    name, pswd = request.form["name"], request.form["password"]
    sql = 'SELECT * FROM Users WHERE Name ="' + name + '" AND Pass ="' + pswd + '"'   # input glued into the SQL
    rows = con.execute(sql).fetchall()
    return "Welcome " + rows[0][1] if rows else ("Login failed", 401)
```

With the table `Users` containing `admin / s3cret`, `alice / pw1` and `bob / pw2`:

| Name entered | Password entered | SQL that is actually executed | Result |
| --- | --- | --- | --- |
| `abcd` | `pass` | `SELECT * FROM Users WHERE Name ="abcd" AND Pass ="pass"` | no row: **login failed** (correct) |
| `" or ""="` | `" or ""="` | `SELECT * FROM Users WHERE Name ="" or ""="" AND Pass ="" or ""=""` | `""=""` is always true, **all three users are returned**: logged in as the first one (`admin`) without a password |
| `admin" --` | anything | `SELECT * FROM Users WHERE Name ="admin" --" AND Pass ="anything"` | `--` starts an SQL comment, so the **password check disappears**: logged in as `admin` |

The quote characters typed by the user *closed the string* and the rest of the input became SQL.

More injections on the same pattern:

- **Reading other data (`UNION`).** The input `x' UNION SELECT id, Pass FROM Users --` turns `SELECT id, Name FROM Users WHERE Name = '...'` into a query that returns **all passwords**.
- **Numbers need no quote.** In `"SELECT Name FROM Users WHERE id = " + uid` the input `1 OR 1=1` returns **every** user.
- **Deleting data.** The name `x"; DROP TABLE Users; --` closes the string, ends the query with `;` and adds a second statement: `SELECT * FROM Users WHERE Name ="x"; DROP TABLE Users; --" AND Pass =""`. Many database drivers refuse several statements in one call (Python's `sqlite3` raises `ProgrammingError: You can only execute one statement at a time`, and our table survived), so *this* classic example often fails, but the login bypass and the `UNION` leak work anyway. **Never rely on the driver to save you.**

### Defence 1: parameterised queries (the real fix)

Send the **SQL text and the values separately**. The database parses the text first, with `?` placeholders; the values are then plugged in as **data** and can never become SQL.

```python
rows = con.execute("SELECT * FROM Users WHERE Name = ? AND Pass = ?", (name, pswd)).fetchall()
```

With this version all three attacks of the table above return **no rows**, a normal login (`alice`, `pw1`) still works, and even a name like `O'Brien` is handled correctly (the apostrophe is just a character).

- Placeholders are `?` in `sqlite3`, `%s` in MySQL and PostgreSQL drivers (check your driver); **never** build the query with `+`, `%`, `.format()` or an f-string.
- Only **values** can be parameters. A table or column name cannot (`SELECT * FROM ?` is a syntax error): if a name comes from the user, accept only names from a fixed allowed list.

### Defence 2: use an ORM correctly

An ORM such as **SQLAlchemy** builds queries for you. This is safe because it uses **bound parameters**; it does not "clean" or escape the text:

```python
stmt = select(User).where(User.name == "' OR '1'='1")
# generated SQL:  SELECT users.id, users.name, users.pw FROM users WHERE users.name = :name_1
# parameter:      name_1 = "' OR '1'='1"       -> treated as a (strange) name, finds nobody
```

The ORM is only as safe as the way it is used. Writing the SQL by hand **inside** the ORM brings the problem back:

```python
s.execute(text(f"SELECT name FROM users WHERE name = '{evil}'"))      # f-string in text(): INJECTABLE, returned 2 rows
s.execute(text("SELECT name FROM users WHERE name = :n"), {"n": evil})  # bound parameter: safe, returned 0 rows
```

### Defence 3: validate the input on the server

**Validation** checks that the input is what we expect *before* it is used. Check:

- **the right kind of input**: text, number, e-mail address, date (convert with `int()` and so on, and handle the error);
- **not empty**, within **length limits** (this also limits damage from overly long inputs, see [overflows](#buffer-and-input-overflows));
- **no unexpected characters**: accept only the characters that are allowed (an *allow-list*) instead of trying to list all bad ones, for example
  ```python
  import re
  def valid_username(s):
      return re.fullmatch(r"[A-Za-z0-9_]{3,20}", s) is not None
  ```
  (`valid_username("alice_01")` is `True`, `valid_username('" or ""="')` is `False`.)

> [!IMPORTANT]
> **Validation must be done on the server, just before the database query.** The `required`, `maxlength` and `type="email"` attributes of the HTML form and any JavaScript checks are only conveniences for honest users: an attacker does not use your form, he sends the HTTP request **directly** (with `curl` or a script) with whatever data he likes:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/login --data-urlencode 'name=<script>' --data-urlencode 'password='
> ```
>
> Validation is a second layer, **not a replacement** for parameterised queries.

### Defence 4: the principle of least privilege

The database account used by the web application should have **only the permissions it needs**: for example `SELECT`, `INSERT` and `UPDATE` on the needed tables, and **no** `DROP`, no access to other databases, no administrator rights. Then even a successful injection can do limited damage.

```sql
-- MySQL: an account for the web app that can only read and write the shop's data
GRANT SELECT, INSERT, UPDATE ON shop.* TO 'webapp'@'localhost';
```

(See also [the principle of least privilege](../week9/9-access-security-mechanisms.md#principle-of-least-privilege) in Week 9. SQLite has no user accounts; there the operating-system file permissions play this role.)

### Defence 5: known frameworks and updates

- Use **well-known frameworks and servers with a good security record**: they have been tested by many people.
- **Keep everything updated**: the operating system, the web server, Python and all libraries should run the **latest stable version with the security patches**. Many attacks use bugs that are already fixed in newer versions.
- **Do code audits** and follow best practices.

## Buffer and input overflows

A **buffer overflow** happens when a program writes **more data into a fixed-size memory area than fits**, overwriting the memory next to it. The result can be a crash or, worse, an attacker making the program run his own code. It affects programs written in languages that do not check bounds (C, C++), which includes many servers and protocol implementations. Python protects you from this: reading beyond the end of a list raises `IndexError` instead of touching foreign memory. So for your own code the lesson is:

- **limit the length of every input** (form fields, query strings, uploads, headers);
- use **servers and libraries with a good security record** and keep them updated, because the vulnerable code is often *theirs*.

An **input overflow** is the same family of problem seen from the application: an input that is **larger than the program expects** (too long, too many items, a number too large) causes unexpected behaviour. Length and range validation (Defence 3) prevents it.

## Passwords: store a hash, never the password

Passwords must not be stored in clear text, and also not "encrypted" (whoever steals the key reads all of them). Store a **salted hash** instead:

- a **hash** is a one-way function: easy to compute, practically impossible to reverse;
- a **salt** is a random value added before hashing, so the **same password gets a different hash for every user** and prepared tables of common-password hashes become useless.

```python
from werkzeug.security import generate_password_hash, check_password_hash

h1 = generate_password_hash("pw1")      # 'scrypt:32768:8:1$<random salt>$<hash>'
h2 = generate_password_hash("pw1")
h1 != h2                                # True: a different salt every time
check_password_hash(h1, "pw1")          # True
check_password_hash(h1, "pw2")          # False
```

A plain `hashlib.sha256(b"pw1")` always gives the *same* output for the same password (no salt), which is exactly the weakness. Use a purpose-built password hash (Werkzeug's default in version 3 is `scrypt`; `bcrypt` and `argon2` are other good choices).

## HTTPS (secure communication)

HTTP sends everything as **plain text**. Anyone who can watch the network (the same Wi-Fi, a router on the way) can read it. **HTTPS** is HTTP inside an encrypted channel created with **TLS (Transport Layer Security)**:

```text
Client ⇄ (encrypted TLS channel) ⇄ Server
```

### How HTTPS works

1. The client connects and asks for a secure session; the server sends its **digital certificate**, which contains the server's public key and the **domain name** it belongs to.
2. The client **verifies the certificate**: it must be signed by a **trusted certificate authority (CA)**, valid (not expired) and issued for the domain that the client is visiting. This is what makes it difficult to impersonate the server.
3. Client and server agree on a **secret session key** with a key-exchange (public-key mathematics and fresh random numbers), so that the key is never sent over the network; the server proves with the key of its certificate that it really is the owner of that certificate.
4. From then on **all data is encrypted** with that key (and protected against modification): a listener sees only random-looking bytes.

**What we measured.** We ran a tiny server over HTTP and over HTTPS and put a recording proxy between the client and the server, like an eavesdropper. The client posted `name=alice&password=TOPSECRET123`:

| | The eavesdropper saw |
| --- | --- |
| **HTTP** | the whole request in clear text, including `POST / HTTP` and `TOPSECRET123` |
| **HTTPS** (TLS 1.3) | only encrypted bytes: **neither** the password **nor** the word `POST` |

Certificates are checked for real: a client that does not know the (self-signed) certificate's CA stops with `SSLCertVerificationError: certificate verify failed: self-signed certificate`, and a certificate issued for another name is refused with a hostname mismatch error.

### What HTTPS does *not* do

- It secures the **transfer between client and server only**. It does not validate the data or check that the application is safe: an SQL injection works exactly the same over HTTPS.
- It **hides the content** of the request, not the fact that you are talking to that server.
- There is a small cost: a **performance overhead** for the handshake and encryption, and responses cannot be stored by shared caches along the way (the browser can still cache static files).

See [HTTPS and TLS handshake in Week 9](../week9/9-https-logging.md) for more.

## Other vulnerabilities

<details>
<summary>XSS, CSRF and more (see Week 9)</summary>

- **XSS (cross-site scripting):** an attacker gets his **script into a page that other users see** (for example in a comment) and it runs in their browsers. The defence is to **escape user text when it is written into HTML**: Flask's Jinja2 templates do it automatically for `.html` files, so `{{ comment }}` with `<script>alert(1)</script>` is output as `&lt;script&gt;alert(1)&lt;/script&gt;`. Use `|safe` only for text you trust ([autoescaping](../week3/3-4-jinja2.md#autoescaping-html-safety)).
- **CSRF (cross-site request forgery):** a malicious site makes your browser send a **fake request to a site where you are logged in**, executed on your behalf. The defence is a secret **CSRF token** in every form, which the attacker cannot guess ([cookies and CSRF](../week9/9-cookie.md#cross-site-request-forgery-csrf)).
- **Buffer / input overflow**: see [above](#buffer-and-input-overflows).
- **Passwords**: store salted hashes, see [above](#passwords-store-a-hash-never-the-password).

</details>

## Checklist

| Risk | Defence |
| --- | --- |
| SQL injection | parameterised queries / ORM bound parameters, never glue input into SQL |
| Bad or oversized input | server-side validation (type, length, allowed characters) |
| Too much damage after a break-in | least-privilege database account |
| Known bugs in software | known frameworks, regular updates and patches |
| Eavesdropping | HTTPS |
| Stolen password table | salted password hashes |
| Script in pages (XSS) | output escaping (Jinja2 autoescape) |
| Forged requests (CSRF) | CSRF tokens |

## Summary

Internet and web security is complex enough for a course of its own. The practical advice is: **use well-known frameworks with a trusted track record, never build SQL from raw user input, validate on the server, give the application the minimum privileges, keep software updated and use HTTPS**, and have your code audited.
