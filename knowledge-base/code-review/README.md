# Code Review Guidelines

## General Principles

1. **Code Quality**
   - Clean, readable, and maintainable code
   - Follows SOLID principles
   - Proper error handling
   - Appropriate logging
   - Security best practices

2. **Documentation**
   - Clear API documentation
   - Updated README files
   - Inline comments for complex logic
   - Updated changelog if applicable

3. **Testing**
   - Unit tests for new functionality
   - Integration tests where appropriate
   - Test coverage meets project standards
   - Edge cases considered

## Language-Specific Review Points

### Spring Boot

- Proper dependency injection
- RESTful API conventions
- Exception handling with @ControllerAdvice
- Proper use of Spring annotations

### React + TypeScript

- Proper type definitions
- React hooks usage
- Component composition
- State management patterns
- Performance considerations

### Python/Django

- PEP 8 compliance
- Django best practices
- API security
- Database optimization

### Node.js

- Async/await usage
- Error handling patterns
- Package management
- Security practices

### Infrastructure (Terraform)

- Resource naming conventions
- Security group configurations
- State management
- Module organization

## Review Process

1. **Pre-Review Checklist**
   - All tests passing
   - Code formatting applied
   - Documentation updated
   - No security vulnerabilities

2. **During Review**
   - Focus on logic and architecture
   - Check for edge cases
   - Verify error handling
   - Review test coverage

3. **Post-Review**
   - All comments addressed
   - Changes approved by required reviewers
   - CI/CD pipelines passing

## Review Comments Best Practices

1. Be constructive and specific
2. Link to documentation when applicable
3. Explain why, not just what
4. Share knowledge and alternatives
5. Use GitHub Copilot context for suggestions

## Automated Checks

- Linting
- Type checking
- Test coverage
- Security scanning
- Performance metrics
