# Remaining Topics:

## 1. `<dl>`, `<dt>`, `<dd>` Tag (HTML Definition List)

These tags are used together to display term–description pairs like in glossaries, documentation, or FAQs.

| Tag    | Meaning                 |
| ------ | ----------------------- |
| `<dl>` | Definition list wrapper |
| `<dt>` | Definition term         |
| `<dd>` | Definition description  |

**Example:**

```html
<dl>
  <dt>Python</dt>
  <dd>A high-level programming language.</dd>

  <dt>Flask</dt>
  <dd>A lightweight web framework in Python.</dd>
</dl>
```

---

## 2. Macros in Jinja2

Macros in Jinja are like functions for HTML templates. They help **avoid repetition**.

**Example:**

```html
{% macro input_field(name, label, type="text") %}
  <label>{{ label }}</label>
  <input type="{{ type }}" name="{{ name }}">
{% endmacro %}

<form>
    {{ input_field("username", "Username") }}
    {{ input_field("password", "Password", "password") }}
</form>
```

---

## 3. Template Inheritance in Jinja (Very Useful in Flask)

Jinja supports inheritance via `block` and `extends`. This is how we reuse a layout (`base.html`).

### base.html

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Welcome{% endblock %}</title>
</head>
<body>
    <header>My Website</header>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

### child.html

```html
{% extends "base.html" %}
{% block title %}Home{% endblock %}
{% block content %}
  <p>Hello from Home Page!</p>
{% endblock %}
```

---

## 4. `set` in Jinja

Used to create variables inside templates.

```html
{% set name = "Himanshu" %}
<p>Hello {{ name }}</p>

{% set total = price * quantity %}
<p>Total cost: {{ total }}</p>
```

---

## 5. Jinja Filters

Filters transform data inside templates.

| Filter        | Purpose                  | Example   |                     |
| ------------- | ------------------------ | --------- | ------------------- |
| `sort`        | Sort list                | `{{ nums  | sort }}`            |
| `reverse`     | Reverse sequence         | `{{ nums  | reverse }}`         |
| `groupby`     | Group items by attribute | `{{ users | groupby('role') }}` |
| `upper/lower` | Case conversion          | `{{ name  | upper }}`           |
| `join`        | List to string           | `{{ items | join(', ') }}`      |

**Example:**

```html
{% set numbers = [5, 3, 9, 1] %}
Sorted: {{ numbers|sort }}  --> [1,3,5,9]
```

link: [link](https://tedboy.github.io/jinja2/templ14.html)

---

## 6. `curl`

Command-line tool to make HTTP requests.

### GET Request

```bash
curl http://127.0.0.1:5000/users
```

### POST Request

```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"name": "John"}' \
     http://127.0.0.1:5000/add_user
```

---

## 7. URL Parameters in Flask

Flask routes can capture parameters from the URL using converters.

| Converter      | Example                | Type         |
| -------------- | ---------------------- | ------------ |
| `<int:var>`    | `/user/5`              | Integer      |
| `<string:var>` | `/user/john`           | Default type |
| `<float:var>`  | `/num/5.6`             | Float        |
| `<path:var>`   | `/files/some/file.txt` | Path         |
| `<uuid:var>`   | `/order/uuid`          | UUID         |

**Example:**

```python
@app.route('/user/<int:user_id>')
def user_profile(user_id):
    return f"User ID = {user_id}"
```

---

## 8. Query Parameters

These are passed after `?` in the URL.

```
/search?query=python&page=2
```

**Example (Flask):**

```python
@app.route('/search')
def search():
    q = request.args.get('query')
    page = request.args.get('page', default=1, type=int)
    return f"Searching for {q} on page {page}"
```

---

## 9. HTML `<input>` Tag

Used in forms.

```html
<input type="text" name="username">
<input type="password" name="password">
<input type="email" name="email">
<input type="submit" value="Submit">
<select>
    <option name="same">option1</option>
    <option name="same">option2</option>
</select>
```

---

## 10. Route With and Without Forward Slashes in Flask

```python
@app.route('/hello')
def hello():
    return "Hello"
```

– Requires exact `/hello`

```python
@app.route('/hello/')
def hello2():
    return "Hello"
```

– Accessible via `/hello/` **AND** `/hello`

> ✅ Best practice: use trailing slash for directory-like resources.

---


## 12. SQLAlchemy Queries (ORM Style)

### Insert

```python
user = User(name="Alice", email="alice@email")
db.session.add(user)
db.session.commit()
```

### Select

```python
users = User.query.all()
user = User.query.filter_by(name="Alice").first()
user = User.query.get(1)
```

### Update

```python
user = User.query.get(1)
user.name = "Alicia"
db.session.commit()
```

### Delete

```python
db.session.delete(user)
db.session.commit()
```

---
