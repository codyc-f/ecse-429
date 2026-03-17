Feature: Update a Category Given an ID

    As a user, I want to update a specific category.

    Background: Server is running and categories exist
        Given the server is running
        And the following categories exist
            | title  | description          |
            | "Work" | "Work related tasks" |

    Scenario Outline: Update a category with valid fields (Normal Flow)
        Given a category with title "Work" exists
        When a user updates the category with title <newTitle> and description <newDescription>
        Then the category is updated successfully
        And the response contains the updated category with title <newTitle>

    Examples:
        | newTitle    | newDescription       |
        | "Office"    | "Office tasks"       |
        | "Business"  | "Business matters"   |

    Scenario Outline: Update a category with partial fields (Alternate Flow)
        Given a category with title "Work" exists
        When a user updates the category with only <field> set to <value>
        Then the category is updated successfully
        And only the <field> field is modified to <value>

    Examples:
        | field       | value               |
        | title       | "Updated Category"  |
        | description | "New description"   |

    Scenario Outline: Update a category with an invalid ID (Error Flow)
        When a user updates a category with invalid ID <invalidId>
        Then the user receives an error
        And the error message indicates <errorMessage>

    Examples:
        | invalidId | errorMessage                             |
        | "999999"  | "Invalid GUID for 999999 entity category"|
        | "abc"     | "Invalid GUID for abc entity category"   |
        | "-1"      | "Invalid GUID for -1 entity category"    |
