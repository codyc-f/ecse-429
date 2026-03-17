"""
Step definitions for Story 11: Create a Project
"""
from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"


@when('a user creates a project with title {title}, completed {completed}, active {active}, and description {description}')
def step_create_project_full(context, title, completed, active, description):
    """Create a project with all fields."""
    title = title.strip('"')
    description = description.strip('"')
    completed_bool = completed.lower() == 'true'
    active_bool = active.lower() == 'true'
    
    payload = {
        "title": title,
        "completed": completed_bool,
        "active": active_bool,
        "description": description
    }
    context.response = requests.post(f"{BASE_URL}/projects", json=payload)
    
    if context.response.status_code == 201:
        response_data = context.response.json()
        if 'id' in response_data:
            context.created_projects.append(response_data['id'])
            context.project_id = response_data['id']


@then('the project is created successfully')
def step_project_created(context):
    """Verify project was created."""
    assert context.response.status_code == 201, \
        f"Expected 201, got {context.response.status_code}: {context.response.text}"


@then('the response contains the project with title {title}')
def step_response_contains_project_title(context, title):
    """Verify response contains expected project title."""
    title = title.strip('"')
    response_data = context.response.json()
    assert response_data.get('title') == title, \
        f"Expected title '{title}', got '{response_data.get('title')}'"


@when('a user creates a project without specifying an ID with title {title}')
def step_create_project_no_id(context, title):
    """Create a project without specifying ID."""
    title = title.strip('"')
    payload = {"title": title}
    context.response = requests.post(f"{BASE_URL}/projects", json=payload)
    
    if context.response.status_code == 201:
        response_data = context.response.json()
        if 'id' in response_data:
            context.created_projects.append(response_data['id'])
            context.project_id = response_data['id']


@then('the system auto-generates a unique ID for the project')
def step_project_auto_id(context):
    """Verify system generated an ID for project."""
    response_data = context.response.json()
    assert 'id' in response_data, "No ID was generated"
    assert response_data['id'] is not None, "ID is None"


@when('a user creates a project with an invalid body {invalidBody}')
def step_create_project_invalid_body(context, invalidBody):
    """Attempt to create project with invalid body."""
    invalidBody = invalidBody.strip('"')
    headers = {'Content-Type': 'application/json'}
    context.response = requests.post(f"{BASE_URL}/projects", data=invalidBody, headers=headers)
