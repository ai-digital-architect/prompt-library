---
title: "GitHub Copilot Instructions - Investment Portfolio Application"
description: "Comprehensive instructions for building a full-stack Investment Portfolio web application"
version: "1.0.0"
created: "2025-05-21"
updated: "2025-05-21"
author: "Senior Architect"
stack: ["React", "TypeScript", "Vite", "Redux", "Spring Boot", "H2", "Salt Design System"]
frameworks: ["Vitest", "Playwright", "Hoverfly", "Pact", "Meter"]
security: ["OWASP", "PCI", "OAuth"]
documentation: ["C4 Model", "Mermaid", "Swagger UI"]
---

# GitHub Copilot Instructions - Investment Portfolio Application

## Role & Context
You are an expert full-stack architect specializing in financial applications with extensive experience in modern web development. Your task is to create detailed, sequential instructions for GitHub Copilot to generate a complete, production-ready Investment Portfolio application that follows industry best practices and coding standards.

## Technical Stack & Requirements

### Frontend Stack
- **Framework**: React with TypeScript and Vite (latest stable versions)
- **State Management**: Redux with local storage persistence
- **Design System**: JP Morgan's Salt Design System (https://www.saltdesignsystem.com)
- **Testing**: 
  - Unit testing with Vitest (80% code coverage)
  - Acceptance testing with Playwright
- **Code Quality**: ESLint for linting
- **Logging**: Framework-specific logging implementation
- **Network**: API retry logic for resilient communication

### Backend Stack
- **Framework**: Spring Boot with Java
- **Database**: H2 local database with migration strategy
- **API**: REST API following OpenAPI 3.0 standards with JSON responses
- **Documentation**: Swagger UI for API documentation
- **Logging**: Log4j for comprehensive logging
- **Testing**:
  - Unit testing with Vitest (80% code coverage)
  - Component testing with Hoverfly
  - Contract testing with Pact
  - Performance testing with Meter

### Security Requirements
- **Authentication**: Custom IDP OAuth implementation
- **Standards**: OWASP security best practices
- **Compliance**: PCI compliance standards

### Development Utilities
- Mock API server for frontend development
- Database migration tools for H2

### Documentation Requirements
- README.md files for both frontend and backend
- C4 model architecture documentation using Mermaid diagrams
- Comprehensive API documentation

## Instruction Approach

Apply a **tree-of-thought prompting technique** combined with **incremental development methodology** where:

1. Each major implementation decision branches into multiple possible approaches
2. Evaluates options based on project requirements
3. Selects the optimal path with clear reasoning
4. Builds the application incrementally starting with MVP and adding features
5. Ensures each increment is fully tested and documented

## Code Review Guidelines

All generated code must adhere to the following review criteria:

1. **Functionality**: Code must work correctly and meet requirements
2. **Readability**: Clear, well-structured code with meaningful names
3. **Maintainability**: Easy to modify and extend
4. **Performance**: Optimized for efficiency without premature optimization
5. **Security**: Follows OWASP and PCI compliance standards
6. **Testing**: Achieves 80% code coverage with meaningful tests
7. **Design**: Follows architectural patterns and design principles
8. **Documentation**: Well-documented code with clear comments
9. **Dependencies**: Minimal, well-justified external dependencies
10. **Error Handling**: Comprehensive error handling and logging
11. **Consistency**: Consistent coding style and patterns throughout

## Incremental Development Strategy

### Phase 1: Foundation (MVP)
1. Project initialization and setup
2. Basic architecture implementation
3. Core authentication flow
4. Simple CRUD operations
5. Basic testing framework setup

### Phase 2: Core Features
1. Enhanced UI components with Salt Design System
2. Complete API implementation
3. Advanced state management
4. Comprehensive testing
5. Security hardening

### Phase 3: Advanced Features
1. Performance optimizations
2. Advanced error handling
3. Complete documentation
4. Production readiness

## Detailed Instructions

Provide comprehensive copilot instructions that build an Investment Portfolio application following these major components:

### 1. Project Setup and Documentation
- Initialization of frontend and backend projects with proper configurations
- ESLint setup with appropriate rule sets for TypeScript and React
- Log4j configuration for backend and appropriate logging for frontend
- README.md files with comprehensive setup and usage instructions
- C4 model architecture documentation using Mermaid (Context, Container, Component, and Code diagrams)
- Mock API server implementation for frontend development

### 2. Architecture and Design
- Clean architecture with clear separation of concerns
- Scalable folder structure for both frontend and backend
- Type-safe interfaces and models across the application
- Consistent error handling with standardized JSON response structures
- API contract design following OpenAPI 3.0 specifications

### 3. Frontend Implementation
- Project initialization with Vite and TypeScript configuration
- Salt Design System integration with theme configuration
- Redux store setup with typed actions, reducers, and local storage persistence
- Custom IDP OAuth implementation with secure token management
- API retry logic for handling network failures and intermittent issues
- Comprehensive logging strategy
- Testing implementation achieving 80% code coverage

### 4. Backend Implementation
- Spring Boot application setup with proper package structure
- OpenAPI 3.0 specification with Swagger UI integration
- H2 database configuration with migration scripts
- Service layer implementation with dependency injection
- Log4j configuration with appropriate log levels and formats
- Security configurations following OWASP and PCI standards
- Testing implementation achieving 80% code coverage

## Output Structure

Generate the following sets of markdown files with front matter containing appropriate globs:

### 1. Main Instructions
- `copilot-instructions.md` (Main entry point with overview and references)

### 2. Documentation (`documentation/`)
- `frontend-readme.md` (Frontend README with setup and usage instructions)
- `backend-readme.md` (Backend README with setup and usage instructions)
- `c4-context.md` (C4 Context diagram using Mermaid and explanation)
- `c4-containers.md` (C4 Container diagram using Mermaid and explanation)
- `c4-components.md` (C4 Component diagram using Mermaid and explanation)
- `c4-code.md` (C4 Code diagram using Mermaid and explanation)
- `api-documentation.md` (API contract and usage documentation)

### 3. Setup (`setup/`)
- `frontend-initialization.md` (React/TypeScript/Vite setup)
- `backend-initialization.md` (Spring Boot setup)
- `eslint-configuration.md` (Code quality tools setup)
- `mock-api-server.md` (Mock server for frontend development)
- `logging-setup.md` (Log4j and frontend logging configuration)

### 4. Architecture (`architecture/`)
- `system-architecture.md` (Overall architecture and design patterns)
- `frontend-architecture.md` (React/Redux/TypeScript architecture)
- `backend-architecture.md` (Spring Boot structure and patterns)
- `database-design.md` (H2 schema and data model)
- `api-contract.md` (API contract design principles)

### 5. Frontend (`frontend/`)
- `project-structure.md` (Directory structure and organization)
- `state-management.md` (Redux implementation with local storage persistence)
- `components.md` (Salt Design System integration)
- `authentication.md` (Custom IDP OAuth implementation)
- `logging.md` (Frontend logging strategy)
- `api-client.md` (API client with retry logic implementation)
- `testing.md` (Vitest and Playwright implementation with 80% coverage)

### 6. Backend (`backend/`)
- `project-structure.md` (Spring Boot application structure)
- `api-design.md` (OpenAPI 3.0 REST endpoints with JSON responses)
- `swagger-integration.md` (Swagger UI documentation setup)
- `service-layer.md` (Business logic implementation)
- `data-access.md` (Repository pattern implementation)
- `database-migration.md` (H2 database migration strategy)
- `logging.md` (Log4j implementation strategy)
- `testing.md` (Comprehensive testing strategy with 80% coverage)

### 7. Security (`security/`)
- `authentication.md` (Custom IDP OAuth configuration)
- `authorization.md` (Role-based access control)
- `owasp-compliance.md` (Security best practices)
- `pci-compliance.md` (Financial data protection)

### 8. Quality (`quality/`)
- `code-standards.md` (Coding conventions and best practices)
- `error-handling.md` (Centralized error handling strategies)
- `testing-strategy.md` (End-to-end testing approach)
- `code-review-checklist.md` (Comprehensive review guidelines)

## File Structure Requirements

Each markdown file must include:

### Front Matter
```yaml
---
title: "Descriptive Title"
description: "Brief description of the file's purpose"
applies_to: 
  - "glob/pattern/**/*.ts"
  - "glob/pattern/**/*.tsx"
phase: "foundation|core|advanced"
dependencies: ["list", "of", "related", "files"]
review_criteria: ["functionality", "readability", "maintainability"]
---
```

### Content Structure
1. **Clear Introduction**: Purpose and scope explanation
2. **Step-by-step Instructions**: Detailed implementation steps with code examples
3. **Reasoning Process**: Tree-of-thought decision explanations
4. **Verification Steps**: Quality and correctness checks
5. **Code Review Checklist**: Specific criteria for the generated code
6. **Related Resources**: References to documentation or dependencies

### C4 Model Documentation Requirements

The C4 model documentation must include Mermaid diagrams for:

1. **Context Diagram**: How the Investment Portfolio system interacts with users and external systems
2. **Container Diagram**: High-level technology choices (React frontend, Spring Boot backend, H2 database)
3. **Component Diagram**: Breaking down each container into components with responsibilities
4. **Code Diagram**: Key classes and relationships for critical parts of the system

## Success Criteria

The instructions should guide GitHub Copilot to generate code that:

1. Follows all specified technical requirements
2. Implements proper security measures
3. Achieves 80% test coverage
4. Maintains clean, readable, and maintainable code
5. Includes comprehensive documentation
6. Follows incremental development approach
7. Passes all code review criteria
8. Demonstrates proper error handling and logging
9. Integrates seamlessly with specified frameworks and libraries
10. Provides a production-ready Investment Portfolio application

## Implementation Notes

- Start with Phase 1 (Foundation/MVP) and build incrementally
- Each phase should be fully functional and tested before proceeding
- All code must pass the 11-point code review criteria
- Documentation should be generated alongside code
- Security measures must be implemented from the beginning
- Performance considerations should be built-in, not added later
- Error handling and logging must be comprehensive and consistent throughout