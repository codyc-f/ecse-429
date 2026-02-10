"""
Unit tests for /categories API endpoints.

Covers:
  - GET /categories                            (list all)
  - POST /categories                           (create)
  - GET /categories/:id                        (get by id)
  - POST /categories/:id                       (amend)
  - PUT /categories/:id                        (replace/amend)
  - DELETE /categories/:id                     (delete)
  - GET /categories/:id/todos                  (get related todos)
  - POST /categories/:id/todos                 (link to todo)
  - DELETE /categories/:id/todos/:id           (unlink from todo)
  - GET /categories/:id/projects               (get related projects)
  - POST /categories/:id/projects              (link to project)
  - DELETE /categories/:id/projects/:id        (unlink from project)
"""
import pytest
import requests
import xmltodict

BASE_URL = "http://localhost:4567"
JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
XML_HEADERS = {"Content-Type": "application/xml", "Accept": "application/xml"}


# ====================================================================
# GET /categories — List All Categories
# ====================================================================
class TestGetAllCategories:
    """Tests for GET /categories."""

    def test_get_all_categories_returns_200(self):
        r = requests.get(f"{BASE_URL}/categories", headers=JSON_HEADERS)
        assert r.status_code == 200

    def test_get_all_categories_returns_list(self):
        r = requests.get(f"{BASE_URL}/categories", headers=JSON_HEADERS)
        data = r.json()
        assert "categories" in data
        assert isinstance(data["categories"], list)

    def test_get_all_categories_json_format(self):
        r = requests.get(f"{BASE_URL}/categories", headers=JSON_HEADERS)
        assert "application/json" in r.headers.get("Content-Type", "")

    def test_get_all_categories_xml_format(self):
        r = requests.get(f"{BASE_URL}/categories", headers=XML_HEADERS)
        assert "application/xml" in r.headers.get("Content-Type", "")
        parsed = xmltodict.parse(r.text)
        assert "categories" in parsed


# ====================================================================
# POST /categories — Create a Category
# ====================================================================
class TestCreateCategory:
    """Tests for POST /categories."""

    def test_create_category_returns_201(self):
        body = {"title": "New Cat", "description": "desc"}
        r = requests.post(f"{BASE_URL}/categories", json=body, headers=JSON_HEADERS)
        assert r.status_code == 201

    def test_create_category_has_id(self):
        body = {"title": "New Cat"}
        r = requests.post(f"{BASE_URL}/categories", json=body, headers=JSON_HEADERS)
        data = r.json()
        assert "id" in data

    def test_create_category_sets_fields(self):
        body = {"title": "Urgent", "description": "High priority items"}
        r = requests.post(f"{BASE_URL}/categories", json=body, headers=JSON_HEADERS)
        data = r.json()
        assert data["title"] == "Urgent"
        assert data["description"] == "High priority items"

    def test_create_category_defaults(self):
        body = {"title": "Minimal"}
        r = requests.post(f"{BASE_URL}/categories", json=body, headers=JSON_HEADERS)
        data = r.json()
        assert data["description"] == ""

    def test_create_category_without_title_returns_400(self):
        body = {"description": "No title"}
        r = requests.post(f"{BASE_URL}/categories", json=body, headers=JSON_HEADERS)
        assert r.status_code == 400
        assert "errorMessages" in r.json()

    def test_create_category_with_empty_title_returns_400(self):
        body = {"title": ""}
        r = requests.post(f"{BASE_URL}/categories", json=body, headers=JSON_HEADERS)
        assert r.status_code == 400

    def test_create_category_xml_payload(self):
        xml_body = "<category><title>XML Cat</title></category>"
        r = requests.post(f"{BASE_URL}/categories", data=xml_body, headers=XML_HEADERS)
        assert r.status_code == 201
        parsed = xmltodict.parse(r.text)
        assert parsed["category"]["title"] == "XML Cat"

    def test_create_category_no_side_effects_on_todos(self, created_todo):
        before = requests.get(f"{BASE_URL}/todos").json()["todos"]
        requests.post(
            f"{BASE_URL}/categories",
            json={"title": "Isolated"},
            headers=JSON_HEADERS,
        )
        after = requests.get(f"{BASE_URL}/todos").json()["todos"]
        assert len(before) == len(after)

    def test_create_category_no_side_effects_on_projects(self, created_project):
        before = requests.get(f"{BASE_URL}/projects").json()["projects"]
        requests.post(
            f"{BASE_URL}/categories",
            json={"title": "Isolated"},
            headers=JSON_HEADERS,
        )
        after = requests.get(f"{BASE_URL}/projects").json()["projects"]
        assert len(before) == len(after)


# ====================================================================
# GET /categories/:id — Get Specific Category
# ====================================================================
class TestGetCategoryById:
    """Tests for GET /categories/:id."""

    def test_get_category_by_id_returns_200(self, created_category):
        cid = created_category["id"]
        r = requests.get(f"{BASE_URL}/categories/{cid}", headers=JSON_HEADERS)
        assert r.status_code == 200

    def test_get_category_by_id_correct_data(self, created_category):
        cid = created_category["id"]
        r = requests.get(f"{BASE_URL}/categories/{cid}", headers=JSON_HEADERS)
        data = r.json()["categories"][0]
        assert data["title"] == created_category["title"]

    def test_get_category_nonexistent_returns_404(self):
        r = requests.get(f"{BASE_URL}/categories/999999", headers=JSON_HEADERS)
        assert r.status_code == 404

    def test_get_category_by_id_xml(self, created_category):
        cid = created_category["id"]
        r = requests.get(f"{BASE_URL}/categories/{cid}", headers=XML_HEADERS)
        assert r.status_code == 200
        assert "application/xml" in r.headers.get("Content-Type", "")


# ====================================================================
# POST /categories/:id — Amend (Partial Update)
# ====================================================================
class TestAmendCategory:
    """Tests for POST /categories/:id (amend)."""

    def test_amend_category_title(self, created_category):
        cid = created_category["id"]
        r = requests.post(
            f"{BASE_URL}/categories/{cid}",
            json={"title": "Updated Cat"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["title"] == "Updated Cat"

    def test_amend_category_description(self, created_category):
        cid = created_category["id"]
        r = requests.post(
            f"{BASE_URL}/categories/{cid}",
            json={"description": "New Desc"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["description"] == "New Desc"

    def test_amend_nonexistent_category_returns_404(self):
        r = requests.post(
            f"{BASE_URL}/categories/999999",
            json={"title": "Ghost"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 404

    def test_amend_preserves_unmodified_fields(self, created_category):
        cid = created_category["id"]
        requests.post(
            f"{BASE_URL}/categories/{cid}",
            json={"title": "Only Title"},
            headers=JSON_HEADERS,
        )
        r = requests.get(f"{BASE_URL}/categories/{cid}", headers=JSON_HEADERS)
        data = r.json()["categories"][0]
        assert data["title"] == "Only Title"
        assert data["description"] == created_category["description"]


# ====================================================================
# PUT /categories/:id — Replace / Full Update
# ====================================================================
class TestPutCategory:
    """Tests for PUT /categories/:id."""

    def test_put_category_updates_fields(self, created_category):
        cid = created_category["id"]
        body = {"title": "Put Cat", "description": "Put Desc"}
        r = requests.put(
            f"{BASE_URL}/categories/{cid}", json=body, headers=JSON_HEADERS
        )
        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "Put Cat"
        assert data["description"] == "Put Desc"

    def test_put_nonexistent_category_returns_404(self):
        body = {"title": "Ghost"}
        r = requests.put(
            f"{BASE_URL}/categories/999999", json=body, headers=JSON_HEADERS
        )
        assert r.status_code == 404

    def test_put_category_xml(self, created_category):
        cid = created_category["id"]
        xml_body = "<category><title>XML Put</title></category>"
        r = requests.put(
            f"{BASE_URL}/categories/{cid}", data=xml_body, headers=XML_HEADERS
        )
        assert r.status_code == 200


# ====================================================================
# DELETE /categories/:id — Delete Category
# ====================================================================
class TestDeleteCategory:
    """Tests for DELETE /categories/:id."""

    def test_delete_category_returns_200(self, created_category):
        cid = created_category["id"]
        r = requests.delete(f"{BASE_URL}/categories/{cid}")
        assert r.status_code == 200

    def test_delete_category_actually_removes_it(self, created_category):
        cid = created_category["id"]
        requests.delete(f"{BASE_URL}/categories/{cid}")
        r = requests.get(f"{BASE_URL}/categories/{cid}", headers=JSON_HEADERS)
        assert r.status_code == 404

    def test_delete_nonexistent_category_returns_404(self):
        r = requests.delete(f"{BASE_URL}/categories/999999")
        assert r.status_code == 404

    def test_delete_already_deleted_category_returns_404(self, created_category):
        cid = created_category["id"]
        requests.delete(f"{BASE_URL}/categories/{cid}")
        r = requests.delete(f"{BASE_URL}/categories/{cid}")
        assert r.status_code == 404

    def test_delete_category_no_side_effects(self, created_category):
        other = requests.post(
            f"{BASE_URL}/categories",
            json={"title": "Other"},
            headers=JSON_HEADERS,
        ).json()
        before = requests.get(f"{BASE_URL}/categories").json()["categories"]
        requests.delete(f"{BASE_URL}/categories/{created_category['id']}")
        after = requests.get(f"{BASE_URL}/categories").json()["categories"]
        assert len(after) == len(before) - 1
        assert any(c["id"] == other["id"] for c in after)


# ====================================================================
# GET /categories/:id/todos — Related Todos
# ====================================================================
class TestCategoryTodos:
    """Tests for the category <-> todo relationship."""

    def test_get_todos_returns_200(self, created_category):
        cid = created_category["id"]
        r = requests.get(f"{BASE_URL}/categories/{cid}/todos", headers=JSON_HEADERS)
        assert r.status_code == 200

    def test_get_todos_initially_empty(self, created_category):
        cid = created_category["id"]
        r = requests.get(f"{BASE_URL}/categories/{cid}/todos", headers=JSON_HEADERS)
        todos = r.json().get("todos", [])
        assert len(todos) == 0

    def test_link_category_to_todo_creates_new_todo(self, created_category):
        """POST /categories/:id/todos creates a NEW todo linked to the category."""
        cid = created_category["id"]
        r = requests.post(
            f"{BASE_URL}/categories/{cid}/todos",
            json={"title": "Linked Todo"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 201
        new_tid = r.json()["id"]
        r2 = requests.get(f"{BASE_URL}/categories/{cid}/todos", headers=JSON_HEADERS)
        todos = r2.json().get("todos", [])
        assert any(t["id"] == new_tid for t in todos)

    def test_unlink_category_from_todo(self, created_category):
        cid = created_category["id"]
        r = requests.post(
            f"{BASE_URL}/categories/{cid}/todos",
            json={"title": "To Unlink"},
            headers=JSON_HEADERS,
        )
        tid = r.json()["id"]
        r2 = requests.delete(f"{BASE_URL}/categories/{cid}/todos/{tid}")
        assert r2.status_code == 200
        r3 = requests.get(f"{BASE_URL}/categories/{cid}/todos", headers=JSON_HEADERS)
        todos = r3.json().get("todos", [])
        assert not any(t["id"] == tid for t in todos)

    def test_link_category_to_todo_with_id_rejected(self, created_category, created_todo):
        """BUG/Undocumented: Cannot link to an existing todo by id."""
        cid = created_category["id"]
        tid = created_todo["id"]
        r = requests.post(
            f"{BASE_URL}/categories/{cid}/todos",
            json={"id": tid},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 400


# ====================================================================
# GET /categories/:id/projects — Related Projects
# ====================================================================
class TestCategoryProjects:
    """Tests for the category <-> project relationship."""

    def test_get_projects_returns_200(self, created_category):
        cid = created_category["id"]
        r = requests.get(
            f"{BASE_URL}/categories/{cid}/projects", headers=JSON_HEADERS
        )
        assert r.status_code == 200

    def test_get_projects_initially_empty(self, created_category):
        cid = created_category["id"]
        r = requests.get(
            f"{BASE_URL}/categories/{cid}/projects", headers=JSON_HEADERS
        )
        projects = r.json().get("projects", [])
        assert len(projects) == 0

    def test_link_category_to_project_creates_new_project(self, created_category):
        """POST /categories/:id/projects creates a NEW project linked to the category."""
        cid = created_category["id"]
        r = requests.post(
            f"{BASE_URL}/categories/{cid}/projects",
            json={"title": "Linked Proj"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 201
        new_pid = r.json()["id"]
        r2 = requests.get(
            f"{BASE_URL}/categories/{cid}/projects", headers=JSON_HEADERS
        )
        projects = r2.json().get("projects", [])
        assert any(p["id"] == new_pid for p in projects)

    def test_unlink_category_from_project(self, created_category):
        cid = created_category["id"]
        r = requests.post(
            f"{BASE_URL}/categories/{cid}/projects",
            json={"title": "To Unlink Proj"},
            headers=JSON_HEADERS,
        )
        pid = r.json()["id"]
        r2 = requests.delete(f"{BASE_URL}/categories/{cid}/projects/{pid}")
        assert r2.status_code == 200
        r3 = requests.get(
            f"{BASE_URL}/categories/{cid}/projects", headers=JSON_HEADERS
        )
        projects = r3.json().get("projects", [])
        assert not any(p["id"] == pid for p in projects)

    def test_link_category_to_project_with_id_rejected(self, created_category, created_project):
        """BUG/Undocumented: Cannot link to an existing project by id."""
        cid = created_category["id"]
        pid = created_project["id"]
        r = requests.post(
            f"{BASE_URL}/categories/{cid}/projects",
            json={"id": pid},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 400


# ====================================================================
# HEAD and OPTIONS
# ====================================================================
class TestCategoryHeadAndOptions:
    """Tests for HEAD and OPTIONS on /categories endpoints."""

    def test_head_categories(self):
        r = requests.head(f"{BASE_URL}/categories")
        assert r.status_code in (200, 405)

    def test_options_categories(self):
        r = requests.options(f"{BASE_URL}/categories")
        assert r.status_code == 200

    def test_head_category_by_id(self, created_category):
        r = requests.head(f"{BASE_URL}/categories/{created_category['id']}")
        assert r.status_code in (200, 405)
