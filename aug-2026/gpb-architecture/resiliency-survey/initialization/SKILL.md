---
name: initialization
description: Environment, model, and credential detection
---

# Initialization Sub-Skill

This is the first action to perform upon invocation.

1. **Version Check**: State that you are running Resiliency Survey v1.0.0.
2. **Environment Detection**:
   - Identify the IDE and harness you are running in.
   - Identify the LLM model in use.
3. **Credential Check**:
   - Check the local environment for an SSO token or OAuth token (e.g., `AWS_PROFILE`, `SSO_TOKEN`). 
   - Note any findings in your internal context to pass to the Final Step.
