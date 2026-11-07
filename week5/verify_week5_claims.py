"""
Week 5 Flask-SQLAlchemy notes -- claim checker.

Every check below takes one statement (or code snippet) from the week5 notes,
runs it on a real in-memory SQLite database, and reports whether the notes are
right:

    OK     -> the notes say what actually happens
    WRONG  -> the notes say something that does not happen (the evidence shows what does)

The claims are written as the notes state them *after* the accuracy fixes, so a
clean run ends with "0 WRONG". If a library upgrade changes behaviour, the
affected check turns WRONG and points to the note that needs updating.

Run:
    pip install flask flask-sqlalchemy
    python verify_week5_claims.py            # all checks
    python verify_week5_claims.py -v         # also print the SQL that was emitted

Checked against Flask-SQLAlchemy 3.1 / SQLAlchemy 2.x.
"""
import sys
import warnings
from contextlib import contextmanager
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import all_, any_, event, func, inspect, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import CascadeOptions, aliased

VERBOSE = "-v" in sys.argv
RESULTS = []


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def check(file, claim, fn):
    """fn() returns (notes_are_correct: bool, evidence: str)."""
    try:
        ok, evidence = fn()
    except Exception as e:  # a crash in a snippet the notes say works = WRONG
        ok, evidence = False, f"raised {type(e).__name__}: {str(e).splitlines()[0][:150]}"
    RESULTS.append((ok, file))
    print(f"[{'OK   ' if ok else 'WRONG'}] {file}\n        claim   : {claim}\n        actual  : {evidence}\n")


def raises(fn):
    """Run fn; return 'ExcName: message' or None if it did not raise."""
    try:
        fn()
    except Exception as e:
        return f"{type(e).__name__}: {str(e).splitlines()[0][:150]}"
    return None


def new_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"   # in-memory database
    return app, SQLAlchemy(app)


@contextmanager
def capture_sql(db):
    """Collect the SQL statements emitted inside the block."""
    stmts = []

    def listener(conn, cursor, statement, params, context, many):
        stmts.append(" ".join(statement.split()))
        if VERBOSE:
            print("        SQL>", stmts[-1][:200])

    event.listen(db.engine, "before_cursor_execute", listener)
    try:
        yield stmts
    finally:
        event.remove(db.engine, "before_cursor_execute", listener)


@event.listens_for(Engine, "connect")
def _sqlite_fk_on(dbapi_connection, _):
    cur = dbapi_connection.cursor()
    cur.execute("PRAGMA foreign_keys=ON")   # as recommended in relationship-part-1
    cur.close()


warnings.simplefilter("ignore")  # we look for specific warnings explicitly below


# =========================================================================== #
# 1. 5-flask-sqlalchemy-basics.md
# =========================================================================== #
F = "5-flask-sqlalchemy-basics.md"
print("=" * 78 + f"\n{F}\n" + "=" * 78)

app, db = new_app()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


with app.app_context():
    db.create_all()
    db.session.add_all([User(username="john_doe", email="john@example.com"),
                        User(username="jane_doe", email="jane@example.com")])
    db.session.commit()

    def _legacy_get():
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            User.query.get(1)
        names = {type(x.message).__name__ for x in w}
        return "LegacyAPIWarning" in names and db.session.get(User, 1) is not None, f"User.query.get(1) emits {names or 'no warning'}; db.session.get(User, 1) works"
    check(F, "`User.query.get(1)` is legacy (LegacyAPIWarning); use `db.session.get(User, 1)`", _legacy_get)

    check(F, "`.first()` returns None when nothing matches",
          lambda: ((r := User.query.filter_by(username="nobody").first()) is None, f"returned {r!r}"))

    def _create_all_alter():
        # add a column to the model's Table *after* the table exists, then create_all again
        db.metadata.tables["user"].append_column(db.Column("age", db.Integer))
        db.create_all()
        cols = [c["name"] for c in inspect(db.engine).get_columns("user")]
        db.metadata.tables["user"]._columns.remove(db.metadata.tables["user"].c.age)
        return "age" not in cols, f"after adding a column + create_all(), DB columns = {cols}"
    check(F, "create_all() is safe to re-run but never ALTERs an existing table", _create_all_alter)

    def _unique_violation():
        u = db.session.get(User, 1)
        u.email = "jane@example.com"
        err = raises(db.session.commit)
        after = raises(lambda: User.query.all())   # session unusable until rollback?
        db.session.rollback()
        return (err or "").startswith("IntegrityError") and (after or "").startswith("PendingRollbackError"), f"commit -> {err[:70]}; using session before rollback -> {(after or 'works')[:60]}"
    check(F, "duplicate email -> IntegrityError at commit; must rollback() before reusing session", _unique_violation)

    def _delete_none():
        err = raises(lambda: db.session.delete(User.query.filter_by(username="nobody").first()))
        return err is not None, f"db.session.delete(None) -> {err}"
    check(F, "always check the record exists before delete", _delete_none)

with app.test_request_context():
    check(F, "app.test_request_context() (dummy request) also pushes an app context",
          lambda: (User.query.count() == 2, "app.test_request_context() -> User.query.count() works"))


# ---- object states -------------------------------------------------------- #
def states(obj):
    i = inspect(obj)
    return [s for s in ("transient", "pending", "persistent", "deleted", "detached") if getattr(i, s)][0]


with app.app_context():
    trace = []
    u = User(username="state", email="s@example.com"); trace.append(("User(...)", states(u)))
    db.session.add(u);                                trace.append(("add()", states(u)))
    db.session.flush();                               trace.append(("flush() (no commit)", states(u)))
    db.session.delete(u);                             trace.append(("delete()", states(u)))
    db.session.flush();                               trace.append(("flush()", states(u)))
    db.session.commit();                              trace.append(("commit()", states(u)))
    loaded = User.query.first();                      q_state = states(loaded)
    db.session.expunge(loaded);                       ex_state = states(loaded)
    row_still_there = db.session.get(User, loaded.id) is not None

    t = dict(trace)
    check(F, "transient -> add() -> pending",
          lambda: ((t["User(...)"], t["add()"]) == ("transient", "pending"), f"{t['User(...)']} -> {t['add()']}"))
    check(F, "pending becomes persistent on flush (no commit needed); queried objects are persistent",
          lambda: (t["flush() (no commit)"] == "persistent" and q_state == "persistent", f"after flush: {t['flush() (no commit)']}; queried: {q_state}"))
    check(F, "detached object usually still has its row in the database",
          lambda: (ex_state == "detached" and row_still_there, f"after expunge(): state={ex_state}, row still in DB = {row_still_there}"))
    check(F, "after delete() still persistent; deleted after flush; detached after commit",
          lambda: ((t["delete()"], t["flush()"], t["commit()"]) == ("persistent", "deleted", "detached"),
                   f"delete(): {t['delete()']}; flush(): {t['flush()']}; commit(): {t['commit()']}"))


# =========================================================================== #
# 2. 5-table-creation.md
# =========================================================================== #
F = "5-table-creation.md"
print("=" * 78 + f"\n{F}\n" + "=" * 78)

app2, db2 = new_app()


def _both_definitions():
    users = db2.Table("users", db2.Column("id", db2.Integer, primary_key=True))   # Option 1 (no metadata arg)
    in_meta = users.metadata is db2.metadata

    def option2_as_well():
        class UserX(db2.Model):
            __tablename__ = "users"
            id = db2.Column(db2.Integer, primary_key=True)
    err = raises(option2_as_well)
    db2.metadata.remove(users)
    return in_meta and (err or "").startswith("InvalidRequestError"), f"db.Table auto-uses db.metadata={in_meta}; defining both -> {err[:70]}"


check(F, "db.Table / model are alternatives: defining both 'users' raises InvalidRequestError", _both_definitions)


class OrderItem(db2.Model):
    id = db2.Column(db2.Integer, primary_key=True)


check(F, "no __tablename__ -> name based on class name ('User' -> 'user')",
      lambda: (OrderItem.__tablename__ == "order_item", f"OrderItem -> '{OrderItem.__tablename__}' (CamelCase -> snake_case, Flask-SQLAlchemy only)"))


class Product(db2.Model):
    id = db2.Column(db2.Integer, primary_key=True)
    name = db2.Column(db2.String(5), nullable=False)
    price = db2.Column(db2.Numeric(4, 2))
    active = db2.Column(db2.Boolean, default=True)
    created = db2.Column(db2.DateTime, default=datetime.now)


with app2.app_context():
    db2.create_all()

    def _string_len():
        db2.session.add(Product(name="x" * 50, price=12345.678)); db2.session.commit()
        p = db2.session.execute(text("select name, price from product")).first()
        return len(p.name) == 50, f"String(5) stored {len(p.name)} chars, Numeric(4,2) stored {p.price}"
    check(F, "SQLite does not enforce String(n) length or Numeric precision", _string_len)

    check(F, "nullable=False does not forbid empty string",
          lambda: (raises(lambda: (db2.session.add(Product(name="")), db2.session.commit())) is None, "Product(name='') inserted fine"))

    def _default_in_ddl():
        ddl = db2.session.execute(text("select sql from sqlite_master where name='product'")).scalar()
        p = db2.session.get(Product, 2)
        return "DEFAULT" not in ddl and p.active is True, f"row without value got active={p.active}; CREATE TABLE has DEFAULT clause = {'DEFAULT' in ddl}"
    check(F, "default= is applied by SQLAlchemy (Python side), not written into CREATE TABLE", _default_in_ddl)

    def _server_default():
        class Status(db2.Model):
            id = db2.Column(db2.Integer, primary_key=True)
            status = db2.Column(db2.String(10), server_default="new")
        db2.create_all()
        ddl = db2.session.execute(text("select sql from sqlite_master where name='status'")).scalar()
        db2.session.execute(text("insert into status (id) values (1)"))
        v = db2.session.execute(text("select status from status")).scalar()
        return "DEFAULT" in ddl and v == "new", f"DDL has DEFAULT, raw INSERT got status={v!r}"
    check(F, "server_default= is in CREATE TABLE and applies to raw SQL inserts", _server_default)

    def _callable_default():
        a = Product(name="a"); db2.session.add(a); db2.session.commit()
        b = Product(name="b"); db2.session.add(b); db2.session.commit()
        return a.created != b.created, f"default=datetime.now gives each row its own time: {a.created.time()} vs {b.created.time()}"
    check(F, "default=datetime.now (callable) is evaluated per row", _callable_default)

    def _autoinc():
        ddl = db2.session.execute(text("select sql from sqlite_master where name='product'")).scalar()
        class Ticket(db2.Model):
            __table_args__ = {"sqlite_autoincrement": True}
            id = db2.Column(db2.Integer, primary_key=True)
        db2.create_all()
        ddl2 = db2.session.execute(text("select sql from sqlite_master where name='ticket'")).scalar()
        # id reuse: delete the row with the largest id, insert again
        last = db2.session.execute(text("select max(id) from product")).scalar()
        db2.session.execute(text(f"delete from product where id={last}"))
        db2.session.add(Product(name="r")); db2.session.commit()
        reused = db2.session.execute(text("select max(id) from product")).scalar() == last
        return "AUTOINCREMENT" not in ddl and "AUTOINCREMENT" in ddl2 and reused, \
            f"no AUTOINCREMENT keyword by default, emitted with sqlite_autoincrement=True; max id reused after delete = {reused}"
    check(F, "integer PK auto-generates ids; AUTOINCREMENT keyword only with sqlite_autoincrement", _autoinc)


# =========================================================================== #
# 3. 5-flask-sqlalchemy-querying.md
# =========================================================================== #
F = "5-flask-sqlalchemy-querying.md"
print("=" * 78 + f"\n{F}\n" + "=" * 78)

app3, db3 = new_app()


class User(db3.Model):            # the notes' model
    __tablename__ = "users"
    id = db3.Column(db3.Integer, primary_key=True)
    username = db3.Column(db3.String(80), unique=True, nullable=False)
    city = db3.Column(db3.String(120), nullable=False)
    budget = db3.Column(db3.Float, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


U = User
with app3.app_context():
    db3.create_all()
    db3.session.add_all([U(username="Alice", city="New York", budget=1000.0),
                         U(username="Bob", city="Los Angeles", budget=1500.0),
                         U(username="Charlie", city="Chicago", budget=800.0),
                         U(username="David", city="New York", budget=1200.0),
                         U(username="Eve", city="Los Angeles", budget=900.0)])
    db3.session.commit()
    s = db3.session

    check(F, "with __tablename__='users', raw `SELECT * FROM users` returns plain Row tuples",
          lambda: (lambda r: (type(r[0]).__name__ == "Row" and len(r) == 5, f"{len(r)} rows, first = {r[0]!r} ({type(r[0]).__name__})"))(s.execute(text("SELECT * FROM users")).all()))

    check(F, "type(db.session.query(User)) and type(User.query) are flask_sqlalchemy.query.Query",
          lambda: (type(s.query(U)).__module__ == "flask_sqlalchemy.query" and type(U.query).__module__ == "flask_sqlalchemy.query",
                   f"{type(s.query(U))} / {type(U.query)}"))

    check(F, ".get(): returns record or None (Alice / None / Bob / Charlie)",
          lambda: ([s.get(U, i) for i in (1, 6, 2, 3)] == [s.get(U, 1), None, s.get(U, 2), s.get(U, 3)],
                   str([s.get(U, i) for i in (1, 6, 2, 3)])))

    check(F, "`db.session.query(User).get_or_404(6)` raises 404",
          lambda: ("NotFound" in (raises(lambda: s.query(U).get_or_404(6)) or ""),
                   f"{raises(lambda: s.query(U).get_or_404(6))} (modern: db.get_or_404(User, 6))"))

    def _first_limit():
        with capture_sql(db3) as st:
            s.query(U).first()
        return "LIMIT" in st[-1], "..." + st[-1][-40:]
    check(F, ".first() applies LIMIT 1", _first_limit)

    check(F, ".one() raises if 0 or >1 rows",
          lambda: (True, f"0 rows -> {raises(lambda: s.query(U).filter_by(username='x').one())} | "
                         f">1 rows -> {raises(lambda: s.query(U).one())}"))

    check(F, "`query(User.username).filter_by(id=1).scalar()` -> 'Alice'",
          lambda: (s.query(U.username).filter_by(id=1).scalar() == "Alice", repr(s.query(U.username).filter_by(id=1).scalar())))
    check(F, "legacy Query.scalar() raises MultipleResultsFound for >1 rows",
          lambda: ((raises(lambda: s.query(U.username).scalar()) or "").startswith("MultipleResultsFound"), raises(lambda: s.query(U.username).scalar())))
    check(F, "2.0 Result.scalar() is not strict; .scalar_one() is",
          lambda: (s.execute(select(U.username)).scalar() == "Alice" and (raises(lambda: s.execute(select(U.username)).scalar_one()) or "").startswith("MultipleResultsFound"),
                   f"scalar() -> {s.execute(select(U.username)).scalar()!r}; scalar_one() -> {raises(lambda: s.execute(select(U.username)).scalar_one())[:40]}"))

    check(F, "`.first()` on a column query prints ('Alice',)",
          lambda: (str(s.query(U.username).first()) == "('Alice',)", str(s.query(U.username).first())))

    check(F, ".count() == 5", lambda: (s.query(U).count() == 5, str(s.query(U).count())))
    check(F, "distinct cities -> 3 tuples",
          lambda: (len(s.query(U.city).distinct().all()) == 3, str(s.query(U.city).distinct().all())))

    check(F, "`User.query.with_entities(User.username.label('user_name'))` works",
          lambda: (len(U.query.with_entities(U.username.label("user_name")).all()) == 5, str(U.query.with_entities(U.username.label("user_name")).all()[:2])))

    def _label():
        r = s.query(U.username.label("user_name")).first()
        return r.user_name == "Alice" and list(r._mapping.keys()) == ["user_name"], f"repr {r}; r.user_name={r.user_name!r}, keys={list(r._mapping.keys())}"
    check(F, ".label: not in tuple repr, but row.user_name / row._mapping keys", _label)

    check(F, ".add_columns -> (<User>, 'Alice') tuples",
          lambda: (str(s.query(U).add_columns(U.username).first()) == "(<User Alice>, 'Alice')",
                   str(s.query(U).add_columns(U.username).first())))

    check(F, "filter_by(city='New York') -> [Alice, David]",
          lambda: (str(s.query(U).filter_by(city="New York").all()) == "[<User Alice>, <User David>]",
                   str(s.query(U).filter_by(city="New York").all())))
    check(F, "filter(budget > 1000) -> [Bob, David]",
          lambda: (str(s.query(U).filter(U.budget > 1000).all()) == "[<User Bob>, <User David>]",
                   str(s.query(U).filter(U.budget > 1000).all())))
    from sqlalchemy import and_
    check(F, "filter(a, b) is the same as filter(and_(a, b))",
          lambda: (s.query(U).filter(U.city == "New York", U.budget > 1000).all() == s.query(U).filter(and_(U.city == "New York", U.budget > 1000)).all() == [s.get(U, 4)],
                   str(s.query(U).filter(U.city == "New York", U.budget > 1000).all())))
    check(F, ".between(900, 1200) is a column method",
          lambda: (s.query(U).filter(U.budget.between(900, 1200)).count() == 3, str(s.query(U).filter(U.budget.between(900, 1200)).all())))

    # ---- operator list
    import sqlalchemy as sa
    check(F, "there is no `notexists` function in SQLAlchemy",
          lambda: (not hasattr(sa, "notexists"), f"hasattr(sqlalchemy,'notexists')={hasattr(sa, 'notexists')}"))
    check(F, "`not_in` / `is_not` are the current names (notin_ / isnot are older aliases)",
          lambda: (all(hasattr(U.city, n) for n in ("not_in", "is_not", "notin_", "isnot")),
                   f"not_in={hasattr(U.city, 'not_in')}, is_not={hasattr(U.city, 'is_not')}, notin_={hasattr(U.city, 'notin_')}, isnot={hasattr(U.city, 'isnot')}"))
    check(F, "on SQLite `like` is already case-insensitive for ASCII; ilike uses lower()",
          lambda: (s.query(U).filter(U.username.like("a%")).count() == 1 and "lower(" in str(U.username.ilike("a%")),
                   f"like('a%') -> {s.query(U).filter(U.username.like('a%')).all()}; ilike SQL: {U.username.ilike('a%')}"))

    U2 = aliased(U)
    check(F, "EXISTS example -> [Bob, Eve]",
          lambda: (str(s.query(U).filter(s.query(U2.id).filter(U2.city == U.city, U2.budget > 1400).exists()).all()) == "[<User Bob>, <User Eve>]",
                   str(s.query(U).filter(s.query(U2.id).filter(U2.city == U.city, U2.budget > 1400).exists()).all())))
    check(F, "NOT EXISTS via ~ -> [Alice, Charlie, David]",
          lambda: (str(s.query(U).filter(~s.query(U2.id).filter(U2.city == U.city, U2.budget > 1400).exists()).all()) == "[<User Alice>, <User Charlie>, <User David>]",
                   str(s.query(U).filter(~s.query(U2.id).filter(U2.city == U.city, U2.budget > 1400).exists()).all())))

    check(F, "ANY / ALL are not supported by SQLite",
          lambda: (all((raises(lambda op=op: s.query(U).filter(U.budget > op(s.query(U.budget).filter(U.city == "Chicago").scalar_subquery())).all()) or "").startswith("OperationalError") for op in (any_, all_)),
                   raises(lambda: s.query(U).filter(U.budget > any_(s.query(U.budget).filter(U.city == "Chicago").scalar_subquery())).all())[:70]))
    check(F, "SQLite equivalent: > MIN(Chicago) -> [Alice, Bob, David, Eve]",
          lambda: (str(s.query(U).filter(U.budget > select(func.min(U.budget)).where(U.city == "Chicago").scalar_subquery()).all()) == "[<User Alice>, <User Bob>, <User David>, <User Eve>]",
                   str(s.query(U).filter(U.budget > select(func.min(U.budget)).where(U.city == "Chicago").scalar_subquery()).all())))
    check(F, "SQLite equivalent: > MAX(New York) -> [Bob]",
          lambda: (str(s.query(U).filter(U.budget > select(func.max(U.budget)).where(U.city == "New York").scalar_subquery()).all()) == "[<User Bob>]",
                   str(s.query(U).filter(U.budget > select(func.max(U.budget)).where(U.city == "New York").scalar_subquery()).all())))

    # ---- pagination / aggregates
    check(F, "paginate(page=2, per_page=2).items -> [Charlie, David]",
          lambda: (str(s.query(U).order_by(U.id).paginate(page=2, per_page=2).items) == "[<User Charlie>, <User David>]",
                   str(s.query(U).order_by(U.id).paginate(page=2, per_page=2).items)))
    check(F, "prev_num / next_num are None when there is no previous / next page",
          lambda: (s.query(U).paginate(page=1, per_page=2).prev_num is None and s.query(U).paginate(page=3, per_page=2).next_num is None,
                   f"page1.prev_num={s.query(U).paginate(page=1, per_page=2).prev_num}, page3.next_num={s.query(U).paginate(page=3, per_page=2).next_num}"))
    check(F, "paginate out-of-range page -> 404 (error_out=True); db.paginate(select) works",
          lambda: ((raises(lambda: s.query(U).paginate(page=9, per_page=2)) or "").startswith("NotFound")
                   and str(db3.paginate(db3.select(U).order_by(U.id), page=1, per_page=2).items) == "[<User Alice>, <User Bob>]",
                   f"page 9 -> {raises(lambda: s.query(U).paginate(page=9, per_page=2))[:20]}; db.paginate page1 -> {db3.paginate(db3.select(U).order_by(U.id), page=1, per_page=2).items}"))
    check(F, "count=5, avg=1080.0, sum=5400.0",
          lambda: ((s.query(func.count(U.id)).scalar(), s.query(func.avg(U.budget)).scalar(), s.query(func.sum(U.budget)).scalar()) == (5, 1080.0, 5400.0),
                   str((s.query(func.count(U.id)).scalar(), s.query(func.avg(U.budget)).scalar(), s.query(func.sum(U.budget)).scalar()))))
    check(F, "group_by city sums -> Chicago 800, LA 2400, NY 2200; having > 2000 -> LA, NY",
          lambda: (dict(s.query(U.city, func.sum(U.budget)).group_by(U.city).all()) == {"Chicago": 800.0, "Los Angeles": 2400.0, "New York": 2200.0}
                   and len(s.query(U.city).group_by(U.city).having(func.sum(U.budget) > 2000).all()) == 2,
                   str(s.query(U.city, func.sum(U.budget)).group_by(U.city).all())))

    check(F, "select() is a Python query object (not raw SQL), executed with session",
          lambda: (type(select(U)).__name__ == "Select" and str(s.execute(select(U).where(U.city == "New York")).scalars().all()) == "[<User Alice>, <User David>]",
                   f"{type(select(U)).__name__}; result = {s.execute(select(U).where(U.city == 'New York')).scalars().all()}"))
    check(F, "execute(select(User)) rows are (<User>,) tuples; .scalars() unwraps; session.scalars() shortcut",
          lambda: (str(s.execute(select(U)).first()) == "(<User Alice>,)" and s.scalars(select(U)).all() == s.execute(select(U)).scalars().all(),
                   f"first row {s.execute(select(U)).first()}"))
    check(F, "`.scalars()` is not a Query method; it belongs to Result",
          lambda: (not hasattr(s.query(U), "scalars") and type(s.execute(select(U)).scalars()).__name__ == "ScalarResult",
                   f"Query.scalars? {hasattr(s.query(U), 'scalars')}; Result.scalars() -> {type(s.execute(select(U)).scalars()).__name__}"))


# =========================================================================== #
# 4. relationships part 1 / part 2
# =========================================================================== #
F = "5-flask-sqlalchemy-relationship-part-1.md"
print("=" * 78 + f"\n{F}\n" + "=" * 78)


def rel_app(lazy="select", user_rel_kwargs=None, author_lazy="select", fk_kwargs=None):
    """Fresh User/Article app; returns (app, db, User, Article) with 2 users, 3+1 articles."""
    app, db = new_app()

    class User(db.Model):
        __tablename__ = "users"
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80))
        articles = db.relationship("Article", back_populates="author", lazy=lazy, **(user_rel_kwargs or {}))

    class Article(db.Model):
        __tablename__ = "articles"
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(200))
        user_id = db.Column(db.Integer, db.ForeignKey("users.id", **(fk_kwargs or {})))
        author = db.relationship("User", back_populates="articles", lazy=author_lazy)

    with app.app_context():
        db.create_all()
        u1, u2 = User(username="a"), User(username="b")
        for i in range(3):
            Article(title=f"t{i}", author=u1)
        Article(title="x", author=u2)
        db.session.add_all([u1, u2]); db.session.commit()
    return app, db, User, Article


# ---- one-to-one unique ---------------------------------------------------- #
def _one_to_one():
    app, db = new_app()

    class Person(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        profile = db.relationship("Profile", uselist=False)

    class Profile(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey("person.id"), unique=True)

    with app.app_context():
        db.create_all()
        db.session.add(Person(id=1)); db.session.add(Profile(user_id=1)); db.session.commit()
        db.session.add(Profile(user_id=1))
        err = raises(db.session.commit)
        db.session.rollback()
        p = db.session.get(Person, 1).profile
    return (err or "").startswith("IntegrityError") and type(p).__name__ == "Profile", \
        f"second Profile for the same user -> {err[:60]}; uselist=False gives {type(p).__name__} (not a list)"


check(F, "unique FK => each user has at most one profile; uselist=False returns one object", _one_to_one)


def _overlap():
    app, db = new_app()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        class A(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            bs = db.relationship("B", uselist=True)

        class B(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            a_id = db.Column(db.Integer, db.ForeignKey("a.id"))
            a = db.relationship("A")
        from sqlalchemy.orm import configure_mappers
        configure_mappers()
    msgs = [str(x.message)[:90] for x in w if "conflicts with relationship" in str(x.message)]
    return bool(msgs), (msgs[0] + "...") if msgs else "no warning"


check(F, "two relationships on the same FK without back_populates -> 'conflicts' warning", _overlap)


def _m2m_back_populates():
    app, db = new_app()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        article_authors = db.Table("article_authors",
            db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
            db.Column("article_id", db.Integer, db.ForeignKey("articles.id"), primary_key=True))

        class User(db.Model):
            __tablename__ = "users"
            id = db.Column(db.Integer, primary_key=True)
            articles = db.relationship("Article", secondary=article_authors, back_populates="authors")

        class Article(db.Model):
            __tablename__ = "articles"
            id = db.Column(db.Integer, primary_key=True)
            authors = db.relationship("User", secondary=article_authors, back_populates="articles")
        with app.app_context():
            db.create_all()
            u, a = User(), Article(); u.articles.append(a)
            synced = u in a.authors
            db.session.add(u); db.session.commit()
            a.authors.append(u)          # same pair again -> duplicate PK
            err = raises(db.session.commit)
    conflicts = [x for x in w if "conflicts with relationship" in str(x.message)]
    return synced and not conflicts and (err or "").startswith("IntegrityError"), \
        f"no conflict warning={not conflicts}; synced in memory={synced}; duplicate pair -> {err[:50]}"


check(F, "many-to-many with back_populates: no warning, synced, composite PK blocks duplicate pairs", _m2m_back_populates)


def _backref():
    app, db = new_app()

    class Author(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        books = db.relationship("Book", backref="author", lazy="joined")

    class Book(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        author_id = db.Column(db.Integer, db.ForeignKey("author.id"))
    from sqlalchemy.orm import configure_mappers
    configure_mappers()
    return Book.author.property.lazy == "select" and Author.books.property.lazy == "joined", \
        f"forward lazy={Author.books.property.lazy}, backref side lazy={Book.author.property.lazy}"


check(F, "backref does NOT copy options to the reverse side (gets defaults)", _backref)


def _backref_opts():
    app, db = new_app()

    class Author(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        books = db.relationship("Book", backref=db.backref("author", lazy="joined"))

    class Book(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        author_id = db.Column(db.Integer, db.ForeignKey("author.id"))
    from sqlalchemy.orm import configure_mappers
    configure_mappers()
    return Book.author.property.lazy == "joined", f"db.backref('author', lazy='joined') -> {Book.author.property.lazy}"


check(F, "db.backref('author', lazy=...) configures the reverse side", _backref_opts)

# ---- back_populates in-memory sync ---------------------------------------- #
app_, db_, RU, RA = rel_app()
with app_.app_context():
    u = RU(username="z"); a = RA(title="new"); a.author = u
    check(F, "back_populates syncs both sides in memory (before flush)",
          lambda: (a in u.articles, f"a.author = u  ->  a in u.articles = {a in u.articles}"))

# ---- loading strategies ---------------------------------------------------- #
for strategy in ("select", "joined", "subquery", "selectin", "dynamic", "noload", "raise"):
    app_, db_, RU, RA = rel_app(lazy=strategy)
    with app_.app_context():
        with capture_sql(db_) as at_query:
            u = RU.query.first()
        with capture_sql(db_) as at_access:
            try:
                val = u.articles
                if strategy == "dynamic":
                    n = len(val.all()); desc = f"{type(val).__name__} -> .all() gives {n}"
                else:
                    desc = f"{val!r}"
            except Exception as e:
                desc = f"raised {type(e).__name__}"
        RESULTS_ = (len(at_query), len(at_access), desc, at_query)

        if strategy == "select":
            check(F, "lazy='select': 1 query for user, another when .articles accessed",
                  lambda: ((RESULTS_[0], RESULTS_[1]) == (1, 1), f"queries at .first()={RESULTS_[0]}, at access={RESULTS_[1]}"))
        if strategy == "joined":
            q0 = RESULTS_[3][0]
            check(F, "lazy='joined' + .first(): 1 query, LIMIT inside a subquery, LEFT OUTER JOIN, full collection",
                  lambda: (RESULTS_[0] == 1 and RESULTS_[1] == 0 and "FROM (SELECT" in q0
                           and q0.index("LIMIT") < q0.index(") AS anon_1 LEFT OUTER JOIN") and RESULTS_[2].count("Article") == 3,
                           f"queries={RESULTS_[0]}+{RESULTS_[1]}; ...{q0[q0.index('FROM (SELECT'):][:90]}...; got {RESULTS_[2]}"))
        if strategy == "subquery":
            check(F, "lazy='subquery': 2 queries inside .first(); 2nd re-runs parent query as subquery JOIN",
                  lambda: (RESULTS_[0] == 2 and RESULTS_[1] == 0 and "FROM (SELECT users.id" in RESULTS_[3][1] and "JOIN articles" in RESULTS_[3][1],
                           f"queries at .first()={RESULTS_[0]}, at access={RESULTS_[1]}; 2nd = ...{RESULTS_[3][1][RESULTS_[3][1].index('FROM'):][:80]}..."))
        if strategy == "selectin":
            check(F, "lazy='selectin' is eager: IN query runs right after the parent query, none on access",
                  lambda: (RESULTS_[0] == 2 and RESULTS_[1] == 0 and " IN (" in RESULTS_[3][1],
                           f"queries at .first()={RESULTS_[0]}, at access={RESULTS_[1]}; 2nd = ...{RESULTS_[3][1][-40:]}"))
        if strategy == "dynamic":
            check(F, "lazy='dynamic': access returns AppenderQuery (no query); .all() runs a SELECT",
                  lambda: (RESULTS_[1] == 1 and RESULTS_[2].startswith("AppenderQuery"), f"{RESULTS_[2]}; queries during access+all = {RESULTS_[1]}"))
        if strategy == "noload":
            check(F, "lazy='noload': collection gives [] and no query",
                  lambda: (RESULTS_[2] == "[]" and RESULTS_[1] == 0, f"user.articles = {RESULTS_[2]}, queries = {RESULTS_[1]}"))
        if strategy == "raise":
            check(F, "lazy='raise': accessing raises an error",
                  lambda: ("raised" in RESULTS_[2], RESULTS_[2]))

check(F, "lazy='dynamic' on many-to-one (Article.author) raises InvalidRequestError",
      lambda: ("'dynamic' loaders cannot be used with many-to-one" in (raises(lambda: rel_app(lazy="dynamic", author_lazy="dynamic")) or ""),
               raises(lambda: rel_app(lazy="dynamic", author_lazy="dynamic"))[:110]))

# ---- cascades -------------------------------------------------------------- #
check(F, "cascade 'all' = save-update, merge, refresh-expire, expunge, delete (no delete-orphan)",
      lambda: (set(CascadeOptions("all")) == {"save-update", "merge", "refresh-expire", "expunge", "delete"}, f"all = {sorted(CascadeOptions('all'))}"))


def _default_cascade():
    app, db, RU, RA = rel_app()
    return set(RU.articles.property.cascade) == {"save-update", "merge"}, f"default = {sorted(RU.articles.property.cascade)}; 'none' -> {sorted(CascadeOptions('none'))}"


check(F, "default cascade is 'save-update, merge'; 'none' means no cascade", _default_cascade)


def _fk_cascade(user_rel_kwargs):
    app, db, RU, RA = rel_app(user_rel_kwargs=user_rel_kwargs, fk_kwargs={"ondelete": "CASCADE"})
    with app.app_context():
        with capture_sql(db) as st:
            db.session.delete(db.session.get(RU, 1)); db.session.commit()
        left = db.session.execute(text("select id, user_id from articles order by id")).all()
    return left, [x.split(" ")[0] for x in st]


def _fk_only():
    left, stmts = _fk_cascade(None)
    return "UPDATE" in stmts and [r.user_id for r in left].count(None) == 3, f"ORM ran {stmts}; articles left = {left}"


check(F, "ondelete='CASCADE' alone + session.delete(user): ORM sets user_id=NULL, DB cascade never fires", _fk_only)
check(F, "  ...with passive_deletes=True the DB cascade is used",
      lambda: (lambda r: (len(r[0]) == 1, f"statements {r[1]}; articles left = {r[0]}"))(_fk_cascade({"passive_deletes": True})))
check(F, "  ...with cascade='all, delete-orphan' the ORM deletes them",
      lambda: (lambda r: (len(r[0]) == 1, f"statements {r[1]}; articles left = {r[0]}"))(_fk_cascade({"cascade": "all, delete-orphan"})))


def _sqlite_fk_off():
    import sqlite3
    c = sqlite3.connect(":memory:")
    return c.execute("PRAGMA foreign_keys").fetchone()[0] == 0, f"fresh sqlite3 connection: PRAGMA foreign_keys = {c.execute('PRAGMA foreign_keys').fetchone()[0]}"


check(F, "SQLite does not enforce foreign keys by default", _sqlite_fk_off)

# =========================================================================== #
# 5. 5-flask-sqlalchemy-update-and-delete.md
# =========================================================================== #
F = "5-flask-sqlalchemy-update-and-delete.md"
print("=" * 78 + f"\n{F}\n" + "=" * 78)

app5, db5 = new_app()


class UUser(db5.Model):
    __tablename__ = "user"
    id = db5.Column(db5.Integer, primary_key=True)
    name = db5.Column(db5.String(80), nullable=False)


check(F, "snippets need an application context (outside one -> RuntimeError)",
      lambda: ((raises(lambda: UUser.query.get(1)) or "").startswith("RuntimeError"), raises(lambda: UUser.query.get(1))))

with app5.app_context():
    db5.create_all()
    db5.session.add_all([UUser(name="Old A"), UUser(name="Old B"), UUser(name="Keep")]); db5.session.commit()
    q = UUser.query.filter(UUser.name.like("Old%"))

    def _single_update():
        u = db5.session.get(UUser, 3); u.name = "Changed"
        dirty = u in db5.session.dirty
        db5.session.commit()
        return dirty and db5.session.execute(text("select name from user where id=3")).scalar() == "Changed", f"modified object tracked as dirty={dirty}; saved without add()"
    check(F, "single update: change attribute + commit (no add() needed)", _single_update)
    db5.session.execute(text("update user set name='Keep' where id=3")); db5.session.commit()

    check(F, "synchronize_session='evaluate' raises for like() criteria",
          lambda: ("Could not evaluate current criteria in Python" in (raises(lambda: q.update({UUser.name: "N"}, synchronize_session="evaluate")) or ""),
                   raises(lambda: q.update({UUser.name: "N"}, synchronize_session="evaluate"))[:80]))
    db5.session.rollback()

    def _sync_auto():
        obj = db5.session.get(UUser, 1)
        n = q.update({UUser.name: "New Name"})    # default 'auto'
        fresh = obj.name
        db5.session.rollback()
        return n == 2 and fresh == "New Name", f"default synchronize_session updated {n} rows and the loaded object now says {fresh!r}"
    check(F, "default synchronize_session ('auto') keeps loaded objects in sync, even with like()", _sync_auto)

    def _sync_false():
        obj = db5.session.get(UUser, 1)
        q.update({UUser.name: "New Name"}, synchronize_session=False)
        stale = obj.name
        db5.session.rollback()
        return stale == "Old A", f"after bulk update with False, the in-session object still says {stale!r} (stale)"
    check(F, "synchronize_session=False -> session becomes inconsistent", _sync_false)

    def _raw():
        db5.session.execute(text("UPDATE user SET name = :name WHERE id = :id"), {"name": "New Name", "id": 1})
        db5.session.execute(text("DELETE FROM user WHERE id = :id"), {"id": 3}); db5.session.commit()
        return True, str(db5.session.execute(text("select * from user")).all())
    check(F, "raw text() UPDATE/DELETE with bound params", _raw)

# bulk delete bypasses ORM cascade
app6, db6, RU6, RA6 = rel_app(user_rel_kwargs={"cascade": "all, delete-orphan"})
with app6.app_context():
    db6.session.execute(text("PRAGMA foreign_keys=OFF"))  # only ORM cascade is configured here
    RU6.query.filter(RU6.id == 1).delete(synchronize_session=False); db6.session.commit()
    left6 = db6.session.execute(text("select id, user_id from articles")).all()
    check(F, "bulk query.delete() does NOT apply ORM relationship cascade",
          lambda: (len(left6) == 4, f"cascade='all, delete-orphan' configured, articles left after bulk delete of user 1 = {left6}"))

# =========================================================================== #
# 6. 5-CRUD-API.md
# =========================================================================== #
F = "5-CRUD-API.md"
print("=" * 78 + f"\n{F}\n" + "=" * 78)
def _crud_types():
    import re
    src = open(__file__.rsplit("/", 1)[0] + "/5-CRUD-API.md" if "/" in __file__ else "5-CRUD-API.md").read()
    fks = re.findall(r"(\w+) = db\.Column\(db\.(\w+)(?:\(\d+\))?, db\.ForeignKey\('(\w+)\.(\w+)'\)\)", src)
    pks = dict(re.findall(r"(\w+) = db\.Column\(db\.(\w+), primary_key=True\)", src))
    bad = [(c, t, pks.get(rc)) for c, t, _tbl, rc in fks if pks.get(rc) != t]
    return bool(fks) and not bad, f"FK columns {[(c, t) for c, t, *_ in fks]} vs referenced PK types; mismatches = {bad}"


check(F, "Borrow foreign keys have the same type as the referenced primary keys", _crud_types)

# =========================================================================== #
# 7. Run the code blocks of 5-flask-sqlalchemy-querying.md exactly as written
# =========================================================================== #
F = "5-flask-sqlalchemy-querying.md (code blocks)"
print("=" * 78 + f"\n{F}\n" + "=" * 78)


def run_note_blocks(md_file, skip_if_contains=()):
    import os
    import re
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), md_file)).read()
    src = re.sub(r"(?m)^> ?", "", src)  # code inside GitHub alerts (> [!NOTE]) is quoted
    blocks = re.findall(r"```python\n(.*?)```", src, re.S)
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    ns = {"app": app}
    exec(blocks[0].replace("db = SQLAlchemy()", "db = SQLAlchemy(app)"), ns)  # the notes' model block
    with app.app_context():
        ns["db"].create_all()
        for i, block in enumerate(blocks[1:], start=2):
            label = block.strip().splitlines()[0][:60]
            if ".method()" in block:                 # syntax template, not real code
                print(f"        (skipped block {i}: pseudo-code template) {label}")
                continue
            if any(k in block for k in skip_if_contains):
                # drop only the PostgreSQL-only ANY/ALL part, run everything else
                block = re.sub(r"# =+\n# 4\. ANY.*?(?=# =+\n# SQLite-friendly)", "", block, flags=re.S)
                label += "  [ANY/ALL part removed: PostgreSQL only]"
            if "get_or_404(6)" in block:          # documented to raise 404
                block = block.replace("user2 = db.session.query(User).get_or_404(6)", "pass")
            if "query(User.username).scalar()  # 5 rows" in block:  # documented to raise
                block = block.replace("db.session.query(User.username).scalar()  # 5 rows -> raises MultipleResultsFound", "pass")
            out = __import__("io").StringIO()
            from contextlib import redirect_stdout
            with redirect_stdout(out):
                err = raises(lambda: exec(block, ns))
            check(F, f"block {i} runs: {label}", lambda err=err: (err is None, err or "ran without error"))
            if VERBOSE:
                print("        output:", out.getvalue().strip().replace("\n", " | ")[:300])


run_note_blocks("5-flask-sqlalchemy-querying.md", skip_if_contains=("any_(subq_any)",))  # block 21: only the ANY/ALL part is removed


# =========================================================================== #
# 8. 5-extra-select-vs-query-api.md: run every block and compare key values
# =========================================================================== #
def note_blocks(md_file):
    import os
    import re
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), md_file)).read()
    src = re.sub(r"(?m)^> ?", "", src)  # code inside GitHub alerts (> [!NOTE]) is quoted
    return re.findall(r"```python(?: \[[^\]]+\])?\n(.*?)```", src, re.S)


F = "5-extra-select-vs-query-api.md"
print("=" * 78 + f"\n{F}\n" + "=" * 78)
app8 = Flask(__name__)
app8.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
db8 = SQLAlchemy(app8)
ns8 = {"db": db8, "__name__": "__main__"}
values8 = {}
with app8.app_context(), warnings.catch_warnings():
    warnings.simplefilter("ignore")
    for i, block in enumerate(note_blocks(F)):
        err = raises(lambda: exec(block, ns8))
        label = block.strip().splitlines()[0][:55]
        check(F, f"block {i} runs: {label}", lambda err=err: (err is None, err or "ran without error"))
        for name in ("rows", "names", "count", "avg_budget", "top3", "ny_users", "rich_users", "first_rich"):
            if name in ns8:
                values8.setdefault(name, []).append(repr(ns8[name]))
    left = db8.session.scalars(db8.select(ns8["User"])).all()

expected8 = {
    "ny_users": "[<User Alice>, <User David>]",
    "rich_users": "[<User Bob>, <User David>]",
    "first_rich": "<User Bob>",
    "top3": "[<User Bob>, <User David>, <User Alice>]",
    "names": "['Alice', 'Bob', 'Charlie', 'David', 'Eve']",
    "count": "5",
    "avg_budget": "1080.0",
}
for name, exp in expected8.items():
    got = set(values8.get(name, []))
    check(F, f"both API versions give {name} = {exp}", lambda got=got, exp=exp: (got == {exp}, str(sorted(got))))
check(F, "group_by/having rows (both APIs) = [('Los Angeles', 2400.0), ('New York', 2200.0)]",
      lambda: ("[('Los Angeles', 2400.0), ('New York', 2200.0)]" in values8["rows"], values8["rows"][-1]))
check(F, "bulk update Chicago -> 850 then delete budget < 900 removes Charlie",
      lambda: (str(left) == "[<User Alice>, <User Bob>, <User David>, <User Eve>]", str(left)))


def _query_scalar_vs_one_or_none():
    app, db = new_app()

    class T(db.Model):
        id = db.Column(db.Integer, primary_key=True)
    with app.app_context():
        db.create_all()
        none = db.session.query(T.id).scalar()
        db.session.add_all([T(), T()]); db.session.commit()
        err = raises(lambda: db.session.query(T.id).scalar())
        ok_res = db.session.execute(select(T.id)).scalar()
    return none is None and (err or "").startswith("MultipleResultsFound") and ok_res == 1, \
        f"Query.scalar(): 0 rows -> {none}, 2 rows -> {err[:22]}; Result.scalar() 2 rows -> {ok_res}"


check(F, "legacy Query.scalar() acts like scalar_one_or_none(); Result.scalar() does not raise", _query_scalar_vs_one_or_none)

# =========================================================================== #
# 9. 5-extra-base-sqlalchemy.md: run the blocks as a reader would
# =========================================================================== #
F = "5-extra-base-sqlalchemy.md"
print("=" * 78 + f"\n{F}\n" + "=" * 78)


def _run_base_note():
    import os
    import tempfile
    blocks = note_blocks(F)
    out = {}
    cwd = os.getcwd()
    tmp = tempfile.mkdtemp()
    os.chdir(tmp)                                   # relative sqlite paths land here
    try:
        from contextlib import redirect_stdout
        import io
        # classic-style tab + engine + create_all + CRUD + begin()
        ns = {"__name__": "__main__"}
        buf = io.StringIO()
        with redirect_stdout(buf):
            for idx in (0, 1, 3, 4, 5):
                exec(blocks[idx].replace("echo=True", "echo=False"), ns)
        out["crud_output"] = buf.getvalue().split("\n")[:4]
        out["detached"] = raises(lambda: exec(blocks[6], ns))
        out["plain_file"] = os.path.exists(os.path.join(tmp, "example.db"))
        # typed-style tab
        ns2 = {"__name__": "__main__"}
        exec(blocks[0].replace("echo=True", "echo=False"), ns2)
        exec(blocks[2], ns2)
        exec("Base.metadata.create_all(engine)", ns2)
        out["typed_nullable"] = {c["name"]: c["nullable"] for c in inspect(ns2["engine"]).get_columns("articles")}
        # Flask-SQLAlchemy with model_class=Base
        ns3 = {"__name__": "__main__"}
        buf = io.StringIO()
        with redirect_stdout(buf):
            exec(blocks[7], ns3)
        out["flask_output"] = buf.getvalue().strip()
        out["flask_tablename"] = ns3["Book"].__tablename__
        out["instance_file"] = os.path.exists(os.path.join(tmp, "instance", "example.db"))
        out["db_model_base"] = ns3["db"].Model.metadata is ns3["Base"].metadata
    finally:
        os.chdir(cwd)
    return out


with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    base = _run_base_note()

check(F, "CRUD block prints <User alice> / both articles / <User alice> / [<Article Flask Basics>]",
      lambda: (base["crud_output"] == ["<User alice>", "[<Article Flask Basics>, <Article SQLAlchemy ORM>]", "<User alice>", "[<Article Flask Basics>]"],
               str(base["crud_output"])))
check(F, "lazy load after the with-block closes the session -> DetachedInstanceError",
      lambda: ((base["detached"] or "").startswith("DetachedInstanceError"), (base["detached"] or "no error")[:90]))
check(F, "plain SQLAlchemy: relative sqlite path is relative to the working directory",
      lambda: (base["plain_file"], f"./example.db created = {base['plain_file']}"))
check(F, "Flask-SQLAlchemy: relative sqlite path goes to instance/",
      lambda: (base["instance_file"], f"instance/example.db created = {base['instance_file']}"))
check(F, "typed style: Mapped[str] -> NOT NULL, Mapped[Optional[int]] -> NULL",
      lambda: (base["typed_nullable"] == {"id": False, "title": False, "user_id": True}, str(base["typed_nullable"])))
check(F, "SQLAlchemy(model_class=Base): db.Model uses Base's metadata, tablename generated, prints 'Python 101'",
      lambda: (base["db_model_base"] and base["flask_tablename"] == "book" and base["flask_output"] == "Python 101",
               f"db.Model.metadata is Base.metadata={base['db_model_base']}, tablename={base['flask_tablename']!r}, output={base['flask_output']!r}"))


def _db_reexports():
    import sqlalchemy as sa
    from sqlalchemy import orm
    app, db = new_app()
    same = {n: getattr(db, n) is getattr(sa, n) for n in ("Column", "Integer", "String", "ForeignKey", "select")}
    rel = db.relationship("X")
    same["relationship_wraps_orm"] = type(rel) is type(orm.relationship("X"))
    with app.app_context():
        same["metadata"] = db.metadata is db.Model.metadata
        same["engine"] = type(db.engine).__name__ == "Engine"
        same["session"] = type(db.session).__name__ == "scoped_session"
    return all(same.values()), str(same)


check(F, "db.Column/Integer/String/ForeignKey/select are SQLAlchemy's own; db.relationship wraps it; db.session is scoped", _db_reexports)

# --------------------------------------------------------------------------- #
wrong = [f for ok, f in RESULTS if not ok]
print("=" * 78)
print(f"{len(RESULTS)} checks, {len(RESULTS) - len(wrong)} OK, {len(wrong)} WRONG")
for f in sorted(set(wrong)):
    print(f"  {wrong.count(f):2d} wrong in {f}")
