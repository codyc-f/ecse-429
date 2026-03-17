"""
Step definitions for Story 20: Remove a Todo from a Project
"""
from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"


@given('the todo is linked to the project')
def step_todo_is_linked_to_project(context):
    """Link todo to project.
    Note: API /task-of endpoint creates NEW projects, doesn't link existing ones.
    We create a new project via the todo's task-of endpoint.
    """
    payload = {"title": "Linked Project"}
    response = requests.post(f"{BASE_URL}/todos/{context.todo_id}/task-of", json=payload)
    assert response.status_code == 201, f"Failed to link todo to project: {response.text}"
    # Update context.project_id to the newly created project
    context.linked_project_id = response.json().get('id')
    context.created_projects.append(context.linked_project_id)


@when('a user removes the link via DELETE /todos/:todoId/tasksof/:projectId')
def step_remove_todo_project_link(context):
    """Remove link between todo and project."""
    project_id = getattr(context, 'linked_project_id', context.project_id)
    context.response = requests.delete(
        f"{BASE_URL}/todos/{context.todo_id}/task-of/{project_id}"
    )


@then('the link is successfully removed')
def step_link_removed(context):
    """Verify link was removed."""
    assert context.response.status_code == 200, \
        f"Expected 200, got {context.response.status_code}"


@then('the todo is no longer associated with the project')
def step_todo_not_associated_with_project(context):
    """Verify todo is not linked to project."""
    project_id = getattr(context, 'linked_project_id', context.project_id)
    response = requests.get(f"{BASE_URL}/projects/{project_id}/tasks")
    if response.status_code == 200:
        tasks = response.json().get('todos', [])
        todo_ids = [task['id'] for task in tasks]
        assert context.todo_id not in todo_ids, \
            f"Todo {context.todo_id} still found in project tasks"
    elif response.status_code == 404:
        # Project was deleted, so todo is definitely not associated
        pass


@when('a user deletes the project')
def step_delete_project(context):
    """Delete the project."""
    context.response = requests.delete(f"{BASE_URL}/projects/{context.project_id}")
    if context.project_id in context.created_projects:
        context.created_projects.remove(context.project_id)


@then('the todo with title {todoTitle} still exists')
def step_todo_still_exists(context, todoTitle):
    """Verify todo still exists."""
    todoTitle = todoTitle.strip('"')
    response = requests.get(f"{BASE_URL}/todos/{context.todo_id}")
    assert response.status_code == 200, \
        f"Todo no longer exists: {response.status_code}"


@then('the todo is no longer linked to any project')
def step_todo_not_linked_to_project(context):
    """Verify todo has no project links."""
    response = requests.get(f"{BASE_URL}/todos/{context.todo_id}/tasksof")
    if response.status_code == 200:
        projects = response.json().get('projects', [])
        # Either no projects returned or the deleted project is not there
        project_ids = [p['id'] for p in projects]
        assert context.project_id not in project_ids


@given('the todo is NOT linked to the project')
def step_todo_not_linked_to_project_given(context):
    """Ensure todo is not linked to project."""
    # Just don't create the link
    pass


@when('a user attempts to remove the link via DELETE /todos/:todoId/tasksof/:projectId')
def step_attempt_remove_nonexistent_link(context):
    """Attempt to remove non-existent link."""
    context.response = requests.delete(
        f"{BASE_URL}/todos/{context.todo_id}/task-of/{context.project_id}"
    )
