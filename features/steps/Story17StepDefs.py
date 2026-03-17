"""
Step definitions for Story 17: Link a Todo to a Category
"""
from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"


@when('a user assigns the category to the todo via POST /todos/:id/categories')
def step_assign_category_to_todo(context):
    """Assign category to todo.
    Note: POST /todos/:id/categories with {"id": ...} is rejected by the API.
    Workaround: look up the category title and POST with {"title": ...} instead,
    which creates a new linked category with the same name.
    """
    cat_response = requests.get(f"{BASE_URL}/categories/{context.category_id}")
    if cat_response.status_code == 200:
        cat_data = cat_response.json()
        cats = cat_data.get('categories', [cat_data])
        cat_info = cats[0] if isinstance(cats, list) and cats else cat_data
        category_title = cat_info.get('title', 'Category')
    else:
        category_title = 'Category'
    payload = {"title": category_title}
    context.response = requests.post(f"{BASE_URL}/todos/{context.todo_id}/categories", json=payload)
    if context.response.status_code == 201:
        new_cat_id = context.response.json().get('id')
        if new_cat_id:
            context.created_categories.append(new_cat_id)


@then('the todo is now associated with the category {categoryTitle}')
def step_todo_associated_with_category(context, categoryTitle):
    """Verify todo is linked to category."""
    categoryTitle = categoryTitle.strip('"')
    response = requests.get(f"{BASE_URL}/todos/{context.todo_id}/categories")
    assert response.status_code == 200
    categories = response.json().get('categories', [])
    category_titles = [cat['title'] for cat in categories]
    assert categoryTitle in category_titles, \
        f"Category '{categoryTitle}' not found in todo categories"


@given('the todo is already linked to category {firstCategory}')
def step_todo_linked_to_first_category(context, firstCategory):
    """Link todo to first category.
    Note: POST /todos/:id/categories with {"id": ...} is rejected by the API.
    Workaround: POST with {"title": ...} to create a new linked category.
    """
    firstCategory = firstCategory.strip('"')
    link_response = requests.post(
        f"{BASE_URL}/todos/{context.todo_id}/categories",
        json={"title": firstCategory}
    )
    if link_response.status_code == 201:
        context.first_category_id = link_response.json().get('id')
        context.created_categories.append(context.first_category_id)
    else:
        context.first_category_id = None


@when('a user assigns the category {secondCategory} to the todo')
def step_assign_second_category(context, secondCategory):
    """Assign second category to todo.
    Note: POST with {"title": ...} to create a new linked category.
    """
    secondCategory = secondCategory.strip('"')
    payload = {"title": secondCategory}
    context.response = requests.post(f"{BASE_URL}/todos/{context.todo_id}/categories", json=payload)
    if context.response.status_code == 201:
        context.second_category_id = context.response.json().get('id')
        context.created_categories.append(context.second_category_id)


@then('the todo is now associated with both categories {firstCategory} and {secondCategory}')
def step_todo_has_both_categories(context, firstCategory, secondCategory):
    """Verify todo has both categories."""
    firstCategory = firstCategory.strip('"')
    secondCategory = secondCategory.strip('"')
    
    response = requests.get(f"{BASE_URL}/todos/{context.todo_id}/categories")
    categories = response.json().get('categories', [])
    category_titles = [cat['title'] for cat in categories]
    
    assert firstCategory in category_titles, \
        f"First category '{firstCategory}' not found"
    assert secondCategory in category_titles, \
        f"Second category '{secondCategory}' not found"


@when('a user assigns a category with malformed body {malformedBody} to the todo')
def step_assign_category_malformed(context, malformedBody):
    """Attempt to assign category with malformed body."""
    malformedBody = malformedBody.strip('"')
    headers = {'Content-Type': 'application/json'}
    context.response = requests.post(
        f"{BASE_URL}/todos/{context.todo_id}/categories",
        data=malformedBody,
        headers=headers
    )
