# Pyhtml and System Integration

In this section, we will briefly cover two small but practical topics:

- accessing command-line input using the `sys` module, and
- generating simple HTML output using the `pyhtml` library.

## Sys Module

The `sys` module in Python provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter. We will only cover a few important aspects of the `sys` module here.

- `sys.argv`: A list of command-line arguments passed to a Python file. The first element is the file name.
- `sys.exit([arg])`: Exit from Python. This function can take an optional argument to specify the exit status.
- `sys.version`: A string containing the version of the Python interpreter.
- `sys.platform`: A string that identifies the platform on which Python is running.

### sys.argv

The `sys.argv` list contains the command-line arguments passed to the file. The first element, `sys.argv[0]`, is the name of the file itself. The subsequent elements are the arguments passed to the file.

Here is an example of how to use `sys.argv` to print the file name and its arguments:

```python
import sys
print("file name:", sys.argv[0])
```

If you run the file with arguments like this:

```bash
python myfile.py arg1 arg2
```

The output will be:

```txt
file name: myfile.py
```

We can also print the entire `sys.argv` list:

```python
import sys
print(sys.argv)
```

If you run the file with arguments like this:

```bash
python myfile.py argument1 argument2 "complex argument 3"
```

The output will be:

```txt
['myfile.py', 'argument1', 'argument2', 'complex argument 3']
```

See the image below for a visual representation of `sys.argv` for the above command:

![sys-argv](./static/sys-argv.png)

:::info

- The first element of `sys.argv` is always the file name.
- If no arguments are passed, `sys.argv` will contain only one element, the file name.
- Arguments are space-separated strings but we can enclose them in quotes to include spaces in arguments or name of the file.

:::

## Pyhtml Library

The `pyhtml` library is a simple and lightweight library for generating HTML in Python. It allows you to create HTML elements using Python syntax. Pyhtml uses functions to represent HTML tags.

### Installation

To install the `pyhtml` library, you can use pip:

```bash
pip install pyhtml
```

### Basic Usage

Here is a simple example of how to use the `pyhtml` library to create an HTML document:

```python
from pyhtml import html, head, title, body, h1, p
doc = html(
    head(
        title("My First Pyhtml Page")
    ),
    body(
        h1("Hello, Pyhtml!"),
        p("This is a paragraph generated using the pyhtml library.")
    )
)
print(doc)
```

This will generate the following HTML output:

```html
<html>
  <head>
    <title>My First Pyhtml Page</title>
  </head>
  <body>
    <h1>Hello, Pyhtml!</h1>
    <p>This is a paragraph generated using the pyhtml library.</p>
  </body>
</html>
```

Here we used the `html`, `head`, `body`, `h1`, and `p` functions from the `pyhtml` library to create an HTML document structure. The base element is `html`, which contains the `head` and `body` elements. Inside the `head`, we added a `title`, and inside the `body`, we added a heading (`h1`) and a paragraph (`p`). We can follow this structure to create more complex HTML documents.

### Creating Nested HTML Structures using Pyhtml

You can create more complex HTML structures by nesting elements. Here is an example:

```python
from pyhtml import html, head, title, body, h1, p, ul, li
doc = html(
    head(
        title("My Complex Pyhtml Page")
    ),
    body(
        h1("Welcome to My Page"),
        p("Here is a list of my favorite fruits:"),
        ul(
            li("Apple"),
            li("Banana"),
            li("Cherry")
        )
    )
)
print(doc)
```

This will generate the following HTML output:

```html
<html>
  <head>
    <title>My Complex Pyhtml Page</title>
  </head>
  <body>
    <h1>Welcome to My Page</h1>
    <p>Here is a list of my favorite fruits:</p>
    <ul>
      <li>Apple</li>
      <li>Banana</li>
      <li>Cherry</li>
    </ul>
  </body>
</html>
```

:::tip

**Try it yourself!**

```python
from pyhtml import html, head, title, body, h1, p, ul, li
doc = html(
    head(
        title("My first Pyhtml Page")
    ),
    body(
        h1("Welcome to My Page"),
        p("Here is a list of my favourite cars"),
        ul(
            li("BMW"),
            li("Audi"),
            li("Mercedes")
        )
    )
)
print(doc)
```

## Attribute Handling in Pyhtml

In `pyhtml`, you can also add attributes to HTML elements. To add attributes, you can pass them as keyword arguments to the functions representing the HTML tags. These attributes need not to a valid attribute in html we can provide any key-value pair and pyhtml will create an attribute out of that pair. For example:

```python
from pyhtml import html, head, title, body, h1, p
doc = html(
    head(
        title("My Pyhtml Page with Attributes")
    ),
    body(
        h1("Hello, Pyhtml!", style="color: blue;"),
        p("This is a paragraph with a class and custom attribute.", class_="my-paragraph", gender="female")
    )
)
print(doc)
```

This will generate the following HTML output:

```html
<html>
    <head>
        <title>My Pyhtml Page with Attributes</title>
    </head>
    <body>
        <h1 style="color: blue;">Hello, Pyhtml!</h1>
        <p class="my-paragraph" gender="female">This is a paragraph with a class and a custom attribute.</p>
    </body>
</html>
```

Here we added a `style` attribute to the `h1` element and `class` and a custom `gender` attribute to the `p` element. Note that since `class` is a reserved keyword in Python, we used `class_` instead.

### Comparison between pyhtml and jinja2

| Feature               | pyhtml                                      | jinja2                                    |
|-----------------------|---------------------------------------------|-------------------------------------------|
| Syntax                | Python function calls                       | Template syntax with delimiters           |
| Learning Curve        | Easier for Python developers                | Requires learning template syntax         |
| Use Case              | Simple HTML generation                      | Complex templating with logic             |
| Integration           | Standalone HTML generation                  | Integrates with web frameworks like Flask |
| Flexibility           | Limited to HTML generation                  | Highly flexible with control structures   |
| Community Support     | Smaller community                           | Large and active community                 |
| Documentation         | Basic documentation available               | Extensive documentation and tutorials     |
| Popularity            | Less popular                               | Widely used in web development             |
| Use in Web Frameworks | Less commonly used                          | Commonly used in frameworks like Flask |

## Summary

In this section, we explored the `sys` module in Python, focusing on `sys.argv` for command-line argument handling. We also introduced the `pyhtml` library for generating HTML using Python syntax, demonstrating its basic usage and how to create nested HTML structures. Finally, we compared `pyhtml` with the popular templating engine `jinja2`, highlighting their differences in syntax, use cases, and community support.

:::info

**Check the following links for more details:**

- [sys module documentation](https://docs.python.org/3/library/sys.html)
- [pyhtml documentation](https://pypi.org/project/pyhtml/)
- [jinja2](./jinja2.md)
