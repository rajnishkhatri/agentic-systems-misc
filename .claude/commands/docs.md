# /docs - Generate and Update Documentation

Use this command to create, update, and maintain project documentation, ensuring it stays current with code changes.

## Usage
```
/docs [action: generate|update|review] [optional: specific component]
```

## Actions

### Generate
```
/docs generate [component]
```
- Creates new documentation for features or components
- Generates API documentation from code
- Creates user guides and tutorials
- Sets up documentation structure

### Update
```
/docs update [component]
```
- Updates existing documentation to match current code
- Refreshes API docs and examples
- Updates installation and setup instructions
- Syncs documentation with recent changes

### Review
```
/docs review
```
- Analyzes documentation completeness and accuracy
- Identifies outdated or missing documentation
- Suggests improvements for clarity and usability
- Validates examples and code snippets

## Documentation Types

### API Documentation
- Function signatures and parameters
- Return types and exceptions
- Usage examples and code snippets
- Integration patterns

### User Guides
- Installation and setup instructions
- Getting started tutorials
- Common use cases and examples
- Troubleshooting guides

### Architecture Docs
- System design and components
- Data flow and interactions
- Configuration and deployment
- Extension and customization

### Development Docs
- Contributing guidelines
- Code standards and conventions
- Testing strategies
- Release processes

## Standards
- **Clarity**: Write for the intended audience
- **Accuracy**: Keep docs in sync with code
- **Examples**: Include practical, working examples
- **Structure**: Use consistent formatting and organization
- **Completeness**: Cover all public APIs and key workflows

## Integration
- Automatically updates when code changes
- Links to relevant source code
- Includes version information
- Generates changelog entries

## Example
```
/docs generate authentication
```

This will create comprehensive documentation for the authentication system, including API reference, usage examples, security considerations, and integration guides.
