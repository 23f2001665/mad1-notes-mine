# Week 6

<SessionResources :week="6" />
This week introduces Web APIs and REST architecture, focusing on how applications communicate over the web using **standardized** interfaces.

You will learn how RESTful APIs expose resources, how HTTP methods `GET, POST, PUT, DELETE` map to these actions, and how data is transferred using formats like `JSON`. The week also introduces `Flask-RESTful` for building structured APIs and OpenAPI `swagger` for documenting them.

You will also explore tools used in industry to test, debug, and document APIs, such as `Swagger UI, Postman and CURL`.

By the end of this week, you should be able to:
- Understand the concept and architecture of REST APIs
- Design **resource-based APIs**
- Implement APIs using `Flask-RESTful`
- Parse request arguments and format `json` responses
- try to document APIs using `OpenAPI/Swagger`
- Test APIs using `curl, Postman`

### Topics Covered

- **[REST APIs and Data Exchange](6-REST-APIs.md)**
  REST constraints, CRUD mapping with HTTP verbs, idempotent operations, JSON data transfer and API design example.

- **[Flask RESTful Basics](6-flask-restful-basics.md)**
  Creating REST APIs using `Flask-RESTful`, resource routing, endpoint mapping, request parsing using `reqparse`, and response formatting with `marshal_with`

- **[OpenAPI Specification & Testing](6-openapi-specification.md)**
  Introduction to OpenAPI, YAML/JSON API description/schema using `Swagger UI` and testing APIs using `CURL, Postman`