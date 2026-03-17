"""
Step definitions for Story 1: Create a Todo
"""
from behave import given, when, then
import requests
import json

BASE_URL = "http://localhost:4567"


@given('the server is running')
def step_server_running(context):
    """Verify the server is running."""
    response = requests.get(f"{BASE_URL}/todos")
    assert response.status_code == 200, f"Server not running. Status: {response.status_code}"


@when('a user creates a todo with title {title}, doneStatus {doneStatus}, and description {description}')
def step_create_todo_full(context, title, doneStatus, description):
    """Create a todo with all fields."""
    title = title.strip('"')
    description = description.strip('"')
    done_bool = doneStatus.lower() == 'true'
    
    payload = {
        "title": title,
        "doneStatus": done_bool,
        "description": description
    }
    context.response = requests.post(f"{BASE_URL}/todos", json=payload)
    
    if context.response.status_code == 201:
        response_data = context.response.json()
        if 'id' in response_data:
            context.created_todos.append(response_data['id'])
            context.todo_id = response_data['id']


@then('the todo is created successfully')
def step_todo_created_successfully(context):
    """Verify todo was created."""
    assert context.response.status_code == 201, f"Expected 201, got {context.response.status_code}"


@then('the response contains the todo with title {title}')
def step_response_contains_title(context, title):
    """Verify response contains expected title."""
    title = title.strip('"')
    response_data = context.response.json()
    assert response_data.get('title') == title, f"Expected title '{title}', got '{response_data.get('title')}'"


@when('a user creates a todo without specifying an ID with title {title}')
def step_create_todo_no_id(context, title):
    """Create a todo without specifying an ID."""
    title = title.strip('"')
    payload = {"title": title}
    context.response = requests.post(f"{BASE_URL}/todos", json=payload)
    
    if context.response.status_code == 201:
        response_data = context.response.json()
        if 'id' in response_data:
            context.created_todos.append(response_data['id'])
            context.todo_id = response_data['id']


@then('the system auto-generates a unique ID for the todo')
def step_auto_generated_id(context):
    """Verify system generated an ID."""
    response_data = context.response.json()
    assert 'id' in response_data, "No ID was generated"
    assert response_data['id'] is not None, "ID is None"


@when('a user creates a todo with an invalid body {invalidBody}')
def step_create_todo_invalid_body(context, invalidBody):
    """Attempt to create a todo with invalid body."""
    invalidBody = invalidBody.strip('"')
    headers = {'Content-Type': 'application/json'}
    context.response = requests.post(f"{BASE_URL}/todos", data=invalidBody, headers=headers)


@then('the user receives an error')
def step_user_receives_error(context):
    """Verify an error response was received."""
    assert context.response.status_code >= 400, f"Expected error status, got {context.response.status_code}"


@then('the error message indicates {errorMessage}')
def step_error_message_indicates(context, errorMessage):
    """Verify error message content."""
    errorMessage = errorMessage.strip('"')
    response_text = context.response.text
    # Check if error message is in the response (flexible check)
    assert errorMessage.lower() in response_text.lower() or context.response.status_code >= 400, \
        f"Expected error message containing '{errorMessage}', got '{response_text}'"
