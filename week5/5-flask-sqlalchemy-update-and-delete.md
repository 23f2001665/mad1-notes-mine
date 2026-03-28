# UPDATE and DELETE Records in Flask-SQLAlchemy

In Flask-SQLAlchemy, we can update and delete records in the database using the session object. Here’s how we can do it:

## Updating Records

We can update a single record or multiple records in the database.

### Single Record Update

To update a record, we first need to query the record we want to update, modify its attributes, and then commit the changes to the database. Here’s an example:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
# Update a user
user = User.query.get(1)  # Query the user with id
if user:
    user.name = 'New Name'  # Update the name
    db.session.commit()  # Commit the changes to the database
```

In this example, we query the user with a specific id, update the name attribute, and then commit the changes to the database.

### Multiple Records Update

To update multiple records, we can use the `update()` method on a query. Here’s an example:

```python
# Update multiple users
User.query.filter(User.name.like('Old%')).update({User.name: 'New Name'}, synchronize_session=False) # synchronize_session can be set to 'fetch' or 'evaluate' based on our needs
db.session.commit()  # Commit the changes to the database
```

In this example, we update the name of all users whose name starts with 'Old' to 'New Name'. The `synchronize_session` parameter is used to specify how the session should be synchronized after the update.
Options:

- `False` → fastest, but session becomes inconsistent
- `'fetch'` → queries DB again to sync
- `'evaluate'` → tries to update in Python (limited support)

## Deleting Records

To delete a record, we first need to query the record we want to delete, and then call the `delete()` method on the session. Here’s an example:

```python
# Delete a user
user = User.query.get(1)  # Query the user with id
if user:
    db.session.delete(user)  # Delete the user
    db.session.commit()  # Commit the changes to the database
```

In this example, we query the user with a specific id, delete the user from the session, and then commit the changes to the database.

:::info Note
`db.session.delete` takes only a single record as an argument. To delete multiple records, we can use the `delete()` method on a query, similar to how we update multiple records. Here’s an example:

```python
# Delete multiple users
User.query.filter(User.name.like('Old%')).delete(synchronize_session=False) # synchronize_session can be set to 'fetch' or 'evaluate' based on our needs
db.session.commit()  # Commit the changes to the database
```

In this example, we delete all users whose name starts with 'Old'. The `synchronize_session` parameter is used to specify how the session should be synchronized after the delete operation.
:::

## Non ORM Way to Update and Delete Records

In addition to using the ORM way to update and delete records, we can also execute raw SQL queries to perform these operations. Here’s how we can do it:

### Update Records using Raw SQL

```python
# Update a user using raw SQL
from sqlalchemy import text
db.session.execute(text('UPDATE user SET name = :name WHERE id = :id'), {'name': 'New Name', 'id': 1})
db.session.commit()  # Commit the changes to the database
```

### Delete Records using Raw SQL

```python
# Delete a user using raw SQL
db.session.execute(text('DELETE FROM user WHERE id = :id'), {'id': 1})
db.session.commit()  # Commit the changes to the database
```

In these examples, we use the `text()` function from SQLAlchemy to execute raw SQL queries for updating and deleting records in the database. We pass the parameters as a dictionary to prevent SQL injection attacks.

## Summary

- We can update and delete records in Flask-SQLAlchemy using the session object.
- To update a single record, we query the record, modify its attributes, and commit the
changes to the database.
- To update multiple records, we can use the `update()` method on a query.
- To delete a record, we query the record, call the `delete()` method on the
session, and commit the changes to the database.
- We can also execute raw SQL queries to perform update and delete operations.
