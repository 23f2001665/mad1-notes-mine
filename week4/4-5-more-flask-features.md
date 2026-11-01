# More Features of Flask

In this module, we will explore some additional features of Flask that enhance its functionality and make it easier to build web applications. We will cover topics such as generating URLs for the resources, creating custom error pages and redirecting users to different routes, etc.

## URL Building with `url_for`

Flask provides a built-in function called `url_for` that allows us to generate URLs for our application routes dynamically. This is particularly useful when we want to create links in the templates or redirect users to different routes without hardcoding the URLs.
Here is an example of how to use `url_for` in a Flask application:

```python
from flask import Flask, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return 'Welcome to the Home Page!'

@app.route('/about')
def about():
    return 'This is the About Page.'

@app.route('/contact')
def contact():
    return 'This is the Contact Page.'

@app.route('/links')
def links():
    home_url = url_for('home')
    about_url = url_for('about')
    contact_url = url_for('contact')
    return f'''
    <a href="{home_url}">Home</a><br>
    <a href="{about_url}">About</a><br>
    <a href="{contact_url}">Contact</a>
    '''

if __name__ == '__main__': 
    app.run(debug=True)
```

In this example, we define three routes: `/`, `/about`, and `/contact`. The `links` route uses the `url_for` function to generate URLs for these routes dynamically. When a user accesses the `/links` route, they will see links to the Home, About, and Contact pages.

### Passing Arguments to `url_for`

We can also pass arguments to the `url_for` function to generate URLs for routes that require parameters. Here is an example:

```python
@app.route('/user/<username>')
def profile(username):
    return f'Profile page of {username}'

@app.route('/user_links')
def user_links():
    user1_url = url_for('profile', username='alice')
    user2_url = url_for('profile', username='bob', age=23)
    return f'''
    <a href="{user1_url}">Alice's Profile</a><br>
    <a href="{user2_url}">Bob's Profile</a>
    '''
```

This will generate the following links:

- Alice's Profile: `/user/alice`
- Bob's Profile: `/user/bob?age=23`
<UrlForVisualizer />

**Note**: The `age` parameter in Bob's profile link is passed as a query parameter since it is not part of the route definition. If a parameter is not defined in the route, it will be added as a query string.

:::info `url_for` with Static Files

To generate links for static files in application, we can use the `url_for` function provided by Flask. This function generates the appropriate URL for the static files. Here is an example of how to include a CSS file in our HTML template:

```python
from flask import Flask, url_for

app = Flask(__name__)

@app.route('/static_example')
def static_example():
    images_link = url_for('static', filename='images/logo.png')
    css_link = url_for('static', filename='styles/main.css')
    return f'''
    <link rel="stylesheet" href="{css_link}">
    <img src="{images_link}" alt="Logo">
    '''

if __name__ == '__main__':
    app.run(debug=True)
```

:::

:::warning

**`url_for` only works within application context**

The `url_for` function requires an application context to work properly. This means that we can only use `url_for` within view functions or when the application context is pushed. If we try to use `url_for` outside of an application context, we will encounter a `RuntimeError`.

For example, the following code will raise an error:

```python
from flask import url_for

# This will raise a RuntimeError
home_url = url_for('home')
```

To avoid this error, make sure to use `url_for` within view functions or use the `app.app_context()` context manager when needed.

:::

:::details Why to use `url_for` instead of hardcoded URLs?

Using `url_for` has several advantages over hardcoding URLs:

1. **Maintainability**: If we change the route of a view function, we only need to update it in one place (the route definition) rather than searching through our code for hardcoded URLs.
2. **Dynamic URL Generation**: `url_for` can generate URLs based on the current application context, making it easier to handle different environments (development, production, etc.).
3. **URL Parameters**: `url_for` allows us to pass parameters to routes easily, making it more flexible for dynamic URL generation.
4. **Avoiding Errors**: Hardcoding URLs can lead to errors if the URL structure changes. Using `url_for` helps prevent broken links in our application.
:::

## app.url_map / flask routes

While `url_for` is used to generate URLs for routes, Flask also provides a way to view all the defined routes in our application using `app.url_map`. This can be useful for debugging and understanding the structure of our application. Here is an example of how to use `app.url_map`:

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Welcome to the Home Page!'

@app.route('/about')
def about():
    return 'This is the About Page.'

@app.route('/contact')
def contact():
    return 'This is the Contact Page.'

if __name__ == '__main__':
    
    print(app.url_map)
    app.run(debug=True)
```

In this example, when we run the application, it will print the URL map to the console, showing all the defined routes and their corresponding endpoints. It will look something like this:

```text
Map([<Rule '/' (HEAD, OPTIONS, GET) -> home>,
 <Rule '/about' (HEAD, OPTIONS, GET) -> about>,
 <Rule '/contact' (HEAD, OPTIONS, GET) -> contact>,
 <Rule '/static/<path:filename>' (HEAD, OPTIONS, GET) -> static>])
```

This output shows the routes defined in the application along with the HTTP methods they support and the endpoint functions they are associated with.

We can also use `flask routes` cli command to see the routes of our application. To use this command, navigate to the directory containing our Flask application and run the following command in our terminal:

```bash
flask routes
```

This command will display a list of all the routes in our Flask application, along with their methods and endpoints.

## Redirecting Requests

Flask provides a convenient way to redirect users to different routes using the `redirect` function. This is useful when we want to guide users to a different page after performing an action, such as submitting a form. Here is an example of how to use the `redirect` function in a Flask application:

```python
from flask import Flask, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return 'Welcome to the Home Page!'

@app.route('/old-page')
def old_page():
    return redirect(url_for('new_page'))

@app.route('/new-page')
def new_page():
    return 'This is the New Page!'

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, when a user accesses the `/old-page` route, they will be redirected to the `/new-page` route using the `redirect` function along with `url_for` to generate the URL for the new page.

When we run this Flask application and navigate to `http://localhost:5000/old-page`, we will be automatically redirected to `http://localhost:5000/new-page`, where we will see the message "This is the New Page!".

:::info

- Though it is very common to use `redirect` along with `url_for`, we can also use it with hardcoded URLs. However, using `url_for` is recommended for the reasons mentioned earlier.
- The `redirect` function sends an HTTP *302* response to the client, indicating that the resource has been *temporarily moved to a different URL*.
- We can also specify different status codes with the `redirect` function, such as *301 for permanent redirects*.

```python
return redirect(url_for('new_page'), code=301)
```

:::

## Error Generation, Handling and Custom Error Pages

Flask allows us to raise HTTP errors using the `abort` function from the `flask` module. This is useful when we want to indicate that a request cannot be fulfilled due to some error condition. This error condition can be **authorization**, **authentication**, **resource not found**, or other client or server errors. Here is an example of how to use the `abort` function in a Flask application:

```python
from flask import Flask, abort

app = Flask(__name__)

@app.route('/resource/<int:resource_id>')
def get_resource(resource_id):
    if resource_id != 1:
        abort(404)  # Resource not found
    return f'Resource {resource_id} found!'

@app.route('/admin/user_list')
def admin_user_list():
    user = ...   # some logic to get current user
    if user.role != 'admin':
        abort(403)  # Forbidden access
    return 'List of users for admin.'

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, when a user tries to access a resource with an ID other than 1, a 404 Not Found error is raised using the `abort` function. Similarly, if a non-admin user tries to access the admin user list, a 403 Forbidden error is raised.

**Note**: The `user` object in the `admin_user_list` function is assumed to be defined elsewhere in our application, representing the currently logged-in user.

We can also create custom error pages for different HTTP error codes by defining error handlers using the `errorhandler` decorator. Here is an example of how to create custom error pages for 404 and 403 errors:

```python
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/resource/<int:resource_id>')
def get_resource(resource_id):
    if resource_id != 1:
        abort(404)  # Resource not found
    return f'Resource {resource_id} found!'

@app.route('/admin/user_list')
def admin_user_list():
    if user.role != 'admin':
        abort(403)  # Forbidden access
    return 'List of users for admin.'

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

if __name__ == '__main__':
    app.run(debug=True)
```

Now when a 404 or 403 error occurs, Flask will render the corresponding custom error page defined in the `404.html` and `403.html` templates.

:::details `abort` [Error Codes](../week1/1-network-history-TCP.md#status-codes)

By default, the `abort` function can raise only a few HTTP status codes which are defined by underlying **Werkzeug** server. Here is a list of a few of those error codes:

- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 405: Method Not Allowed
- 500: Internal Server Error

If we try to `abort(407)` it will throw a **LookupError** instead of a **Proxy Authentication Required** error. The `abort` function can raise only those HTTP status codes that have corresponding `HTTPException` classes in Werkzeug.<br>
While many common HTTP status codes are supported (404, 403, 401, etc.), some valid HTTP codes like 407 (Proxy Authentication Required) do not have a built-in exception class.<br>
Attempting to `abort(407)` therefore raises a LookupError. But if we want to raise custom error codes, we can create a custom exception class that inherits from `HTTPException` and define our own status code.

**We can also return the error code directly from the view function without using `abort`. For example:**

```python
@app.route('/custom-error')
def custom_error():
    return 'Custom Error Occurred', 407  # HTTP 407 Proxy Authentication Required

```

This will return a response with the specified error code without raising a LookupError.
:::

## Flask Cli Commands:

Flask provides a command-line interface (CLI) that allows us to manage our Flask applications easily. Some of the commonly used Flask CLI commands include:

- `flask run`: This command starts the Flask development server.
- `flask shell`: This command opens an interactive Python shell with the Flask application context.
- `flask routes`: This command displays all the routes defined in the Flask application along with their methods and endpoints.

To use the Flask Cli commands, we need to set the `FLASK_APP` environment variable to point to our Flask application file. This can be done by exporting the variable in the terminal:

```bash
export FLASK_APP=app.py
```

or specifying it in the command itself:

```bash
flask --app mydir/app.py run
```

## Summary

In this module, we explored some additional features of Flask that enhance its functionality for building web applications. We learned about URL building using the `url_for` function, which allows us to generate URLs dynamically based on our defined routes. We also saw how to redirect users to different routes using the `redirect` function. Additionally, we covered error generation and handling using the `abort` function and how to create custom error pages for different HTTP error codes.

### Other Flask Features

Flask offers many more features that we can be really useful. Some of these features include:

- **Blueprints**: A way to organize our application into smaller, reusable components.
- **Flask Extensions**: A wide range of extensions are available to add functionality to our Flask applications, such as database integration, authentication, and more.
- **Session Management**: Flask provides built-in support for managing user sessions using secure cookies.
- **Flask CLI**: A command-line interface for managing Flask applications, including running the development server, initializing databases, and more.
- **Testing Support**: Flask includes tools for testing our applications, making it easier to write unit tests and integration tests.

In the next module, we will explore HTML Forms and how to handle user input in Flask applications.

### Additional resources

- [Flask Documentation - URL Building](https://flask.palletsprojects.com/en/2.3.x/quickstart/#url-building)
