# Pattern 27: Infrastructure Drift Detection

## Category
Multi-environment Workflows

## Overview

A sub-agent compares the declared Terraform or CloudFormation state against the live cloud resource inventory (via a Bash call to the cloud CLI). Drift items are categorized as safe drift, risky drift, or unauthorized change, and routed to the appropriate owner.

## Complete File Implementations

### Skill — `.claude/skills/infra-drift/SKILL.md`

```yaml
---
name: infra-drift
description: >
  Detects infrastructure drift by comparing declared IaC state against live
  cloud resources. Categorizes drift by risk level. Use for periodic
  infrastructure audits or before applying IaC changes.
argument-hint: "[provider: aws|gcp|azure] [scope: all|module-name]"
disable-model-invocation: true
allowed-tools: Read, Bash
---

Detect infrastructure drift: $ARGUMENTS

1. Invoke `infra-drift-detector` sub-agent
2. Present drift items categorized by severity:
   - **Safe drift**: cosmetic or expected differences (tags, descriptions)
   - **Risky drift**: security group changes, IAM modifications, networking
   - **Unauthorized changes**: resources not in IaC at all
3. For each risky/unauthorized item, suggest remediation (update IaC or revert cloud)
```

### Sub-agent — `.claude/agents/infra-drift-detector.md`

```yaml
---
name: infra-drift-detector
description: >
  Compares IaC declarations against live cloud state to detect drift.
  Read-only — never modifies infrastructure.
model: claude-opus-4-5
tools: [Read, Bash]
disallowedTools: [Write, Edit, MultiEdit]
maxTurns: 15
---

Detect infrastructure drift.

1. Read IaC files (Terraform `.tf`, CloudFormation `.yaml`)
2. Run plan/diff commands:
   - Terraform: `terraform plan -detailed-exitcode -no-color`
   - CloudFormation: `aws cloudformation detect-stack-drift`
3. Parse the output to identify drift items
4. Categorize each item:
   - **Safe**: tag changes, description updates, non-functional metadata
   - **Risky**: security groups, IAM policies, network ACLs, encryption settings
   - **Unauthorized**: resources in cloud not declared in IaC

Write to `.claude/infra/drift-report.json`:
```json
{
  "provider": "aws",
  "total_resources": 45,
  "drifted": 5,
  "items": [
    {
      "resource": "aws_security_group.api",
      "category": "risky",
      "declared": { "ingress_cidr": ["10.0.0.0/16"] },
      "actual": { "ingress_cidr": ["0.0.0.0/0"] },
      "owner": "platform-team",
      "remediation": "Revert cloud to match IaC — open ingress is a security risk"
    }
  ]
}
```
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(terraform plan:*)",
      "Bash(terraform show:*)",
      "Bash(aws cloudformation:*)",
      "Bash(aws ec2 describe-*)",
      "Bash(gcloud *)",
      "Bash(cat *.tf)",
      "Bash(find * -name *.tf)",
      "Bash(mkdir -p .claude/infra)"
    ],
    "deny": [
      "Bash(terraform apply:*)",
      "Bash(terraform destroy:*)",
      "Bash(aws * delete-*)",
      "Bash(aws * terminate-*)"
    ]
  }
}
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Detector modifies infrastructure | `disallowedTools: [Write, Edit]`; `deny` list blocks apply/destroy commands |
| Cloud CLI credentials exposed | Use IAM roles or env var references; never hardcode credentials |
| Drift report misses resources | Combine IaC plan output with cloud inventory listing for completeness |
