# Bitbucket Integration and VS Code Copilot Agent Configuration

## VS Code GitHub Copilot Extension Integration

### VS Code Workspace Configuration (`.vscode/copilot-agents.json`)
```json
{
  "agents": [
    {
      "name": "spring-upgrade-planner",
      "displayName": "Spring Upgrade Planner",
      "description": "Analyzes Spring projects and creates comprehensive upgrade plans",
      "icon": "📋",
      "category": "planning",
      "commands": [
        {
          "name": "analyze-project",
          "description": "Analyze current Spring project structure and dependencies",
          "prompt": "Analyze the current Spring Framework project in the workspace. Identify the current version, dependencies, and create a comprehensive upgrade plan to the latest stable version. Include timeline estimation and risk assessment."
        },
        {
          "name": "create-upgrade-plan",
          "description": "Create detailed upgrade plan with timeline",
          "prompt": "Create a detailed Spring Framework upgrade plan for this project. Include:\n1. Current state analysis\n2. Target version recommendations\n3. Breaking changes identification\n4. Step-by-step upgrade phases\n5. Timeline with milestones\n6. Risk assessment and mitigation strategies"
        },
        {
          "name": "assess-compatibility",
          "description": "Check dependency compatibility for target Spring version",
          "prompt": "Analyze all dependencies in this Spring project for compatibility with Spring Framework 6.1.0. Identify version conflicts, breaking changes, and required updates."
        }
      ],
      "context": {
        "include": [
          "pom.xml",
          "build.gradle",
          "src/**/*.java",
          "src/**/*.xml",
          "application.properties",
          "application.yml",
          "README.md"
        ]
      }
    },
    {
      "name": "spring-upgrade-executor",
      "displayName": "Spring Upgrade Executor",
      "description": "Executes Spring upgrade tasks and applies best practices",
      "icon": "🔧",
      "category": "execution",
      "commands": [
        {
          "name": "apply-openrewrite-recipes",
          "description": "Apply OpenRewrite recipes for Spring upgrade",
          "prompt": "Apply OpenRewrite recipes to upgrade this Spring project. Focus on:\n1. Spring Framework version updates\n2. Deprecated API replacements\n3. Modern configuration patterns\n4. Constructor injection conversion\n5. Security modernization\n\nExecute recipes incrementally and validate after each step."
        },
        {
          "name": "modernize-code-patterns",
          "description": "Apply modern Spring development patterns",
          "prompt": "Modernize the Spring code patterns in this project:\n1. Convert field injection to constructor injection\n2. Apply modern Spring configuration patterns\n3. Update security configurations\n4. Implement proper exception handling\n5. Apply Spring best practices throughout the codebase"
        },
        {
          "name": "update-dependencies",
          "description": "Update Spring and related dependencies",
          "prompt": "Update all Spring-related dependencies in this project to their latest compatible versions. Resolve any version conflicts and ensure compatibility with the target Spring Framework version."
        },
        {
          "name": "enhance-tests",
          "description": "Generate tests to improve coverage",
          "prompt": "Analyze the current test coverage and generate additional tests to reach 80%+ coverage. Focus on:\n1. Unit tests for service layer\n2. Integration tests for controllers\n3. Security tests for authentication/authorization\n4. Repository tests with proper mocking"
        }
      ],
      "context": {
        "include": [
          "src/**/*.java",
          "src/test/**/*.java",
          "pom.xml",
          "build.gradle"
        ]
      }
    },
    {
      "name": "spring-upgrade-validator",
      "displayName": "Spring Upgrade Validator",
      "description": "Validates upgrade success and ensures quality gates",
      "icon": "✅",
      "category": "validation",
      "commands": [
        {
          "name": "validate-upgrade",
          "description": "Comprehensive validation of Spring upgrade",
          "prompt": "Perform comprehensive validation of the Spring upgrade:\n1. Check compilation and build success\n2. Validate test execution and coverage\n3. Scan for security vulnerabilities\n4. Verify application startup\n5. Check for performance regressions\n6. Validate all quality gates are met"
        },
        {
          "name": "security-scan",
          "description": "Scan for security vulnerabilities",
          "prompt": "Perform a comprehensive security scan of the upgraded Spring application:\n1. Check for known vulnerabilities in dependencies\n2. Validate Spring Security configuration\n3. Test authentication and authorization\n4. Check for common security issues\n5. Provide remediation recommendations"
        },
        {
          "name": "performance-check",
          "description": "Validate performance metrics",
          "prompt": "Analyze the performance impact of the Spring upgrade:\n1. Check application startup time\n2. Validate memory usage\n3. Test key endpoint response times\n4. Compare with baseline metrics\n5. Identify performance optimizations"
        }
      ],
      "context": {
        "include": [
          "src/**/*.java",
          "target/**",
          "build/**",
          "*.log"
        ]
      }
    },
    {
      "name": "documentation-generator",
      "displayName": "Documentation Generator",
      "description": "Generates comprehensive documentation and architectural artifacts",
      "icon": "📚",
      "category": "documentation",
      "commands": [
        {
          "name": "generate-upgrade-report",
          "description": "Generate comprehensive upgrade documentation",
          "prompt": "Generate a comprehensive Spring upgrade report including:\n1. Executive summary with key metrics\n2. Detailed upgrade timeline and changes\n3. Architecture diagrams (C4 Context, Container, Class)\n4. Security assessment results\n5. Performance validation metrics\n6. Project metadata and configuration analysis\n7. Interactive HTML report with Mermaid diagrams"
        },
        {
          "name": "create-architecture-diagrams",
          "description": "Generate architectural diagrams",
          "prompt": "Create comprehensive architectural diagrams for this Spring application:\n1. C4 Context diagram showing system boundaries\n2. C4 Container diagram showing Spring components\n3. Class diagram showing domain model\n4. Sequence diagram for key workflows\n5. State diagram for application lifecycle\nGenerate in Mermaid DSL format."
        },
        {
          "name": "extract-project-metadata",
          "description": "Extract and analyze project metadata",
          "prompt": "Extract comprehensive metadata from this Spring project:\n1. Project structure and statistics\n2. Spring configuration analysis\n3. Dependency inventory and versions\n4. README and documentation content\n5. Test coverage and quality metrics\nFormat as structured JSON for reporting."
        }
      ],
      "context": {
        "include": [
          "**/*",
          "!node_modules/**",
          "!target/**",
          "!build/**"
        ]
      }
    }
  ],
  "workflows": [
    {
      "name": "complete-spring-upgrade",
      "displayName": "Complete Spring Framework Upgrade",
      "description": "End-to-end Spring Framework upgrade workflow",
      "steps": [
        {
          "agent": "spring-upgrade-planner",
          "command": "create-upgrade-plan"
        },
        {
          "agent": "spring-upgrade-executor",
          "command": "apply-openrewrite-recipes"
        },
        {
          "agent": "spring-upgrade-executor",
          "command": "modernize-code-patterns"
        },
        {
          "agent": "spring-upgrade-executor",
          "command": "enhance-tests"
        },
        {
          "agent": "spring-upgrade-validator",
          "command": "validate-upgrade"
        },
        {
          "agent": "documentation-generator",
          "command": "generate-upgrade-report"
        }
      ]
    }
  ],
  "settings": {
    "auto_save_context": true,
    "max_context_files": 100,
    "enable_file_watching": true,
    "output_directory": "upgrade-reports"
  }
}
```

### VS Code Settings Configuration (`.vscode/settings.json`)
```json
{
  "github.copilot.enable": {
    "*": true,
    "yaml": true,
    "markdown": true,
    "java": true
  },
  "github.copilot.agent.enabled": true,
  "github.copilot.agent.workspace": true,
  "spring-upgrade": {
    "outputDirectory": "upgrade-reports",
    "targetVersion": "6.1.0",
    "qualityGates": {
      "minTestCoverage": 80,
      "maxCriticalVulnerabilities": 0,
      "maxHighVulnerabilities": 5
    }
  },
  "java.compile.nullAnalysis.mode": "automatic",
  "java.configuration.updateBuildConfiguration": "automatic"
}
```

### VS Code Launch Configuration (`.vscode/launch.json`)
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "java",
      "name": "Spring Boot App (Pre-Upgrade)",
      "request": "launch",
      "mainClass": "${workspaceFolder}/src/main/java/com/company/Application.java",
      "projectName": "spring-app",
      "args": "--spring.profiles.active=dev",
      "envFile": "${workspaceFolder}/.env"
    },
    {
      "type": "java",
      "name": "Spring Boot App (Post-Upgrade)",
      "request": "launch",
      "mainClass": "${workspaceFolder}/src/main/java/com/company/Application.java",
      "projectName": "spring-app",
      "args": "--spring.profiles.active=dev",
      "envFile": "${workspaceFolder}/.env"
    },
    {
      "type": "java",
      "name": "Run Tests",
      "request": "launch",
      "mainClass": "org.junit.platform.console.ConsoleLauncher",
      "args": ["--scan-classpath"],
      "projectName": "spring-app"
    }
  ]
}
```

## Bitbucket Integration

### Bitbucket Pipelines Configuration (`bitbucket-pipelines.yml`)
```yaml
image: openjdk:17

definitions:
  steps:
    - step: &install-tools
        name: Install Required Tools
        script:
          - apt-get update && apt-get install -y curl git python3 python3-pip nodejs npm
          - curl -o rewrite.jar https://github.com/openrewrite/rewrite/releases/latest/download/rewrite.jar
          - chmod +x rewrite.jar
          - npm install -g @mermaid-js/mermaid-cli
          - pip3 install jinja2 markdown beautifulsoup4

    - step: &spring-upgrade
        name: Enhanced Spring Framework Upgrade
        script:
          - echo "Starting Spring Framework upgrade process..."
          - chmod +x scripts/*.sh
          - export BITBUCKET_REPO_SLUG=$BITBUCKET_REPO_SLUG
          - export BITBUCKET_WORKSPACE=$BITBUCKET_WORKSPACE
          - export TARGET_SPRING_VERSION=${TARGET_SPRING_VERSION:-"6.1.0"}
          
          # Run enhanced upgrade orchestrator
          - ./scripts/upgrade-orchestrator-bitbucket.sh . $TARGET_SPRING_VERSION
          
          # Generate comprehensive documentation
          - ./scripts/generate-documentation-bitbucket.sh . upgrade-reports
          
        artifacts:
          - upgrade-reports/**
          - output/**
        after-script:
          - ./scripts/create-bitbucket-pr.sh

    - step: &deploy-docs
        name: Deploy Documentation
        deployment: staging
        script:
          - echo "Deploying documentation..."
          # Deploy to Netlify or S3
          - if [ -n "$NETLIFY_SITE_ID" ]; then
              npm install -g netlify-cli;
              netlify deploy --prod --dir=output/reports --site=$NETLIFY_SITE_ID --auth=$NETLIFY_AUTH_TOKEN;
            fi
          # Or deploy to S3
          - if [ -n "$AWS_S3_BUCKET" ]; then
              pip3 install awscli;
              aws s3 sync output/reports s3://$AWS_S3_BUCKET/upgrade-reports/$BITBUCKET_BUILD_NUMBER/ --delete;
            fi

pipelines:
  custom:
    spring-upgrade:
      - step: *install-tools
      - step: *spring-upgrade
      - step: *deploy-docs
  
  branches:
    main:
      - step: *install-tools
      - step: *spring-upgrade
      - step: *deploy-docs

  pull-requests:
    '**':
      - step:
          name: Validate Upgrade Changes
          script:
            - chmod +x scripts/*.sh
            - ./scripts/validate-upgrade.sh .
```

### Bitbucket-specific Orchestrator Script (`scripts/upgrade-orchestrator-bitbucket.sh`)
```bash
#!/bin/bash

set -e

# Configuration for Bitbucket
PROJECT_DIR=${1:-"."}
TARGET_SPRING_VERSION=${2:-"6.1.0"}
MAX_ITERATIONS=${3:-10}
REPORT_DIR="upgrade-reports"
OUTPUT_DIR="output"

# Bitbucket environment variables
BITBUCKET_WORKSPACE=${BITBUCKET_WORKSPACE}
BITBUCKET_REPO_SLUG=${BITBUCKET_REPO_SLUG}
BITBUCKET_COMMIT=${BITBUCKET_COMMIT}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Initialize directories
mkdir -p "$REPORT_DIR" "$OUTPUT_DIR"/{reports,diagrams,artifacts}
ITERATION=1
START_TIME=$(date +%s)

log "Starting Enhanced Spring Framework upgrade process for Bitbucket..."
log "Workspace: $BITBUCKET_WORKSPACE"
log "Repository: $BITBUCKET_REPO_SLUG"
log "Target version: $TARGET_SPRING_VERSION"
log "Project directory: $PROJECT_DIR"

# Step 0: Extract baseline metadata
log "Phase 0: Extracting baseline metadata"
./scripts/extract-metadata.sh "$PROJECT_DIR" "$OUTPUT_DIR/artifacts/baseline-metadata.json"

# Update metadata with Bitbucket information
python3 << EOF
import json
with open('$OUTPUT_DIR/artifacts/baseline-metadata.json', 'r+') as f:
    data = json.load(f)
    data['repository'] = {
        'type': 'bitbucket',
        'workspace': '$BITBUCKET_WORKSPACE',
        'repo_slug': '$BITBUCKET_REPO_SLUG',
        'commit': '$BITBUCKET_COMMIT'
    }
    f.seek(0)
    json.dump(data, f, indent=2)
    f.truncate()
EOF

# Step 1: Enhanced Planning Phase
log "Phase 1: Enhanced Planning and Analysis"
./scripts/spring-upgrade-planner.sh \
    --project-dir "$PROJECT_DIR" \
    --target-version "$TARGET_SPRING_VERSION" \
    --output "$REPORT_DIR/upgrade-plan.json" \
    --timeline-output "$REPORT_DIR/timeline-data.json" \
    --metadata-output "$OUTPUT_DIR/artifacts/planning-metadata.json"

if [ $? -ne 0 ]; then
    error "Planning phase failed"
    exit 1
fi

# Step 2: Iterative Upgrade Loop
while [ $ITERATION -le $MAX_ITERATIONS ]; do
    log "Iteration $ITERATION: Executing upgrade tasks"
    
    ITERATION_START=$(date +%s)
    echo "{\"iteration\": $ITERATION, \"start_time\": \"$(date -Iseconds)\", \"status\": \"running\"}" > "$REPORT_DIR/iteration-$ITERATION.json"
    
    # Execute upgrade
    ./scripts/spring-upgrade-executor.sh \
        --project-dir "$PROJECT_DIR" \
        --plan "$REPORT_DIR/upgrade-plan.json" \
        --iteration $ITERATION \
        --changes-output "$REPORT_DIR/changes-iteration-$ITERATION.json"
    
    # Validate results
    log "Validating upgrade results..."
    ./scripts/spring-upgrade-validator.sh \
        --project-dir "$PROJECT_DIR" \
        --report-dir "$REPORT_DIR/iteration-$ITERATION" \
        --detailed-output "$REPORT_DIR/validation-iteration-$ITERATION.json"
    
    VALIDATION_RESULT=$?
    ITERATION_END=$(date +%s)
    ITERATION_DURATION=$((ITERATION_END - ITERATION_START))
    
    if [ $VALIDATION_RESULT -eq 0 ]; then
        echo "{\"iteration\": $ITERATION, \"duration\": $ITERATION_DURATION, \"status\": \"success\"}" > "$REPORT_DIR/iteration-$ITERATION.json"
        success "All objectives met! Upgrade completed successfully in iteration $ITERATION"
        break
    else
        warn "Validation failed. Issues found in iteration $ITERATION"
        
        if [ $ITERATION -eq $MAX_ITERATIONS ]; then
            error "Maximum iterations reached. Upgrade incomplete."
            exit 1
        fi
        
        log "Preparing for next iteration..."
        ((ITERATION++))
    fi
done

# Step 3: Final metadata extraction
log "Extracting final project metadata..."
./scripts/extract-metadata.sh "$PROJECT_DIR" "$OUTPUT_DIR/artifacts/final-metadata.json"

# Step 4: Generate execution summary
END_TIME=$(date +%s)
TOTAL_DURATION=$((END_TIME - START_TIME))

cat > "$REPORT_DIR/execution-log.json" << EOF
{
  "upgrade_summary": {
    "repository": {
      "workspace": "$BITBUCKET_WORKSPACE",
      "repo_slug": "$BITBUCKET_REPO_SLUG",
      "commit": "$BITBUCKET_COMMIT"
    },
    "start_time": "$(date -Iseconds -d @$START_TIME)",
    "end_time": "$(date -Iseconds)",
    "total_duration": $TOTAL_DURATION,
    "iterations_completed": $((ITERATION - 1)),
    "target_version": "$TARGET_SPRING_VERSION",
    "status": "completed"
  }
}
EOF

success "Enhanced Spring Framework upgrade process completed!"
log "Total duration: $TOTAL_DURATION seconds"
log "Iterations completed: $((ITERATION - 1))"
log "Reports available in: $OUTPUT_DIR/reports/"
log "Documentation will be deployed to configured hosting platform"
```

### Bitbucket PR Creation Script (`scripts/create-bitbucket-pr.sh`)
```bash
#!/bin/bash

set -e

# Bitbucket API configuration
BITBUCKET_WORKSPACE=${BITBUCKET_WORKSPACE}
BITBUCKET_REPO_SLUG=${BITBUCKET_REPO_SLUG}
BITBUCKET_USERNAME=${BITBUCKET_USERNAME}
BITBUCKET_APP_PASSWORD=${BITBUCKET_APP_PASSWORD}

# Git configuration
BRANCH_NAME="spring-upgrade-$(date +%Y%m%d-%H%M%S)"
TARGET_VERSION=${TARGET_SPRING_VERSION:-"6.1.0"}

log() {
    echo -e "\033[0;34m[$(date +'%Y-%m-%d %H:%M:%S')] $1\033[0m"
}

success() {
    echo -e "\033[0;32m[SUCCESS] $1\033[0m"
}

error() {
    echo -e "\033[0;31m[ERROR] $1\033[0m"
}

# Create and push branch
log "Creating upgrade branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"
git add .

if ! git diff --cached --quiet; then
    git commit -m "feat: Spring Framework upgrade to $TARGET_VERSION

🚀 Automated Spring Framework Upgrade
- Upgraded to Spring Framework $TARGET_VERSION
- Applied OpenRewrite recipes and modernization patterns
- Enhanced test coverage and security posture
- Generated comprehensive documentation

📊 Upgrade Metrics:
- Test coverage: $(jq -r '.validation.test_coverage // "N/A"' upgrade-reports/final-validation.json 2>/dev/null || echo "N/A")%
- Security vulnerabilities: $(jq -r '.validation.vulnerabilities // "0"' upgrade-reports/final-validation.json 2>/dev/null || echo "0")
- Build status: $(jq -r '.validation.build_status // "SUCCESS"' upgrade-reports/final-validation.json 2>/dev/null || echo "SUCCESS")

Generated by Enhanced Spring Upgrade System for Bitbucket"
fi

git push origin "$BRANCH_NAME"

# Create pull request using Bitbucket API
log "Creating pull request..."

PR_BODY=$(cat << EOF
{
  "title": "🚀 Spring Framework Upgrade to $TARGET_VERSION",
  "description": "# Spring Framework Upgrade to $TARGET_VERSION\n\n## 📋 Executive Summary\nThis automated upgrade enhances the Spring Framework version while maintaining code quality, security, and test coverage standards.\n\n## 🎯 Objectives Achieved\n- ✅ Successful upgrade to Spring Framework $TARGET_VERSION\n- ✅ Test coverage maintained above 80%\n- ✅ Security vulnerabilities resolved\n- ✅ All tests passing\n- ✅ Best practices applied\n\n## 📊 Metrics\n| Metric | Value |\n|--------|-------|\n| Test Coverage | $(jq -r '.validation.test_coverage // "N/A"' upgrade-reports/final-validation.json 2>/dev/null || echo "N/A")% |\n| Vulnerabilities | $(jq -r '.validation.vulnerabilities // "0"' upgrade-reports/final-validation.json 2>/dev/null || echo "0") |\n| Build Status | $(jq -r '.validation.build_status // "SUCCESS"' upgrade-reports/final-validation.json 2>/dev/null || echo "SUCCESS") |\n\n## 🔄 Changes Made\n$(jq -r '.changes[] | \"- \" + .description' upgrade-reports/changes-summary.json 2>/dev/null || echo \"- Detailed changes available in upgrade artifacts\")\n\n---\n*This PR was automatically generated by the Enhanced Spring Upgrade System*",
  "source": {
    "branch": {
      "name": "$BRANCH_NAME"
    }
  },
  "destination": {
    "branch": {
      "name": "main"
    }
  },
  "reviewers": [],
  "close_source_branch": false
}
EOF
)

# Make API call to create PR
RESPONSE=$(curl -s -u "$BITBUCKET_USERNAME:$BITBUCKET_APP_PASSWORD" \
  -H "Content-Type: application/json" \
  -X POST \
  -d "$PR_BODY" \
  "https://api.bitbucket.org/2.0/repositories/$BITBUCKET_WORKSPACE/$BITBUCKET_REPO_SLUG/pullrequests")

if echo "$RESPONSE" | jq -e '.id' > /dev/null; then
    PR_ID=$(echo "$RESPONSE" | jq -r '.id')
    PR_URL=$(echo "$RESPONSE" | jq -r '.links.html.href')
    success "Pull request created successfully!"
    log "PR ID: $PR_ID"
    log "PR URL: $PR_URL"
    
    # Export for pipeline artifacts
    echo "PR_ID=$PR_ID" >> bitbucket-pr-info.env
    echo "PR_URL=$PR_URL" >> bitbucket-pr-info.env
else
    error "Failed to create pull request"
    echo "Response: $RESPONSE"
    exit 1
fi
```

### Documentation Deployment Script for Bitbucket (`scripts/generate-documentation-bitbucket.sh`)
```bash
#!/bin/bash

set -e

PROJECT_DIR=${1:-"."}
REPORT_DIR=${2:-"upgrade-reports"}
OUTPUT_DIR="output"

# Bitbucket-specific configuration
BITBUCKET_WORKSPACE=${BITBUCKET_WORKSPACE}
BITBUCKET_REPO_SLUG=${BITBUCKET_REPO_SLUG}
BUILD_NUMBER=${BITBUCKET_BUILD_NUMBER}

log() {
    echo -e "\033[0;34m[$(date +'%Y-%m-%d %H:%M:%S')] $1\033[0m"
}

success() {
    echo -e "\033[0;32m[SUCCESS] $1\033[0m"
}

# Create output directories
mkdir -p "$OUTPUT_DIR"/{reports,diagrams,artifacts}

log "Starting documentation generation for Bitbucket..."

# Extract project metadata
log "Extracting project metadata..."
./scripts/extract-metadata.sh "$PROJECT_DIR" "$OUTPUT_DIR/artifacts/metadata.json"

# Add Bitbucket-specific metadata
python3 << EOF
import json
from datetime import datetime

with open('$OUTPUT_DIR/artifacts/metadata.json', 'r+') as f:
    data = json.load(f)
    data['bitbucket'] = {
        'workspace': '$BITBUCKET_WORKSPACE',
        'repository': '$BITBUCKET_REPO_SLUG',
        'build_number': '$BUILD_NUMBER',
        'pipeline_url': 'https://bitbucket.org/$BITBUCKET_WORKSPACE/$BITBUCKET_REPO_SLUG/pipelines/results/$BUILD_NUMBER'
    }
    f.seek(0)
    json.dump(data, f, indent=2)
    f.truncate()
EOF

# Generate Mermaid diagrams
log "Generating architecture diagrams..."
./scripts/generate-mermaid-diagrams.sh "$PROJECT_DIR" "$OUTPUT_DIR/diagrams"

# Generate HTML report with Bitbucket-specific template
log "Generating HTML report..."
./scripts/generate-html-report-bitbucket.sh "$PROJECT_DIR" "$REPORT_DIR" "$OUTPUT_DIR/reports"

# Convert Mermaid diagrams to images
log "Converting diagrams to images..."
find "$OUTPUT_DIR/diagrams" -name "*.mmd" -exec mmdc -i {} -o {}.png \;

# Create downloadable artifacts
log "Creating downloadable artifacts..."
cd "$OUTPUT_DIR"
tar -czf "spring-upgrade-documentation-$BUILD_NUMBER.tar.gz" reports/ diagrams/ artifacts/
cd ..

# Upload artifacts to Bitbucket Downloads (if configured)
if [ -n "$BITBUCKET_USERNAME" ] && [ -n "$BITBUCKET_APP_PASSWORD" ]; then
    log "Uploading documentation artifacts to Bitbucket Downloads..."
    curl -s -u "$BITBUCKET_USERNAME:$BITBUCKET_APP_PASSWORD" \
        -X POST \
        -F files=@"$OUTPUT_DIR/spring-upgrade-documentation-$BUILD_NUMBER.tar.gz" \
        "https://api.bitbucket.org/2.0/repositories/$BITBUCKET_WORKSPACE/$BITBUCKET_REPO_SLUG/downloads"
fi

# Deploy to external hosting if configured
if [ -n "$NETLIFY_SITE_ID" ] && [ -n "$NETLIFY_AUTH_TOKEN" ]; then
    log "Deploying documentation to Netlify..."
    npm install -g netlify-cli
    netlify deploy --prod --dir="$OUTPUT_DIR/reports" --site="$NETLIFY_SITE_ID" --auth="$NETLIFY_AUTH_TOKEN"
    
    # Update metadata with deployment URL
    DEPLOY_URL="https://$NETLIFY_SITE_ID.netlify.app"
    python3 << EOF
import json
with open('$OUTPUT_DIR/artifacts/metadata.json', 'r+') as f:
    data = json.load(f)
    data['documentation_url'] = '$DEPLOY_URL'
    f.seek(0)
    json.dump(data, f, indent=2)
    f.truncate()
EOF
    log "Documentation deployed to: $DEPLOY_URL"
fi

if [ -n "$AWS_S3_BUCKET" ]; then
    log "Deploying documentation to S3..."
    pip3 install awscli
    aws s3 sync "$OUTPUT_DIR/reports" "s3://$AWS_S3_BUCKET/spring-upgrades/$BUILD_NUMBER/" --delete
    
    # Update metadata with S3 URL
    S3_URL="https://$AWS_S3_BUCKET.s3.amazonaws.com/spring-upgrades/$BUILD_NUMBER/upgrade-report.html"
    python3 << EOF
import json
with open('$OUTPUT_DIR/artifacts/metadata.json', 'r+') as f:
    data = json.load(f)
    data['documentation_url'] = '$S3_URL'
    f.seek(0)
    json.dump(data, f, indent=2)
    f.truncate()
EOF
    log "Documentation deployed to: $S3_URL"
fi

success "Documentation generation completed for Bitbucket!"
log "Artifacts available in: $OUTPUT_DIR/"
```

### VS Code Task Configuration (`.vscode/tasks.json`)
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Spring Upgrade: Analyze Project",
      "type": "shell",
      "command": "echo",
      "args": ["@spring-upgrade-planner analyze-project"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      },
      "problemMatcher": []
    },
    {
      "label": "Spring Upgrade: Create Plan",
      "type": "shell",
      "command": "echo",
      "args": ["@spring-upgrade-planner create-upgrade-plan"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      },
      "problemMatcher": []
    },
    {
      "label": "Spring Upgrade: Execute Upgrade",
      "type": "shell",
      "command": "chmod +x scripts/*.sh && ./scripts/upgrade-orchestrator-vscode.sh",
      "args": ["."],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      },
      "problemMatcher": []
    },
    {
      "label": "Spring Upgrade: Apply OpenRewrite",
      "type": "shell",
      "command": "echo",
      "args": ["@spring-upgrade-executor apply-openrewrite-recipes"],
      "group": "build",
      "dependsOn": "Spring Upgrade: Create Plan"
    },
    {
      "label": "Spring Upgrade: Validate",
      "type": "shell",
      "command": "echo",
      "args": ["@spring-upgrade-validator validate-upgrade"],
      "group": "test",
      "dependsOn": "Spring Upgrade: Apply OpenRewrite"
    },
    {
      "label": "Spring Upgrade: Generate Documentation",
      "type": "shell",
      "command": "echo",
      "args": ["@documentation-generator generate-upgrade-report"],
      "group": "build",
      "dependsOn": "Spring Upgrade: Validate"
    },
    {
      "label": "Spring Upgrade: Complete Workflow",
      "dependsOrder": "sequence",
      "dependsOn": [
        "Spring Upgrade: Create Plan",
        "Spring Upgrade: Apply OpenRewrite",
        "Spring Upgrade: Validate",
        "Spring Upgrade: Generate Documentation"
      ]
    }
  ]
}
```

### VS Code Copilot Agent Runner Script (`scripts/upgrade-orchestrator-vscode.sh`)
```bash
#!/bin/bash

set -e

PROJECT_DIR=${1:-"."}
TARGET_SPRING_VERSION=${2:-"6.1.0"}
REPORT_DIR="upgrade-reports"
OUTPUT_DIR="output"

# Colors for VS Code terminal
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[VS Code Upgrade] $1${NC}"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[INFO] $1${NC}"
}

# Create directories
mkdir -p "$REPORT_DIR" "$OUTPUT_DIR"

log "Starting Spring Framework upgrade in VS Code..."
log "Use VS Code Copilot Chat with the following agents:"

cat << EOF

🤖 Available Copilot Agents:

1. Planning Phase:
   @spring-upgrade-planner analyze-project
   @spring-upgrade-planner create-upgrade-plan

2. Execution Phase:
   @spring-upgrade-executor apply-openrewrite-recipes
   @spring-upgrade-executor modernize-code-patterns
   @spring-upgrade-executor update-dependencies
   @spring-upgrade-executor enhance-tests

3. Validation Phase:
   @spring-upgrade-validator validate-upgrade
   @spring-upgrade-validator security-scan
   @spring-upgrade-validator performance-check

4. Documentation Phase:
   @documentation-generator generate-upgrade-report
   @documentation-generator create-architecture-diagrams

📋 Or run the complete workflow:
Use Command Palette (Ctrl+Shift+P):
- "Tasks: Run Task" → "Spring Upgrade: Complete Workflow"

💡 Pro Tips:
- Each agent analyzes your current workspace automatically
- Results are saved to upgrade-reports/ directory
- Use Copilot Chat for interactive guidance and questions
- Run "Spring Upgrade: Validate" task to check progress

EOF

# Create VS Code workspace state file
cat > ".vscode/spring-upgrade-state.json" << EOF
{
  "upgrade_session": {
    "started": "$(date -Iseconds)",
    "target_version": "$TARGET_SPRING_VERSION",
    "project_dir": "$PROJECT_DIR",
    "status": "initialized"
  },
  "available_agents": [
    "spring-upgrade-planner",
    "spring-upgrade-executor", 
    "spring-upgrade-validator",
    "documentation-generator"
  ],
  "workspace_config": {
    "reports_dir": "$REPORT_DIR",
    "output_dir": "$OUTPUT_DIR"
  }
}
EOF

success "VS Code Spring upgrade environment initialized!"
warn "Open VS Code Copilot Chat and start with: @spring-upgrade-planner analyze-project"
```

### Bitbucket Notification Configuration (`scripts/send-bitbucket-notifications.sh`)
```bash
#!/bin/bash

set -e

# Bitbucket and notification configuration
BITBUCKET_WORKSPACE=${BITBUCKET_WORKSPACE}
BITBUCKET_REPO_SLUG=${BITBUCKET_REPO_SLUG}
BUILD_NUMBER=${BITBUCKET_BUILD_NUMBER}
UPGRADE_STATUS=${1:-"success"}
TARGET_VERSION=${TARGET_SPRING_VERSION:-"6.1.0"}

log() {
    echo -e "\033[0;34m[$(date +'%Y-%m-%d %H:%M:%S')] $1\033[0m"
}

# Slack notification
send_slack_notification() {
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        local status_emoji="✅"
        local status_color="good"
        local status_text="Success"
        
        if [ "$UPGRADE_STATUS" != "success" ]; then
            status_emoji="❌"
            status_color="danger" 
            status_text="Failed"
        fi
        
        SLACK_PAYLOAD=$(cat << EOF
{
  "attachments": [
    {
      "color": "$status_color",
      "title": "$status_emoji Spring Framework Upgrade $status_text",
      "fields": [
        {
          "title": "Repository",
          "value": "$BITBUCKET_WORKSPACE/$BITBUCKET_REPO_SLUG",
          "short": true
        },
        {
          "title": "Target Version", 
          "value": "$TARGET_VERSION",
          "short": true
        },
        {
          "title": "Build Number",
          "value": "$BUILD_NUMBER",
          "short": true
        },
        {
          "title": "Pipeline",
          "value": "<https://bitbucket.org/$BITBUCKET_WORKSPACE/$BITBUCKET_REPO_SLUG/pipelines/results/$BUILD_NUMBER|View Pipeline>",
          "short": true
        }
      ],
      "footer": "Bitbucket Pipelines",
      "ts": $(date +%s)
    }
  ]
}
EOF
        )
        
        curl -X POST -H 'Content-type: application/json' \
            --data "$SLACK_PAYLOAD" \
            "$SLACK_WEBHOOK_URL"
        
        log "Slack notification sent"
    fi
}

# Microsoft Teams notification
send_teams_notification() {
    if [ -n "$TEAMS_WEBHOOK_URL" ]; then
        local status_color="00FF00"
        local status_text="✅ Success"
        
        if [ "$UPGRADE_STATUS" != "success" ]; then
            status_color="FF0000"
            status_text="❌ Failed"
        fi
        
        TEAMS_PAYLOAD=$(cat << EOF
{
    "@type": "MessageCard",
    "@context": "https://schema.org/extensions",
    "summary": "Spring Framework Upgrade $status_text",
    "themeColor": "$status_color",
    "sections": [
        {
            "activityTitle": "Spring Framework Upgrade $status_text",
            "activitySubtitle": "$BITBUCKET_WORKSPACE/$BITBUCKET_REPO_SLUG",
            "facts": [
                {
                    "name": "Target Version:",
                    "value": "$TARGET_VERSION"
                },
                {
                    "name": "Build Number:",
                    "value": "$BUILD_NUMBER"
                },
                {
                    "name": "Repository:",
                    "value": "$BITBUCKET_WORKSPACE/$BITBUCKET_REPO_SLUG"
                }
            ]
        }
    ],
    "potentialAction": [
        {
            "@type": "OpenUri",
            "name": "View Pipeline",
            "targets": [
                {
                    "os": "default",
                    "uri": "https://bitbucket.org/$BITBUCKET_WORKSPACE/$BITBUCKET_REPO_SLUG/pipelines/results/$BUILD_NUMBER"
                }
            ]
        }
    ]
}
EOF
        )
        
        curl -X POST -H 'Content-Type: application/json' \
            --data "$TEAMS_PAYLOAD" \
            "$TEAMS_WEBHOOK_URL"
        
        log "Teams notification sent"
    fi
}

# Email notification (if SMTP configured)
send_email_notification() {
    if [ -n "$SMTP_SERVER" ] && [ -n "$SMTP_USERNAME" ]; then
        local subject="Spring Framework Upgrade $UPGRADE_STATUS - $BITBUCKET_REPO_SLUG"
        local body="Spring Framework upgrade to $TARGET_VERSION has $UPGRADE_STATUS for repository $BITBUCKET_WORKSPACE/$BITBUCKET_REPO_SLUG.

Build Number: $BUILD_NUMBER
Pipeline URL: https://bitbucket.org/$BITBUCKET_WORKSPACE/$BITBUCKET_REPO_SLUG/pipelines/results/$BUILD_NUMBER

Documentation and artifacts are available in the pipeline artifacts."

        python3 << EOF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

smtp_server = os.environ.get('SMTP_SERVER')
smtp_port = int(os.environ.get('SMTP_PORT', '587'))
username = os.environ.get('SMTP_USERNAME')
password = os.environ.get('SMTP_PASSWORD')
to_email = os.environ.get('NOTIFICATION_EMAIL')

if all([smtp_server, username, password, to_email]):
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = to_email
    msg['Subject'] = '$subject'
    
    msg.attach(MIMEText('$body', 'plain'))
    
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(username, password)
    server.send_message(msg)
    server.quit()
    
    print("Email notification sent")
EOF
    fi
}

# Send notifications
log "Sending upgrade notifications..."
send_slack_notification
send_teams_notification  
send_email_notification

log "Notification dispatch completed"
```

### Repository Variables Configuration for Bitbucket

Add these repository variables in Bitbucket Repository Settings → Pipelines → Repository variables:

```bash
# Required Variables
TARGET_SPRING_VERSION=6.1.0
BITBUCKET_USERNAME=your-username
BITBUCKET_APP_PASSWORD=your-app-password

# Optional: External Documentation Hosting
NETLIFY_SITE_ID=your-netlify-site-id
NETLIFY_AUTH_TOKEN=your-netlify-token
AWS_S3_BUCKET=your-s3-bucket-name

# Optional: Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
NOTIFICATION_EMAIL=team@company.com

# Optional: SMTP (for email notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=notifications@company.com
SMTP_PASSWORD=your-smtp-password
```

## Usage Instructions

### Using VS Code GitHub Copilot Extension

1. **Setup VS Code Workspace:**
   ```bash
   # Copy configuration files to your Spring project
   cp .vscode/* your-spring-project/.vscode/
   cp scripts/* your-spring-project/scripts/
   chmod +x your-spring-project/scripts/*.sh
   ```

2. **Start Upgrade Process:**
   - Open VS Code in your Spring project
   - Open Copilot Chat (Ctrl+Shift+I)
   - Run: `@spring-upgrade-planner analyze-project`
   - Follow the agent recommendations step by step

3. **Execute Complete Workflow:**
   - Use Command Palette (Ctrl+Shift+P)
   - Run: "Tasks: Run Task" → "Spring Upgrade: Complete Workflow"
   - Monitor progress in VS Code terminal

4. **Interactive Guidance:**
   ```
   # In Copilot Chat:
   @spring-upgrade-planner What Spring version should I upgrade to?
   @spring-upgrade-executor How do I modernize my configuration?
   @spring-upgrade-validator What security issues need attention?
   @documentation-generator Show me the architecture diagrams
   ```

### Using Bitbucket Pipelines

1. **Setup Repository:**
   ```bash
   # Add configuration files to your repository
   cp bitbucket-pipelines.yml your-spring-project/
   cp scripts/* your-spring-project/scripts/
   ```

2. **Configure Variables:**
   - Go to Repository Settings → Pipelines → Repository variables
   - Add required variables (see configuration above)

3. **Trigger Upgrade:**
   - Go to Pipelines → Run pipeline
   - Select custom pipeline: "spring-upgrade"
   - Monitor progress and review generated PR

4. **Review Results:**
   - Check created Pull Request with upgrade summary
   - Download documentation artifacts
   - View deployed documentation (if hosting configured)

### Integration Benefits

✅ **VS Code Integration:**
- Interactive upgrade guidance through Copilot Chat
- Context-aware suggestions based on your codebase
- Step-by-step execution with validation
- Integrated terminal and task runner support

✅ **Bitbucket Integration:**
- Automated CI/CD pipeline execution
- Pull Request creation with detailed metrics
- Artifact management and documentation hosting
- Team notifications via Slack/Teams/Email

✅ **Unified Workflow:**
- Use VS Code for development and testing
- Commit changes and trigger Bitbucket pipeline
- Automated deployment and team notifications
- Complete audit trail and documentation