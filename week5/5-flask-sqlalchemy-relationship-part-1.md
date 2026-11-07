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
    profile = db.relationship('Profile', uselist=False, back_populates='user')

class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    user = db.relationship('User', back_populates='profile')

```

Here we have defined a one-to-one relationship between `User` and `Profile`. The `profile` attribute in the `User` model allows us to access the profile associated with a user, while the `user_id` column in the `Profile` model is a foreign key that references the `id` column in the `User` model. A profile always points to exactly one user anyway (it has a single `user_id` value); the `unique=True` constraint on the `user_id` column additionally ensures that **no two profiles can have the same `user_id`**, i.e. each user has at most one profile. That is what turns a one-to-many into a one-to-one at the database level. `uselist` parameter in `db.relationship()` is set to `False` to indicate that this relationship should return a single object rather than a list.

### One-to-Many Relationships

A one-to-many relationship is a relationship where one record in a table is associated with multiple records in another table. To define a one-to-many relationship in Flask SQLAlchemy, we can use the `db.relationship()` function along with a foreign key column. For example:

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    articles = db.relationship('Article', back_populates='author')  # a list (uselist=True is the default here)

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', back_populates='articles')

```

In this example, we have defined a one-to-many relationship between `User` and `Article`. The `articles` attribute in the `User` model allows us to access all articles written by a user, while the `author` attribute in the `Article` model allows us to access the user who wrote the article. The `user_id` column in the `Article` model is a foreign key that references the `id` column in the `User` model. The foreign key always goes on the "many" side.

If we define both relationships **without** `back_populates`, SQLAlchemy treats them as two unrelated relationships writing to the same foreign key and emits a warning (`relationship 'Article.author' will copy column users.id to column articles.user_id, which conflicts with relationship(s): 'User.articles'`). Linking them with `back_populates` (explained below) fixes this.

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
    articles = db.relationship('Article', secondary=article_authors, back_populates='authors')

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    authors = db.relationship('User', secondary=article_authors, back_populates='articles')
```

In this example, we have defined a many-to-many relationship between `User` and `Article` using an association table called `article_authors`. The `articles` attribute in the `User` model allows us to access all articles written by a user, while the `authors` attribute in the `Article` model allows us to access all users who wrote the article. The association table contains two foreign key columns, `user_id` and `article_id`, which reference the primary keys of the `users` and `articles` tables, respectively.
`secondary` parameter in `db.relationship()` is used to specify the association table for the many-to-many relationship. Making both columns the composite primary key also prevents the same (user, article) pair from being stored twice.

### Relationships Synchronization and back_populates

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


`back_populates` is part of SQLAlchemy’s ORM relationship synchronization system. It tells SQLAlchemy:

“These two relationship attributes represent the same link — keep them in sync in Python.”


### backref vs back_populates

The `backref` parameter is a shortcut for creating a bidirectional relationship. It automatically creates a new attribute on the related model that points back to the original model, and links the two sides just like `back_populates` does. It is shorter but less explicit: the reverse attribute does not appear in the other class's code. Note that the reverse side does **not** copy the options of the forward side (e.g. `lazy='joined'` on `User.articles` does not make `Article.author` joined); it gets default options unless we pass them with `db.backref('author', lazy='joined')`. Modern SQLAlchemy documentation considers `backref` legacy and recommends `back_populates`. For example:

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

In this example, we have defined the relationship on both sides using `back_populates`, so each side is visible in its own class and has its own options, such as the loading strategy (e.g., `lazy='select'` or `lazy='joined'`).

## Loading Strategies

The `lazy` parameter of `db.relationship()` decides **when and how** related objects are loaded. The strategies can be grouped into three categories: *lazy loading*, *eager loading*, and *no loading* (`noload` / `raise`; this grouping is just for understanding). Lets see each of these loading strategies in more details.

### Lazy Loading

Object will be only loaded when the relationship attribute is accessed for the first time.

| Strategy  | Behavior             |
| --------- | -------------------- |
| `select`  | query on access      |
| `dynamic` | returns query object (collections only, legacy) |

### Eager Loading

Related objects are loaded together with the parent, while the parent query runs: either in the same query (JOIN) or in an extra query sent immediately afterwards.

| Strategy   | Behavior            |
| ---------- | ------------------- |
| `joined`   | JOIN in same query  |
| `subquery` | subquery-based load |
| `selectin` | IN-based batch load |

### No Loading

Related objects are never loaded automatically; accessing the attribute either gives an empty value or raises an error.

| Strategy  | Behavior                                                     |
| --------- | ------------------------------------------------------------ |
| `noload`  | never load: empty list `[]` for collections, `None` for a single object (deprecated in SQLAlchemy 2.1) |
| `raise`   | raise an error on access                                     |



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

user = User.query.first()  # query 1
# At this point, the articles are not loaded yet.
articles = user.articles  # This will trigger a separate query to load the articles.
```

#### Equivalent SQL

```sql
SELECT * FROM users LIMIT 1;  -- executed by User.query.first()
SELECT * FROM articles WHERE user_id = ?;  -- executed when we first access user.articles
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
SELECT anon_1.*, articles_1.*
FROM (SELECT users.* FROM users LIMIT 1) AS anon_1
LEFT OUTER JOIN articles AS articles_1 ON anon_1.id = articles_1.user_id;
```

Notice that SQLAlchemy moves the `LIMIT 1` into a subquery. If it simply wrote `... LEFT OUTER JOIN articles ... LIMIT 1`, the database would return only **one joined row**, i.e. the user with only **one** of their articles. Limiting the users first and then joining keeps the whole collection.

A JOIN repeats the user's columns once per article, which is why joined loading suits many-to-one / one-to-one relationships best.

#### Pros

- Reduces the number of queries by loading related data in a single query.
- Can be more efficient when you know you will need the related data.
- Works best for many-to-one and one-to-one relationships (e.g. `article.author`).

#### Cons

- Can lead to larger result sets and increased memory usage if there are many related records, because the parent row is repeated for every child row.
- For collections (one-to-many / many-to-many), `selectin` is usually the better eager strategy.
- Wasted work when the related data is not needed.

### Subquery Loading or Eager on Subquery

Load the related data using a second query that is sent immediately after the parent query. The second query **re-runs the original parent query as a subquery** and joins it to the related table. This avoids repeating parent rows like joined loading does. (It is an older strategy; `selectin` is generally preferred today.)

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
# Both queries run here, inside .first()
articles = user.articles  # No additional query is executed to load the articles.
```

#### Equivalent SQL

```sql
SELECT * FROM users LIMIT 1;  -- query 1: the parent query
SELECT articles.*, anon_1.id   -- query 2: sent immediately, re-runs query 1 as a subquery
FROM (SELECT users.id FROM users LIMIT 1) AS anon_1
JOIN articles ON anon_1.id = articles.user_id;
```

#### Pros

- Always exactly 2 queries, no matter how many parents are loaded (no N+1 problem).
- Parent rows are not repeated as in joined loading.

#### Cons

- The original query is executed twice (once as a subquery), which can be expensive for complex queries.
- `selectin` usually does the same job more simply and efficiently.

### Eager Loading - Select In Loading

Load the related data using a second query that is sent **immediately after the parent query** (it is an *eager* strategy). The second query collects the primary keys of all loaded parents and fetches their children with one `WHERE ... IN (...)` query. This avoids the N+1 problem when we need the related data of many records, and is the recommended eager strategy for collections.

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
# Two queries run here: one for users, one IN-query for the articles of all those users.
for user in users:
    articles = user.articles  # Already loaded: no query is executed here.
```

#### Equivalent SQL

```sql
SELECT * FROM users;  -- query 1: load all users
SELECT * FROM articles WHERE user_id IN (?, ?, ?, ...);  -- query 2: sent right after query 1, loads the articles of all users at once
```

#### Pros

- Reduces the number of queries by loading related data for multiple records in a single query.
- Can be more efficient when you need to access the related data for multiple records.
- Recommended eager strategy for one-to-many and many-to-many collections.

#### Cons

- Always one extra query (but only one, not N).
- Very large `IN` lists are split into batches (500 keys per batch by default).

### Lazy Loading - Dynamic Loading

Accessing the attribute does **not** load anything; instead it returns a query object (`AppenderQuery`) for the related rows. We can add `.filter()`, `.order_by()`, `.count()` etc. before executing it. Every time we iterate it or call `.all()`, a **new** query is sent (results are not cached). It only works for collections (one-to-many / many-to-many) and is considered legacy in SQLAlchemy 2.x (the replacement is `lazy='write_only'`).

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
    author = db.relationship('User', back_populates='articles')  # many-to-one side cannot be dynamic

user = User.query.first()
articles_query = user.articles  # No query yet: returns a query object that can be further filtered
articles = articles_query.all()  # This executes the query to load the articles.
recent = user.articles.filter(Article.title.like('Flask%')).all()  # another, filtered query
```

#### Equivalent SQL

```sql
SELECT * FROM users LIMIT 1;  -- executed by User.query.first()
SELECT * FROM articles WHERE ? = articles.user_id;  -- executed each time the articles query is run
```

Using `lazy='dynamic'` on the many-to-one side (`Article.author`) raises `InvalidRequestError: 'dynamic' loaders cannot be used with many-to-one/one-to-one relationships`.

#### Pros

- Provides full control over the query used to load the related data (filter, order, count, paginate).
- Useful for very large collections that we never want to load completely.

#### Cons

- A new query on every access, so looping over many parents still causes the N+1 problem.
- Cannot be combined with eager loading; collections only; legacy in SQLAlchemy 2.x.

### No Loading - No Load

Do not load the related data at all. Accessing the attribute returns an empty list `[]` for a collection (or `None` for a single object), even if related rows exist in the database. This can be useful when you want to prevent accidental loading of related data, but it can silently give wrong-looking results. `noload` is deprecated as of SQLAlchemy 2.1; prefer `raise`.

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
# The articles are never loaded.
articles = user.articles  # [] (empty list), and no query is executed.
```

#### Equivalent SQL

```sql
SELECT * FROM users LIMIT 1;  -- This query is executed when we access the user
-- No query is executed to load the articles; user.articles is an empty list.
```

#### Pros

- Prevents accidental loading of related data, which can improve performance in some cases.
- Can be useful when you want to explicitly control when related data is loaded.
- Can be efficient for one-to-many relationships when you do not always need to access the related data.

#### Cons

- Can lead to confusion: an empty list looks like "this user has no articles".

### No Loading - Raise

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
    articles = user.articles  # raises sqlalchemy.exc.InvalidRequestError, no query is executed
except Exception as e:
    print(f"Error: {e}")  # Error: 'User.articles' is not available due to lazy='raise'
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

## Cascade Options

Cascade options define how changes to a parent object should affect related child objects in a relationship. Cascade happens when you perform operations like delete, update, or save on a parent object, and you want those operations to automatically propagate to related child objects.

Cascade options can be specified in the ForeignKey (database level) or in the relationship using the `cascade` parameter (ORM level). Let's see both of the cases in details.

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
| `RESTRICT` | Prevents deletion or update of the parent record if there are related records (checked immediately). |
| `NO ACTION` | The **default**. Also rejects the change if related records exist; the difference from RESTRICT is only *when* it is checked (at the end of the statement, or at commit if the constraint is declared `DEFERRABLE INITIALLY DEFERRED`). |

`ondelete=...` produces the SQL clause `ON DELETE <action>` and `onupdate=...` produces `ON UPDATE <action>`.

> **NOTE:** By default, `sqlite3` does not enforce foreign key constraints, so you need to enable it explicitly by executing `PRAGMA foreign_keys = ON;` after establishing a connection to the database. In other databases like PostgreSQL and MySQL, foreign key constraints are enforced by default. You can enable foreign key constraints in SQLite by adding the following code to your application:

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```

Without enabling foreign key constraints, the cascade options specified in the foreign key definition will not be enforced, and related records will not be automatically deleted or updated when a parent record is deleted or updated. This leads to potential data integrity issues, as orphaned records may remain in the database without the expected cascading behavior.

#### `ondelete='CASCADE'` and the ORM: `passive_deletes`

Even with foreign keys enabled, the model above does **not** delete the articles when we do `db.session.delete(user)`. The relationship's default cascade (`save-update, merge`) makes the ORM first load the user's articles and set their `user_id` to `NULL` (so they are no longer "pointing" to a row that is going away), and only then delete the user. By the time the `DELETE` reaches the database there are no children left referencing the user, so `ON DELETE CASCADE` never fires and we are left with orphan articles (`user_id = NULL`).

```sql
-- what SQLAlchemy actually sends for db.session.delete(user)
SELECT * FROM articles WHERE ? = articles.user_id;
UPDATE articles SET user_id = NULL WHERE articles.id = ?;   -- for every article
DELETE FROM users WHERE users.id = ?;
```

To let the database do the cascade, tell the ORM not to touch the children:

```python
articles = db.relationship('Article', back_populates='author', passive_deletes=True)
```

Or let the ORM delete them itself with `cascade='all, delete-orphan'` (next section).

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

In this example, we have specified `cascade='all, delete-orphan'` for the `articles` relationship in the `User` model. This means that if a `User` record is deleted with `db.session.delete(user)`, all related `Article` records will also be deleted automatically (due to the `delete` cascade included in `all`). Additionally, if an `Article` record is removed from the `articles` relationship of a `User`, it will be automatically deleted from the database (due to the `delete-orphan` option).

#### Common Cascade Options in Relationships

| Option          | Description                                                                 |
| --------------  | --------------------------------------------------------------------------- |
| `all`           | Shortcut for `save-update, merge, refresh-expire, expunge, delete`. It does **not** include `delete-orphan`, which is why we write `"all, delete-orphan"`. |
| `delete`        | Deletes related records when the parent record is deleted.|
| `delete-orphan` | Deletes related records that are removed from the relationship (de-associated from their parent). |
| `save-update`   | When the parent is added to the session, related records are added too (so they get saved on commit). |
| `merge`         | Merges related records when the parent record is merged. |
| `refresh-expire`| Refreshes or expires related records when the parent record is refreshed or expired. |
| `expunge`       | Removes related records from the session when the parent is expunged. |
| `none`          | No cascade behavior is applied (`cascade=""` does the same). |

If we don't pass `cascade`, the default is `"save-update, merge"`.

### Difference between ForeignKey Cascade and Relationship Cascade

The cascade options specified in a foreign key definition (using `ondelete` and `onupdate`) are enforced at the database level, while the cascade options specified in a relationship definition (using the `cascade` parameter in `db.relationship()`) are enforced at the application level by SQLAlchemy's ORM.

The ORM level cascades only run when we work through ORM objects (`db.session.delete(obj)`). They are bypassed by raw SQL and also by bulk statements such as `User.query.filter(...).delete()`. The database level rules are applied by the database itself, regardless of how the data is changed — as long as they are enforced (in SQLite only on connections where `PRAGMA foreign_keys=ON` was run).

## Summary

In this module, we have learned how to define relationships between models, keep both sides in sync with `back_populates`, choose loading strategies for related data, and configure cascades at the database and ORM level. We have also seen the equivalent SQL commands for loading related data. Understanding these concepts is crucial for effectively using Flask SQLAlchemy to manage your database and optimize performance when working with related data.
