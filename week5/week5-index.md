# Week 5

<SessionResources :week="5" />
This week focuses on the **Business Logic Layer** of a web application and introduces how <span style="font-weight:bold; color:rgb(98, 151, 208)">controllers manage interactions between the view and the model</span>

You can revise [Model–View–Controller (MVC) design pattern](../week4/4-database-layer-MODEL.md#MVC(Model-View-Controller))  

We will understand understand how **web requests and responses work** through `curl` & learn how **CRUD operations form the core functionality of most APIs**. You will heavily use **CRUD-logic** in your MAD1 project controllers.

This week also introduces **Flask-SQLAlchemy**, which simplifies database interactions in Flask applications using **ORM (Object Relational Mapping)**.

By the end of this week, you should be able to:

- Understand the **role of controllers in a web application**
- Handle **HTTP requests and responses**
- Implement **CRUD-based APIs** in `app.py`
- Configure and use **Flask-SQLAlchemy for database models & relationships** in `models.py`

### Topics Covered

- **[Business Logic Layer – Controllers](5-curl-server.md)**<br>
  Controller responsibilities, and `curl` commands for HTTP request-response

- **[CRUD Operations & API Design](5-CRUD-API.md)**<br>
  Understanding Create, Read, Update, Delete operations and how they form the foundation of web APIs

- **[Flask SQLAlchemy Basics](5-flask-sqlalchemy-basics.md)**<br>
  Configuring the database, Flask-SQLAlchemy features, creating models, and CRUD operations using ORM

- **[Tables and Models](5-table-creation.md)**<br>
  Defining tables/models, data types, column constraints and composite constraints

- **[Querying the Database](5-flask-sqlalchemy-querying.md)**<br>
  Query methods, projection, filtering, operators, ordering, pagination, aggregation and raw SQL

- **[Update and Delete](5-flask-sqlalchemy-update-and-delete.md)**<br>
  Updating/deleting single records, bulk update/delete and `synchronize_session`

- **[Flask SQLAlchemy Relationships – Part 1](5-flask-sqlalchemy-relationship-part-1.md)**<br>
  One-to-one, one-to-many, many-to-many, `back_populates` vs `backref`, loading strategies and cascades

- **[Flask SQLAlchemy Relationships – Part 2](5-flask-sqlalchemy-relationships-part-2.md)**<br>
  Quick reference: where the foreign key goes, association tables, one-to-one

- **[Extra: Select vs Query API](5-extra-select-vs-query-api.md)**<br>
  The modern SQLAlchemy 2.0 `select()` style compared with the legacy `Query` API
