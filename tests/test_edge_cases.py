"""
Unit tests for edge cases and error handling.

Covers:
  - Malformed JSON payloads
  - Malformed XML payloads
  - Invalid operations (delete already deleted, update nonexistent, etc.)
  - Service availability check (tests fail if service is not running)
  - Invalid HTTP methods on endpoints
  - Boundary value testing
  - Undocumented endpoint behavior (PATCH, etc.)
"""
import pytest
import requests

BASE_URL = "http://localhost:4567"
JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
XML_HEADERS = {"Content-Type": "application/xml", "Accept": "application/xml"}


# ====================================================================
# Service Availability
# ====================================================================
class TestServiceAvailability:
    """Verify the service is reachable."""

    def test_service_responds(self):
        """The service should respond to a basic GET request."""
        r = requests.get(f"{BASE_URL}/todos", timeout=5)
        assert r.status_code == 200

    def test_service_returns_json_by_default(self):
        r = requests.get(f"{BASE_URL}/todos")
        # Should default to JSON
        assert "application/json" in r.headers.get("Content-Type", "")


# ====================================================================
# Malformed JSON Payloads
# ====================================================================
class TestMalformedJson:
    """Test API behavior when receiving malformed JSON."""

    def test_malformed_json_on_create_todo(self):
        """Sending invalid JSON should return 400."""
        malformed = '{"title": "broken", "doneStatus": }'
        r = requests.post(
            f"{BASE_URL}/todos",
            data=malformed,
            headers=JSON_HEADERS,
        )
        assert r.status_code == 400

    def test_malformed_json_on_create_project(self):
        malformed = '{"title": "broken",,,}'
        r = requests.post(
            f"{BASE_URL}/projects",
            data=malformed,
            headers=JSON_HEADERS,
        )
        assert r.status_code == 400

    def test_malformed_json_on_create_category(self):
        malformed = '{"title": }'
        r = requests.post(
            f"{BASE_URL}/categories",
            data=malformed,
            headers=JSON_HEADERS,
        )
        assert r.status_code == 400

    def test_malformed_json_on_update_todo(self, created_todo):
        tid = created_todo["id"]
        malformed = '{title: no quotes}'
        r = requests.post(
            f"{BASE_URL}/todos/{tid}",
            data=malformed,
            headers=JSON_HEADERS,
        )
        assert r.status_code == 400

    def test_empty_body_on_create_todo(self):
        """Sending an empty body should return 400 (title is mandatory)."""
        r = requests.post(
            f"{BASE_URL}/todos",
            data="",
            headers=JSON_HEADERS,
        )
        assert r.status_code == 400

    def test_array_body_on_create_todo(self):
        """Sending an array instead of an object."""
        r = requests.post(
            f"{BASE_URL}/todos",
            data='[{"title":"bad"}]',
            headers=JSON_HEADERS,
        )
        assert r.status_code == 400


# ====================================================================
# Malformed XML Payloads
# ====================================================================
class TestMalformedXml:
    """Test API behavior when receiving malformed XML."""

    def test_malformed_xml_on_create_todo(self):
        malformed_xml = "<todo><title>broken</title><unclosed>"
        r = requests.post(
            f"{BASE_URL}/todos",
            data=malformed_xml,
            headers=XML_HEADERS,
        )
        assert r.status_code == 400

    def test_malformed_xml_on_create_project(self):
        malformed_xml = "<project><title>broken<</title></project>"
        r = requests.post(
            f"{BASE_URL}/projects",
            data=malformed_xml,
            headers=XML_HEADERS,
        )
        assert r.status_code == 400

    def test_malformed_xml_on_create_category(self):
        malformed_xml = "<category><<<</category>"
        r = requests.post(
            f"{BASE_URL}/categories",
            data=malformed_xml,
            headers=XML_HEADERS,
        )
        assert r.status_code == 400

    def test_empty_xml_on_create_todo(self):
        r = requests.post(
            f"{BASE_URL}/todos",
            data="",
            headers=XML_HEADERS,
        )
        # Should fail because title is mandatory
        assert r.status_code == 400

    def test_wrong_root_element_xml(self):
        """XML with wrong root element name."""
        xml = "<wrongroot><title>test</title></wrongroot>"
        r = requests.post(
            f"{BASE_URL}/todos",
            data=xml,
            headers=XML_HEADERS,
        )
        # May succeed or fail depending on API flexibility
        assert r.status_code in (201, 400)


# ====================================================================
# Invalid Operations
# ====================================================================
class TestInvalidOperations:
    """Test invalid operations that should fail gracefully."""

    def test_delete_already_deleted_todo(self):
        """Delete a todo, then delete it again."""
        todo = requests.post(
            f"{BASE_URL}/todos",
            json={"title": "Temp"},
            headers=JSON_HEADERS,
        ).json()
        requests.delete(f"{BASE_URL}/todos/{todo['id']}")
        r = requests.delete(f"{BASE_URL}/todos/{todo['id']}")
        assert r.status_code == 404

    def test_delete_already_deleted_project(self):
        proj = requests.post(
            f"{BASE_URL}/projects",
            json={"title": "Temp"},
            headers=JSON_HEADERS,
        ).json()
        requests.delete(f"{BASE_URL}/projects/{proj['id']}")
        r = requests.delete(f"{BASE_URL}/projects/{proj['id']}")
        assert r.status_code == 404

    def test_delete_already_deleted_category(self):
        cat = requests.post(
            f"{BASE_URL}/categories",
            json={"title": "Temp"},
            headers=JSON_HEADERS,
        ).json()
        requests.delete(f"{BASE_URL}/categories/{cat['id']}")
        r = requests.delete(f"{BASE_URL}/categories/{cat['id']}")
        assert r.status_code == 404

    def test_update_nonexistent_todo(self):
        r = requests.post(
            f"{BASE_URL}/todos/999999",
            json={"title": "Ghost"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 404

    def test_update_nonexistent_project(self):
        r = requests.post(
            f"{BASE_URL}/projects/999999",
            json={"title": "Ghost"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 404

    def test_update_nonexistent_category(self):
        r = requests.post(
            f"{BASE_URL}/categories/999999",
            json={"title": "Ghost"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 404

    def test_get_nonexistent_todo(self):
        r = requests.get(f"{BASE_URL}/todos/999999", headers=JSON_HEADERS)
        assert r.status_code == 404
        assert "errorMessages" in r.json()

    def test_get_nonexistent_project(self):
        r = requests.get(f"{BASE_URL}/projects/999999", headers=JSON_HEADERS)
        assert r.status_code == 404
        assert "errorMessages" in r.json()

    def test_get_nonexistent_category(self):
        r = requests.get(f"{BASE_URL}/categories/999999", headers=JSON_HEADERS)
        assert r.status_code == 404
        assert "errorMessages" in r.json()

    def test_link_with_id_to_project_rejected(self, created_project):
        """BUG: API rejects linking existing entities by id — returns 400."""
        pid = created_project["id"]
        r = requests.post(
            f"{BASE_URL}/projects/{pid}/tasks",
            json={"id": "999999"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 400

    def test_link_with_id_to_todo_rejected(self, created_todo):
        """BUG: API rejects linking existing entities by id — returns 400."""
        tid = created_todo["id"]
        r = requests.post(
            f"{BASE_URL}/todos/{tid}/task-of",
            json={"id": "999999"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 400

    def test_unlink_nonexistent_relationship(self, created_todo, created_project):
        """Delete a relationship that doesn't exist."""
        tid = created_todo["id"]
        pid = created_project["id"]
        r = requests.delete(f"{BASE_URL}/todos/{tid}/task-of/{pid}")
        assert r.status_code == 404

    def test_create_todo_with_id_in_body(self):
        """Attempt to specify an ID when creating — should error or ignore."""
        body = {"id": "999", "title": "With ID"}
        r = requests.post(f"{BASE_URL}/todos", json=body, headers=JSON_HEADERS)
        # API should reject specifying ID on creation
        assert r.status_code == 400 or (
            r.status_code == 201 and r.json()["id"] != "999"
        )

    def test_create_project_with_id_in_body(self):
        body = {"id": "999", "title": "With ID"}
        r = requests.post(f"{BASE_URL}/projects", json=body, headers=JSON_HEADERS)
        assert r.status_code == 400 or (
            r.status_code == 201 and r.json()["id"] != "999"
        )

    def test_create_category_with_id_in_body(self):
        body = {"id": "999", "title": "With ID"}
        r = requests.post(f"{BASE_URL}/categories", json=body, headers=JSON_HEADERS)
        assert r.status_code == 400 or (
            r.status_code == 201 and r.json()["id"] != "999"
        )


# ====================================================================
# Undocumented HTTP Methods
# ====================================================================
class TestUndocumentedMethods:
    """Test behavior of methods not explicitly documented."""

    def test_patch_todos_returns_405(self):
        """PATCH is not documented — should return 405 Method Not Allowed."""
        r = requests.patch(
            f"{BASE_URL}/todos",
            json={"title": "patch"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 405

    def test_patch_projects_returns_405(self):
        r = requests.patch(
            f"{BASE_URL}/projects",
            json={"title": "patch"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 405

    def test_patch_categories_returns_405(self):
        r = requests.patch(
            f"{BASE_URL}/categories",
            json={"title": "patch"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 405


# ====================================================================
# Boundary Values
# ====================================================================
class TestBoundaryValues:
    """Test boundary conditions and unusual input values."""

    def test_create_todo_very_long_title(self):
        """Create a todo with a very long title."""
        long_title = "A" * 5000
        body = {"title": long_title}
        r = requests.post(f"{BASE_URL}/todos", json=body, headers=JSON_HEADERS)
        # Should either accept or explicitly reject
        assert r.status_code in (201, 400)
        if r.status_code == 201:
            assert r.json()["title"] == long_title

    def test_create_todo_special_characters_title(self):
        """Title with special characters."""
        body = {"title": "Test <>&\"' \\n \\t !@#$%^&*()"}
        r = requests.post(f"{BASE_URL}/todos", json=body, headers=JSON_HEADERS)
        assert r.status_code == 201

    def test_create_todo_unicode_title(self):
        """Title with unicode characters."""
        body = {"title": "Tâche à faire — été 日本語 中文"}
        r = requests.post(f"{BASE_URL}/todos", json=body, headers=JSON_HEADERS)
        assert r.status_code == 201

    def test_create_project_empty_fields(self):
        """Create project with all fields as empty strings."""
        body = {"title": "", "description": ""}
        r = requests.post(f"{BASE_URL}/projects", json=body, headers=JSON_HEADERS)
        # Title might not be mandatory for projects
        assert r.status_code in (201, 400)

    def test_boolean_as_string_true_rejected(self, created_todo):
        """BUG: API returns doneStatus as string but rejects string input."""
        tid = created_todo["id"]
        r = requests.post(
            f"{BASE_URL}/todos/{tid}",
            json={"doneStatus": "true"},
            headers=JSON_HEADERS,
        )
        # The API returns booleans as strings in GET responses,
        # but rejects string booleans in POST/PUT requests
        assert r.status_code == 400

    def test_boolean_as_actual_boolean_accepted(self, created_todo):
        """API requires actual boolean values, not string booleans."""
        tid = created_todo["id"]
        r = requests.post(
            f"{BASE_URL}/todos/{tid}",
            json={"doneStatus": True},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["doneStatus"] == "true"

    def test_numeric_string_id(self):
        """Access with a non-numeric ID."""
        r = requests.get(f"{BASE_URL}/todos/abc", headers=JSON_HEADERS)
        assert r.status_code == 404

    def test_negative_id(self):
        r = requests.get(f"{BASE_URL}/todos/-1", headers=JSON_HEADERS)
        assert r.status_code == 404

    def test_zero_id(self):
        r = requests.get(f"{BASE_URL}/todos/0", headers=JSON_HEADERS)
        assert r.status_code == 404

    def test_float_id(self):
        r = requests.get(f"{BASE_URL}/todos/1.5", headers=JSON_HEADERS)
        assert r.status_code == 404

    def test_extra_unknown_fields_ignored_or_rejected(self):
        """Sending unknown fields in the body."""
        body = {"title": "Extra", "unknownField": "value", "anotherUnknown": 42}
        r = requests.post(f"{BASE_URL}/todos", json=body, headers=JSON_HEADERS)
        # API should either ignore extra fields or return 400
        assert r.status_code in (201, 400)


# ====================================================================
# Content-Type Negotiation
# ====================================================================
class TestContentNegotiation:
    """Test content type negotiation via Accept and Content-Type headers."""

    def test_accept_json_returns_json(self):
        r = requests.get(
            f"{BASE_URL}/todos",
            headers={"Accept": "application/json"},
        )
        assert "application/json" in r.headers.get("Content-Type", "")

    def test_accept_xml_returns_xml(self):
        r = requests.get(
            f"{BASE_URL}/todos",
            headers={"Accept": "application/xml"},
        )
        assert "application/xml" in r.headers.get("Content-Type", "")

    def test_accept_any_returns_json_by_default(self):
        r = requests.get(
            f"{BASE_URL}/todos",
            headers={"Accept": "*/*"},
        )
        ct = r.headers.get("Content-Type", "")
        assert "application/json" in ct or "application/xml" in ct

    def test_unsupported_accept_type(self):
        """Request an unsupported content type."""
        r = requests.get(
            f"{BASE_URL}/todos",
            headers={"Accept": "text/csv"},
        )
        # Should return 406 Not Acceptable or fallback to JSON
        assert r.status_code in (200, 406)

    def test_json_content_type_posts_json(self):
        body = {"title": "JSON Post"}
        r = requests.post(
            f"{BASE_URL}/todos",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 201

    def test_xml_content_type_posts_xml(self):
        xml = "<todo><title>XML Post</title></todo>"
        r = requests.post(
            f"{BASE_URL}/todos",
            data=xml,
            headers={"Content-Type": "application/xml"},
        )
        assert r.status_code == 201


# ====================================================================
# Return Code Validation
# ====================================================================
class TestReturnCodes:
    """Verify that correct HTTP status codes are returned for various operations."""

    def test_get_returns_200(self):
        assert requests.get(f"{BASE_URL}/todos").status_code == 200

    def test_post_create_returns_201(self):
        r = requests.post(
            f"{BASE_URL}/todos",
            json={"title": "RC Test"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 201

    def test_post_update_returns_200(self, created_todo):
        r = requests.post(
            f"{BASE_URL}/todos/{created_todo['id']}",
            json={"title": "RC Update"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 200

    def test_put_returns_200(self, created_todo):
        r = requests.put(
            f"{BASE_URL}/todos/{created_todo['id']}",
            json={"title": "RC Put"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 200

    def test_delete_returns_200(self, created_todo):
        r = requests.delete(f"{BASE_URL}/todos/{created_todo['id']}")
        assert r.status_code == 200

    def test_get_nonexistent_returns_404(self):
        assert requests.get(f"{BASE_URL}/todos/999999").status_code == 404

    def test_validation_error_returns_400(self):
        r = requests.post(
            f"{BASE_URL}/todos",
            json={"title": "test", "doneStatus": "notbool"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 400

    def test_options_returns_200(self):
        assert requests.options(f"{BASE_URL}/todos").status_code == 200

    def test_head_returns_200_or_405(self):
        r = requests.head(f"{BASE_URL}/todos")
        assert r.status_code in (200, 405)

    def test_link_create_returns_201(self, created_todo):
        r = requests.post(
            f"{BASE_URL}/todos/{created_todo['id']}/task-of",
            json={"title": "RC Proj"},
            headers=JSON_HEADERS,
        )
        assert r.status_code == 201
