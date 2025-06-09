# Spring Upgrade MCP Server Specification

## Overview
This document defines the specifications for a Spring Framework upgrade toolkit exposed through the Model Context Protocol (MCP) specification version 2025-03-26. The server provides comprehensive upgrade tools designed to be orchestrated by AI coding assistants (GitHub Copilot, Windsurf, Cursor, OpenHands) without making any LLM calls itself. It uses Qdrant for vector storage of upgrade patterns.

## Architecture
- **State Management**: Maintains detailed upgrade session state including progress, validations, checkpoints, and documentation artifacts
- **Tools as Services**: Upgrade operations exposed as MCP tools returning structured data
- **Prompts as Templates**: Structured guidance templates for AI assistants (not AI-generated content)
- **Resources**: Upgrade artifacts, reports, diagrams, and state data exposed for consumption
- **Vector Storage**: Qdrant-based pattern storage without embedding generation
- **MCP Communication**: Full compliance with MCP protocol 2025-03-26 via JSON-RPC 2.0
- **No LLM Integration**: All intelligence provided by the consuming AI assistant

---

## 1. Core Design Principles

### No Built-in AI
- Server provides tools and data only
- AI coding assistants make all decisions
- No LLM API integrations
- No prompt engineering or generation
- Structured responses for AI interpretation

### Tool-First Architecture
- Everything exposed as MCP tools
- Consistent response structure
- Progressive workflow support
- Suggestions for next steps
- Clear error messages

### Vector Storage Without Generation
- Stores embeddings provided by AI assistants
- Searches patterns using provided vectors
- Tracks pattern success metrics
- No embedding model required

---

## 2. Upgrade State Representation

Each upgrade session maintains comprehensive state:

```json
{
  "session_id": "upgrade-12345",
  "project": {
    "path": "/path/to/spring-project",
    "name": "e-commerce-api",
    "type": "maven",
    "modules": ["core", "web", "data"],
    "current_version": "5.3.23",
    "java_version": "17",
    "size_metrics": {
      "total_files": 487,
      "java_files": 234,
      "test_files": 112,
      "lines_of_code": 45230
    }
  },
  "upgrade": {
    "target_version": "6.1.0",
    "strategy": "conservative",
    "phase": "validation",
    "progress": 75,
    "start_time": "2024-01-15T09:00:00Z",
    "elapsed_time": 4500,
    "estimated_remaining": 1500
  },
  "tasks": [
    {
      "id": "task-1",
      "name": "Apply Spring Boot 3.x recipes",
      "status": "completed",
      "duration": 1200,
      "changes_count": 47
    }
  ],
  "validations": {
    "build": {
      "status": "passed",
      "duration": 145,
      "warnings": 0
    },
    "tests": {
      "status": "passed",
      "total": 127,
      "passed": 127,
      "coverage": 84.7
    },
    "security": {
      "status": "passed",
      "vulnerabilities": {
        "critical": 0,
        "high": 0,
        "medium": 2,
        "low": 5
      },
      "scan_tools": ["owasp", "snyk"]
    }
  },
  "checkpoints": [
    {
      "id": "checkpoint-3",
      "created_at": "2024-01-15T11:30:00Z",
      "description": "After recipe execution",
      "git_commit": "abc123def",
      "restorable": true
    }
  ],
  "documentation": {
    "report_generated": true,
    "report_path": "output/upgrade-report.html",
    "diagrams": ["timeline", "sequence", "c4-context"],
    "generation_time": 45
  }
}
```

---

## 3. Tools (Upgrade Operations)

All tools return structured data for AI assistant interpretation.

### Tool Discovery
```json
{
  "method": "tools/list",
  "result": {
    "tools": [
      {
        "name": "analyze_project",
        "description": "Comprehensive Spring project analysis with metadata extraction",
        "inputSchema": {
          "type": "object",
          "properties": {
            "project_path": {
              "type": "string",
              "description": "Path to the Spring project root"
            },
            "analysis_depth": {
              "type": "string",
              "enum": ["quick", "standard", "deep"],
              "default": "standard",
              "description": "Depth of analysis to perform"
            },
            "include_test_analysis": {
              "type": "boolean",
              "default": true,
              "description": "Include test code in analysis"
            }
          },
          "required": ["project_path"]
        },
        "annotations": {
          "category": "analysis",
          "execution_time": "fast",
          "modifies_code": false,
          "requires_build_tool": true
        }
      }
    ]
  }
}
```

### Tool Response Structure

All tools follow this response pattern:

```json
{
  "success": true,
  "data": {
    // Tool-specific structured data
  },
  "metadata": {
    "tool": "analyze_project",
    "duration_ms": 1250,
    "timestamp": "2024-01-15T10:30:00Z",
    "session_id": "upgrade-12345"
  },
  "suggestions": [
    {
      "action": "search_patterns",
      "reason": "Find similar upgrade scenarios",
      "priority": "high"
    },
    {
      "action": "create_upgrade_plan",
      "reason": "Project analysis complete",
      "priority": "high"
    }
  ],
  "warnings": [],
  "errors": []
}
```

### Tool Definitions

#### `analyze_project`
Performs comprehensive project analysis without AI.

**Input**:
```json
{
  "project_path": "/path/to/project",
  "analysis_depth": "standard",
  "include_test_analysis": true
}
```

**Output**:
```json
{
  "success": true,
  "data": {
    "project_info": {
      "name": "e-commerce-api",
      "type": "maven",
      "packaging": "jar",
      "java_version": "17",
      "spring_boot_version": "2.7.0",
      "spring_framework_version": "5.3.23"
    },
    "structure": {
      "modules": ["core", "web", "data"],
      "source_packages": 23,
      "test_packages": 15,
      "configuration_files": 8
    },
    "dependencies": {
      "total": 87,
      "spring_dependencies": 12,
      "outdated": 5,
      "vulnerable": 2,
      "conflicts": 1
    },
    "code_analysis": {
      "patterns_found": [
        {
          "pattern": "field-injection",
          "occurrences": 34,
          "locations": ["controllers", "services"]
        },
        {
          "pattern": "xml-configuration",
          "occurrences": 3,
          "locations": ["security-config.xml"]
        }
      ],
      "deprecated_apis": [
        {
          "api": "WebSecurityConfigurerAdapter",
          "usage_count": 1,
          "migration_required": true
        }
      ]
    },
    "test_analysis": {
      "test_count": 127,
      "coverage": 78.5,
      "test_types": {
        "unit": 98,
        "integration": 29
      }
    },
    "complexity_metrics": {
      "cyclomatic_complexity": 3.2,
      "coupling": "moderate",
      "size": "medium"
    }
  },
  "suggestions": [
    {
      "action": "search_patterns",
      "reason": "Found field injection pattern - search for migration examples"
    }
  ]
}
```

#### `search_patterns`
Searches for similar upgrade patterns in Qdrant.

**Input**:
```json
{
  "embedding": [0.1, 0.2, ...], // 1536-dimensional vector from AI assistant
  "filter": {
    "from_version": "5.x",
    "to_version": "6.x",
    "pattern_type": "security-migration"
  },
  "limit": 5
}
```

**Output**:
```json
{
  "success": true,
  "data": {
    "patterns": [
      {
        "id": "pattern-123",
        "similarity_score": 0.92,
        "pattern_type": "security-migration",
        "description": "WebSecurityConfigurerAdapter to SecurityFilterChain",
        "from_version": "5.7.x",
        "to_version": "6.0.x",
        "solution": {
          "summary": "Replace adapter with @Bean SecurityFilterChain",
          "recipes": ["org.openrewrite.spring.security6.UpgradeSpringSecurity_6_0"],
          "manual_steps": ["Review custom security configurations"],
          "success_rate": 0.95
        },
        "usage_count": 47,
        "last_used": "2024-01-10T15:30:00Z"
      }
    ],
    "search_metadata": {
      "total_patterns": 1247,
      "search_time_ms": 23
    }
  },
  "suggestions": [
    {
      "action": "create_upgrade_plan",
      "reason": "Similar patterns found - ready to plan upgrade"
    }
  ]
}
```

#### `create_upgrade_plan`
Generates a structured upgrade plan using rules and heuristics.

**Input**:
```json
{
  "target_version": "6.1.0",
  "strategy": "conservative",
  "priorities": ["minimize_risk", "maintain_compatibility"],
  "constraints": {
    "max_downtime": 3600,
    "require_rollback": true
  }
}
```

**Output**:
```json
{
  "success": true,
  "data": {
    "plan": {
      "id": "plan-789",
      "phases": [
        {
          "phase": 1,
          "name": "Preparation",
          "tasks": [
            {
              "id": "task-1",
              "name": "Create baseline metrics",
              "type": "validation",
              "estimated_duration": 600,
              "automated": true
            },
            {
              "id": "task-2",
              "name": "Backup and checkpoint",
              "type": "checkpoint",
              "estimated_duration": 300,
              "automated": true
            }
          ]
        },
        {
          "phase": 2,
          "name": "Core Framework Upgrade",
          "tasks": [
            {
              "id": "task-3",
              "name": "Update Spring Boot version",
              "type": "dependency",
              "estimated_duration": 120,
              "recipes": ["org.openrewrite.spring.boot3.UpgradeSpringBoot_3_2"]
            }
          ]
        }
      ],
      "timeline": {
        "total_duration": 7200,
        "phases": [
          {"phase": 1, "start": 0, "duration": 900},
          {"phase": 2, "start": 900, "duration": 3600}
        ]
      },
      "risks": [
        {
          "category": "compatibility",
          "description": "Custom security configuration requires manual review",
          "severity": "medium",
          "mitigation": "Test security endpoints thoroughly"
        }
      ]
    }
  },
  "suggestions": [
    {
      "action": "apply_recipes",
      "reason": "Plan created - ready to execute"
    }
  ]
}
```

#### `discover_recipes`
Finds applicable OpenRewrite recipes.

**Input**:
```json
{
  "current_version": "5.3.23",
  "target_version": "6.1.0",
  "categories": ["framework", "security", "testing"]
}
```

**Output**:
```json
{
  "success": true,
  "data": {
    "recipes": [
      {
        "name": "org.openrewrite.spring.boot3.UpgradeSpringBoot_3_2",
        "description": "Upgrade Spring Boot to 3.2",
        "category": "framework",
        "estimated_changes": 150,
        "risk_level": "medium",
        "prerequisites": ["Java 17+"],
        "includes": [
          "Dependency updates",
          "Property migrations",
          "API updates"
        ]
      }
    ],
    "recipe_count": 8,
    "estimated_total_changes": 450
  }
}
```

#### `apply_recipes`
Executes OpenRewrite recipes and tracks changes.

**Input**:
```json
{
  "recipes": ["org.openrewrite.spring.boot3.UpgradeSpringBoot_3_2"],
  "dry_run": false,
  "create_checkpoint": true,
  "validation_level": "standard"
}
```

**Output**:
```json
{
  "success": true,
  "data": {
    "execution_id": "exec-456",
    "checkpoint_id": "checkpoint-4",
    "changes": {
      "total_files_changed": 47,
      "changes_by_type": {
        "dependency_updates": 12,
        "import_changes": 23,
        "annotation_updates": 8,
        "configuration_changes": 4
      },
      "changed_files": [
        {
          "path": "pom.xml",
          "change_count": 5,
          "change_types": ["version_update", "dependency_addition"]
        }
      ]
    },
    "validation": {
      "compilation": "success",
      "warnings": 3,
      "errors": 0
    },
    "duration": 2450
  },
  "suggestions": [
    {
      "action": "validate_upgrade",
      "reason": "Recipes applied - validate changes"
    }
  ]
}
```

#### `validate_upgrade`
Runs comprehensive validation suite.

**Input**:
```json
{
  "validation_types": ["build", "test", "security"],
  "quality_gates": {
    "min_test_coverage": 80,
    "max_vulnerabilities": 0,
    "required_test_types": ["unit", "integration"]
  }
}
```

**Output**:
```json
{
  "success": true,
  "data": {
    "overall_status": "passed",
    "validations": {
      "build": {
        "status": "passed",
        "duration": 145,
        "output": "BUILD SUCCESS",
        "warnings": 0
      },
      "tests": {
        "status": "passed",
        "total": 127,
        "passed": 127,
        "failed": 0,
        "skipped": 0,
        "coverage": 84.7,
        "duration": 234
      },
      "security": {
        "status": "passed",
        "scan_tools": ["owasp-dependency-check", "snyk"],
        "vulnerabilities": {
          "critical": 0,
          "high": 0,
          "medium": 2,
          "low": 5
        },
        "scan_duration": 89
      }
    },
    "quality_gates": {
      "test_coverage": {"required": 80, "actual": 84.7, "passed": true},
      "vulnerabilities": {"required": 0, "actual": 0, "passed": true}
    }
  }
}
```

#### `generate_documentation`
Creates comprehensive upgrade documentation.

**Input**:
```json
{
  "format": "html",
  "include_diagrams": true,
  "diagram_types": ["timeline", "sequence", "c4-context"],
  "sections": ["executive_summary", "changes", "validation", "architecture"]
}
```

**Output**:
```json
{
  "success": true,
  "data": {
    "report_path": "output/upgrade-report.html",
    "generation_time": 45,
    "report_size": 2457600,
    "included_sections": [
      "executive_summary",
      "project_overview",
      "upgrade_timeline",
      "changes_summary",
      "validation_results",
      "architecture_diagrams"
    ],
    "diagrams": {
      "timeline": "output/diagrams/timeline.mmd",
      "sequence": "output/diagrams/execution-sequence.mmd",
      "c4_context": "output/diagrams/c4-context.mmd"
    },
    "assets": {
      "css": ["bootstrap.min.css", "custom.css"],
      "js": ["mermaid.min.js", "report.js"]
    }
  }
}
```

#### `store_pattern`
Stores a successful upgrade pattern for future reference.

**Input**:
```json
{
  "pattern_type": "security-migration",
  "description": "WebSecurityConfigurerAdapter migration",
  "embedding": [0.1, 0.2, ...], // From AI assistant
  "solution": {
    "recipes": ["org.openrewrite.spring.security6.UpgradeSpringSecurity_6_0"],
    "manual_steps": ["Review custom configurations"],
    "notes": "Successful migration with custom JWT filter"
  },
  "from_version": "5.7.x",
  "to_version": "6.0.x"
}
```

**Output**:
```json
{
  "success": true,
  "data": {
    "pattern_id": "pattern-new-456",
    "stored_at": "2024-01-15T12:00:00Z",
    "collection": "upgrade-patterns",
    "vector_dimensions": 1536
  }
}
```

---

## 4. Prompts (Template System)

The server provides structured templates, not AI-generated content.

### Prompt Discovery
```json
{
  "method": "prompts/list",
  "result": {
    "prompts": [
      {
        "name": "upgrade_planning",
        "description": "Template for upgrade planning analysis",
        "variables": ["current_version", "target_version", "project_type"],
        "sections": ["current_state", "target_state", "gap_analysis", "risks"]
      },
      {
        "name": "validation_guide",
        "description": "Framework for interpreting validation results",
        "variables": ["test_coverage", "vulnerabilities", "build_status"],
        "decision_points": ["proceed", "investigate", "rollback"]
      }
    ]
  }
}
```

### Template Structure Example

```json
{
  "name": "upgrade_planning",
  "template": {
    "sections": [
      {
        "id": "current_state",
        "title": "Current State Analysis",
        "prompts": [
          "Project {{project_name}} is currently on Spring {{current_version}}",
          "Found {{pattern_count}} patterns that need migration",
          "Dependency analysis shows {{outdated_count}} outdated dependencies"
        ]
      },
      {
        "id": "risks",
        "title": "Risk Assessment",
        "factors": [
          {
            "factor": "breaking_changes",
            "threshold": 10,
            "guidance": "High number of breaking changes detected"
          }
        ]
      }
    ],
    "decision_tree": {
      "root": "Should we proceed with upgrade?",
      "branches": [
        {
          "condition": "test_coverage > 80",
          "recommendation": "proceed",
          "reason": "Good test coverage provides safety net"
        }
      ]
    }
  }
}
```

---

## 5. Resources

Resources expose upgrade artifacts and state.

### Resource Discovery
```json
{
  "method": "resources/list",
  "result": {
    "resources": [
      {
        "uri": "upgrade://session/current",
        "name": "Current Session State",
        "mimeType": "application/json",
        "description": "Complete upgrade session state"
      },
      {
        "uri": "upgrade://reports/latest",
        "name": "Latest Upgrade Report",
        "mimeType": "text/html",
        "description": "Generated HTML report"
      },
      {
        "uri": "upgrade://patterns/collection",
        "name": "Pattern Collection Stats",
        "mimeType": "application/json",
        "description": "Statistics about stored patterns"
      }
    ]
  }
}
```

---

## 6. Vector Storage with Qdrant

### Collection Schema
```json
{
  "collection_name": "upgrade-patterns",
  "vectors": {
    "size": 1536,
    "distance": "Cosine"
  },
  "payload_schema": {
    "pattern_type": "keyword",
    "from_version": "keyword",
    "to_version": "keyword",
    "description": "text",
    "solution": "text",
    "success_rate": "float",
    "usage_count": "integer",
    "last_used": "datetime",
    "recipes": "keyword[]",
    "tags": "keyword[]"
  },
  "indexes": [
    {
      "field": "pattern_type",
      "type": "keyword"
    },
    {
      "field": "from_version",
      "type": "keyword"
    }
  ]
}
```

### Pattern Storage Flow
1. AI assistant analyzes code and generates embedding
2. AI calls `store_pattern` with embedding and metadata
3. Server stores in Qdrant with success metrics
4. Future searches use similarity matching

### Search Operations
- No embedding generation in server
- Expects embeddings from AI assistant
- Supports filtered search by version, type
- Returns relevant patterns with solutions

---

## 7. Documentation Generation

### Report Structure
Generated reports are data-driven, not AI-generated:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Spring Upgrade Report - {{project_name}}</title>
    <link rel="stylesheet" href="css/bootstrap.min.css">
    <script src="js/mermaid.min.js"></script>
</head>
<body>
    <div class="container">
        <h1>Spring Framework Upgrade Report</h1>
        
        <!-- Executive Summary -->
        <section id="summary">
            <h2>Executive Summary</h2>
            <div class="metrics">
                <div class="metric">
                    <span class="value">{{duration}}</span>
                    <span class="label">Total Duration</span>
                </div>
                <!-- More metrics -->
            </div>
        </section>
        
        <!-- Timeline Diagram -->
        <section id="timeline">
            <h2>Upgrade Timeline</h2>
            <div class="mermaid">
                {{timeline_diagram}}
            </div>
        </section>
        
        <!-- Validation Results -->
        <section id="validation">
            <h2>Validation Results</h2>
            <table class="table">
                <!-- Structured validation data -->
            </table>
        </section>
    </div>
</body>
</html>
```

### Diagram Generation
Diagrams are generated from structural analysis:

- **Timeline**: Task execution sequence
- **Architecture**: Component relationships
- **Sequence**: Upgrade flow
- **Class**: Modified classes

---

## 8. Error Handling

All errors return structured responses:

```json
{
  "success": false,
  "error": {
    "code": "RECIPE_EXECUTION_FAILED",
    "message": "Failed to apply Spring Security migration recipe",
    "details": {
      "recipe": "org.openrewrite.spring.security6.UpgradeSpringSecurity_6_0",
      "failure_point": "SecurityConfig.java:45",
      "compilation_error": "cannot find symbol: WebSecurityConfigurerAdapter"
    },
    "suggestions": [
      "Check if all required dependencies are updated",
      "Verify SecurityConfig extends correct base class",
      "Consider manual migration for this file"
    ],
    "recoverable": true,
    "rollback_available": true
  },
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "session_id": "upgrade-12345",
    "tool": "apply_recipes"
  }
}
```

---

## 9. Security & Compliance

### Authentication
- API key-based authentication
- Rate limiting per client
- Audit logging

### Code Security
- Local execution only
- No external code transmission
- Secure workspace isolation
- Git integration for rollback

### Data Privacy
- No LLM API calls
- No code sent externally
- Local pattern storage option
- Configurable retention

---

## 10. Implementation Guidelines

### Spring Boot Configuration
```java
@SpringBootApplication
@EnableMcpServer
public class SpringUpgradeMcpApplication {
    public static void main(String[] args) {
        SpringApplication.run(SpringUpgradeMcpApplication.class, args);
    }
}
```

### Tool Implementation Pattern
```java
@Component
@McpTool("analyze_project")
public class AnalyzeProjectTool implements UpgradeTool {
    
    private final ProjectAnalyzer analyzer;
    private final MetricsCalculator metrics;
    
    @Override
    public ToolResponse execute(ToolRequest request) {
        var projectPath = request.getRequiredParameter("project_path", String.class);
        var depth = request.getParameter("analysis_depth", "standard");
        
        try {
            var analysis = analyzer.analyze(projectPath, AnalysisDepth.valueOf(depth));
            var projectMetrics = metrics.calculate(analysis);
            
            return ToolResponse.success()
                .data("project_info", analysis.getProjectInfo())
                .data("dependencies", analysis.getDependencies())
                .data("patterns", analysis.getPatterns())
                .data("metrics", projectMetrics)
                .suggestion("search_patterns", "Find similar upgrade patterns")
                .suggestion("create_upgrade_plan", "Ready to plan upgrade")
                .build();
                
        } catch (Exception e) {
            return ToolResponse.error("ANALYSIS_FAILED", e.getMessage())
                .suggestion("verify_project_path", "Check if path is correct")
                .build();
        }
    }
}
```

### Qdrant Integration
```java
@Service
public class PatternSearchService {
    
    private final QdrantClient qdrantClient;
    
    public List<Pattern> searchSimilar(float[] embedding, SearchFilter filter) {
        var searchRequest = SearchPoints.newBuilder()
            .setCollectionName("upgrade-patterns")
            .addAllVector(Arrays.asList(embedding))
            .setLimit(filter.getLimit())
            .setFilter(buildFilter(filter))
            .setWithPayload(true)
            .build();
            
        var response = qdrantClient.search(searchRequest);
        
        return response.getResultList().stream()
            .map(this::toPattern)
            .collect(Collectors.toList());
    }
}
```

---

## 11. Testing & Validation

### Tool Testing
```java
@Test
void testAnalyzeProjectTool() {
    var request = ToolRequest.builder()
        .parameter("project_path", "test-project")
        .parameter("analysis_depth", "standard")
        .build();
        
    var response = analyzeProjectTool.execute(request);
    
    assertThat(response.isSuccess()).isTrue();
    assertThat(response.getData()).containsKey("project_info");
    assertThat(response.getSuggestions()).isNotEmpty();
}
```

### Integration Testing
- Mock Qdrant for pattern searches
- Test data fixtures for projects
- Validation of all tool responses
- MCP protocol compliance

---

## 12. Deployment Architecture

### Standalone Deployment
```yaml
version: '3.8'
services:
  mcp-server:
    image: spring-upgrade-mcp:latest
    ports:
      - "8080:8080"
    environment:
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
    volumes:
      - ./workspace:/workspace
      
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_data:/qdrant/storage
```

### Configuration
```yaml
server:
  port: 8080

mcp:
  transport: websocket
  path: /mcp

qdrant:
  host: ${QDRANT_HOST:localhost}
  port: ${QDRANT_PORT:6333}
  collection: upgrade-patterns
  
upgrade:
  workspace: ${UPGRADE_WORKSPACE:./workspace}
  max-concurrent-sessions: 10
  session-timeout: 3600
```

---

## 13. Usage with AI Assistants

### GitHub Copilot Integration
```javascript
// Copilot can use the MCP tools
const mcp = await connectMCP('ws://localhost:8080/mcp');

// Analyze project
const analysis = await mcp.callTool('analyze_project', {
  project_path: userProject
});

// Copilot interprets results and suggests next steps
if (analysis.data.dependencies.vulnerable > 0) {
  // Copilot explains vulnerabilities and suggests fixes
}
```

### Cursor/Windsurf Integration
Tools appear in the assistant's available actions, allowing natural language commands like:
- "Analyze this Spring project for upgrade readiness"
- "Find patterns similar to our security configuration"
- "Create an upgrade plan to Spring 6.1"

---

## Conclusion

The Spring Upgrade MCP Server provides a comprehensive toolkit for Spring Framework upgrades without requiring its own AI capabilities. By exposing structured tools through MCP, it enables AI coding assistants to orchestrate complex upgrades while maintaining:

- **Separation of Concerns** - Tools provide data, AI provides intelligence
- **Cost Efficiency** - No duplicate LLM API calls
- **Flexibility** - Works with any MCP-compatible AI assistant
- **Reliability** - Deterministic tool behavior
- **Extensibility** - Easy to add new tools and patterns

This design creates a powerful upgrade assistant that leverages the AI capabilities of modern coding tools while providing specialized Spring expertise through a clean, tool-based interface.