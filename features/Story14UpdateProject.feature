Feature: Update a Project Given an ID

    As a user, I want to update a specific project.

    Background: Server is running and projects exist
        Given the server is running
        And the following projects exist
            | title            | completed | active | description        |
            | "School Project" | false     | true   | "Group assignment" |

    Scenario Outline: Update a project with valid fields (Normal Flow)
        Given a project with title "School Project" exists
        When a user updates the project with title <newTitle>, completed <newCompleted>, active <newActive>, and description <newDescription>
        Then the project is updated successfully
        And the response contains the updated project with title <newTitle>

    Examples:
        | newTitle         | newCompleted | newActive | newDescription      |
        | "Final Project"  | true         | false     | "Completed project" |
        | "Team Project"   | false        | true      | "Updated assignment"|

    Scenario Outline: Update a project with partial fields (Alternate Flow)
        Given a project with title "School Project" exists
        When a user updates the project with only <field> set to <value>
        Then the project is updated successfully
        And only the <field> field is modified to <value>

    Examples:
        | field       | value              |
        | title       | "Updated Project"  |
        | completed   | true               |
        | active      | false              |
        | description | "New description"  |

    Scenario Outline: Update a project with an invalid ID (Error Flow)
        When a user updates a project with invalid ID <invalidId>
        Then the user receives an error
        And the error message indicates <errorMessage>

    Examples:
        | invalidId | errorMessage                             |
        | "999999"  | "Invalid GUID for 999999 entity project" |
        | "abc"     | "Invalid GUID for abc entity project"    |
        | "-1"      | "Invalid GUID for -1 entity project"     |
