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

Relationships Synchronization and back_populates

When defining relationships in Flask-SQLAlchemy, synchronization between both sides of a relationship is not automatic by default. It only happens when the ORM knows that two relationship attributes represent the same bidirectional relationship.

This synchronization is explicitly configured using the back_populates parameter in db.relationship().

By specifying back_populates on both sides, SQLAlchemy ensures that changes made on one side of the relationship are immediately reflected on the other side in memory, without requiring a database flush or commit.

For example:

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

In this setup:

Assigning article.author = user will automatically add the article to user.articles

Appending to user.articles will automatically set article.author

This bidirectional synchronization happens purely in memory, before any database interaction.

Without back_populates, both relationship attributes behave independently, and SQLAlchemy will not keep them in sync automatically, which can lead to inconsistent application state.

:::info `back_populates`

`back_populates` is part of SQLAlchemy’s ORM relationship synchronization system. It tells SQLAlchemy:

“These two relationship attributes represent the same link — keep them in sync in Python.”
:::

### backref vs back_populates

:::info `backref`
The `backref` parameter is a shortcut for creating a bidirectional relationship. It automatically creates a new attribute on the related model that points back to the original model. Backref creates a symmetric relationship(exact same properties on both sides) which is easier to use but less explicit. For example:
:::

```python
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    articles = db.relationship('Article', backref='author', lazy='select')

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
```

In this example, the `backref='author'` in the `User` model automatically creates an `author` attribute in the `Article` model that points back to the `User`. This means that we can access the author of an article using `article.author`, and it will return the corresponding `User` object.

The `back_populates` parameter, on the other hand, requires us to explicitly define the relationship on both sides and specify the corresponding attribute names. This provides more control and clarity over the relationships. For example:

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    articles = db.relationship('Article', back_populates='author', lazy='select')

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', back_populates='articles', lazy='joined')
```

In this example, we have defined the relationship on both sides using `back_populates`, which enables us to have more control over the relationship properties, such as the loading strategy (e.g., `lazy='select'` or `lazy='joined'`).

## Loading Strategies

Loading strategies can be classified into three main categories: *lazy loading*, *eager loading*, and *passive loading*. Lets see each of these loading strategies in more details.

### Lazy Loading

Object will be only loaded when the relationship attribute is accessed for the first time.

| Strategy  | Behavior             |
| --------- | -------------------- |
| `select`  | query on access      |
| `dynamic` | returns query object |

### Eager Loading

Object will be loaded at the same time as the parent record using a JOIN or a separate query.

| Strategy   | Behavior            |
| ---------- | ------------------- |
| `joined`   | JOIN in same query  |
| `subquery` | subquery-based load |
| `selectin` | IN-based batch load |

### Passive Loading

Object will not be loaded automatically, and access to the relationship attribute will either return None or raise an error.

| Strategy  | Behavior                         |
| --------- | -------------------------------- |
| `noload`  | never load, return None          |
| `raise`   | raise an error on access         |

:::details More Details on Loading Strategies

### Lazy Loading or Select Loading (**Default**)

Load the related data only when the relationship attribute is accessed for the first time. This is the default loading strategy.

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    articles = db.relationship('Article', lazy='select')

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

user = User.query.first()
# At this point, the articles are not loaded yet.
articles = user.articles  # This will trigger a separate query to load the articles.
```

#### Equivalent SQL

```sql
SELECT * FROM users LIMIT 1;  -- This query is executed when we access the user
SELECT * FROM articles WHERE user_id = ?;  -- This query is executed when we access the articles
```

#### Pros

- Reduces initial load time by only loading related data when needed.
- Can be more efficient if the related data is not always accessed.

#### Cons

- Can lead to the "N+1 query problem" if you access the relationship for multiple records, resulting in multiple queries being executed.

### Eager Loading - Joined Loading

Load the related data at the same time as the parent record using a JOIN. This can be more efficient when you know you will need the related data.

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    articles = db.relationship('Article', lazy='joined')

class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

user = User.query.first()
# The articles are loaded at the same time as the user using a JOIN.
articles = user.articles  # No additional query is executed to load the articles.
```

#### Equivalent SQL

```sql
SELECT users.*, articles.* FROM users LEFT OUTER JOIN articles ON users.id = articles.user_id LIMIT 1;
```

#### Pros

- Reduces the number of queries by loading related data in a single query.
- Can be more efficient when you know you will need the related data.
- Can be efficient for one-to-one or one-to-many relationships.

#### Cons

- Can lead to larger result sets and increased memory usage if the related data is large or if there are many related records.
- Can be less efficient for many-to-many relationships or when the related data is not always needed.

### Subquery Loading or Eager on Subquery

Load the related data using a separate query that is executed immediately after the parent record is loaded. This can be more efficient than joined loading when the related data is large or when there are many related records.

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    articles = db.relationship('Article', lazy='subquery')

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

user = User.query.first()
# The articles are loaded using a separate query immediately after the user is loaded.
articles = user.articles  # No additional query is executed to load the articles.
```

#### Equivalent SQL

```sql
SELECT * FROM users LIMIT 1;  -- This query is executed when we access the user
SELECT * FROM articles WHERE user_id = ?;  -- This query is executed immediately after the user is loaded to load the articles
```

#### Pros

- Reduces the number of queries by loading related data in a single query.
- Can be more efficient when the related data is large or when there are many related records.
- Can be efficient for one-to-many relationships.

#### Cons

- Can lead to increased load time due to multiple queries being executed.
- Can be less efficient for one-to-one relationships or when the related data is small.

### Eager Loading - Select In Loading

Load the related data using a separate query that is executed when the relationship attribute is accessed for the first time. This can be more efficient than lazy loading when you need to access the related data for multiple records.

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    articles = db.relationship('Article', lazy='selectin')

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

users = User.query.all()
# The articles are loaded using a separate query when the relationship attribute is accessed for the first time.
for user in users:
    articles = user.articles  # This will trigger a separate query to load the articles for all users at once.
```

#### Equivalent SQL

```sql
SELECT * FROM users;  -- This query is executed to load all users
SELECT * FROM articles WHERE user_id IN (?, ?, ?, ...);  -- This query is executed when we access the articles for all users at once, using a single query with an IN clause to load the articles for all users
```

#### Pros

- Reduces the number of queries by loading related data for multiple records in a single query.
- Can be more efficient when you need to access the related data for multiple records.
- Can be efficient for one-to-many relationships.

#### Cons

- Can lead to increased load time due to multiple queries being executed.

### Lazy Loading - Dynamic Loading

Load the related data using a separate query that is executed when the relationship attribute is accessed for the first time. This can be more efficient than lazy loading when you need to access the related data for multiple records, but you want to have more control over the query.

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    articles = db.relationship('Article', lazy='dynamic', back_populates='author')

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', back_populates='articles', lazy='dynamic')

user = User.query.first()
# The articles are loaded using a separate query when the relationship attribute is accessed for the first time.
articles_query = user.articles  # This will return a query object that can be further filtered or executed to load the articles.
articles = articles_query.all()  # This will execute the query to load the articles.
```

#### Equivalent SQL

```sql
SELECT * FROM users LIMIT 1;  -- This query is executed when we access the user
SELECT * FROM articles WHERE user_id = ?;  -- This query is executed when we execute
```

the articles query to load the articles

#### Pros

- Provides more control over the query used to load the related data.
- Can be more efficient when you need to access the related data for multiple records, but you want to have more control over the query.
- Can be efficient for one-to-many relationships.

#### Cons

- Can lead to increased load time due to multiple queries being executed.

### Passive Loading - No Load

Do not load the related data automatically, and return None when the relationship attribute is accessed. This can be useful when you want to prevent accidental loading of related data.

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    articles = db.relationship('Article', lazy='noload', back_populates='author')

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', back_populates='articles')


user = User.query.first()
# The articles are not loaded automatically, and accessing the relationship attribute will return None.
articles = user.articles  # This will return None, and no query will be executed to load the articles.
```

#### Equivalent SQL

```sql
SELECT * FROM users LIMIT 1;  -- This query is executed when we access the user
-- No query is executed to load the articles, and accessing user.articles will return None.
```

#### Pros

- Prevents accidental loading of related data, which can improve performance in some cases.
- Can be useful when you want to explicitly control when related data is loaded.
- Can be efficient for one-to-many relationships when you do not always need to access the related data.

#### Cons

- Can lead to confusion if you forget that the related data is not loaded automatically.

### Passive Loading - Raise

Do not load the related data automatically, and raise an error when the relationship attribute is accessed. This can be useful when you want to enforce that related data must be loaded explicitly.

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    articles = db.relationship('Article', lazy='raise', back_populates='author')

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', back_populates='articles')

user = User.query.first()
# The articles are not loaded automatically, and accessing the relationship attribute will raise an error.
try:
    articles = user.articles  # This will raise an error, and no query will be
    # executed to load the articles.
except Exception as e:
    print(f"Error: {e}")
```

#### Equivalent SQL

```sql
SELECT * FROM users LIMIT 1;  -- This query is executed when we access the user
-- No query is executed to load the articles, and accessing user.articles will raise an error
```

#### Pros

- Enforces that related data must be loaded explicitly, which can improve performance in some cases.
- Can be useful when you want to ensure that related data is not accessed without being loaded first
- Can be efficient for one-to-many relationships when you want to enforce that related data must be loaded explicitly.

#### Cons

- Can lead to confusion if you forget that the related data is not loaded automatically and that accessing it will raise an error.

:::

## Cascade Options

Cascade options define how changes to a parent object should affect related child objects in a relationship. Cascade happens when you perform operations like delete, update, or save on a parent object, and you want those operations to automatically propagate to related child objects.

Cascade options can be specified in ForiegnKey or in relationship using `cascade` parameter. Let's see both of the cases in details.

### ForeignKey Cascade Options

When defining a foreign key in a model, you can specify cascade options using the `ondelete` and `onupdate` parameters. These options determine what happens to related records when a parent record is deleted or updated.
For example:

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    author = db.relationship('User', back_populates='articles')
```

In this example, we have specified `ondelete='CASCADE'` and `onupdate='CASCADE'` for the `user_id` foreign key in the `Article` model. This means that if a `User` record is deleted, all related `Article` records will also be deleted automatically. Similarly, if a `User` record is updated, the corresponding foreign key values in the related `Article` records will also be updated automatically.

#### Cascade Options for Foreign Keys

| Option     | Description                                                                 |
| ---------- | --------------------------------------------------------------------------- |
| `CASCADE`  | Deletes or updates related records when the parent record is deleted or updated. |
| `SET NULL` | Sets the foreign key to NULL in related records when the parent record is deleted or updated. |
| `SET DEFAULT` | Sets the foreign key to its default value in related records when the parent record is deleted or updated. |
| `RESTRICT` | Prevents deletion or update of the parent record if there are related records. |
| `NO ACTION` | Similar to RESTRICT, but the check is deferred until the end of the transaction. |
| `ON DELETE` | Specifies the action to take when a parent record is deleted. |
| `ON UPDATE` | Specifies the action to take when a parent record is updated. |
| `NONE`     | No action is taken on related records when the parent record is deleted or updated. |

:::warning NOTE
By default, `sqlite3` does not enforce foreign key constraints, so you need to enable it explicitly by executing `PRAGMA foreign_keys = ON;` after establishing a connection to the database. In other databases like PostgreSQL and MySQL, foreign key constraints are enforced by default. You can enable foreign key constraints in SQLite by adding the following code to your application:

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```

without enabling foreign key constraints, the cascade options specified in the foreign key definition will not be enforced, and related records will not be automatically deleted or updated when a parent record is deleted or updated. This leads to potential data integrity issues, as orphaned records may remain in the database without the expected cascading behavior.
:::

### Relationship Cascade Options

When defining a relationship in a model, you can specify cascade options using the `cascade` parameter in the `db.relationship()` function. These options determine what happens to related records when a parent record is deleted, updated, or saved.
For example:

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    articles = db.relationship('Article', back_populates='author', cascade='all, delete-orphan')

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', back_populates='articles')
```

In this example, we have specified `cascade='all, delete-orphan'` for the `articles` relationship in the `User` model. This means that if a `User` record is deleted, all related `Article` records will also be deleted automatically (due to the `all` option). Additionally, if an `Article` record is removed from the `articles` relationship of a `User`, it will be automatically deleted from the database (due to the `delete-orphan` option).

#### Common Cascade Options in Relationships

| Option          | Description                                                                 |
| --------------  | --------------------------------------------------------------------------- |
| `all`           | Applies all cascade options (delete, delete-orphan, save-update, merge, refresh-expire)|
| `delete`        | Deletes related records when the parent record is deleted.|
| `delete-orphan` | Deletes related records that are removed from the relationship. |
| `save-update`   | Saves or updates related records when the parent record is saved or updated. |
| `merge`         | Merges related records when the parent record is merged. |
| `refresh-expire`| Refreshes or expires related records when the parent record is refreshed or expired. |
| `none`          | No cascade behavior is applied. |

### Difference between ForeignKey Cascade and Relationship Cascade

The cascade options specified in a foreign key definition (using `ondelete` and `onupdate`) are enforced at the database level, while the cascade options specified in a relationship definition (using the `cascade` parameter in `db.relationship()`) are enforced at the application level by SQLAlchemy's ORM.

The ORM level restrictions can be bypassed by executing raw SQL queries directly against the database, while the database level restrictions cannot be bypassed and will always be enforced regardless of how the data is manipulated.

## Summary

In this module, we have learned how to create tables and models in Flask SQLAlchemy, define relationships between tables, and understand different loading strategies for related data. We have also seen the equivalent SQL commands for creating tables and loading related data. Understanding these concepts is crucial for effectively using Flask SQLAlchemy to manage your database and optimize performance when working with related data.
