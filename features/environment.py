"""
Behave environment configuration for API testing.
"""
import requests
import time

BASE_URL = "http://localhost:4567"

def before_all(context):
    """Setup before all tests."""
    context.base_url = BASE_URL
    context.created_todos = []
    context.created_categories = []
    context.created_projects = []

def before_scenario(context, scenario):
    """Reset context before each scenario."""
    context.response = None
    context.todo_id = None
    context.category_id = None
    context.project_id = None
    context.created_todos = []
    context.created_categories = []
    context.created_projects = []
    context.todos_by_status = {'true': [], 'false': []}
    context.categories_by_title = {}
    context.projects_by_completed = {'true': [], 'false': []}

def after_scenario(context, scenario):
    """Cleanup after each scenario - delete created resources."""
    # Delete created todos
    for todo_id in context.created_todos:
        try:
            requests.delete(f"{BASE_URL}/todos/{todo_id}")
        except:
            pass
    
    # Delete created categories
    for category_id in context.created_categories:
        try:
            requests.delete(f"{BASE_URL}/categories/{category_id}")
        except:
            pass
    
    # Delete created projects
    for project_id in context.created_projects:
        try:
            requests.delete(f"{BASE_URL}/projects/{project_id}")
        except:
            pass

def wait_for_server(url, timeout=30):
    """Wait for server to be available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.ConnectionError:
            pass
        time.sleep(0.5)
    return False
