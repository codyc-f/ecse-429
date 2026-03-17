Feature: Retrieve All Todos for a Specific Category

    As a user, I want to filter todos by category.

    Background: Server is running
        Given the server is running

    Scenario Outline: Get all todos for a category (Normal Flow)
        Given a category with title <categoryTitle> exists
        And the following todos are linked to the category
            | title          | doneStatus | description     |
            | "Task 1"       | false      | "First task"    |
            | "Task 2"       | true       | "Second task"   |
        When a user requests GET /categories/:id/todos
        Then the user receives all linked todos
        And the response contains <expectedCount> todos
        And the response status code is 200

    Examples:
        | categoryTitle | expectedCount |
        | "Work"        | 2             |

    Scenario Outline: Get todos filtered by category using query parameter (Alternate Flow)
        Given a category with title <categoryTitle> exists and has ID <categoryId>
        And the following todos are linked to the category
            | title          | doneStatus | description     |
            | "Task 1"       | false      | "First task"    |
        When a user requests GET /todos with query parameter categories=<categoryId>
        Then the user receives filtered todos linked to the category
        And the response status code is 200

    Examples:
        | categoryTitle | categoryId |
        | "Work"        | "1"        |

    Scenario Outline: Get todos for a category with malformed or non-numeric ID (Error Flow)
        When a user requests GET /categories/<invalidId>/todos
        Then the user receives an error
        And the error message indicates <errorMessage>

    Examples:
        | invalidId | errorMessage                                        |
        | "abc"     | "Could not find an instance with categories/abc"    |
        | "!@#"     | "Could not find an instance with categories/!@#"    |
        | "999999"  | "Could not find an instance with categories/999999" |
