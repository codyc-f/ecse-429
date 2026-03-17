"""
Step definitions for Story 6: Create a Category
"""
from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"


@when('a user creates a category with title {title} and description {description}')
def step_create_category_full(context, title, description):
    """Create a category with title and description."""
    title = title.strip('"')
    description = description.strip('"')
    
    payload = {
        "title": title,
        "description": description
    }
    context.response = requests.post(f"{BASE_URL}/categories", json=payload)
    
    if context.response.status_code == 201:
        response_data = context.response.json()
        if 'id' in response_data:
            context.created_categories.append(response_data['id'])
            context.category_id = response_data['id']


@then('the category is created successfully')
def step_category_created(context):
    """Verify category was created."""
    assert context.response.status_code == 201, \
        f"Expected 201, got {context.response.status_code}: {context.response.text}"


@then('the response contains the category with title {title}')
def step_response_contains_category_title(context, title):
    """Verify response contains expected category title."""
    title = title.strip('"')
    response_data = context.response.json()
    assert response_data.get('title') == title, \
        f"Expected title '{title}', got '{response_data.get('title')}'"


@when('a user creates a category without specifying an ID with title {title}')
def step_create_category_no_id(context, title):
    """Create a category without specifying ID."""
    title = title.strip('"')
    payload = {"title": title}
    context.response = requests.post(f"{BASE_URL}/categories", json=payload)
    
    if context.response.status_code == 201:
        response_data = context.response.json()
        if 'id' in response_data:
            context.created_categories.append(response_data['id'])
            context.category_id = response_data['id']


@then('the system auto-generates a unique ID for the category')
def step_category_auto_id(context):
    """Verify system generated an ID for category."""
    response_data = context.response.json()
    assert 'id' in response_data, "No ID was generated"
    assert response_data['id'] is not None, "ID is None"


@when('a user creates a category with an invalid body {invalidBody}')
def step_create_category_invalid_body(context, invalidBody):
    """Attempt to create category with invalid body."""
    invalidBody = invalidBody.strip('"')
    headers = {'Content-Type': 'application/json'}
    context.response = requests.post(f"{BASE_URL}/categories", data=invalidBody, headers=headers)
