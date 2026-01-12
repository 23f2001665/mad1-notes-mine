# 📝 Jinja2 Cheatsheet

A quick reference guide for commonly used Jinja2 statements, filters,
and patterns.

------------------------------------------------------------------------

## 🔹 Variable Printing

``` jinja2
{{ variable }}
{{ user.name }}
{{ items[0] }}
```

👉 Outputs values from context.

------------------------------------------------------------------------

## 🔹 Template Inheritance (`extends` + `block`)

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

------------------------------------------------------------------------

## 🔹 Comments

``` jinja2
{# This is a comment #}
```

------------------------------------------------------------------------

## 🔹 Control Structures

### If / Else

``` jinja2
{% if user %}
  Hello, {{ user.name }}
{% elif guest %}
  Welcome guest
{% else %}
  Please login
{% endif %}
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

------------------------------------------------------------------------

# ✅ Summary

-   `extends` → Base layouts with `block`s\
-   `include` → Reusable fragments (`with context` / `without context`)\
-   `set` → Variables (global scope)\
-   `with` → Variables (block scope, e.g., flash messages)\
-   `macro` → Reusable function-like snippets\
-   `call` → Macros with blocks of HTML\
-   Filters → Modify data output
