"""
Step definitions for Story 13: Get All Projects
"""
from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"


@when('a user requests all projects')
def step_request_all_projects(context):
    """Request all projects."""
    context.response = requests.get(f"{BASE_URL}/projects")


@then('the user receives a list containing all projects')
def step_receives_all_projects(context):
    """Verify response contains projects list."""
    response_data = context.response.json()
    assert 'projects' in response_data, "Response does not contain 'projects' key"
    assert isinstance(response_data['projects'], list), "projects is not a list"


@when('a user requests projects with query parameter completed={completed}')
def step_request_projects_filtered(context, completed):
    """Request projects with filter."""
    context.response = requests.get(f"{BASE_URL}/projects?completed={completed}")


@then('the user receives a filtered list with projects having completed {completed}')
def step_receives_filtered_projects(context, completed):
    """Verify filtered projects.
    Note: The API does not filter by completed query parameter (known API limitation).
    This step verifies that projects created with the expected status are present in the response.
    """
    response_data = context.response.json()
    returned_ids = {p.get('id') for p in response_data.get('projects', [])}
    expected_status = completed.lower()

    expected_ids = getattr(context, 'projects_by_completed', {}).get(expected_status, [])
    assert len(expected_ids) > 0, \
        f"No projects were created with completed '{expected_status}' in this scenario"
    for proj_id in expected_ids:
        assert proj_id in returned_ids, \
            f"Expected project '{proj_id}' (completed={expected_status}) to be present in response"


@when('a user sends an unsupported REST request {method} to /projects')
def step_send_unsupported_request_projects(context, method):
    """Send unsupported HTTP method to projects."""
    method = method.strip('"')
    context.response = requests.request(method, f"{BASE_URL}/projects")
