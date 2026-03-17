Feature: Get a Todo Given an ID

    As a user, I want to read a specific todo.

    Background: Server is running and todos exist
        Given the server is running
        And the following todos exist
            | title          | doneStatus | description     |
            | "Buy groceries"| false      | "Milk and bread"|
            | "Do homework"  | false      | "Math problems" |

    Scenario Outline: Get a todo by valid ID (Normal Flow)
        Given a todo with title <title> exists
        When a user requests the todo with its ID
        Then the user receives the todo with title <title>
        And the response status code is 200

    Examples:
        | title            |
        | "Buy groceries"  |
        | "Do homework"    |

    Scenario Outline: Get a todo with a valid but non-existent ID (Alternate Flow)
        Given no todo exists with ID <nonExistentId>
        When a user requests the todo with ID <nonExistentId>
        Then the user receives a 404 Not Found error
        And the error message indicates <errorMessage>

    Examples:
        | nonExistentId | errorMessage                              |
        | "999999"      | "Could not find an instance with todos/999999" |
        | "888888"      | "Could not find an instance with todos/888888" |

    Scenario Outline: Get a todo with an improperly formatted ID (Error Flow)
        When a user requests the todo with invalid ID <invalidId>
        Then the user receives an error
        And the error message indicates <errorMessage>

    Examples:
        | invalidId       | errorMessage                              |
        | "abc"           | "Could not find an instance with todos/abc"   |
        | "!@#"           | "Could not find an instance with todos/!@#"   |
        | "-1"            | "Could not find an instance with todos/-1"    |
