"""
Step definitions for Story 12: Get a Project Given an ID
"""
from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"


@given('the following projects exist')
def step_projects_exist(context):
    """Create projects from table."""
    if not hasattr(context, 'projects_by_completed'):
        context.projects_by_completed = {'true': [], 'false': []}
    for row in context.table:
        title = row['title'].strip('"')
        completed = row['completed'].lower() == 'true'
        active = row['active'].lower() == 'true'
        description = row['description'].strip('"')
        
        payload = {
            "title": title,
            "completed": completed,
            "active": active,
            "description": description
        }
        response = requests.post(f"{BASE_URL}/projects", json=payload)
        if response.status_code == 201:
            proj_id = response.json()['id']
            context.created_projects.append(proj_id)
            status_key = 'true' if completed else 'false'
            context.projects_by_completed[status_key].append(proj_id)


@given('a project with title {title} exists')
def step_project_with_title_exists(context, title):
    """Create a project with given title."""
    title = title.strip('"')
    payload = {"title": title, "completed": False, "active": True, "description": "Test description"}
    response = requests.post(f"{BASE_URL}/projects", json=payload)
    assert response.status_code == 201, f"Failed to create project: {response.text}"
    context.project_id = response.json()['id']
    context.created_projects.append(context.project_id)


@when('a user requests the project with its ID')
def step_request_project_by_id(context):
    """Request project by stored ID."""
    context.response = requests.get(f"{BASE_URL}/projects/{context.project_id}")


@then('the user receives the project with title {title}')
def step_receives_project_with_title(context, title):
    """Verify received project has expected title."""
    title = title.strip('"')
    response_data = context.response.json()
    projects = response_data.get('projects', [response_data])
    if isinstance(projects, list) and len(projects) > 0:
        assert projects[0].get('title') == title, \
            f"Expected title '{title}', got '{projects[0].get('title')}'"
    else:
        assert response_data.get('title') == title


@given('no project exists with ID {nonExistentId}')
def step_no_project_with_id(context, nonExistentId):
    """Ensure no project exists with given ID."""
    nonExistentId = nonExistentId.strip('"')
    requests.delete(f"{BASE_URL}/projects/{nonExistentId}")
    context.non_existent_id = nonExistentId


@when('a user requests the project with ID {projectId}')
def step_request_project_by_specific_id(context, projectId):
    """Request project by specific ID."""
    projectId = projectId.strip('"')
    context.response = requests.get(f"{BASE_URL}/projects/{projectId}")


@when('a user requests the project with invalid ID {invalidId}')
def step_request_project_invalid_id(context, invalidId):
    """Request project with invalid ID format."""
    invalidId = invalidId.strip('"')
    context.response = requests.get(f"{BASE_URL}/projects/{invalidId}")
