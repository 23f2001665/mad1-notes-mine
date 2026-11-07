# Base SQLAlchemy (without Flask)

::: danger Out of syllabus
In the course we always use **Flask-SQLAlchemy**. This page shows plain SQLAlchemy, the library that Flask-SQLAlchemy is built on, so that we understand what `db.Model`, `db.session` and `db.engine` really are. It is only for learning purposes and can be skipped if you lack time.
:::

Flask-SQLAlchemy does not have its own ORM. It is a thin layer that **configures SQLAlchemy for a Flask app**: it reads the database URI from `app.config`, creates the engine, gives us a ready-made base class (`db.Model`) and a session that is cleaned up after every request (`db.session`). If we remove Flask, we have to do these steps ourselves.

## Building Blocks of SQLAlchemy

| Building block | What it does | Flask-SQLAlchemy equivalent |
|---|---|---|
| **Engine** (`create_engine`) | Knows *how* to talk to the database (URI, driver, connection pool). Opens connections when needed. | `db.engine` (created from `SQLALCHEMY_DATABASE_URI`) |
| **Declarative Base** (`DeclarativeBase`) | Parent class of all our models. Collects every table in its `metadata`. | `db.Model` |
| **MetaData** | The collection of all `Table` objects; used by `create_all()` / `drop_all()`. | `db.metadata` |
| **Session** (`Session`) | The "workspace" for ORM objects: tracks `add`, changes, `delete`, and sends them in a transaction on `commit()`. | `db.session` (a *scoped* session, one per app context/request) |
| **select()** | Builds a query that the session executes. | `db.select()` (same function), or the legacy `Model.query` |

👉 `db.Column`, `db.Integer`, `db.String`, `db.ForeignKey`, `db.select`... are simply SQLAlchemy's own `Column`, `Integer`, `String`, `ForeignKey`, `select` re-exported on the `db` object for convenience. `db.relationship` is a thin wrapper around SQLAlchemy's `relationship` that only adds Flask-SQLAlchemy's `Query` class for `lazy='dynamic'` relationships and backrefs.

## Step 1: Creating the Engine

```python
from sqlalchemy import create_engine

engine = create_engine("sqlite:///example.db", echo=True)  # echo=True prints every SQL statement
```

- The URI has the same format we saw in the basics note: `dialect+driver://username:password@host:port/database`.
- Unlike Flask-SQLAlchemy, a relative SQLite path here is relative to the **current working directory**, not the `instance` folder.
- Creating the engine does not connect yet; the first connection is opened when we actually run something (lazy).

## Step 2: Defining Models

We first create our own base class, then inherit our models from it. SQLAlchemy 2.0 supports two styles of writing columns; both create exactly the same tables.

:::tabs

== Classic style (same as the course)

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"          # required in plain SQLAlchemy
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    articles = relationship("Article", back_populates="author")

    def __repr__(self):
        return f"<User {self.username}>"

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="articles")

    def __repr__(self):
        return f"<Article {self.title}>"
```

== Typed style (SQLAlchemy 2.0)

```python
from typing import List, Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True)    # Mapped[str] -> NOT NULL
    articles: Mapped[List["Article"]] = relationship(back_populates="author")

class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))  # Optional -> NULL allowed
    author: Mapped[Optional["User"]] = relationship(back_populates="articles")
```

:::

::: info Typed style in short
- The Python type decides the column type: `Mapped[int]` → `INTEGER`, `Mapped[str]` → `VARCHAR`.
- `Mapped[X]` means `nullable=False`, `Mapped[Optional[X]]` means `nullable=True`.
- `Mapped[List["Article"]]` tells SQLAlchemy the relationship is a collection (one-to-many), `Mapped["User"]` a single object, so `uselist` is rarely needed.
- Editors and type checkers (mypy, Pylance) understand these attributes, which is the main reason for this style.
:::

Differences from Flask-SQLAlchemy models:
- `__tablename__` is **required**; Flask-SQLAlchemy generates it from the class name for us.
- There is no `User.query` attribute; all queries go through a session.

## Step 3: Creating the Tables

```python
Base.metadata.create_all(engine)   # Flask-SQLAlchemy: db.create_all()
```

No application context is needed: the engine is a normal Python object, not tied to a Flask app. Like `db.create_all()`, it only creates the tables that are missing and never alters existing ones.

## Step 4: Working with a Session

In Flask-SQLAlchemy we just use `db.session` and Flask removes it at the end of each request. In plain SQLAlchemy we create a session ourselves, and the best way is a `with` block, which **closes the session automatically**.

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

# Create
with Session(engine) as session:
    alice = User(username="alice")
    alice.articles.append(Article(title="Flask Basics"))
    alice.articles.append(Article(title="SQLAlchemy ORM"))
    session.add(alice)        # the articles are added too (save-update cascade)
    session.commit()

# Read
with Session(engine) as session:
    user = session.scalars(select(User).where(User.username == "alice")).one()
    print(user)               # <User alice>
    print(user.articles)      # [<Article Flask Basics>, <Article SQLAlchemy ORM>]

    article = session.get(Article, 1)
    print(article.author)     # <User alice>

# Update
with Session(engine) as session:
    user = session.get(User, 1)
    user.username = "alice_new"
    session.commit()

# Delete
with Session(engine) as session:
    article = session.get(Article, 2)
    session.delete(article)
    session.commit()
    print(session.scalars(select(Article)).all())   # [<Article Flask Basics>]
```

::: details `session.begin()`: commit automatically
Instead of calling `commit()` ourselves we can let a block do it: the transaction is committed at the end of the block, or rolled back if an exception happens inside it.

```python
with Session(engine) as session:
    with session.begin():
        session.add(User(username="bob"))
    # committed here
```

Flask-SQLAlchemy does not commit for us: we still call `db.session.commit()` in our views.
:::

::: warning Lazy loading after the session is closed
When the `with` block ends, the session is closed and the objects become **detached**. Accessing a relationship that was not loaded yet then fails:

```python
with Session(engine) as session:
    user = session.get(User, 1)
print(user.articles)   # DetachedInstanceError: ... is not bound to a Session
```

Either access what you need inside the block, or load it eagerly (e.g. `lazy="selectin"`). In Flask-SQLAlchemy this happens less often because `db.session` lives for the whole request.
:::

## Using Your Own Base Class with Flask-SQLAlchemy

Since Flask-SQLAlchemy 3.1 we can give it our own `DeclarativeBase` class. Then `db.Model` is created from that base (it uses the base's `metadata` and settings, plus Flask-SQLAlchemy's extras such as automatic table names) and we can write models in the typed style while keeping everything else (`db.session`, `db.paginate`, `db.get_or_404`...) the same:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.db"
db = SQLAlchemy(app, model_class=Base)

class Book(db.Model):                          # __tablename__ generated: 'book'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))

with app.app_context():
    db.create_all()
    db.session.add(Book(title="Python 101"))
    db.session.commit()
    print(db.session.scalars(db.select(Book)).all()[0].title)   # Python 101
```

## Flask-SQLAlchemy vs Plain SQLAlchemy

| Task | Plain SQLAlchemy | Flask-SQLAlchemy |
|---|---|---|
| Configure database | `engine = create_engine(uri)` | `app.config['SQLALCHEMY_DATABASE_URI'] = uri` + `SQLAlchemy(app)` |
| Base class for models | `class Base(DeclarativeBase): pass` | `db.Model` |
| Table name | `__tablename__` required | generated from class name if missing |
| Create tables | `Base.metadata.create_all(engine)` | `db.create_all()` (inside app context) |
| Session | `with Session(engine) as session:` | `db.session` (removed after each request) |
| Get by primary key | `session.get(User, 1)` | `db.session.get(User, 1)` |
| Query | `session.scalars(select(User)).all()` | same, or legacy `User.query.all()` |
| 404 helpers / pagination | not available | `db.get_or_404()`, `db.first_or_404()`, `db.paginate()` |
| Needs app context | no | yes |

## Summary

- SQLAlchemy is the ORM; Flask-SQLAlchemy only wires it into Flask.
- Plain SQLAlchemy needs three things from us: an **engine**, a **declarative base** for the models and a **session** for every unit of work.
- `db.engine`, `db.Model`, `db.metadata` and `db.session` are exactly these objects, created and managed by Flask-SQLAlchemy.
- The typed style (`Mapped[...]`, `mapped_column`) is the modern SQLAlchemy 2.0 way of writing models; it can also be used in Flask-SQLAlchemy through `SQLAlchemy(model_class=Base)`.

### Extra Resources

- [SQLAlchemy 2.0 ORM Quick Start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [SQLAlchemy Unified Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/index.html)
- [Flask-SQLAlchemy: Models and Tables](https://flask-sqlalchemy.palletsprojects.com/en/stable/models/)
