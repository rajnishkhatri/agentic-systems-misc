# /review - Code Review and Quality Checks

Use this command to perform thorough code reviews, focusing on quality, maintainability, and adherence to project standards.

## Usage
```
/review [optional: specific file, directory, or PR number]
```

## What it does
- Analyzes code for quality, readability, and maintainability
- Checks adherence to project coding standards
- Identifies potential bugs, performance issues, and security concerns
- Suggests improvements and refactoring opportunities
- Validates test coverage and documentation

## Review Criteria

### Code Quality
- **Clarity**: Is the code easy to understand?
- **Maintainability**: Can it be easily modified and extended?
- **Performance**: Are there any obvious performance issues?
- **Security**: Any potential security vulnerabilities?

### Standards Compliance
- **Formatting**: Follows Ruff configuration (120 char lines)
- **Type Hints**: All functions have proper type annotations
- **Naming**: Variables, functions, and classes follow conventions
- **Documentation**: Functions and classes are properly documented

### Testing
- **Coverage**: Are edge cases and error conditions tested?
- **Quality**: Tests are clear, focused, and maintainable
- **Integration**: Integration tests cover key user workflows

### Architecture
- **Separation of Concerns**: Logic is properly separated
- **Dependencies**: Dependencies are minimal and well-defined
- **Interfaces**: APIs are clean and consistent

## Output Format
- **Summary**: High-level assessment and key findings
- **Issues**: Specific problems that need attention
- **Suggestions**: Recommendations for improvement
- **Approval**: Clear yes/no recommendation with reasoning

## Example
```
/review src/api/auth.py
```

This will review the authentication module, checking for security best practices, proper error handling, test coverage, and adherence to project standards.
