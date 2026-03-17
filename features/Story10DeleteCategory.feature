Feature: Delete a Category Given an ID

    As a user, I want to delete a specific category.

    Background: Server is running
        Given the server is running

    Scenario Outline: Delete a category successfully (Normal Flow)
        Given a category with title <title> exists
        When a user deletes the category by its ID
        Then the category is successfully removed
        And the response status code is 200
        And the category no longer exists in the system

    Examples:
        | title        |
        | "Work"       |
        | "Personal"   |

    Scenario Outline: Delete a category with a non-existing ID (Alternate Flow)
        Given no category exists with ID <nonExistentId>
        When a user deletes the category with ID <nonExistentId>
        Then the user receives a 404 Not Found error
        And the error message indicates <errorMessage>

    Examples:
        | nonExistentId | errorMessage                                        |
        | "999999"      | "Could not find any instances with categories/999999"|
        | "888888"      | "Could not find any instances with categories/888888"|

    Scenario Outline: Delete a category with an invalid ID format (Error Flow)
        When a user deletes a category with invalid ID format <invalidId>
        Then the user receives an error
        And the error message indicates <errorMessage>

    Examples:
        | invalidId | errorMessage                                        |
        | "abc"     | "Could not find any instances with categories/abc"  |
        | "!@#"     | "Could not find any instances with categories/!@#"  |
