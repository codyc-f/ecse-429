"""
Step definitions for Story 10: Delete a Category Given an ID
"""
from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"


@when('a user deletes the category by its ID')
def step_delete_category_by_id(context):
    """Delete category by stored ID."""
    context.response = requests.delete(f"{BASE_URL}/categories/{context.category_id}")
    if context.category_id in context.created_categories:
        context.created_categories.remove(context.category_id)


@then('the category is successfully removed')
def step_category_deleted(context):
    """Verify category was deleted."""
    assert context.response.status_code == 200, \
        f"Expected 200, got {context.response.status_code}"


@then('the category no longer exists in the system')
def step_category_not_exists(context):
    """Verify category no longer exists."""
    response = requests.get(f"{BASE_URL}/categories/{context.category_id}")
    assert response.status_code == 404, \
        f"Expected 404, got {response.status_code}"


@when('a user deletes the category with ID {categoryId}')
def step_delete_category_by_specific_id(context, categoryId):
    """Delete category by specific ID."""
    categoryId = categoryId.strip('"')
    context.response = requests.delete(f"{BASE_URL}/categories/{categoryId}")


@when('a user deletes a category with invalid ID format {invalidId}')
def step_delete_category_invalid_id(context, invalidId):
    """Attempt to delete category with invalid ID."""
    invalidId = invalidId.strip('"')
    context.response = requests.delete(f"{BASE_URL}/categories/{invalidId}")
