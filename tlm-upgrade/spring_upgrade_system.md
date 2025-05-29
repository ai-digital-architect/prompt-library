# Spring Framework Upgrade System with GitHub Copilot Agent Mode

## Overview
This system provides a comprehensive approach to upgrade Spring Framework projects using GitHub Copilot's agent mode with OpenRewrite recipes, automated testing, security scanning, and iterative improvement until all objectives are met.

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Planning      │───▶│   Execution      │───▶│   Validation    │
│   Agent         │    │   Agent          │    │   Agent         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Generate Plan   │    │ Apply Changes    │    │ Run Tests &     │
│ Analyze Project │    │ OpenRewrite      │    │ Security Scan   │
│ Identify Issues │    │ Best Practices   │    │ Coverage Check  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                 │
                                 ▼
                    ┌──────────────────┐
                    │ Iterative Loop   │
                    │ Until Success    │
                    └──────────────────┘
```

## File Structure

```
spring-upgrade-system/
├── .github/
│   └── copilot/
│       ├── agents/
│       │   ├── spring-upgrade-planner.yml
│       │   ├── spring-upgrade-executor.yml
│       │   └── spring-upgrade-validator.yml
│       └── workflows/
│           └── spring-upgrade.yml
├── upgrade-config/
│   ├── openrewrite/
│   │   ├── rewrite.yml
│   │   └── custom-recipes/
│   │       └── spring-modernization.yml
│   ├── rules/
│   │   ├── upgrade-rules.json
│   │   └── quality-gates.yml
│   └── templates/
│       ├── test-templates/
│       └── code-patterns/
├── scripts/
│   ├── upgrade-orchestrator.sh
│   ├── validate-upgrade.sh
│   └── generate-report.sh
└── docs/
    ├── upgrade-guide.md
    └── troubleshooting.md
```

## Core Components

### 1. GitHub Copilot Agent Configurations

#### Planning Agent (`spring-upgrade-planner.yml`)
```yaml
name: spring-upgrade-planner
description: Analyzes Spring projects and creates upgrade plans
version: 1.0

capabilities:
  - project-analysis
  - dependency-mapping
  - risk-assessment
  - plan-generation

instructions: |
  You are a Spring Framework upgrade planning specialist. Your role is to:
  
  1. **Project Analysis**:
     - Scan the project structure and identify current Spring version
     - Map all dependencies and their compatibility
     - Identify deprecated APIs and patterns
     - Assess custom configurations and beans
  
  2. **Risk Assessment**:
     - Identify breaking changes between versions
     - Flag potentially problematic code patterns
     - Estimate upgrade complexity and timeline
  
  3. **Plan Generation**:
     - Create step-by-step upgrade plan
     - Prioritize changes by risk and impact
     - Generate OpenRewrite recipe configurations
     - Define rollback strategies

tools:
  - file-analysis
  - dependency-scanner
  - version-comparator
  - report-generator

context_files:
  - "pom.xml"
  - "build.gradle"
  - "src/**/*.java"
  - "src/**/*.xml"
  - "application.properties"
  - "application.yml"
```

#### Execution Agent (`spring-upgrade-executor.yml`)
```yaml
name: spring-upgrade-executor
description: Executes Spring upgrade tasks and applies best practices
version: 1.0

capabilities:
  - code-transformation
  - dependency-updates
  - pattern-modernization
  - test-generation

instructions: |
  You are a Spring Framework upgrade execution specialist. Your role is to:
  
  1. **Code Transformation**:
     - Apply OpenRewrite recipes for version upgrades
     - Update deprecated API usage
     - Modernize configuration patterns
     - Apply Spring best practices
  
  2. **Dependency Management**:
     - Update Spring dependencies to target version
     - Resolve version conflicts
     - Add missing dependencies for new features
  
  3. **Pattern Modernization**:
     - Convert XML config to Java config where beneficial
     - Apply modern Spring patterns (e.g., @Configuration, @ComponentScan)
     - Update security configurations
     - Modernize data access patterns
  
  4. **Test Enhancement**:
     - Generate missing tests to achieve 80%+ coverage
     - Update test configurations for new Spring version
     - Add integration tests for upgraded components

tools:
  - openrewrite-runner
  - code-generator
  - test-generator
  - dependency-updater

best_practices:
  - Use constructor injection over field injection
  - Prefer Java configuration over XML
  - Apply proper exception handling patterns
  - Use Spring Boot auto-configuration where possible
  - Implement proper security practices
```

#### Validation Agent (`spring-upgrade-validator.yml`)
```yaml
name: spring-upgrade-validator
description: Validates upgrade success and ensures quality gates
version: 1.0

capabilities:
  - test-execution
  - coverage-analysis
  - security-scanning
  - quality-assessment

instructions: |
  You are a Spring Framework upgrade validation specialist. Your role is to:
  
  1. **Test Execution**:
     - Run all unit and integration tests
     - Verify application startup and basic functionality
     - Check for runtime errors and warnings
  
  2. **Quality Gates**:
     - Ensure test coverage >= 80%
     - Verify no critical security vulnerabilities
     - Check code quality metrics
     - Validate performance hasn't degraded
  
  3. **Iterative Improvement**:
     - Identify and fix failing tests
     - Address security vulnerabilities
     - Improve test coverage where needed
     - Continue until all objectives are met
  
  4. **Reporting**:
     - Generate comprehensive upgrade report
     - Document changes made and rationale
     - Provide recommendations for future maintenance

tools:
  - test-runner
  - coverage-analyzer
  - security-scanner
  - quality-checker

quality_gates:
  test_coverage_threshold: 80
  max_critical_vulnerabilities: 0
  max_high_vulnerabilities: 5
  build_success_required: true
```

### 2. OpenRewrite Configuration

#### Main Configuration (`rewrite.yml`)
```yaml
type: specs.openrewrite.org/v1beta/recipe
name: com.company.spring.upgrade.SpringUpgradeRecipe
displayName: Complete Spring Framework Upgrade
description: Comprehensive recipe for upgrading Spring Framework projects

recipeList:
  # Core Spring upgrades
  - org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_2
  - org.openrewrite.java.spring.framework.UpgradeSpringFramework_6_1
  
  # Security upgrades
  - org.openrewrite.java.spring.security6.UpgradeSpringSecurity_6_2
  
  # Custom recipes
  - com.company.spring.upgrade.ModernizeConfigurations
  - com.company.spring.upgrade.ApplyBestPractices
  - com.company.spring.upgrade.EnhanceTestCoverage

---
type: specs.openrewrite.org/v1beta/recipe
name: com.company.spring.upgrade.ModernizeConfigurations
displayName: Modernize Spring Configurations
description: Convert legacy patterns to modern Spring practices

recipeList:
  # XML to Java Config
  - org.openrewrite.java.spring.xml2java.XmlBeanDefinitionToJavaBean
  
  # Component scanning improvements
  - org.openrewrite.java.spring.ImplicitWebAnnotationNames
  
  # Property binding modernization
  - org.openrewrite.java.spring.boot2.SpringBootProperties_2_4
```

#### Custom Recipe (`custom-recipes/spring-modernization.yml`)
```yaml
type: specs.openrewrite.org/v1beta/recipe
name: com.company.spring.upgrade.ApplyBestPractices
displayName: Apply Spring Best Practices
description: Apply modern Spring development patterns and practices

recipeList:
  - name: Constructor Injection Pattern
    preconditions:
      - java.FindAnnotations:
          annotationPattern: "@org.springframework.beans.factory.annotation.Autowired"
    recipe:
      - java.ChangeMethodTargetToStatic:
          methodPattern: "*..* *(..)";
          fullyQualifiedTargetTypeName: "ConstructorBasedInjection"

  - name: Configuration Class Patterns
    recipe:
      - java.AddAnnotation:
          annotationPattern: "@org.springframework.context.annotation.Configuration"
          onlyIfReferenced: false

  - name: Modern Exception Handling
    recipe:
      - java.ReplaceMethodInvocations:
          oldMethodPattern: "*.printStackTrace()"
          newMethodPattern: "log.error(\"Error occurred\", {})"
```

### 3. Upgrade Rules Configuration

#### Upgrade Rules (`rules/upgrade-rules.json`)
```json
{
  "upgrade_rules": {
    "version_compatibility": {
      "spring_framework": {
        "min_java_version": "17",
        "supported_versions": ["6.0.x", "6.1.x"],
        "breaking_changes": [
          {
            "version": "6.0.0",
            "changes": [
              "javax.* packages migrated to jakarta.*",
              "Minimum Java 17 required",
              "Spring Web MVC changes"
            ]
          }
        ]
      }
    },
    "code_patterns": {
      "deprecated_replacements": {
        "WebMvcConfigurerAdapter": "WebMvcConfigurer",
        "@EnableWebMvcSecurity": "@EnableWebSecurity",
        "HttpSecurity.authorizeRequests()": "HttpSecurity.authorizeHttpRequests()"
      }
    },
    "test_requirements": {
      "min_coverage": 80,
      "required_test_types": ["unit", "integration", "security"],
      "test_patterns": {
        "@SpringBootTest": "Use for integration tests",
        "@WebMvcTest": "Use for web layer tests",
        "@DataJpaTest": "Use for JPA repository tests"
      }
    }
  }
}
```

#### Quality Gates (`rules/quality-gates.yml`)
```yaml
quality_gates:
  build:
    compilation_success: true
    test_execution_success: true
    
  testing:
    min_test_coverage: 80
    max_test_execution_time: 300 # seconds
    required_test_categories:
      - unit
      - integration
      - security
    
  security:
    max_critical_vulnerabilities: 0
    max_high_vulnerabilities: 5
    security_scan_tools:
      - "OWASP Dependency Check"
      - "Snyk"
      - "GitHub Security Advisory"
    
  code_quality:
    max_code_smells: 100
    max_duplicated_lines: 5 # percentage
    maintainability_rating: "A"
    
  performance:
    max_startup_time: 30 # seconds
    max_memory_usage_increase: 20 # percentage
```

### 4. Orchestration Scripts

#### Main Orchestrator (`scripts/upgrade-orchestrator.sh`)
```bash
#!/bin/bash

set -e

# Configuration
PROJECT_DIR=${1:-"."}
TARGET_SPRING_VERSION=${2:-"6.1.0"}
MAX_ITERATIONS=${3:-10}
REPORT_DIR="upgrade-reports"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Initialize
mkdir -p "$REPORT_DIR"
ITERATION=1

log "Starting Spring Framework upgrade process..."
log "Target version: $TARGET_SPRING_VERSION"
log "Project directory: $PROJECT_DIR"

# Step 1: Planning Phase
log "Phase 1: Planning and Analysis"
gh copilot agent spring-upgrade-planner \
    --project-dir "$PROJECT_DIR" \
    --target-version "$TARGET_SPRING_VERSION" \
    --output "$REPORT_DIR/upgrade-plan.json"

if [ $? -ne 0 ]; then
    error "Planning phase failed"
    exit 1
fi

# Step 2: Iterative Upgrade Loop
while [ $ITERATION -le $MAX_ITERATIONS ]; do
    log "Iteration $ITERATION: Executing upgrade tasks"
    
    # Execute upgrade
    gh copilot agent spring-upgrade-executor \
        --project-dir "$PROJECT_DIR" \
        --plan "$REPORT_DIR/upgrade-plan.json" \
        --iteration $ITERATION
    
    # Validate results
    log "Validating upgrade results..."
    gh copilot agent spring-upgrade-validator \
        --project-dir "$PROJECT_DIR" \
        --report-dir "$REPORT_DIR/iteration-$ITERATION"
    
    VALIDATION_RESULT=$?
    
    if [ $VALIDATION_RESULT -eq 0 ]; then
        success "All objectives met! Upgrade completed successfully."
        break
    else
        warn "Validation failed. Issues found in iteration $ITERATION"
        
        # Check if we've reached max iterations
        if [ $ITERATION -eq $MAX_ITERATIONS ]; then
            error "Maximum iterations reached. Upgrade incomplete."
            exit 1
        fi
        
        log "Preparing for next iteration..."
        ((ITERATION++))
    fi
done

# Generate final report
log "Generating final upgrade report..."
./scripts/generate-report.sh "$REPORT_DIR" "$PROJECT_DIR"

success "Spring Framework upgrade process completed!"
```

#### Validation Script (`scripts/validate-upgrade.sh`)
```bash
#!/bin/bash

set -e

PROJECT_DIR=${1:-"."}
REPORT_DIR=${2:-"upgrade-reports"}

log() {
    echo -e "\033[0;34m[$(date +'%Y-%m-%d %H:%M:%S')] $1\033[0m"
}

error() {
    echo -e "\033[0;31m[ERROR] $1\033[0m"
}

success() {
    echo -e "\033[0;32m[SUCCESS] $1\033[0m"
}

# Validation functions
validate_build() {
    log "Validating build..."
    cd "$PROJECT_DIR"
    
    if [ -f "pom.xml" ]; then
        mvn clean compile
    elif [ -f "build.gradle" ]; then
        ./gradlew build
    else
        error "No recognized build file found"
        return 1
    fi
}

validate_tests() {
    log "Running tests..."
    cd "$PROJECT_DIR"
    
    if [ -f "pom.xml" ]; then
        mvn test
    elif [ -f "build.gradle" ]; then
        ./gradlew test
    fi
}

check_test_coverage() {
    log "Checking test coverage..."
    cd "$PROJECT_DIR"
    
    if [ -f "pom.xml" ]; then
        mvn jacoco:report
        COVERAGE=$(grep -o 'Total.*\([0-9]\+\)%' target/site/jacoco/index.html | grep -o '[0-9]\+' | tail -1)
    elif [ -f "build.gradle" ]; then
        ./gradlew jacocoTestReport
        COVERAGE=$(grep -o 'Total.*\([0-9]\+\)%' build/reports/jacoco/test/html/index.html | grep -o '[0-9]\+' | tail -1)
    fi
    
    if [ "$COVERAGE" -lt 80 ]; then
        error "Test coverage ($COVERAGE%) below threshold (80%)"
        return 1
    else
        success "Test coverage: $COVERAGE%"
    fi
}

check_security_vulnerabilities() {
    log "Scanning for security vulnerabilities..."
    cd "$PROJECT_DIR"
    
    # OWASP Dependency Check
    if [ -f "pom.xml" ]; then
        mvn org.owasp:dependency-check-maven:check
    elif [ -f "build.gradle" ]; then
        ./gradlew dependencyCheckAnalyze
    fi
    
    # Check results
    if [ -f "target/dependency-check-report.html" ] || [ -f "build/reports/dependency-check-report.html" ]; then
        CRITICAL_VULNS=$(grep -c "CRITICAL" target/dependency-check-report.html 2>/dev/null || grep -c "CRITICAL" build/reports/dependency-check-report.html 2>/dev/null || echo "0")
        
        if [ "$CRITICAL_VULNS" -gt 0 ]; then
            error "Found $CRITICAL_VULNS critical vulnerabilities"
            return 1
        else
            success "No critical vulnerabilities found"
        fi
    fi
}

validate_application_startup() {
    log "Validating application startup..."
    cd "$PROJECT_DIR"
    
    # Start application in background
    if [ -f "pom.xml" ]; then
        timeout 60 mvn spring-boot:run > startup.log 2>&1 &
        APP_PID=$!
    elif [ -f "build.gradle" ]; then
        timeout 60 ./gradlew bootRun > startup.log 2>&1 &
        APP_PID=$!
    fi
    
    # Wait for startup
    sleep 30
    
    # Check if application started successfully
    if grep -q "Started.*Application" startup.log; then
        success "Application started successfully"
        kill $APP_PID 2>/dev/null || true
        return 0
    else
        error "Application failed to start"
        kill $APP_PID 2>/dev/null || true
        return 1
    fi
}

# Main validation flow
VALIDATION_PASSED=true

validate_build || VALIDATION_PASSED=false
validate_tests || VALIDATION_PASSED=false
check_test_coverage || VALIDATION_PASSED=false
check_security_vulnerabilities || VALIDATION_PASSED=false
validate_application_startup || VALIDATION_PASSED=false

if [ "$VALIDATION_PASSED" = true ]; then
    success "All validations passed!"
    exit 0
else
    error "Some validations failed"
    exit 1
fi
```

### 5. GitHub Actions Workflow

#### Workflow Configuration (`.github/workflows/spring-upgrade.yml`)
```yaml
name: Spring Framework Upgrade

on:
  workflow_dispatch:
    inputs:
      target_version:
        description: 'Target Spring Framework version'
        required: true
        default: '6.1.0'
      project_path:
        description: 'Project path (relative to repository root)'
        required: false
        default: '.'

jobs:
  spring-upgrade:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    
    permissions:
      contents: write
      pull-requests: write
      security-events: write
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: |
          ~/.m2/repository
          ~/.gradle/caches
        key: ${{ runner.os }}-deps-${{ hashFiles('**/pom.xml', '**/build.gradle*') }}
    
    - name: Install OpenRewrite CLI
      run: |
        curl -o rewrite.jar https://github.com/openrewrite/rewrite/releases/latest/download/rewrite.jar
        chmod +x rewrite.jar
    
    - name: Set up GitHub Copilot CLI
      run: |
        gh extension install github/gh-copilot
        gh auth login --with-token <<< "${{ secrets.GITHUB_TOKEN }}"
    
    - name: Create upgrade branch
      run: |
        BRANCH_NAME="spring-upgrade-$(date +%Y%m%d-%H%M%S)"
        git checkout -b "$BRANCH_NAME"
        echo "UPGRADE_BRANCH=$BRANCH_NAME" >> $GITHUB_ENV
    
    - name: Run Spring upgrade orchestrator
      run: |
        chmod +x scripts/upgrade-orchestrator.sh
        ./scripts/upgrade-orchestrator.sh "${{ github.event.inputs.project_path }}" "${{ github.event.inputs.target_version }}"
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Commit changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        
        if git diff --staged --quiet; then
          git add .
        fi
        
        if ! git diff --cached --quiet; then
          git commit -m "feat: upgrade Spring Framework to ${{ github.event.inputs.target_version }}
          
          - Applied OpenRewrite recipes for version upgrade
          - Updated dependencies and configurations
          - Applied Spring best practices and patterns
          - Enhanced test coverage to meet 80% threshold
          - Resolved security vulnerabilities
          - Ensured all tests pass
          
          Generated by automated Spring upgrade process"
        fi
    
    - name: Push changes
      run: |
        git push origin "$UPGRADE_BRANCH"
    
    - name: Create Pull Request
      run: |
        gh pr create \
          --title "Spring Framework Upgrade to ${{ github.event.inputs.target_version }}" \
          --body-file upgrade-reports/final-report.md \
          --base main \
          --head "$UPGRADE_BRANCH" \
          --label "enhancement,spring-upgrade,automated"
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Upload upgrade reports
      uses: actions/upload-artifact@v3
      with:
        name: spring-upgrade-reports
        path: upgrade-reports/
        retention-days: 30
```

## Usage Instructions

### 1. Setup
```bash
# Clone and set up the upgrade system
git clone <your-repo>
cd your-spring-project

# Copy upgrade system files
cp -r spring-upgrade-system/* .

# Make scripts executable
chmod +x scripts/*.sh

# Install dependencies
gh extension install github/gh-copilot
```

### 2. Configuration
```bash
# Edit upgrade rules for your project
vim upgrade-config/rules/upgrade-rules.json

# Customize OpenRewrite recipes
vim upgrade-config/openrewrite/rewrite.yml

# Set quality gates
vim upgrade-config/rules/quality-gates.yml
```

### 3. Execution

#### Automated (via GitHub Actions)
1. Go to Actions tab in your repository
2. Select "Spring Framework Upgrade" workflow
3. Click "Run workflow"
4. Specify target Spring version
5. Monitor progress and review generated PR

#### Manual (local execution)
```bash
# Run the complete upgrade process
./scripts/upgrade-orchestrator.sh . 6.1.0

# Or run individual phases
gh copilot agent spring-upgrade-planner --project-dir .
gh copilot agent spring-upgrade-executor --project-dir .
gh copilot agent spring-upgrade-validator --project-dir .
```

## Key Features

### Automated Planning
- Analyzes current project structure and dependencies
- Identifies compatibility issues and breaking changes
- Generates step-by-step upgrade plan with risk assessment

### Intelligent Execution
- Applies OpenRewrite recipes for automated code transformation
- Updates dependencies with conflict resolution
- Modernizes configuration patterns and applies best practices
- Generates missing tests to achieve coverage goals

### Comprehensive Validation
- Runs all tests and ensures build success
- Validates test coverage meets 80% threshold
- Scans for security vulnerabilities
- Performs application startup validation

### Iterative Improvement
- Continues making improvements until all objectives are met
- Provides detailed reporting at each iteration
- Maintains audit trail of all changes made

### Integration Ready
- GitHub Actions workflow for CI/CD integration
- Pull request automation with detailed reports
- Artifact preservation for audit and rollback

This system provides a complete, automated solution for Spring Framework upgrades that ensures quality, security, and maintainability throughout the process.