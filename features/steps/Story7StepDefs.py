"""
Step definitions for Story 7: Get a Category Given an ID
"""
from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"


@given('the following categories exist')
def step_categories_exist(context):
    """Create categories from table."""
    if not hasattr(context, 'categories_by_title'):
        context.categories_by_title = {}
    for row in context.table:
        title = row['title'].strip('"')
        description = row['description'].strip('"')
        
        payload = {
            "title": title,
            "description": description
        }
        response = requests.post(f"{BASE_URL}/categories", json=payload)
        if response.status_code == 201:
            cat_id = response.json()['id']
            context.created_categories.append(cat_id)
            context.categories_by_title.setdefault(title, []).append(cat_id)


@given('a category with title {title} exists')
def step_category_with_title_exists(context, title):
    """Create a category with given title."""
    title = title.strip('"')
    payload = {"title": title, "description": "Test description"}
    response = requests.post(f"{BASE_URL}/categories", json=payload)
    assert response.status_code == 201, f"Failed to create category: {response.text}"
    context.category_id = response.json()['id']
    context.created_categories.append(context.category_id)


@when('a user requests the category with its ID')
def step_request_category_by_id(context):
    """Request category by stored ID."""
    context.response = requests.get(f"{BASE_URL}/categories/{context.category_id}")


@then('the user receives the category with title {title}')
def step_receives_category_with_title(context, title):
    """Verify received category has expected title."""
    title = title.strip('"')
    response_data = context.response.json()
    categories = response_data.get('categories', [response_data])
    if isinstance(categories, list) and len(categories) > 0:
        assert categories[0].get('title') == title, \
            f"Expected title '{title}', got '{categories[0].get('title')}'"
    else:
        assert response_data.get('title') == title


@given('no category exists with ID {nonExistentId}')
def step_no_category_with_id(context, nonExistentId):
    """Ensure no category exists with given ID."""
    nonExistentId = nonExistentId.strip('"')
    requests.delete(f"{BASE_URL}/categories/{nonExistentId}")
    context.non_existent_id = nonExistentId


@when('a user requests the category with ID {categoryId}')
def step_request_category_by_specific_id(context, categoryId):
    """Request category by specific ID."""
    categoryId = categoryId.strip('"')
    context.response = requests.get(f"{BASE_URL}/categories/{categoryId}")


@when('a user requests the category with invalid ID {invalidId}')
def step_request_category_invalid_id(context, invalidId):
    """Request category with invalid ID format."""
    invalidId = invalidId.strip('"')
    context.response = requests.get(f"{BASE_URL}/categories/{invalidId}")
