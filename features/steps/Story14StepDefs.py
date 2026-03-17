"""
Step definitions for Story 14: Update a Project Given an ID
"""
from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"


@when('a user updates the project with title {newTitle}, completed {newCompleted}, active {newActive}, and description {newDescription}')
def step_update_project_full(context, newTitle, newCompleted, newActive, newDescription):
    """Update project with all fields."""
    newTitle = newTitle.strip('"')
    newDescription = newDescription.strip('"')
    completed_bool = newCompleted.lower() == 'true'
    active_bool = newActive.lower() == 'true'
    
    payload = {
        "title": newTitle,
        "completed": completed_bool,
        "active": active_bool,
        "description": newDescription
    }
    context.response = requests.put(f"{BASE_URL}/projects/{context.project_id}", json=payload)


@then('the project is updated successfully')
def step_project_updated(context):
    """Verify project was updated."""
    assert context.response.status_code == 200, \
        f"Expected 200, got {context.response.status_code}: {context.response.text}"


@then('the response contains the updated project with title {newTitle}')
def step_response_contains_updated_project_title(context, newTitle):
    """Verify updated title in response."""
    newTitle = newTitle.strip('"')
    response_data = context.response.json()
    assert response_data.get('title') == newTitle, \
        f"Expected title '{newTitle}', got '{response_data.get('title')}'"


@when('a user updates the project with only {field} set to {value}')
def step_update_project_partial(context, field, value):
    """Update project with single field."""
    field = field.strip('"')
    value = value.strip('"')
    
    if field in ['completed', 'active']:
        value = value.lower() == 'true'
    
    payload = {field: value}
    context.response = requests.put(f"{BASE_URL}/projects/{context.project_id}", json=payload)


@when('a user updates a project with invalid ID {invalidId}')
def step_update_project_invalid_id(context, invalidId):
    """Attempt to update project with invalid ID."""
    invalidId = invalidId.strip('"')
    payload = {"title": "Test Update"}
    context.response = requests.put(f"{BASE_URL}/projects/{invalidId}", json=payload)
