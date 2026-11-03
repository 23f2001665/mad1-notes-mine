# Tables and Models in Flask SQLAlchemy

In this module, we will learn how to create tables and models in Flask SQLAlchemy. We will also see how to define relationships between tables.

We may also see the equivalent code in raw SQL for creating tables for few models.

## Creating Tables and Models

To create a table in Flask SQLAlchemy, we need to define a *table* or a *model class* that inherits from `db.Model`. Each attribute of the class represents a column in the table. We can also specify the data type and other constraints for each column.

Here is an example of how to create a simple `User` table defined in both ways:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'  # Example database URI
db = SQLAlchemy(app)

db.Table('users', db.metadata,
    db.Column('id', db.Integer, primary_key=True),
    db.Column('username', db.String(80), unique=True, nullable=False),
    db.Column('email', db.String(120), unique=True, nullable=False)
)

# or using a model class

class User(db.Model):
    __tablename__ = 'users'  # Optional: specify the table name

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
```

In this example, we have defined a `User` model with three columns: `id`, `username`, and `email`. The table name is explicitly set to 'users'. If we do not specify the `__tablename__`, SQLAlchemy will automatically generate a table name based on the class name (in this case, it would be 'user').

The `id` column is an integer that serves as the primary key. The `username` and `email` columns are strings that must be unique and cannot be null.

We have also defined a `__repr__` method to provide a string representation of the `User` object, which can be useful for debugging and logging.

To create the corresponding table in the database, we can use the `db.create_all()` method:

```python
with app.app_context():
    db.create_all()
```

This will create the `users` table in the database based on the `User` model we defined. The equivalent SQL command for creating this table would be:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL
);
```


Most of the time, we will use the model class approach as it provides more functionality and is easier to work with becuase of its object-oriented nature. The `db.Table` approach is more suitable for defining association tables in many-to-many relationships, where we do not need to define a model class.

## DataTypes and Constraints

When defining columns in a model, we can specify the data type and various constraints. Some common data types include:

### SQLAlchemy Data Types

| Data Type | Description | Python Values Accepted | Example |
|---|---|---|---|
| `db.Integer` | Represents an integer value. | Whole numbers (`int`) | `age = 21` |
| `db.String(length)` | Represents text with a maximum specified length. | String (`str`) | `name = "Pallavi"` |
| `db.Text` | Represents a large text field. | String (`str`) | `description = "IITM Student"` |
| `db.Boolean` | Represents a Boolean value. | `True` or `False` (`bool`) | `is_active = True` |
| `db.DateTime` | Represents a date and time value. | Python `datetime` object | `created_at = datetime.now()` |
| `db.Float` | Represents a floating-point number. | Float (`float`) | `price = 99.5` |
| `db.Numeric(precision, scale)` | Represents a fixed-point number with specified precision and scale. | `Decimal` object | `amount = Decimal("99.50")` |
| `db.Enum(*values)` | Represents one value from predefined options. | One of the predefined values | `role = "admin"` |
| `db.LargeBinary` | Represents binary data, such as files or images. | Bytes (`bytes`) | `file = b"Hello"` |

**Note:**
- `precision`: Total number of digits.
- `scale`: Number of digits after the decimal point.
- Example: `db.Numeric(10, 2)` allows 10 digits in total, with 2 digits after the decimal point.



### Column Constraints and Options in SQLAlchemy

We can specify additional constraints and options while defining columns to control how data is stored in a database.

| Constraint / Option | Purpose | Example |
|---|---|---|
| `primary_key=True` | Marks a column as the primary key. Uniquely identifies each row. | `id = db.Column(db.Integer, primary_key=True)` |
| `unique=True` | Prevents duplicate values in a column. | `email = db.Column(db.String(100), unique=True)` |
| `nullable=False` | Prevents the column from storing NULL values. | `name = db.Column(db.String(50), nullable=False)` |
| `default=value` | Provides a default value if no value is supplied. | `is_active = db.Column(db.Boolean, default=True)` |
| `onupdate=value` | Automatically sets a new value when the row is updated. | `updated_at = db.Column(db.DateTime, onupdate=datetime.now)` |
| `index=True` | Creates an index to make searches on the column faster. | `email = db.Column(db.String(100), index=True)` |
| `autoincrement=True` | Automatically generates the next integer value for a primary key. | `id = db.Column(db.Integer, primary_key=True, autoincrement=True)` |

**Important Notes:**
- `primary_key=True` generally implies `nullable=False` and uniqueness.
- `unique=True` is useful for fields like email and username.
- `nullable=False` means a value must be provided; it does not mean an empty string is forbidden.
- `default=True` is applied when a value is not provided during insertion.
- `onupdate=datetime.now` updates the timestamp when an update occurs through SQLAlchemy.
- `index=True` improves lookup performance but can add overhead to insert and update operations.
- Integer primary keys generally auto-increment by default in SQLite, so explicitly writing `autoincrement=True` is often unnecessary.

### Important Questions to Understand Column Constraints

**Q1. Does `primary_key=True` automatically make a column unique and non-nullable?**

Yes. A primary key uniquely identifies each row and cannot contain NULL values.

**Q2. When should we use `unique=True`?**

When duplicate values are not allowed, such as email addresses and usernames.

**Q3. Does `nullable=False` prevent empty strings?**

No. It prevents NULL values, but an empty string (`""`) is still allowed.

**Q4. When is the `default` value applied?**

When a new record is inserted without providing a value for that column.

Example: `default=True` sets the value to `True` if no value is provided.

**Q5. What is the purpose of `onupdate`?**

It automatically assigns a new value when an existing record is updated through SQLAlchemy.

Example: `onupdate=datetime.now`

**Q6. Why do we use `index=True`?**

It creates an index that helps retrieve records faster when searching or filtering using that column.

Note: Indexes can add overhead to INSERT and UPDATE operations.

**Q7. Is `autoincrement=True` always necessary for an integer primary key?**

No. SQLite generally auto-increments integer primary keys automatically, so explicitly specifying `autoincrement=True` is often unnecessary.

### Defining Composite Constraints

In addition to column-level constraints, we can also define composite constraints that involve multiple columns using the `__table_args__` attribute. For example, we can define a unique constraint on a combination of columns:

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)

    __table_args__ = (db.UniqueConstraint('username', 'email', name='uix_username_email'),)
```

In this example, we have defined a unique constraint named `uix_username_email` that ensures that the combination of `username` and `email` is unique across the table.

