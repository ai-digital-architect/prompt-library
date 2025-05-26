# Semantic Memory System
*Factual knowledge, logic patterns, and consistent project information for GitHub Copilot*

## Core Project Facts

### Project Identity
**Project Name**: [Your project name]
**Project Type**: [Web application/API/Mobile app/Desktop application/etc.]
**Primary Purpose**: [Main business purpose and goals]
**Target Users**: [Who uses this system]
**Current Version**: [Current version or development stage]
**Project Status**: [Active development/Maintenance/Legacy/etc.]

### System Architecture
**Architecture Style**: [Microservices/Monolithic/Serverless/Hybrid]
**Primary Language**: [Main programming language and version]
**Framework Stack**: [Primary frameworks and versions]
**Database Technology**: [Database systems used]
**Hosting Environment**: [Cloud provider/On-premise/Hybrid]
**Deployment Method**: [CI/CD pipeline/Manual/Container orchestration]

## Technical Knowledge Base

### Technology Stack Facts
```yaml
Languages:
  Primary: [Language] [Version]
  Secondary: [Additional languages if any]

Frameworks:
  Backend: [Framework] [Version]
  Frontend: [Framework] [Version]
  Testing: [Testing frameworks]

Databases:
  Primary: [Database] [Version]
  Caching: [Redis/Memcached/etc.]
  Search: [ElasticSearch/Solr/etc.]

Infrastructure:
  Cloud: [AWS/Azure/GCP/etc.]
  Containers: [Docker/Kubernetes/etc.]
  CDN: [CloudFlare/AWS CloudFront/etc.]
  Monitoring: [Monitoring tools]
```

### System Architecture Principles
1. **[Principle 1]**: [Fundamental architectural principle]
   - **Rationale**: [Why this principle exists]
   - **Application**: [How it's applied in practice]
   - **Constraints**: [Limitations this principle creates]

2. **[Principle 2]**: [Second architectural principle]
   - **Rationale**: [Why this principle exists]
   - **Application**: [How it's applied in practice]
   - **Constraints**: [Limitations this principle creates]

3. **Security Review**
   - **Input Validation**: [Is user input properly validated and sanitized]
   - **Authentication**: [Are authentication requirements properly enforced]
   - **Authorization**: [Are permission checks correctly implemented]
   - **Data Protection**: [Is sensitive data properly protected]

4. **Architecture Review**
   - **Design Patterns**: [Are appropriate design patterns used]
   - **Dependencies**: [Are dependencies managed appropriately]
   - **Integration**: [Does code integrate properly with existing systems]
   - **Scalability**: [Will code perform well under load]

## Consistency Rules and Validation

### Code Consistency Rules
**Error Handling Consistency**:
```yaml
Exception Handling:
  - All public methods must handle exceptions appropriately
  - Error messages must be user-friendly and actionable
  - Internal errors must be logged with sufficient detail
  - Error responses must follow standard format

Logging Consistency:
  - All significant operations must be logged
  - Log levels must be used appropriately (ERROR, WARN, INFO, DEBUG)
  - Log messages must include relevant context
  - No sensitive information in logs

Validation Consistency:
  - All user inputs must be validated at entry points
  - Business rule validation must be centralized
  - Validation errors must provide clear feedback
  - Default values must be explicit and documented
```

**API Consistency Rules**:
```yaml
Request/Response Format:
  - All responses must include standard metadata
  - Error responses must follow error response schema
  - Success responses must follow success response schema
  - Pagination must use standard pagination format

URL and Method Consistency:
  - REST endpoints must follow URL naming conventions
  - HTTP methods must be used semantically correctly
  - Query parameters must follow naming conventions
  - Headers must follow standard header conventions

Documentation Consistency:
  - All endpoints must be documented with examples
  - Request/response schemas must be documented
  - Error codes and messages must be documented
  - Authentication requirements must be clear
```

### Data Consistency Rules
**Database Consistency**:
```yaml
Schema Standards:
  - All tables must have primary keys
  - Foreign keys must be properly defined
  - Indexes must follow naming conventions
  - Data types must be appropriate for data

Data Integrity:
  - Referential integrity must be maintained
  - Business rules must be enforced at database level where appropriate
  - Data validation must prevent invalid states
  - Audit trails must be maintained for critical data

Migration Standards:
  - All schema changes must be done through migrations
  - Migrations must be reversible where possible
  - Data migrations must preserve data integrity
  - Migration scripts must be tested before deployment
```

**Caching Consistency**:
```yaml
Cache Strategy:
  - Cache keys must follow naming conventions
  - Cache expiration must be appropriate for data volatility
  - Cache invalidation must be handled correctly
  - Cache misses must be handled gracefully

Cache Coherence:
  - Related data must be invalidated together
  - Cache updates must maintain data consistency
  - Distributed cache must handle network partitions
  - Cache warming strategies must be implemented for critical data
```

## Business Logic Patterns

### Validation Patterns
**Input Validation Framework**:
```yaml
Client-Side Validation:
  - Immediate feedback for user experience
  - Basic format and range validation
  - Cannot be relied upon for security
  - Must be duplicated on server side

Server-Side Validation:
  - Authoritative validation for all inputs
  - Business rule enforcement
  - Security validation and sanitization
  - Error handling and user feedback

Database Validation:
  - Data integrity constraints
  - Referential integrity enforcement
  - Final safety net for data consistency
  - Performance considerations for complex validation
```

**Business Rule Enforcement**:
```yaml
Rule Location:
  - Simple rules: Database constraints
  - Complex rules: Application layer
  - Cross-system rules: Service layer
  - User-configurable rules: Rule engine

Rule Documentation:
  - Business rules must be documented with rationale
  - Implementation location must be documented
  - Rule changes must be tracked and versioned
  - Rule testing must cover all scenarios
```

### Transaction Patterns
**Transaction Management**:
```yaml
Database Transactions:
  - Use transactions for multi-step operations
  - Keep transaction scope as small as possible
  - Handle deadlocks and timeouts gracefully
  - Use appropriate isolation levels

Distributed Transactions:
  - Use saga pattern for cross-service transactions
  - Implement compensation actions for rollback
  - Handle partial failures gracefully
  - Maintain audit trails for distributed operations

Event-Driven Patterns:
  - Use events for loose coupling between services
  - Implement idempotent event handlers
  - Handle event ordering and duplication
  - Maintain event audit trails
```

## Monitoring and Observability Knowledge

### Monitoring Standards
**Application Monitoring**:
```yaml
Health Checks:
  - All services must implement health check endpoints
  - Health checks must verify critical dependencies
  - Health check responses must be standardized
  - Health checks must be used by load balancers

Performance Metrics:
  - Response time percentiles (50th, 95th, 99th)
  - Error rates by endpoint and error type
  - Throughput (requests per second)
  - Resource utilization (CPU, memory, disk)

Business Metrics:
  - Key business process completion rates
  - User engagement and conversion metrics
  - Feature usage and adoption metrics
  - Revenue and cost impact metrics
```

**Logging Standards**:
```yaml
Log Structure:
  - Use structured logging (JSON format)
  - Include correlation IDs for request tracing
  - Include timestamp, level, and source information
  - Include relevant context and metadata

Log Levels:
  - ERROR: System errors requiring immediate attention
  - WARN: Potential issues that should be monitored
  - INFO: Important business events and state changes
  - DEBUG: Detailed information for troubleshooting

Log Content:
  - No sensitive information (passwords, tokens, PII)
  - Include sufficient context for troubleshooting
  - Use consistent terminology and formatting
  - Include performance timing for operations
```

### Alerting Standards
**Alert Categories**:
```yaml
Critical Alerts:
  - Service unavailability
  - Data corruption or loss
  - Security breaches
  - SLA violations

Warning Alerts:
  - Performance degradation
  - Increased error rates
  - Resource utilization thresholds
  - Dependency issues

Information Alerts:
  - Deployment notifications
  - Configuration changes
  - Capacity planning triggers
  - Maintenance windows
```

## Knowledge Validation Framework

### Accuracy Validation
**Source Authority**:
```yaml
Architecture Knowledge:
  - Source: Lead architect and architecture review board
  - Validation: Architecture review process
  - Update Frequency: Major releases and architecture changes
  - Approval Process: Architecture review board approval

Business Knowledge:
  - Source: Product owner and business stakeholders
  - Validation: Business review process
  - Update Frequency: Feature releases and business requirement changes
  - Approval Process: Product owner approval

Technical Knowledge:
  - Source: Tech leads and engineering team
  - Validation: Technical review process
  - Update Frequency: Technology updates and standard changes
  - Approval Process: Technical lead approval
```

**Consistency Validation**:
```yaml
Cross-Reference Checking:
  - Architecture facts must align with implementation
  - Business rules must be consistently implemented
  - Technical standards must be universally applied
  - Integration patterns must be followed across services

Conflict Resolution:
  - Identify conflicting information
  - Escalate to appropriate authority
  - Document resolution rationale
  - Update all affected knowledge areas
```

### Application Validation
**Usage Monitoring**:
```yaml
Knowledge Application Tracking:
  - Monitor which knowledge is being referenced
  - Track decision alignment with established knowledge
  - Identify knowledge gaps in decision-making
  - Measure knowledge effectiveness in problem-solving

Quality Improvement:
  - Analyze decisions that didn't align with knowledge
  - Identify knowledge that led to poor outcomes
  - Update knowledge based on lessons learned
  - Improve knowledge organization and accessibility
```

## Integration Hooks

### Cross-Memory System Integration
**Long-term Memory Integration**:
```yaml
Preference Validation:
  - Ensure personal preferences don't violate business rules
  - Apply architectural constraints to preference evolution
  - Use factual knowledge to guide preference development
  - Validate preference changes against established standards

Knowledge Enhancement:
  - Use semantic knowledge to improve preference accuracy
  - Apply factual constraints to learned behavioral patterns
  - Ensure consistency between personal and organizational knowledge
```

**Working Memory Integration**:
```yaml
Problem-Solving Support:
  - Provide relevant facts for active problem analysis
  - Apply business rules to solution evaluation
  - Ensure architectural compliance in solution design
  - Reference standards during implementation planning

Decision Support:
  - Apply decision frameworks to active choices
  - Provide constraint information for option evaluation
  - Reference past similar decisions and outcomes
  - Ensure consistency with established patterns
```

**Procedural Memory Integration**:
```yaml
Workflow Validation:
  - Ensure automated procedures follow established standards
  - Apply quality gates based on factual requirements
  - Validate procedure outputs against business rules
  - Maintain consistency with architectural principles

Process Enhancement:
  - Use factual knowledge to improve procedure effectiveness
  - Apply standards to procedure template generation
  - Ensure procedures maintain data integrity and security
  - Validate procedures against compliance requirements
```

**Episodic Memory Integration**:
```yaml
Historical Context:
  - Validate episodic memories against factual knowledge
  - Use facts to interpret historical events and decisions
  - Apply current knowledge to understand past contexts
  - Ensure lessons learned align with established facts

Pattern Recognition:
  - Use factual knowledge to identify meaningful patterns
  - Validate patterns against business rules and constraints
  - Apply architectural knowledge to pattern interpretation
  - Ensure pattern application maintains consistency
```

### External System Integration
**Documentation Systems**:
```yaml
Knowledge Synchronization:
  - Sync with official documentation systems
  - Reference authoritative design documents
  - Maintain links to specification documents
  - Update based on official policy changes

Version Control:
  - Track knowledge changes with version control
  - Maintain history of knowledge evolution
  - Link knowledge updates to code changes
  - Coordinate knowledge updates with releases
```

## Knowledge Maintenance and Evolution

### Update Procedures
**Regular Review Cycles**:
```yaml
Weekly Reviews:
  - Validate recent knowledge applications
  - Check for new information requiring updates
  - Review consistency across knowledge areas
  - Identify immediate correction needs

Monthly Reviews:
  - Comprehensive accuracy validation
  - Cross-system integration assessment
  - Knowledge gap analysis
  - Usage pattern analysis

Quarterly Reviews:
  - Strategic knowledge alignment assessment
  - Technology evolution impact analysis
  - Business requirement evolution review
  - Knowledge architecture optimization
```

**Change Management**:
```yaml
Change Process:
  1. Change Request: Document proposed knowledge change
  2. Impact Assessment: Analyze effects on related knowledge
  3. Stakeholder Review: Get approval from knowledge owners
  4. Implementation: Update knowledge base systematically
  5. Validation: Verify changes maintain consistency
  6. Communication: Notify affected team members
  7. Monitoring: Track effectiveness of changes

Emergency Changes:
  - Fast-track process for critical corrections
  - Immediate implementation with post-facto review
  - Rapid communication to affected stakeholders
  - Documentation of emergency change rationale
```

### Knowledge Evolution
**Continuous Improvement**:
```yaml
Learning Integration:
  - Incorporate lessons learned from projects
  - Update knowledge based on technology evolution
  - Refine patterns based on effectiveness data
  - Improve organization based on usage patterns

Quality Enhancement:
  - Regular accuracy and consistency audits
  - User feedback integration for knowledge improvement
  - Performance analysis for knowledge application
  - Best practice identification and documentation
```

---

**Knowledge Base Established**: [Date when semantic memory system was created]
**Last Major Update**: [Most recent comprehensive knowledge update]
**Knowledge Areas**: [Count of major knowledge categories]
**Validation Status**: [Current accuracy and consistency status]
**Next Review**: [Scheduled comprehensive knowledge review date]
**Authority Level**: [Confidence level in knowledge base accuracy and completeness][Principle 3]**: [Third architectural principle]
   - **Rationale**: [Why this principle exists]
   - **Application**: [How it's applied in practice]
   - **Constraints**: [Limitations this principle creates]

### System Boundaries and Responsibilities
**Service/Module A**: [Name]
- **Purpose**: [What this component does]
- **Responsibilities**: [Specific duties and functions]
- **Dependencies**: [What it depends on]
- **Interfaces**: [How other components interact with it]
- **Data Ownership**: [What data it owns/manages]

**Service/Module B**: [Name]
- **Purpose**: [What this component does]
- **Responsibilities**: [Specific duties and functions]
- **Dependencies**: [What it depends on]
- **Interfaces**: [How other components interact with it]
- **Data Ownership**: [What data it owns/manages]

**Service/Module C**: [Name]
- **Purpose**: [What this component does]
- **Responsibilities**: [Specific duties and functions]
- **Dependencies**: [What it depends on]
- **Interfaces**: [How other components interact with it]
- **Data Ownership**: [What data it owns/manages]

## Business Domain Knowledge

### Core Business Rules
**Rule 1**: [Fundamental business rule]
- **Description**: [Detailed explanation of the rule]
- **Impact**: [What this affects in the system]
- **Exceptions**: [Any exceptions to this rule]
- **Implementation**: [How this is enforced in code]

**Rule 2**: [Second business rule]
- **Description**: [Detailed explanation of the rule]
- **Impact**: [What this affects in the system]
- **Exceptions**: [Any exceptions to this rule]
- **Implementation**: [How this is enforced in code]

**Rule 3**: [Third business rule]
- **Description**: [Detailed explanation of the rule]
- **Impact**: [What this affects in the system]
- **Exceptions**: [Any exceptions to this rule]
- **Implementation**: [How this is enforced in code]

### Domain Models and Entities
**Entity: [Entity Name]**
```yaml
Purpose: [What this entity represents]
Key Properties:
  - property1: [Type] [Description]
  - property2: [Type] [Description]
  - property3: [Type] [Description]
Relationships:
  - [Related Entity]: [Relationship type and description]
Business Rules:
  - [Rule affecting this entity]
Validation Rules:
  - [Validation requirements]
```

**Entity: [Entity Name]**
```yaml
Purpose: [What this entity represents]
Key Properties:
  - property1: [Type] [Description]
  - property2: [Type] [Description]
  - property3: [Type] [Description]
Relationships:
  - [Related Entity]: [Relationship type and description]
Business Rules:
  - [Rule affecting this entity]
Validation Rules:
  - [Validation requirements]
```

### Business Processes and Workflows
**Process: [Process Name]**
1. **Trigger**: [What initiates this process]
2. **Prerequisites**: [What must be true before starting]
3. **Steps**: [Ordered list of process steps]
4. **Validation Points**: [Where business rules are checked]
5. **Outcomes**: [Possible results of the process]
6. **Error Handling**: [How errors are managed]
7. **Rollback**: [How to undo if needed]

**Process: [Process Name]**
1. **Trigger**: [What initiates this process]
2. **Prerequisites**: [What must be true before starting]
3. **Steps**: [Ordered list of process steps]
4. **Validation Points**: [Where business rules are checked]
5. **Outcomes**: [Possible results of the process]
6. **Error Handling**: [How errors are managed]
7. **Rollback**: [How to undo if needed]

## Technical Standards and Conventions

### Coding Standards
**Language-Specific Standards**:
```yaml
Naming Conventions:
  Variables: [camelCase/snake_case/etc.]
  Functions: [naming pattern]
  Classes: [naming pattern]
  Constants: [naming pattern]
  Files: [naming pattern]

Code Organization:
  File Structure: [How files are organized]
  Import Order: [How imports are ordered]
  Function Order: [How functions are arranged]
  Comment Style: [Comment format and requirements]

Code Quality:
  Line Length: [Maximum line length]
  Function Length: [Maximum function length]
  Complexity: [Cyclomatic complexity limits]
  Documentation: [Documentation requirements]
```

**Framework-Specific Standards**:
```yaml
[Framework Name]:
  Component Structure: [How components are organized]
  State Management: [How state is handled]
  Error Handling: [Error handling patterns]
  Testing Patterns: [How tests are structured]
  Performance: [Performance requirements]
```

### API Design Standards
**REST API Standards**:
```yaml
URL Structure:
  Pattern: [URL naming pattern]
  Versioning: [How APIs are versioned]
  Resource Naming: [How resources are named]

HTTP Methods:
  GET: [Usage guidelines]
  POST: [Usage guidelines]
  PUT: [Usage guidelines]
  DELETE: [Usage guidelines]
  PATCH: [Usage guidelines]

Response Format:
  Success: [Standard success response format]
  Error: [Standard error response format]
  Pagination: [How pagination is handled]
  Filtering: [How filtering is implemented]

Authentication:
  Method: [Authentication method used]
  Headers: [Required headers]
  Tokens: [Token format and lifecycle]
```

### Database Standards
**Schema Design Standards**:
```yaml
Naming Conventions:
  Tables: [Table naming pattern]
  Columns: [Column naming pattern]
  Indexes: [Index naming pattern]
  Constraints: [Constraint naming pattern]

Design Principles:
  Normalization: [Normalization level used]
  Relationships: [How relationships are modeled]
  Data Types: [Preferred data types]
  Constraints: [Standard constraints used]

Performance Standards:
  Indexing: [Indexing requirements]
  Query Optimization: [Query performance standards]
  Data Archiving: [Data retention policies]
```

## Integration Patterns and Standards

### Internal Integration
**Service-to-Service Communication**:
- **Protocol**: [HTTP/gRPC/Message Queue/etc.]
- **Data Format**: [JSON/XML/Protocol Buffers/etc.]
- **Authentication**: [How services authenticate]
- **Error Handling**: [How errors are communicated]
- **Retry Logic**: [How retries are handled]
- **Circuit Breakers**: [How circuit breakers are implemented]

**Database Integration**:
- **Connection Management**: [How connections are managed]
- **Transaction Handling**: [Transaction patterns]
- **Migration Strategy**: [How database changes are managed]
- **Backup and Recovery**: [Data protection strategies]

### External Integration
**Third-Party APIs**:
- **Authentication**: [How external APIs are authenticated]
- **Rate Limiting**: [How rate limits are handled]
- **Error Handling**: [How external errors are managed]
- **Data Transformation**: [How external data is normalized]
- **Monitoring**: [How integrations are monitored]

**Webhook Handling**:
- **Security**: [How webhooks are secured]
- **Validation**: [How webhook data is validated]
- **Processing**: [How webhook events are processed]
- **Retry Logic**: [How failed webhooks are retried]

## Security Knowledge Base

### Security Principles
1. **Authentication**: [How users are authenticated]
2. **Authorization**: [How permissions are enforced]
3. **Data Protection**: [How sensitive data is protected]
4. **Communication Security**: [How communications are secured]
5. **Audit Logging**: [What security events are logged]

### Security Standards
**Data Security**:
```yaml
Encryption:
  At Rest: [How data is encrypted when stored]
  In Transit: [How data is encrypted during transmission]
  Key Management: [How encryption keys are managed]

Access Control:
  Authentication: [Authentication mechanisms]
  Authorization: [Authorization patterns]
  Session Management: [How sessions are managed]
  Password Policy: [Password requirements]

Data Privacy:
  PII Handling: [How personally identifiable information is handled]
  Data Retention: [How long data is kept]
  Data Deletion: [How data is securely deleted]
  Compliance: [Relevant compliance requirements]
```

### Security Compliance
**Regulatory Requirements**:
- **[Regulation 1]**: [How this regulation affects the system]
- **[Regulation 2]**: [How this regulation affects the system]
- **Data Processing**: [How data processing complies with regulations]
- **User Rights**: [What rights users have regarding their data]

## Performance and Scalability Knowledge

### Performance Requirements
**Response Time Standards**:
```yaml
API Endpoints:
  Critical: [< X milliseconds]
  Standard: [< X milliseconds]
  Bulk Operations: [< X seconds]

Database Queries:
  Simple Queries: [< X milliseconds]
  Complex Queries: [< X milliseconds]
  Reports: [< X seconds]

Page Load Times:
  Critical Pages: [< X seconds]
  Standard Pages: [< X seconds]
  Heavy Pages: [< X seconds]
```

**Scalability Standards**:
```yaml
Concurrent Users:
  Current Capacity: [Number of users]
  Target Capacity: [Target number of users]
  Peak Load: [Peak usage patterns]

Data Volume:
  Current Size: [Current data volume]
  Growth Rate: [Expected growth rate]
  Retention Period: [How long data is kept]

Transaction Volume:
  Current TPS: [Transactions per second]
  Target TPS: [Target transactions per second]
  Peak Load: [Peak transaction patterns]
```

### Performance Optimization Patterns
**Caching Strategy**:
- **Browser Caching**: [How browser caching is configured]
- **CDN Caching**: [How CDN caching is used]
- **Application Caching**: [How application-level caching works]
- **Database Caching**: [How database query caching works]

**Database Optimization**:
- **Query Optimization**: [Query optimization standards]
- **Index Strategy**: [Indexing standards and patterns]
- **Connection Pooling**: [How database connections are managed]
- **Read Replicas**: [How read scaling is handled]

## Logic Patterns and Decision Frameworks

### Technology Decision Framework
When evaluating new technologies:
1. **Compatibility Assessment**
   - **Current Stack**: [How well does it integrate with existing technology]
   - **Team Knowledge**: [Does team have expertise or can acquire it]
   - **Migration Path**: [How difficult is adoption/migration]

2. **Business Value Assessment**
   - **Problem Solving**: [How well does it solve the business problem]
   - **Cost-Benefit**: [Is the value worth the cost and effort]
   - **Time to Value**: [How quickly can benefits be realized]

3. **Risk Assessment**
   - **Maturity**: [How mature and stable is the technology]
   - **Community**: [Size and activity of community support]
   - **Vendor Lock-in**: [Risk of becoming dependent on specific vendor]
   - **Security**: [Security implications and track record]

4. **Long-term Viability**
   - **Roadmap**: [Technology roadmap and future development]
   - **Alternatives**: [Availability of alternatives and exit strategies]
   - **Skill Market**: [Availability of skills in job market]

### Problem-Solving Framework
When approaching technical problems:
1. **Problem Definition**
   - **Symptoms**: [What is observed that indicates a problem]
   - **Impact**: [Who or what is affected and how]
   - **Constraints**: [What limitations exist for solving the problem]
   - **Success Criteria**: [How will we know the problem is solved]

2. **Root Cause Analysis**
   - **Data Collection**: [What information is needed]
   - **Hypothesis Formation**: [Possible causes to investigate]
   - **Testing**: [How to validate or eliminate hypotheses]
   - **Verification**: [How to confirm the root cause]

3. **Solution Design**
   - **Options**: [Different approaches to solving the problem]
   - **Trade-offs**: [Pros and cons of each approach]
   - **Architecture Alignment**: [How solutions fit with system architecture]
   - **Resource Requirements**: [What resources are needed for each option]

4. **Implementation Planning**
   - **Phases**: [How to break implementation into phases]
   - **Testing Strategy**: [How to validate the solution works]
   - **Rollback Plan**: [How to revert if the solution causes problems]
   - **Monitoring**: [How to track solution effectiveness]

### Code Review Framework
When reviewing code:
1. **Functionality Review**
   - **Requirements**: [Does code meet functional requirements]
   - **Business Logic**: [Is business logic correctly implemented]
   - **Edge Cases**: [Are edge cases properly handled]
   - **Error Handling**: [Are errors properly caught and handled]

2. **Quality Review**
   - **Standards Compliance**: [Does code follow established standards]
   - **Readability**: [Is code clear and well-documented]
   - **Maintainability**: [Will code be easy to modify and extend]
   - **Performance**: [Are there performance concerns]

3. **