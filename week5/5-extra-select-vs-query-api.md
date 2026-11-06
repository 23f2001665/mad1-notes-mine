# Select vs Query API

## Select API

Introduced in SQLAlchemy 1.4, the Select API is a modern way to construct SQL queries using Pythonic syntax. It provides a more intuitive and flexible approach to building queries compared to the traditional Query API.

Here is example of using the Select API:

```python
from sqlalchemy import select

stmt = select(User).where(User.name == 'Alice')
result = db.session.execute(stmt).scalars().all()

```

Here `stmt` is a Select object that represents the SQL query. The `where` method is used to filter the results based on the condition specified.