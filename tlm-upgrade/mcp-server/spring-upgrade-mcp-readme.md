# Spring Upgrade MCP Server 🚀⚙️🔧

*An intelligent Spring Framework upgrade assistant powered by the Model Context Protocol (MCP) and Spring AI - designed to automate complex upgrade processes with AI-driven insights!*

## 🎯 Automate Your Spring Framework Upgrades with AI!

**Tired of manual dependency conflicts and breaking changes?** Let AI guide your Spring Framework upgrades with confidence! The Spring Upgrade MCP Server combines the power of Large Language Models with automated tooling to make upgrades seamless and reliable.

### 🌟 What Makes This Special?

Picture this: Your AI assistant analyzes your entire Spring codebase, creates a comprehensive upgrade plan, and executes it step-by-step while you focus on what matters. It discovers:

- 🔍 **Intelligent Analysis** - AI-powered code analysis to identify upgrade impacts
- 📋 **Smart Planning** - Context-aware upgrade strategies tailored to your project  
- 🔧 **Automated Execution** - OpenRewrite recipes applied with AI validation
- ✅ **Quality Assurance** - Continuous validation with AI-driven insights
- 📊 **Rich Documentation** - Comprehensive reports with architecture diagrams

But here's the **real magic** ✨ - this isn't just automation! It's a **living, breathing AI assistant** powered by MCP where:

- **Tools dynamically adapt** based on your project's specific needs
- **Prompts evolve** as the upgrade progresses through phases
- **Real-time notifications** keep you informed of critical decisions
- **AI insights** guide you through complex migration challenges

### 🎯 Perfect for Enterprise Spring Upgrades!

Whether you're upgrading a monolith or a microservices architecture, this MCP server delivers:

- **AI-Powered Analysis** - Understands your codebase context deeply
- **Risk Assessment** - Identifies potential breaking changes before they break
- **Automated Testing** - Ensures quality gates are met at every step
- **Documentation Generation** - Creates comprehensive upgrade reports

## Overview

The Spring Upgrade MCP Server combines Spring AI capabilities with the Model Context Protocol to provide an intelligent upgrade assistant. This server maintains upgrade state and provides dynamic tools for:

- **State Management**: Tracks upgrade progress, validation results, and rollback points
- **Tools as Upgrade Actions**: AI-driven tools for analysis, execution, and validation
- **Prompts as Intelligence**: Context-aware prompts that adapt to your project
- **Spring AI Integration**: Leverages LLMs for intelligent decision-making

## Features

- **Intelligent Code Analysis**: AI-powered analysis of Spring codebases
- **Adaptive Upgrade Strategies**: Plans that adjust based on project complexity
- **OpenRewrite Integration**: Automated recipe application with validation
- **Quality Gate Enforcement**: Ensures standards are met before proceeding
- **MCP Compliant**: Full compatibility with Claude Desktop and other MCP clients
- **Spring AI Powered**: Native Spring AI integration for enhanced intelligence
- **Real-time Progress**: Watch your upgrade unfold with live notifications
- **Rollback Safety**: Checkpoint system for safe experimentation

### 🎁 Why Your Team Needs This

**DevOps Engineers**, **Architects**, **Development Teams** - everyone benefits from intelligent automation:

- ⚡ **Speed** - Reduce upgrade time from weeks to hours
- 🛡️ **Safety** - AI validates every change before committing
- 📈 **Quality** - Automated test generation ensures coverage
- 🧠 **Intelligence** - Learn from AI insights about your codebase
- 🤝 **Collaboration** - Share upgrade reports and documentation

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
- Current upgrade phase
- Validation results
- Applied changes
- Rollback checkpoints
- Quality metrics

### Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `analyze_project` | AI-powered project analysis | `project_path`: path to Spring project |
| `create_upgrade_plan` | Generate comprehensive upgrade plan | `target_version`: target Spring version |
| `apply_recipes` | Execute OpenRewrite recipes | `recipe_names`: list of recipes to apply |
| `validate_upgrade` | Run comprehensive validation | `validation_type`: build, test, security, or all |
| `generate_report` | Create upgrade documentation | `report_format`: html, markdown, or pdf |

### Dynamic Prompts

The server adjusts prompts based on upgrade context:

- **Analysis prompts**: Tailored to discovered project patterns
- **Decision prompts**: Appear when AI needs guidance
- **Validation prompts**: Context-aware quality checks

## Spring AI Integration

The server leverages Spring AI for:

- **Embedding Models**: Code similarity analysis for impact assessment
- **Chat Models**: Interactive upgrade assistance and decision support
- **Vector Stores**: Maintaining upgrade knowledge base
- **Function Calling**: Direct integration with upgrade tools

## MCP Notifications

Real-time notifications keep clients informed:

### Tool Notifications
- New tools become available as upgrade progresses
- Context-specific tools for different project types

### Prompt Notifications
- Adaptive prompts based on discovered issues
- Decision points that require human input

### Resource Notifications
- Upgrade progress and status updates
- Validation results and metrics

## Development

### Project Structure

```
├── src/main/java/          # Java source code
│   ├── config/             # Spring configuration
│   ├── controller/         # MCP request handlers
│   ├── service/           # Business logic
│   │   ├── mcp/          # MCP protocol implementation
│   │   ├── upgrade/      # Upgrade orchestration
│   │   ├── ai/           # Spring AI integration
│   │   └── validation/   # Quality gates
│   ├── model/             # Domain models
│   └── repository/        # Data persistence
├── src/main/resources/    # Configuration files
│   ├── application.yml    # Spring configuration
│   ├── prompts/          # AI prompt templates
│   └── recipes/          # OpenRewrite recipes
└── src/test/             # Test suites
```

### Adding New Features

To extend the upgrade capabilities:

1. Define new tools in the MCP service layer
2. Create corresponding Spring AI chains
3. Add prompts for AI interactions
4. Register with the MCP server

## Technical Details

### Spring AI Configuration

The server uses Spring AI with:
- OpenAI for advanced reasoning
- PGVector for upgrade knowledge persistence
- Advisors for context injection
- Function calling for tool integration

### MCP Integration

Built on the official MCP SDK with:
- Full protocol compliance
- WebSocket and HTTP transports
- Structured tool definitions
- Dynamic capability negotiation

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.