Feature: Get a Project Given an ID

    As a user, I want to get a specific project to view details.

    Background: Server is running and projects exist
        Given the server is running
        And the following projects exist
            | title            | completed | active | description        |
            | "School Project" | false     | true   | "Group assignment" |
            | "Work Tasks"     | false     | true   | "Daily work tasks" |

    Scenario Outline: Get a project by valid ID (Normal Flow)
        Given a project with title <title> exists
        When a user requests the project with its ID
        Then the user receives the project with title <title>
        And the response status code is 200

    Examples:
        | title            |
        | "School Project" |
        | "Work Tasks"     |

    Scenario Outline: Get a project with a non-existing ID (Alternate Flow)
        Given no project exists with ID <nonExistentId>
        When a user requests the project with ID <nonExistentId>
        Then the user receives a 404 Not Found error
        And the error message indicates <errorMessage>

    Examples:
        | nonExistentId | errorMessage                                     |
        | "999999"      | "Could not find an instance with projects/999999"|
        | "888888"      | "Could not find an instance with projects/888888"|

    Scenario Outline: Get a project with an invalid ID format (Error Flow)
        When a user requests the project with invalid ID <invalidId>
        Then the user receives an error
        And the error message indicates <errorMessage>

    Examples:
        | invalidId | errorMessage                                   |
        | "abc"     | "Could not find an instance with projects/abc" |
        | "!@#"     | "Could not find an instance with projects/!@#" |
        | "-1"      | "Could not find an instance with projects/-1"  |
