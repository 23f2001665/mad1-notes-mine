# 🌐 Appdev Quick Revision

---

## 🧩 1. What is an App?

### 📘 Definition

An **application (app)** is a software program designed to perform specific tasks for users.
It may run:

* on a **device** (mobile, desktop),
* on the **web** (browser-based),
* or as a **hybrid** of both.

**Examples:**

* **Native app:** Android Calculator, MS Word
* **Web app:** Gmail, Google Docs
* **Hybrid app:** Instagram (mobile app + web interface)

### ⚙️ Platforms for Apps

Different types of apps need different **platforms** to run or develop on.

| Type        | Platform Example      | Description                             |
| ----------- | --------------------- | --------------------------------------- |
| Mobile App  | Android, iOS          | Runs directly on smartphone OS          |
| Web App     | Browser               | Delivered via HTTP, executed in browser |
| Desktop App | Windows, macOS, Linux | Installed locally, often GUI-based      |

### 🧰 SDK (Software Development Kit)

An **SDK** is a collection of tools, libraries, documentation, and compilers that developers use to build software for a specific platform.

**Examples:**

* Android SDK → tools to build Android apps
* iOS SDK → Xcode + Apple APIs
* Java SDK (JDK) → for Java-based desktop/server apps
* Flask → a micro “web app SDK” for Python

**Try this 👨‍💻**

```bash
# Check installed SDKs (example for Python)
python --version
pip list
```

👉 Think: Which of these tools together form your *Python development kit*?

---

## 🌐 2. Network Architecture

### 🕰️ History of Networks

* **1960s:** ARPANET → first packet-switched network (ancestor of Internet)
* **1980s:** TCP/IP protocol stack standardized
* **1990s:** Rise of World Wide Web (HTTP + HTML)
* **2000s–Present:** Broadband, Wi-Fi, mobile data, cloud computing

**Key milestone protocols:**

* TCP (Transmission Control Protocol)
* IP (Internet Protocol)
* HTTP (Hypertext Transfer Protocol)
* DNS (Domain Name System)

---

### 🌍 History of the Web

Invented by **Tim Berners-Lee (1989)**

* Used **HTTP** for communication
* Used **HTML** for documents
* Used **URL** to identify resources

**Evolution:**

| Generation | Features                                                |
| ---------- | ------------------------------------------------------- |
| Web 1.0    | Static content, read-only websites                      |
| Web 2.0    | User interaction, dynamic content (social media, blogs) |
| Web 3.0    | Decentralization, AI integration, semantic data         |

---

### 🖥️ Client–Server vs Peer-to-Peer

| Model                  | Description                                           | Example                |
| ---------------------- | ----------------------------------------------------- | ---------------------- |
| **Client–Server**      | Central server provides resources to multiple clients | Gmail, YouTube         |
| **Peer-to-Peer (P2P)** | Each node acts as both client and server              | BitTorrent, Blockchain |

**Diagram:**

```
Client-Server:     P2P:
Client → Server    Node ↔ Node
Client → Server    Node ↔ Node
```

**Try this 👨‍💻**
Run a mini client-server test:

```bash
# In one terminal:
nc -l 8080

# In another terminal:
nc 127.0.0.1 8080
# Type something and see it appear on both ends.
```

---

### 🔁 Loopback Address

* **127.0.0.1** or **localhost** refers to your own machine.
* Used for testing without an active network.

Example:

```bash
ping 127.0.0.1
```

→ Tests your local network stack.

---

## 🧱 3. Software Architecture

### 🧩 MVC (Model–View–Controller)

**MVC** separates an application into three logical layers:

| Layer          | Role                         | Flask Analogy                  |
| -------------- | ---------------------------- | ------------------------------ |
| **Model**      | Manages data & logic         | Database models (`SQLAlchemy`) |
| **View**       | Displays UI                  | HTML templates (`Jinja2`)      |
| **Controller** | Handles requests, user input | Flask routes & functions       |

**Example (Flask):**

```python
# Controller
@app.route('/users')
def show_users():
    users = User.query.all()       # Model
    return render_template('users.html', users=users)  # View
```

**Try this 👨‍💻**
Explain in your words:

> When a user visits `/users`, which layer actually *runs first* and which *renders last*?

---

## ⚙️ 4. Tools

### 🔌 `nc` (Netcat)

Used for sending/receiving raw data over TCP or UDP.

**Examples:**

```bash
# Listen on port 8080
nc -l 8080

# Connect to another host
nc 127.0.0.1 8080
```

You can even send a file:

```bash
# Sender
nc -l 1234 < file.txt
# Receiver
nc 192.168.0.5 1234 > received.txt
```

---

### 🌍 `python -m http.server`

Start a quick web server to share files:

```bash
python -m http.server 8000
```

Now visit `http://localhost:8000` in your browser.

**Try this 👨‍💻**
Create an `index.html` and test:

```html
<h1>Hello, Python Server!</h1>
```

---

### 🌐 `curl`

Command-line tool for making HTTP requests.

**Examples:**

```bash
curl https://example.com
curl -X POST -d "name=Himanshu" http://localhost:5000/form
```

Use `-v` for verbose output and headers:

```bash
curl -v https://httpbin.org/get
```

---

### 📡 HTTP Methods

| Method | Description               | Safe? | Idempotent? |
| ------ | ------------------------- | ----- | ----------- |
| GET    | Retrieve data             | ✅     | ✅           |
| POST   | Create resource           | ❌     | ❌           |
| PUT    | Replace resource          | ❌     | ✅           |
| PATCH  | Partially modify resource | ❌     | ❌           |
| DELETE | Remove resource           | ❌     | ✅           |

**Example (Flask):**

```python
@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        return "User created"
    return "User list"
```

---

Perfect 😎
Let’s continue with **Part 2** of your study-oriented Markdown handbook.
This section covers **Markups**, **CSS**, and **UI Principles**, with solid theory, examples, and small exercises.

---

## 🏷️ 5. Markup Languages

### 📖 History

A **markup language** is a way to *annotate text* so that computers can interpret structure or presentation.

* **1960s:** SGML (Standard Generalized Markup Language) — the ancestor of HTML and XML
* **1990s:** HTML (1993) made SGML practical for the web
* **2000s:** XML became a universal data representation format
* **2010s–Now:** Markdown, JSON, and lightweight markups dominate APIs and docs

---

### 🧩 Types of Markup

| Type                         | Purpose                                   | Example                 |
| ---------------------------- | ----------------------------------------- | ----------------------- |
| **Presentational**           | Specifies *how* text looks                | `<b>bold</b>`           |
| **Procedural**               | Contains formatting instructions or logic | LaTeX, RTF              |
| **Descriptive (Structural)** | Describes *what* content is               | `<article>`, `<header>` |

---

### 🌐 HTML Basics

**HTML (HyperText Markup Language)** defines the structure of a web page.
It uses **elements** enclosed in tags.

Example:

```html
<!DOCTYPE html>
<html>
  <head>
    <title>My First Page</title>
  </head>
  <body>
    <h1>Hello, Web!</h1>
    <p>This is a simple paragraph.</p>
  </body>
</html>
```

**Important concepts:**

* **Elements** → `<p>`, `<h1>`, `<div>`
* **Attributes** → `<img src="cat.png" alt="Cat">`
* **Nesting** → Tags must be properly opened and closed
* **Block vs Inline** → `<div>` (block) vs `<span>` (inline)

---

### 🌳 DOM (Document Object Model)

The **DOM** represents an HTML document as a *tree of nodes*.

```
Document
 └── html
     ├── head
     │   └── title
     └── body
         ├── h1
         └── p
```

You can manipulate the DOM using JavaScript or frameworks like Vue/React.

**Example:**

```javascript
document.querySelector("h1").textContent = "Welcome, Himanshu!";
```

**Try this 👨‍💻**

1. Open any web page.
2. Press **F12 → Console**, type:

   ```js
   document.body.style.backgroundColor = "lightblue";
   ```
3. See the effect live!

---

## 🎨 6. CSS (Cascading Style Sheets)

CSS controls the **presentation** and **layout** of HTML elements.

---

### 🔍 Selectors

A **selector** targets elements to style.

| Selector     | Example               | Meaning                     |
| ------------ | --------------------- | --------------------------- |
| Element      | `p {}`                | All `<p>` tags              |
| ID           | `#main {}`            | Element with `id="main"`    |
| Class        | `.btn {}`             | Elements with `class="btn"` |
| Attribute    | `input[type=text] {}` | Inputs of type text         |
| Descendant   | `div p {}`            | All `<p>` inside `<div>`    |
| Pseudo-class | `a:hover {}`          | Style when hovered          |

**Example:**

```css
h1 {
  color: navy;
  text-align: center;
}
```

---

### ⚖️ Priority Rules (Specificity)

When multiple styles apply, CSS decides which one wins:

| Selector Type                    | Specificity Weight |
| -------------------------------- | ------------------ |
| Inline Style                     | 1000               |
| ID                               | 100                |
| Class / Attribute / Pseudo-class | 10                 |
| Element                          | 1                  |
| Universal `*`                    | 0                  |

> When scores tie, **last rule wins** (because of the “Cascading” in CSS).

**Example:**

```html
<p id="text" class="note">Hello!</p>
```

```css
.note { color: blue; }      /* 10 */
#text { color: red; }       /* 100 → wins */
p { color: green; }         /* 1 */
```

Result → **Red**

---

### 🧬 Inheritance

Some properties naturally *inherit* from parent elements (like `color`, `font-family`), while others (like `margin`, `border`) do not.

**Example:**

```html
<div style="color: blue;">
  <p>This will be blue</p>
  <span>This too!</span>
</div>
```

---

### 🕵️ Inspect Tool

Every browser provides a **Developer Tools → Elements → Styles** tab.
You can:

* View applied CSS rules
* Edit them live
* Test responsive design

**Try this 👨‍💻**
Right-click on an element → *Inspect* → change its color.
Instant feedback = instant learning.

---

## 🧠 7. UI (User Interface)

---

### 🧍 Static vs Dynamic UI

| Type           | Description                                    | Example                             |
| -------------- | ---------------------------------------------- | ----------------------------------- |
| **Static UI**  | Content doesn’t change without reload          | HTML + CSS only                     |
| **Dynamic UI** | Updates interactively (via JS or data-binding) | React, Vue, Flask + Jinja templates |

**Example (Dynamic via JS):**

```html
<button onclick="changeText()">Click Me</button>
<p id="msg">Hello</p>

<script>
function changeText() {
  document.getElementById('msg').innerText = "You clicked!";
}
</script>
```

---

### ♿ Accessibility Principles (POUR)

Accessibility ensures **everyone** (including users with disabilities) can use your app.

| Principle              | Meaning                                  | Example                      |
| ---------------------- | ---------------------------------------- | ---------------------------- |
| **P – Perceivable**    | Info must be visible/hearable            | Alt text for images          |
| **O – Operable**       | Interface can be used via keyboard, etc. | Tab navigation               |
| **U – Understandable** | Predictable and clear                    | Simple language, form labels |
| **R – Robust**         | Works across devices & assistive tech    | Valid HTML, ARIA roles       |

**Example:**

```html
<img src="dog.jpg" alt="Golden retriever playing fetch">
<label for="email">Email:</label>
<input id="email" type="email" aria-required="true">
```

**Try this 👨‍💻**
Use the **Lighthouse** tab in Chrome DevTools → *Accessibility Audit* → check your page score.

---

## 🧰 8. Python Tools for UI and Templating

When building apps or web interfaces, Python gives you multiple ways to **insert variables into text or HTML**.

Let’s go from simplest to most powerful.

---

### 🪄 f-Strings

Introduced in Python 3.6.
They allow inline variable substitution directly inside strings.

**Example:**

```python
name = "Himanshu"
age = 21
print(f"My name is {name} and I am {age} years old.")
```

Output:

```
My name is Himanshu and I am 21 years old.
```

**Advantages:**

* Fast and readable
* Can include expressions:

  ```python
  print(f"{2 + 3 = }")
  # Output: 2 + 3 = 5
  ```

**Try this 👨‍💻**
Make a mini HTML line:

```python
title = "Web Systems"
print(f"<h1>{title}</h1>")
```

---

### 💬 `string.Template`

Safer and simpler substitution (useful when taking input or working with external templates).

**Example:**

```python
from string import Template

t = Template("Welcome, $user! Your balance is $$${amount}.")
msg = t.substitute(user="Himanshu", amount=250)
print(msg)
```

Output:

```
Welcome, Himanshu! Your balance is $250.
```

Difference from f-strings:

* Uses `$` placeholders
* Doesn’t execute Python expressions (safer for user input)

---

### ⚙️ `sys.argv` and `sys.exit`

#### `sys.argv`

Gives access to command-line arguments.

**Example:**

```python
import sys
print("Arguments:", sys.argv)
```

If run as:

```bash
python app.py Hello Flask
```

Output:

```
Arguments: ['app.py', 'Hello', 'Flask']
```

#### `sys.exit`

Gracefully stops program execution.

```python
import sys

if len(sys.argv) < 2:
    print("Usage: python app.py <name>")
    sys.exit(1)

print(f"Hello {sys.argv[1]}!")
```

---

### 🧱 pyhtml

A small Python library to **generate HTML using Python syntax** (like JSX or React components).

**Example:**

```python
from pyhtml import html, body, h1, p

page = html(
    body(
        h1("Hello from Python!"),
        p("This HTML was generated dynamically.")
    )
)

print(page.render())
```

Output:

```html
<html><body><h1>Hello from Python!</h1><p>This HTML was generated dynamically.</p></body></html>
```

**Try this 👨‍💻**
Use `python -m http.server` and open the file you generate with `pyhtml`.

---

### 🧩 Jinja2

A **powerful templating engine** used by Flask.
It allows embedding Python-like expressions inside HTML safely.

**Example:**

```html
<!-- templates/user.html -->
<h2>Hello, {{ name }}!</h2>
<p>You have {{ messages|length }} new messages.</p>
```

```python
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('user.html', name="Himanshu", messages=['hi', 'ok', 'bye'])
```

Output:

```
Hello, Himanshu!
You have 3 new messages.
```

**Features:**

* `{{ }}` → expression interpolation
* `{% %}` → control logic (loops, conditions)
* Filters → e.g., `|upper`, `|length`, `|safe`

**Try this 👨‍💻**
Add to a template:

```html
{% for i in range(3) %}
  <p>Line {{ i }}</p>
{% endfor %}
```

---

## 🧭 9. Flask Fundamentals

Flask is a **micro web framework** for Python.
It handles routing, requests, and rendering.

---

### 🧱 App Creation

**Basic setup:**

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"

if __name__ == '__main__':
    app.run(debug=True)
```

Run:

```bash
python app.py
```

Then visit → [http://localhost:5000](http://localhost:5000)

---

### 🚦 Routes

Routes map URLs to functions (called *view functions*).

```python
@app.route('/about')
def about():
    return "About Page"
```

Multiple routes can point to same function:

```python
@app.route('/')
@app.route('/home')
def home():
    return "Home Page"
```

---

### 🧾 Forms (POST requests)

HTML form:

```html
<form action="/submit" method="POST">
  <input name="username" placeholder="Enter name">
  <button type="submit">Send</button>
</form>
```

Flask handler:

```python
from flask import request

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['username']
    return f"Received: {name}"
```

---

### ❓ Query Parameters

Used in URLs after `?`, like `/search?q=python`.

```python
@app.route('/search')
def search():
    query = request.args.get('q', 'None')
    return f"Search term: {query}"
```

Try:

```
http://localhost:5000/search?q=Flask
```

---

### 🧭 URL Parameters

Dynamic routes with variables:

```python
@app.route('/user/<username>')
def user(username):
    return f"Hello {username}"
```

Type conversion:

```python
@app.route('/post/<int:id>')
def post(id):
    return f"Post ID: {id}"
```

---

### 🔁 Redirect and `url_for`

`url_for()` builds URLs dynamically from function names.

```python
from flask import redirect, url_for

@app.route('/')
def home():
    return redirect(url_for('dashboard', user='Himanshu'))

@app.route('/dashboard/<user>')
def dashboard(user):
    return f"Welcome to dashboard, {user}!"
```

---

**Try this 👨‍💻**
Build a small app:

* `/form` → shows a form
* `/greet` → receives form input
* Redirect back to `/form` after greeting

---

## 📡 10. Numericals (Networking and Data Metrics)

Let’s test your applied understanding.

---

### ⚡ Latency

**Definition:**
Time taken for a request to travel from source → destination → back.

**Formula:**

```
Latency = Round Trip Time (RTT)
```

If each one-way trip = 30 ms → latency = 60 ms.

---

### 🔢 Maximum Number of Requests

If a server handles `R` requests per second and you test for `T` seconds:

```
Total Requests = R × T
```

Example:

```
R = 200 requests/sec, T = 60 sec → 12,000 requests
```

---

### 📦 Data Transferred

```
Data = Packet Size × Number of Packets
```

Example:

```
Packet = 1.5 KB
Packets = 1000
Data = 1.5 × 1000 KB = 1.5 MB
```

---

### 🔄 Unit Conversions

| Unit  | Conversion |
| ----- | ---------- |
| 1 KB  | 1024 bytes |
| 1 MB  | 1024 KB    |
| 1 GB  | 1024 MB    |
| 1 bit | 1/8 byte   |

Example:

```
10 MB = 10 × 1024 × 1024 × 8 = 83,886,080 bits
```

---

### 🧮 Base Conversions

**Binary → Decimal**

```
1011₂ = (1×8) + (0×4) + (1×2) + (1×1) = 11₁₀
```

**Decimal → Hex**

```
255₁₀ = FF₁₆
```

Python tip:

```python
bin(10), hex(255), int('1011', 2)
```

---

### 🔤 Encoding Questions

Each **character set** defines how many bits per character are needed.

| Encoding       | Bits per character | Notes                      |
| -------------- | ------------------ | -------------------------- |
| ASCII          | 7 bits             | English only               |
| Extended ASCII | 8 bits             | Latin/Western              |
| UTF-8          | 8–32 bits          | Variable-length, universal |
| UTF-16         | 16 or 32 bits      | Common in Windows          |
| UTF-32         | 32 bits            | Fixed width, slower        |

**Example question:**

> Minimum bits to represent 256 characters?

Answer → 8 bits (2⁸ = 256)

---

### 🧠 Quick Recap

| Concept       | Formula / Example                 |
| ------------- | --------------------------------- |
| Latency       | RTT = 2 × one-way delay           |
| Throughput    | Data / Time                       |
| Conversion    | 1 byte = 8 bits                   |
| Encoding bits | log₂(n) bits needed for n symbols |

---

### ✅ Mini Challenge

**Question:**
If a file is 2 MB and your network speed is 1 Mbps,
how long will it take to transfer?

**Solution:**
1 Mbps = 1 megabit/sec = 1/8 MB/sec
→ 2 MB / (1/8 MB/s) = 16 seconds.

---
