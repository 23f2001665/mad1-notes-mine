# Jinja2 Guide <a name="jinja2-guide"></a>

In previous sections, we have discussed about `string.Template` and Python's built-in formatting methods like `f-strings`, `str.format()`, and `%-formatting`. These methods are great for simple string interpolation, but when it comes to generating complex HTML or text documents with appropriate safety measures, a more powerful templating engine is often needed.

## Why Jinja2?

**Jinja2** is a full-featured templating engine for Python that is widely used in web frameworks like **Flask**. It provides a robust way to separate application logic from presentation logic, making it easier to manage and maintain code.

### Key Features of Jinja2

- Allows limited expression evaluation.
- Restricted what templates can access (sandboxing).
- Clean syntax for embedding Python-like code in HTML.
- Very Easy to learn for Python developers.
- Template inheritance for reusable layouts.
- Control structures (loops, conditionals).
- Macros for reusable components.
- Filters for data transformation.

---

## Template Syntax Overview

Templates in Jinja2 are plain text blocks with placeholders and control structures enclosed in special delimiters, which when rendered with context data produce the final output.

Example of a simple Jinja2 template:

``` python
from jinja2 import Template
template = Template("""
  <h1>Welcome, {{ username }}!</h1>
  <p>Does user have admin privileges?{{ is_admin }}</p>
  <p>{{roll_number}} will not be displayed</p>
""")
rendered = template.render(username="Alice", is_admin=True)
print(rendered)
```

Output:

``` html
  <h1>Welcome, Alice!</h1>
  <p>Does user have admin privileges?True</p>
  <p> will not be displayed</p>
```

Some important information about Jinja2 rendering:

- **Context Data**: Passed as keyword arguments to `render()`.
- **Delimiters**:
  - `{{ ... }}`: Expression to print value.
  - `{% ... %}`: Control structures (if, for, block, etc.).
  - `{# ... #}`: Comments (not rendered).
- **If data is missing, Jinja2 outputs an empty string by default (can be configured).**
- **If any argument is passed extra to `render()`, it will be ignored if not used in the template.**

---

## Now we will explore the key features of Jinja2 with code examples

## Variable Printing or Interpolation

 We can use double curly braces to access variables, object attributes, list items and evaluate a limited set of python like expressions like arithmetic, logical operations etc.

 :::info
Jinja2 have its own expression syntax which is similar to Python but not exactly the same. For example, Jinja2 uses `and`, `or`, `not`. But it is important to note that not all Python expressions are supported in Jinja2 templates.
 :::

### syntax

``` jinja2
{{ variable }}
{{ user.name }}
{{ items[0] }}
{{ price * quantity }}
{{ "Hello " + user.first_name }}
{{ 5 > 3  or len(items) > 0 }}
{{ user in users }}
```

### code example

code snippet:

``` python
from jinja2 import Template
template = Template("""
  <h1>Welcome, {{ user.name }}!</h1>
  <p>Your total is: ${{ price * quantity }}</p>
""")
rendered = template.render(user={"name": "Alice"}, price=19.99, quantity=3)
print(rendered)
```

output:

``` html
  <h1>Welcome, Alice!</h1>
  <p>Your total is: $59.97</p>
```

---

## Comments

We can add comments in Jinja2 templates using `{# ... #}` syntax. Comments are ignored during rendering.

``` jinja2
{# This is a comment #}
```

:::warning
Do not confuse Jinja2 comments with HTML comments (`<!-- ... -->`). Jinja2 comments are not included in the output rendered by jinja2, while HTML comments are.
:::

---

## Control Structures

Jinja2 provides control structures like conditionals and loops to add logic to templates. Syntax is similar to Python but uses `{% ... %}` delimiters and requires explicit `endif`, `endfor` statements.

### If / Else

``` python
{% if user is not None %}
  Hello, {{ user.name }}
{% elif guest is not None %}
  Welcome guest
{% else %}
  Please login
{% endif %}
```
example:

``` python
from jinja2 import Template
template = Template("""
  {% if user == "Alice" %}
    <h1>Hello, {{ user.name }}!</h1>
  {% else %}
    <h1>Please log in.</h1>
  {% endif %}
""")
rendered = template.render(user={"name": "Alice"})
print(rendered)
```

output:

``` html
  <h1>Hello, Alice!</h1>
```

### For Loops

``` jinja2
{% for item in items %}
   <li>{{ loop.index }} - {{ item }}</li>
{% endfor %}
```

Special loop vars: `loop.index`, `loop.first`, `loop.last`,
`loop.revindex`.

### Set Variables

``` jinja2
{% set total = price * quantity %}
```

------------------------------------------------------------------------

## 🔹 With Statement (Scoped Variables)

``` jinja2
{% with x = 5 %}
   <p>{{ x }}</p>
{% endwith %}

<p>{{ x }}</p>  {# undefined here #}
```

👉 Like `set`, but limited to block scope.

Example with Flask:

``` jinja2
{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    {% for category, msg in messages %}
      <div class="alert {{ category }}">{{ msg }}</div>
    {% endfor %}
  {% endif %}
{% endwith %}
```

------------------------------------------------------------------------

## 🔹 Macros (Reusable Functions)

``` jinja2
{% macro render_input(name, type="text") %}
  <input type="{{ type }}" name="{{ name }}">
{% endmacro %}

{{ render_input("email", "email") }}
```

------------------------------------------------------------------------

## 🔹 Importing Macros

``` jinja2
{% import "forms.html" as forms %}
{{ forms.render_input("username") }}

{% from "forms.html" import render_input %}
{{ render_input("email") }}
```

------------------------------------------------------------------------

## 🔹 Call Blocks (Macros with Blocks)

``` jinja2
{% macro panel(title) %}
  <div class="panel">
    <h3>{{ title }}</h3>
    <div class="panel-body">
      {{ caller() }}
    </div>
  </div>
{% endmacro %}

{% call panel("User Info") %}
   <p>Name: {{ user.name }}</p>
   <p>Email: {{ user.email }}</p>
{% endcall %}
```

👉 Use for wrapper components (cards, modals, etc.).

------------------------------------------------------------------------

## 🔹 Filters (Common)

``` jinja2
{{ "hello world" | title }}       # Hello World
{{ name | upper }}                # UPPERCASE
{{ list | length }}               # Count
{{ value | default("N/A") }}      # Fallback
{{ text | safe }}                 # Don't escape HTML
```

------------------------------------------------------------------------

## 🔹 Escaping

``` jinja2
{% raw %}
   {{ this will not be evaluated }}
{% endraw %}
```

------------------------------------------------------------------------

## 🔹 Whitespace Control

``` jinja2
{{- variable -}}
{% if cond -%} text {%- endif %}
```

## Template Inheritance (`extends` + `block`)

``` jinja2
{% extends "base.html" %}
{% block content %}
   <h1>Hello</h1>
{% endblock %}
```

NOTE: `super()` to call parent block.

```
{% block content %}
   {{ super() }}  {# calls base.html content block #}
   <p>Additional content</p>
{% endblock %}

```
This will prepend the base content block( super()'s output ) to the block content.
------------------------------------------------------------------------

## 🔹 Includes

``` jinja2
{% include "navbar.html" %}
```

-   `with context` → Passes current variables.
-   `without context` → Isolates fragment.

Example:

``` jinja2
{% include "sidebar.html" with context %}
{% include "footer.html" without context %}
```

---

# ✅ Summary

-   `extends` → Base layouts with `block`s\
-   `include` → Reusable fragments (`with context` / `without context`)\
-   `set` → Variables (global scope)\
-   `with` → Variables (block scope, e.g., flash messages)\
-   `macro` → Reusable function-like snippets\
-   `call` → Macros with blocks of HTML\
-   Filters → Modify data output
