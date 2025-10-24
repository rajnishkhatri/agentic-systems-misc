# /work - Execute Tasks from GitHub Project Board

Use this command to work on tasks from the GitHub project board, following TDD principles and systematic implementation.

## Usage
```
/work [optional: specific issue number or "next"]
```

## What it does
- Fetches the next available task from the project board
- Moves the task to "In Progress" column
- Follows TDD approach: tests first, then implementation
- Uses parallel execution for independent operations
- Updates task status and creates PR when complete

## Workflow
1. **Analysis**: Understand the task requirements and acceptance criteria
2. **Planning**: Break down into smaller, testable units
3. **Testing**: Write tests first (unit, integration, e2e as needed)
4. **Implementation**: Write code to make tests pass
5. **Review**: Self-review code quality and test coverage
6. **Documentation**: Update relevant docs and comments
7. **Completion**: Move to "Done" and create PR

## TDD Principles
- **Red**: Write a failing test
- **Green**: Write minimal code to pass the test
- **Refactor**: Improve code while keeping tests green
- **Repeat**: Continue the cycle for each requirement

## Parallel Execution
When multiple independent tasks can be worked on simultaneously:
- Use Claude's Task tool to create parallel work streams
- Coordinate through clear interfaces and contracts
- Merge results systematically

## Quality Gates
- All tests must pass
- Code must be properly formatted (Ruff)
- Type hints required for all functions
- Documentation updated as needed
- No linting errors

## Example
```
/work next
```

This will pick up the next available task from the Todo column, move it to In Progress, and begin systematic implementation following TDD principles.
