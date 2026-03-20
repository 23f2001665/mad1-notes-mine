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

:::info

Most of the time, we will use the model class approach as it provides more functionality and is easier to work with becuase of its object-oriented nature. The `db.Table` approach is more suitable for defining association tables in many-to-many relationships, where we do not need to define a model class.

:::

## DataTypes and Constraints

When defining columns in a model, we can specify the data type and various constraints. Some common data types include:

- `db.Integer`: Represents an integer value.
- `db.String(length)`: Represents a string with a maximum length.
- `db.Text`: Represents a large text field.
- `db.Boolean`: Represents a boolean value (True/False).
- `db.DateTime`: Represents a date and time value.
- `db.Float`: Represents a floating-point number.
- `db.Numeric(precision, scale)`: Represents a fixed-point number with specified precision and scale.
- `db.Enum(*values)`: Represents an enumeration of possible values.
- `db.LargeBinary`: Represents binary data (e.g., for storing files or images).

We can also specify various constraints for the columns, such as:

- `primary_key=True`: Marks the column as the primary key.
- `unique=True`: Ensures that all values in the column are unique.
- `nullable=False`: Ensures that the column cannot contain null values.
- `default=value`: Sets a default value for the column.
- `onupdate=value`: Sets a value to be used when the row is updated.
- `index=True`: Creates an index on the column for faster querying.
- `autoincrement=True`: Automatically increments the value for integer primary keys.

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

## Defining Relationships

In Flask SQLAlchemy, we can define relationships between tables using the `db.relationship()` function. Relationships provides an attribute based access to related records, saving us from writing complex join queries.

Here is a simple example of defining a one-to-many relationship between `User` and `Article` models:

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    articles = db.relationship('Article', back_populates='author')
    
class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', back_populates='articles')
```

In this example, we have defined a one-to-many relationship where one `User` can have many `Article`s. The `articles` attribute in the `User` model allows us to access all articles written by a user, while the `author` attribute in the `Article` model allows us to access the user who wrote the article.

Now we will see how to define different types of relationships in Flask SQLAlchemy in more details in this module.

### One-to-One Relationships

A one-to-one relationship is a relationship where one record in a table is associated with exactly one record in another table. To define a one-to-one relationship in Flask SQLAlchemy, we can use the `db.relationship()` function along with a unique constraint on the foreign key column. For example:

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    profile = db.relationship('Profile', uselist=False)

class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)

```

Here we have defined a one-to-one relationship between `User` and `Profile`. The `profile` attribute in the `User` model allows us to access the profile associated with a user, while the `user_id` column in the `Profile` model is a foreign key that references the `id` column in the `User` model. The `unique=True` constraint on the `user_id` column ensures that each profile is associated with only one user. `uselist` parameter in `db.relationship()` is set to `False` to indicate that this relationship should return a single object rather than a list.

### One-to-Many Relationships

A one-to-many relationship is a relationship where one record in a table is associated with multiple records in another table. To define a one-to-many relationship in Flask SQLAlchemy, we can use the `db.relationship()` function along with a foreign key column. For example:

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    articles = db.relationship('Article', uselist=True)

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User')

```

In this example, we have defined a one-to-many relationship between `User` and `Article`. The `articles` attribute in the `User` model allows us to access all articles written by a user, while the `author` attribute in the `Article` model allows us to access the user who wrote the article. The `user_id` column in the `Article` model is a foreign key that references the `id` column in the `User` model.

### Many-to-Many Relationships

A many-to-many relationship is a relationship where multiple records in one table are associated with multiple records in another table. To define a many-to-many relationship in Flask SQLAlchemy, we need to create an association table that contains foreign keys referencing the primary keys of the two tables involved in the relationship. For example:

```python
article_authors = db.Table('article_authors',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('article_id', db.Integer, db.ForeignKey('articles.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    articles = db.relationship('Article', secondary=article_authors, uselist=True)

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    authors = db.relationship('User', secondary=article_authors, uselist=True)
```

In this example, we have defined a many-to-many relationship between `User` and `Article` using an association table called `article_authors`. The `articles` attribute in the `User` model allows us to access all articles written by a user, while the `authors` attribute in the `Article` model allows us to access all users who wrote the article. The association table contains two foreign key columns, `user_id` and `article_id`, which reference the primary keys of the `users` and `articles` tables, respectively.
`secondary` parameter in `db.relationship()` is used to specify the association table for the many-to-many relationship.

## Relationships Synchronization and Back-populates

When we define relationships in Flask SQLAlchemy, it automatically synchronizes the relationship attributes on both sides of the relationship. This means that when we add an article to a user's `articles` attribute, it will automatically update the corresponding `author` attribute in the `Article` model, and vice versa. This synchronization is achieved using the `back_populates` parameter in the `db.relationship()` function. By specifying `back_populates` on both sides of the relationship, we can ensure that changes to one side of the relationship are reflected on the other side. For example:

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    articles = db.relationship('Article', back_populates='author')

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', back_populates='articles')
```

In this example, we have defined a one-to-many relationship between `User` and `Article` with `back_populates` specified on both sides. This means that when we add an article to a user's `articles` attribute, it will automatically update the corresponding `author` attribute in the `Article` model, and vice versa. This ensures that the relationship remains consistent and synchronized across both models.

## Loading Strategies

When we access related records through a relationship attribute, SQLAlchemy needs to load the 

### backref vs back_populates

The `backref` parameter is a shortcut for creating a bidirectional relationship. It automatically creates a new attribute on the related model that points back to the original model. For example:

```python
class User(db.Model):
    __tablename__ = 'users'
