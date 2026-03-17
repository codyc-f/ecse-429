Feature: Get All Categories

    As a user, I want to get all categories so I can view them.

    Background: Server is running
        Given the server is running

    Scenario: Get all categories (Normal Flow)
        Given the following categories exist
            | title      | description          |
            | "Work"     | "Work related tasks" |
            | "Personal" | "Personal tasks"     |
            | "Urgent"   | "Urgent matters"     |
        When a user requests all categories
        Then the user receives a list containing all categories
        And the response status code is 200

    Scenario Outline: Get categories with a URL query parameter (Alternate Flow)
        Given the following categories exist
            | title      | description          |
            | "Work"     | "Work related tasks" |
            | "Personal" | "Personal tasks"     |
        When a user requests categories with query parameter title=<title>
        Then the user receives a filtered list with categories having title <title>

    Examples:
        | title      |
        | "Work"     |
        | "Personal" |

    Scenario Outline: Send unsupported REST request to categories (Error Flow)
        When a user sends an unsupported REST request <method> to /categories
        Then the user receives an error
        And the response status code is <statusCode>

    Examples:
        | method   | statusCode |
        | "PATCH"  | 405        |
