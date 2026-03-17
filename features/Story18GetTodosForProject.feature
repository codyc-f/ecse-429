Feature: Retrieve All Todos for a Specific Project

    As a user, I want to view tasks belonging to a project.

    Background: Server is running
        Given the server is running

    Scenario Outline: Get all todos for a project (Normal Flow)
        Given a project with title <projectTitle> exists
        And the following todos are linked to the project
            | title          | doneStatus | description     |
            | "Task 1"       | false      | "First task"    |
            | "Task 2"       | true       | "Second task"   |
        When a user requests GET /projects/:id/tasks
        Then the user receives all associated todos
        And the response contains <expectedCount> todos
        And the response status code is 200

    Examples:
        | projectTitle     | expectedCount |
        | "School Project" | 2             |

    Scenario Outline: Get todos for a project with no tasks (Alternate Flow)
        Given a project with title <projectTitle> exists
        And the project has no linked todos
        When a user requests GET /projects/:id/tasks
        Then the user receives an empty list
        And the response status code is 200

    Examples:
        | projectTitle     |
        | "Empty Project"  |

    Scenario Outline: Get todos for a project with invalid ID (Error Flow)
        When a user requests GET /projects/<invalidId>/tasks
        Then the user receives a 404 Not Found error
        And the error message indicates <errorMessage>

    Examples:
        | invalidId | errorMessage                                     |
        | "999999"  | "Could not find an instance with projects/999999"|
        | "abc"     | "Could not find an instance with projects/abc"   |
