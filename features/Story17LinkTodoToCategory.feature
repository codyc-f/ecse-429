Feature: Link a Todo to a Category

    As a user, I want to assign a category to a todo.

    Background: Server is running with todos and categories
        Given the server is running
        And the following todos exist
            | title          | doneStatus | description     |
            | "Buy groceries"| false      | "Milk and bread"|
        And the following categories exist
            | title      | description          |
            | "Work"     | "Work related tasks" |
            | "Personal" | "Personal tasks"     |

    Scenario Outline: Assign a category to a todo (Normal Flow)
        Given a todo with title <todoTitle> exists
        And a category with title <categoryTitle> exists
        When a user assigns the category to the todo via POST /todos/:id/categories
        Then the link is created successfully
        And the todo is now associated with the category <categoryTitle>
        And the response status code is 201

    Examples:
        | todoTitle        | categoryTitle |
        | "Buy groceries"  | "Work"        |

    Scenario Outline: Assign a second category to a todo (Alternate Flow)
        Given a todo with title <todoTitle> exists
        And the todo is already linked to category <firstCategory>
        And a category with title <secondCategory> exists
        When a user assigns the category <secondCategory> to the todo
        Then the link is created successfully
        And the todo is now associated with both categories <firstCategory> and <secondCategory>

    Examples:
        | todoTitle        | firstCategory | secondCategory |
        | "Buy groceries"  | "Work"        | "Personal"     |

    Scenario Outline: Assign a category to a todo with malformed body (Error Flow)
        Given a todo with title <todoTitle> exists
        When a user assigns a category with malformed body <malformedBody> to the todo
        Then the user receives an error
        And the error message indicates <errorMessage>

    Examples:
        | todoTitle        | malformedBody        | errorMessage           |
        | "Buy groceries"  | "{ invalid json }"   | "Invalid request body" |
        | "Buy groceries"  | "{ \"id\": \"abc\" }"| "Could not find thing matching value for id" |
