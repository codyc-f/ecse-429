Feature: Delete a Todo Given an ID

    As a user, I want to delete a specific todo to remove it.

    Background: Server is running
        Given the server is running

    Scenario Outline: Delete a todo successfully (Normal Flow)
        Given a todo with title <title> exists
        When a user deletes the todo by its ID
        Then the todo is successfully deleted
        And the response status code is 200
        And the todo no longer exists in the system

    Examples:
        | title             |
        | "Buy groceries"   |
        | "Complete project"|

    Scenario Outline: Delete a todo with a non-existing ID (Alternate Flow)
        Given no todo exists with ID <nonExistentId>
        When a user deletes the todo with ID <nonExistentId>
        Then the user receives a 404 Not Found error
        And the error message indicates <errorMessage>

    Examples:
        | nonExistentId | errorMessage                                   |
        | "999999"      | "Could not find any instances with todos/999999"|
        | "888888"      | "Could not find any instances with todos/888888"|

    Scenario Outline: Delete a todo with an invalid ID format (Error Flow)
        When a user deletes a todo with invalid ID format <invalidId>
        Then the user receives an error
        And the error message indicates <errorMessage>

    Examples:
        | invalidId | errorMessage                                   |
        | "abc"     | "Could not find any instances with todos/abc"  |
        | "!@#"     | "Could not find any instances with todos/!@#"  |
