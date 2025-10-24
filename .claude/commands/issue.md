# /issue - Create GitHub Issues with Templates

Use this command to create well-structured GitHub issues that integrate with the project's Kanban board workflow.

## Usage
```
/issue [issue type: epic|story|bug|infra] [brief description]
```

## Issue Types

### Epic
For large features that need to be broken down into smaller stories.
- Use when planning major functionality
- Should have clear business value and acceptance criteria
- Will be broken down into multiple stories

### Story
For specific user-facing features or improvements.
- Use for most development work
- Should be implementable in 1-3 days
- Needs clear acceptance criteria and test cases

### Bug
For fixing issues or unexpected behavior.
- Include steps to reproduce
- Describe expected vs actual behavior
- Provide relevant error messages or logs

### Infra
For infrastructure, tooling, or process improvements.
- DevOps tasks, CI/CD improvements
- Documentation updates
- Development environment setup

## What it does
- Creates issues using GitHub templates
- Automatically adds to project board (Todo column)
- Includes proper labels and milestones
- Ensures consistent issue structure across the team
- Links to relevant documentation and examples

## Example
```
/issue story "Add user authentication with JWT tokens"
```

This will create a story issue with proper template, add it to the project board, and include acceptance criteria for JWT authentication implementation.
