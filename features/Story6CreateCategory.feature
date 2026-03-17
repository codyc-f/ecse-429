Feature: Create a Category

    As a user, I want to create a category to organize my todos.

    Background: Server is running
        Given the server is running

    Scenario Outline: Create a category with valid fields (Normal Flow)
        When a user creates a category with title <title> and description <description>
        Then the category is created successfully
        And the response contains the category with title <title>
        And the response status code is 201

    Examples:
        | title        | description          |
        | "Work"       | "Work related tasks" |
        | "Personal"   | "Personal tasks"     |
        | "Urgent"     | ""                   |

    Scenario Outline: Create a category without an ID and system auto-generates one (Alternate Flow)
        When a user creates a category without specifying an ID with title <title>
        Then the category is created successfully
        And the system auto-generates a unique ID for the category

    Examples:
        | title          |
        | "High Priority"|
        | "Low Priority" |
        | "Medium"       |

    Scenario Outline: Create a category with an invalid body (Error Flow)
        When a user creates a category with an invalid body <invalidBody>
        Then the user receives an error
        And the error message indicates <errorMessage>

    Examples:
        | invalidBody          | errorMessage             |
        | "{ invalid json }"   | "Invalid request body"   |
        | ""                   | "Invalid request body"   |
