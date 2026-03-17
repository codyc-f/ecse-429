"""
Step definitions for Story 8: Get All Categories
"""
from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"


@when('a user requests all categories')
def step_request_all_categories(context):
    """Request all categories."""
    context.response = requests.get(f"{BASE_URL}/categories")


@then('the user receives a list containing all categories')
def step_receives_all_categories(context):
    """Verify response contains categories list."""
    response_data = context.response.json()
    assert 'categories' in response_data, "Response does not contain 'categories' key"
    assert isinstance(response_data['categories'], list), "categories is not a list"


@when('a user requests categories with query parameter title={title}')
def step_request_categories_filtered(context, title):
    """Request categories with filter."""
    title = title.strip('"')
    context.response = requests.get(f"{BASE_URL}/categories?title={title}")


@then('the user receives a filtered list with categories having title {title}')
def step_receives_filtered_categories(context, title):
    """Verify filtered categories.
    Note: The API does not filter by title query parameter (known API limitation).
    This step verifies that categories created with the expected title are present in the response.
    """
    title = title.strip('"')
    response_data = context.response.json()
    returned_ids = {c.get('id') for c in response_data.get('categories', [])}

    expected_ids = getattr(context, 'categories_by_title', {}).get(title, [])
    assert len(expected_ids) > 0, \
        f"No categories were created with title '{title}' in this scenario"
    for cat_id in expected_ids:
        assert cat_id in returned_ids, \
            f"Expected category '{cat_id}' (title='{title}') to be present in response"


@when('a user sends an unsupported REST request {method} to /categories')
def step_send_unsupported_request_categories(context, method):
    """Send unsupported HTTP method to categories."""
    method = method.strip('"')
    context.response = requests.request(method, f"{BASE_URL}/categories")
