
# Distributed Software Architecture

Distributed software architecture is a system design approach in which application components run on multiple machines and communicate over a network.

- Components run on **different systems**
- Communication happens via **network protocols (HTTP, TCP, etc.)**
- Enables **scalability** (handling increased load by adding machines) and **fault tolerance** (system continues working even if some components fail).


### Web Architecture

The structure used to design, build, and deliver web applications over the internet. using technologies like **HTML, CSS, JavaScript, HTTP**.

- Clients and servers may be **geographically far apart**
- Network conditions vary (latency, speed), can be **unreliable**


### Client–Server Responsibilities
#### Client

- User interface
- Sends requests
- Displays response

#### Server

- Stores data
- Processes business logic and handles requests
- Returns results


```mermaid
graph LR
    Client1[Client - Browser]
    Client2[Client - Mobile]
    Network[(Network)]
    Server[Server]

    Client1 --> Network
    Client2 --> Network
    Network --> Server
    Server --> Network
    Network --> Client1
    Network --> Client2
```

---

# Assumptions in Distributed Systems

1. Server is **not always on**
2. The server **does not maintain client state** between requests (**stateless** interaction).
3. Authentication is **not automatic** (must be handled explicitly by tokens/sessions)
4. Network latency is **unpredictable**



# REST Architecture 

An API (Application Programming Interface) is a set of rules and protocols that allows different software systems to communicate and exchange data

- REST = **REpresentational State Transfer**
- A **set of design constraints**, not strict rules
- Designed to work efficiently over HTTP and handle real-world web constraints such as **latency, scalability, and stateless** communication.


## REST Constraints


### 1 Client–Server
Separation of concerns

- Client → UI & interaction
- Server → data & logic
- Independent development
- network can be `local`, not alter just connects client to server.


### 2: Stateless

Each request is independent
- Server does NOT keep any per-client state (a "session") between requests. (The data of the resources themselves, e.g. the rows of a database, is of course stored.)
- Client must send **all required data every time**, we can't assume it is the same server answering us.
- Server does not know:
  - which page user was on
  - if user is logged in (unless token is sent)


```mermaid
sequenceDiagram
    participant Client
    participant Server

    Client->>Server: Request (with all info)
    Server->>Client: Response

    Client->>Server: New Request (no memory)
    Server->>Client: Response
```


### 3: Layered System

The system is organized into multiple layers, where each layer has a specific responsibility and only talks to the layer next to it. The client cannot tell whether it is connected directly to the final server or to an intermediary on the way.

#### Typical Components

- Load Balancer
- Authentication Server
- Backend Servers
- (Inside the backend, the code itself is often divided into model, view and controller, see [MVC](../week4/4-1-database-layer-MODEL.md); that is a separate, internal way of layering.)
##### Benefits
Can make changes in one layer without affecting other, making it secure and easier to maintain or debug errors.
- reuse components
- modular design

```mermaid
graph LR
    Client --> Network
    Network --> LB[Load Balancer]
    LB --> Auth[Auth Server]
    LB --> Backend[Backend Pool]
```

---

### 4: Cacheability

Responses can be stored (cached): the server labels every response as cacheable or not, and caches (browser, proxy, CDN) may reuse a cacheable response instead of asking the server again. In practice mostly `GET` responses are cached.

#### Benefits

- Faster responses
- Reduced server load

- Example: Browser caches images, CSS


```mermaid
graph LR
    Client --> Proxy[Cache / Proxy]
    Proxy -->|Cached Response| Client
    Proxy -->|Miss| Server
    Server --> Proxy
```

- `Cache-Control`
- `Expires`
- `ETag` / `Last-Modified` (let a client ask "has it changed?")

---

### 5: Uniform Interface


Standard way of communication between client-server. It has four parts: resources are identified by URIs, they are manipulated through representations (JSON, XML, ...), every message describes itself (method, status code, `Content-Type`), and responses can contain links to other resources (HATEOAS).

### Rules

- In REST APIs, **URLs represent resources** (e.g., /books, /students) rather than actions. Use standard HTTP methods:

| Method | Purpose |
| ------ | ------- |
| GET    | Read    |
| POST   | Create (the server chooses the new id) |
| PUT    | Replace / update a whole resource (can also create it at a URL chosen by the client) |
| PATCH  | Update part of a resource |
| DELETE | Remove  |

#### Benefits

- Simplicity
- Consistency
- Easy to understand APIs

---

#### 6. Code on Demand

The only **optional** constraint: the server can send executable code to extend the client. Example:
- JavaScript
- Applets (obsolete today)

## Summary Table

| Constraint        | Purpose                     |
| ----------------- | --------------------------- |
| Client-Server     | Separation of concerns      |
| Stateless         | No memory on server         |
| Layered           | Modular system              |
| Cacheable         | Improve performance         |
| Uniform Interface | Standard communication      |
| Code on Demand    | Extend client functionality (optional) |

---

# REST (REpresentational State Transfer)

- Client - Server may be far apart & State?
- Different networks, latencies, quality
- Authentication? Not core part of protocol
- guidelines & constraints

### What is REST?

- REST is an **architectural style** for designing web services.
- Uses **HTTP methods** to operate on **resources**.
- Resources are identified using **URIs (Uniform Resource Identifiers)**.
- Communication happens in a **client–server model**.


#### What does it actually mean?

- Every request from client → server must include **all required information (state)**.
- Server does **not remember previous requests**.
- This is called **stateless communication**.

> [!NOTE]
> - Everything is a **resource** (user, product, order, etc.)
> - Each resource has:
>
>   - A **URI**
>   - A **representation** (JSON, XML, etc.)
>
> ```
> GET /users/101
> ```
>
> → Fetch user with ID 101

### REST Communication Flow (Sequence)

1. **Client accesses resource**

   - Uses URI (e.g., `/users/101`)
   - No prior state assumed

2. **Client specifies operation**

   - Using HTTP methods:

     - GET, POST, PUT, DELETE

3. **Server processes request**

   - Applies business logic
   - Interacts with database if needed

4. **Server sends response**

   - Returns:

     - Data (JSON/XML)
     - Status codes (200, 404, etc.)
     - Links to other resources (HATEOAS, part of the uniform interface but often left out in practice)

| Aspect             | CRUD                         | REST                         |
| ------------------ | ---------------------------- | ---------------------------- |
| **Definition**     | Basic database operations    | Architectural style for APIs |
| **Scope**          | Database level               | Web/API level                |
| **Operations**     | Create, Read, Update, Delete | Uses HTTP methods            |
| **Protocol**       | Not tied to any protocol     | Uses HTTP                    |
| **Focus**          | Data manipulation            | Resource-based communication |
| **Implementation** | SQL / ORM / DB logic         | APIs using URIs + HTTP       |
| **State**          | Internal DB state            | Stateless communication      |

- REST ≠ CRUD
- But:

  - REST **maps well to CRUD operations**

##  Idempotent Operations
- An operation is **idempotent** if:

  - Repeating it multiple times → same effect on the server as doing it once (the *response* may differ: a second `DELETE` can answer "not found", the state is still the same)

### Idempotent

- GET
- PUT
- DELETE
- HEAD
- OPTIONS

### Non-Idempotent

- POST
- PATCH (not guaranteed to be idempotent)

| Method | Safe (does not change anything) | Idempotent |
| ------ | ------------------------------- | ---------- |
| GET, HEAD, OPTIONS | Yes | Yes |
| PUT, DELETE | No | Yes |
| POST | No | No |
| PATCH | No | No (not guaranteed) |



## Typical REST API Functionality

- CRUD operations
- Filtering & listing
- Create VM
- Restart server
- Control IoT devices

(Actions like these are modelled as resources too, e.g. `POST /servers/5/restarts` creates a "restart".)



### **Flask Application with Idempotency Handling**
```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Initialize database
with app.app_context():
    db.create_all()

def name_from_request():
    data = request.get_json(silent=True) or {}   # None (not an error) if the body is missing or not JSON
    return data.get("name")

# ✅ IDEMPOTENT: PUT (Update or Create)
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    name = name_from_request()
    if not name:
        return jsonify({"message": "name is required"}), 400
    user = db.session.get(User, user_id)

    if user:  # If user exists, update it
        user.name = name
    else:  # If user doesn't exist, create it (still idempotent)
        user = User(id=user_id, name=name)
        db.session.add(user)

    db.session.commit()
    return jsonify({"id": user.id, "name": user.name}), 200

# ✅ IDEMPOTENT: DELETE (Always results in resource absence)
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = db.session.get(User, user_id)

    if user:  # Delete if exists
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted"}), 200
    else:  # Already deleted: the state is the same (many APIs answer 404 here, still idempotent)
        return jsonify({"message": "User not found"}), 200

# ❌ NON-IDEMPOTENT: POST (Creates new entry every time)
@app.route("/users", methods=["POST"])
def create_user():
    name = name_from_request()
    if not name:
        return jsonify({"message": "name is required"}), 400
    new_user = User(name=name)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"id": new_user.id, "name": new_user.name}), 201

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
```

Sending the same request twice to an empty database (`curl` or Thunder Client, JSON body, `Content-Type: application/json`):

| Request | 1st response | 2nd response (same request again) |
| ------- | ------------ | --------------------------------- |
| `PUT /users/7` with `{"name": "Alice"}` | `200 {"id": 7, "name": "Alice"}` | `200 {"id": 7, "name": "Alice"}` (same, one row) |
| `POST /users` with `{"name": "Bob"}` | `201 {"id": 8, "name": "Bob"}` | `201 {"id": 9, "name": "Bob"}` (a new row) |
| `DELETE /users/7` | `200 {"message": "User deleted"}` | `200 {"message": "User not found"}` (state unchanged) |

---
