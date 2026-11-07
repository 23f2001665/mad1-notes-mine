# Select vs Query API

SQLAlchemy gives us two ways to write ORM queries:

- **Query API** (*legacy*): `db.session.query(User)...` and Flask-SQLAlchemy's shortcut `User.query...`. This is what we used in the querying note and what most course material uses.
- **Select API** (*2.0 style*): build a statement with `select(User)...` and run it with `db.session.execute(...)` / `db.session.scalars(...)`.

`select()` has existed in SQLAlchemy Core for a long time, but since SQLAlchemy 1.4 it can also be used for ORM queries, and in SQLAlchemy 2.0 it is the recommended way to query. The Query API still works fully and is not going to be removed soon, but the SQLAlchemy documentation calls it *legacy*.

> [!NOTE]
> **Is `select()` raw SQL?**
>
> No. `select()` is a Python object that *describes* a query. SQLAlchemy compiles it into SQL for the database we are using (SQLite, PostgreSQL, ...). Raw SQL is what we write by hand inside `text("SELECT ...")`.

For the examples we use the same model and data as the querying note:

```python
from sqlalchemy import select, func, update, delete

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    budget = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

db.create_all()
db.session.add_all([
    User(username='Alice', city='New York', budget=1000.0),
    User(username='Bob', city='Los Angeles', budget=1500.0),
    User(username='Charlie', city='Chicago', budget=800.0),
    User(username='David', city='New York', budget=1200.0),
    User(username='Eve', city='Los Angeles', budget=900.0),
])
db.session.commit()
```

👉 Flask-SQLAlchemy also exposes the same function as `db.select`, so `db.select(User)` and `select(User)` are identical.

## How the Select API Works

With the Query API, the query object builds **and** runs the query (`User.query.filter(...).all()`). With the Select API these are two separate steps:

1. **Build** a statement: `stmt = select(User).where(User.city == 'New York')`. Nothing is sent to the database.
2. **Execute** it with the session: `result = db.session.execute(stmt)`. This returns a `Result`.
3. **Shape** the result: `result.scalars().all()`, `result.first()`, `result.scalar_one()`...

```python
stmt = select(User).where(User.city == 'New York')
print(stmt)
# SELECT users.id, users.username, users.city, users.budget
# FROM users
# WHERE users.city = :city_1

result = db.session.execute(stmt)
print(result.all())          # [(<User Alice>,), (<User David>,)]   <- rows (tuples)

result = db.session.execute(stmt)
print(result.scalars().all())   # [<User Alice>, <User David>]      <- objects

print(db.session.scalars(stmt).all())   # shortcut for execute(...).scalars()
```

> [!WARNING]
> **Rows vs objects**
>
> `db.session.execute(select(User))` returns **rows**, and each row is a tuple with one element: `(<User Alice>,)`. Use `.scalars()` (or `db.session.scalars(...)`) when you want the `User` objects themselves. Forgetting `.scalars()` is the most common mistake with the Select API.

### Methods on the Result

| Method | Returns | If no rows | If more than one row |
|---|---|---|---|
| `.all()` | list of rows | `[]` | all rows |
| `.first()` | first row | `None` | returns the first, ignores the rest |
| `.one()` | the only row | raises `NoResultFound` | raises `MultipleResultsFound` |
| `.one_or_none()` | the only row | `None` | raises `MultipleResultsFound` |
| `.scalar()` | first column of the first row | `None` | returns the first, ignores the rest |
| `.scalar_one()` | first column of the only row | raises `NoResultFound` | raises `MultipleResultsFound` |
| `.scalars()` | first column of every row (`ScalarResult`, then call `.all()`, `.first()`, `.one()`...) | | |

Careful: the legacy `Query.scalar()` behaves like `scalar_one_or_none()`: it **raises** when there is more than one row, while `Result.scalar()` does not.

## Side by Side Comparison

### Get by Primary Key

**Query API**

```python
user = User.query.get(1)              # legacy, emits LegacyAPIWarning
user = db.session.query(User).get(1)  # legacy
```

**Select API**

```python
user = db.session.get(User, 1)        # <User Alice>, or None if not found
```

### Filtering

**Query API**

```python
ny_users = User.query.filter_by(city='New York').all()
rich_users = User.query.filter(User.budget > 1000).all()
first_rich = User.query.filter(User.budget > 1000).first()
```

**Select API**

```python
ny_users = db.session.scalars(select(User).filter_by(city='New York')).all()
rich_users = db.session.scalars(select(User).where(User.budget > 1000)).all()
first_rich = db.session.scalars(select(User).where(User.budget > 1000)).first()
```

`where()` is the Select API name for `filter()`; `select()` also accepts `.filter()` and `.filter_by()`, so old habits still work. All the operators (`==`, `in_`, `like`, `and_`, `or_`, ...) are exactly the same in both APIs.

### Ordering and Limiting

**Query API**

```python
top3 = User.query.order_by(User.budget.desc()).limit(3).all()
```

**Select API**

```python
top3 = db.session.scalars(select(User).order_by(User.budget.desc()).limit(3)).all()
# [<User Bob>, <User David>, <User Alice>]
```

### Selecting Specific Columns

**Query API**

```python
rows = db.session.query(User.username, User.city).all()
names = [name for (name,) in db.session.query(User.username).all()]
```

**Select API**

```python
rows = db.session.execute(select(User.username, User.city)).all()
# [('Alice', 'New York'), ('Bob', 'Los Angeles'), ...]
names = db.session.scalars(select(User.username)).all()
# ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
```

Here `.scalars()` is handy: it gives a plain list of values instead of one-element tuples.

### Counting and Aggregates

**Query API**

```python
count = User.query.count()
avg_budget = db.session.query(func.avg(User.budget)).scalar()
```

**Select API**

```python
count = db.session.scalar(select(func.count()).select_from(User))   # 5
avg_budget = db.session.scalar(select(func.avg(User.budget)))      # 1080.0
```

There is no `.count()` method on a `select()`; we select `func.count()` like we would in SQL. `select_from(User)` tells SQLAlchemy which table to count, because `func.count()` alone does not mention any table.

### Group By and Having

**Query API**

```python
rows = (db.session.query(User.city, func.sum(User.budget))
        .group_by(User.city)
        .having(func.sum(User.budget) > 2000)
        .all())
```

**Select API**

```python
rows = db.session.execute(
    select(User.city, func.sum(User.budget))
    .group_by(User.city)
    .having(func.sum(User.budget) > 2000)
).all()
# [('Los Angeles', 2400.0), ('New York', 2200.0)]
```

### Pagination and 404 Helpers (Flask-SQLAlchemy)

**Query API**

```python
page = User.query.order_by(User.id).paginate(page=1, per_page=2)
user = User.query.get_or_404(1)
user = User.query.filter_by(username='Alice').first_or_404()
```

**Select API**

```python
page = db.paginate(select(User).order_by(User.id), page=1, per_page=2)
user = db.get_or_404(User, 1)
user = db.first_or_404(select(User).filter_by(username='Alice'))
```

### Bulk Update and Delete

**Query API**

```python
User.query.filter(User.city == 'Chicago').update({User.budget: 850.0})
User.query.filter(User.budget < 900).delete()
db.session.commit()
```

**Select API**

```python
db.session.execute(update(User).where(User.city == 'Chicago').values(budget=850.0))
db.session.execute(delete(User).where(User.budget < 900))
db.session.commit()
```

Both are bulk statements: they run a single `UPDATE`/`DELETE` in the database and do not apply ORM relationship cascades (see the update-and-delete note).

## Quick Reference

| Task | Query API (legacy) | Select API (2.0 style) |
|---|---|---|
| All rows | `User.query.all()` | `db.session.scalars(select(User)).all()` |
| By primary key | `User.query.get(1)` | `db.session.get(User, 1)` |
| First match | `User.query.filter_by(city='X').first()` | `db.session.scalars(select(User).filter_by(city='X')).first()` |
| Exactly one | `User.query.filter_by(id=1).one()` | `db.session.scalars(select(User).filter_by(id=1)).one()` |
| Filter | `.filter(User.budget > 1000)` | `.where(User.budget > 1000)` |
| Count | `User.query.count()` | `db.session.scalar(select(func.count()).select_from(User))` |
| Paginate | `User.query.paginate(page=1, per_page=10)` | `db.paginate(select(User), page=1, per_page=10)` |
| 404 helper | `User.query.get_or_404(1)` | `db.get_or_404(User, 1)` |
| Bulk update | `User.query.filter(...).update({...})` | `db.session.execute(update(User).where(...).values(...))` |
| Bulk delete | `User.query.filter(...).delete()` | `db.session.execute(delete(User).where(...))` |

## Key Differences

| | Query API | Select API |
|---|---|---|
| Status | Legacy (still supported) | Recommended since SQLAlchemy 2.0 |
| Who executes | The query object itself (`.all()`, `.first()`) | The session (`execute`, `scalars`, `scalar`) |
| Return of `select(User)` / `query(User)` | `User` objects directly | Rows `(User,)`; use `.scalars()` for objects |
| Filtering method | `.filter()` / `.filter_by()` | `.where()` (also `.filter()` / `.filter_by()`) |
| Count | `.count()` | `select(func.count())` |
| Same statement object for Core and ORM | No | Yes (`select()` works with or without the ORM, and with async sessions) |

<details>
<summary>Which one should I use?</summary>

Both produce the same SQL and either is fine for the course and the project. Most course videos, PYQs and older tutorials use the **Query API** (`User.query...`), so we must be able to read it. For new code, the SQLAlchemy and Flask-SQLAlchemy documentation use the **Select API**, and it avoids the `LegacyAPIWarning` messages. Mixing both in one project works but is harder to read, so pick one style and stay consistent.

</details>

## Summary

- The Query API (`User.query`, `db.session.query`) builds and runs the query in one object; it is the legacy style.
- The Select API separates **building** (`select(...)`) from **executing** (`db.session.execute/scalars/scalar`); it is the SQLAlchemy 2.0 style.
- `execute(select(User))` returns rows; `.scalars()` turns them into `User` objects.
- Filters, operators, ordering, grouping and joins are written the same way in both; only the start (`select(User)`) and the end (`db.session.scalars(...).all()`) change.
- Flask-SQLAlchemy helpers have Select API versions: `db.get_or_404`, `db.first_or_404`, `db.one_or_404`, `db.paginate`.

### Extra Resources

- [SQLAlchemy 2.0 Migration: ORM Querying](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html#orm-query-unified-with-core-select)
- [SQLAlchemy: Legacy Query API](https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html)
- [Flask-SQLAlchemy: Modifying and Querying Data](https://flask-sqlalchemy.palletsprojects.com/en/stable/queries/)
