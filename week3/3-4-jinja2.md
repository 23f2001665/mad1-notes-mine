# Jinja2 Guide

>This guide is designed as a compact reference to Jinja2 syntax and features.
>You can read it linearly or jump directly to a section when you need a refresher.

In previous sections, we have discussed about `string.Template` and Python's built-in formatting methods like `f-strings`, `str.format()`, and `%-formatting`. These methods are great for simple string interpolation, but when it comes to generating complex HTML or text documents with appropriate safety measures, a more powerful templating engine is often needed.

## Why Jinja2?

**Jinja2** is a full-featured templating engine for Python that is widely used in web frameworks like **Flask**. It provides a robust way to separate application logic from presentation logic, making it easier to manage and maintain code.

### Key Features of Jinja2

- Allows limited expression evaluation.
- If configured correctly, restricts what templates can access (sandboxing).
- Optional automatic HTML escaping (autoescaping), switched on by Flask for HTML templates.
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

```python
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

```html
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
- **If data is missing, Jinja2 outputs an empty string by default (can be configured).** But careful: only printing the missing variable itself is safe. Reading an attribute or item of a missing variable (`{{ user.name }}` when `user` was not passed) raises an `UndefinedError`.
- **If any argument is passed extra to `render()`, it will be ignored if not used in the template.**

---

## Variable Printing or Interpolation

We can use double curly braces to access variables, object attributes, list items and evaluate a limited set of python like expressions like arithmetic, logical operations etc.

> [!NOTE]
> Jinja2 has its own expression syntax which is similar to Python but not exactly the same. For example, Jinja2 has filters (`items|length`), tests (`x is defined`) and `~` for joining strings, while Python features such as list comprehensions, lambdas and f-strings are not supported. So not all Python expressions work in Jinja2 templates.

### syntax

```jinja
{{ variable }}
{{ user.name }}
{{ items[0] }}
{{ price * quantity }}
{{ "Hello " + user.first_name }}
{{ 5 > 3  or items|length > 0 }}
{{ user in users }}
```

### code example

code snippet:

```python
from jinja2 import Template
template = Template("""
  <h1>Welcome, {{ user.name }}!</h1>
  <p>Your total is: ${{ price * quantity }}</p>
""")
rendered = template.render(user={"name": "Alice"}, price=19.99, quantity=3)
print(rendered)
```

output:

```html
  <h1>Welcome, Alice!</h1>
  <p>Your total is: $59.97</p>
```

<details>
<summary><b>Try it yourself</b></summary>

copy the following code and paste it into a python file, then run it to see the output

```python
from jinja2 import Template
template = Template("""
  <h2>Hello, {{ customer.first_name }} {{ customer.last_name }}!</h2>
  <p>Your order total is: ${{ item_price * item_quantity }}</p>
""")
rendered = template.render(customer={"first_name": "John", "last_name": "Doe"}, item_price=15.50, item_quantity=2)
print(rendered)
```

</details>

---

## Comments

We can add comments in Jinja2 templates using `{# ... #}` syntax. Comments are ignored during rendering.

```jinja
{# This is a comment #}
```

> [!WARNING]
> Do not confuse Jinja2 comments with HTML comments (`<!-- ... -->`). Jinja2 comments are not included in the output rendered by jinja2, while HTML comments are. Many times we may try to comment out jinja2 code using HTML comments, but that will not work as expected: the Jinja2 code inside the HTML comment is still executed.

---

## Control Structures

Jinja2 provides control structures like conditionals and loops to add logic to templates. Syntax is similar to Python but uses `{% ... %}` delimiters and requires explicit `endif`, `endfor` statements.

### If / Else

```jinja
{% if condition %}
  Block A
{% elif condition %}
  Block B
{% elif condition %}
  Block C
{% else %}
  Block D
{% endif %}
```

example:

```python
from jinja2 import Template
template = Template("""
  {% if user.name == "Alice" %}
    <h1>Hello, {{ user.name }}!</h1>
  {% else %}
    <h1>Please log in.</h1>
  {% endif %}
""")
rendered = template.render(user={"name": "Alice"})
print(rendered)
```

output:

```html
  <h1>Hello, Alice!</h1>
```

### For Loops

```jinja
{% for iterative_variable in iterable %}
  Block of code that can use {{ iterative_variable }}
{% endfor %}
```

example:

```python
from jinja2 import Template
template = Template("""
  <ul>  
  {% for item in items %}
    <li>{{ item }}</li>
  {% endfor %}
  </ul>
""")
rendered = template.render(items=["Apple", "Banana", "Cherry"])
print(rendered)
```

output:

```html
  <ul>  
    <li>Apple</li>
    <li>Banana</li>
    <li>Cherry</li>
  </ul>
```

#### Special loop vars

Inside a for loop, Jinja2 provides special variables to get information about the loop state:

- `loop.index`: Current iteration (1-based).
- `loop.index0`: Current iteration (0-based).
- `loop.revindex`: Remaining iterations (1-based).
- `loop.revindex0`: Remaining iterations (0-based).
- `loop.first`: True if first iteration.
- `loop.last`: True if last iteration.
- `loop.length`: Total number of items.

Example:

```python
from jinja2 import Template
template = Template("""
{% for item in items %}
  <p>{{ loop.index }}: {{ item }} </p>{% if not loop.last %},{% endif %}
{% endfor %}
""")
rendered = template.render(items=["Apple", "Banana", "Cherry"])
print(rendered)
```

output:

```html
  <p>1: Apple </p>,
  <p>2: Banana </p>,
  <p>3: Cherry </p>
```

#### Try it yourself

copy the following code and paste it into a python file, then run it to see the output

```python
from jinja2 import Template
template = Template("""
{% for user in users %}
  <p>User {{ loop.index }}: {{ user.first_name }} {{ user.last_name }}</p>{% if not loop.last %},{% endif %}
{% endfor %}
""")
rendered = template.render(users=[{"first_name": "John", "last_name": "Doe"}, {"first_name": "Jane", "last_name": "Smith"}, {"first_name": "Alice", "last_name": "Johnson"}])
print(rendered)
```

- Jinja2 supports looping over lists, tuples, dictionaries (`{% for key, value in data.items() %}`; looping over a dictionary directly gives its keys), and ranges.
- Jinja2 has only `for` loops, no `while` loops.
- `break` and `continue` are not available by default (they raise a `TemplateSyntaxError`). They need the `jinja2.ext.loopcontrols` extension, `Environment(extensions=["jinja2.ext.loopcontrols"])`. Usually it is simpler to filter the loop instead: `{% for x in items if x.visible %}`.

## Scope, Reusable Blocks and Variable Management

Jinja2 provides mechanisms to define and manage variables within templates. This includes setting variables, scoping them, and creating reusable components.

### Scopes in Jinja2

A scope defines where a variable can be seen. Jinja2 has one **template (top-level) scope** and a few constructs that open a **nested scope**:

- **Template scope**: everything written outside the constructs below. A variable set here can be used from the `set` line to the end of the template, also inside the nested scopes (reading it is always allowed), and by templates that `include` or `import` this one (see [Sharing variables between templates](#sharing-variables-between-templates)).
- **Nested scopes** are opened by `for` (a **new scope for every iteration**), `with`, `macro`, `call`, `filter` and `{% block %}`. Variables set inside them (and the loop variables `i`, `loop`...) disappear at the end tag.
- **`if` / `elif` / `else` do not open a scope**: a variable set inside an `if` is still there after `{% endif %}`.

| Construct | New scope? | Is a variable `set` inside visible after the end tag? |
| --------- | ---------- | ----------------------------------------------------- |
| `if` / `elif` / `else` | No | **Yes** |
| `for` | Yes, for every iteration | No |
| `with` | Yes | No |
| `macro` | Yes | No |
| `call` | Yes | No |
| `filter` | Yes | No |
| `block` (template inheritance) | Yes | No |

```python
from jinja2 import Template
template = Template("""
{% if true %}{% set a = "set inside if" %}{% endif %}
{% for i in range(2) %}{% set b = "set inside for" %}{% endfor %}
a: {{ a }}
b: {{ b }}
""")
print(template.render())
```

Output:

```txt
a: set inside if
b:
```

### Set Statement (Assigning Variables)

We can define variables using the `set` statement. A variable defined with `set` exists in the **scope** where it is declared (see above) from the `set` line onwards: uses before the `set` line do not see it.

```jinja

<p>{{ variable }}</p>  <!-- undefined here -->
{% set variable = value %}
<p>{{ variable }}</p>  <!-- defined here -->
```

`set` accepts any expression, and it has two more forms:

```jinja
{% set total = price * quantity %}                 {# any expression #}
{% set a, b = 1, 2 %}                               {# unpacking #}
{% set greeting %}Hello, {{ name }}!{% endset %}    {# block form: the rendered text becomes the value #}
{% set shout | upper %}hello{% endset %}            {# block form with a filter #}
```

```python
from jinja2 import Template
template = Template("""
{% set a, b = 1, 2 %}
{% set greeting %}Hello, {{ name }}!{% endset %}
{% set shout | upper %}{{ greeting }}{% endset %}
{{ a }} {{ b }}
{{ greeting }}
{{ shout }}
""")
print(template.render(name="Alice"))
```

Output:

```txt
1 2
Hello, Alice!
HELLO, ALICE!
```

Unlike Python, chained assignment (`{% set a = b = 1 %}`) is not allowed (`TemplateSyntaxError`), and we cannot assign to constants such as `true`.

**Example #6**

```python
from jinja2 import Template
template = Template("""
  {% set total = price * quantity %}
  <p>Total Price: ${{ total }}</p>
""")
rendered = template.render(price=19.99, quantity=3)
print(rendered)
```

Output:

```html
  <p>Total Price: $59.97</p>
```

- A variable defined with `set` takes the scope where it is defined and can be **read** in that scope and in every nested scope inside it (loops, macros, `with`...). If defined at the top level, it can be read through the rest of the template after its declaration.

The name of an outer variable cannot be **re-assigned** from inside a nested scope (`for`, `with`, `macro`, ...). A `set` there creates a *new* variable with the same name that exists only inside that scope (inside a loop: only for that one iteration) and it will not affect the variable outside. (`if` is the exception: it opens no scope, so a `set` inside it does change the variable.)

A follow up question become then how we can accumulate values in a variable across iterations of a loop? We will see that in the next section using `namespace`.

### Namespace (Mutable Objects)

Jinja2 provides a `namespace` class that can be used to create mutable objects that can be modified within loops and blocks. This allows us to create mutable variables that can be updated across iterations of a loop or within blocks. The *name* `ns` itself is never re-assigned, only an attribute of the object it refers to is changed, and that object is shared by every scope.

**Example #7**

```python
from jinja2 import Template
template = Template("""
{% set ns2 = namespace(total=0) %}
{% set ns1 = namespace(total=0) %}
{% for i in range(5) %}
  {% set ns1.total = ns1.total + i %}
    {% set ns2.total = ns2.total + i*2 %}
{% endfor %}
<p>Total in ns1: {{ ns1.total }}</p>
<p>Total in ns2: {{ ns2.total }}</p>
""")
rendered = template.render()
print(rendered)
```

Output:

```html
<p>Total in ns1: 10</p>
<p>Total in ns2: 20</p>
```

> [!NOTE]
>
> - Each namespace object is a separate mutable object that can hold multiple attributes. We can use it to store and update multiple related variables together.
> - The namespace object follows normal variable scope, but its attributes can be mutated across inner scopes because the object reference is shared.
> - Only a `namespace` accepts `{% set obj.attr = ... %}`: on a dictionary it raises a `TemplateRuntimeError` ("cannot assign attribute on non-namespace object").

Often we do not need an accumulator at all, a filter is simpler (and heavy calculations are better done in the Python view function before rendering):

```python
from jinja2 import Template
template = Template("{{ range(5) | sum }} and {{ products | sum(attribute='price') }}")
print(template.render(products=[{"price": 2}, {"price": 3}]))
```

Output:

```txt
10 and 5
```

### With Statement (Scoped Variables)

Like `set`, but manually defined scope. Variables defined with `with` are only accessible within that block and its nested blocks.

```jinja
{% with x = 5 %}
   <p>{{ x }}</p>
{% endwith %}

<p>{{ x }}</p>  {# undefined here #}
```

**Note**: undefined variables are rendered as empty strings by default.

**Example #8**

```python
from jinja2 import Template
template = Template("""
  {% with discount = price * 0.1 %}
    <p>Discount: ${{ discount }}</p>
  {% endwith %}
  <p>Discount outside block: ${{ discount }}</p>  {# undefined here, variable discount cannot be accessed outside the with block #}
""")
rendered = template.render(price=100)
print(rendered)
```

Output (the `{# ... #}` comment is not part of the output):

```html
  <p>Discount: $10.0</p>
  <p>Discount outside block: $</p>
```

**Important Gotcha**: Look at the following code snippet, and try to guess the output before running it.

```python
from jinja2 import Template
template = Template("""
  {% set x = 10 %}
  <p>Value of x: {{ x }}</p>
  {% for i in range(5) %}
    {% set x = x + i %}
    <p>x inside the loop: {{ x }}</p>
  {% endfor %}
  <p>Value of x after loop: {{ x }}</p>
""")
rendered = template.render()
print(rendered)
```

<details>
<summary>Output and Explanation</summary>

Output:

```html
  <p>Value of x: 10</p>
    <p>x inside the loop: 10</p>
    <p>x inside the loop: 11</p>
    <p>x inside the loop: 12</p>
    <p>x inside the loop: 13</p>
    <p>x inside the loop: 14</p>
  <p>Value of x after loop: 10</p>
```

In this example, the variable `x` is defined in the template scope with an initial value of `10`. Inside the loop, we attempt to set `x` to `x + i` for each iteration. However the `set x = x + i` statement inside the loop only creates a new variable `x` that exists inside that one iteration: every iteration starts again from the outer `x` (still `10`), so the loop prints `10, 11, 12, 13, 14` instead of accumulating `10, 11, 13, 16, 20`. It does not modify the outer variable `x` either. Therefore, after the loop, `x` still retains its original value of `10`. (Use a `namespace` to really accumulate a value.)

</details>

### Sharing variables between templates

Variables set at the **top level** of a template are also visible to other templates:

- **`include`** gets the current scope, so the included template sees the variables we `set` (and the loop variable when included inside a loop).
- **`import`** / **`from ... import`** exposes the top-level `set` variables (and macros) of the imported template as `module.name`; names that start with an underscore (`_private`) are not exported.
- A **child template** (`extends`) can `set` a variable at its top level, outside the blocks, and both the base layout and the child's blocks can use it. A `set` made **inside** a `{% block %}` is local to that block.

```python
from jinja2 import Environment, DictLoader

env = Environment(loader=DictLoader({
    "base.html": "<title>{{ title }}</title>\n{% block content %}{% endblock %}",
    "home.html": '{% extends "base.html" %}\n{% set title = "Home" %}\n{% block content %}<h1>{{ title }}</h1>{% endblock %}',
}))
print(env.get_template("home.html").render())
```

Output:

```html
<title>Home</title>
<h1>Home</h1>
```

### Macros (Reusable Blocks)

Jinja2 macros are similar to functions in programming languages. They allow us to define reusable blocks of code that can accept parameters.

- A macro returns its rendered body as a string (marked as safe, so it is not escaped a second time when autoescaping is on).
- Macros can be defined in the same template or imported from other templates.
- Macros may include **parameters** with default values.

```jinja
{% macro macro_name(param1, param2="default") %}
   Macro body using {{ param1 }} and {{ param2 }}
{% endmacro %}

{# now the macro can be called in the template: #}
{{ macro_name("value1", "value2") }}
```

**Example #9**

```python
from jinja2 import Template
template = Template("""
{% macro render_input(name, type="text") %}
  <input type="{{ type }}" name="{{ name }}" />
{% endmacro %}

{{ render_input("username") }}
{{ render_input("password", type="password") }}
""")
print(template.render())
```

Output:

```html
  <input type="text" name="username" />
  <input type="password" name="password" />
```

#### Importing Macros

We can import macros from other templates using `import` or `from ... import` statements. (This needs a template loader, like the inheritance examples below.)

```jinja
{% import "forms.html" as forms %}
{{ forms.render_input("username") }}

{% from "forms.html" import render_input %}
{{ render_input("email") }}
```

> [!NOTE]
> Imported templates do **not** get the variables of the importing template by default (unlike `include`). Write `{% from "forms.html" import render_input with context %}` if a macro needs them.

<details>
<summary><b>Try it yourself</b></summary>

copy the following code and paste it into a python file, then run it to see the output

```python
from jinja2 import Template
template = Template("""
  {% set greeting = "Hello" %}
  {% macro greet_user(name) %}
    <h1>{{ greeting }}, {{ name }}!</h1>
  {% endmacro %}  

  {{ greet_user("Alice") }}
  {{ greet_user("Bob") }}
""")
rendered = template.render()
print(rendered)
```

</details>

### Different Blocks and their scopes

| Construct   | What it does                                            |
| ----------- | ------------------------------------------------------- |
| `set`       | Assigns variable in the current scope (`if` does not open a new one) |
| `with`      | Creates a new limited scope                             |
| `namespace` | Provides a mutable object that bypasses scope isolation |
| `macro`     | Defines a reusable block that can accept parameters     |

## Escaping, Autoescaping and Whitespace Control

### Escaping Jinja2 syntax

Escape Jinja2 syntax using `{% raw %}` ... `{% endraw %}` to prevent evaluation.

Example:

```jinja
{% raw %}
   {{ this will not be evaluated 2+3 }}
{% endraw %}
```

Output:

```txt
   {{ this will not be evaluated 2+3 }}
```

### Autoescaping (HTML safety)

When a variable is printed into HTML, characters like `<` and `&` must be escaped (`&lt;`, `&amp;`), otherwise a user can inject a `<script>` (XSS). Jinja2 can do this automatically, **but it is switched off by default** in a plain `Template` / `Environment`:

```python
from jinja2 import Template
comment = "<script>alert('hi')</script>"
print(Template("{{ comment }}").render(comment=comment))
print(Template("{{ comment }}", autoescape=True).render(comment=comment))
print(Template("{{ comment|e }} | {{ comment|safe }}", autoescape=True).render(comment=comment))
```

Output:

```txt
<script>alert('hi')</script>
&lt;script&gt;alert(&#39;hi&#39;)&lt;/script&gt;
&lt;script&gt;alert(&#39;hi&#39;)&lt;/script&gt; | <script>alert('hi')</script>
```

- **Flask turns autoescaping on** for templates ending in `.html`, `.htm`, `.xml` and `.xhtml` and for `render_template_string`, so `{{ comment }}` is safe there.
- `|e` escapes a value explicitly; `|safe` marks a value as already safe, so use it only for content we trust.
- Accessing an attribute of a missing variable (`{{ user.name }}` with no `user`) raises `UndefinedError`, while printing a missing variable (`{{ user }}`) gives an empty string.

> [!CAUTION]
> **Never render template text written by users with a normal Jinja2 environment** (for example Flask's `render_template_string(user_text)`). A template like `{{ ''.__class__.__mro__ }}` can walk from a harmless string to dangerous Python objects (server-side template injection). Pass user input as **data** to a template we wrote, or use `jinja2.sandbox.SandboxedEnvironment`, which raises a `SecurityError` for such expressions.

### Whitespace Control

Jinja2 provides options to control whitespace around tags using `-` (dash) character: a dash on the left (`{%-`, `{{-`) removes the whitespace **before** the tag, a dash on the right (`-%}`, `-}}`) removes the whitespace **after** it.

```jinja
{{- variable -}}
{%- if condition -%}
   Block of code
{%- endif -%}
```

#### Try it yourself

```python
from jinja2 import Template
template = Template("""
  {%- if user %}
    <h1>Welcome, {{ user.name }}!</h1>
  {%- else %}
    <h1>Please log in.</h1>
  {%- endif %}
""")
rendered = template.render(user={"name": "Alice"})
print(rendered)
```

This example only has dashes on the left side, so it trims the whitespace **before** each tag (the line breaks and indentation in front of `{%- if`, `{%- else` and `{%- endif`) but not the whitespace after them. Add `-%}` to trim after a tag as well.

## Template Inheritance (`extends` + `block`)

Jinja2 supports template inheritance, allowing we to create a base template and extend it in child templates. This promotes code reuse and consistent layouts. 

> [!NOTE]
> `extends`, `include` and `import` need a template **loader** that can find the other templates. A plain `Template(...)` has none and fails with `TypeError: no loader for this environment specified`. The examples below use `Environment(loader=DictLoader({...}))` so that they run as plain Python; in Flask (later sections) the templates are loaded from files in the `templates` folder.

### Base Template

```html+jinja
<!DOCTYPE html>
<html>
<head>
   <title>{% block title %}Default Title{% endblock %}</title> 
</head>
<body>
   <header>
      <h1>Site Header</h1>
   </header>
    <main>
        {% block content %}
        <p>Default content goes here.</p>
        {% endblock %}
    </main>
    <footer>
      <p>Site Footer</p>
    </footer>
</body>
</html>
```

### Child Template

```html+jinja
{% extends "base.html" %}

{% block title %}Custom Page Title{% endblock %}

{% block content %}
   <p>This is custom content for the page.</p>
{% endblock %}
```

### python rendering

```python
from jinja2 import Environment, DictLoader

base_template = """<!DOCTYPE html>
<html>
<head>
   <title>{% block title %}Default Title{% endblock %}</title> 
</head>
<body>
   <header>
      <h1>Site Header</h1>
   </header>
    <main>
        {% block content %}
        <p>Default content goes here.</p>
        {% endblock %}
    </main>
    <footer>
      <p>Site Footer</p>
    </footer>
</body>
</html>
"""

child_template = """{% extends "base.html" %}

{% block title %}Custom Page Title{% endblock %}

{% block content %}
   <p>This is custom content for the page.</p>
{% endblock %}
"""

env = Environment(loader=DictLoader({"base.html": base_template, "child.html": child_template}))
print(env.get_template("child.html").render())
```

Output:

```html
<!DOCTYPE html>
<html>
<head>
   <title>Custom Page Title</title> 
</head>
<body>
   <header>
      <h1>Site Header</h1>
   </header>
    <main>
        <p>This is custom content for the page.</p>
    </main>
    <footer>
      <p>Site Footer</p>
    </footer>
</body>
</html>
```

Explanation: When a child template is rendered, Jinja2 first resolves the template inheritance chain defined by the extends statements. It collects all block definitions from the base and child templates, determines which blocks override others, and builds a single final template structure. This resolved template is then rendered to produce the final output.

### Using `super()`

We can use `super()` to call the content of the parent block within an overridden block. The parent's content appears exactly where `{{ super() }}` is written.

#### Child Template

```html+jinja
{% extends "base.html" %}
{% block title %}Custom Page Title{% endblock %}
{% block content %}
   {{ super() }}
   <p>This is additional content for the page.</p>
{% endblock %}
```

Here `{{ super() }}` comes first, so the base content is rendered before the additional paragraph.

#### Try it yourself

copy the following code and paste it into a python file, then run it to see the output

```python
from jinja2 import Environment, DictLoader

base_template = """
<!DOCTYPE html>
<html>
<head> 
    <title>{% block title %}Default Title{% endblock %}</title>
</head>
<body>
    <header>
        <h1>Site Header</h1>
    </header>
    <main>
        {% block content %}
        <p>Default content goes here.</p>
        {% endblock %}
    </main>
    <footer>
        <p>Site Footer</p>
    </footer>
</body>
</html>
"""

child_template = """
{% extends "base.html" %}
{% block title %}Custom Page Title{% endblock %}
{% block content %}
   {{ super() }}
   <p>This is additional content for the page.</p>
{% endblock %}
"""

env = Environment(loader=DictLoader({"base.html": base_template, "child.html": child_template}))
print(env.get_template("child.html").render())
```

Output:

```html
<!DOCTYPE html>
<html>
<head> 
    <title>Custom Page Title</title>
</head>
<body>
    <header>
        <h1>Site Header</h1>
    </header>
    <main>
        <p>Default content goes here.</p>
        <p>This is additional content for the page.</p>
    </main>
    <footer>
        <p>Site Footer</p>
    </footer>
</body>
</html>
```

## Includes

Jinja2 allows including reusable template fragments using the `include` statement. This is useful for components like headers, footers, or navigation bars that are shared across multiple templates.
```jinja
{% include "header.html" %}
```

### With Context vs Without Context

By default, included templates have access to the context of the parent template. However, we can use `with context` or `without context` to control this behavior.

- `with context`: The included template has access to the parent template's context (default behavior).
- `without context`: The included template does not have access to the parent template's context.

```jinja
{% include "header.html" with context %}
{% include "footer.html" without context %}
```

#### Example

```python
from jinja2 import Environment, DictLoader

header = """<header>
  <h1>{{ title }}</h1>
</header>"""

footer = """<footer>
  <p>&copy; {{ year }}</p>
</footer>"""

env = Environment(loader=DictLoader({"header.html": header, "footer.html": footer}))
template = env.from_string("""
  {% include "header.html" with context %}
  <p>Main content goes here.</p>
  {% include "footer.html" without context %}
""")
print(template.render(title="My Page", year=2024))
```

Output (`year` is not visible inside the footer, so it prints nothing):

```html
  <header>
  <h1>My Page</h1>
</header>
  <p>Main content goes here.</p>
  <footer>
  <p>&copy; </p>
</footer>
```

Header.html:

```html+jinja
<header>
  <h1>{{ title }}</h1>
</header>
```

Footer.html:

```html+jinja
<footer>
  <p>&copy; {{ year }}</p>
</footer>
```

## Filters

Filters in Jinja2 are used to modify the output of variables. They are applied using the pipe (`|`) symbol.

### Commonly Used Filters

- `lower`: Converts a string to lowercase.
- `upper`: Converts a string to uppercase.
- `title`: Converts a string to title case.
- `length`: Returns the length of a string, list, or dictionary.
- `default`: Provides a default value if the variable is **undefined**. `{{ x | default("none") }}` keeps `0`, `""` and `False`; use `default("none", true)` to replace every false value as well.
- `join`: Joins a list into a string with a specified separator.
- `replace`: Replaces occurrences of a substring with another substring.
- **`groupby`: Groups a list of objects by a specified attribute.** 

### Example

```python
from jinja2 import Template
template = Template("""
  <p>{{ name | upper }}</p>
  <p>{{ items | length }}</p>
  <p>{{ description | default("No description available.") }}</p>
""")
rendered = template.render(name="Alice", items=["apple", "banana"])
print(rendered)
```

Output:

```html
  <p>ALICE</p>
  <p>2</p>
  <p>No description available.</p>
```

### Groupby Filter

The `groupby` filter in Jinja2 is used to group a list of objects based on a specified attribute. This is particularly useful when we want to organize data into categories or sections. The groups come out **sorted by the grouping key**. We can group items by an attribute and then iterate over each group to display the grouped data. Fetching grouped data can be done in two ways:

- Using two loop variables: one for the group key and another for the list of items in that group.
- Using a single loop variable that contains both the group key and the list of items, through the `grouper` and `list` attributes.

Example:

```python
from jinja2 import Template
template1 = Template("""
  {% for category, items in products | groupby('category') %}
    <h2>{{ category }}</h2>
    <ul>
    {% for item in items %}
      <li>{{ item.name }} - ${{ item.price }}</li> 
    {% endfor %}
    </ul>
  {% endfor %}
""")

# Alternative syntax using item.grouper and item.list from a single groupby variable 'item'

template2 = Template("""
  {% for item in products | groupby('category') %}
    <h2>{{ item.grouper }}</h2>
    <ul>
    {% for product in item.list %}
      <li>{{ product.name }} - ${{ product.price }}</li> 
    {% endfor %}
    </ul>
  {% endfor %}
""")
products = [
    {"name": "Apple", "category": "Fruits", "price": 1.00},
    {"name": "Banana", "category": "Fruits", "price": 0.50},
    {"name": "Carrot", "category": "Vegetables", "price": 0.30},
    {"name": "Broccoli", "category": "Vegetables", "price": 0.80},
]
output1 = template1.render(products=products)
output2 = template2.render(products=products)
print(output1)
print(output2)
```

Output:

```html
  <h2>Fruits</h2>
  <ul>
    <li>Apple - $1.0</li> 
    <li>Banana - $0.5</li> 
  </ul>
  <h2>Vegetables</h2>
  <ul>
    <li>Carrot - $0.3</li> 
    <li>Broccoli - $0.8</li> 
  </ul>

  <h2>Fruits</h2>
  <ul>
    <li>Apple - $1.0</li> 
    <li>Banana - $0.5</li> 
  </ul>
  <h2>Vegetables</h2>
  <ul>
    <li>Carrot - $0.3</li> 
    <li>Broccoli - $0.8</li> 
  </ul>
```

<details>
<summary><b>Try it yourself</b></summary>

copy the following code and paste it into a python file, then run it to see the output

```python
from jinja2 import Template
template = Template("""
  {% for department, employees in staff | groupby('department') %}
    <h2>{{ department | upper }}</h2>
    <ul>
    {% for employee in employees %}
      <li>{{ employee.name }} - {{ employee.role }}</li> 
    {% endfor %}
    </ul>
  {% endfor %}
""")
staff = [
    {"name": "Alice", "department": "HR", "role": "Manager"},
    {"name": "Bob", "department": "IT", "role": "Developer"},
    {"name": "Charlie", "department": "HR", "role": "Recruiter"},
    {"name": "David", "department": "IT", "role": "SysAdmin"},
]
rendered = template.render(staff=staff)
print(rendered)
```

</details>

## Comparison Tables

### Template Inheritance vs Includes

| Feature                 | Template Inheritance (`extends` + `block`) | Includes (`include`)                     |
|-------------------------|--------------------------------------------|------------------------------------------|
| Purpose                 | Create base layouts and override sections  | Reuse template fragments/components      |
| Structure               | Hierarchical (base and child templates)    | Flat (independent fragments)              |
| Context Access          | Full context access                        | Can choose `with context` or `without context` |
| Use Case                | Consistent layouts across multiple pages   | Reusable components like headers, footers, navbars |
| Complexity              | More complex due to inheritance hierarchy  | Simpler, just includes fragments         |

### Macros vs Includes

| Feature                 | Macros                                    | Includes                                 |
|-------------------------|-------------------------------------------|------------------------------------------|
| Purpose                 | Define reusable function-like snippets    | Reuse template fragments/components      |
| Parameters              | Accept parameters                         | No parameters (uses the surrounding context) |
| Return Value            | Return rendered content                   | Include entire fragment                  |
| Use Case                | Reusable form elements, widgets           | Headers, footers, navbars                |
| Complexity              | More complex due to parameterization      | Simpler, just includes fragments         |

### Jinja2 vs string.Template vs Python Built-in Formatting

| Feature | Jinja2 | string.Template | Python Built-in Formatting |
|---------|--------|-----------------|----------------------------|
| Purpose | Full-featured templating engine | Simple string substitution | String formatting |
| Syntax | `{{ }}`, `{% %}`, `{# #}` | `$variable`, `${variable}` | `f-strings`, `str.format()`, `%-formatting` |
| Control Structures | Yes (if, for, macros) | No | No |
| Template Inheritance | Yes | No | No |
| Reusable Components | Yes (macros, includes) | No | No |
| Escaping & Safety | Optional: autoescaping (off by default, on in Flask for HTML templates) and `SandboxedEnvironment` for untrusted templates | No escaping; user-written templates can only read the values passed in | No |
| Complexity | More complex, powerful | Simple, limited | Moderate |
| formatting capabilities | Advanced (filters, custom functions) | Substitution | very precise and flexible formatting |
| Use Case | Web applications, complex documents | Simple string substitutions | General-purpose string formatting |

## Summary

In this guide, we have explored the key features of Jinja2, a powerful templating engine for Python. We covered variable interpolation, control structures, template inheritance, includes, macros, filters, and more. Jinja2 provides a robust way to separate application logic from presentation logic, making it easier to manage and maintain code in web applications. In future sections, we will explore how to integrate Jinja2 with web frameworks like Flask to build dynamic web applications. Here's a quick summary of the main features covered:

- `extends` → Base layouts with `block`s
- `include` → Reusable fragments (`with context` / `without context`)
- `set` → Variables (current scope; top-level ones are shared with `include` / `import` / base templates)
- `with` → Variables (block scope, e.g., flash messages)
- `macro` → Reusable function-like snippets
- `filters` → Modify data output
- autoescaping (`|e`, `|safe`) → Protect HTML output from injected markup

### Further Reading

- [Jinja2 Official Documentation](https://jinja.palletsprojects.com/)
- [Jinja2 Filter Reference](https://jinja.palletsprojects.com/en/latest/templates/#builtin-filters)
- [Jinja2 Template Inheritance](https://jinja.palletsprojects.com/en/latest/templates/#template-inheritance)
- [Jinja2 Extensions](https://jinja.palletsprojects.com/en/latest/extensions/)
