# Todo Manager REST API Documentation

A RESTful API for managing **todos**, **projects**, and **categories** with full relationship support between entities. Built on the [Thingifier](https://github.com/eviltester/thingifier) engine (v1.5).

**Base URL:** `http://localhost:4567`

---

## Table of Contents

- [Overview](#overview)
- [Content Negotiation](#content-negotiation)
- [Data Models](#data-models)
- [API Endpoints](#api-endpoints)
  - [Todos](#todos)
  - [Projects](#projects)
  - [Categories](#categories)
  - [Relationships: Todo ↔ Project (task-of / tasks)](#relationships-todo--project-task-of--tasks)
  - [Relationships: Todo ↔ Category](#relationships-todo--category)
  - [Relationships: Project ↔ Category](#relationships-project--category)
  - [Relationships: Category ↔ Todo](#relationships-category--todo)
  - [Relationships: Category ↔ Project](#relationships-category--project)
  - [Utility Endpoints](#utility-endpoints)
- [Error Handling](#error-handling)
- [Known Bugs & Quirks](#known-bugs--quirks)

---

## Overview

The Todo Manager API provides CRUD operations on three entity types (**todos**, **projects**, **categories**) plus the ability to create and manage relationships between them:

| Relationship | Direction | Description |
|---|---|---|
| `task-of` / `tasks` | todo ↔ project | A todo is a task of a project |
| `categories` | todo ↔ category | A todo belongs to categories |
| `todos` | category → todo | A category contains todos |
| `projects` | category → project | A category contains projects |
| `categories` | project → category | A project belongs to categories |

All data lives **in memory only** and is not persisted — the application resets every time you start it. It ships with some default test data.

---

## Content Negotiation

### Request Format

Set the `Content-Type` header to control the input format:

| Content-Type | Format |
|---|---|
| `application/json` (default) | JSON |
| `application/xml` | XML |

### Response Format

Set the `Accept` header to control the output format:

| Accept | Format |
|---|---|
| `application/json` (default) | JSON |
| `application/xml` | XML |
| `*/*` | JSON (default fallback) |

---

## Data Models

### Todo

| Field | Type | Mandatory | Validation | Default |
|---|---|---|---|---|
| `id` | ID (auto) | No (auto-generated) | — | Auto-increment |
| `title` | STRING | **Yes** | Cannot be empty | — |
| `doneStatus` | BOOLEAN | No | Must be boolean | `false` |
| `description` | STRING | No | — | `""` |

**JSON Example:**

```json
{
  "doneStatus": "false",
  "description": "A sample todo",
  "id": "1",
  "title": "Buy groceries"
}
```

**XML Example:**

```xml
<todo>
  <doneStatus>false</doneStatus>
  <description>A sample todo</description>
  <id>1</id>
  <title>Buy groceries</title>
</todo>
```

### Project

| Field | Type | Mandatory | Validation | Default |
|---|---|---|---|---|
| `id` | ID (auto) | No (auto-generated) | — | Auto-increment |
| `title` | STRING | No | — | `""` |
| `description` | STRING | No | — | `""` |
| `active` | BOOLEAN | No | Must be boolean | `false` |
| `completed` | BOOLEAN | No | Must be boolean | `false` |

**JSON Example:**

```json
{
  "description": "Sprint 1 deliverables",
  "active": "true",
  "id": "1",
  "completed": "false",
  "title": "Backend API"
}
```

**XML Example:**

```xml
<project>
  <description>Sprint 1 deliverables</description>
  <active>true</active>
  <id>1</id>
  <completed>false</completed>
  <title>Backend API</title>
</project>
```

### Category

| Field | Type | Mandatory | Validation | Default |
|---|---|---|---|---|
| `id` | ID (auto) | No (auto-generated) | — | Auto-increment |
| `title` | STRING | **Yes** | Cannot be empty | — |
| `description` | STRING | No | — | `""` |

**JSON Example:**

```json
{
  "description": "High priority items",
  "id": "1",
  "title": "Urgent"
}
```

**XML Example:**

```xml
<category>
  <description>High priority items</description>
  <id>1</id>
  <title>Urgent</title>
</category>
```

---

## API Endpoints

### Todos

---

#### 1. `GET /todos`

Return all todo instances. Supports query parameter filtering.

- **Status:** `200 OK`
- **Allowed Methods** (via OPTIONS): `OPTIONS, GET, POST`

**Example Request:**

```bash
curl http://localhost:4567/todos -H "Accept: application/json"
```

**Example Response:**

```json
{
  "todos": [
    {
      "doneStatus": "false",
      "description": "",
      "id": "1",
      "title": "scan paperwork"
    },
    {
      "doneStatus": "false",
      "description": "",
      "id": "2",
      "title": "file paperwork"
    }
  ]
}
```

**Query Parameter Filtering:**

```bash
curl "http://localhost:4567/todos?title=scan%20paperwork" -H "Accept: application/json"
```

---

#### 2. `POST /todos`

Create a new todo. The `title` field is mandatory and cannot be empty.

- **Status:** `201 Created`
- **Error:** `400 Bad Request` (missing/empty title, invalid fields)

**Example Request:**

```bash
curl -X POST http://localhost:4567/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "doneStatus": false, "description": "Weekly shopping"}'
```

**Example Response:**

```json
{
  "doneStatus": "false",
  "description": "Weekly shopping",
  "id": "3",
  "title": "Buy groceries"
}
```

**XML Example:**

```bash
curl -X POST http://localhost:4567/todos \
  -H "Content-Type: application/xml" \
  -H "Accept: application/xml" \
  -d '<todo><title>XML Todo</title></todo>'
```

---

#### 3. `OPTIONS /todos`

Return the allowed HTTP methods for the `/todos` collection endpoint.

- **Status:** `200 OK`
- **Headers:** `Allow: OPTIONS, GET, POST`

**Example Request:**

```bash
curl -X OPTIONS http://localhost:4567/todos
```

---

#### 4. `HEAD /todos`

Attempt a HEAD request on the collection endpoint.

- **Status:** `405 Method Not Allowed`

> **Note:** HEAD is not supported on collection endpoints in this API.

---

#### 5. `GET /todos/:id`

Return a specific todo by its ID.

- **Status:** `200 OK`
- **Error:** `404 Not Found` (invalid ID)

**Example Request:**

```bash
curl http://localhost:4567/todos/1 -H "Accept: application/json"
```

**Example Response:**

```json
{
  "todos": [
    {
      "doneStatus": "false",
      "description": "",
      "id": "1",
      "title": "scan paperwork"
    }
  ]
}
```

**Error Response (404):**

```json
{
  "errorMessages": ["Could not find an instance with todos/999999"]
}
```

---

#### 6. `POST /todos/:id`

Amend (partial update) a specific todo. Only the fields provided in the body are updated; unspecified fields retain their current values.

- **Status:** `200 OK`
- **Error:** `404 Not Found` (invalid ID)

**Example Request:**

```bash
curl -X POST http://localhost:4567/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

**Example Response:**

```json
{
  "doneStatus": "false",
  "description": "",
  "id": "1",
  "title": "Updated Title"
}
```

---

#### 7. `PUT /todos/:id`

Replace/amend a specific todo. Behaves similarly to POST for amendment.

- **Status:** `200 OK`
- **Error:** `404 Not Found` (invalid ID)

**Example Request:**

```bash
curl -X PUT http://localhost:4567/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Replaced Title", "doneStatus": true, "description": "Fully replaced"}'
```

**Example Response:**

```json
{
  "doneStatus": "true",
  "description": "Fully replaced",
  "id": "1",
  "title": "Replaced Title"
}
```

---

#### 8. `DELETE /todos/:id`

Delete a specific todo by its ID.

- **Status:** `200 OK`
- **Error:** `404 Not Found` (invalid or already-deleted ID)

**Example Request:**

```bash
curl -X DELETE http://localhost:4567/todos/1
```

---

#### 9. `OPTIONS /todos/:id`

Return the allowed HTTP methods for a specific todo resource.

- **Status:** `200 OK`
- **Headers:** `Allow: OPTIONS, GET, POST, PUT, DELETE`

**Example Request:**

```bash
curl -X OPTIONS http://localhost:4567/todos/1
```

---

#### 10. `HEAD /todos/:id`

Attempt a HEAD request on a specific todo.

- **Status:** `405 Method Not Allowed`

> **Note:** HEAD is not supported on individual resource endpoints.

---

### Projects

---

#### 11. `GET /projects`

Return all project instances.

- **Status:** `200 OK`

**Example Request:**

```bash
curl http://localhost:4567/projects -H "Accept: application/json"
```

**Example Response:**

```json
{
  "projects": [
    {
      "description": "",
      "active": "false",
      "id": "1",
      "completed": "false",
      "title": "Office Work"
    }
  ]
}
```

---

#### 12. `POST /projects`

Create a new project. The `title` field is **not** mandatory for projects.

- **Status:** `201 Created`
- **Error:** `400 Bad Request` (invalid boolean fields)

**Example Request:**

```bash
curl -X POST http://localhost:4567/projects \
  -H "Content-Type: application/json" \
  -d '{"title": "New Project", "active": true, "completed": false, "description": "Project desc"}'
```

**Example Response:**

```json
{
  "description": "Project desc",
  "active": "true",
  "id": "2",
  "completed": "false",
  "title": "New Project"
}
```

---

#### 13. `OPTIONS /projects`

Return the allowed HTTP methods for the `/projects` collection.

- **Status:** `200 OK`
- **Headers:** `Allow: OPTIONS, GET, POST`

---

#### 14. `HEAD /projects`

Attempt a HEAD request on the projects collection.

- **Status:** `405 Method Not Allowed`

---

#### 15. `GET /projects/:id`

Return a specific project by its ID.

- **Status:** `200 OK`
- **Error:** `404 Not Found`

**Example Request:**

```bash
curl http://localhost:4567/projects/1 -H "Accept: application/json"
```

**Example Response:**

```json
{
  "projects": [
    {
      "description": "",
      "active": "false",
      "id": "1",
      "completed": "false",
      "title": "Office Work"
    }
  ]
}
```

---

#### 16. `POST /projects/:id`

Amend (partial update) a specific project.

- **Status:** `200 OK`
- **Error:** `404 Not Found`

**Example Request:**

```bash
curl -X POST http://localhost:4567/projects/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Project Name"}'
```

---

#### 17. `PUT /projects/:id`

Replace/amend a specific project.

- **Status:** `200 OK`
- **Error:** `404 Not Found`

**Example Request:**

```bash
curl -X PUT http://localhost:4567/projects/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Replaced Project", "active": false, "completed": true, "description": "Done"}'
```

---

#### 18. `DELETE /projects/:id`

Delete a specific project by its ID.

- **Status:** `200 OK`
- **Error:** `404 Not Found`

**Example Request:**

```bash
curl -X DELETE http://localhost:4567/projects/1
```

---

#### 19. `OPTIONS /projects/:id`

Return the allowed HTTP methods for a specific project resource.

- **Status:** `200 OK`
- **Headers:** `Allow: OPTIONS, GET, POST, PUT, DELETE`

---

#### 20. `HEAD /projects/:id`

Attempt a HEAD request on a specific project.

- **Status:** `405 Method Not Allowed`

---

### Categories

---

#### 21. `GET /categories`

Return all category instances.

- **Status:** `200 OK`

**Example Request:**

```bash
curl http://localhost:4567/categories -H "Accept: application/json"
```

**Example Response:**

```json
{
  "categories": [
    {
      "description": "",
      "id": "1",
      "title": "Office"
    },
    {
      "description": "",
      "id": "2",
      "title": "Home"
    }
  ]
}
```

---

#### 22. `POST /categories`

Create a new category. The `title` field is mandatory and cannot be empty.

- **Status:** `201 Created`
- **Error:** `400 Bad Request` (missing/empty title)

**Example Request:**

```bash
curl -X POST http://localhost:4567/categories \
  -H "Content-Type: application/json" \
  -d '{"title": "Urgent", "description": "High priority items"}'
```

**Example Response:**

```json
{
  "description": "High priority items",
  "id": "3",
  "title": "Urgent"
}
```

---

#### 23. `OPTIONS /categories`

Return the allowed HTTP methods for the `/categories` collection.

- **Status:** `200 OK`
- **Headers:** `Allow: OPTIONS, GET, POST`

---

#### 24. `HEAD /categories`

Attempt a HEAD request on the categories collection.

- **Status:** `405 Method Not Allowed`

---

#### 25. `GET /categories/:id`

Return a specific category by its ID.

- **Status:** `200 OK`
- **Error:** `404 Not Found`

**Example Request:**

```bash
curl http://localhost:4567/categories/1 -H "Accept: application/json"
```

**Example Response:**

```json
{
  "categories": [
    {
      "description": "",
      "id": "1",
      "title": "Office"
    }
  ]
}
```

---

#### 26. `POST /categories/:id`

Amend (partial update) a specific category.

- **Status:** `200 OK`
- **Error:** `404 Not Found`

**Example Request:**

```bash
curl -X POST http://localhost:4567/categories/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Category"}'
```

---

#### 27. `PUT /categories/:id`

Replace/amend a specific category.

- **Status:** `200 OK`
- **Error:** `404 Not Found`

**Example Request:**

```bash
curl -X PUT http://localhost:4567/categories/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Replaced Category", "description": "New desc"}'
```

---

#### 28. `DELETE /categories/:id`

Delete a specific category by its ID.

- **Status:** `200 OK`
- **Error:** `404 Not Found`

**Example Request:**

```bash
curl -X DELETE http://localhost:4567/categories/1
```

---

#### 29. `OPTIONS /categories/:id`

Return the allowed HTTP methods for a specific category resource.

- **Status:** `200 OK`
- **Headers:** `Allow: OPTIONS, GET, POST, PUT, DELETE`

---

#### 30. `HEAD /categories/:id`

Attempt a HEAD request on a specific category.

- **Status:** `405 Method Not Allowed`

---

### Relationships: Todo ↔ Project (task-of / tasks)

---

#### 31. `GET /todos/:id/task-of`

Return all projects related to a given todo via the `task-of` relationship.

- **Status:** `200 OK`

**Example Request:**

```bash
curl http://localhost:4567/todos/1/task-of -H "Accept: application/json"
```

**Example Response:**

```json
{
  "projects": [
    {
      "description": "",
      "active": "false",
      "id": "1",
      "completed": "false",
      "title": "Office Work"
    }
  ]
}
```

---

#### 32. `POST /todos/:id/task-of`

Create a `task-of` relationship between a todo and a project. The project ID is provided in the request body.

- **Status:** `201 Created`
- **Error:** `404 Not Found` (nonexistent project ID)

**Example Request:**

```bash
curl -X POST http://localhost:4567/todos/1/task-of \
  -H "Content-Type: application/json" \
  -d '{"id": "1"}'
```

---

#### 33. `DELETE /todos/:id/task-of/:id`

Remove the `task-of` relationship between a todo and a project.

- **Status:** `200 OK`
- **Error:** `404 Not Found` (relationship does not exist)

**Example Request:**

```bash
curl -X DELETE http://localhost:4567/todos/1/task-of/1
```

---

#### 34. `GET /projects/:id/tasks`

Return all todos related to a given project via the `tasks` relationship (inverse of `task-of`).

- **Status:** `200 OK`

**Example Request:**

```bash
curl http://localhost:4567/projects/1/tasks -H "Accept: application/json"
```

**Example Response:**

```json
{
  "todos": [
    {
      "doneStatus": "false",
      "description": "",
      "id": "1",
      "title": "scan paperwork"
    }
  ]
}
```

---

#### 35. `POST /projects/:id/tasks`

Create a `tasks` relationship between a project and a todo. The todo ID is provided in the request body.

- **Status:** `201 Created`
- **Error:** `404 Not Found` (nonexistent todo ID)

**Example Request:**

```bash
curl -X POST http://localhost:4567/projects/1/tasks \
  -H "Content-Type: application/json" \
  -d '{"id": "2"}'
```

---

#### 36. `DELETE /projects/:id/tasks/:id`

Remove the `tasks` relationship between a project and a todo.

- **Status:** `200 OK`
- **Error:** `404 Not Found`

**Example Request:**

```bash
curl -X DELETE http://localhost:4567/projects/1/tasks/2
```

---

### Relationships: Todo ↔ Category

---

#### 37. `GET /todos/:id/categories`

Return all categories related to a given todo.

- **Status:** `200 OK`

**Example Request:**

```bash
curl http://localhost:4567/todos/1/categories -H "Accept: application/json"
```

**Example Response:**

```json
{
  "categories": [
    {
      "description": "",
      "id": "1",
      "title": "Office"
    }
  ]
}
```

---

#### 38. `POST /todos/:id/categories`

Create a relationship between a todo and a category.

- **Status:** `201 Created`
- **Error:** `404 Not Found` (nonexistent category ID)

**Example Request:**

```bash
curl -X POST http://localhost:4567/todos/1/categories \
  -H "Content-Type: application/json" \
  -d '{"id": "1"}'
```

---

#### 39. `DELETE /todos/:id/categories/:id`

Remove the relationship between a todo and a category.

- **Status:** `200 OK`
- **Error:** `404 Not Found`

**Example Request:**

```bash
curl -X DELETE http://localhost:4567/todos/1/categories/1
```

---

### Relationships: Project ↔ Category

---

#### 40. `GET /projects/:id/categories`

Return all categories related to a given project.

- **Status:** `200 OK`

**Example Request:**

```bash
curl http://localhost:4567/projects/1/categories -H "Accept: application/json"
```

**Example Response:**

```json
{
  "categories": []
}
```

---

#### 41. `POST /projects/:id/categories`

Create a relationship between a project and a category.

- **Status:** `201 Created`
- **Error:** `404 Not Found` (nonexistent category ID)

**Example Request:**

```bash
curl -X POST http://localhost:4567/projects/1/categories \
  -H "Content-Type: application/json" \
  -d '{"id": "1"}'
```

---

#### 42. `DELETE /projects/:id/categories/:id`

Remove the relationship between a project and a category.

- **Status:** `200 OK`
- **Error:** `404 Not Found`

**Example Request:**

```bash
curl -X DELETE http://localhost:4567/projects/1/categories/1
```

---

### Relationships: Category ↔ Todo

---

#### 43. `GET /categories/:id/todos`

Return all todos related to a given category.

- **Status:** `200 OK`

**Example Request:**

```bash
curl http://localhost:4567/categories/1/todos -H "Accept: application/json"
```

**Example Response:**

```json
{
  "todos": [
    {
      "doneStatus": "false",
      "description": "",
      "id": "1",
      "title": "scan paperwork"
    }
  ]
}
```

---

#### 44. `POST /categories/:id/todos`

Create a relationship between a category and a todo.

- **Status:** `201 Created`
- **Error:** `404 Not Found` (nonexistent todo ID)

**Example Request:**

```bash
curl -X POST http://localhost:4567/categories/1/todos \
  -H "Content-Type: application/json" \
  -d '{"id": "1"}'
```

---

#### 45. `DELETE /categories/:id/todos/:id`

Remove the relationship between a category and a todo.

- **Status:** `200 OK`
- **Error:** `404 Not Found`

**Example Request:**

```bash
curl -X DELETE http://localhost:4567/categories/1/todos/1
```

---

### Relationships: Category ↔ Project

---

#### 46. `GET /categories/:id/projects`

Return all projects related to a given category.

- **Status:** `200 OK`

**Example Request:**

```bash
curl http://localhost:4567/categories/1/projects -H "Accept: application/json"
```

**Example Response:**

```json
{
  "projects": []
}
```

---

#### 47. `POST /categories/:id/projects`

Create a relationship between a category and a project.

- **Status:** `201 Created`
- **Error:** `404 Not Found` (nonexistent project ID)

**Example Request:**

```bash
curl -X POST http://localhost:4567/categories/1/projects \
  -H "Content-Type: application/json" \
  -d '{"id": "1"}'
```

---

#### 48. `DELETE /categories/:id/projects/:id`

Remove the relationship between a category and a project.

- **Status:** `200 OK`
- **Error:** `404 Not Found`

**Example Request:**

```bash
curl -X DELETE http://localhost:4567/categories/1/projects/1
```

---

### Utility Endpoints

---

#### 49. `GET /docs`

Render the API documentation as an HTML page.

- **Status:** `200 OK`
- **Content-Type:** `text/html`

**Example:**

```bash
curl http://localhost:4567/docs
```

---

#### 50. `GET /shutdown`

Shut down the API server.

- **WARNING:** This will terminate the running server process.

**Example:**

```bash
curl -X GET http://localhost:4567/shutdown
```

---

#### 51. `GET /gui`

Open the default GUI / Entities Explorer in a web browser.

- **Status:** `200 OK`
- **Content-Type:** `text/html`

**Example:**

```bash
curl http://localhost:4567/gui
```

---

## Error Handling

### Error Response Format

All errors return a JSON object with an `errorMessages` array:

```json
{
  "errorMessages": ["Could not find an instance with todos/999999"]
}
```

### HTTP Status Codes

| Code | Meaning | When |
|---|---|---|
| `200` | OK | Successful GET, POST (amend), PUT, DELETE |
| `201` | Created | Successful POST (create new entity or relationship) |
| `400` | Bad Request | Validation error, malformed JSON/XML, missing required fields |
| `404` | Not Found | Entity or relationship not found |
| `405` | Method Not Allowed | Unsupported HTTP method (e.g., PATCH, HEAD) |

### Common Error Scenarios

**Missing required field (title for todos/categories):**

```bash
curl -X POST http://localhost:4567/todos \
  -H "Content-Type: application/json" \
  -d '{"description": "No title"}'
```

```json
{
  "errorMessages": ["title : field is mandatory"]
}
```

**Malformed JSON:**

```bash
curl -X POST http://localhost:4567/todos \
  -H "Content-Type: application/json" \
  -d '{"title":}'
```

```json
{
  "errorMessages": ["com.google.gson.stream.MalformedJsonException: Expected value at line 1 column 10 path $."]
}
```

**Invalid boolean value:**

```bash
curl -X POST http://localhost:4567/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "doneStatus": "notabool"}'
```

```json
{
  "errorMessages": ["Failed Validation: doneStatus should be BOOLEAN"]
}
```

**Linking to nonexistent entity:**

```bash
curl -X POST http://localhost:4567/todos/1/task-of \
  -H "Content-Type: application/json" \
  -d '{"id": "999999"}'
```

Response: `404 Not Found`

---

## Known Bugs & Quirks

### 1. Boolean String Inconsistency

The API **returns** boolean fields as strings (`"true"`, `"false"`) in JSON responses, but **rejects** string boolean values in request bodies. You must send actual JSON booleans:

```json
// CORRECT - API accepts this
{"title": "Test", "doneStatus": false}

// INCORRECT - API rejects this with 400
{"title": "Test", "doneStatus": "false"}
```

### 2. HEAD Method Returns 405

The HTTP `HEAD` method returns `405 Method Not Allowed` on all endpoints, despite HEAD being a standard HTTP method that should behave like GET without a response body.

### 3. ID Assignment on Create

Attempting to specify an `id` field when creating a new entity (via `POST /todos`, `POST /projects`, `POST /categories`) will be rejected with `400 Bad Request`. IDs are always auto-generated by the server.

### 4. PUT Behaves Like POST for Amendment

The `PUT` method on `/:id` endpoints behaves similarly to `POST` for amendment rather than strict REST semantics where PUT would replace the entire resource.

### 5. Extra Unknown Fields

Sending unknown/extra fields in the request body may be silently ignored or may cause a `400` error depending on the field name.

---

## Endpoint Summary

| # | Method | Endpoint | Description |
|---|---|---|---|
| 1 | `GET` | `/todos` | List all todos |
| 2 | `POST` | `/todos` | Create a new todo |
| 3 | `OPTIONS` | `/todos` | Get allowed methods |
| 4 | `HEAD` | `/todos` | (Returns 405) |
| 5 | `GET` | `/todos/:id` | Get a specific todo |
| 6 | `POST` | `/todos/:id` | Amend a todo (partial update) |
| 7 | `PUT` | `/todos/:id` | Replace/amend a todo |
| 8 | `DELETE` | `/todos/:id` | Delete a todo |
| 9 | `OPTIONS` | `/todos/:id` | Get allowed methods |
| 10 | `HEAD` | `/todos/:id` | (Returns 405) |
| 11 | `GET` | `/todos/:id/task-of` | Get related projects |
| 12 | `POST` | `/todos/:id/task-of` | Link todo to project |
| 13 | `DELETE` | `/todos/:id/task-of/:id` | Unlink todo from project |
| 14 | `GET` | `/todos/:id/categories` | Get related categories |
| 15 | `POST` | `/todos/:id/categories` | Link todo to category |
| 16 | `DELETE` | `/todos/:id/categories/:id` | Unlink todo from category |
| 17 | `GET` | `/projects` | List all projects |
| 18 | `POST` | `/projects` | Create a new project |
| 19 | `OPTIONS` | `/projects` | Get allowed methods |
| 20 | `HEAD` | `/projects` | (Returns 405) |
| 21 | `GET` | `/projects/:id` | Get a specific project |
| 22 | `POST` | `/projects/:id` | Amend a project (partial update) |
| 23 | `PUT` | `/projects/:id` | Replace/amend a project |
| 24 | `DELETE` | `/projects/:id` | Delete a project |
| 25 | `OPTIONS` | `/projects/:id` | Get allowed methods |
| 26 | `HEAD` | `/projects/:id` | (Returns 405) |
| 27 | `GET` | `/projects/:id/tasks` | Get related todos |
| 28 | `POST` | `/projects/:id/tasks` | Link project to todo |
| 29 | `DELETE` | `/projects/:id/tasks/:id` | Unlink project from todo |
| 30 | `GET` | `/projects/:id/categories` | Get related categories |
| 31 | `POST` | `/projects/:id/categories` | Link project to category |
| 32 | `DELETE` | `/projects/:id/categories/:id` | Unlink project from category |
| 33 | `GET` | `/categories` | List all categories |
| 34 | `POST` | `/categories` | Create a new category |
| 35 | `OPTIONS` | `/categories` | Get allowed methods |
| 36 | `HEAD` | `/categories` | (Returns 405) |
| 37 | `GET` | `/categories/:id` | Get a specific category |
| 38 | `POST` | `/categories/:id` | Amend a category (partial update) |
| 39 | `PUT` | `/categories/:id` | Replace/amend a category |
| 40 | `DELETE` | `/categories/:id` | Delete a category |
| 41 | `OPTIONS` | `/categories/:id` | Get allowed methods |
| 42 | `HEAD` | `/categories/:id` | (Returns 405) |
| 43 | `GET` | `/categories/:id/todos` | Get related todos |
| 44 | `POST` | `/categories/:id/todos` | Link category to todo |
| 45 | `DELETE` | `/categories/:id/todos/:id` | Unlink category from todo |
| 46 | `GET` | `/categories/:id/projects` | Get related projects |
| 47 | `POST` | `/categories/:id/projects` | Link category to project |
| 48 | `DELETE` | `/categories/:id/projects/:id` | Unlink category from project |
| 49 | `GET` | `/docs` | API documentation (HTML) |
| 50 | `GET` | `/shutdown` | Shut down the server |
| 51 | `GET` | `/gui` | Default GUI / Entities Explorer |

**Total: 51 endpoints**
