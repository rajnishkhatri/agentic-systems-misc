# /reflect - Post-Implementation Analysis and Learning

Use this command after completing features or sprints to analyze what worked well, what didn't, and how to improve future development.

## Usage
```
/reflect [scope: feature|sprint|project] [optional: specific component or timeframe]
```

## Reflection Scope

### Feature Reflection
```
/reflect feature [feature name]
```
- Analyzes a specific feature implementation
- Reviews development process and outcomes
- Identifies lessons learned and improvements

### Sprint Reflection
```
/reflect sprint
```
- Reviews completed work from the current sprint
- Analyzes velocity, quality, and process effectiveness
- Plans improvements for next sprint

### Project Reflection
```
/reflect project
```
- Long-term analysis of project health and direction
- Reviews architectural decisions and their outcomes
- Identifies technical debt and improvement opportunities

## Analysis Areas

### Development Process
- **Planning**: Were requirements clear and complete?
- **Execution**: Did the implementation approach work well?
- **Testing**: Was test coverage adequate and effective?
- **Review**: Were code reviews thorough and helpful?

### Technical Decisions
- **Architecture**: Did design choices support the requirements?
- **Performance**: Are there performance bottlenecks or concerns?
- **Maintainability**: Is the code easy to understand and modify?
- **Scalability**: Will the solution handle future growth?

### Team Collaboration
- **Communication**: Was information shared effectively?
- **Coordination**: Did parallel work streams integrate smoothly?
- **Knowledge Transfer**: Is the team better equipped for similar work?

### Quality Metrics
- **Bug Rate**: How many issues were found post-implementation?
- **Test Coverage**: Did tests catch problems before production?
- **Documentation**: Is the feature well-documented for future work?
- **User Feedback**: How did users respond to the feature?

## Output Format
- **Summary**: Key findings and overall assessment
- **What Worked**: Successful practices to continue
- **What Didn't**: Problems to avoid in the future
- **Improvements**: Specific actions for next iteration
- **Metrics**: Quantitative measures of success/failure

## Learning Integration
- Updates project documentation with lessons learned
- Suggests process improvements for future work
- Identifies training or skill development needs
- Documents patterns and anti-patterns for the team

## Example
```
/reflect feature user-authentication
```

This will analyze the user authentication feature implementation, reviewing the development process, technical decisions, testing approach, and outcomes to identify what worked well and what could be improved in future authentication work.
