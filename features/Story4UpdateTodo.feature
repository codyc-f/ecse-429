Feature: Update a Todo Given an ID

    As a user, I want to update the details of a specific todo.

    Background: Server is running and todos exist
        Given the server is running
        And the following todos exist
            | title          | doneStatus | description     |
            | "Buy groceries"| false      | "Milk and bread"|

    Scenario Outline: Update a todo with valid fields (Normal Flow)
        Given a todo with title "Buy groceries" exists
        When a user updates the todo with title <newTitle>, doneStatus <newDoneStatus>, and description <newDescription>
        Then the todo is updated successfully
        And the response contains the updated todo with title <newTitle>

    Examples:
        | newTitle         | newDoneStatus | newDescription    |
        | "Buy vegetables" | true          | "Carrots and peas"|
        | "Shopping"       | false         | "Weekly shopping" |

    Scenario Outline: Update a todo with only some fields (Alternate Flow)
        Given a todo with title "Buy groceries" exists
        When a user updates the todo with only <field> set to <value>
        Then the todo is updated successfully
        And only the <field> field is modified to <value>

    Examples:
        | field       | value            |
        | title       | "Updated title"  |
        | doneStatus  | true             |
        | description | "New description"|

    Scenario Outline: Update a todo with an invalid ID (Error Flow)
        When a user updates a todo with invalid ID <invalidId>
        Then the user receives an error
        And the error message indicates <errorMessage>

    Examples:
        | invalidId | errorMessage                                   |
        | "999999"  | "Invalid GUID for 999999 entity todo"          |
        | "abc"     | "Invalid GUID for abc entity todo"             |
        | "-1"      | "Invalid GUID for -1 entity todo"              |
