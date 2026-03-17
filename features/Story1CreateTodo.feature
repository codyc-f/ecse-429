Feature: Create a Todo

    As a user, I want to create a new todo to keep track of a task.

    Background: Server is running
        Given the server is running

    Scenario Outline: Create a todo with valid fields (Normal Flow)
        When a user creates a todo with title <title>, doneStatus <doneStatus>, and description <description>
        Then the todo is created successfully
        And the response contains the todo with title <title>

    Examples:
        | title              | doneStatus | description          |
        | "Buy groceries"    | false      | "Milk and bread"     |
        | "Complete homework"| true       | "Math assignment"    |
        | "Call mom"         | false      | ""                   |

    Scenario Outline: Create a todo without an ID and system auto-generates one (Alternate Flow)
        When a user creates a todo without specifying an ID with title <title>
        Then the todo is created successfully
        And the system auto-generates a unique ID for the todo

    Examples:
        | title               |
        | "Meeting at 3pm"    |
        | "Review documents"  |
        | "Send email"        |

    Scenario Outline: Create a todo with an invalid body (Error Flow)
        When a user creates a todo with an invalid body <invalidBody>
        Then the user receives an error
        And the error message indicates <errorMessage>

    Examples:
        | invalidBody                    | errorMessage                          |
        | "{ invalid json }"             | "Invalid request body"                |
        | "{ \"doneStatus\": \"wrong\" }"| "Failed Validation: doneStatus should be BOOLEAN" |
        | ""                             | "Invalid request body"                |
