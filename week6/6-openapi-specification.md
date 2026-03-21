# **API Data Transfer Formats**

Web services use different formats to transfer data between client and server.
<div class="card">
<h3>🌐 HTML (HyperText Markup Language)</h3>

- Used mainly for **displaying web pages**  
- Not suitable for APIs because:  
    - Contains presentation + data mixed  
    - Hard to parse programmatically  
- Rarely used in modern APIs  

**Example**
<img src="https://www.devopsschool.com/blog/wp-content/uploads/2022/02/student-json-object.jpg" style="width:100%; border-radius:8px;">
</div>

<!-- JSON -->
<div class="card">
<h3>🟦 JSON (JavaScript Object Notation)</h3>

- Most widely used API format  
- Lightweight and easy to read/write  
- Language-independent  
- Supports:  
    - Objects → `{ }`  
    - Arrays → `[ ]`  
    - Key-value pairs  

**Example**
<img src="https://www.devopsschool.com/blog/wp-content/uploads/2022/02/student-json-object.jpg" style="width:100%; border-radius:8px;">

**Key Points**
- Keys must be **strings (in quotes)**  
- Common in REST APIs  
- Fast parsing  
</div>

<!-- XML -->
<div class="card">
<h3>🟧 XML (Extensible Markup Language)</h3>

- Structured and hierarchical format  
- Uses tags like HTML  
- More verbose than JSON  

**Example**
<img src="https://passyworldofict.com/wp-content/uploads/2019/04/XMLRead01.jpg" style="width:100%; border-radius:8px;">

**Key Points**
- Self-descriptive  
- Supports schemas (XSD)  
- Heavier than JSON  
</div>

<!-- YAML -->
<div class="card">
<h3>🟩 YAML (Yet Another Markup Language)</h3>

- Human-readable format  
- Uses **indentation instead of brackets**  
- Common in config files (Docker, Kubernetes)  

**Example**
<img src="https://static1.smartbear.co/swagger/media/images/links.png" style="width:100%; border-radius:8px;">

**Key Points**
- Cleaner than JSON<br>
- Sensitive to indentation<br>
- Less used in APIs, more in configs  
</div>


| Feature            | JSON            | YAML                             | XML                |
| ------------------ | --------------- | -------------------------------- | ------------------ |
| **Readability**    | Medium          | High                             | Low                |
| **Syntax**         | `{}` and `[]`   | Indentation                      | Tags `< >`         |
| **Size**           | Compact         | Moderate                         | Large              |
| **Parsing Speed**  | Fast            | Slower                           | Slow               |
| **Comments**       | ❌ Not supported | ✅ Supported                      | ✅ Supported        |
| **Usage**          | APIs, web apps  | Config files                     | Enterprise systems |
| **Learning Curve** | Easy            | Easy (but indentation-sensitive) | Moderate           |


## **OpenAPI (Swagger)**
- A **standard specification** for describing REST APIs
- Written in **JSON or YAML**
- Acts as a **contract between client and server**

#### **Key Features**
##### 1. API Description Language
- Defines:
  - Endpoints
  - Request/response format
  - Parameters
- Helps developers understand API structure


### 2. Endpoint Documentation
- Specifies:
  - HTTP methods → GET, POST, PUT, DELETE
  - URL paths → `/users`, `/books`
  - Query parameters → `?page=1`
  - Request body format
  - Response structure


### 3. Tooling & Interoperability
- Supports:
  - Auto code generation (client/server)
  - API testing (Swagger UI, Postman)
  - Validation of requests/responses
- Works across multiple languages


### 4. OpenAPI Specification Components

#### a. API Version & Paths
- Example:
```yaml
openapi: 3.0.0
paths:
  /users:
    get:
      summary: Get all users
```


#### b. HTTP Methods & Parameters
- Defines:
  - Path parameters → `/users/{id}`
  - Query parameters → `?limit=10`
  - Headers → `Authorization`


#### c. Request & Response Schemas
- Defines structure of data

```yaml
responses:
  200:
    description: Success
    content:
      application/json:
        schema:
          type: object
```


#### d. Authentication & Security
- Types:
  1. API Key
  2. OAuth
  3. Bearer Token


#### e. Error Handling
- Standard error format:
```json
{
  "error": "Not Found",
  "message": "User not found",
  "status_code": 404
}
```

#### f. API Documentation
- Interactive docs (Swagger UI)
- Helps frontend + backend teams

#### g. Data Models
- Defines reusable objects

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        name:
          type: string
```


## **Why OpenAPI is Important?**
- Standardizes API design
- Improves collaboration
- Reduces bugs
- Enables automation

---

:::details Additional Points

### API Best Practices
- Use **nouns** → `/users`, not `/getUsers`
- Version APIs → `/api/v1/users`
- Use query params → filtering, pagination


### HTTP Methods Summary
- **GET** → Read (safe, idempotent)
- **POST** → Create (not idempotent)
- **PUT** → Update (idempotent)
- **DELETE** → Remove (idempotent)
:::
### API Testing Tools
- Postman / Thunder Client
- curl (command line)
- Swagger UI 


### **🔹 Testing with Thunder Client or Postman**

:::tabs
==GET Request
   - URL: `http://127.0.0.1:5000/user/1`
   - Response:  
     ```json
     {
       "id": 1,
       "name": "John Doe",
       "email": "john@example.com"
     }
     ```
   
==POST Request
   - URL: `http://127.0.0.1:5000/user/1`
   - Headers: `{ "Content-Type": "application/json" }`
   - Body:
     ```json
     {
       "name": "John Doe",
       "email": "john@example.com"
     }
     ```
   - Response:
     ```json
     {
       "message": "User added",
       "data": {
         "name": "John Doe",
         "email": "john@example.com"
       }
     }
     ```
   
==PUT Request
   - URL: `http://127.0.0.1:5000/user/1`
   - Headers: `{ "Content-Type": "application/json" }`
   - Body:
     ```json
     {
       "name": "Jane Doe",
       "email": "jane@example.com"
     }
     ```
   - Response:
     ```json
     {
       "message": "User updated",
       "data": {
         "name": "Jane Doe",
         "email": "jane@example.com"
       }
     }
     ```
   
==DELETE Request
   - URL: `http://127.0.0.1:5000/user/1`
   - Response:
     ```json
     {
       "message": "User deleted"
     }
     ```
:::


#### Best Practices:

1. Use Nouns for Resources
Good: `/users, /posts`
Bad: `/getUsers, /createPost`
2. Version Your API
`/api/v1/users`
`/api/v2/users`
3. Handle Errors Consistently
`{"error": "Not Found", "message": "User 123 not found", "status_code": 404}`
4. Use Query Parameters for Filtering
`/api/posts?status=published&category=tech`
5. Implement Pagination
`/api/posts?page=2&limit=10`


### **Testing the API**

:::tabs
==PUT
```bash
curl -X PUT http://127.0.0.1:5000/users/1 -H "Content-Type: application/json" -d '{"name": "Alice"}'
```
- Running it multiple times **does not create duplicate users**, only updates user

== DELETE
```bash
curl -X DELETE http://127.0.0.1:5000/users/1
```
- Running it multiple times ensures user 1 is **deleted or already absent**.

== POST (Non-Idempotent)
```bash
curl -X POST http://127.0.0.1:5000/users -H "Content-Type: application/json" -d '{"name": "Bob"}'
```
- Running it multiple times **creates new users** (e.g., Bob with different IDs).
:::


### **Key Takeaways**
- `PUT` is **idempotent** → No matter how many times you update user 1, the result remains the same.  
- `DELETE` is **idempotent** → User 1 remains deleted regardless of retries.  
- ❌ `POST` is **not idempotent** → Creates a **new user every time**.

::: info [Tools helpful for TDS course as well](https://tds.s-anand.net/2025-01/rest-apis/):

- `Postman/Thunder Client`: API testing and documentation
- `Swagger/OpenAPI`: API documentation
- `HTTPie`: Modern command-line HTTP client
- `JSON` Schema: API request/response validation

- [Google API design guide](https://cloud.google.com/apis/design)
- [REST API Best practices](https://stackoverflow.blog/2020/03/02/best-practices-for-rest-api-design/)

:::


##### Example CURL Requests
Create Student
```sh
curl -X POST http://127.0.0.1:5000/students/S104 \
-H "Content-Type: application/json" \
-d '{"name":"Kunal","dept":"ME"}'
```
Get Student
```sh
curl http://127.0.0.1:5000/students/S104
```
Borrow Book
```sh
curl -X POST http://127.0.0.1:5000/borrow \
-H "Content-Type: application/json" \
-d '{"student_id":"S101","book_id":"B1","borrow_date":"2024-02-01"}'
```