# Spring Upgrade MCP Server 🚀⚙️🔧

*A powerful Spring Framework upgrade toolkit exposed through the Model Context Protocol (MCP) - designed to be used by AI coding assistants like GitHub Copilot, Windsurf, Cursor, and OpenHands to automate complex upgrade processes!*

## 🎯 Empower Your AI Assistant to Upgrade Spring Projects!

**Let your AI coding assistant handle Spring upgrades with confidence!** The Spring Upgrade MCP Server provides a comprehensive toolkit that AI assistants can use to analyze, plan, execute, and document Spring Framework upgrades - without the complexity of managing its own AI models.

### 🌟 What Makes This Special?

This MCP server acts as a specialized Spring upgrade expert that your AI assistant can leverage. It provides:

- 🔍 **Deep Project Analysis** - Comprehensive Spring project analysis and metadata extraction
- 📋 **Smart Planning Tools** - Upgrade planning with timelines and risk assessment
- 🔧 **Automated Execution** - OpenRewrite recipe application with validation
- ✅ **Quality Assurance** - Built-in quality gates and validation framework
- 📊 **Rich Documentation** - Automatic HTML report generation with Mermaid diagrams
- 🏗️ **Architecture Artifacts** - C4, sequence, class, and state diagram generation

But here's the **key difference** ✨ - this server doesn't make AI decisions itself! Instead:

- **Your AI assistant** makes the intelligent decisions
- **The MCP server** provides the tools and data needed
- **No duplicate LLM costs** - uses your assistant's existing AI
- **Clean separation** of tools and intelligence
- **Flexible integration** with any MCP-compatible AI assistant

### 🎯 Perfect for AI-Assisted Spring Upgrades!

Your AI coding assistant can use this toolkit to:

- **Analyze** - Get detailed project structure and dependency information
- **Plan** - Create comprehensive upgrade strategies with timelines
- **Execute** - Apply validated code transformations
- **Validate** - Ensure quality standards are met
- **Document** - Generate professional upgrade reports

## Overview

The Spring Upgrade MCP Server is a specialized toolkit that provides Spring Framework upgrade capabilities through the Model Context Protocol. It maintains upgrade state and provides tools for:

- **State Management**: Tracks upgrade progress, validation results, and rollback points
- **Tools as Services**: Upgrade operations exposed as MCP tools
- **Prompts as Templates**: Guidance templates for AI assistants to use
- **Code Analysis**: Pattern detection and similarity search using Qdrant
- **Documentation Generation**: Professional reports with architecture diagrams

## Key Architecture Principles

1. **No Built-in LLM Calls** - The server provides tools and data, not AI decisions
2. **AI Assistant Driven** - Designed to be orchestrated by external AI coding assistants
3. **Stateful Operations** - Maintains context between tool calls
4. **Vector Storage** - Uses Qdrant for code pattern storage and retrieval
5. **Tool-First Design** - Everything is exposed as MCP tools

## Features

- **Project Analysis Tools**: Deep Spring project analysis with metadata extraction
- **Upgrade Planning**: Timeline generation and risk assessment tools
- **OpenRewrite Integration**: Recipe discovery and execution with validation
- **Pattern Modernization**: Tools for applying Spring best practices
- **Quality Gates**: Configurable validation thresholds
- **Test Enhancement**: Coverage analysis and test generation support
- **Documentation Engine**: HTML reports with embedded Mermaid diagrams
- **Architecture Analysis**: Automatic diagram generation from code structure
- **Vector Search**: Code similarity search using Qdrant
- **Checkpoint System**: Safe rollback points during upgrade

### 🎁 Why AI Assistants Love This

**GitHub Copilot**, **Windsurf**, **Cursor**, **OpenHands** - any MCP-compatible AI assistant benefits from:

- ⚡ **Specialized Tools** - Purpose-built for Spring upgrades
- 🛡️ **Safe Execution** - Validation and rollback built-in
- 📈 **Quality Enforcement** - Automatic quality gate checks
- 📊 **Beautiful Reports** - Professional documentation generation
- 🔍 **Pattern Learning** - Vector search for similar upgrade patterns
- 🤝 **Clean Integration** - Simple tool-based interface

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourorg/spring-upgrade-mcp
cd spring-upgrade-mcp
```

2. Install dependencies:
```bash
./mvnw clean install
npm install -g @mermaid-js/mermaid-cli
pip install jinja2 markdown beautifulsoup4
```

3. Start Qdrant vector database:
```bash
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
```

4. Configure the application:
```bash
cp application.yml.example application.yml
# Edit application.yml with your settings
```

5. Build the project:
```bash
./mvnw spring-boot:build-image
```

## Running the Server

Start the server using:

```bash
./mvnw spring-boot:run
```

For development with hot reload:

```bash
./mvnw spring-boot:run -Dspring-boot.run.profiles=dev
```

## How AI Assistants Use This Server

When connected via MCP, AI coding assistants can:

1. **Analyze a project**: Call `analyze_project` to get comprehensive project data
2. **Check patterns**: Use `search_patterns` to find similar upgrade scenarios
3. **Create a plan**: Call `create_upgrade_plan` with target version
4. **Execute changes**: Use `apply_recipes` with selected recipes
5. **Validate results**: Call `validate_upgrade` to check quality gates
6. **Generate docs**: Use `generate_documentation` for reports

The AI assistant orchestrates these tools based on its own intelligence and the user's requests.

## Available Tools

| Tool | Description | Returns |
|------|-------------|---------|
| `analyze_project` | Deep project analysis with metadata | Project structure, dependencies, patterns |
| `search_patterns` | Find similar upgrade patterns in vector store | Similar patterns with solutions |
| `create_upgrade_plan` | Generate upgrade plan with timeline | Phases, tasks, timeline, risks |
| `discover_recipes` | Find applicable OpenRewrite recipes | Recipe list with descriptions |
| `apply_recipes` | Execute OpenRewrite recipes | Changes made, validation results |
| `modernize_patterns` | Apply Spring best practices | Pattern updates applied |
| `analyze_test_coverage` | Get current test coverage | Coverage metrics by package |
| `suggest_tests` | Identify areas needing tests | Test suggestions with templates |
| `validate_upgrade` | Run quality gate checks | Validation results, metrics |
| `generate_documentation` | Create upgrade report | HTML report with diagrams |
| `extract_metadata` | Get project configuration | Config files, properties, structure |
| `create_checkpoint` | Create rollback point | Checkpoint ID for rollback |
| `list_checkpoints` | Get available checkpoints | Checkpoint list with metadata |
| `rollback` | Rollback to checkpoint | Rollback status |

## Tool Response Format

All tools return structured data that AI assistants can interpret:

```json
{
  "success": true,
  "data": {
    // Tool-specific structured data
  },
  "metadata": {
    "duration": 1250,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "suggestions": [
    // Optional suggestions for next steps
  ]
}
```

## Prompts as Templates

The server provides prompt templates that AI assistants can use for guidance:

- **upgrade_planning** - Template for analyzing upgrade complexity
- **risk_assessment** - Framework for evaluating upgrade risks  
- **validation_interpretation** - Guide for understanding validation results
- **documentation_sections** - Templates for report sections
- **architecture_description** - Patterns for describing architecture

These are returned as structured templates, not AI-generated content.

## Vector Storage with Qdrant

The server uses Qdrant to store and search upgrade patterns:

- **Pattern Storage**: Successful upgrade patterns are vectorized and stored
- **Similarity Search**: Find similar code patterns and their solutions
- **No Embedding Generation**: Expects embeddings from the AI assistant
- **Configurable Collections**: Separate collections for different pattern types

## Documentation Generation

The server generates professional documentation without AI:

- **HTML Reports** with responsive design
- **Mermaid Diagrams** embedded in reports
- **Structured Data** presentation
- **Change Tracking** with file-level detail
- **Architecture Visualization** from code analysis

## Development

### Project Structure

```
├── src/main/java/              # Java source code
│   ├── config/                 # Spring configuration
│   ├── controller/             # MCP request handlers
│   ├── service/               # Business logic
│   │   ├── mcp/              # MCP protocol implementation
│   │   ├── upgrade/          # Upgrade orchestration
│   │   ├── analysis/         # Code analysis services
│   │   ├── validation/       # Quality gates
│   │   └── documentation/    # Report generation
│   ├── model/                 # Domain models
│   └── repository/            # Data persistence
├── src/main/resources/        # Configuration files
│   ├── application.yml        # Spring configuration
│   ├── recipes/              # OpenRewrite recipes
│   └── templates/            # Documentation templates
│       ├── report-template.html
│       └── mermaid-templates/
├── scripts/                   # Utility scripts
└── src/test/                  # Test suites
```

### Configuration

```yaml
spring:
  application:
    name: spring-upgrade-mcp
    
qdrant:
  host: localhost
  port: 6333
  collection: upgrade-patterns
  vector-size: 1536

upgrade:
  quality-gates:
    min-test-coverage: 80
    max-vulnerabilities: 0
    max-build-time: 600
  documentation:
    output-dir: ./output
    include-diagrams: true
```

## Technical Details

### MCP Protocol Compliance

- Full MCP 2025-03-26 specification support
- Tool definitions with JSON Schema
- Structured responses
- Progress notifications
- Resource exposure

### Quality Gates

```yaml
quality_gates:
  testing:
    min_coverage: 80
    required_types: [unit, integration]
  security:
    max_critical: 0
    max_high: 5
  performance:
    max_startup_time: 30
    max_memory_mb: 512
```

### Vector Storage Schema

```json
{
  "collections": {
    "upgrade_patterns": {
      "vectors": {
        "size": 1536,
        "distance": "Cosine"
      },
      "payload_schema": {
        "pattern_type": "keyword",
        "from_version": "keyword", 
        "to_version": "keyword",
        "success_rate": "float",
        "solution": "text"
      }
    }
  }
}
```

## Integration Examples

### With GitHub Copilot
```typescript
// In your AI coding assistant
const mcp = new MCPClient('http://localhost:8080/mcp');

// Analyze project
const analysis = await mcp.callTool('analyze_project', {
  project_path: './my-spring-app'
});

// AI assistant processes analysis and decides next steps
if (analysis.data.current_version < '6.0.0') {
  const plan = await mcp.callTool('create_upgrade_plan', {
    target_version: '6.1.0',
    strategy: 'conservative'
  });
  // AI explains plan to user and proceeds...
}
```

### With Cursor/Windsurf
The MCP server appears as available tools that the AI can invoke based on user requests about Spring upgrades.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.