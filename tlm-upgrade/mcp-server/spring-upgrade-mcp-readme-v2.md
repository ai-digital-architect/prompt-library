# Spring Upgrade MCP Server 🚀⚙️🔧

*An intelligent Spring Framework upgrade assistant powered by the Model Context Protocol (MCP) and Spring AI - designed to automate complex upgrade processes with AI-driven insights and comprehensive documentation generation!*

## 🎯 Automate Your Spring Framework Upgrades with AI!

**Tired of manual dependency conflicts and breaking changes?** Let AI guide your Spring Framework upgrades with confidence! The Spring Upgrade MCP Server combines the power of Large Language Models with automated tooling to make upgrades seamless, reliable, and fully documented.

### 🌟 What Makes This Special?

Picture this: Your AI assistant analyzes your entire Spring codebase, creates a comprehensive upgrade plan, executes it step-by-step, and generates beautiful documentation with architecture diagrams - all while you focus on what matters. It discovers:

- 🔍 **Intelligent Analysis** - AI-powered code analysis to identify upgrade impacts
- 📋 **Smart Planning** - Context-aware upgrade strategies with timeline visualization
- 🔧 **Automated Execution** - OpenRewrite recipes applied with AI validation
- ✅ **Quality Assurance** - Continuous validation with comprehensive quality gates
- 📊 **Rich Documentation** - Interactive HTML reports with Mermaid diagrams
- 🏗️ **Architecture Artifacts** - C4, sequence, class, and state diagrams

But here's the **real magic** ✨ - this isn't just automation! It's a **living, breathing AI assistant** powered by MCP where:

- **Tools dynamically adapt** based on your project's specific needs
- **Prompts evolve** as the upgrade progresses through phases
- **Real-time notifications** keep you informed of critical decisions
- **AI insights** guide you through complex migration challenges
- **Documentation generation** creates professional-grade reports automatically

### 🎯 Perfect for Enterprise Spring Upgrades!

Whether you're upgrading a monolith or a microservices architecture, this MCP server delivers:

- **AI-Powered Analysis** - Understands your codebase context deeply
- **Risk Assessment** - Identifies potential breaking changes before they break
- **Automated Testing** - Ensures quality gates are met at every step
- **Documentation Generation** - Creates comprehensive upgrade reports with visualizations
- **Metadata Extraction** - Captures project configuration and structure

## Overview

The Spring Upgrade MCP Server combines Spring AI capabilities with the Model Context Protocol to provide an intelligent upgrade assistant. This server maintains upgrade state and provides dynamic tools for:

- **State Management**: Tracks upgrade progress, validation results, and rollback points
- **Tools as Upgrade Actions**: AI-driven tools for analysis, execution, validation, and documentation
- **Prompts as Intelligence**: Context-aware prompts that adapt to your project
- **Spring AI Integration**: Leverages LLMs for intelligent decision-making
- **Documentation Generation**: Creates comprehensive reports with architecture diagrams

## Features

- **Intelligent Code Analysis**: AI-powered analysis of Spring codebases with pattern recognition
- **Adaptive Upgrade Strategies**: Plans that adjust based on project complexity and risk
- **OpenRewrite Integration**: Automated recipe application with validation and rollback
- **Quality Gate Enforcement**: Ensures test coverage, security, and performance standards
- **MCP Compliant**: Full compatibility with Claude Desktop and other MCP clients
- **Spring AI Powered**: Native Spring AI integration for enhanced intelligence
- **Real-time Progress**: Watch your upgrade unfold with live notifications
- **Rollback Safety**: Checkpoint system for safe experimentation
- **Documentation Engine**: Generates HTML reports with embedded Mermaid diagrams
- **Architecture Analysis**: Creates C4, sequence, class, and state diagrams
- **Metadata Extraction**: Captures application properties, README content, and project structure

### 🎁 Why Your Team Needs This

**DevOps Engineers**, **Architects**, **Development Teams** - everyone benefits from intelligent automation:

- ⚡ **Speed** - Reduce upgrade time from weeks to hours
- 🛡️ **Safety** - AI validates every change before committing
- 📈 **Quality** - Automated test generation ensures >80% coverage
- 🧠 **Intelligence** - Learn from AI insights about your codebase
- 📊 **Documentation** - Professional reports with architecture diagrams
- 🤝 **Collaboration** - Share upgrade reports via GitHub Pages or cloud hosting

*Trust us - your team will wonder how they ever did upgrades manually!*

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

3. Configure Spring AI:
```bash
export OPENAI_API_KEY=your-api-key
# or configure in application.yml
```

4. Build the project:
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

## Upgrade Mechanics

### State
Each upgrade maintains comprehensive state including:
- Current upgrade phase (analysis, planning, execution, validation, documentation)
- Validation results with detailed metrics
- Applied changes with file-level tracking
- Rollback checkpoints for safety
- Quality metrics and test coverage
- Generated documentation artifacts

### Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `analyze_project` | AI-powered project analysis with metadata extraction | `project_path`: path to Spring project, `depth`: analysis depth |
| `create_upgrade_plan` | Generate comprehensive upgrade plan with timeline | `target_version`: target Spring version, `strategy`: upgrade approach |
| `apply_recipes` | Execute OpenRewrite recipes with validation | `recipe_names`: list of recipes, `dry_run`: preview mode |
| `modernize_patterns` | Apply modern Spring patterns (constructor injection, etc.) | `pattern_type`: specific patterns to apply |
| `enhance_tests` | Generate tests to improve coverage | `target_coverage`: desired coverage percentage |
| `validate_upgrade` | Run comprehensive validation suite | `validation_type`: build, test, security, or all |
| `generate_documentation` | Create HTML report with diagrams | `format`: html/markdown/pdf, `include_diagrams`: boolean |
| `extract_metadata` | Extract project metadata and configuration | `include_sections`: array of sections to extract |

### Dynamic Prompts

The server provides context-aware prompts that adapt based on upgrade progress:

- **Analysis prompts**: Tailored to discovered project patterns and complexity
- **Planning prompts**: Strategic guidance based on risk assessment
- **Execution prompts**: Step-by-step guidance through recipe application
- **Validation prompts**: Interpretation of test results and quality metrics
- **Documentation prompts**: Assistance with report customization

### Documentation Generation

The server generates comprehensive documentation including:

- **Interactive HTML Reports** with responsive design
- **Upgrade Timeline** visualization using Mermaid
- **Execution Sequence** diagrams showing the upgrade flow
- **Architecture Diagrams**:
  - C4 Context diagram
  - C4 Container diagram
  - Class diagrams with Spring annotations
  - State diagrams for application lifecycle
- **Metadata Sections** with configuration and project information
- **Change Tracking** with file-level modifications

## Spring AI Integration

The server leverages Spring AI for:

- **Embedding Models**: Code similarity analysis and pattern matching
- **Chat Models**: Interactive upgrade assistance and decision support
- **Vector Stores**: Maintaining upgrade knowledge base with PGVector
- **Function Calling**: Direct integration with upgrade tools
- **Advisors**: Context enhancement and memory management

## MCP Notifications

Real-time notifications keep clients informed:

### Tool Notifications
- New tools become available as upgrade progresses
- Context-specific tools for different project types
- Documentation tools appear after validation

### Prompt Notifications
- Adaptive prompts based on discovered issues
- Decision points that require human input
- Documentation customization options

### Resource Notifications
- Upgrade progress and status updates
- Validation results and metrics
- Generated documentation availability

## Development

### Project Structure

```
├── src/main/java/              # Java source code
│   ├── config/                 # Spring configuration
│   ├── controller/             # MCP request handlers
│   ├── service/               # Business logic
│   │   ├── mcp/              # MCP protocol implementation
│   │   ├── upgrade/          # Upgrade orchestration
│   │   ├── ai/               # Spring AI integration
│   │   ├── validation/       # Quality gates
│   │   └── documentation/    # Report generation
│   ├── model/                 # Domain models
│   └── repository/            # Data persistence
├── src/main/resources/        # Configuration files
│   ├── application.yml        # Spring configuration
│   ├── prompts/              # AI prompt templates
│   ├── recipes/              # OpenRewrite recipes
│   └── templates/            # Documentation templates
│       ├── report-template.html
│       └── mermaid-templates/
├── scripts/                   # Utility scripts
│   ├── upgrade-orchestrator.sh
│   ├── generate-documentation.sh
│   └── extract-metadata.sh
└── src/test/                  # Test suites
```

### Template System

The server includes comprehensive templates for documentation:

- **HTML Report Template** with professional styling
- **Mermaid Diagram Templates**:
  - Timeline template
  - Execution sequence template
  - C4 diagrams templates
  - Architecture diagram templates

### Adding New Features

To extend the upgrade capabilities:

1. Define new tools in the MCP service layer
2. Create corresponding Spring AI chains
3. Add prompts for AI interactions
4. Update documentation templates
5. Register with the MCP server

## Technical Details

### Spring AI Configuration

```yaml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
      chat:
        options:
          model: gpt-4-turbo-preview
          temperature: 0.3
    embedding:
      options:
        model: text-embedding-3-small
    vectorstore:
      pgvector:
        dimensions: 1536
    advisor:
      - type: MessageChatMemoryAdvisor
      - type: QuestionAnswerAdvisor
```

### Quality Gates Configuration

```yaml
quality_gates:
  testing:
    min_coverage: 80
    max_test_execution_time: 15
  security:
    max_critical_vulnerabilities: 0
    max_high_vulnerabilities: 5
  performance:
    max_startup_time: 30
    max_memory_usage: 512
```

### MCP Integration

Built on the official MCP SDK with:
- Full protocol compliance (2025-03-26 specification)
- WebSocket and HTTP transports
- Structured tool definitions with JSON Schema
- Dynamic capability negotiation
- Real-time notifications

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run Spring Upgrade
  uses: spring-upgrade-mcp/action@v1
  with:
    target-version: '6.1.0'
    generate-docs: true
    deploy-to-pages: true
```

### Bitbucket Pipelines
```yaml
- step:
    name: Spring Framework Upgrade
    script:
      - ./scripts/upgrade-orchestrator.sh . 6.1.0
      - ./scripts/generate-documentation.sh
```

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.