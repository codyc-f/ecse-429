"""
Step definitions for Story 5: Delete a Todo Given an ID
"""
from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"


@when('a user deletes the todo by its ID')
def step_delete_todo_by_id(context):
    """Delete todo by stored ID."""
    context.response = requests.delete(f"{BASE_URL}/todos/{context.todo_id}")
    # Remove from cleanup list since we're deleting it
    if context.todo_id in context.created_todos:
        context.created_todos.remove(context.todo_id)


@then('the todo is successfully deleted')
def step_todo_deleted(context):
    """Verify todo was deleted."""
    assert context.response.status_code == 200, \
        f"Expected 200, got {context.response.status_code}"


@then('the todo no longer exists in the system')
def step_todo_not_exists(context):
    """Verify todo no longer exists."""
    response = requests.get(f"{BASE_URL}/todos/{context.todo_id}")
    assert response.status_code == 404, \
        f"Expected 404, got {response.status_code}"


@when('a user deletes the todo with ID {todoId}')
def step_delete_todo_by_specific_id(context, todoId):
    """Delete todo by specific ID."""
    todoId = todoId.strip('"')
    context.response = requests.delete(f"{BASE_URL}/todos/{todoId}")


@when('a user deletes a todo with invalid ID format {invalidId}')
def step_delete_todo_invalid_id(context, invalidId):
    """Attempt to delete todo with invalid ID."""
    invalidId = invalidId.strip('"')
    context.response = requests.delete(f"{BASE_URL}/todos/{invalidId}")
