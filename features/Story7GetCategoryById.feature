Feature: Get a Category Given an ID

    As a user, I want to get a specific category to view it.

    Background: Server is running and categories exist
        Given the server is running
        And the following categories exist
            | title      | description          |
            | "Work"     | "Work related tasks" |
            | "Personal" | "Personal tasks"     |

    Scenario Outline: Get a category by valid ID (Normal Flow)
        Given a category with title <title> exists
        When a user requests the category with its ID
        Then the user receives the category with title <title>
        And the response status code is 200

    Examples:
        | title      |
        | "Work"     |
        | "Personal" |

    Scenario Outline: Get a category with a non-existing ID (Alternate Flow)
        Given no category exists with ID <nonExistentId>
        When a user requests the category with ID <nonExistentId>
        Then the user receives a 404 Not Found error
        And the error message indicates <errorMessage>

    Examples:
        | nonExistentId | errorMessage                                        |
        | "999999"      | "Could not find an instance with categories/999999" |
        | "888888"      | "Could not find an instance with categories/888888" |

    Scenario Outline: Get a category with an invalid ID format (Error Flow)
        When a user requests the category with invalid ID <invalidId>
        Then the user receives an error
        And the error message indicates <errorMessage>

    Examples:
        | invalidId | errorMessage                                      |
        | "abc"     | "Could not find an instance with categories/abc"  |
        | "!@#"     | "Could not find an instance with categories/!@#"  |
        | "-1"      | "Could not find an instance with categories/-1"   |
