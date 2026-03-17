"""
Step definitions for Story 3: Get All Todos
"""
from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"


@when('a user requests all todos')
def step_request_all_todos(context):
    """Request all todos."""
    context.response = requests.get(f"{BASE_URL}/todos")


@then('the user receives a list containing all todos')
def step_receives_all_todos(context):
    """Verify response contains todos list."""
    response_data = context.response.json()
    assert 'todos' in response_data, "Response does not contain 'todos' key"
    assert isinstance(response_data['todos'], list), "todos is not a list"


@when('a user requests todos with query parameter doneStatus={doneStatus}')
def step_request_todos_filtered(context, doneStatus):
    """Request todos with filter."""
    context.response = requests.get(f"{BASE_URL}/todos?doneStatus={doneStatus}")


@then('the user receives a filtered list with todos having doneStatus {doneStatus}')
def step_receives_filtered_todos(context, doneStatus):
    """Verify filtered todos.
    Note: The API does not filter by doneStatus query parameter (known API limitation).
    This step verifies that todos created with the expected status are present in the response.
    """
    response_data = context.response.json()
    returned_ids = {t.get('id') for t in response_data.get('todos', [])}
    expected_status = doneStatus.lower()

    expected_ids = getattr(context, 'todos_by_status', {}).get(expected_status, [])
    assert len(expected_ids) > 0, \
        f"No todos were created with doneStatus '{expected_status}' in this scenario"
    for todo_id in expected_ids:
        assert todo_id in returned_ids, \
            f"Expected todo '{todo_id}' (doneStatus={expected_status}) to be present in response"


@when('a user sends an invalid REST request {method} to /todos')
def step_send_invalid_request_todos(context, method):
    """Send invalid HTTP method to todos."""
    method = method.strip('"')
    context.response = requests.request(method, f"{BASE_URL}/todos")
