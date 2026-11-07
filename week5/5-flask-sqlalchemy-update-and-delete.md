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

# All the snippets on this page need an application context
# (inside a view function this is automatic).
with app.app_context():
    # Update a user
    user = db.session.get(User, 1)  # Query the user with id (legacy: User.query.get(1))
    if user:
        user.name = 'New Name'  # Update the name
        db.session.commit()  # Commit the changes to the database
```

We don't need to call `db.session.add(user)` again: the object came from the session, so the session already tracks it and detects the changed attribute.

In this example, we query the user with a specific id, update the name attribute, and then commit the changes to the database.

### Multiple Records Update

To update multiple records, we can use the `update()` method on a query. Here’s an example:

```python
# Update multiple users
User.query.filter(User.name.like('Old%')).update({User.name: 'New Name'}, synchronize_session=False) # synchronize_session can be set to 'fetch' or 'evaluate' based on our needs
db.session.commit()  # Commit the changes to the database
```

In this example, we update the name of all users whose name starts with 'Old' to 'New Name' with a single `UPDATE ... WHERE` statement, without loading the users into Python. The `synchronize_session` parameter is used to specify how objects that are *already in the session* should be synchronized after the update.
Options:

- `'auto'` → the default in SQLAlchemy 2.x: tries `'evaluate'`, falls back to `'fetch'`
- `False` → fastest, but objects already loaded in the session keep their old (stale) values until they are refreshed
- `'fetch'` → finds the affected rows from the database (via `RETURNING` or an extra `SELECT`) and updates those objects in the session
- `'evaluate'` → evaluates the `WHERE` condition in Python against the objects in the session; raises an error if the condition can't be evaluated in Python (for example, `like()` in the example above)

**Important:** bulk `update()` / `delete()` run directly in the database. They do **not** load objects, so ORM relationship cascades (`cascade='all, delete-orphan'`) are **not** applied; only database-level `ON DELETE` / `ON UPDATE` rules are.

## Deleting Records

To delete a record, we first need to query the record we want to delete, and then call the `delete()` method on the session. Here’s an example:

```python
# Delete a user
user = db.session.get(User, 1)  # Query the user with id
if user:
    db.session.delete(user)  # Mark the user for deletion
    db.session.commit()  # The DELETE is sent and committed here
```

In this example, we query the user with a specific id, mark it for deletion with `db.session.delete(user)`, and then commit, which sends the `DELETE` to the database. Relationship cascades (e.g. `cascade='all, delete-orphan'`) are applied here because we deleted through the ORM object.

`db.session.delete` takes only a single record as an argument. To delete multiple records, we can use the `delete()` method on a query, similar to how we update multiple records. Here’s an example:

```python
# Delete multiple users
User.query.filter(User.name.like('Old%')).delete(synchronize_session=False) # synchronize_session can be set to 'fetch' or 'evaluate' based on our needs
db.session.commit()  # Commit the changes to the database
```

In this example, we delete all users whose name starts with 'Old' with a single `DELETE ... WHERE` statement. The `synchronize_session` parameter is used to specify how the session should be synchronized after the delete operation. As mentioned above, ORM cascades are not applied by this bulk delete.

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

In these examples, we use the `text()` function from SQLAlchemy to execute raw SQL queries for updating and deleting records in the database. The table name is `user` because Flask-SQLAlchemy derives it from the class name `User`. We pass the parameters as a dictionary (bound parameters `:name`, `:id`) to prevent SQL injection attacks. Raw SQL bypasses the ORM completely: no cascades, no `onupdate` defaults, and already-loaded objects are not updated.

## Summary

- We can update and delete records in Flask-SQLAlchemy using the session object.
- To update a single record, we query the record, modify its attributes, and commit the
changes to the database.
- To update multiple records, we can use the `update()` method on a query (a single bulk statement; ORM cascades are not applied).
- To delete a record, we query the record, call the `delete()` method on the
session, and commit the changes to the database.
- We can also execute raw SQL queries to perform update and delete operations.
