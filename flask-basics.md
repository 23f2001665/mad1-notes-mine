# FLASK

**Flask** is a micro web framework written in Python. It's called a "micro" framework because it aims to keep the core simple but extensible. It doesn't make many decisions for you, like which database to use, giving you the flexibility to choose the tools you want. It's an excellent choice for beginners and for building everything from simple websites to complex web applications.

-----

## Your First Flask Application: "Hello, World\!"

The foundation of any Flask project is the application instance. This basic example shows the simplest possible Flask app.

1.  **Installation**: First, you need to install Flask. It's best practice to do this in a virtual environment.

    ```bash
    pip install Flask
    ```

2.  **Application Code**: Create a file named `app.py`.

    ```python
    from flask import Flask

    # Create an instance of the Flask class
    app = Flask(__name__)

    # Define a "route" that maps a URL to a Python function
    @app.route('/')
    def hello_world():
        return 'Hello, World!'

    # This block ensures the server only runs when the script is executed directly
    if __name__ == '__main__':
        app.run(debug=True)
    ```

<!-- end list -->

  * `app = Flask(__name__)`: This line creates the main application object. `__name__` is a special Python variable that gets the name of the current module.
  * `@app.route('/')`: This is a **decorator**. It tells Flask that the function `hello_world()` should be triggered whenever a user visits the root URL (`/`) of your website.
  * `app.run(debug=True)`: This starts a simple development web server. `debug=True` is incredibly useful during development as it automatically reloads the server when you make code changes and provides detailed error pages. **Never use `debug=True` in a production environment.**

To run this app, save the code and execute it from your terminal: `python app.py`. You can then visit `http://127.0.0.1:5000` in your web browser to see the result.

-----

## Core Concepts

These are the fundamental building blocks of a Flask application.

### Routing

Routing is the mechanism that maps URLs to the specific functions that should handle them. You've already seen the basic syntax: `@app.route('/url')`.

You can also create **dynamic routes** by adding variable parts to the URL.

```python
# A dynamic route that accepts a string
@app.route('/user/<username>')
def show_user_profile(username):
    return f'User: {username}'

# A dynamic route that accepts an integer
@app.route('/post/<int:post_id>')
def show_post(post_id):
    # post_id will be an integer, not a string
    return f'Post Number: {post_id}'
```

### Templates

Hardcoding HTML directly in your Python code is messy. Flask uses the powerful **Jinja2** templating engine to render HTML files.

1.  **Folder Structure**: You **must** create a folder named `templates` in the same directory as your `app.py` file. Flask will automatically look for HTML files here.
2.  **`render_template()`**: To use a template, you import the `render_template` function from Flask.

**Example:**

**`app.py`**

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/hello/<name>')
def hello(name):
    # Pass the 'name' variable from Python into the template
    return render_template('hello.html', user_name=name)
```

**`templates/hello.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Greeting</title>
</head>
<body>
    <h1>Hello, {{ user_name }}!</h1>
    <p>This is a message from our Flask template.</p>
</body>
</html>
```

The `{{ ... }}` syntax is part of Jinja2. It's a placeholder that gets replaced by the value of the variable you passed from your Python code.

### The Request Object

To handle incoming data from a user (like a form submission or URL parameters), Flask provides a global `request` object. You must import it first: `from flask import request`.

  * **`request.method`**: A string that tells you the HTTP method used (`'GET'`, `'POST'`, etc.).
  * **`request.form`**: A dictionary-like object containing data from an HTML form submitted via the `POST` method.
  * **`request.args`**: A dictionary-like object containing data from the URL query string (e.g., in `/search?q=flask`, `request.args['q']` would be `'flask'`).

### Static Files

For files like CSS, JavaScript, and images, you should create a folder named `static`. Flask knows to serve files from this directory. To link to them in your templates, use the `url_for()` function.

**`templates/index.html`**

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
```

-----

## A Complete Example: A Simple Greeting Form

This example combines routing, templates, and the request object to create a simple interactive web page.

**Project Structure:**

```
/my_flask_app
├── app.py
├── static/
│   └── css/
│       └── style.css
└── templates/
    ├── index.html
    └── greet.html
```

**`app.py`**

```python
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Route for the home page, which displays the form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the form submission
# We specify it accepts both GET and POST methods
@app.route('/greet', methods=['POST', 'GET'])
def greet():
    if request.method == 'POST':
        # Get the name from the form object
        user_name = request.form['username']
        if user_name: # Check if the user actually entered a name
             return render_template('greet.html', name=user_name)
    # If it's a GET request or the name is empty, redirect back to the home page
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
```

**`templates/index.html`**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Welcome</title>
</head>
<body>
    <h2>What is your name?</h2>
    <form action="/greet" method="POST">
        <input type="text" name="username" placeholder="Enter your name" required>
        <button type="submit">Submit</button>
    </form>
</body>
</html>
```

**`templates/greet.html`**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Hello!</title>
</head>
<body>
    <h1>Hello, {{ name }}!</h1>
    <a href="/">Go back</a>
</body>
</html>
```

This simple application demonstrates the fundamental workflow of a Flask application: receiving a request, processing user input, and rendering a dynamic response using a template.