Feature: Remove a Todo from a Project

    As a user, I want to remove a todo from a project.

    Background: Server is running
        Given the server is running

    Scenario Outline: Remove a todo from a project (Normal Flow)
        Given a todo with title <todoTitle> exists
        And a project with title <projectTitle> exists
        And the todo is linked to the project
        When a user removes the link via DELETE /todos/:todoId/tasksof/:projectId
        Then the link is successfully removed
        And the todo is no longer associated with the project
        And the response status code is 200

    Examples:
        | todoTitle        | projectTitle     |
        | "Buy groceries"  | "School Project" |

    Scenario Outline: Delete a project and verify todo still exists but is unlinked (Alternate Flow)
        Given a todo with title <todoTitle> exists
        And a project with title <projectTitle> exists
        And the todo is linked to the project
        When a user deletes the project
        Then the project is successfully deleted
        And the todo with title <todoTitle> still exists
        And the todo is no longer linked to any project

    Examples:
        | todoTitle        | projectTitle     |
        | "Buy groceries"  | "School Project" |

    Scenario Outline: Remove a relationship that never existed (Error Flow)
        Given a todo with title <todoTitle> exists
        And a project with title <projectTitle> exists
        And the todo is NOT linked to the project
        When a user attempts to remove the link via DELETE /todos/:todoId/tasksof/:projectId
        Then the user receives an error
        And the error message indicates <errorMessage>

    Examples:
        | todoTitle        | projectTitle     | errorMessage                                                          |
        | "Buy groceries"  | "School Project" | "Could not find any instances with todos/:todoId/tasksof/:projectId" |
