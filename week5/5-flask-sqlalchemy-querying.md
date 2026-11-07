# Querying Database with Flask-SQLAlchemy

In this section, we will learn more about querying the database using Flask-SQLAlchemy. We will cover the following topics:

- Query object
- Query Methods
- Projecting results
- Filtering results
- SqlAlchemy operators
- Ordering results
- Limiting results
- Pagination
- Aggregating results
- Using raw SQL queries

For the examples in this section, we will use the following `User` model:

```python
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'   # without this, Flask-SQLAlchemy would name the table 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    budget = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
```

And we will assume that we have some sample data in our database:

```python

user1 = User(username='Alice', city='New York', budget=1000.0)
user2 = User(username='Bob', city='Los Angeles', budget=1500.0)
user3 = User(username='Charlie', city='Chicago', budget=800.0)
user4 = User(username='David', city='New York', budget=1200.0)
user5 = User(username='Eve', city='Los Angeles', budget=900.0)
db.session.add_all([user1, user2, user3, user4, user5])
db.session.commit()
```

> All the snippets below must run inside an application context (`with app.app_context():` or inside a view function).

## Query Object

In Flask-SQLAlchemy, the `query` object (the *legacy* `Query` API) is used to query the database. It still works fully in Flask-SQLAlchemy 3.x, but the modern SQLAlchemy 2.0 style is `db.session.execute(db.select(User)...)` (see the end of this page and the *Select vs Query API* note). It provides various methods to filter, order, and manipulate the results. The basic syntax for querying a model is as follows:

```python
query_object = db.session.query(User)
results = query_object.method()

# or 

query_object = User.query
results = query_object.method()
```

When we call the `query` method from db.session with `User`, we get a query object based on a select statement for the `User` model, which looks like this:

```sql
SELECT users.id AS users_id,
users.username AS users_username,
users.city AS users_city,
users.budget AS users_budget
FROM users
```

> [!NOTE]
> **`Model.query` vs `db.session.query(Model)`**
>
> The `query` object provided by Model itself is just a convenient shortcut to `db.session.query(Model)`. Both of them will give you the same query object that you can use to perform various operations on the database.
>
> ```python
> # Both of these will give you the same query object
> query1 = db.session.query(User)
> query2 = User.query
> print(type(query1))  # <class 'flask_sqlalchemy.query.Query'>
> print(type(query2))  # <class 'flask_sqlalchemy.query.Query'>
> ```

In this section, we will be using `db.session.query(User)` to demonstrate the querying capabilities of Flask-SQLAlchemy. However, you can also use `User.query` if you prefer a more concise syntax.

## Query Methods

The `query` object provides various methods to manipulate and get the results from the query. We will explore a few important ones in some details here:

### `.get`

The `.get` method is used to retrieve a single record by its primary key. It takes the primary key value as an argument and returns the corresponding record if it exists, or `None` if it does not find the record for the given key. 

The `.get` method can be invoked in two ways:

- Using the `query` object: `Model.query.get(primary_key_value)`. This is a *legacy* feature (it still works but emits a `LegacyAPIWarning` in SQLAlchemy 2.x).
- Directly on the session: `db.session.get(Model, primary_key)`. Recommended in SQLAlchemy 2.x.

Both do the same job: they first look in the session's *identity map* (objects already loaded) and only send a `SELECT` if the object is not there.

```python
# assuming the database we have created earlier
user1 = db.session.query(User).get(1)
user2 = User.query.get(6) # there is no user with id 6
user3 = db.session.query(User).get(2)
user4 = db.session.get(User, 3)
print(user1)  # <User Alice>
print(user2)  # None
print(user3)  # <User Bob>
print(user4)  # <User Charlie>
```

### `.get_or_404`

We can further extend the functionality of `.get` method by using `.get_or_404` method. This method is commonly used in Flask applications to handle cases where a requested resource is not found. It works similarly to `.get`, but instead of returning `None` when the record is not found, it raises a `404 Not Found` error.

```python
user1 = db.session.query(User).get_or_404(1)   # legacy Query style
user2 = db.session.query(User).get_or_404(6)   # raises werkzeug.exceptions.NotFound (404)

user3 = db.get_or_404(User, 1)                 # modern Flask-SQLAlchemy 3.x style
```

`get_or_404` (and `first_or_404`, `one_or_404`, `paginate`) are Flask-SQLAlchemy additions; they are available on `db.session.query(...)` only because Flask-SQLAlchemy configures the session to use its own `Query` class.

### `.first`

The `.first` method is used to retrieve the first record that matches the query criteria. It returns the first record if it exists, or `None` if no records match the criteria.

```python
first_user = db.session.query(User).first()
print(first_user)  # <User Alice>
```

- `.first` does not guarantee any specific order of the results unless you explicitly specify an order using `.order_by`. If you want to ensure a specific order, you should use `.order_by` before calling `.first`.
- We can also use `.first_or_404` method, which works similarly to `.first`, but raises a `404 Not Found` error if no records match the criteria.
- `.first()` → applies LIMIT 1 at SQL level.

### `.one`

The `.one` method is used to retrieve exactly one record that matches the query criteria. It returns the record if it exists, but raises `sqlalchemy.exc.NoResultFound` if there are no records and `sqlalchemy.exc.MultipleResultsFound` if more than one record matches.

```python
try:
    user = db.session.query(User).filter_by(username='Alice').one()
    print(user)  # <User Alice>
except Exception as e:
    print(e)
```

We can also use `.one_or_404`.

### `.all`

The `.all` method is used to retrieve all records that match the query criteria. It returns a list of records, which can be empty if no records match the criteria.

```python
all_users = db.session.query(User).all()
print(all_users)  # [<User Alice>, <User Bob>, <User Charlie>, <User David>, <User Eve>]
```

### `.scalar`

The `.scalar` method is used to retrieve a single value from the query. It returns the value of the first column of the result. If no records match the criteria, it returns `None`. If **more than one** record matches, it raises `MultipleResultsFound` (internally the legacy `Query.scalar()` calls `.one()`).

```python
# .first() on a column query returns a Row (tuple-like)
username = db.session.query(User.username).first()
print(username)  # ('Alice',)

# .scalar() returns the bare value, but the query must match at most one row
username = db.session.query(User.username).filter_by(id=1).scalar()
print(username)  # Alice

db.session.query(User.username).scalar()  # 5 rows -> raises MultipleResultsFound
```

Typical use of `.scalar()` is with aggregate queries which always return one row, e.g. `db.session.query(func.count(User.id)).scalar()`.

**Careful:** in the SQLAlchemy 2.0 style, `db.session.execute(select(User.username)).scalar()` is *not* strict: it simply returns the first column of the first row. Its strict version is `.scalar_one()`.

### `.count`

The `.count` method is used to count the number of records that match the query criteria. It returns an integer representing the count.

```python
user_count = db.session.query(User).count()
print(user_count)  # 5
```

### `.distinct`

The `.distinct` method is used to return only distinct (unique) records that match the query criteria. It eliminates duplicate records from the result set.

```python
# Get distinct cities of users
distinct_cities = db.session.query(User.city).distinct().all()
print(distinct_cities)  # [('New York',), ('Los Angeles',), ('Chicago',)]
```

There are many more methods available in the `query` object that allow you to manipulate and retrieve data from the database in various ways. You can refer to the Flask-SQLAlchemy documentation for a comprehensive list of query methods and their usage.

## Projecting Results

We can project specific columns or entities from the database using various methods provided by the `query` object. This allows us to retrieve only the data we need, which can improve performance and reduce memory usage.

Projecting results can be done using the following methods:

### `.with_entities`

The `.with_entities` method is used to specify which columns or entities should be included in the result set. It allows you to project specific columns instead of retrieving entire records.

```python
# Get the usernames and cities of users
usernames_and_cities = db.session.query(User).with_entities(User.username, User.city).all()
print(usernames_and_cities)
# [('Alice', 'New York'), ('Bob', 'Los Angeles'), ('Charlie', 'Chicago'), ('David', 'New York'), ('Eve', 'Los Angeles')]
```

### `db.session.query(*entities)`

Alternatively, you can also specify the entities directly in the `query` method to achieve the same result as `.with_entities`.

```python
# Get the usernames and cities of users
usernames_and_cities = db.session.query(User.username, User.city).all()
print(usernames_and_cities)
# [('Alice', 'New York'), ('Bob', 'Los Angeles'), ('Charlie', 'Chicago'), ('David', 'New York'), ('Eve', 'Los Angeles')]
```

### `.label`

The `.label` method is used to label the columns in the result set. This can be useful when projecting specific columns to avoid ambiguity in the column names.

```python
# Get the usernames of users with labels    
usernames_with_labels = User.query.with_entities(User.username.label('user_name')).all()
usernames_cities_with_labels = db.session.query(User.username.label('user_name'), User.city.label('city')).all()

print(usernames_with_labels)  # [('Alice',), ('Bob',), ('Charlie',), ('David',), ('Eve',)]
print(usernames_cities_with_labels)  # [('Alice', 'New York'), ('Bob', 'Los Angeles'), ('Charlie', 'Chicago'), ('David', 'New York'), ('Eve', 'Los Angeles')]

# the label does not show up in the tuple repr; it becomes the attribute/key name of each row
row = usernames_with_labels[0]
print(row.user_name)             # Alice
print(list(row._mapping.keys())) # ['user_name']
```

### `.add_columns`

The `.add_columns` method is used to add additional columns to the result set while still retrieving the entire record. This allows you to project specific columns along with the full records.

Useful when we want to include some other columns along with the repr.

```python
# Get the full user records along with their usernames
users_with_usernames = db.session.query(User).add_columns(User.username).all()
print(users_with_usernames)
# [(<User Alice>, 'Alice'), (<User Bob>, 'Bob'), (<User Charlie>, 'Charlie'), (<User David>, 'David'), (<User Eve>, 'Eve')]
```

## Filtering Results

Filtering results is a common operation when querying a database. Flask-SQLAlchemy provides several methods to filter the results based on specific criteria. The most commonly used filtering methods are:

### `.filter_by`

The `.filter_by` method is used to filter results based on keyword arguments. It takes column names as keyword arguments and their corresponding values to filter the results.

```python
# Get users from New York
ny_users = db.session.query(User).filter_by(city='New York').all()
print(ny_users)  # [<User Alice>, <User David>]
```

It is important to note that `.filter_by` is a more concise way to filter results based on simple equality conditions. However, it does not support more complex filtering criteria such as comparisons, logical operators, or functions. For more complex filtering, you should use the `.filter` method.

### `.filter`

The `.filter` method is used to apply filtering criteria to the query. It takes one or more conditions as arguments and returns a new query object with the applied filters.

```python
# Get users with a budget greater than 1000
rich_users = db.session.query(User).filter(User.budget > 1000).all()
print(rich_users)  # [<User Bob>, <User David>]
```

The `.filter` method allows you to use a wide range of operators and functions to create complex filtering criteria. You can combine multiple conditions using logical operators such as `and_`, `or_`, and `not_` from the `sqlalchemy` library. Passing several conditions to `.filter(a, b)` (or chaining `.filter(a).filter(b)`) also combines them with AND.

```python
from sqlalchemy import and_, or_
# Get users from New York with a budget greater than 1000
ny_rich_users = db.session.query(User).filter(and_(User.city == 'New York', User.budget > 1000)).all()
print(ny_rich_users)  # [<User David>]
```

### `.filter_by` vs `.filter`

The main difference between `.filter_by` and `.filter` is that `.filter_by` is a more concise way to filter results based on simple equality conditions, while `.filter` allows for more complex filtering criteria using a wider range of operators and functions.

```python
# Using .filter_by for simple equality condition
ny_users = db.session.query(User).filter_by(city='New York').all()
print(ny_users)  # [<User Alice>, <User David>]

# Using .filter for more complex conditions
ny_rich_users = db.session.query(User).filter(and_(User.city == 'New York', User.budget > 1000)).all()
print(ny_rich_users)  # [<User David>]
```

## SQLAlchemy Operators

We just saw that we can use various operators in the `.filter` method to create complex filtering criteria. SQLAlchemy provides a wide range of operators that can be used to compare column values, combine conditions, and perform various operations on the data. Some of the commonly used SQLAlchemy operators include:

- `==`: Equal to
- `!=`: Not equal to
- `<`: Less than
- `<=`: Less than or equal to
- `>`: Greater than
- `>=`: Greater than or equal to
- `in_`: In a list of values
- `not_in`: Not in a list of values (older name: `notin_`)
- `like`: Pattern matching using SQL LIKE syntax (note: in **SQLite**, `LIKE` is already case-insensitive for ASCII letters, so `like('a%')` also matches `'Alice'`)
- `ilike`: Case-insensitive pattern matching (SQLAlchemy renders it as `lower(x) LIKE lower(y)`, so it is case-insensitive on every database)
- `and_`: Logical AND operator
- `or_`: Logical OR operator
- `not_`: Logical NOT operator
- `.between(a, b)`: Between two values (a column method, e.g. `User.budget.between(900, 1200)`)
- `is_`: Is (used for comparing with `None`)
- `is_not`: Is not (used for comparing with `None`; older name: `isnot`)
- `any_` / `all_`: SQL operators (ANY, ALL) used with subqueries — **not supported by SQLite** (works on PostgreSQL)
- `.any()` / `.has()`: relationship methods that generate an `EXISTS` subquery (completely different from `any_`)
- `exists`: Used for filtering based on the existence of (related) records
- "not exists": there is no `notexists` function; negate the exists clause with `~` or `not_()`, e.g. `~query.exists()`
- **`func`: Used to call SQL functions (e.g., `func.count()`, `func.sum()`, etc.)** we will cover this in more details in the Aggregating results section.

While we will not cover example of all of these operators here, you can refer to the SQLAlchemy documentation for a comprehensive list of operators and their usage. Let's see a few of them: 

```python
from sqlalchemy import and_, or_, any_, all_, select, func
from sqlalchemy.orm import aliased

# ============================================================
# 1. IN → filter by multiple values
# ============================================================
print("\nIN operator:")
users_in = db.session.query(User).filter(
    User.city.in_(["New York", "Los Angeles"])
).all()
print(users_in)
# → Users from NY and LA

# ============================================================
# 2. LIKE → pattern matching
# ============================================================
print("\nLIKE operator:")
users_like = db.session.query(User).filter(
    User.username.like("A%")
).all()
print(users_like)
# → Names starting with 'A'

# ============================================================
# 3. EXISTS → correlated subquery
# Find users whose city has someone with budget > 1400
# ============================================================
print("\nEXISTS operator:")

U2 = aliased(User)

users_exists = db.session.query(User).filter(
    db.session.query(U2.id)
    .filter(U2.city == User.city, U2.budget > 1400)
    .exists()
).all()

print(users_exists)
# → [<User Bob>, <User Eve>]  (Los Angeles is the only city with a budget > 1400)

# NOT EXISTS -> negate with ~
users_not_exists = db.session.query(User).filter(
    ~db.session.query(U2.id)
    .filter(U2.city == User.city, U2.budget > 1400)
    .exists()
).all()
print(users_not_exists)
# → [<User Alice>, <User Charlie>, <User David>]

# ============================================================
# 4. ANY → greater than ANY (at least one)
# Compare with Chicago users
# ⚠ ANY / ALL are NOT supported by SQLite (syntax error).
#   Examples 4, 5 and BONUS only run on databases like PostgreSQL.
# ============================================================
print("\nANY operator:")

subq_any = db.session.query(User.budget).filter(User.city == "Chicago").scalar_subquery()

users_any = db.session.query(User).filter(
    User.budget > any_(subq_any)
).all()

print(users_any)
# → Budget > at least one Chicago budget (800)

# ============================================================
# 5. ALL → greater than ALL (every value)
# Compare with New York users
# ============================================================
print("\nALL operator:")

subq_all = db.session.query(User.budget).filter(User.city == "New York").scalar_subquery()

users_all = db.session.query(User).filter(
    User.budget > all_(subq_all)
).all()

print(users_all)
# → [<User Bob>]  Budget greater than ALL NY budgets (1000, 1200)

# ============================================================
# BONUS: ALL to find max budget user
# ============================================================
print("\nALL (max budget):")

subq_max = db.session.query(User.budget).scalar_subquery()

max_user = db.session.query(User).filter(
    User.budget >= all_(subq_max)
).all()

print(max_user)
# → [<User Bob>]  User with highest budget

# ============================================================
# SQLite-friendly equivalents of ANY / ALL using MIN / MAX
# ============================================================
# > ANY(...)  is the same as  > MIN(...)
users_any_sqlite = db.session.query(User).filter(
    User.budget > select(func.min(User.budget)).where(User.city == "Chicago").scalar_subquery()
).all()
print(users_any_sqlite)  # [<User Alice>, <User Bob>, <User David>, <User Eve>]

# > ALL(...)  is the same as  > MAX(...)
users_all_sqlite = db.session.query(User).filter(
    User.budget > select(func.max(User.budget)).where(User.city == "New York").scalar_subquery()
).all()
print(users_all_sqlite)  # [<User Bob>]
```

(`> ANY` equals `> MIN` and `> ALL` equals `> MAX` as long as the subquery returns at least one non-NULL value.)

## Ordering and Limiting Results

When querying a database, it is often useful to order the results based on specific columns and to limit the number of results returned. Flask-SQLAlchemy provides methods to achieve both of these operations.

### `.order_by`

The `.order_by` method is used to specify the ordering of the results based on one or more columns. You can specify ascending or descending order using the `asc()` and `desc()` functions from SQLAlchemy.

```python
from sqlalchemy import asc, desc
# Get users ordered by budget in ascending order
users_ordered_asc = db.session.query(User).order_by(asc(User.budget)).all()
print(users_ordered_asc)
# Get users ordered by budget in descending order
users_ordered_desc = db.session.query(User).order_by(desc(User.budget)).all()
print(users_ordered_desc)
```

### `.limit`

The `.limit` method is used to limit the number of results returned by the query. It takes an integer as an argument, which specifies the maximum number of records to return.

```python
# Get the top 3 users with the highest budget
top_users = db.session.query(User).order_by(desc(User.budget)).limit(3).all()
print(top_users)
```

### `.offset`

The `.offset` method is used to skip a specified number of records before returning the results. It is often used in combination with `.limit` for pagination.

```python
# Get users ordered by budget and skip the first 2 records
users_with_offset = db.session.query(User).order_by(desc(User.budget)).offset(2).all()
print(users_with_offset)
```

> [!NOTE]
> While `.limit` and `.offset` can be used for simple pagination, Flask-SQLAlchemy also provides a more convenient method called `.paginate`, which we will cover in the next section. The `.paginate` method handles both limiting and offsetting the results based on the page number and items per page.
>
> example of using `.limit` and `.offset` for pagination:
>
> ```python
> # Get the second page of users with 2 users per page
> page_number = 2
> items_per_page = 2
> users_page_2 = db.session.query(User).order_by(User.id).limit(items_per_page).offset((page_number - 1) * items_per_page).all()
> print(users_page_2)
> ```
>

## Pagination

Pagination is a common technique used to divide large result sets into smaller, more manageable pages. Flask-SQLAlchemy provides a convenient way to implement pagination using the `paginate` method.
The `paginate` method takes the page number and the number of items per page as arguments and returns a `Pagination` object that contains the results for the specified page.

```python
# Get the first page of users with 2 users per page
page1 = db.session.query(User).order_by(User.id).paginate(page=1, per_page=2)
print(page1.items)  # [<User Alice>, <User Bob>]
# Get the second page of users with 2 users per page
page2 = db.session.query(User).order_by(User.id).paginate(page=2, per_page=2)
print(page2.items)  # [<User Charlie>, <User David>]
```

The `Pagination` object returned by the `paginate` method has several attributes that can be useful for implementing pagination in your application:

- `items`: The list of items for the current page.
- `page`: The current page number.
- `per_page`: The number of items per page.
- `total`: The total number of items across all pages.
- `pages`: The total number of pages.
- `has_next`: A boolean indicating if there is a next page.
- `has_prev`: A boolean indicating if there is a previous page.
- `next_num`: The page number of the next page (`None` if there is no next page).
- `prev_num`: The page number of the previous page (`None` if there is no previous page).

Notes:
- `paginate` is a Flask-SQLAlchemy feature. The modern form is `db.paginate(db.select(User).order_by(User.id), page=1, per_page=2)`.
- If `page` and `per_page` are not passed, they are read from the request's query string (`?page=2&per_page=10`).
- By default (`error_out=True`) an out-of-range or invalid page aborts with a **404** error.

We can use these attributes to create pagination controls in our application, allowing users to navigate through the pages of results.

## Aggregating Results

Aggregating results is a common operation when working with databases, as it allows you to perform calculations and summarize data based on specific criteria. Flask-SQLAlchemy provides several methods to perform aggregation using SQL functions.

### Using SQL Functions

SQLAlchemy provides a `func` object that allows you to call SQL functions in your queries. You can use this to perform various aggregation operations such as counting, summing, averaging, etc.

```python
from sqlalchemy import func
# Count the total number of users
user_count = db.session.query(func.count(User.id)).scalar()
print(user_count)  # 5
# Get the average budget of users
average_budget = db.session.query(func.avg(User.budget)).scalar()
print(average_budget)  # 1080.0
# Get the total budget of users
total_budget = db.session.query(func.sum(User.budget)).scalar()
print(total_budget)  # 5400.0
```

### Grouping Results

You can also group results based on specific columns and perform aggregation on each group using the `group_by` method.

```python
# Get the total budget for each city
budget_by_city = db.session.query(User.city, func.sum(User.budget)).group_by(User.city).all()
print(budget_by_city)
# [('Chicago', 800.0), ('Los Angeles', 2400.0), ('New York', 2200.0)]
```

### Filtering Aggregated Results

You can also filter the results of an aggregation using the `having` method, which is used in conjunction with `group_by`.

```python
# Get cities with a total budget greater than 2000
cities_with_high_budget = db.session.query(User.city, func.sum(User.budget)).group_by(User.city).having(func.sum(User.budget) > 2000).all()
print(cities_with_high_budget)
# [('Los Angeles', 2400.0), ('New York', 2200.0)]
```

## Using Raw SQL Queries

While Flask-SQLAlchemy provides a powerful and flexible ORM for querying the database, there may be cases where you need to execute raw SQL queries directly. Flask-SQLAlchemy allows you to do this using the `db.session.execute` method.

```python
# Execute a raw SQL query to get all users
from sqlalchemy import text

result = db.session.execute(text("SELECT * FROM users"))
users = result.fetchall()
print(users)
# [(1, 'Alice', 'New York', 1000.0), (2, 'Bob', 'Los Angeles', 1500.0), ...]
```

Note that raw SQL returns plain `Row` objects (tuple-like), **not** `User` objects. Always pass values as bound parameters (`text("... WHERE city = :city")`, `{"city": city}`) instead of building the string with f-strings, to avoid SQL injection.

## The SQLAlchemy 2.0 Style: `select()`

`select()` is **not** raw SQL. It is SQLAlchemy's modern (2.0-style) way of building queries in Python; it is the recommended replacement for the legacy `Model.query` / `db.session.query()` API.

```python
from sqlalchemy import select
# Build a query with select() and execute it with the session
stmt = select(User).where(User.city == 'New York')
result = db.session.execute(stmt)
users = result.scalars().all()
print(users)  # [<User Alice>, <User David>]

# shortcut for execute(...).scalars()
users = db.session.scalars(stmt).all()
```

`db.session.execute(stmt)` returns a `Result` whose rows are tuples (here `(<User Alice>,)`); `.scalars()` takes the first element of each row, giving `User` objects.

In this section, we have not covered querying across relationships and joining tables. This is a more advanced topic that involves understanding how to define relationships between models and how to query across those relationships using joins. We will cover this topic in more detail in a later section when we discuss relationships in Flask-SQLAlchemy.

## Summary

In this section, we have covered various methods for querying the database using Flask-SQLAlchemy. These methods can be broadly classified into two categories:

1. Execution (Terminal) Methods:
   These methods execute the query and return results. Once called, the SQL query is sent to the database.

   Examples:
   - .get() → object by primary key or None
   - .first() → first row or None
   - .one() → exactly one row (strict)
   - .all() → list of rows
   - .scalar() → single value (legacy Query: raises if more than one row)
   - .count() → integer count
   - .paginate() → Pagination object
   - iterating over the query (`for u in query:`) also executes it

   (`.scalars()` is not a Query method: it belongs to the `Result` returned by `db.session.execute(select(...))`.)

2. Query Modifying Methods:
   These methods modify the query object and return a new query object. They do not execute the query.

   Examples:
   - .filter()
   - .filter_by()
   - .order_by()
   - .limit()
   - .offset()
   - .distinct()

> SQLAlchemy queries are lazy. The query is not executed until an execution method is called. (This is unrelated to "lazy loading" of relationships, which we will see later.)

