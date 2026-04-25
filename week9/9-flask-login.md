# Authentication in Flask: Session vs Flask-Login vs Token

So far, we learned:
- What authentication is  
- How sessions and tokens work  
- What attacks exist (CSRF, cookie theft)  

Now the question is:
> **How do we implement this in a real web application?**

Authentication answers:
> **“Who are you?”**

After login, the system must **persist identity across requests**.

There are three practical approaches:
1. Manual **Session-Based Authentication**
2. **Flask-Login** (structured session management)
3. **Token-Based Authentication** (stateless APIs)

## Basic Configuration

```python
from flask import Flask, session, redirect, url_for, request, flash, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# REQUIRED for sessions + cookies signing
app.secret_key = "very_secret_key"

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)
```

## 1. Session-Based Authentication (Manual)

Flask provides a built-in `session` object (dictionary-like).

1. User submits login form
2. Server verifies credentials
3. Server stores identity in session
4. Browser stores session cookie

### Login

```python
user = User.query.filter_by(username=username).first()

if not user:
    flash("User does not exist")
    
if not check_password_hash(user.password, password):
    flash("Incorrect password")

session['username'] = username
```

```python
session = {
    "username": "admin"
}
```

This is serialized and stored in a **signed cookie**.


### Check Login

```python
if 'username' in session:
    return f"Logged in as {session['username']}"
```

### Logout

```python
session.pop('username', None)
```

> [!DANGER]
> * No standard way to load user objects
> * No protection for routes
> * Easy to forget checks (good for learning but not for production development)
> * No session lifecycle control


## 2. Flask-Login (Structured Session Management)

Flask-Login builds on top of Flask sessions and standardizes authentication.


### 1. LoginManager

```python
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)
```

* Redirect unauthorized users
* Load user from session
* Manage session lifecycle


### 2. User Model + `UserMixin`

```python
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(255))
```

#### What does `UserMixin` provide?

| Property           | Meaning                             |
| ------------------ | ----------------------------------- |
| `is_authenticated` | True if user is logged in           |
| `is_active`        | True if account is active           |
| `is_anonymous`     | False for real users                |
| `get_id()`         | Returns unique ID (used in session) |

Without `UserMixin`, you must implement all of these manually.


### 3. User Loader

```python
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```
Session only stores user_id but we want entire user object in our `jinja` template:

```python
session = {
    "user_id": "2"
}
```

Flask-Login calls `load_user()` to convert:

```bash
user_id → full User object → current_user
```


### Login Flow (Flask-Login)

```python
user = User.query.filter_by(username=username).first()

if not user:
    flash("User does not exist")

if not check_password_hash(user.password, password):
    return redirect(url_for("login"))

login_user(user, remember=True)
```


> [!DANGER]
> `login_user()` does internally:
> 
> ```python
> session['user_id'] = user.get_id()
> session['_fresh'] = True
> ```


## current_user

```python
from flask_login import current_user
```
* Proxy object
* Automatically loaded from session
* Available in:
  * Python code
  * Jinja templates

```html
<h2>Hello, {{ current_user.username }}!</h2>
```

## Route Protection

```python
from flask_login import login_required

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")
```

If user is not logged in → redirected to `login_view`

## Logout

```python
logout_user()
```

> [!DANGER]
> 
>  Internally:
> ```python
> session.pop("user_id")
> ```

| code | usage |
|---|-----|
| `if current_user.is_authenticated:` | only true after successful login  |
| `is_active` | Used to disable accounts. If False → login blocked |

### Remember Me

```python
login_user(user, remember=True)
```
Creates:
* Long-lived cookie
* Survives browser restart

Controlled by:
```python
REMEMBER_COOKIE_DURATION = timedelta(days=7)
```

## Password Hashing

```python
generate_password_hash("admin123")
check_password_hash(user.password, password)
```

### Why hashing?

* Password is never stored directly
* Even if DB leaks → attacker cannot read original password

## Registration Example

```python
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    hashed = generate_password_hash(password)

    user = User(username=username, password=hashed)
    db.session.add(user)
    db.session.commit()

    return redirect(url_for("login"))
```


## 3. Token-Based Authentication (APIs)

Used in:
* Mobile apps
* REST APIs

### Flow

1. User logs in
2. Server generates token
3. Client stores token
4. Requests include:

```bash
Authorization: Bearer <token>
```
You will learn `Flask-JWT-Extended` for it in MAD2 course (or you can use `Flask-security-too`)

* No server-side session
* Stateless
* Scalable

> [!DANGER]
> 
>  Risks
> * Token theft = full access
> * Must use:
> 
>   * HTTPS
>   * Expiry
>   * Secure storage


### Final Summary

| Feature  | Session     | Flask-Login | Token     |
| -------- | ----------- | ----------- | --------- |
| Control  | Manual      | Managed     | Stateless |
| Security | Error-prone | Safer       | Strong    |
| Storage  | Server      | Server      | Client    |
| Best Use | Learning    | Web apps    | APIs      |

`Flask-Login` is a **safe abstraction over session-based authentication**

* Session stores **user_id**, not full user
* `user_loader` reconstructs user object
* `current_user` is a proxy
* `login_required` checks `is_authenticated`
* `logout_user` clears session
* Always hash passwords
* Always use HTTPS (in production)
* Always protect forms (CSRF)

Authentication is not just login, it has to also has to **securely maintain identity across requests**

> [!TIP]
> ### CSRF Protection
> 
> Your form:
> 
> ```html
> <form method="POST">
>     {{ csrf_token }}
> ```
> Prevents: `Cross-Site Request Forgery`
> 
> Use:
> 
> ```python
> from flask_wtf import FlaskForm
> from flask_wtf.csrf import CSRFProtect
> 
> csrf = CSRFProtect(app)
> ```