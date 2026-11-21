# Week 7

This week focuses on **efficient data handling, system-level understanding, web security fundamentals and finding problems in a running application**.

You will explore how **search algorithms optimize data retrieval**, how **memory architecture impacts performance**, how **databases are indexed, distributed and scaled**, how **real-world security vulnerabilities** arise and are prevented, and how **logging and debugging** help you understand what your application is doing.

By the end of this week, you should be able to:

* choose appropriate **search algorithms and data structures** for different scenarios, and compare them with **Big-O notation**
* understand how the **memory hierarchy affects system performance**
* explain how **database indexes** work, and choose between relational and **NoSQL** databases
* explain **scale up vs scale out**, the **CAP theorem** and **ACID vs BASE**
* identify and prevent **common web security issues** (SQL injection, unvalidated input, plain-text passwords, no HTTPS)
* add **logging** to an application and use **debugging** tools (`pdb`, `flask shell`, the Flask debugger)

### Topics Covered

* **[Data Search Algorithms](7-data-search-algo.md)**<br>
  Linear vs binary search, arrays, binary search trees, hash tables, Big-O notation and practical use cases

* **[Memory Architecture](7-memory-architecture.md)**<br>
  Memory hierarchy, cache levels and locality, latency vs throughput, and performance trade-offs

* **[Databases at Scale: Indexes, NoSQL and Scaling](7-SQL-web.md)**<br>
  B-tree and hash indexes, compound indexes, the NoSQL families, scale up vs scale out, replication, the CAP theorem and consistency (ACID vs BASE)

* **[Web Security](7-web-security.md)**<br>
  SQL injection and its defences (parameterised queries, validation, least privilege), password hashing and HTTPS

* **[Logging](7-logging.md)**<br>
  Python's `logging` module: levels, handlers, formatters, rotating files and logging in Flask

* **[Debugging](debugging.md)**<br>
  Reading a traceback, `breakpoint()` and `pdb`, `flask shell`, and the Flask debug mode
