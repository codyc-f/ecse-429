Feature: Link a Todo to a Project

    As a user, I want to associate a todo with a project.

    Background: Server is running with todos and projects
        Given the server is running
        And the following todos exist
            | title          | doneStatus | description     |
            | "Buy groceries"| false      | "Milk and bread"|
        And the following projects exist
            | title            | completed | active | description        |
            | "School Project" | false     | true   | "Group assignment" |

    Scenario Outline: Link a todo to a project via todos endpoint (Normal Flow)
        Given a todo with title <todoTitle> exists
        And a project with title <projectTitle> exists
        When a user links the todo to the project via POST /todos/:id/tasksof
        Then the link is created successfully
        And the todo is now associated with the project
        And the response status code is 201

    Examples:
        | todoTitle        | projectTitle     |
        | "Buy groceries"  | "School Project" |

    Scenario Outline: Link a todo to a project via projects endpoint (Alternate Flow)
        Given a todo with title <todoTitle> exists
        And a project with title <projectTitle> exists
        When a user links the todo to the project via POST /projects/:id/tasks
        Then the link is created successfully
        And the todo is now associated with the project
        And the response status code is 201

    Examples:
        | todoTitle        | projectTitle     |
        | "Buy groceries"  | "School Project" |

    Scenario Outline: Link a todo to a non-existent project (Error Flow)
        Given a todo with title <todoTitle> exists
        And no project exists with ID <nonExistentProjectId>
        When a user links the todo to project with ID <nonExistentProjectId>
        Then the user receives an error
        And the error message indicates <errorMessage>

    Examples:
        | todoTitle        | nonExistentProjectId | errorMessage                                            |
        | "Buy groceries"  | "999999"             | "Not allowed to create with id"            |
