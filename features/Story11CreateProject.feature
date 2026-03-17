Feature: Create a Project

    As a user, I want to create a project to organize my todos.

    Background: Server is running
        Given the server is running

    Scenario Outline: Create a project with valid fields (Normal Flow)
        When a user creates a project with title <title>, completed <completed>, active <active>, and description <description>
        Then the project is created successfully
        And the response contains the project with title <title>
        And the response status code is 201

    Examples:
        | title            | completed | active | description         |
        | "School Project" | false     | true   | "Group assignment"  |
        | "Work Tasks"     | false     | true   | "Daily work tasks"  |
        | "Home Renovation"| true      | false  | "Kitchen remodel"   |

    Scenario Outline: Create a project without an ID and system auto-generates one (Alternate Flow)
        When a user creates a project without specifying an ID with title <title>
        Then the project is created successfully
        And the system auto-generates a unique ID for the project

    Examples:
        | title               |
        | "New Initiative"    |
        | "Research Project"  |
        | "Personal Goals"    |

    Scenario Outline: Create a project with an invalid body (Error Flow)
        When a user creates a project with an invalid body <invalidBody>
        Then the user receives an error
        And the error message indicates <errorMessage>

    Examples:
        | invalidBody                   | errorMessage                                    |
        | "{ invalid json }"            | "Invalid request body"                          |
        | "{ \"completed\": \"wrong\" }"| "Failed Validation: completed should be BOOLEAN"|
        | "{ \"active\": \"wrong\" }"   | "Failed Validation: active should be BOOLEAN"  |
