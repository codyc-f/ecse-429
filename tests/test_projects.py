"""
Unit tests for /projects API endpoints.

Covers:
  - GET /projects                          (list all)
  - POST /projects                         (create)
  - GET /projects/:id                      (get by id)
  - POST /projects/:id                     (amend)
  - PUT /projects/:id                      (replace/amend)
  - DELETE /projects/:id                   (delete)
  - GET /projects/:id/tasks                (get related todos)
  - POST /projects/:id/tasks               (link to todo)
  - DELETE /projects/:id/tasks/:id         (unlink from todo)
  - GET /projects/:id/categories           (get related categories)
  - POST /projects/:id/categories          (link to category)
  - DELETE /projects/:id/categories/:id    (unlink from category)
"""
import pytest
import requests
import xmltodict

BASE_URL = "http://localhost:4567"
JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
XML_HEADERS = {"Content-Type": "application/xml", "Accept": "application/xml"}


# ====================================================================
# GET /projects — List All Projects
# ====================================================================
class TestGetAllProjects:
    """Tests for GET /projects."""

    def test_get_all_projects_returns_200(self):
        r = requests.get(f"{BASE_URL}/projects", headers=JSON_HEADERS)
        assert r.status_code == 200

    def test_get_all_projects_returns_list(self):
        r = requests.get(f"{BASE_URL}/projects", headers=JSON_HEADERS)
        data = r.json()
        assert "projects" in data
        assert isinstance(data["projects"], list)

    def test_get_all_projects_json_format(self):
        r = requests.get(f"{BASE_URL}/projects", headers=JSON_HEADERS)
        assert "application/json" in r.headers.get("Content-Type", "")

    def test_get_all_projects_xml_format(self):
        r = requests.get(f"{BASE_URL}/projects", headers=XML_HEADERS)
        assert "application/xml" in r.headers.get("Content-Type", "")
        parsed = xmltodict.parse(r.text)
        assert "projects" in parsed


# ====================================================================
# POST /projects — Create a Project
# ====================================================================
class TestCreateProject:
    """Tests for POST /projects."""

    def test_create_project_returns_201(self):
        body = {"title": "New Proj", "completed": False, "active": True}
        r = requests.post(f"{BASE_URL}/projects", json=body, headers=JSON_HEADERS)
        assert r.status_code == 201

    def test_create_project_has_id(self):
        body = {"title": "New Proj"}
        r = requests.post(f"{BASE_URL}/projects", json=body, headers=JSON_HEADERS)
        data = r.json()
        assert "id" in data

    def test_create_project_sets_fields(self):
        body = {
            "title": "Alpha",
            "description": "Desc",
            "completed": True,
            "active": False,
        }
        r = requests.post(f"{BASE_URL}/projects", json=body, headers=JSON_HEADERS)
        data = r.json()
        assert data["title"] == "Alpha"
        assert data["description"] == "Desc"
        assert data["completed"] == "true"
        assert data["active"] == "false"

    def test_create_project_defaults(self):
        """Minimal project creation — check default field values."""
        body = {"title": "Minimal"}
        r = requests.post(f"{BASE_URL}/projects", json=body, headers=JSON_HEADERS)
        data = r.json()
        assert data["completed"] == "false"
        assert data["active"] == "false"
        assert data["description"] == ""

    def test_create_project_without_title(self):
        """Projects may allow empty title; document observed behavior."""
        body = {"description": "No title"}
        r = requests.post(f"{BASE_URL}/projects", json=body, headers=JSON_HEADERS)
        # Project title is not mandatory, so 201 is expected
        assert r.status_code == 201

    def test_create_project_xml_payload(self):
        xml_body = "<project><title>XML Proj</title></project>"
        r = requests.post(f"{BASE_URL}/projects", data=xml_body, headers=XML_HEADERS)
        assert r.status_code == 201
        parsed = xmltodict.parse(r.text)
        assert parsed["project"]["title"] == "XML Proj"

    def test_create_project_no_side_effects_on_todos(self, created_todo):
        """Creating a project should not modify existing todos."""
        before = requests.get(f"{BASE_URL}/todos").json()["todos"]
        requests.post(
            f"{BASE_URL}/projects", json={"title": "Isolated"}, headers=JSON_HEADERS
        )
        after = requests.get(f"{BASE_URL}/todos").json()["todos"]
        assert len(before) == len(after)

    def test_create_project_string_completed_value_rejected(self):
        """BUG: API returns completed as string but rejects string input."""
        body = {"title": "Bad", "completed": "false"}
        r = requests.post(f"{BASE_URL}/projects", json=body, headers=JSON_HEADERS)
        assert r.status_code == 400

    def test_create_project_invalid_active_value(self):
        body = {"title": "Bad", "active": "notbool"}
        r = requests.post(f"{BASE_URL}/projects", json=body, headers=JSON_HEADERS)
        assert r.status_code == 400


# ====================================================================
# GET /projects/:id — Get Specific Project
# ====================================================================
class TestGetProjectById:
    """Tests for GET /projects/:id."""

    def test_get_project_by_id_returns_200(self, created_project):
        pid = created_project["id"]
        r = requests.get(f"{BASE_URL}/projects/{pid}", headers=JSON_HEADERS)
        assert r.status_code == 200

    def test_get_project_by_id_correct_data(self, created_project):
        pid = created_project["id"]
        r = requests.get(f"{BASE_URL}/projects/{pid}", headers=JSON_HEADERS)
        data = r.json()["projects"][0]
        assert data["title"] == created_project["title"]

    def test_get_project_nonexistent_returns_404(self):
        r = requests.get(f"{BASE_URL}/projects/999999", headers=JSON_HEADERS)
        assert r.status_code == 404

    def test_get_project_by_id_xml(self, created_project):
        pid = created_project["id"]
        r = requests.get(f"{BASE_URL}/projects/{pid}", headers=XML_HEADERS)
        assert r.status_code == 200
        assert "application/xml" in r.headers.get("Content-Type", "")


# ====================================================================
# POST /projects/:id — Amend (Partial Update)
# ====================================================================
class TestAmendProject:
    """Tests for POST /projects/:id (amend)."""

    def test_amend_project_title(self, created_project):
        pid = created_project["id"]
        r = requests.post(
            f"{BASE_URL}/projects/{pid}",
            json={"title": "Updated Proj"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["title"] == "Updated Proj"

    def test_amend_project_description(self, created_project):
        pid = created_project["id"]
        r = requests.post(
            f"{BASE_URL}/projects/{pid}",
            json={"description": "New Desc"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["description"] == "New Desc"

    def test_amend_project_completed(self, created_project):
        pid = created_project["id"]
        r = requests.post(
            f"{BASE_URL}/projects/{pid}",
            json={"completed": True},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["completed"] == "true"

    def test_amend_nonexistent_project_returns_404(self):
        r = requests.post(
            f"{BASE_URL}/projects/999999",
            json={"title": "Ghost"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 404

    def test_amend_preserves_unmodified_fields(self, created_project):
        pid = created_project["id"]
        requests.post(
            f"{BASE_URL}/projects/{pid}",
            json={"title": "Only Title"},
            headers=JSON_HEADERS,
        )
        r = requests.get(f"{BASE_URL}/projects/{pid}", headers=JSON_HEADERS)
        data = r.json()["projects"][0]
        assert data["title"] == "Only Title"
        assert data["description"] == created_project["description"]


# ====================================================================
# PUT /projects/:id — Replace / Full Update
# ====================================================================
class TestPutProject:
    """Tests for PUT /projects/:id."""

    def test_put_project_updates_fields(self, created_project):
        pid = created_project["id"]
        body = {
            "title": "Put Title",
            "description": "Put Desc",
            "completed": True,
            "active": False,
        }
        r = requests.put(f"{BASE_URL}/projects/{pid}", json=body, headers=JSON_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "Put Title"

    def test_put_nonexistent_project_returns_404(self):
        body = {"title": "Ghost"}
        r = requests.put(
            f"{BASE_URL}/projects/999999", json=body, headers=JSON_HEADERS
        )
        assert r.status_code == 404

    def test_put_project_xml(self, created_project):
        pid = created_project["id"]
        xml_body = "<project><title>XML Put</title></project>"
        r = requests.put(
            f"{BASE_URL}/projects/{pid}", data=xml_body, headers=XML_HEADERS
        )
        assert r.status_code == 200


# ====================================================================
# DELETE /projects/:id — Delete Project
# ====================================================================
class TestDeleteProject:
    """Tests for DELETE /projects/:id."""

    def test_delete_project_returns_200(self, created_project):
        pid = created_project["id"]
        r = requests.delete(f"{BASE_URL}/projects/{pid}")
        assert r.status_code == 200

    def test_delete_project_actually_removes_it(self, created_project):
        pid = created_project["id"]
        requests.delete(f"{BASE_URL}/projects/{pid}")
        r = requests.get(f"{BASE_URL}/projects/{pid}", headers=JSON_HEADERS)
        assert r.status_code == 404

    def test_delete_nonexistent_project_returns_404(self):
        r = requests.delete(f"{BASE_URL}/projects/999999")
        assert r.status_code == 404

    def test_delete_already_deleted_project_returns_404(self, created_project):
        pid = created_project["id"]
        requests.delete(f"{BASE_URL}/projects/{pid}")
        r = requests.delete(f"{BASE_URL}/projects/{pid}")
        assert r.status_code == 404

    def test_delete_project_no_side_effects_on_other_projects(self, created_project):
        other = requests.post(
            f"{BASE_URL}/projects",
            json={"title": "Other"},
            headers=JSON_HEADERS,
        ).json()
        before = requests.get(f"{BASE_URL}/projects").json()["projects"]
        requests.delete(f"{BASE_URL}/projects/{created_project['id']}")
        after = requests.get(f"{BASE_URL}/projects").json()["projects"]
        assert len(after) == len(before) - 1
        assert any(p["id"] == other["id"] for p in after)


# ====================================================================
# GET /projects/:id/tasks — Related Todos
# ====================================================================
class TestProjectTasks:
    """Tests for the project <-> todo (tasks) relationship."""

    def test_get_tasks_returns_200(self, created_project):
        pid = created_project["id"]
        r = requests.get(f"{BASE_URL}/projects/{pid}/tasks", headers=JSON_HEADERS)
        assert r.status_code == 200

    def test_get_tasks_initially_empty(self, created_project):
        pid = created_project["id"]
        r = requests.get(f"{BASE_URL}/projects/{pid}/tasks", headers=JSON_HEADERS)
        todos = r.json().get("todos", [])
        assert len(todos) == 0

    def test_link_project_to_todo_creates_new_todo(self, created_project):
        """POST /projects/:id/tasks creates a NEW todo linked to the project."""
        pid = created_project["id"]
        r = requests.post(
            f"{BASE_URL}/projects/{pid}/tasks",
            json={"title": "Linked Todo"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 201
        new_tid = r.json()["id"]
        r2 = requests.get(f"{BASE_URL}/projects/{pid}/tasks", headers=JSON_HEADERS)
        todos = r2.json().get("todos", [])
        assert any(t["id"] == new_tid for t in todos)

    def test_unlink_project_from_todo(self, created_project):
        pid = created_project["id"]
        r = requests.post(
            f"{BASE_URL}/projects/{pid}/tasks",
            json={"title": "To Unlink"},
            headers=JSON_HEADERS,
        )
        tid = r.json()["id"]
        r2 = requests.delete(f"{BASE_URL}/projects/{pid}/tasks/{tid}")
        assert r2.status_code == 200
        r3 = requests.get(f"{BASE_URL}/projects/{pid}/tasks", headers=JSON_HEADERS)
        todos = r3.json().get("todos", [])
        assert not any(t["id"] == tid for t in todos)

    def test_link_project_to_todo_with_id_rejected(self, created_project, created_todo):
        """BUG/Undocumented: Cannot link to an existing todo by id."""
        pid = created_project["id"]
        tid = created_todo["id"]
        r = requests.post(
            f"{BASE_URL}/projects/{pid}/tasks",
            json={"id": tid},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 400


# ====================================================================
# GET /projects/:id/categories — Related Categories
# ====================================================================
class TestProjectCategories:
    """Tests for the project <-> category relationship."""

    def test_get_categories_returns_200(self, created_project):
        pid = created_project["id"]
        r = requests.get(
            f"{BASE_URL}/projects/{pid}/categories", headers=JSON_HEADERS
        )
        assert r.status_code == 200

    def test_get_categories_initially_empty(self, created_project):
        pid = created_project["id"]
        r = requests.get(
            f"{BASE_URL}/projects/{pid}/categories", headers=JSON_HEADERS
        )
        cats = r.json().get("categories", [])
        assert len(cats) == 0

    def test_link_project_to_category_creates_new_category(self, created_project):
        """POST /projects/:id/categories creates a NEW category linked to the project."""
        pid = created_project["id"]
        r = requests.post(
            f"{BASE_URL}/projects/{pid}/categories",
            json={"title": "Linked Cat"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 201
        new_cid = r.json()["id"]
        r2 = requests.get(
            f"{BASE_URL}/projects/{pid}/categories", headers=JSON_HEADERS
        )
        cats = r2.json().get("categories", [])
        assert any(c["id"] == new_cid for c in cats)

    def test_unlink_project_from_category(self, created_project):
        pid = created_project["id"]
        r = requests.post(
            f"{BASE_URL}/projects/{pid}/categories",
            json={"title": "To Unlink Cat"},
            headers=JSON_HEADERS,
        )
        cid = r.json()["id"]
        r2 = requests.delete(f"{BASE_URL}/projects/{pid}/categories/{cid}")
        assert r2.status_code == 200
        r3 = requests.get(
            f"{BASE_URL}/projects/{pid}/categories", headers=JSON_HEADERS
        )
        cats = r3.json().get("categories", [])
        assert not any(c["id"] == cid for c in cats)

    def test_link_project_to_category_with_id_rejected(self, created_project, created_category):
        """BUG/Undocumented: Cannot link to an existing category by id."""
        pid = created_project["id"]
        cid = created_category["id"]
        r = requests.post(
            f"{BASE_URL}/projects/{pid}/categories",
            json={"id": cid},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 400


# ====================================================================
# HEAD and OPTIONS
# ====================================================================
class TestProjectHeadAndOptions:
    """Tests for HEAD and OPTIONS on /projects endpoints."""

    def test_head_projects(self):
        r = requests.head(f"{BASE_URL}/projects")
        assert r.status_code in (200, 405)

    def test_options_projects(self):
        r = requests.options(f"{BASE_URL}/projects")
        assert r.status_code == 200

    def test_head_project_by_id(self, created_project):
        r = requests.head(f"{BASE_URL}/projects/{created_project['id']}")
        assert r.status_code in (200, 405)
