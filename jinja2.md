# Jinja2 Guide <a name="jinja2-guide"></a>

:::info
This guide is designed as a compact reference to Jinja2 syntax and features.
You can read it linearly or jump directly to a section when you need a refresher.
:::

<div v-pre>

In previous sections, we have discussed about `string.Template` and Python's built-in formatting methods like `f-strings`, `str.format()`, and `%-formatting`. These methods are great for simple string interpolation, but when it comes to generating complex HTML or text documents with appropriate safety measures, a more powerful templating engine is often needed.

## Why Jinja2?

**Jinja2** is a full-featured templating engine for Python that is widely used in web frameworks like **Flask**. It provides a robust way to separate application logic from presentation logic, making it easier to manage and maintain code.

### Key Features of Jinja2

- Allows limited expression evaluation.
- If configured correctly, restricts what templates can access (sandboxing).
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
- **If data is missing, Jinja2 outputs an empty string by default (can be configured).**
- **If any argument is passed extra to `render()`, it will be ignored if not used in the template.**

---

## Variable Printing or Interpolation

We can use double curly braces to access variables, object attributes, list items and evaluate a limited set of python like expressions like arithmetic, logical operations etc.

 :::info
Jinja2 has its own expression syntax which is similar to Python but not exactly the same. For example, Jinja2 uses `and`, `or`, `not`. But it is important to note that not all Python expressions are supported in Jinja2 templates.
 :::

### syntax

```html
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

:::tip

### Try it yourself

copy the following code and paste it into a python file, then run it to see the output

``` python
from jinja2 import Template
template = Template("""
  <h2>Hello, {{ customer.first_name }} {{ customer.last_name }}!</h2>
  <p>Your order total is: ${{ item_price * item_quantity }}</p>
""")
rendered = template.render(customer={"first_name": "John", "last_name": "Doe"}, item_price=15.50, item_quantity=2)
print(rendered)
```

:::

---

## Comments

We can add comments in Jinja2 templates using `{# ... #}` syntax. Comments are ignored during rendering.

```html
{# This is a comment #}
```

:::warning
Do not confuse Jinja2 comments with HTML comments (`<!-- ... -->`). Jinja2 comments are not included in the output rendered by jinja2, while HTML comments are. Many times we may try to comment out jinja2 code using HTML comments, but that will not work as expected.
:::

---

## Control Structures

Jinja2 provides control structures like conditionals and loops to add logic to templates. Syntax is similar to Python but uses `{% ... %}` delimiters and requires explicit `endif`, `endfor` statements.

### If / Else

``` python
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

``` python
from jinja2 import Template
template = Template("""
  {% if user == "Alice" %}
    <h1>Hello, {{ user.name }}!</h1>
  {% else %}
    <h1>Please log in.</h1>
  {% endif %}
""")
rendered = template.render(user="Alice")
print(rendered)
```

output:

``` html
  <h1>Hello, Alice!</h1>
```

### For Loops

```html
{% for iterative_variable in iterable %}
  Block of code that can use {{ iterative_variable }}
{% endfor %}
```

example:

``` python
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

:::info

- Jinja2 supports looping over lists, tuples, dictionaries, and ranges.
- we can also use `continue` and `break` statements inside loops.
- Jinja2 has only `for` loops, no `while` loops.

:::

## Scope, Reusable Blocks and Variable Management

Jinja2 provides mechanisms to define and manage variables within templates. This includes setting variables, scoping them, and creating reusable components.

### Set Statement (Global Variables)

We can define variables using the `set` statement. Variables defined with `set` are available in the entire template after their declaration.

```html
{% set variable = value %}
```

Example:

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

### With Statement (Scoped Variables)

```html
{% with x = 5 %}
   <p>{{ x }}</p>
{% endwith %}

<p>{{ x }}</p>  {# undefined here #}
```

**Note**: undefined variables are rendered as empty strings by default.

Like `set`, but limited to block scope.

Example:

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

Output:

```html
  <p>Discount: $10.0</p>
  <p>Discount outside block: $</p>  {# undefined here #}
```

### Macros (Reusable Blocks)

Jinja2 macros are similar to functions in programming languages. They allow us to define reusable blocks of code that can accept parameters.

- Macros return the entire block enclosed within them.
- Macros can be defined in the same template or imported from other templates.
- Macros may include parameters with default values.

```html
{% macro macro_name(param1, param2="default") %}
   Macro body using {{ param1 }} and {{ param2 }}
{% endmacro %}

{{# now macro_name("value1", "value2") is a macro that can be called in templates #}}
```

Example:

```html
{% macro render_input(name, type="text") %}
  <input type="{{ type }}" name="{{ name }}" />
{% endmacro %}

{{ render_input("username") }}
{{ render_input("password", type="password") }}
```

Output:

```html
  <input type="text" name="username" />
  <input type="password" name="password" />
```

#### Importing Macros

We can import macros from other templates using `import` or `from ... import` statements.

```html
{% import "forms.html" as forms %}
{{ forms.render_input("username") }}

{% from "forms.html" import render_input %}
{{ render_input("email") }}
```

:::tip

### Try it yourself

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

:::

## Escaping and Whitespace Control

### Escaping

Escape Jinja2 syntax using `{% raw %}` ... `{% endraw %}` to prevent evaluation.

Example:

```html
{% raw %}
   {{ this will not be evaluated 2+3 }}
{% endraw %}
```

Output:

```html
   {{ this will not be evaluated 2+3 }}
```

### Whitespace Control

Jinja2 provides options to control whitespace around tags using `-` (dash) character.

```html
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

This trims whitespace before and after the tags.

## Template Inheritance (`extends` + `block`)

Jinja2 supports template inheritance, allowing we to create a base template and extend it in child templates. This promotes code reuse and consistent layouts. 

:::info

The examples below illustrates the syntax and behavior of template inheritance but to use it in practice, we need to use a template loader that can load templates from files. We will see this practically when we integrate Jinja2 with Flask in later sections.
:::

### Base Template

```html
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

```html
{% extends "base.html" %}

{% block title %}Custom Page Title{% endblock %}

{% block content %}
   <p>This is custom content for the page.</p>
{% endblock %}
```

### python rendering

```python
from jinja2 import Template
base_template = open("base.html").read()
child_template = open("child.html").read()
template = Template(child_template)
rendered = template.render()
print(rendered)
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

Explanation:When a child template is rendered, Jinja2 first resolves the template inheritance chain defined by the extends statements. It collects all block definitions from the base and child templates, determines which blocks override others, and builds a single final template structure. This resolved template is then rendered to produce the final output.

### Using `super()`

We can use `super()` to call the content of the parent block within an overridden block.

#### Child Template

```python
{% extends "base.html" %}
{% block title %}Custom Page Title{% endblock %}
{% block content %}
   {{ super() }}
   <p>This is additional content for the page.</p>
{% endblock %}
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

This will prepend the base content block( super()'s output ) to the block content.

:::tip

#### Try it yourself

copy the following code and paste it into a python file, then run it to see the output

```python
from jinja2 import Template
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

child_template = Template("""
{% extends "base.html" %}
{% block title %}Custom Page Title{% endblock %}
{% block content %}
   {{ super() }}
   <p>This is additional content for the page.</p>
{% endblock %}
""")
rendered = child_template.render()
print(rendered)
```

:::

## Includes

Jinja2 allows including reusable template fragments using the `include` statement. This is useful for components like headers, footers, or navigation bars that are shared across multiple templates.
```html
{% include "header.html" %}
```

### With Context vs Without Context

By default, included templates have access to the context of the parent template. However, we can use `with context` or `without context` to control this behavior.

- `with context`: The included template has access to the parent template's context (default behavior).
- `without context`: The included template does not have access to the parent template's context.

```html
{% include "header.html" with context %}
{% include "footer.html" without context %}
```

#### Example

```python
from jinja2 import Template
template = Template("""
  {% include "header.html" with context %}
  <p>Main content goes here.</p>
  {% include "footer.html" without context %}
""")
rendered = template.render(title="My Page", year=2024)
print(rendered)
```

Output:

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

```html
<header>
  <h1>{{ title }}</h1>
</header>
```

Footer.html:

```html
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
- `default`: Provides a default value if the variable is undefined or false.
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

The `groupby` filter in Jinja2 is used to group a list of objects based on a specified attribute. This is particularly useful when we want to organize data into categories or sections. We can group items by an attribute and then iterate over each group to display the grouped data. Fetching grouped data can be done in two ways:

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

:::tip

### Try it yourself

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

:::

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
| Parameters              | Accept parameters                         | No parameters, static inclusion          |
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
| Escaping & Safety | Yes (auto-escaping, sandboxing) | No | No |
| Complexity | More complex, powerful | Simple, limited | Moderate |
| formatting capabilities | Advanced (filters, custom functions) | Substitution | very precise and flexible formatting |
| Use Case | Web applications, complex documents | Simple string substitutions | General-purpose string formatting |

## Summary

In this guide, we have explored the key features of Jinja2, a powerful templating engine for Python. We covered variable interpolation, control structures, template inheritance, includes, macros, filters, and more. Jinja2 provides a robust way to separate application logic from presentation logic, making it easier to manage and maintain code in web applications. In future sections, we will explore how to integrate Jinja2 with web frameworks like Flask to build dynamic web applications. Here's a quick summary of the main features covered:

- `extends` → Base layouts with `block`s
- `include` → Reusable fragments (`with context` / `without context`)
- `set` → Variables (global scope)
- `with` → Variables (block scope, e.g., flash messages)
- `macro` → Reusable function-like snippets
- `filters` → Modify data output

### Further Reading

- [Jinja2 Official Documentation](https://jinja.palletsprojects.com/)
- [Jinja2 Filter Reference](https://jinja.palletsprojects.com/en/latest/templates/#builtin-filters)
- [Jinja2 Template Inheritance](https://jinja.palletsprojects.com/en/latest/templates/#template-inheritance)
- [Jinja2 Extensions](https://jinja.palletsprojects.com/en/latest/extensions/)

</div>
