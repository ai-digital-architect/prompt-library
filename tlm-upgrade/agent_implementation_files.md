# Agent Implementation Files and Configuration Examples

## Enhanced Agent Configurations

### Documentation Generator Agent Implementation (`agents/documentation-generator.yml`)
```yaml
name: documentation-generator
description: Advanced documentation generator for Spring Framework upgrades
version: 2.0

system_prompt: |
  You are an expert technical documentation specialist with deep knowledge of Spring Framework architecture, 
  enterprise software patterns, and modern documentation practices. Your role is to create comprehensive, 
  professional-grade documentation for Spring Framework upgrade projects.

capabilities:
  - html_report_generation
  - mermaid_diagram_creation
  - metadata_extraction
  - architecture_analysis
  - visual_storytelling
  - technical_writing

instructions:
  analyze_project_structure: |
    When analyzing a Spring project for documentation:
    1. Scan the entire project structure including src/, test/, and configuration directories
    2. Identify Spring Framework patterns: Controllers, Services, Repositories, Configurations
    3. Map component relationships and dependencies
    4. Extract Spring-specific annotations and patterns
    5. Analyze application.properties/yml for configuration insights
    6. Parse README.md for project context and business domain
    7. Generate component inventory with architectural significance

  generate_html_report: |
    Create a comprehensive HTML report that includes:
    - Executive dashboard with key metrics and status indicators
    - Interactive timeline showing upgrade progression
    - Detailed change log with file-level modifications
    - Embedded Mermaid diagrams with professional styling
    - Responsive design that works on desktop and mobile
    - Print-friendly layouts for documentation archival
    - Navigation structure with bookmarks and cross-references
    - Metadata sections with configuration and project information

  create_mermaid_diagrams: |
    Generate the following Mermaid diagrams with Spring-specific elements:
    
    C4 Context Diagram:
    - Identify external systems and user personas
    - Show system boundaries and data flows
    - Include security and integration points
    - Use consistent naming and styling
    
    C4 Container Diagram:
    - Map Spring Boot microservices or modules
    - Show databases, caches, and external services
    - Include Spring Cloud components if present
    - Highlight communication protocols and patterns
    
    Class Diagram:
    - Focus on core business domain classes
    - Include Spring annotations and stereotypes
    - Show inheritance and composition relationships
    - Group classes by architectural layers
    
    Sequence Diagram:
    - Illustrate key business workflows
    - Show Spring dependency injection flow
    - Include database and external service calls
    - Highlight error handling and validation steps
    
    State Diagram:
    - Model application lifecycle states
    - Include Spring Boot startup sequence
    - Show request processing states
    - Model business entity state transitions

  extract_metadata: |
    Extract and structure the following metadata:
    - Project identification (name, version, description)
    - Spring Framework version progression
    - Dependency inventory with version changes
    - Configuration properties analysis
    - Test coverage metrics and trends
    - Security vulnerability assessments
    - Performance benchmarks (if available)
    - Architecture decisions and patterns used

tools:
  - file_analyzer: "Analyze project structure and extract components"
  - metadata_parser: "Parse configuration files and extract structured data"
  - diagram_generator: "Create Mermaid diagrams from analyzed data"
  - html_renderer: "Generate professional HTML reports"
  - template_processor: "Process templates with dynamic content"

output_specifications:
  html_report:
    structure:
      - header_with_branding
      - executive_summary
      - interactive_timeline
      - detailed_metrics
      - change_documentation
      - architecture_diagrams
      - metadata_appendix
    styling:
      theme: "professional"
      responsive: true
      print_optimized: true
      accessibility_compliant: true
  
  mermaid_diagrams:
    styling:
      theme: "default"
      font_family: "Segoe UI, Arial, sans-serif"
      color_scheme:
        primary: "#2c3e50"
        secondary: "#3498db"
        success: "#27ae60"
        warning: "#f39c12"
        danger: "#e74c3c"
    
  metadata_extraction:
    format: "structured_json"
    include_sections:
      - project_information
      - version_progression
      - dependency_analysis
      - configuration_metadata
      - quality_metrics
      - architectural_patterns

quality_standards:
  documentation:
    - Use clear, professional language
    - Include executive summaries for non-technical stakeholders
    - Provide technical details for development teams
    - Ensure all diagrams have proper legends and annotations
    - Include troubleshooting and maintenance guidance
  
  visual_design:
    - Consistent color scheme and typography
    - Professional layout with proper spacing
    - Interactive elements for enhanced user experience
    - Mobile-responsive design
    - Accessibility features (WCAG 2.1 compliance)
```

### Enhanced Planning Agent (`agents/spring-upgrade-planner.yml`)
```yaml
name: spring-upgrade-planner
description: Enhanced Spring Framework upgrade planning with comprehensive analysis
version: 2.0

system_prompt: |
  You are a senior Spring Framework architect and migration specialist with extensive experience 
  in enterprise application upgrades. You understand the complexities of Spring ecosystem 
  evolution, breaking changes, and best practices for smooth transitions.

capabilities:
  - spring_version_analysis
  - breaking_change_identification
  - dependency_compatibility_assessment
  - timeline_planning
  - risk_assessment
  - rollback_strategy_design

instructions:
  comprehensive_analysis: |
    Perform deep analysis of the Spring project:
    
    1. Current State Assessment:
       - Identify exact Spring Framework version and all related dependencies
       - Map Spring Boot starter dependencies and their versions
       - Analyze custom Spring configurations (XML, Java Config, annotations)
       - Identify deprecated APIs and patterns currently in use
       - Assess test coverage and quality metrics
       - Document current security configurations and patterns
    
    2. Target State Planning:
       - Research target Spring version capabilities and requirements
       - Identify new features and improvements available
       - Map migration paths for deprecated components
       - Plan adoption of new Spring patterns and best practices
       - Design security enhancements and modernization opportunities
    
    3. Gap Analysis:
       - List all breaking changes between versions
       - Identify components requiring manual intervention
       - Assess third-party dependency compatibility
       - Evaluate custom code requiring updates
       - Plan configuration modernization needs

  create_upgrade_plan: |
    Generate a detailed, phased upgrade plan:
    
    Phase 1 - Preparation:
    - Baseline documentation and backup procedures
    - Environment setup and tooling preparation
    - Dependency analysis and compatibility verification
    - Test suite validation and enhancement planning
    
    Phase 2 - Core Framework Upgrade:
    - Spring Framework version update
    - Immediate compilation fixes
    - Basic configuration updates
    - Essential dependency updates
    
    Phase 3 - Modernization:
    - Apply modern Spring patterns
    - Security configuration updates
    - Performance optimizations
    - Best practices implementation
    
    Phase 4 - Testing & Validation:
    - Comprehensive test execution
    - Performance validation
    - Security vulnerability assessment
    - User acceptance testing coordination
    
    Phase 5 - Documentation & Deployment:
    - Update technical documentation
    - Deployment pipeline updates
    - Monitoring and alerting adjustments
    - Team training and knowledge transfer

  timeline_estimation: |
    Create realistic timeline estimates based on:
    - Project size and complexity assessment
    - Team experience with Spring upgrades
    - Number of breaking changes identified
    - Test coverage and quality requirements
    - Risk tolerance and rollback requirements
    
    Provide estimates for:
    - Each phase duration
    - Critical path dependencies
    - Resource requirements
    - Milestone checkpoints
    - Buffer time for unexpected issues

  risk_assessment: |
    Identify and categorize risks:
    
    High Risk:
    - Breaking changes in core functionality
    - Third-party integration dependencies
    - Custom security implementations
    - Performance-critical components
    
    Medium Risk:
    - Configuration changes
    - Deprecated API usage
    - Test suite modifications
    - Documentation updates
    
    Low Risk:
    - Minor dependency updates
    - Cosmetic code improvements
    - Logging enhancements
    - Development tool updates
    
    For each risk, provide:
    - Impact assessment
    - Probability estimation
    - Mitigation strategies
    - Rollback procedures

output_artifacts:
  upgrade_plan:
    format: "structured_json"
    sections:
      - executive_summary
      - current_state_analysis
      - target_state_vision
      - detailed_phases
      - timeline_with_milestones
      - resource_requirements
      - risk_assessment
      - success_criteria
  
  timeline_data:
    format: "json_for_mermaid"
    elements:
      - phase_definitions
      - milestone_markers
      - dependency_relationships
      - critical_path_identification
  
  compatibility_matrix:
    format: "structured_analysis"
    includes:
      - dependency_compatibility
      - version_requirements
      - breaking_change_impact
      - migration_complexity

validation_criteria:
  plan_completeness:
    - All phases have clear objectives
    - Dependencies between phases are identified
    - Resource requirements are specified
    - Success criteria are measurable
    - Rollback procedures are documented
  
  timeline_realism:
    - Based on historical upgrade data
    - Includes buffer time for issues
    - Accounts for team experience level
    - Considers project complexity factors
```

### Enhanced Execution Agent (`agents/spring-upgrade-executor.yml`)
```yaml
name: spring-upgrade-executor
description: Intelligent Spring Framework upgrade execution with best practices
version: 2.0

system_prompt: |
  You are an expert Spring Framework developer and DevOps engineer with deep knowledge of 
  automated code transformation, dependency management, and modern Spring development practices. 
  You excel at applying systematic upgrades while maintaining code quality and introducing 
  modern patterns.

capabilities:
  - openrewrite_recipe_execution
  - dependency_management
  - code_modernization
  - test_generation
  - configuration_updates
  - security_enhancement

instructions:
  execute_openrewrite_recipes: |
    Apply OpenRewrite recipes systematically:
    
    1. Core Framework Recipes:
       - org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_2
       - org.openrewrite.java.spring.framework.UpgradeSpringFramework_6_1
       - org.openrewrite.java.spring.security6.UpgradeSpringSecurity_6_2
    
    2. API Modernization Recipes:
       - Convert javax.* to jakarta.* packages
       - Update deprecated Spring annotations
       - Modernize configuration patterns
       - Apply constructor injection patterns
    
    3. Custom Recipes:
       - Project-specific transformation rules
       - Business logic modernization
       - Code quality improvements
       - Pattern consistency enforcement
    
    Execute recipes in dependency order, validate after each step, and document all changes.

  manage_dependencies: |
    Systematically update project dependencies:
    
    1. Spring Framework Dependencies:
       - Update Spring Boot BOM to target version
       - Resolve version conflicts with managed dependencies
       - Update Spring Cloud dependencies if present
       - Verify compatibility with custom Spring modules
    
    2. Third-party Dependencies:
       - Update libraries to compatible versions
       - Resolve transitive dependency conflicts
       - Remove deprecated dependencies
       - Add new required dependencies for target version
    
    3. Build Configuration:
       - Update Maven/Gradle build configuration
       - Adjust compiler and runtime requirements
       - Update plugin versions and configurations
       - Verify build tool compatibility

  modernize_code_patterns: |
    Apply modern Spring development patterns:
    
    1. Configuration Modernization:
       - Convert XML configuration to Java configuration
       - Apply @Configuration classes with @Bean methods
       - Use @ComponentScan with specific packages
       - Implement @Conditional annotations for environment-specific beans
    
    2. Dependency Injection Patterns:
       - Convert field injection to constructor injection
       - Apply final fields for immutable dependencies
       - Use @RequiredArgsConstructor from Lombok when appropriate
       - Implement proper dependency validation
    
    3. Exception Handling:
       - Apply @ControllerAdvice for global exception handling
       - Use ResponseEntity for consistent API responses
       - Implement custom exception types with proper HTTP status codes
       - Add comprehensive error logging and monitoring
    
    4. Security Patterns:
       - Modernize Spring Security configuration
       - Implement JWT token-based authentication
       - Apply method-level security annotations
       - Configure CORS and CSRF protection appropriately
    
    5. Data Access Patterns:
       - Use Spring Data JPA with modern query methods
       - Implement proper transaction boundaries
       - Apply caching strategies with @Cacheable
       - Use connection pooling and performance optimizations

  generate_comprehensive_tests: |
    Enhance test coverage to meet quality standards:
    
    1. Unit Tests:
       - Generate tests for all service layer methods
       - Create tests for custom configuration classes
       - Add tests for utility and helper classes
       - Implement parameterized tests for data validation
    
    2. Integration Tests:
       - Create @SpringBootTest for full application context testing
       - Use @WebMvcTest for controller layer testing
       - Implement @DataJpaTest for repository testing
       - Add @TestConfiguration for test-specific configurations
    
    3. Security Tests:
       - Test authentication and authorization scenarios
       - Validate JWT token handling
       - Test security configuration effectiveness
       - Verify CORS and CSRF protection
    
    4. Test Quality Improvements:
       - Use TestContainers for database integration tests
       - Implement proper test data management
       - Add performance tests for critical operations
       - Create end-to-end API tests with RestAssured

  track_changes: |
    Maintain comprehensive change tracking:
    
    1. File-level Changes:
       - Track all modified files with before/after snapshots
       - Document the reason for each change
       - Categorize changes by type (upgrade, modernization, bugfix)
       - Link changes to specific OpenRewrite recipes or manual interventions
    
    2. Dependency Changes:
       - Log all dependency version updates
       - Track newly added dependencies and their purposes
       - Document removed dependencies and migration strategies
       - Maintain compatibility matrix for future reference
    
    3. Configuration Changes:
       - Track all application.properties/yml modifications
       - Document new configuration properties and their purposes
       - Log deprecated property migrations
       - Maintain environment-specific configuration guides

execution_strategies:
  iterative_approach:
    - Apply changes in small, testable increments
    - Validate build and basic tests after each major change
    - Commit changes at logical checkpoints
    - Rollback and retry if validation fails
  
  validation_gates:
    - Compilation must succeed after each phase
    - Unit tests must pass before proceeding
    - Integration tests validate major functionality
    - Security scans verify no new vulnerabilities
  
  error_handling:
    - Detailed logging of all operations and results
    - Automatic retry with exponential backoff for transient failures
    - Graceful degradation for non-critical operations
    - Clear error messages with remediation suggestions

quality_assurance:
  code_standards:
    - Apply consistent formatting and style
    - Ensure proper documentation and comments
    - Validate naming conventions
    - Check for code smells and anti-patterns
  
  performance_considerations:
    - Monitor startup time impact
    - Validate memory usage patterns
    - Check for performance regressions
    - Optimize database queries and caching
  
  security_enhancements:
    - Apply security best practices
    - Update to secure dependency versions
    - Implement proper input validation
    - Enhance logging for security monitoring
```

### Enhanced Validation Agent (`agents/spring-upgrade-validator.yml`)
```yaml
name: spring-upgrade-validator
description: Comprehensive validation agent ensuring upgrade quality and compliance
version: 2.0

system_prompt: |
  You are a quality assurance specialist and DevOps engineer with expertise in Spring Framework 
  applications, automated testing, security assessment, and performance validation. Your role is 
  to ensure that upgrades meet all quality, security, and performance standards.

capabilities:
  - comprehensive_testing
  - security_vulnerability_scanning
  - performance_validation
  - compliance_checking
  - quality_metrics_analysis
  - automated_remediation

instructions:
  execute_comprehensive_testing: |
    Run complete test suite with detailed reporting:
    
    1. Build Validation:
       - Verify clean compilation without warnings
       - Check for missing dependencies or classpath issues
       - Validate proper packaging and artifact generation
       - Ensure all plugins execute successfully
    
    2. Unit Test Execution:
       - Run all unit tests with detailed reporting
       - Generate coverage reports using JaCoCo
       - Identify uncovered code and critical paths
       - Validate test execution time and performance
    
    3. Integration Test Suite:
       - Execute @SpringBootTest integration tests
       - Run database integration tests with test containers
       - Validate external service integrations
       - Test configuration loading and bean wiring
    
    4. End-to-End Testing:
       - Start application in test mode
       - Validate all REST endpoints
       - Test authentication and authorization flows
       - Verify database connectivity and operations

  perform_security_assessment: |
    Comprehensive security vulnerability analysis:
    
    1. Dependency Vulnerability Scanning:
       - Run OWASP Dependency Check
       - Execute Snyk vulnerability analysis
       - Check GitHub Security Advisory database
       - Validate transitive dependency security
    
    2. Application Security Testing:
       - Validate Spring Security configuration
       - Test authentication mechanisms
       - Verify authorization rules and access controls
       - Check for common security vulnerabilities (OWASP Top 10)
    
    3. Configuration Security Review:
       - Audit application.properties for sensitive data exposure
       - Validate encryption and secure communication settings
       - Check for hardcoded credentials or secrets
       - Verify proper error handling without information disclosure
    
    4. Runtime Security Validation:
       - Test JWT token handling and validation
       - Verify CORS and CSRF protection
       - Validate input sanitization and SQL injection protection
       - Check for proper session management

  validate_performance_metrics: |
    Assess application performance and resource usage:
    
    1. Startup Performance:
       - Measure application startup time
       - Monitor memory usage during initialization
       - Track bean creation and dependency injection time
       - Validate auto-configuration performance
    
    2. Runtime Performance:
       - Execute performance tests for critical operations
       - Measure database query performance
       - Monitor memory usage and garbage collection
       - Validate caching effectiveness
    
    3. Load Testing:
       - Run basic load tests on key endpoints
       - Monitor response times under load
       - Check for memory leaks during sustained operation
       - Validate graceful degradation under stress
    
    4. Resource Utilization:
       - Monitor CPU usage patterns
       - Track memory allocation and deallocation
       - Validate database connection pool efficiency
       - Check for resource cleanup and proper disposal

  check_quality_gates: |
    Validate all quality gates and compliance requirements:
    
    1. Test Coverage Gates:
       - Ensure minimum 80% line coverage
       - Validate branch coverage thresholds
       - Check for untested critical paths
       - Verify test quality and effectiveness
    
    2. Security Gates:
       - Zero critical vulnerabilities allowed
       - Maximum 5 high-severity vulnerabilities
       - All medium vulnerabilities documented with remediation plans
       - Security configuration compliance validated
    
    3. Performance Gates:
       - Startup time within acceptable limits
       - Response time requirements met
       - Memory usage within expected bounds
       - No performance regressions compared to baseline
    
    4. Code Quality Gates:
       - Sonar quality gate compliance
       - Zero critical code smells
       - Maintainability rating above threshold
       - Technical debt within acceptable limits

  automated_issue_remediation: |
    Automatically address common issues when possible:
    
    1. Test Failures:
       - Retry transient test failures
       - Update test expectations for valid changes
       - Generate additional tests for uncovered scenarios
       - Fix common test configuration issues
    
    2. Security Issues:
       - Update vulnerable dependencies to secure versions
       - Apply security patches and configuration fixes
       - Add missing security headers and configurations
       - Implement proper input validation where missing
    
    3. Performance Issues:
       - Optimize slow database queries
       - Add appropriate caching configurations
       - Tune connection pool settings
       - Apply performance best practices
    
    4. Configuration Issues:
       - Fix common configuration mismatches
       - Update deprecated property names
       - Apply environment-specific optimizations
       - Validate and correct resource configurations

validation_workflows:
  iterative_validation:
    sequence:
      - build_validation
      - unit_test_execution
      - security_quick_scan
      - integration_testing
      - comprehensive_security_scan
      - performance_validation
      - final_compliance_check
    
    failure_handling:
      - Immediate stop on critical failures
      - Automatic retry for transient issues
      - Detailed reporting of all failures
      - Suggested remediation actions
  
  quality_reporting:
    metrics_tracked:
      - test_coverage_percentage
      - vulnerability_count_by_severity
      - performance_benchmarks
      - code_quality_scores
      - compliance_status
    
    report_formats:
      - detailed_json_report
      - executive_summary
      - trend_analysis
      - remediation_recommendations

success_criteria:
  mandatory_requirements:
    - All tests pass successfully
    - Test coverage >= 80%
    - Zero critical security vulnerabilities
    - Application starts within time limit
    - All endpoints respond correctly
  
  quality_thresholds:
    - Build time < 10 minutes
    - Startup time < 30 seconds
    - Memory usage within 20% of baseline
    - Response time < 200ms for standard operations
    - Zero critical or high severity code smells
```

## Sample Configuration Files

### OpenRewrite Custom Recipe Configuration (`openrewrite/custom-recipes/spring-modernization.yml`)
```yaml
type: specs.openrewrite.org/v1beta/recipe
name: com.company.spring.SpringModernizationSuite
displayName: Complete Spring Modernization Suite
description: Comprehensive recipe for modernizing Spring Framework applications
tags:
  - spring
  - modernization
  - best-practices

recipeList:
  # Core Spring upgrades
  - org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_2
  - org.openrewrite.java.spring.framework.UpgradeSpringFramework_6_1
  - org.openrewrite.java.spring.security6.UpgradeSpringSecurity_6_2
  
  # Dependency injection modernization
  - org.openrewrite.java.spring.NoFieldInjection
  - org.openrewrite.java.spring.ImplicitWebAnnotationNames
  
  # Configuration modernization
  - org.openrewrite.java.spring.xml2java.XmlBeanDefinitionToJavaBean
  - org.openrewrite.java.spring.boot2.SpringBootProperties_2_4
  
  # Security modernization
  - org.openrewrite.java.spring.security5.UpdateArgon2PasswordEncoder
  - org.openrewrite.java.spring.security6.RequireExplicitSavingOfSecurityContextRepository
  
  # Custom modernization recipes
  - com.company.spring.ConstructorInjectionPattern
  - com.company.spring.ModernExceptionHandling
  - com.company.spring.ResponseEntityPattern
  - com.company.spring.ConfigurationClassPattern

---
type: specs.openrewrite.org/v1beta/recipe
name: com.company.spring.ConstructorInjectionPattern
displayName: Convert to Constructor Injection
description: Convert field injection to constructor injection with final fields

recipeList:
  - org.openrewrite.java.spring.NoFieldInjection
  - org.openrewrite.java.ChangeType:
      oldFullyQualifiedTypeName: "org.springframework.beans.factory.annotation.Autowired"
      newFullyQualifiedTypeName: "lombok.RequiredArgsConstructor"
      ignoreDefinition: true

---
type: specs.openrewrite.org/v1beta/recipe
name: com.company.spring.ModernExceptionHandling
displayName: Implement Modern Exception Handling
description: Add proper exception handling with @ControllerAdvice

recipeList:
  - org.openrewrite.java.AddAnnotation:
      annotationPattern: "@org.springframework.web.bind.annotation.ControllerAdvice"
      onlyIfReferenced: false
  - org.openrewrite.java.AddAnnotation:
      annotationPattern: "@org.springframework.web.bind.annotation.ExceptionHandler"
      onlyIfReferenced: false

---
type: specs.openrewrite.org/v1beta/recipe
name: com.company.spring.ResponseEntityPattern
displayName: Use ResponseEntity Pattern
description: Convert return types to ResponseEntity for consistent API responses

recipeList:
  - org.openrewrite.java.ChangeMethodReturnType:
      methodPattern: "*..* *Controller.*(..)";
      newReturnType: "org.springframework.http.ResponseEntity"
```

### Quality Gates Configuration (`rules/quality-gates.yml`)
```yaml
quality_gates:
  project_info:
    name: "Spring Framework Upgrade Quality Gates"
    version: "2.0"
    description: "Comprehensive quality standards for Spring upgrades"
  
  build_requirements:
    compilation:
      success_required: true
      warning_threshold: 0
      max_build_time_minutes: 10
    
    packaging:
      jar_creation_required: true
      test_jar_creation: true
      source_jar_creation: true
      javadoc_generation: false
  
  testing_requirements:
    coverage:
      min_line_coverage: 80
      min_branch_coverage: 75
      exclude_patterns:
        - "**/*Configuration.java"
        - "**/*Application.java"
        - "**/dto/**"
        - "**/entity/**"
    
    test_execution:
      unit_tests_required: true
      integration_tests_required: true
      max_test_execution_time_minutes: 15
      fail_fast_on_first_failure: false
    
    test_categories:
      unit:
        pattern: "**/*Test.java"
        required: true
        min_count: 10
      
      integration:
        pattern: "**/*IT.java"
        required: true
        min_count: 3
      
      security:
        pattern: "**/*SecurityTest.java"
        required: false
        min_count: 0
  
  security_requirements:
    vulnerability_scanning:
      tools:
        - name: "OWASP Dependency Check"
          required: true
          config_file: "dependency-check-config.xml"
        
        - name: "Snyk"
          required: false
          api_token_env: "SNYK_TOKEN"
        
        - name: "GitHub Security Advisory"
          required: true
          integration: "github_actions"
    
    vulnerability_thresholds:
      critical: 0
      high: 5
      medium: 20
      low: 100
    
    security_validations:
      - name: "JWT Token Validation"
        endpoint: "/api/auth/validate"
        expected_status: 200
      
      - name: "Unauthorized Access Prevention"
        endpoint: "/api/admin/users"
        headers: {}
        expected_status: 401
      
      - name: "CORS Configuration"
        endpoint: "/api/products"
        origin: "https://malicious-site.com"
        expected_cors_header: false
  
  performance_requirements:
    startup_performance:
      max_startup_time_seconds: 30
      max_memory_mb: 512
      monitor_gc_activity: true
    
    runtime_performance:
      endpoints:
        - path: "/api/health"
          max_response_time_ms: 100
          load_test_users: 10
        
        - path: "/api/products"
          max_response_time_ms: 200
          load_test_users: 50
        
        - path: "/api/orders"
          max_response_time_ms: 500
          load_test_users: 20
    
    resource_utilization:
      max_cpu_usage_percent: 80
      max_memory_usage_mb: 1024
      max_database_connections: 20
      max_file_descriptors: 1000
  
  code_quality_requirements:
    sonarqube:
      quality_gate: "Sonar way"
      required_metrics:
        - name: "Coverage"
          threshold: 80
          operator: "GT"
        
        - name: "Duplicated Lines (%)"
          threshold: 3
          operator: "LT"
        
        - name: "Maintainability Rating"
          threshold: "A"
          operator: "EQ"
        
        - name: "Reliability Rating"
          threshold: "A"
          operator: "EQ"
        
        - name: "Security Rating"
          threshold: "A"
          operator: "EQ"
    
    code_standards:
      formatting:
        tool: "google-java-format"
        config_file: ".google-java-format.xml"
      
      static_analysis:
        tools:
          - "SpotBugs"
          - "PMD"
          - "Checkstyle"
        
        max_violations:
          critical: 0
          major: 10
          minor: 50
  
  documentation_requirements:
    api_documentation:
      swagger_ui_required: true
      openapi_spec_required: true
      endpoint_coverage: 100
    
    technical_documentation:
      readme_updated: true
      architecture_diagrams: true
      deployment_guide: true
      api_usage_examples: true
    
    upgrade_documentation:
      change_log_required: true
      migration_guide_required: true
      breaking_changes_documented: true
      rollback_procedures_documented: true

notification_settings:
  success_notifications:
    - type: "email"
      recipients: ["dev-team@company.com"]
      template: "upgrade_success_template"
    
    - type: "slack"
      channel: "#spring-upgrades"
      webhook_url_env: "SLACK_WEBHOOK_URL"
  
  failure_notifications:
    - type: "email"
      recipients: ["dev-team@company.com", "devops@company.com"]
      template: "upgrade_failure_template"
      include_logs: true
    
    - type: "pagerduty"
      service_key_env: "PAGERDUTY_SERVICE_KEY"
      severity: "high"

reporting_configuration:
  report_formats:
    - "html"
    - "json"
    - "junit_xml"
  
  report_sections:
    - "executive_summary"
    - "detailed_metrics"
    - "test_results"
    - "security_findings"
    - "performance_analysis"
    - "code_quality_assessment"
    - "recommendations"
  
  archive_settings:
    retention_days: 90
    compression: true
    cloud_storage: "s3://upgrade-reports-bucket"
```

### Example Project Metadata Output (`artifacts/metadata-example.json`)
```json
{
  "project": {
    "name": "e-commerce-api",
    "description": "Spring Boot REST API for e-commerce platform",
    "version": "2.1.0",
    "spring_boot_version": "3.2.0",
    "java_version": "17",
    "build_tool": "maven",
    "packaging": "jar",
    "structure": {
      "total_java_files": 127,
      "controller_files": 8,
      "service_files": 15,
      "repository_files": 12,
      "entity_files": 18,
      "configuration_files": 6,
      "test_files": 68,
      "total_lines_of_code": 15420
    },
    "dependencies": {
      "spring_framework": "6.1.0",
      "spring_boot": "3.2.0",
      "spring_security": "6.2.0",
      "spring_data": "3.2.0",
      "hibernate": "6.4.0",
      "jackson": "2.16.0",
      "junit": "5.10.0",
      "mockito": "5.7.0",
      "testcontainers": "1.19.0"
    },
    "configuration": {
      "profiles": ["dev", "test", "prod"],
      "datasource": {
        "type": "postgresql",
        "driver": "org.postgresql.Driver",
        "pool": "HikariCP",
        "max_pool_size": 20
      },
      "security": {
        "authentication": "jwt",
        "authorization": "role_based",
        "cors_enabled": true,
        "csrf_enabled": false
      },
      "caching": {
        "provider": "redis",
        "ttl_seconds": 3600,
        "max_entries": 10000
      },
      "monitoring": {
        "actuator_enabled": true,
        "metrics_enabled": true,
        "health_checks": ["db", "redis", "disk"]
      }
    },
    "readme": {
      "has_readme": true,
      "sections": [
        "Project Description",
        "Getting Started",
        "API Documentation",
        "Development Setup",
        "Deployment Guide",
        "Contributing Guidelines"
      ],
      "last_updated": "2024-01-10T10:30:00Z"
    }
  },
  "upgrade": {
    "timestamp": "2024-01-15T16:15:00Z",
    "from_version": "5.3.21",
    "to_version": "6.1.0",
    "duration_seconds": 7245,
    "iterations_completed": 2,
    "status": "completed",
    "changes": [
      {
        "category": "dependency_update",
        "description": "Updated Spring Framework from 5.3.21 to 6.1.0",
        "files_affected": ["pom.xml"],
        "impact": "major"
      },
      {
        "category": "api_modernization",
        "description": "Migrated javax.* packages to jakarta.*",
        "files_affected": [
          "src/main/java/com/company/config/SecurityConfig.java",
          "src/main/java/com/company/entity/Product.java",
          "src/main/java/com/company/entity/Order.java"
        ],
        "impact": "high"
      },
      {
        "category": "injection_pattern",
        "description": "Converted field injection to constructor injection",
        "files_affected": [
          "src/main/java/com/company/service/ProductService.java",
          "src/main/java/com/company/service/OrderService.java",
          "src/main/java/com/company/controller/ProductController.java"
        ],
        "impact": "medium"
      },
      {
        "category": "test_enhancement",
        "description": "Added 23 new unit tests and 8 integration tests",
        "files_affected": [
          "src/test/java/com/company/service/ProductServiceTest.java",
          "src/test/java/com/company/integration/OrderIntegrationTest.java"
        ],
        "impact": "low"
      }
    ],
    "metrics": {
      "test_coverage_before": 65.2,
      "test_coverage_after": 84.7,
      "vulnerabilities_before": 3,
      "vulnerabilities_after": 0,
      "build_time_before": 145,
      "build_time_after": 132,
      "startup_time_before": 18.5,
      "startup_time_after": 12.3
    }
  },
  "quality_assessment": {
    "code_quality": {
      "sonar_quality_gate": "passed",
      "maintainability_rating": "A",
      "reliability_rating": "A",
      "security_rating": "A",
      "technical_debt_minutes": 245,
      "code_smells": 12,
      "duplicated_lines_percent": 1.8
    },
    "security_assessment": {
      "scan_timestamp": "2024-01-15T16:10:00Z",
      "tools_used": ["OWASP Dependency Check", "Snyk", "GitHub Security Advisory"],
      "vulnerabilities": {
        "critical": 0,
        "high": 0,
        "medium": 2,
        "low": 5
      },
      "security_hotspots": 0,
      "compliance_status": "compliant"
    },
    "performance_metrics": {
      "startup_time_seconds": 12.3,
      "memory_usage_mb": 387,
      "gc_time_percent": 2.1,
      "endpoint_response_times": {
        "/api/health": 23,
        "/api/products": 156,
        "/api/orders": 234,
        "/api/users/profile": 89
      }
    }
  },
  "architecture": {
    "patterns_identified": [
      "MVC (Model-View-Controller)",
      "Repository Pattern",
      "Service Layer Pattern",
      "Dependency Injection",
      "RESTful API Design"
    ],
    "components": {
      "controllers": 8,
      "services": 15,
      "repositories": 12,
      "entities": 18,
      "configurations": 6,
      "filters": 3,
      "interceptors": 2
    },
    "external_integrations": [
      "PostgreSQL Database",
      "Redis Cache",
      "Payment Gateway API",
      "Email Service API",
      "Inventory Management System"
    ]
  }
}
```

This comprehensive configuration provides all the necessary components for an enterprise-grade Spring Framework upgrade system with full documentation generation capabilities.