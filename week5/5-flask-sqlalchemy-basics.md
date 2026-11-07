# Flask SQLAlchemy

In week 4 we have learned about how to create a Flask application, how to define routes and handle form data and other requests.
 In week 5, we will learn about how to use SQLAlchemy with Flask to interact with a database.

## What is SQLAlchemy?

SQLAlchemy is a popular Object-Relational Mapping (ORM) library for Python. It provides a high-level interface for working with databases, allowing developers to interact with the database using Python objects instead of writing raw SQL queries.

## What is ORM

ORM (Object-Relational Mapping) is a technique that allows developers to interact with a database using object-oriented programming concepts. Instead of writing raw SQL queries, developers can use Python classes and objects to represent database tables and rows.

so instead of doing

```sql
SELECT * FROM users WHERE id = 1;
```

we can do this

```python
user = db.session.get(User, 1)   # modern (SQLAlchemy 2.x) way
# user = User.query.get(1)       # older/legacy style, still works but shows a LegacyAPIWarning
```

## What is Flask-SQLAlchemy?

Flask-SQLAlchemy is an extension for Flask that adds support for SQLAlchemy. It provides a simple and convenient way to integrate SQLAlchemy into our Flask applications, allowing us to define our database models and interact with the database using Python code. In our course, we will be using Flask-SQLAlchemy to manage our database interactions in our Flask applications.

### Flask-SQLAlchemy Features

Flask-SQLAlchemy is a Flask extension that integrates SQLAlchemy with Flask and simplifies database operations in Flask applications.

| Feature | Explanation | Example |
|---|---|---|
| **Declarative Syntax** | Allows us to define database tables using Python classes. | Creating a `User` model with `db.Model`. |
| **Database Abstraction** | Allows us to work with different databases using similar Python code. | SQLite, PostgreSQL, MySQL. |
| **Querying** | Provides Python methods to retrieve, filter and search database records. | `User.query.filter_by(username="Pallavi").first()` |
| **Relationships** | Allows us to establish relationships between database tables. | One course can have multiple examinations. |
| **Transactions** | Ensures database operations are committed together or rolled back when necessary. | `db.session.commit()` and `db.session.rollback()`. |
| **Connection Pooling** | Reuses database connections instead of creating a new connection for every request. | Efficiently managing database connections. |
| **Security** | Uses parameterized queries through SQLAlchemy's query system, helping protect against SQL injection. | `User.query.filter_by(username=username).first()` |
| **Session Management** | Provides `db.session` to manage database operations such as adding, updating and deleting records. | `db.session.add(user)` |
| **Schema Generation** | Allows us to create database tables based on our model definitions. | `db.create_all()` |
| **Migrations** | Not built into Flask-SQLAlchemy itself; provided by the separate **Flask-Migrate** extension (built on Alembic), which works with Flask-SQLAlchemy models. | Adding a new column to an existing table. |
| **Validation Integration** | Can work with external validation libraries to validate data before storing it. | Flask-WTF, Marshmallow. |
| **Flask Integration** | Integrates SQLAlchemy with Flask application configuration and application context. | `db.init_app(app)` |
| **Performance** | Supports efficient query execution, indexing and other database optimisation techniques. | Filtering records using indexed columns. |


### How to install Flask-SQLAlchemy?

We can install Flask-SQLAlchemy using pip:

```bash
pip install Flask-SQLAlchemy
```

This command will install Flask-SQLAlchemy and its dependencies, allowing us to use it in our Flask applications.

## sqlite3 and vscode extensions

Before actually using Flask-SQLAlchemy, it is helpful to have basic understanding of SQLite and to install the SQLite extension in VSCode. This will help us to visualize and manage our database more effectively.

Sqlite is a lightweight, file-based database that is commonly used for development and testing purposes. It is easy to set up and does not require a separate server, making it a great choice for small applications and projects.

To install the SQLite extension in VSCode, follow these steps:

1. Open VSCode and go to the Extensions view by clicking on the Extensions icon in the Activity Bar on the side of the window or by pressing `Ctrl+Shift+X`.
2. In the search bar, type "SQLite" and look for the extension named "SQLite3Editor" by **yy0931**.
3. Click on the "Install" button to install the extension.

Now you open the sqlite files with the sqlite3 editor to get a nice UI to visualize and manage your database. You can also use this extension to run SQL queries directly on your database, which can be very helpful for debugging and testing purposes.

## Basic Usage of Flask-SQLAlchemy

To use Flask-SQLAlchemy in our Flask application, we need to follow these steps:

1. Import the necessary modules and initialize the Flask application.
2. Configure the database URI for our application.
3. Create an instance of the SQLAlchemy class and pass the Flask application to it.
4. Define our database models as Python classes.
5. Create the database tables based on our models.
6. Use the models to interact with the database (e.g., create, read, update and delete records).

Here is a simple example of how to use Flask-SQLAlchemy in a Flask application:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'  # Configure the database URI
db = SQLAlchemy(app)  # Initialize SQLAlchemy with the Flask app

# Define a database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key column
    username = db.Column(db.String(80), unique=True, nullable=False)  # Username column
    email = db.Column(db.String(120), unique=True, nullable=False)  # Email column
    def __repr__(self):
        return f'<User {self.username}>'

# Create the database tables
with app.app_context():
    db.create_all()

    # Example of creating a new user
    new_user = User(username='john_doe',
                    email='john@example.com')
    db.session.add(new_user)  # Add the new user to the session
    db.session.commit()  # Commit the session to save the user to the database

    # Example of querying the database
    user = User.query.filter_by(username='john_doe').first()  # Query for a user with username 'john_doe'
    print(user)  # Output: <User john_doe>
```

In this example, we have defined a `User` model with three columns: `id`, `username`, and `email`. We then create the database tables using `db.create_all()`, add a new user to the database, and query for that user. This is just a basic example, and Flask-SQLAlchemy provides many more features and capabilities for working with databases in our Flask applications.

Now we will go through each of these steps in a little more detail in the upcoming sections.

### Step 1: Importing Modules and Initializing Flask Application

To use Flask-SQLAlchemy, we need to import the necessary modules and initialize our Flask application. This is typically done at the beginning of our application code.

For most purposes, Flask-SQLAlchemy provides all the required functionality, but if we want to use some of the advanced features of SQLAlchemy, we may also need to import additional modules from SQLAlchemy. But for basic usage, we can simply import Flask and SQLAlchemy as shown in the example above.

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)  # Initialize the Flask application
```

### Step 2: Configuring the Database URI

The **DATABASE_URI** is a configuration parameter that specifies the following details about the database we want to connect to:

- **Database Type**: The type of database we are using (e.g., SQLite, PostgreSQL, MySQL).
- **Username**: The username for authenticating with the database (if required).
- **Password**: The password for authenticating with the database (if required).
- **Host**: The hostname or IP address of the database server (if required).
- **Port**: The port number on which the database server is listening (if required).
- **Database Name**: The name of the specific database we want to connect to.

The format of the DATABASE_URI is typically as follows:

```bash
dialect+driver://username:password@host:port/database
```

but for our course we will be using SQLite as our database, which is a file-based database and does not require a username, password, host, or port. Therefore, the DATABASE_URI for SQLite is simply:

```bash
sqlite:///path/to/database.db
```

We have to set the DATABASE_URI in our Flask application configuration before initializing SQLAlchemy. This allows SQLAlchemy to know the information it needs to connect to the database when we create an instance of the SQLAlchemy class.

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'  # Configure the database URI
```

Now SQLAlchemy knows that we want to use a SQLite database file named `example.db`. In Flask-SQLAlchemy 3.x, a *relative* SQLite path is resolved relative to the app's **`instance` folder**, so the file ends up at `instance/example.db` (the folder is created automatically). The file itself is created by SQLite the first time a connection is actually made (for example, when we call `db.create_all()`), not at the moment we write `SQLAlchemy(app)`.

This step must be done before initializing SQLAlchemy, as SQLAlchemy needs to know the database URI when it is initialized. If we try to initialize SQLAlchemy without setting the DATABASE_URI, we will get an error because SQLAlchemy will not know how to connect to the database.


### Step 3: Initializing SQLAlchemy

After configuring the database URI, we can create an instance of the SQLAlchemy class and pass our Flask application to it. This will initialize SQLAlchemy and allow us to use it in our application.

```python
db = SQLAlchemy(app)  # Initialize SQLAlchemy with the Flask app
```

This can be done with this alternative syntax as well:

```python
db = SQLAlchemy()  # Create an instance of SQLAlchemy
db.init_app(app)  # Initialize SQLAlchemy with the Flask app
```

### Step 4: Defining Database Models

In Flask-SQLAlchemy, we define our database models as Python classes that inherit from `db.Model`. Each class represents a table in the database, and each attribute of the class represents a column in that table. We can also define relationships between different models using SQLAlchemy's relationship features.

Here is a simple example of defining a `User` model:

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key column
    username = db.Column(db.String(80), unique=True, nullable=False)  # Username column
    email = db.Column(db.String(120), unique=True, nullable=False)  # Email column
    def __repr__(self):
        return f'<User {self.username}>'
```

Here in this example, we have defined a `User` model with three columns: `id`, `username`, and `email`. The `id` column is an integer that serves as the primary key for the table. The `username` and `email` columns are strings that must be unique and cannot be null. We have also defined a `__repr__` method to provide a string representation of the user object.

We will learn more about defining models and relationships in the upcoming sections.

### Step 5: Creating Database Tables

After defining our database models, we need to create the corresponding tables in the database. We can do this using the `db.create_all()` method, which will create all the tables defined by our models in the database.

```python
with app.app_context():
    db.create_all()  # Create the database tables based on our models
```

`db.create_all()` only creates tables that **do not exist yet**, so running it again is harmless. However, it **never alters an existing table**: if we later add/remove/change a column in a model, `create_all()` will not update that table. To change the schema of an existing database we either drop and recreate the tables (losing data) or use a migration tool like `Flask-Migrate`.



A few methods in flask and sqlalchemy require an application context to be active in order to work properly. An application context is a way for Flask to keep track of the current application and its configuration.

An application context can be activated in the following ways:

- using `with app.app_context():` block
- using `app.app_context().push()` to manually push the application context onto the stack
- handling a request: whenever Flask handles a request to one of our routes, it automatically pushes an application context (and a request context) for the duration of that request
- using `app.test_request_context()` to create a *dummy* request context (useful in scripts/tests), which also pushes an application context

Inside a view function we therefore never need to push the context manually. Let's see an example where a request to a route provides the application context:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

# Defining Models

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    def __repr__(self):
        return f'<User {self.username}>'

@app.route('/create_tables')
def create_tables():
    db.create_all()  # This will create the database tables based on our models
    return 'Tables created successfully!'

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, we have defined a route `/create_tables`; when it is accessed, Flask handles the request inside an application context, so `db.create_all()` works and creates the database tables based on our models. We can simply run the application and access `http://localhost:5000/create_tables` in our browser to create the tables without needing to manually push the application context. This is a convenient way to use the context-specific features of Flask and SQLAlchemy without needing to worry about managing the application context manually.



In real world applications, we would typically use a migration tool like `Flask-Migrate` to manage our database schema changes over time, rather than using `db.create_all()` directly. This allows us to keep track of changes to our database schema and apply those changes in a controlled manner, especially when working with production databases.

### Step 6: Interacting with the Database

Once we have defined our models and created the database tables, we can use the models to interact with the database. This includes creating new records, querying existing records, updating records, and deleting records.

Here are some examples of how to perform these operations using Flask-SQLAlchemy:

#### Creating New Records

```python
# Example of creating a new user
user1 = User(username='john_doe', email='john@example.com')
user2 = User(username='jane_doe', email='jane@example.com')
db.session.add(user1)  # Add the new user to the session
db.session.add(user2)  # Add another user to the session
db.session.commit()  # Commit the session to save the users to the database
```

#### Querying Existing Records

```python
# Example of querying the database
user = User.query.filter_by(username='john_doe').first()  # Query for a user with username 'john_doe'
print(user)  # Output: <User john_doe>
```

If the query does not find any matching records, it will return `None`. Therefore, it is important to check if the result of the query is `None` before trying to access any attributes of the returned object to avoid getting an `AttributeError`.

Same thing applies to updating and deleting records as well. We should always check if the record we want to update or delete exists in the database before trying to perform the update or delete operation.

#### Updating Records

```python
# Example of updating a user's email
user = User.query.filter_by(username='john_doe').first()  # Query for the user we want to update
user.email = 'john_updated@example.com'  # Update the user's email
db.session.commit()  # Commit the changes to the database
```

In this example, if we try to update the user's email to an email that already exists for another user in the database, we will get a `sqlalchemy.exc.IntegrityError` (raised when the change is flushed, i.e. at `commit()`) because of the unique constraint on the email column. After such an error the session's transaction is no longer usable, so we must call `db.session.rollback()` before using the session again. Therefore, it is important to ensure that any updates we make to the database do not violate any constraints defined in our models.

```python
from sqlalchemy.exc import IntegrityError

try:
    user.email = 'jane@example.com'   # already used by another user
    db.session.commit()
except IntegrityError:
    db.session.rollback()             # undo the failed transaction
```

We will learn more about constraints in the upcoming sections when we discuss defining models in more detail.

#### Deleting Records

```python
# Example of deleting a user
user = User.query.filter_by(username='john_doe').first()  # Query for the user we want to delete
db.session.delete(user)  # Delete the user from the session
db.session.commit()  # Commit the changes to the database
```

These are just basic examples of how to interact with the database using Flask-SQLAlchemy. The library provides many more features and capabilities for working with databases, including advanced querying options, relationships between models, and support for transactions. We will explore these features in more detail in the upcoming sections.

## Complete Example

Here is a complete example that demonstrates how to use Flask-SQLAlchemy to create a simple Flask application that interacts with a SQLite database:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

@app.route('/create_tables')
def create_tables():
    db.create_all()
    return 'Tables created successfully!'

@app.route('/add_user/<username>/<email>')   # this should be post method in real application
def add_user(username, email):
    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()
    return f'User {username} added successfully!'

@app.route('/get_user/<username>')
def get_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return f'User found: {user.username}, {user.email}'
    else:
        return 'User not found!'

@app.route('/update_user/<username>/<new_email>')  # this should be put method in real application
def update_user(username, new_email):
    user = User.query.filter_by(username=username).first()
    if user:
        user.email = new_email
        db.session.commit()
        return f'User {username} updated successfully!'
    else:
        return 'User not found!'

@app.route('/delete_user/<username>')  # this should be delete method in real application
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return f'User {username} deleted successfully!'
    else:
        return 'User not found!'

if __name__ == '__main__':
    app.run(debug=True)
```

### How to run this example?

1. Save the code in a file named `app.py`.
2. Install Flask and Flask-SQLAlchemy using pip:

   ```bash
   pip install Flask Flask-SQLAlchemy
   ```

3. Run the application:

    ```bash
    python app.py
    ```

4. Open your browser and access the following URLs to interact with the application:

    - `http://localhost:5000/create_tables` to create the database tables.
        - After running this once, you can check the following file in your current directory to see the created database:

        ```bash
            .
            ├── app.py
            |── instance/
            |   └── example.db
            └── ...
        ```

    - visit the following URLs to add the following users to the database:

        - `http://localhost:5000/add_user/john_doe/john@example.com` to add a user named "john_doe".
        - `http://localhost:5000/add_user/jane_smith/jane@example.com` to add a user named "jane_smith".
        - `http://localhost:5000/add_user/robert_johnson/robert@example.com` to add a user named "robert_johnson".

    - visit the following URLs to query for the users in the database:

        - `http://localhost:5000/get_user/john_doe` to get the details of user "john_doe".
        - `http://localhost:5000/get_user/jane_smith` to get the details of user "jane_smith".
        - `http://localhost:5000/get_user/robert_johnson` to get the details of user "robert_johnson".

    - visit the following URLs to update the email of the users in the database:
        - `http://localhost:5000/update_user/john_doe/john_new@example.com` to update the email of user "john_doe".
        - `http://localhost:5000/update_user/jane_smith/jane_new@example.com` to update the email of user "jane_smith".
        - `http://localhost:5000/update_user/robert_johnson/robert_new@example.com` to update the email of user "robert_johnson".

    - visit the following URLs to delete the users from the database:
        - `http://localhost:5000/delete_user/john_doe` to delete user "john_doe".
        - `http://localhost:5000/delete_user/jane_smith` to delete user "jane_smith".
        - `http://localhost:5000/delete_user/robert_johnson` to delete user "robert_johnson".

## Extra: States of SQLAlchemy Objects

In SQLAlchemy, an ORM object is always in one of the following states (relative to a session):

- **Transient**: The object has just been created (`User(...)`), is not in any session and has no row in the database.
- **Pending**: The object has been added to a session with `db.session.add()`, but no `INSERT` has been sent to the database yet.
- **Persistent**: The object is in a session **and** has a corresponding row in the database. A pending object becomes persistent when the session is **flushed** (a `commit()` flushes automatically, and so does running a query because of *autoflush*). Objects returned by a query are also persistent.
- **Deleted**: The object was marked with `db.session.delete()` and the `DELETE` statement has been flushed, but the transaction is not yet committed. (Right after calling `db.session.delete()` and before the flush, the object is still *persistent*, just marked for deletion.)
- **Detached**: The object is not attached to any session. This happens after `db.session.expunge(obj)` / `db.session.close()`, or after a deleted object's transaction is committed. A detached object usually still corresponds to a row in the database (unless it was deleted); it just is no longer tracked by a session, so lazy-loading its relationships will fail.

```text
User(...) ──add()──> pending ──flush/commit──> persistent ──delete()+flush──> deleted ──commit──> detached
                                                   │
                                                   └──expunge()/close()──> detached
```

## Summary

In this section, we learned how to use Flask-SQLAlchemy to setup flask-sqlalchemy, define models, create database tables, and interact with the database. We also explored how to manage application contexts in Flask applications.

### Extra Resources

- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
