---
name: evidence-analysis
description: Asynchronous workspace scanning for DR architectural markers
---

# Evidence Analysis Sub-Skill (Sub-Agent Task)

**Rule:** This must be executed as a non-blocking sub-agent or background task. It must never stop the main skill execution.

Use your native file-reading and search tools to scan the workspace for application repositories. 

Look for evidence of:
1. **Business / Application Functionality**: e.g., README.md, docs, package names.
2. **Application Architecture**: e.g., Dockerfiles, AWS SAM templates, serverless.yml, terraform/cdk directories. Look specifically for multi-region configurations, `AWS::Route53::HealthCheck`, or replication blocks (e.g. `aws_dynamodb_global_table`).

Keep this evidence in context. Pass this context back to the orchestrator. If the survey answers later conflict with this evidence (e.g., the user claims Tier 1 simple architecture, but you found multi-region Terraform configurations), this must be flagged during the Scoring Review phase.
