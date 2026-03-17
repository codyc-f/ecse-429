Feature: Get All Projects

    As a user, I want to get all projects.

    Background: Server is running
        Given the server is running

    Scenario: Get all projects (Normal Flow)
        Given the following projects exist
            | title            | completed | active | description        |
            | "School Project" | false     | true   | "Group assignment" |
            | "Work Tasks"     | false     | true   | "Daily work tasks" |
            | "Home Project"   | true      | false  | "Completed project"|
        When a user requests all projects
        Then the user receives a list containing all projects
        And the response status code is 200

    Scenario Outline: Get projects with a query parameter (Alternate Flow)
        Given the following projects exist
            | title            | completed | active | description        |
            | "School Project" | false     | true   | "Group assignment" |
            | "Work Tasks"     | true      | false  | "Completed tasks"  |
        When a user requests projects with query parameter completed=<completed>
        Then the user receives a filtered list with projects having completed <completed>

    Examples:
        | completed |
        | true      |
        | false     |

    Scenario Outline: Send unsupported REST request to projects (Error Flow)
        When a user sends an unsupported REST request <method> to /projects
        Then the user receives an error
        And the response status code is <statusCode>

    Examples:
        | method   | statusCode |
        | "PATCH"  | 405        |
