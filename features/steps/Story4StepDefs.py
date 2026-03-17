"""
Step definitions for Story 4: Update a Todo Given an ID
"""
from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"


@when('a user updates the todo with title {newTitle}, doneStatus {newDoneStatus}, and description {newDescription}')
def step_update_todo_full(context, newTitle, newDoneStatus, newDescription):
    """Update todo with all fields."""
    newTitle = newTitle.strip('"')
    newDescription = newDescription.strip('"')
    done_bool = newDoneStatus.lower() == 'true'
    
    payload = {
        "title": newTitle,
        "doneStatus": done_bool,
        "description": newDescription
    }
    context.response = requests.put(f"{BASE_URL}/todos/{context.todo_id}", json=payload)


@then('the todo is updated successfully')
def step_todo_updated(context):
    """Verify todo was updated."""
    assert context.response.status_code == 200, \
        f"Expected 200, got {context.response.status_code}: {context.response.text}"


@then('the response contains the updated todo with title {newTitle}')
def step_response_contains_updated_title(context, newTitle):
    """Verify updated title in response."""
    newTitle = newTitle.strip('"')
    response_data = context.response.json()
    assert response_data.get('title') == newTitle, \
        f"Expected title '{newTitle}', got '{response_data.get('title')}'"


@when('a user updates the todo with only {field} set to {value}')
def step_update_todo_partial(context, field, value):
    """Update todo with single field.
    Note: API requires 'title' to be present in PUT requests.
    Fetch the current todo first to include the mandatory title.
    """
    field = field.strip('"')
    value = value.strip('"')

    if field == 'doneStatus':
        value = value.lower() == 'true'

    # Fetch current todo to get the mandatory title field
    current_data = requests.get(f"{BASE_URL}/todos/{context.todo_id}").json()
    todos = current_data.get('todos', [current_data])
    current_title = todos[0].get('title', '') if todos else ''
    payload = {"title": current_title}
    payload[field] = value
    context.response = requests.put(f"{BASE_URL}/todos/{context.todo_id}", json=payload)


@then('only the {field} field is modified to {value}')
def step_field_modified(context, field, value):
    """Verify specific field was modified."""
    field = field.strip('"')
    value = value.strip('"')
    response_data = context.response.json()
    
    if field == 'doneStatus':
        expected = value.lower() == 'true'
        actual = response_data.get(field)
        if isinstance(actual, str):
            actual = actual.lower() == 'true'
        assert actual == expected, f"Expected {field}={expected}, got {actual}"
    else:
        assert response_data.get(field) == value, \
            f"Expected {field}='{value}', got '{response_data.get(field)}'"


@when('a user updates a todo with invalid ID {invalidId}')
def step_update_todo_invalid_id(context, invalidId):
    """Attempt to update todo with invalid ID."""
    invalidId = invalidId.strip('"')
    payload = {"title": "Test Update"}
    context.response = requests.put(f"{BASE_URL}/todos/{invalidId}", json=payload)
