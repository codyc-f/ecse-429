Feature: Delete a Project Given an ID

    As a user, I want to delete a specific project.

    Background: Server is running
        Given the server is running

    Scenario Outline: Delete a project successfully (Normal Flow)
        Given a project with title <title> exists
        When a user deletes the project by its ID
        Then the project is successfully deleted
        And the response status code is 200
        And the project no longer exists in the system

    Examples:
        | title            |
        | "School Project" |
        | "Work Tasks"     |

    Scenario Outline: Delete a project with a non-existing ID (Alternate Flow)
        Given no project exists with ID <nonExistentId>
        When a user deletes the project with ID <nonExistentId>
        Then the user receives a 404 Not Found error
        And the error message indicates <errorMessage>

    Examples:
        | nonExistentId | errorMessage                                      |
        | "999999"      | "Could not find any instances with projects/999999"|
        | "888888"      | "Could not find any instances with projects/888888"|

    Scenario Outline: Delete a project with an invalid ID (Error Flow)
        When a user deletes a project with invalid ID <invalidId>
        Then the user receives an error
        And the error message indicates <errorMessage>

    Examples:
        | invalidId | errorMessage                                      |
        | "abc"     | "Could not find any instances with projects/abc"  |
        | "!@#"     | "Could not find any instances with projects/!@#"  |
