"""
Shared fixtures and helpers for the REST API Todo List Manager test suite.

Ensures:
  - The system is ready to be tested (service is running).
  - System state is saved before each test.
  - System state is restored after each test.
  - Tests can run in any order.
"""
import json
import pytest
import requests

BASE_URL = "http://localhost:4567"


# ---------------------------------------------------------------------------
# Helper: check if the service is running
# ---------------------------------------------------------------------------
def is_service_running():
    """Return True if the API service responds to a GET /todos request."""
    try:
        r = requests.get(f"{BASE_URL}/todos", timeout=3)
        return r.status_code == 200
    except requests.ConnectionError:
        return False


# ---------------------------------------------------------------------------
# Session-scoped guard: fail fast if the service is not running
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def require_service():
    """Fail the entire test session immediately if the API is unreachable."""
    if not is_service_running():
        pytest.fail(
            "REST API service is not running at "
            f"{BASE_URL}. Start it before running tests."
        )


# ---------------------------------------------------------------------------
# Snapshot helpers
# ---------------------------------------------------------------------------
def _get_all_todos():
    r = requests.get(f"{BASE_URL}/todos")
    return r.json().get("todos", [])


def _get_all_projects():
    r = requests.get(f"{BASE_URL}/projects")
    return r.json().get("projects", [])


def _get_all_categories():
    r = requests.get(f"{BASE_URL}/categories")
    return r.json().get("categories", [])


def _get_todo_relationships(todo_id):
    """Return task-of and categories relationships for a todo."""
    taskof = requests.get(f"{BASE_URL}/todos/{todo_id}/task-of").json().get("projects", [])
    cats = requests.get(f"{BASE_URL}/todos/{todo_id}/categories").json().get("categories", [])
    return {"task-of": taskof, "categories": cats}


def _get_project_relationships(project_id):
    """Return tasks and categories relationships for a project."""
    tasks = requests.get(f"{BASE_URL}/projects/{project_id}/tasks").json().get("todos", [])
    cats = requests.get(f"{BASE_URL}/projects/{project_id}/categories").json().get("categories", [])
    return {"tasks": tasks, "categories": cats}


def _get_category_relationships(category_id):
    """Return todos and projects relationships for a category."""
    todos = requests.get(f"{BASE_URL}/categories/{category_id}/todos").json().get("todos", [])
    projects = requests.get(f"{BASE_URL}/categories/{category_id}/projects").json().get("projects", [])
    return {"todos": todos, "projects": projects}


def _take_snapshot():
    """Capture the full system state: all entities and their relationships."""
    todos = _get_all_todos()
    projects = _get_all_projects()
    categories = _get_all_categories()

    todo_rels = {}
    for t in todos:
        todo_rels[t["id"]] = _get_todo_relationships(t["id"])

    project_rels = {}
    for p in projects:
        project_rels[p["id"]] = _get_project_relationships(p["id"])

    category_rels = {}
    for c in categories:
        category_rels[c["id"]] = _get_category_relationships(c["id"])

    return {
        "todos": todos,
        "projects": projects,
        "categories": categories,
        "todo_rels": todo_rels,
        "project_rels": project_rels,
        "category_rels": category_rels,
    }


def _restore_snapshot(snapshot):
    """Restore the system to a previously captured state."""
    # --- Delete everything that currently exists ---
    for t in _get_all_todos():
        requests.delete(f"{BASE_URL}/todos/{t['id']}")
    for p in _get_all_projects():
        requests.delete(f"{BASE_URL}/projects/{p['id']}")
    for c in _get_all_categories():
        requests.delete(f"{BASE_URL}/categories/{c['id']}")

    # --- Helper to convert string booleans to actual booleans ---
    def _to_bool(val):
        """The API returns booleans as strings but requires actual booleans."""
        if isinstance(val, bool):
            return val
        return str(val).lower() == "true"

    # --- Recreate categories ---
    old_to_new_cat = {}
    for c in snapshot["categories"]:
        body = {"title": c["title"], "description": c.get("description", "")}
        r = requests.post(f"{BASE_URL}/categories", json=body)
        new_cat = r.json()
        old_to_new_cat[c["id"]] = new_cat["id"]

    # --- Recreate projects ---
    old_to_new_proj = {}
    for p in snapshot["projects"]:
        body = {
            "title": p.get("title", ""),
            "description": p.get("description", ""),
            "completed": _to_bool(p.get("completed", "false")),
            "active": _to_bool(p.get("active", "false")),
        }
        r = requests.post(f"{BASE_URL}/projects", json=body)
        new_proj = r.json()
        old_to_new_proj[p["id"]] = new_proj["id"]

    # --- Recreate todos ---
    old_to_new_todo = {}
    for t in snapshot["todos"]:
        body = {
            "title": t["title"],
            "doneStatus": _to_bool(t.get("doneStatus", "false")),
            "description": t.get("description", ""),
        }
        r = requests.post(f"{BASE_URL}/todos", json=body)
        new_todo = r.json()
        old_to_new_todo[t["id"]] = new_todo["id"]

    # --- Recreate relationships ---
    # Todo -> task-of (project)
    for old_todo_id, rels in snapshot.get("todo_rels", {}).items():
        new_todo_id = old_to_new_todo.get(old_todo_id)
        if not new_todo_id:
            continue
        for proj in rels.get("task-of", []):
            new_proj_id = old_to_new_proj.get(proj["id"])
            if new_proj_id:
                requests.post(
                    f"{BASE_URL}/todos/{new_todo_id}/task-of",
                    json={"id": new_proj_id},
                )
        for cat in rels.get("categories", []):
            new_cat_id = old_to_new_cat.get(cat["id"])
            if new_cat_id:
                requests.post(
                    f"{BASE_URL}/todos/{new_todo_id}/categories",
                    json={"id": new_cat_id},
                )

    # Project -> categories
    for old_proj_id, rels in snapshot.get("project_rels", {}).items():
        new_proj_id = old_to_new_proj.get(old_proj_id)
        if not new_proj_id:
            continue
        for cat in rels.get("categories", []):
            new_cat_id = old_to_new_cat.get(cat["id"])
            if new_cat_id:
                requests.post(
                    f"{BASE_URL}/projects/{new_proj_id}/categories",
                    json={"id": new_cat_id},
                )


# ---------------------------------------------------------------------------
# Per-test fixture: save and restore state around every test
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def save_and_restore_state():
    """Save system state before each test and restore it afterwards."""
    snapshot = _take_snapshot()
    yield
    _restore_snapshot(snapshot)


# ---------------------------------------------------------------------------
# Convenience fixtures for creating test data
# ---------------------------------------------------------------------------
@pytest.fixture
def created_todo():
    """Create a fresh todo and return its data dict."""
    body = {"title": "Test Todo", "doneStatus": False, "description": "A test todo"}
    r = requests.post(f"{BASE_URL}/todos", json=body)
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def created_project():
    """Create a fresh project and return its data dict."""
    body = {
        "title": "Test Project",
        "description": "A test project",
        "completed": False,
        "active": True,
    }
    r = requests.post(f"{BASE_URL}/projects", json=body)
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def created_category():
    """Create a fresh category and return its data dict."""
    body = {"title": "Test Category", "description": "A test category"}
    r = requests.post(f"{BASE_URL}/categories", json=body)
    assert r.status_code == 201
    return r.json()
