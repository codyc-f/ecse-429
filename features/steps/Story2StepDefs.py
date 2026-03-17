"""
Step definitions for Story 2: Get a Todo Given an ID
"""
from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"


@given('the following todos exist')
def step_todos_exist(context):
    """Create todos from table."""
    if not hasattr(context, 'todos_by_status'):
        context.todos_by_status = {'true': [], 'false': []}
    for row in context.table:
        title = row['title'].strip('"')
        doneStatus = row['doneStatus'].lower() == 'true'
        description = row['description'].strip('"')
        
        payload = {
            "title": title,
            "doneStatus": doneStatus,
            "description": description
        }
        response = requests.post(f"{BASE_URL}/todos", json=payload)
        if response.status_code == 201:
            todo_id = response.json()['id']
            context.created_todos.append(todo_id)
            status_key = 'true' if doneStatus else 'false'
            context.todos_by_status[status_key].append(todo_id)


@given('a todo with title {title} exists')
def step_todo_with_title_exists(context, title):
    """Create a todo with given title and store its ID."""
    title = title.strip('"')
    payload = {"title": title, "doneStatus": False, "description": "Test description"}
    response = requests.post(f"{BASE_URL}/todos", json=payload)
    assert response.status_code == 201, f"Failed to create todo: {response.text}"
    context.todo_id = response.json()['id']
    context.created_todos.append(context.todo_id)


@when('a user requests the todo with its ID')
def step_request_todo_by_id(context):
    """Request todo by stored ID."""
    context.response = requests.get(f"{BASE_URL}/todos/{context.todo_id}")


@then('the user receives the todo with title {title}')
def step_receives_todo_with_title(context, title):
    """Verify received todo has expected title."""
    title = title.strip('"')
    response_data = context.response.json()
    todos = response_data.get('todos', [response_data])
    if isinstance(todos, list) and len(todos) > 0:
        assert todos[0].get('title') == title, f"Expected title '{title}', got '{todos[0].get('title')}'"
    else:
        assert response_data.get('title') == title


@then('the response status code is {status_code}')
def step_response_status_code(context, status_code):
    """Verify response status code."""
    expected = int(status_code)
    assert context.response.status_code == expected, \
        f"Expected status {expected}, got {context.response.status_code}"


@given('no todo exists with ID {nonExistentId}')
def step_no_todo_with_id(context, nonExistentId):
    """Ensure no todo exists with given ID."""
    nonExistentId = nonExistentId.strip('"')
    # Try to delete if exists (ignore errors)
    requests.delete(f"{BASE_URL}/todos/{nonExistentId}")
    context.non_existent_id = nonExistentId


@when('a user requests the todo with ID {todoId}')
def step_request_todo_by_specific_id(context, todoId):
    """Request todo by specific ID."""
    todoId = todoId.strip('"')
    context.response = requests.get(f"{BASE_URL}/todos/{todoId}")


@then('the user receives a 404 Not Found error')
def step_receives_404_error(context):
    """Verify 404 response."""
    assert context.response.status_code == 404, \
        f"Expected 404, got {context.response.status_code}"


@when('a user requests the todo with invalid ID {invalidId}')
def step_request_todo_invalid_id(context, invalidId):
    """Request todo with invalid ID format."""
    invalidId = invalidId.strip('"')
    context.response = requests.get(f"{BASE_URL}/todos/{invalidId}")
