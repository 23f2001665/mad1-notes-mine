# Request Handling in Flask

In flask, the `request` object is used to handle incoming HTTP requests. It provides various attributes and methods to access data sent by the client, such as form data, query parameters, headers, and files. Here are some commonly used attributes and methods of the `request` object:

- `request.method`: Returns the HTTP method used for the request (e.g., GET, POST).
- `request.args`: A MultiDict containing the query parameters from the URL (for GET requests).
- `request.form`: A MultiDict containing the form data submitted in the body of a POST request.
- `request.headers`: A dictionary-like object containing the headers of the request.
- `request.get_json()`: Parses the JSON data sent in the request body and returns it as a Python dictionary.
- `request.data`: Contains the raw data sent in the request body as a byte string.
- `request.files`: A MultiDict containing the files uploaded in the request.

Now we discuss each of the above attributes and methods in detail with examples.

## request.method

The `request.method` attribute is used to determine the HTTP method used for the incoming request. Common HTTP methods include GET, POST, PUT, DELETE, etc. This is particularly useful when we want to handle different types of requests differently in our Flask routes.

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/example', methods=['GET', 'POST'])
def example():
    if request.method == 'POST':
        return "This is a POST request"
    else:
        return "This is a GET request"
if __name__ == '__main__':
    app.run(debug=True)
```

In this example, the `/example` route can handle both GET and POST requests. Depending on the method used, it returns a different response. This allows us to create routes that can handle multiple types of requests in a single function, particularly useful for forms and APIs.

## request.args

The `request.args` attribute is used to access the query parameters sent in the URL of a GET request. request.args is populated only from the URL query string, regardless of HTTP method. It returns a MultiDict (a dictionary-like object) containing the key-value pairs of the query parameters.

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('q')  # Get the value of the 'q' query parameter
    return f'Search results for: {query}'

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, when a user accesses the URL `/search?q=flask`, the `request.args.get('q')` retrieves the value of the `q` parameter, which is "flask". The response will be "Search results for: flask". This is useful for handling search queries or filtering data based on user input in the URL.

## request.form

The `request.form` attribute is used to access form data submitted in the body of a POST request. It returns a MultiDict containing the key-value pairs of the form fields. The single value fields can be accessed using the `get` method or `[]` operator.

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')  # Get the value of the 'name' form field
    email = request.form.get('email')  # Get the value of the 'email' form field
    return f'Submitted Name: {name}, Email: {email}'

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, when a user submits a form to the `/submit` route with fields `name` and `email`, the `request.form.get('name')` and `request.form.get('email')` retrieve the values of those fields. The response will display the submitted name and email. This is commonly used for processing form submissions in web applications.

## MultiDict Object and Accessing Multiple Values

The `request.args` and `request.form` attributes return a MultiDict object, which allows us to access multiple values for the same key. This is particularly useful when dealing with form fields that can have multiple selections, such as checkboxes or multi-select dropdowns. 

::: warning When accessing a key normally (using get() or []), Flask returns only the first value associated with that key, even if multiple values exist. We can access all values using the `getlist` method. 

We can also convert the MultiDict to a standard dictionary using to_dict(flat=False).
For low-level inspection, we may read the raw request body using request.stream.read().
Though the recommended way is to use `getlist` method to access multiple values for a key.
:::
::: tabs

== python code

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/multi', methods=['GET', 'POST'])
def multi():
    if request.method == 'POST':
        data = request.form.to_dict(flat=False)  # Get all form data as a dictionary with lists of values
        print(data) # For demonstration, print the data to console

        fruits = request.form.getlist('fruits')  # Get all selected values for 'fruits' field
        username = request.form.get('username')  # Get single value field 'username'

        return str(data)  # Return form data as string for demonstration
    
    # return a simple HTML form with multiple selection options on get request
    return '''
        <form method="POST">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username"><br><br>

            <label>Select your favorite fruits:</label><br>
            <input type="checkbox" name="fruits" value="apple"> Apple<br>
            <input type="checkbox" name="fruits" value="banana"> Banana<br>
            <input type="checkbox" name="fruits" value="cherry"> Cherry<br>
            <input type="submit" value="Submit">
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
```

== terminal output

When the form is submitted with multiple fruits selected, the mentioned code will print the data on terminal which will look similar to this:

```bash
{'username': ['john_doe'], 'fruits': ['apple', 'cherry']}
```

== browser output

When the form is submitted with multiple fruits selected, the browser will display the following output:

```html
{'username': ['john_doe'], 'fruits': ['apple', 'cherry']}
```

:::

In this example, when the form is submitted, `request.form.to_dict(flat=False)` retrieves all form data as a dictionary where each key maps to a list of values. The `request.form.getlist('fruits')` method retrieves all selected values for the `fruits` field, allowing us to handle multiple selections effectively. The `username` field is accessed normally since it is a single value field.

## request.headers

The `request.headers` attribute is used to access the headers of the incoming request. It returns a dictionary-like object containing the headers, which can be accessed using standard dictionary methods.

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/headers')
def headers():
    user_agent = request.headers.get('User-Agent')  # Get the User-Agent header
    return f'User-Agent: {user_agent}'

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, when a user accesses the `/headers` route, the `request.headers.get('User-Agent')` retrieves the value of the `User-Agent` header from the request. The response will display the User-Agent string, which provides information about the client's browser and operating system. This is useful for customizing responses based on client characteristics.

## request.get_json()

The `request.get_json()` method is used to parse JSON data sent in the request body. It returns the parsed JSON data as a Python dictionary. This is particularly useful for handling API requests where data is often sent in JSON format.

```python
from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/json', methods=['POST'])
def json_example():
    data = request.get_json(silent=True) or {} # empty dict to avoid None.get -> AttributeError
    name = data.get('name')  # Get the 'name' field from the JSON
    age = data.get('age')    # Get the 'age' field from the JSON
    return f'Name: {name}, Age: {age}'
    
if __name__ == '__main__':
    app.run(debug=True)
```

In this example, when a user sends a POST request to the `/json` route with JSON data in the body, the `request.get_json()` method parses the JSON and returns it as a Python dictionary. The `name` and `age` fields are then accessed from the dictionary and included in the response. This is essential for building RESTful APIs that communicate using JSON.

:::info `request.get_json()` 
works only when the request’s Content-Type is set to application/json. If the Content-Type is different or the JSON is malformed, it will raise an error. To avoid this, we can use the silent=True parameter, which returns None instead of raising an error for invalid JSON.
:::

## request.data

The `request.data` attribute contains the raw data sent in the request body as a byte string. This is useful when we need to access the raw payload of the request, especially for non-form data or when dealing with custom content types.

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/raw', methods=['POST'])
def raw_data():
    raw_data = request.data  # Get the raw data from the request body
    return f'Raw Data: {raw_data.decode("utf-8")}'  # Decode byte string to UTF-8 for display

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, when a user sends a POST request to the `/raw` route with raw data in the body, the `request.data` retrieves the raw byte string. The byte string is then decoded to UTF-8 for display in the response. This is useful for handling custom payloads or binary data in requests.

:::info

In most applications, we should prefer `request.form` or `request.get_json()` over `request.data`.

:::

## request.files

The `request.files` attribute is used to access files uploaded in the request. It returns a MultiDict containing the uploaded files, which can be accessed using the file field names.

```python
from flask import Flask, request
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        data_fields = request.form.to_dict(flat=False)  # Get all text-based fields as a dictionary
        files = request.files  # Get uploaded files
        os.makedirs('uploads', exist_ok=True)  # Create uploads directory if it doesn't exist
        for file_key in files:
            file = files[file_key]
            file.save(os.path.join('uploads', secure_filename(file.filename)))  # Save uploaded files
        return str(data_fields)  # Return form data as string for demonstration
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, when a user submits a form with file uploads, the `request.files` retrieves the uploaded files. Each file can be accessed using its field name, and the `save` method is used to save the uploaded files to a specified directory. The `secure_filename` function is used to ensure that the filenames are safe to use on the filesystem. This is essential for handling file uploads securely in web applications.

:::details Try it yourself

Save the following HTML code as `index.html` in the `templates` folder of your Flask application. This form includes various input fields, including a file upload and a dropdown selection. When you submit the form, the Flask application will handle the request and process the form data accordingly.

```html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTML Form Example</title>
</head>
<body>
    <form action="/" method="POST" enctype="multipart/form-data">
        <div>
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>

            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>

            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>

            <label for="profile_picture">Profile Picture:</label>
            <input type="file" id="profile_picture" name="profile_picture" required>
        </div>

        <div id="fruit_section">
            <!-- A single selection dropdown -->
            <label for="fruits">Choose a fruit:</label>
            <select name="fruits" id="fruits">
              <option value="" disabled selected>Select a fruit</option>
              <option value="mango">Mango</option>
              <option value="banana">Banana</option>
              <option value="apple">Apple</option>
              <option value="grapes">Grapes</option>
            </select>
        </div>

        <div>
            <button type="submit">Submit</button>
        </div>
    </form>
</body>
</html>
```

Save the following Python code as `app.py` in the same directory as your `templates` folder. This Flask application will render the HTML form and handle the form submission, including processing the uploaded file and form data.

```python
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        data_fields = request.form.to_dict(flat=False)  # Get all text-based fields as a dictionary
        files = request.files  # Get uploaded files
        os.makedirs('uploads', exist_ok=True)  # Create uploads directory if it doesn't exist
        for file_key in files:
            file = files[file_key]
            file.save(os.path.join('uploads', secure_filename(file.filename)))  # Save uploaded files
        return str(data_fields)  # Return form data as string for demonstration 
    elif request.method == 'GET':
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
```

The directory structure should look like this:

```text
week4/
│├── app.py
│└── templates/
│    └── index.html
|-uploads/  # This folder will be created automatically by the program to store uploaded files
```

Run the Flask application by executing `python app.py` in your terminal. Open your web browser and navigate to `http://127.0.0.1:5000/` to access the form. Fill out the form fields, select a file to upload, and submit the form. The application will process the form data and save the uploaded file to the `uploads` directory. The submitted form data will be displayed as a string in the browser.

:::

## Summary

In this section, we explored the `request` object in Flask, which is essential for handling incoming HTTP requests.
- We covered various attributes and methods of the `request` object, including `request.method`, `request.args`, `request.form`, `request.files`, `request.headers`, `request.get_json()`, and `request.data`.
- Each of these components plays a crucial role in accessing different types of data sent by the client, such as query parameters, form data, uploaded files, headers, and raw request payloads.
- Understanding how to use the `request` object effectively allows developers to build dynamic and interactive web applications that can process user input and handle various request types seamlessly.

### Additional Resources

- [Flask Request Documentation](https://flask.palletsprojects.com/en/2.3.x/api/#flask.Request)
- [Werkzeug MultiDict Documentation](https://werkzeug.palletsprojects.com/en/2.3.x/datastructures/#werkzeug.datastructures.MultiDict)
