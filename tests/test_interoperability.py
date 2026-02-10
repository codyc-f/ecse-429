"""
Unit tests for interoperability between todos, projects, and categories.

KEY FINDING: The relationship endpoints (e.g., POST /todos/:id/task-of) do NOT
link to existing entities by id. Instead, they CREATE a new related entity and
link it. This is undocumented behavior.

Covers cross-entity relationship scenarios:
  - Bidirectional linking (todo task-of project <==> project has task todo)
  - Bidirectional linking (todo <-> category, project <-> category)
  - Cascading behavior on delete (does deleting an entity remove relationships?)
  - Multiple relationships from one entity
  - Complex workflows involving all three entity types
"""
import pytest
import requests

BASE_URL = "http://localhost:4567"
JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


# ====================================================================
# Bidirectional Relationship Consistency
# ====================================================================
class TestBidirectionalTodoProject:
    """Verify that creating a project via todo's task-of endpoint is reflected
    when querying the project's tasks, and vice versa."""

    def test_link_via_todo_taskof_shows_in_project_tasks(self, created_todo):
        tid = created_todo["id"]
        # Create project via todo's task-of
        r = requests.post(
            f"{BASE_URL}/todos/{tid}/task-of",
            json={"title": "Bidir Proj"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 201
        pid = r.json()["id"]
        # Check project side: the todo should appear as a task
        r2 = requests.get(f"{BASE_URL}/projects/{pid}/tasks", headers=JSON_HEADERS)
        todos = r2.json().get("todos", [])
        assert any(t["id"] == tid for t in todos)

    def test_link_via_project_tasks_shows_in_todo_taskof(self, created_project):
        pid = created_project["id"]
        # Create todo via project's tasks
        r = requests.post(
            f"{BASE_URL}/projects/{pid}/tasks",
            json={"title": "Bidir Todo"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 201
        tid = r.json()["id"]
        # Check todo side: the project should appear as task-of
        r2 = requests.get(f"{BASE_URL}/todos/{tid}/task-of", headers=JSON_HEADERS)
        projects = r2.json().get("projects", [])
        assert any(p["id"] == pid for p in projects)

    def test_unlink_via_todo_removes_from_project_tasks(self, created_todo):
        tid = created_todo["id"]
        r = requests.post(
            f"{BASE_URL}/todos/{tid}/task-of",
            json={"title": "Unlink Test"},
            headers=JSON_HEADERS,
        )
        pid = r.json()["id"]
        requests.delete(f"{BASE_URL}/todos/{tid}/task-of/{pid}")
        r2 = requests.get(f"{BASE_URL}/projects/{pid}/tasks", headers=JSON_HEADERS)
        todos = r2.json().get("todos", [])
        assert not any(t["id"] == tid for t in todos)

    def test_unlink_via_project_removes_from_todo_taskof(self, created_project):
        pid = created_project["id"]
        r = requests.post(
            f"{BASE_URL}/projects/{pid}/tasks",
            json={"title": "Unlink Test"},
            headers=JSON_HEADERS,
        )
        tid = r.json()["id"]
        requests.delete(f"{BASE_URL}/projects/{pid}/tasks/{tid}")
        r2 = requests.get(f"{BASE_URL}/todos/{tid}/task-of", headers=JSON_HEADERS)
        projects = r2.json().get("projects", [])
        assert not any(p["id"] == pid for p in projects)


class TestBidirectionalTodoCategory:
    """Verify bidirectional consistency between todos and categories.

    BUG FOUND: Category relationships are NOT bidirectional.
    Creating a category via /todos/:id/categories does NOT make the todo
    appear in /categories/:id/todos (and vice versa).
    """

    def test_link_via_todo_not_bidirectional_bug(self, created_todo):
        """BUG: Creating a category via todo does NOT appear in category's todos."""
        tid = created_todo["id"]
        r = requests.post(
            f"{BASE_URL}/todos/{tid}/categories",
            json={"title": "Bidir Cat"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 201
        cid = r.json()["id"]
        # BUG: The todo does NOT appear in category's todos list
        r2 = requests.get(f"{BASE_URL}/categories/{cid}/todos", headers=JSON_HEADERS)
        todos = r2.json().get("todos", [])
        # This SHOULD be True, but the API does not establish bidirectional link
        assert not any(t["id"] == tid for t in todos), \
            "BUG: relationship is not bidirectional (todo->cat but not cat->todo)"

    def test_link_via_category_not_bidirectional_bug(self, created_category):
        """BUG: Creating a todo via category does NOT appear in todo's categories."""
        cid = created_category["id"]
        r = requests.post(
            f"{BASE_URL}/categories/{cid}/todos",
            json={"title": "Bidir Todo"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 201
        tid = r.json()["id"]
        # BUG: The category does NOT appear in todo's categories list
        r2 = requests.get(f"{BASE_URL}/todos/{tid}/categories", headers=JSON_HEADERS)
        cats = r2.json().get("categories", [])
        assert not any(c["id"] == cid for c in cats), \
            "BUG: relationship is not bidirectional (cat->todo but not todo->cat)"


class TestBidirectionalProjectCategory:
    """Verify bidirectional consistency between projects and categories.

    BUG FOUND: Same as todo-category — project-category relationships
    are NOT bidirectional.
    """

    def test_link_via_project_not_bidirectional_bug(self, created_project):
        """BUG: Creating a category via project does NOT appear in category's projects."""
        pid = created_project["id"]
        r = requests.post(
            f"{BASE_URL}/projects/{pid}/categories",
            json={"title": "Bidir Cat"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 201
        cid = r.json()["id"]
        r2 = requests.get(
            f"{BASE_URL}/categories/{cid}/projects", headers=JSON_HEADERS
        )
        projects = r2.json().get("projects", [])
        assert not any(p["id"] == pid for p in projects), \
            "BUG: relationship is not bidirectional (proj->cat but not cat->proj)"

    def test_link_via_category_not_bidirectional_bug(self, created_category):
        """BUG: Creating a project via category does NOT appear in project's categories."""
        cid = created_category["id"]
        r = requests.post(
            f"{BASE_URL}/categories/{cid}/projects",
            json={"title": "Bidir Proj"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 201
        pid = r.json()["id"]
        r2 = requests.get(
            f"{BASE_URL}/projects/{pid}/categories", headers=JSON_HEADERS
        )
        cats = r2.json().get("categories", [])
        assert not any(c["id"] == cid for c in cats), \
            "BUG: relationship is not bidirectional (cat->proj but not proj->cat)"


# ====================================================================
# Cascading Behavior on Delete
# ====================================================================
class TestCascadingDelete:
    """Test what happens to relationships when an entity is deleted."""

    def test_delete_project_removes_todo_taskof_link(self, created_todo):
        """After deleting a project, the todo's task-of should no longer list it."""
        tid = created_todo["id"]
        r = requests.post(
            f"{BASE_URL}/todos/{tid}/task-of",
            json={"title": "Cascade Proj"},
            headers=JSON_HEADERS,
        )
        pid = r.json()["id"]
        requests.delete(f"{BASE_URL}/projects/{pid}")
        r2 = requests.get(f"{BASE_URL}/todos/{tid}/task-of", headers=JSON_HEADERS)
        projects = r2.json().get("projects", [])
        assert not any(p["id"] == pid for p in projects)

    def test_delete_todo_removes_project_tasks_link(self, created_project):
        """After deleting a todo, the project's tasks should no longer list it."""
        pid = created_project["id"]
        r = requests.post(
            f"{BASE_URL}/projects/{pid}/tasks",
            json={"title": "Cascade Todo"},
            headers=JSON_HEADERS,
        )
        tid = r.json()["id"]
        requests.delete(f"{BASE_URL}/todos/{tid}")
        r2 = requests.get(f"{BASE_URL}/projects/{pid}/tasks", headers=JSON_HEADERS)
        todos = r2.json().get("todos", [])
        assert not any(t["id"] == tid for t in todos)

    def test_delete_category_dangling_ref_bug_in_todo(self, created_todo):
        """BUG: Deleting a category leaves a dangling reference in the todo's categories."""
        tid = created_todo["id"]
        r = requests.post(
            f"{BASE_URL}/todos/{tid}/categories",
            json={"title": "Cascade Cat"},
            headers=JSON_HEADERS,
        )
        cid = r.json()["id"]
        requests.delete(f"{BASE_URL}/categories/{cid}")
        r2 = requests.get(f"{BASE_URL}/todos/{tid}/categories", headers=JSON_HEADERS)
        cats = r2.json().get("categories", [])
        # BUG: The deleted category's id STILL appears (dangling reference)
        assert any(c["id"] == cid for c in cats), \
            "BUG: deleted category still referenced in todo's categories list"

    def test_delete_category_dangling_ref_bug_in_project(self, created_project):
        """BUG: Deleting a category leaves a dangling reference in the project's categories."""
        pid = created_project["id"]
        r = requests.post(
            f"{BASE_URL}/projects/{pid}/categories",
            json={"title": "Cascade Cat"},
            headers=JSON_HEADERS,
        )
        cid = r.json()["id"]
        requests.delete(f"{BASE_URL}/categories/{cid}")
        r2 = requests.get(
            f"{BASE_URL}/projects/{pid}/categories", headers=JSON_HEADERS
        )
        cats = r2.json().get("categories", [])
        # BUG: The deleted category's id STILL appears (dangling reference)
        assert any(c["id"] == cid for c in cats), \
            "BUG: deleted category still referenced in project's categories list"

    def test_delete_todo_does_not_delete_linked_project(self, created_todo):
        """Deleting a todo must not cascade-delete the linked project."""
        tid = created_todo["id"]
        r = requests.post(
            f"{BASE_URL}/todos/{tid}/task-of",
            json={"title": "Survive Proj"},
            headers=JSON_HEADERS,
        )
        pid = r.json()["id"]
        requests.delete(f"{BASE_URL}/todos/{tid}")
        r2 = requests.get(f"{BASE_URL}/projects/{pid}", headers=JSON_HEADERS)
        assert r2.status_code == 200

    def test_delete_project_does_not_delete_linked_todo(self, created_project):
        """Deleting a project must not cascade-delete the linked todo."""
        pid = created_project["id"]
        r = requests.post(
            f"{BASE_URL}/projects/{pid}/tasks",
            json={"title": "Survive Todo"},
            headers=JSON_HEADERS,
        )
        tid = r.json()["id"]
        requests.delete(f"{BASE_URL}/projects/{pid}")
        r2 = requests.get(f"{BASE_URL}/todos/{tid}", headers=JSON_HEADERS)
        assert r2.status_code == 200


# ====================================================================
# Multiple Relationships
# ====================================================================
class TestMultipleRelationships:
    """Test that entities can have multiple simultaneous relationships."""

    def test_todo_linked_to_multiple_projects(self, created_todo):
        tid = created_todo["id"]
        r1 = requests.post(
            f"{BASE_URL}/todos/{tid}/task-of",
            json={"title": "P1"},
            headers=JSON_HEADERS,
        )
        r2 = requests.post(
            f"{BASE_URL}/todos/{tid}/task-of",
            json={"title": "P2"},
            headers=JSON_HEADERS,
        )
        p1_id = r1.json()["id"]
        p2_id = r2.json()["id"]
        r3 = requests.get(f"{BASE_URL}/todos/{tid}/task-of", headers=JSON_HEADERS)
        projects = r3.json().get("projects", [])
        project_ids = {p["id"] for p in projects}
        assert p1_id in project_ids
        assert p2_id in project_ids

    def test_todo_linked_to_multiple_categories(self, created_todo):
        tid = created_todo["id"]
        r1 = requests.post(
            f"{BASE_URL}/todos/{tid}/categories",
            json={"title": "C1"},
            headers=JSON_HEADERS,
        )
        r2 = requests.post(
            f"{BASE_URL}/todos/{tid}/categories",
            json={"title": "C2"},
            headers=JSON_HEADERS,
        )
        c1_id = r1.json()["id"]
        c2_id = r2.json()["id"]
        r3 = requests.get(f"{BASE_URL}/todos/{tid}/categories", headers=JSON_HEADERS)
        cats = r3.json().get("categories", [])
        cat_ids = {c["id"] for c in cats}
        assert c1_id in cat_ids
        assert c2_id in cat_ids

    def test_project_with_multiple_tasks(self, created_project):
        pid = created_project["id"]
        r1 = requests.post(
            f"{BASE_URL}/projects/{pid}/tasks",
            json={"title": "T1"},
            headers=JSON_HEADERS,
        )
        r2 = requests.post(
            f"{BASE_URL}/projects/{pid}/tasks",
            json={"title": "T2"},
            headers=JSON_HEADERS,
        )
        t1_id = r1.json()["id"]
        t2_id = r2.json()["id"]
        r3 = requests.get(f"{BASE_URL}/projects/{pid}/tasks", headers=JSON_HEADERS)
        todos = r3.json().get("todos", [])
        todo_ids = {t["id"] for t in todos}
        assert t1_id in todo_ids
        assert t2_id in todo_ids


# ====================================================================
# Complex End-to-End Workflow
# ====================================================================
class TestComplexWorkflow:
    """Test a realistic end-to-end workflow involving all three entities."""

    def test_full_workflow_create_link_modify_unlink_delete(self):
        """
        1. Create a project.
        2. Add two todos to the project via tasks endpoint.
        3. Add a category to the project.
        4. Mark one todo as done.
        5. Unlink the done todo.
        6. Delete the done todo.
        7. Verify remaining state is correct.
        """
        # Step 1: Create a project
        proj = requests.post(
            f"{BASE_URL}/projects",
            json={"title": "Sprint 1", "active": True},
            headers=JSON_HEADERS,
        ).json()
        pid = proj["id"]

        # Step 2: Add two todos via tasks
        todo1 = requests.post(
            f"{BASE_URL}/projects/{pid}/tasks",
            json={"title": "Setup DB"},
            headers=JSON_HEADERS,
        ).json()
        todo2 = requests.post(
            f"{BASE_URL}/projects/{pid}/tasks",
            json={"title": "Write API"},
            headers=JSON_HEADERS,
        ).json()
        t1_id = todo1["id"]
        t2_id = todo2["id"]

        # Verify project has 2 tasks
        tasks = requests.get(
            f"{BASE_URL}/projects/{pid}/tasks", headers=JSON_HEADERS
        ).json().get("todos", [])
        assert len(tasks) == 2

        # Step 3: Add a category to the project
        cat = requests.post(
            f"{BASE_URL}/projects/{pid}/categories",
            json={"title": "Backend"},
            headers=JSON_HEADERS,
        ).json()
        cid = cat["id"]

        # Step 4: Mark todo1 as done
        requests.post(
            f"{BASE_URL}/todos/{t1_id}",
            json={"doneStatus": True},
            headers=JSON_HEADERS,
        )

        # Step 5: Unlink done todo from project
        requests.delete(f"{BASE_URL}/projects/{pid}/tasks/{t1_id}")

        # Step 6: Delete done todo
        requests.delete(f"{BASE_URL}/todos/{t1_id}")

        # Step 7: Verify remaining state
        tasks = requests.get(
            f"{BASE_URL}/projects/{pid}/tasks", headers=JSON_HEADERS
        ).json().get("todos", [])
        assert len(tasks) == 1
        assert tasks[0]["id"] == t2_id

        # Category still linked
        cats = requests.get(
            f"{BASE_URL}/projects/{pid}/categories", headers=JSON_HEADERS
        ).json().get("categories", [])
        assert any(c["id"] == cid for c in cats)

        # todo1 no longer exists
        r = requests.get(f"{BASE_URL}/todos/{t1_id}", headers=JSON_HEADERS)
        assert r.status_code == 404

    def test_all_three_entities_linked_together(self):
        """Create all three entities via relationship endpoints and verify links.
        Note: Due to the non-bidirectional category bug, only forward links are checked.
        """
        # Create a todo
        todo = requests.post(
            f"{BASE_URL}/todos",
            json={"title": "Linked Todo"},
            headers=JSON_HEADERS,
        ).json()
        tid = todo["id"]

        # Create project via todo's task-of (this IS bidirectional)
        proj = requests.post(
            f"{BASE_URL}/todos/{tid}/task-of",
            json={"title": "Linked Proj"},
            headers=JSON_HEADERS,
        ).json()
        pid = proj["id"]

        # Create category via todo's categories
        cat = requests.post(
            f"{BASE_URL}/todos/{tid}/categories",
            json={"title": "Linked Cat"},
            headers=JSON_HEADERS,
        ).json()
        cid = cat["id"]

        # Also link project to category
        proj_cat = requests.post(
            f"{BASE_URL}/projects/{pid}/categories",
            json={"title": "Proj Cat"},
            headers=JSON_HEADERS,
        ).json()
        pcid = proj_cat["id"]

        # Verify forward links (all should work)
        todo_projects = requests.get(
            f"{BASE_URL}/todos/{tid}/task-of", headers=JSON_HEADERS
        ).json().get("projects", [])
        assert any(p["id"] == pid for p in todo_projects)

        todo_cats = requests.get(
            f"{BASE_URL}/todos/{tid}/categories", headers=JSON_HEADERS
        ).json().get("categories", [])
        assert any(c["id"] == cid for c in todo_cats)

        proj_cats = requests.get(
            f"{BASE_URL}/projects/{pid}/categories", headers=JSON_HEADERS
        ).json().get("categories", [])
        assert any(c["id"] == pcid for c in proj_cats)

        # Verify bidirectional: project should see the todo (task-of IS bidirectional)
        proj_tasks = requests.get(
            f"{BASE_URL}/projects/{pid}/tasks", headers=JSON_HEADERS
        ).json().get("todos", [])
        assert any(t["id"] == tid for t in proj_tasks)
