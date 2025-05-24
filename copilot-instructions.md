# Copilot Instructions 🤖

This document provides instructions for GitHub Copilot to effectively work with the prompt library project.

## Project Overview

The prompt-library is a collection of reusable, well-structured prompts designed to enhance AI interactions. These prompts follow a consistent format and are organized by their specific use cases.

## File Structure

```
.
├── .github/
│   └── prompts/
│       └── reusable-prompts/
│           ├── cognitive-mind-gym.prompt.md
│           ├── expert-prompt-engineer.prompt.md
│           ├── prompt-engnineer.prompt.md
│           ├── software-project-requirements.prompt.md
│           └── tutor.prompt.md
├── README.md
└── copilot-instructions.md
```

## Prompt File Format

Each prompt file should follow this structure:

```markdown
---
title: "Prompt Title"
description: "Brief description of the prompt's purpose"
version: "1.0.0"
[optional] author: "Author Name"
[optional] date: "YYYY-MM-DD"
---

# Main Title

## Purpose/Core Responsibilities
[Description of the prompt's main purpose]

## Process/Approach
[Detailed breakdown of how the prompt works]

### Sections
[Various sections specific to the prompt]

## Output Format
[Expected output format if applicable]
```

## Working with Prompts

When working with this project:

1. **File Naming**: Use the format `[prompt-name].prompt.md`
2. **Metadata**: Always include required front matter (title, description, version)
3. **Structure**: Follow the established section hierarchy
4. **Formatting**: Use proper Markdown syntax and maintain consistent styling

## Best Practices

- Keep prompts focused and single-purpose
- Include clear examples where appropriate
- Use consistent formatting and structure
- Document any special requirements or dependencies
- Follow semantic versioning for version numbers

## Version Control

When making changes:

- Update the version number in the front matter
- Document significant changes in commit messages
- Test prompts before committing changes
