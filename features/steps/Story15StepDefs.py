"""
Step definitions for Story 15: Delete a Project Given an ID
"""
from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"


@when('a user deletes the project by its ID')
def step_delete_project_by_id(context):
    """Delete project by stored ID."""
    context.response = requests.delete(f"{BASE_URL}/projects/{context.project_id}")
    if context.project_id in context.created_projects:
        context.created_projects.remove(context.project_id)


@then('the project is successfully deleted')
def step_project_deleted(context):
    """Verify project was deleted."""
    assert context.response.status_code == 200, \
        f"Expected 200, got {context.response.status_code}"


@then('the project no longer exists in the system')
def step_project_not_exists(context):
    """Verify project no longer exists."""
    response = requests.get(f"{BASE_URL}/projects/{context.project_id}")
    assert response.status_code == 404, \
        f"Expected 404, got {response.status_code}"


@when('a user deletes the project with ID {projectId}')
def step_delete_project_by_specific_id(context, projectId):
    """Delete project by specific ID."""
    projectId = projectId.strip('"')
    context.response = requests.delete(f"{BASE_URL}/projects/{projectId}")


@when('a user deletes a project with invalid ID {invalidId}')
def step_delete_project_invalid_id(context, invalidId):
    """Attempt to delete project with invalid ID."""
    invalidId = invalidId.strip('"')
    context.response = requests.delete(f"{BASE_URL}/projects/{invalidId}")
