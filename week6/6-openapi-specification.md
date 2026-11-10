# API Data Transfer Formats

Web services use different data formats to exchange information between a client (e.g., browser) and a server over a network. Which format we choose affects performance, readability, and compatibility between systems.

## 🌐 HTML (HyperText Markup Language)

- Used mainly for **displaying web pages**  
- Not suitable for data-exchange in APIs because:  
    - Contains presentation like `<em><strong>` with data, making it difficult to extract structured information programmatically. 
- Rarely used in modern APIs  

## 🟦 JSON (JavaScript Object Notation)

- Most widely used API format  
- Lightweight, easy to read for humans.  
- Language-independent, with support in most programming languages (in Python the `json` module, in Flask `request.get_json()` & `jsonify()`)
- Supports:  
    - Objects → `{ }`  
    - Arrays → `[ ]`  
    - Key-value pairs  `{"k": v}`
    - Strings, numbers, `true`/`false` and `null`
    - easy to parse and generate for machines

**Key Points**
- Keys must be **strings in double quotes** (`"name"`, not `'name'` or `name`)  
- No comments and no trailing commas
- Common in REST APIs  
- Fast parsing  

## 🟧 XML (Extensible Markup Language)

- Structured and hierarchical format  
- Uses tags like HTML  
- More verbose and follows stricter syntax rules than JSON.

**Key Points**
- Self-descriptive, as tags clearly indicate the meaning of data. 
- Supports schemas (XSD)  
- Heavier than JSON  
- Everything is text: a parser gives `"1"`, not the number 1, unless a schema says otherwise

## 🟩 YAML (YAML Ain't Markup Language)

- Can be more human-readable than JSON due to minimal syntax. 
- Uses **indentation instead of brackets** (tabs are not allowed for indentation)  
- Common in config files (Docker, Kubernetes)  
- Valid JSON is also (in practice) valid YAML, so a YAML parser can read JSON

**Key Points**
- Cleaner than JSON
- Sensitive to indentation
- Less commonly used for API data transfer, but widely used for `config` & API specifications  [swagger](https://editor.swagger.io/)

## The same record in all three formats

**JSON**

```json
{
  "id": 1,
  "name": "Priya Shah",
  "email": "priya@example.com",
  "courses": ["MAD1", "MAD2"]
}
```

**YAML**

```yaml
id: 1
name: Priya Shah
email: priya@example.com
courses:
  - MAD1
  - MAD2
```

**XML**

```xml
<student id="1">
  <name>Priya Shah</name>
  <email>priya@example.com</email>
  <courses>
    <course>MAD1</course>
    <course>MAD2</course>
  </courses>
</student>
```

## JSON, YAML, XML formats

| Feature            | JSON            | YAML                             | XML                |
| ------------------ | --------------- | -------------------------------- | ------------------ |
| **Readability**    | Medium          | High                             | Low                |
| **Syntax**         | `{}` and `[]`   | Indentation                      | Tags `< >`         |
| **Size** (record above) | Compact    | Most compact                     | Largest (every name is written twice) |
| **Parsing Speed** (Python's libraries) | Fastest | Slowest          | In between         |
| **Comments**       | Not supported   | Supported `#`                    | Supported `<!-- -->` |
| **Data types**     | string, number, boolean, null, array, object | same as JSON | text only (types come from a schema) |
| **Usage**          | APIs, web apps  | Config files, API specifications | Enterprise systems, feeds |
| **Learning Curve** | Easy            | Easy (but indentation-sensitive) | Moderate           |

## OpenAPI (Swagger)
- A **standardized specification** for describing RESTful APIs in a machine-readable format.
- Written in **JSON or YAML**
- Acts as a **contract between client and server** by clearly defining available endpoints, inputs, and outputs.
- Can be used to automatically generate interactive documentation (Swagger UI) and client/server code.
- "Swagger" is the old name of the specification; today it is called the **OpenAPI Specification** (versions 3.0.x and 3.1.x) and "Swagger" names the tools around it (Swagger UI, Swagger Editor).

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
openapi: 3.0.3
info:
  title: Users API
  version: 1.0.0
paths:
  /users:
    get:
      summary: Get all users
      responses:
        '200':
          description: Success
```

`openapi`, `info` (with `title` and `version`) and `paths` are required, and every operation needs at least one entry in `responses`. Response codes are written as quoted strings (`'200'`): an unquoted `200:` is read by YAML as a number and the document is invalid.

#### b. HTTP Methods & Parameters
- Path parameters → `/users/{id}`
- Query parameters → `?limit=10`
- Headers → `Authorization`

Every parameter is declared with its location (`in`) and a schema; path parameters must be `required: true`:

```yaml
paths:
  /users/{id}:
    get:
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
        - name: limit
          in: query
          schema:
            type: integer
```

#### c. Request & Response Format
- Defines the structure and data types of request and response bodies.

```yaml
responses:
  '200':
    description: Success
    content:
      application/json:
        schema:
          type: object
```

A request body is described in the same way with `requestBody`:

```yaml
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/User'
```

#### d. Error Handling
- Use **one consistent error format** for the whole API, for example:
```json
{
  "error": "Not Found",
  "message": "User not found",
  "status_code": 404
}
```
- This shape is our own convention, OpenAPI does not prescribe one (Flask Restful's default is `{"message": "..."}`; the standard for error bodies is `application/problem+json`, RFC 9457). Whatever we choose, the error responses should be described in `responses` too (`'404'`, ...).


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
  1. API Key (`type: apiKey`)
  2. HTTP authentication, e.g. a `Bearer Token` (`type: http`, `scheme: bearer`) or Basic
  3. OAuth 2 (`type: oauth2`)

#### A complete example

The pieces above together form one valid document (written for OpenAPI 3.0.3):

```yaml
openapi: 3.0.3
info:
  title: Users API
  version: 1.0.0
paths:
  /users:
    get:
      summary: Get all users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
    post:
      summary: Add a user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      responses:
        '201':
          description: User added
  /users/{id}:
    get:
      summary: Get one user
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
  schemas:
    User:
      type: object
      properties:
        name:
          type: string
        email:
          type: string
```

Paste it into [editor.swagger.io](https://editor.swagger.io/) and Swagger UI shows it as interactive documentation: every endpoint is listed, with its parameters and responses, and can be tried out from the browser.

### 2. Tooling & Interoperability
- Supports:
  <!-- - Auto code generation (client/server) -->
  - API testing (Swagger UI, Postman)
  - Validation of requests/responses against the specification (tools such as connexion or flask-smorest use the OpenAPI document; `flask_pydantic` validates requests with pydantic models, not with the OpenAPI file)
- Works across multiple languages

## Why OpenAPI is Important?
- Standardizes API design
- Improves collaboration in open-source contribution or within a team of developers
- Reduces bugs
- Enables automation

<details>
<summary>API Best Practices</summary>

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

</details>


## Testing with Thunder Client or Postman

The examples below use a small API with the routes `/user` and `/user/<id>` that answers with the JSON shown.

### GET Request

- URL: `http://127.0.0.1:5000/user/1`
- Response:

```json
{
  "id": 1,
  "name": "Priya Shah",
  "email": "priya@example.com"
}
```

### POST Request

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

### PUT Request

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

### DELETE Request

- URL: `http://127.0.0.1:5000/user/3`
- Response:

```json
{
  "message": "User deleted"
}
```


## Testing the API with curl

> [!NOTE]
> A command written over several lines needs a **line continuation** at the end of every line but the last: `\` in bash/zsh (Linux, macOS, Git Bash, WSL). Without it the shell runs each line as a separate command and `curl` only receives the first one. The `Content-Type: application/json` header is required for Flask's `request.get_json()`: without it `curl -d` sends `application/x-www-form-urlencoded` and Flask answers `415 Unsupported Media Type`. In Windows Command Prompt the continuation is `^` and the JSON needs double quotes with escaped inner quotes (`-d "{\"name\": \"Rahul\"}"`); in PowerShell `curl` is an alias of `Invoke-WebRequest`, so type `curl.exe`.

### GET

```bash
curl http://127.0.0.1:5000/user/1
```

### POST (Non-Idempotent)

```bash
curl -X POST http://127.0.0.1:5000/user \
  -H "Content-Type: application/json" \
  -d '{"name": "Rahul Srivastava","email": "rahul@example.com"}'
```
- Running it multiple times **creates new users** (e.g., Rahul with different IDs).
- (`-X POST` is optional here: `-d` already makes curl send a POST.)

### PUT

```bash
curl -X PUT http://127.0.0.1:5000/user/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Shiv Varma", "email": "shiv@example.com"}'
```
- Running it multiple times **does not create duplicate users**, only updates user

### DELETE

```bash
curl -X DELETE http://127.0.0.1:5000/user/3
```
- Running it multiple times ensures user 3 remains **deleted**. (no effect on the state after the first request)

## Idempotency

> [!WARNING]
> **`POST` is not idempotent (and `PATCH` is not guaranteed to be): `GET`, `PUT`, `DELETE`, `HEAD` and `OPTIONS` are**
>
> An HTTP method is idempotent if making the same request multiple times has the same effect on the server as making it once, regardless of how many times it is executed. (The response may differ: a second `DELETE` can answer "not found".)
> - Idempotency is important for reliability in distributed systems, especially when requests may be retried due to network failures.

- `GET` is **idempotent** → No change in Database, repeated requests produce the same result. (It is also *safe*: it never changes anything.)
- `PUT` is **idempotent** → No matter how many times you update user `1` with same data, final user state is same.
  - After first -> updated
  - After second -> no further change

- `DELETE` is **idempotent** → User 3 remains deleted regardless of retries. 
  - First → deletes
  - Second → nothing changes

- ❌ `POST` is **not idempotent** → creates a **new resource, resulting in multiple entries.**
  - First -> creates row
  - Second -> creates another user row (duplicate)


> [!NOTE]
> **[Tools helpful for API development & testing, even in TDS course](https://tds.s-anand.net/2025-01/rest-apis/):**
>
> - `Postman/Thunder Client`: API testing and documentation
> - `Swagger/OpenAPI`: API documentation
> - `HTTPie`: Modern command-line HTTP client
> - `JSON` Schema: API request/response validation
>
> - [Google API design guide](https://cloud.google.com/apis/design)
> - [REST API Best practices](https://stackoverflow.blog/2020/03/02/best-practices-for-rest-api-design/)
