::: tip A small recap for those who  want to revise SQL queries (Details of these concepts are covered in DBMS course)
:::

## Database Example: **Library Management System**

A college library built a database to keep track of:
##### `Students`

| student_id | name  | dept |
| ---------- | ----- | ---- |
| S101       | Aditi | CS   |
| S102       | Rohan | EE   |
| S103       | Meera | CS   |


##### `Books`
| book_id | title            | category | edition | publisher       |
| ------- | ---------------- | -------- | ------- | --------------- |
| B1      | Database Systems | CS       | 3rd     | Pearson         |
| B2      | Calculus         | Math     | 2nd     | McGraw Hill     |
| B3      | Physics Basics   | Physics  | 1st     | Cambridge Press |


##### `BorrowedBooks` (Many-to-Many)

| student_id | book_id | borrow_date |
| ---------- | ------- | ----------- |
| S101       | B1      | 2024-01-10  |
| S101       | B2      | 2024-01-15  |
| S102       | B3      | 2024-01-12  |
| S103       | B1      | 2024-01-18  |


This design shows a **many-to-many relationship**:

* A student can borrow multiple books.
* A book can be borrowed by multiple students (over course of time but one at a time).

## ER diagrams
<img style="margin: auto;" src="../static/ER-diagram.jpg">

::: tip crow feet ER diagram (this is different from the ER symbols you learn in DBMS course⚠️<br> don't confuse the two conventions)
- Vertical line `|` → One (Exactly one instance of the entity)<br>Ex. *A borrow record must be linked to exactly one student*
- Circle `O` → Optional (Zero or more participate)<br>Ex. *A student may or may not have borrowed books.*
- Crow's feet - Many<br> Ex. *A student can borrow many books.*
- Second Vertical Line `||` → Mandatory (At least one)<br> Ex. Every borrow record must have at least one book
:::

## Case 1: Create Table (Datatypes + Constraints)
```sql
CREATE TABLE Students (
  student_id CHAR(4) PRIMARY KEY,
  name VARCHAR(20) NOT NULL,
  dept VARCHAR(5)
);
```

👉🏻 `CREATE TABLE` defines a new relation with specified columns, datatypes, and integrity constraints.

## Case 2: Insert Data

```sql
INSERT INTO Students
VALUES ('S104', 'Kunal', 'ME');
```

👉🏻 Adds a new student (tuple/row) to the table

## Case 3: Simple SELECT + WHERE

### ❓ Find all CS students

:::code-group
```sql [SQL]
SELECT name
FROM Students
WHERE dept = 'CS';
-- WHERE category IN ('CS', 'Math'); for >1 departments
```

```txt [output]
Aditi
Meera
```
:::

👉🏻 `SELECT` retrieves data from a table, and WHERE filters rows before they are returned.


## Case 4: JOIN (Who borrowed which book?)

::: code-group
```sql [SQL]
SELECT s.name, b.title
FROM Students s
JOIN BorrowedBooks bb
  ON s.student_id = bb.student_id
JOIN Books b
  ON b.book_id = bb.book_id;
```


```txt [output]
Aditi   Database Systems
Aditi   Calculus
Rohan   Physics Basics
Meera   Database Systems
```
:::

👉🏻 `JOIN` combines rows from multiple tables using a related attribute, avoiding a Cartesian product.

## Case 5: Condition with JOIN

### ❓ Find students who borrowed **Database Systems**

::: code-group
```sql [SQL]
SELECT s.name
FROM Students s
JOIN BorrowedBooks bb
  ON s.student_id = bb.student_id
JOIN Books b
  ON b.book_id = bb.book_id
WHERE b.title = 'Database Systems';
```

```txt [output]
Aditi
Meera
```
:::

👉🏻 `WHERE` can also be used with joined tables to filter results based on a condition.

## Case 6: Aggregation (COUNT + GROUP BY + HAVING)

### ❓ How many books has each student borrowed?

```sql
SELECT student_id, COUNT(*) AS books_borrowed
FROM BorrowedBooks
GROUP BY student_id;
ORDER BY name ASC;
```
👉🏻 `GROUP BY` groups rows with the same value, aggregate functions COUNT compute a result per group.
👉🏻 Orders final output alphabetically by value of "name" column

### ❓ Students who borrowed **more than 1 book**

::: code-group
```sql [SQL]
SELECT student_id, COUNT(*) AS books_borrowed
FROM BorrowedBooks
GROUP BY student_id
HAVING COUNT(*) > 1;
```


```txt [output]
S101   2
```
:::

👉🏻 `HAVING` filters groups after aggregation, while WHERE filters rows before grouping.

### DELETE

```sql
DELETE FROM BorrowedBooks
WHERE student_id = 'S102';
```
👉🏻 `DELETE` removes selected rows from a table while keeping the table structure intact.