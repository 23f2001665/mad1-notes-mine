# API Data Transfer Formats

Web services use different data formats to exchange information between a client (e.g., browser) and a server over a network. Which format use choose affects performance, readability, and compatibility between systems.
<div class="card">
<h3> HTML (HyperText Markup Language)</h3>

- Used mainly for **displaying web pages**  
- Not suitable for data-exchange in APIs because:  
    - Contains presentation like `<em><strong>`with data, making it difficult to extract structured information programmatically. 
- Rarely used in modern APIs  
</div>

<!-- JSON -->
<div class="card">
<h3>🟦 JSON (JavaScript Object Notation)</h3>

- Most widely used API format  
- Lightweight, easy to read for humans.  
- Language-independent, with built-in support in most programming languages like `request.get_json()` & `jsonify()`
- Supports:  
    - Objects → `{ }`  
    - Arrays → `[ ]`  
    - Key-value pairs  `{"k":v}`
    - easy to parse and generate for machines

**Example**
<img src="https://www.devopsschool.com/blog/wp-content/uploads/2022/02/student-json-object.jpg" style="width:100%; border-radius:8px;">

**Key Points**
- Keys must be **strings (in `" "`quotes)**  
- Common in REST APIs  
- Fast parsing  
</div>

<!-- XML -->
<div class="card">
<h3>🟧 XML (Extensible Markup Language)</h3>

- Structured and hierarchical format  
- Uses tags like HTML  
- More verbose and follows stricter syntax rules than JSON.

**Example**
<img src="https://passyworldofict.com/wp-content/uploads/2019/04/XMLRead01.jpg" style="width:100%; border-radius:8px;">

**Key Points**
- Self-descriptive, as tags clearly indicate the meaning of data. 
- Supports schemas (XSD)  
- Heavier than JSON  
</div>

<!-- YAML -->
<div class="card">
<h3>🟩 YAML (Yet Another Markup Language)</h3>

- Can be more human-readable than JSON due to minimal syntax. 
- Uses **indentation instead of brackets**  
- Common in config files (Docker, Kubernetes)  

**Example**
<img src="https://static1.smartbear.co/swagger/media/images/links.png" style="width:100%; border-radius:8px;">

**Key Points**
- Cleaner than JSON<br>
- Sensitive to indentation<br>
- Less commonly used for API data transfer, but widely used for `config` & API specifications  [swagger](https://editor.swagger.io/)
</div>

## JSON, YAML, XML formats

| Feature            | JSON            | YAML                             | XML                |
| ------------------ | --------------- | -------------------------------- | ------------------ |
| **Readability**    | Medium          | High                             | Low                |
| **Syntax**         | `{}` and `[]`   | Indentation                      | Tags `< >`         |
| **Size**           | Compact         | Moderate                         | Large              |
| **Parsing Speed**  | Fast            | Slower                           | Slow               |
| **Comments**       | Not supported |  Supported `#`                   |  Supported        |
| **Usage**          | APIs, web apps  | Config files                     | Enterprise systems |
| **Learning Curve** | Easy            | Easy (but indentation-sensitive) | Moderate           |


## OpenAPI (Swagger)
- A **standardized specification** for describing RESTful APIs in a machine-readable format.
- Written in **JSON or YAML**
- Acts as a **contract between client and server** by clearly defining available endpoints, inputs, and outputs.
- Can be used to automatically generate interactive documentation (Swagger UI) and client/server code.
#### Key Features
### 1. API Description Language
- API documentation specifies the following for each endpoint:
  - HTTP methods
  - URL paths → `/users`, `/books`
  - Query parameters → `?page=1`
  - Request body format
  - Response structure
- This helps developers understand API structure. Smoother collaboration between frontend and backend teams

#### a. API Version & Paths
```yaml
openapi: 3.0.0
paths:
  /users:
    get:
      summary: Get all users
```


#### b. HTTP Methods & Parameters
- Path parameters → `/users/{id}`
- Query parameters → `?limit=10`
- Headers → `Authorization`


#### c. Request & Response Format
- Defines the structure and data types of request and response bodies.

```yaml
responses:
  200:
    description: Success
    content:
      application/json:
        schema:
          type: object
```


#### d. Error Handling
- Standard error format:
```json
{
  "error": "Not Found",
  "message": "User not found",
  "status_code": 404
}
```


#### e. Data Models
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

#### f. Authentication & Security
- Common methods include:
  1. API Key
  2. OAuth
  3. `Bearer Token`

<SwaggerUI />

### 2. Tooling & Interoperability
- Supports:
  <!-- - Auto code generation (client/server) -->
  - API testing (Swagger UI, Postman)
  - Validation of requests/responses using tools such as `flask_pydantic`.
- Works across multiple languages

## Why OpenAPI is Important?
- Standardizes API design
- Improves collaboration in open-source contribution or within a team of developers
- Reduces bugs
- Enables automation

:::details API Best Practices

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
:::


## Testing with Thunder Client or Postman

:::tabs
==GET Request
   - URL: `http://127.0.0.1:5000/user/1`
   - Response:  
     ```json
     {
       "id": 1,
       "name": "Priya Shah",
       "email": "priya@example.com"
     }
     ```
   
==POST Request
   - URL: `http://127.0.0.1:5000/user`
   - Headers: `{ "Content-Type": "application/json" }`
   - Body:
     ```json
     {
       "name": "Rahul Srivastava",
       "email": "rahul@example.com"
     }
     ```
   - Response:
     ```json
     {
       "message": "User added",
       "data": {
         "name": "Rahul Srivastava",
         "email": "rahul@example.com"
       }
     }
     ```
   
==PUT Request
   - URL: `http://127.0.0.1:5000/user/1`
   - Headers: `{ "Content-Type": "application/json" }`
   - Body:
     ```json
     {
       "name": "Shiv Varma",
       "email": "shiv@example.com"
     }
     ```
   - Response:
     ```json
     {
       "message": "User updated",
       "data": {
         "name": "Shiv Varma",
         "email": "shiv@example.com"
       }
     }
     ```
   
==DELETE Request
   - URL: `http://127.0.0.1:5000/user/3`
   - Response:
     ```json
     {
       "message": "User deleted"
     }
     ```
:::


## Testing the API with curl

:::tabs
==GET
```bash
curl http://127.0.0.1:5000/user/1
```

== POST (Non-Idempotent)
```bash
curl -X POST http://127.0.0.1:5000/user 
-H "Content-Type: application/json" 
-d '{"name": "Rahul Srivastava","email": "rahul@example.com"}'
```
- Running it multiple times **creates new users** (e.g., Rahul with different IDs).
==PUT
```bash
curl -X PUT http://127.0.0.1:5000/user/1 
-H "Content-Type: application/json" 
-d '{"name": "Shiv Varma", "email": "shiv@example.com"}'
```
- Running it multiple times **does not create duplicate users**, only updates user

== DELETE
```bash
curl -X DELETE http://127.0.0.1:5000/user/3
```
- Running it multiple times ensures user 1 remains **deleted**. (no effect after the first request)

:::

## Idempotency
::: warning all are idempotent except `POST`
An HTTP method is idempotent if making the same request multiple times results in the same final state of the server, regardless of how many times it is executed.
- Idempotency is important for reliability in distributed systems, especially when requests may be retried due to network failures.
:::

- `GET` is **idempotent** → No change in Database, repeated requests produce the same result.
- `PUT` is **idempotent** → No matter how many times you update user `1` with same data, final user state is same.
  - After first -> updated
  - After second -> no further change

- `DELETE` is **idempotent** → User 1 remains deleted regardless of retries. 
  - First → deletes
  - Second → nothing changes

- ❌ `POST` is **not idempotent** → creates a **new resource, resulting in multiple entries.**
  - First -> creates row
  - Second -> creates another user row (duplicate)


::: info [Tools helpful for API development & testing, even in TDS course](https://tds.s-anand.net/2025-01/rest-apis/):

- `Postman/Thunder Client`: API testing and documentation
- `Swagger/OpenAPI`: API documentation
- `HTTPie`: Modern command-line HTTP client
- `JSON` Schema: API request/response validation

- [Google API design guide](https://cloud.google.com/apis/design)
- [REST API Best practices](https://stackoverflow.blog/2020/03/02/best-practices-for-rest-api-design/)

:::

