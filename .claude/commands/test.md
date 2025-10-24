# /test - Run Comprehensive Test Suites

Use this command to run tests systematically, ensuring code quality and functionality.

## Usage
```
/test [optional: specific test type or file]
```

## Test Types

### Unit Tests
```
/test unit
```
- Tests individual functions and classes in isolation
- Fast execution, high coverage
- Mocks external dependencies

### Integration Tests
```
/test integration
```
- Tests component interactions
- Database and API integration
- End-to-end workflows

### All Tests
```
/test
```
- Runs the complete test suite
- Includes unit, integration, and any other test categories
- Generates coverage reports

### Specific File
```
/test src/auth/test_authentication.py
```
- Runs tests for a specific module or file
- Useful for focused development

## What it does
- Executes tests using pytest with proper configuration
- Generates coverage reports
- Identifies failing tests with clear error messages
- Suggests fixes for common test failures
- Validates test quality and completeness

## Test Standards
- **Naming**: Tests clearly describe what they're testing
- **Independence**: Tests don't depend on each other
- **Speed**: Unit tests run quickly (< 1ms each)
- **Coverage**: Aim for 90%+ code coverage
- **Clarity**: Test code is as readable as production code

## TDD Integration
When following TDD principles:
1. Write failing test first
2. Run test to confirm it fails
3. Write minimal code to pass
4. Run test to confirm it passes
5. Refactor while keeping test green

## Example
```
/test unit src/models/
```

This will run all unit tests in the models directory, providing detailed output on test results, coverage, and any failures that need attention.
