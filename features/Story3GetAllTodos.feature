Feature: Get All Todos

    As a user, I want to read all my todos.

    Background: Server is running
        Given the server is running

    Scenario: Get all todos (Normal Flow)
        Given the following todos exist
            | title          | doneStatus | description     |
            | "Buy groceries"| false      | "Milk and bread"|
            | "Do homework"  | false      | "Math problems" |
            | "Call mom"     | true       | "Weekly call"   |
        When a user requests all todos
        Then the user receives a list containing all todos
        And the response status code is 200

    Scenario Outline: Get todos with a query parameter (Alternate Flow)
        Given the following todos exist
            | title          | doneStatus | description     |
            | "Buy groceries"| false      | "Milk and bread"|
            | "Do homework"  | true       | "Math problems" |
            | "Call mom"     | true       | "Weekly call"   |
        When a user requests todos with query parameter doneStatus=<doneStatus>
        Then the user receives a filtered list with todos having doneStatus <doneStatus>

    Examples:
        | doneStatus |
        | true       |
        | false      |

    Scenario Outline: Send an invalid REST request to todos (Error Flow)
        When a user sends an invalid REST request <method> to /todos
        Then the user receives an error
        And the response status code is <statusCode>

    Examples:
        | method   | statusCode |
        | "PATCH"  | 405        |
