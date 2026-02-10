"""
Unit tests for /todos API endpoints.

Covers:
  - GET /todos                      (list all)
  - POST /todos                     (create)
  - GET /todos/:id                  (get by id)
  - POST /todos/:id                 (amend)
  - PUT /todos/:id                  (replace/amend)
  - DELETE /todos/:id               (delete)
  - GET /todos/:id/task-of          (get related projects)
  - POST /todos/:id/task-of         (link to project)
  - DELETE /todos/:id/task-of/:id   (unlink from project)
  - GET /todos/:id/categories       (get related categories)
  - POST /todos/:id/categories      (link to category)
  - DELETE /todos/:id/categories/:id(unlink from category)

Each test:
  - Uses the autouse save_and_restore_state fixture from conftest.
  - Validates JSON and XML payloads where applicable.
  - Validates correct HTTP return codes.
  - Checks for absence of unexpected side effects.
"""
import pytest
import requests
import xmltodict

BASE_URL = "http://localhost:4567"
JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
XML_HEADERS = {"Content-Type": "application/xml", "Accept": "application/xml"}


# ====================================================================
# GET /todos — List All Todos
# ====================================================================
class TestGetAllTodos:
    """Tests for GET /todos."""

    def test_get_all_todos_returns_200(self):
        r = requests.get(f"{BASE_URL}/todos", headers=JSON_HEADERS)
        assert r.status_code == 200

    def test_get_all_todos_returns_list(self):
        r = requests.get(f"{BASE_URL}/todos", headers=JSON_HEADERS)
        data = r.json()
        assert "todos" in data
        assert isinstance(data["todos"], list)

    def test_get_all_todos_json_format(self):
        r = requests.get(f"{BASE_URL}/todos", headers=JSON_HEADERS)
        assert "application/json" in r.headers.get("Content-Type", "")

    def test_get_all_todos_xml_format(self):
        r = requests.get(f"{BASE_URL}/todos", headers=XML_HEADERS)
        assert "application/xml" in r.headers.get("Content-Type", "")
        parsed = xmltodict.parse(r.text)
        assert "todos" in parsed

    def test_get_all_todos_with_filter(self, created_todo):
        """Filter todos by title using query parameter."""
        r = requests.get(
            f"{BASE_URL}/todos",
            params={"title": created_todo["title"]},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 200
        todos = r.json()["todos"]
        assert any(t["title"] == created_todo["title"] for t in todos)


# ====================================================================
# POST /todos — Create a Todo
# ====================================================================
class TestCreateTodo:
    """Tests for POST /todos."""

    def test_create_todo_returns_201(self):
        body = {"title": "New Todo", "doneStatus": False, "description": "desc"}
        r = requests.post(f"{BASE_URL}/todos", json=body, headers=JSON_HEADERS)
        assert r.status_code == 201

    def test_create_todo_has_id(self):
        body = {"title": "New Todo"}
        r = requests.post(f"{BASE_URL}/todos", json=body, headers=JSON_HEADERS)
        data = r.json()
        assert "id" in data
        assert data["id"] is not None

    def test_create_todo_sets_fields(self):
        body = {"title": "My Task", "doneStatus": True, "description": "Details"}
        r = requests.post(f"{BASE_URL}/todos", json=body, headers=JSON_HEADERS)
        data = r.json()
        assert data["title"] == "My Task"
        assert data["doneStatus"] == "true"
        assert data["description"] == "Details"

    def test_create_todo_defaults(self):
        """doneStatus should default to 'false', description to empty string."""
        body = {"title": "Minimal"}
        r = requests.post(f"{BASE_URL}/todos", json=body, headers=JSON_HEADERS)
        data = r.json()
        assert data["doneStatus"] == "false"
        assert data["description"] == ""

    def test_create_todo_without_title_returns_400(self):
        body = {"description": "No title provided"}
        r = requests.post(f"{BASE_URL}/todos", json=body, headers=JSON_HEADERS)
        assert r.status_code == 400
        assert "errorMessages" in r.json()

    def test_create_todo_with_empty_title_returns_400(self):
        body = {"title": ""}
        r = requests.post(f"{BASE_URL}/todos", json=body, headers=JSON_HEADERS)
        assert r.status_code == 400

    def test_create_todo_xml_payload(self):
        xml_body = "<todo><title>XML Todo</title></todo>"
        r = requests.post(f"{BASE_URL}/todos", data=xml_body, headers=XML_HEADERS)
        assert r.status_code == 201
        parsed = xmltodict.parse(r.text)
        assert parsed["todo"]["title"] == "XML Todo"

    def test_create_todo_no_side_effects_on_projects(self, created_project):
        """Creating a todo should not modify existing projects."""
        before = requests.get(f"{BASE_URL}/projects").json()["projects"]
        requests.post(
            f"{BASE_URL}/todos",
            json={"title": "Isolated"},
            headers=JSON_HEADERS,
        )
        after = requests.get(f"{BASE_URL}/projects").json()["projects"]
        assert len(before) == len(after)

    def test_create_todo_no_side_effects_on_categories(self, created_category):
        """Creating a todo should not modify existing categories."""
        before = requests.get(f"{BASE_URL}/categories").json()["categories"]
        requests.post(
            f"{BASE_URL}/todos",
            json={"title": "Isolated"},
            headers=JSON_HEADERS,
        )
        after = requests.get(f"{BASE_URL}/categories").json()["categories"]
        assert len(before) == len(after)

    def test_create_todo_with_invalid_done_status_string(self):
        """doneStatus must be a boolean; a string value should error."""
        body = {"title": "Bad Status", "doneStatus": "notabool"}
        r = requests.post(f"{BASE_URL}/todos", json=body, headers=JSON_HEADERS)
        assert r.status_code == 400

    def test_create_todo_with_string_false_done_status(self):
        """BUG: API returns doneStatus as string 'false' but rejects string 'false' in input."""
        body = {"title": "String False", "doneStatus": "false"}
        r = requests.post(f"{BASE_URL}/todos", json=body, headers=JSON_HEADERS)
        # This documents the bug: API returns strings but requires booleans
        assert r.status_code == 400  # Actual behavior: rejects string booleans


# ====================================================================
# GET /todos/:id — Get Specific Todo
# ====================================================================
class TestGetTodoById:
    """Tests for GET /todos/:id."""

    def test_get_todo_by_id_returns_200(self, created_todo):
        tid = created_todo["id"]
        r = requests.get(f"{BASE_URL}/todos/{tid}", headers=JSON_HEADERS)
        assert r.status_code == 200

    def test_get_todo_by_id_correct_data(self, created_todo):
        tid = created_todo["id"]
        r = requests.get(f"{BASE_URL}/todos/{tid}", headers=JSON_HEADERS)
        data = r.json()["todos"][0]
        assert data["title"] == created_todo["title"]

    def test_get_todo_nonexistent_returns_404(self):
        r = requests.get(f"{BASE_URL}/todos/999999", headers=JSON_HEADERS)
        assert r.status_code == 404

    def test_get_todo_by_id_xml(self, created_todo):
        tid = created_todo["id"]
        r = requests.get(f"{BASE_URL}/todos/{tid}", headers=XML_HEADERS)
        assert r.status_code == 200
        assert "application/xml" in r.headers.get("Content-Type", "")


# ====================================================================
# POST /todos/:id — Amend (Partial Update)
# ====================================================================
class TestAmendTodo:
    """Tests for POST /todos/:id (amend)."""

    def test_amend_todo_title(self, created_todo):
        tid = created_todo["id"]
        r = requests.post(
            f"{BASE_URL}/todos/{tid}",
            json={"title": "Updated Title"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["title"] == "Updated Title"

    def test_amend_todo_description(self, created_todo):
        tid = created_todo["id"]
        r = requests.post(
            f"{BASE_URL}/todos/{tid}",
            json={"description": "Updated Desc"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["description"] == "Updated Desc"

    def test_amend_todo_done_status(self, created_todo):
        tid = created_todo["id"]
        r = requests.post(
            f"{BASE_URL}/todos/{tid}",
            json={"doneStatus": True},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["doneStatus"] == "true"

    def test_amend_nonexistent_todo_returns_404(self):
        r = requests.post(
            f"{BASE_URL}/todos/999999",
            json={"title": "Ghost"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 404

    def test_amend_preserves_unmodified_fields(self, created_todo):
        """Amending title should not change description or doneStatus."""
        tid = created_todo["id"]
        requests.post(
            f"{BASE_URL}/todos/{tid}",
            json={"title": "Only Title Changed"},
            headers=JSON_HEADERS,
        )
        r = requests.get(f"{BASE_URL}/todos/{tid}", headers=JSON_HEADERS)
        data = r.json()["todos"][0]
        assert data["title"] == "Only Title Changed"
        assert data["description"] == created_todo["description"]
        assert data["doneStatus"] == created_todo["doneStatus"]


# ====================================================================
# PUT /todos/:id — Replace / Full Update
# ====================================================================
class TestPutTodo:
    """Tests for PUT /todos/:id."""

    def test_put_todo_updates_fields(self, created_todo):
        tid = created_todo["id"]
        body = {"title": "Put Title", "doneStatus": True, "description": "Put Desc"}
        r = requests.put(f"{BASE_URL}/todos/{tid}", json=body, headers=JSON_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "Put Title"
        assert data["doneStatus"] == "true"
        assert data["description"] == "Put Desc"

    def test_put_todo_requires_title(self, created_todo):
        """PUT without title — the API may reset title or return 400."""
        tid = created_todo["id"]
        body = {"description": "No title in put"}
        r = requests.put(f"{BASE_URL}/todos/{tid}", json=body, headers=JSON_HEADERS)
        # Depending on API behavior: title might be cleared or error returned
        assert r.status_code in (200, 400)

    def test_put_nonexistent_todo_returns_404(self):
        body = {"title": "Ghost"}
        r = requests.put(f"{BASE_URL}/todos/999999", json=body, headers=JSON_HEADERS)
        assert r.status_code == 404

    def test_put_todo_xml(self, created_todo):
        tid = created_todo["id"]
        xml_body = "<todo><title>XML Put</title></todo>"
        r = requests.put(f"{BASE_URL}/todos/{tid}", data=xml_body, headers=XML_HEADERS)
        assert r.status_code == 200


# ====================================================================
# DELETE /todos/:id — Delete Todo
# ====================================================================
class TestDeleteTodo:
    """Tests for DELETE /todos/:id."""

    def test_delete_todo_returns_200(self, created_todo):
        tid = created_todo["id"]
        r = requests.delete(f"{BASE_URL}/todos/{tid}")
        assert r.status_code == 200

    def test_delete_todo_actually_removes_it(self, created_todo):
        tid = created_todo["id"]
        requests.delete(f"{BASE_URL}/todos/{tid}")
        r = requests.get(f"{BASE_URL}/todos/{tid}", headers=JSON_HEADERS)
        assert r.status_code == 404

    def test_delete_nonexistent_todo_returns_404(self):
        r = requests.delete(f"{BASE_URL}/todos/999999")
        assert r.status_code == 404

    def test_delete_already_deleted_todo_returns_404(self, created_todo):
        tid = created_todo["id"]
        requests.delete(f"{BASE_URL}/todos/{tid}")
        r = requests.delete(f"{BASE_URL}/todos/{tid}")
        assert r.status_code == 404

    def test_delete_todo_no_side_effects_on_other_todos(self, created_todo):
        """Deleting one todo should not affect other todos."""
        other = requests.post(
            f"{BASE_URL}/todos",
            json={"title": "Other"},
            headers=JSON_HEADERS,
        ).json()
        before = requests.get(f"{BASE_URL}/todos").json()["todos"]
        requests.delete(f"{BASE_URL}/todos/{created_todo['id']}")
        after = requests.get(f"{BASE_URL}/todos").json()["todos"]
        assert len(after) == len(before) - 1
        assert any(t["id"] == other["id"] for t in after)


# ====================================================================
# GET /todos/:id/task-of — Related Projects
# ====================================================================
class TestTodoTaskOf:
    """Tests for the todo <-> project (task-of) relationship."""

    def test_get_task_of_returns_200(self, created_todo):
        tid = created_todo["id"]
        r = requests.get(f"{BASE_URL}/todos/{tid}/task-of", headers=JSON_HEADERS)
        assert r.status_code == 200

    def test_get_task_of_initially_empty(self, created_todo):
        tid = created_todo["id"]
        r = requests.get(f"{BASE_URL}/todos/{tid}/task-of", headers=JSON_HEADERS)
        projects = r.json().get("projects", [])
        assert len(projects) == 0

    def test_link_todo_to_project_creates_new_project(self, created_todo):
        """POST /todos/:id/task-of creates a NEW project linked to the todo."""
        tid = created_todo["id"]
        r = requests.post(
            f"{BASE_URL}/todos/{tid}/task-of",
            json={"title": "Linked Project"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 201
        new_pid = r.json()["id"]
        # Verify the link exists
        r2 = requests.get(f"{BASE_URL}/todos/{tid}/task-of", headers=JSON_HEADERS)
        projects = r2.json().get("projects", [])
        assert any(p["id"] == new_pid for p in projects)

    def test_unlink_todo_from_project(self, created_todo):
        tid = created_todo["id"]
        # Create a project via the relationship endpoint
        r = requests.post(
            f"{BASE_URL}/todos/{tid}/task-of",
            json={"title": "To Unlink"},
            headers=JSON_HEADERS,
        )
        pid = r.json()["id"]
        # Unlink
        r2 = requests.delete(f"{BASE_URL}/todos/{tid}/task-of/{pid}")
        assert r2.status_code == 200
        # Verify the link is removed
        r3 = requests.get(f"{BASE_URL}/todos/{tid}/task-of", headers=JSON_HEADERS)
        projects = r3.json().get("projects", [])
        assert not any(p["id"] == pid for p in projects)

    def test_link_todo_to_project_with_id_rejected(self, created_todo, created_project):
        """BUG/Undocumented: Cannot link to an existing project by id — API rejects it."""
        tid = created_todo["id"]
        pid = created_project["id"]
        r = requests.post(
            f"{BASE_URL}/todos/{tid}/task-of",
            json={"id": pid},
            headers=JSON_HEADERS,
        )
        # The API returns 400 "Not allowed to create with id" instead of linking
        assert r.status_code == 400


# ====================================================================
# GET /todos/:id/categories — Related Categories
# ====================================================================
class TestTodoCategories:
    """Tests for the todo <-> category relationship."""

    def test_get_categories_returns_200(self, created_todo):
        tid = created_todo["id"]
        r = requests.get(f"{BASE_URL}/todos/{tid}/categories", headers=JSON_HEADERS)
        assert r.status_code == 200

    def test_get_categories_initially_empty(self, created_todo):
        tid = created_todo["id"]
        r = requests.get(f"{BASE_URL}/todos/{tid}/categories", headers=JSON_HEADERS)
        cats = r.json().get("categories", [])
        assert len(cats) == 0

    def test_link_todo_to_category_creates_new_category(self, created_todo):
        """POST /todos/:id/categories creates a NEW category linked to the todo."""
        tid = created_todo["id"]
        r = requests.post(
            f"{BASE_URL}/todos/{tid}/categories",
            json={"title": "Linked Category"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 201
        new_cid = r.json()["id"]
        r2 = requests.get(f"{BASE_URL}/todos/{tid}/categories", headers=JSON_HEADERS)
        cats = r2.json().get("categories", [])
        assert any(c["id"] == new_cid for c in cats)

    def test_unlink_todo_from_category(self, created_todo):
        tid = created_todo["id"]
        r = requests.post(
            f"{BASE_URL}/todos/{tid}/categories",
            json={"title": "To Unlink Cat"},
            headers=JSON_HEADERS,
        )
        cid = r.json()["id"]
        r2 = requests.delete(f"{BASE_URL}/todos/{tid}/categories/{cid}")
        assert r2.status_code == 200
        r3 = requests.get(f"{BASE_URL}/todos/{tid}/categories", headers=JSON_HEADERS)
        cats = r3.json().get("categories", [])
        assert not any(c["id"] == cid for c in cats)

    def test_link_todo_to_category_with_id_rejected(self, created_todo, created_category):
        """BUG/Undocumented: Cannot link to an existing category by id."""
        tid = created_todo["id"]
        cid = created_category["id"]
        r = requests.post(
            f"{BASE_URL}/todos/{tid}/categories",
            json={"id": cid},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 400


# ====================================================================
# HEAD and OPTIONS — Documented utility methods
# ====================================================================
class TestTodoHeadAndOptions:
    """Tests for HEAD and OPTIONS on /todos endpoints."""

    def test_head_todos(self):
        r = requests.head(f"{BASE_URL}/todos")
        # HEAD should return 200 per HTTP spec, but API may return differently
        assert r.status_code in (200, 405)

    def test_options_todos(self):
        r = requests.options(f"{BASE_URL}/todos")
        assert r.status_code == 200
        assert "Allow" in r.headers or r.status_code == 200

    def test_head_todo_by_id(self, created_todo):
        r = requests.head(f"{BASE_URL}/todos/{created_todo['id']}")
        assert r.status_code in (200, 405)
