# Select vs Query API

## Select API

`select()` has existed in SQLAlchemy Core for a long time, but since SQLAlchemy 1.4 it can also be used for ORM queries, and in SQLAlchemy 2.0 it is the recommended way to query (the "2.0 style"). The older `Query` API (`db.session.query(User)`, `User.query`) still works but is called *legacy*. `select()` is **not** raw SQL: it is a Python object that SQLAlchemy compiles into SQL for the database we are using.

Here is example of using the Select API:

```python
from sqlalchemy import select

stmt = select(User).where(User.name == 'Alice')
result = db.session.execute(stmt).scalars().all()

```

Here `stmt` is a Select object that represents the SQL query. The `where` method is used to filter the results based on the condition specified (it plays the role of `.filter()`). Nothing is sent to the database until `db.session.execute(stmt)`; `.scalars()` turns each row `(<User>,)` into the `User` object, and `.all()` collects them into a list.

| Legacy Query API | 2.0 style |
|---|---|
| `User.query.get(1)` | `db.session.get(User, 1)` |
| `User.query.filter_by(name='Alice').first()` | `db.session.execute(select(User).filter_by(name='Alice')).scalars().first()` |
| `User.query.filter(User.age > 18).all()` | `db.session.scalars(select(User).where(User.age > 18)).all()` |
| `User.query.count()` | `db.session.scalar(select(func.count()).select_from(User))` |
| `User.query.get_or_404(1)` | `db.get_or_404(User, 1)` |
| `User.query.paginate(page=1, per_page=10)` | `db.paginate(select(User), page=1, per_page=10)` |