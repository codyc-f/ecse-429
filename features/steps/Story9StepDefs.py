"""
Step definitions for Story 9: Update a Category Given an ID
"""
from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"


@when('a user updates the category with title {newTitle} and description {newDescription}')
def step_update_category_full(context, newTitle, newDescription):
    """Update category with all fields."""
    newTitle = newTitle.strip('"')
    newDescription = newDescription.strip('"')
    
    payload = {
        "title": newTitle,
        "description": newDescription
    }
    context.response = requests.put(f"{BASE_URL}/categories/{context.category_id}", json=payload)


@then('the category is updated successfully')
def step_category_updated(context):
    """Verify category was updated."""
    assert context.response.status_code == 200, \
        f"Expected 200, got {context.response.status_code}: {context.response.text}"


@then('the response contains the updated category with title {newTitle}')
def step_response_contains_updated_category_title(context, newTitle):
    """Verify updated title in response."""
    newTitle = newTitle.strip('"')
    response_data = context.response.json()
    assert response_data.get('title') == newTitle, \
        f"Expected title '{newTitle}', got '{response_data.get('title')}'"


@when('a user updates the category with only {field} set to {value}')
def step_update_category_partial(context, field, value):
    """Update category with single field.
    Note: API requires 'title' to be present in PUT requests.
    Fetch the current category first to include the mandatory title.
    """
    field = field.strip('"')
    value = value.strip('"')

    # Fetch current category to get the mandatory title field
    current_resp = requests.get(f"{BASE_URL}/categories/{context.category_id}")
    current_data = current_resp.json()
    cats = current_data.get('categories', [current_data])
    current_title = cats[0].get('title', '') if isinstance(cats, list) and cats else current_data.get('title', '')
    payload = {"title": current_title}
    payload[field] = value
    context.response = requests.put(f"{BASE_URL}/categories/{context.category_id}", json=payload)


@when('a user updates a category with invalid ID {invalidId}')
def step_update_category_invalid_id(context, invalidId):
    """Attempt to update category with invalid ID."""
    invalidId = invalidId.strip('"')
    payload = {"title": "Test Update"}
    context.response = requests.put(f"{BASE_URL}/categories/{invalidId}", json=payload)
