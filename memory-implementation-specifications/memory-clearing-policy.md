# Memory Clearing Policy

## Overview and Principles

Memory accumulates. Without a clearing policy, episodic logs grow noisy, stale context misleads agents, and storage bloats. This document defines **what gets cleared, when, by what mechanism, and how it is enforced** for both GitHub Copilot and Claude Code.

### Core Principles

1. **Clearing is not deletion — it is lifecycle management.** Entries transition from active to archived to deleted. Only truly obsolete data is removed.
2. **The policy is opinionated with escape hatches.** Defaults are concrete and enforced. Teams customize thresholds, not mechanisms.
3. **Source-of-truth files are never silently deleted.** Automated clearing moves entries to `_archive/` and opens a PR for human review. Only manual confirmation deletes permanently.
4. **Session-scoped memory clears itself.** Working and short-term memory are ephemeral by design. No policy needed — the platform handles it.
5. **Semantic and procedural memory do not expire.** Knowledge and workflows are maintained, not cleared. They are reviewed for accuracy, not age.

## Retention Schedule

| Memory Type | Active Retention | Archive Retention | Max Active Entries | Clearing Trigger | Automation Level |
|---|---|---|---|---|---|
| **Episodic** | 180 days | +180 days (360 total) | 200 files | Time + count, weekly check | Fully automated (PR-based) |
| **Semantic** | No expiration | N/A | No limit | Manual quarterly review | Manual only |
| **Procedural** | No expiration | N/A | No limit | Manual quarterly review | Manual only |
| **Working** | Session end | N/A | N/A | Automatic (platform) | Platform-native |
| **Short-term** | Session end | N/A | N/A | Automatic (platform) | Platform-native |
| **Long-term** | No expiration | N/A | 200 lines (Claude MEMORY.md) | Manual biannual review | Manual only |

### Customizable Thresholds

Teams should adjust these based on project activity:

| Parameter | Default | Low-activity Projects | High-activity Projects |
|---|---|---|---|
| `EPISODIC_ACTIVE_DAYS` | 180 | 365 | 90 |
| `EPISODIC_ARCHIVE_DAYS` | 180 | 365 | 90 |
| `EPISODIC_MAX_ACTIVE` | 200 | 100 | 500 |
| `SEMANTIC_REVIEW_INTERVAL` | Quarterly | Biannually | Monthly |
| `LONG_TERM_REVIEW_INTERVAL` | Biannually | Annually | Quarterly |

## Episodic Memory Clearing: Detailed Rules

### What Gets Cleared

An episodic entry is eligible for archiving when **all** of these are true:

1. Its `date` field in YAML frontmatter is older than `EPISODIC_ACTIVE_DAYS` (default: 180 days)
2. Its `retain` field is not `true`
3. It is not referenced by a `related` field in any active (non-archived) entry

### What Never Gets Cleared

- Entries with `retain: true` in frontmatter (permanent entries)
- Entries with `impact: critical` (auto-set to `retain: true` by convention)
- Entries referenced by active entries (dependency chain protection)

### Clearing Lifecycle

```
Active (.github/memory/episodic/ or .claude/memory/episodic/)
  │
  │  After EPISODIC_ACTIVE_DAYS (180 days), if not retained:
  ▼
Archived (_archive/ subdirectory, same parent)
  │
  │  After EPISODIC_ARCHIVE_DAYS (180 more days):
  ▼
Deleted (removed from repository via PR)
```

### Archive Directory Structure

```
.github/memory/episodic/          # Active entries (Copilot)
.github/memory/episodic/_archive/ # Archived entries (Copilot)

.claude/memory/episodic/          # Active entries (Claude Code)
.claude/memory/episodic/_archive/ # Archived entries (Claude Code)
```

Archived entries keep their original filename. They remain in git history even after final deletion.

## Semantic Memory Clearing: Review Protocol

Semantic memory does not expire, but it can become **stale** (facts change) or **contradictory** (rules conflict). The clearing mechanism is a manual review, not automated deletion.

### Quarterly Review Checklist

```markdown
- [ ] Read all `.github/instructions/*.instructions.md` (Copilot) or `CLAUDE.md` (Claude Code)
- [ ] Check: Are project facts still accurate? (language versions, hosting, dependencies)
- [ ] Check: Are coding standards still followed? Remove any that the team has abandoned.
- [ ] Check: Are business rules still valid? Update or remove changed rules.
- [ ] Read `.github/memory/semantic/*.md` or `.claude/memory/semantic/*.md`
- [ ] Check: Are domain models current? Do entities match the actual database schema?
- [ ] Check: Are there contradictions between files? (e.g., CLAUDE.md says X, semantic file says Y)
- [ ] Remove superseded sections. Do not leave commented-out rules — delete them cleanly.
- [ ] Update "last reviewed" date at the top of each file.
```

### Agent Self-Enforcement (Semantic)

Add to instructions/CLAUDE.md:

> When you notice that a semantic memory entry contradicts what you observe in the codebase (e.g., a documented standard that the code does not follow), flag it to the user: "I notice that [standard X] in memory doesn't match the current code. Should I update the memory or the code?"

## Procedural Memory Clearing: Deprecation Protocol

Procedural workflows do not expire, but they can become **deprecated** (replaced by a new workflow) or **broken** (tooling changed).

### Deprecation Steps

1. Add a deprecation notice at the top of the workflow file:

   ```markdown
   > **DEPRECATED** (YYYY-MM-DD): Replaced by [new-workflow.md]. Remove after [date].
   ```

2. After 90 days, delete the deprecated file.
3. If using the `_index.json` approach for procedural files, remove the entry.

## Long-term Memory Clearing: Preference Hygiene

Long-term memory (user preferences) does not expire but can become **contradicted** (user changed their mind) or **stale** (preference no longer relevant).

### Biannual Review Checklist

For Claude Code (`MEMORY.md`):

```markdown
- [ ] Read ~/.claude/projects/<path>/memory/MEMORY.md
- [ ] For each preference: Is this still true? Have I changed my mind?
- [ ] Remove preferences that are no longer relevant
- [ ] Update preferences that have evolved
- [ ] Check linked detail files — are they still accurate?
- [ ] Verify MEMORY.md is under 200 lines
```

For GitHub Copilot (`/memories/`):

```markdown
- [ ] Run: @copilot /memories/ view
- [ ] Review each [PREFERENCE] and [LEARNED] entry
- [ ] Delete entries that are no longer accurate
- [ ] Update entries that have evolved
```

## Implementation: GitHub Copilot

### Manual Clearing

**Native `/memories/` scopes**:

```
# View all user memories
@copilot /memories/ view

# Delete a specific memory
@copilot /memories/ delete [memory-id-or-content-match]

# Session memories clear automatically — no action needed
# Repo memories: ask Copilot to delete specific entries
@copilot /memories/repo/ view
```

**File-based (Track A)**:

```bash
# List episodic entries older than 180 days
jq --arg cutoff "$(date -d '-180 days' +%Y-%m-%d 2>/dev/null || date -v-180d +%Y-%m-%d)" \
  '[.[] | select(.date < $cutoff and .retain != true)]' \
  .github/memory/episodic/_index.json

# Move eligible entries to archive
mkdir -p .github/memory/episodic/_archive
for file in $(jq -r --arg cutoff "$(date -d '-180 days' +%Y-%m-%d 2>/dev/null || date -v-180d +%Y-%m-%d)" \
  '.[] | select(.date < $cutoff and .retain != true) | .file' \
  .github/memory/episodic/_index.json); do
  git mv ".github/memory/episodic/$file" ".github/memory/episodic/_archive/$file"
done

# Delete entries archived more than 180 days ago
for file in $(jq -r --arg cutoff "$(date -d '-360 days' +%Y-%m-%d 2>/dev/null || date -v-360d +%Y-%m-%d)" \
  '.[] | select(.date < $cutoff and .retain != true) | .file' \
  .github/memory/episodic/_index.json); do
  git rm ".github/memory/episodic/_archive/$file" 2>/dev/null || true
done
```

### Automated Clearing: GitHub Actions Workflow

#### File: `.github/workflows/memory-clearing.yml`

```yaml
name: Memory Clearing

on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9:00 UTC
  workflow_dispatch:
    inputs:
      dry_run:
        description: 'Dry run (no changes)'
        required: false
        default: 'true'
        type: choice
        options: ['true', 'false']

permissions:
  contents: write
  pull-requests: write

jobs:
  clear-episodic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: pip install pyyaml

      - name: Run episodic memory clearing
        id: clear
        env:
          EPISODIC_ACTIVE_DAYS: 180
          EPISODIC_ARCHIVE_DAYS: 180
          DRY_RUN: ${{ github.event.inputs.dry_run || 'false' }}
          # Detect platform: check which directory exists
        run: |
          if [ -d ".github/memory/episodic" ]; then
            EPISODIC_DIR=".github/memory/episodic"
          elif [ -d ".claude/memory/episodic" ]; then
            EPISODIC_DIR=".claude/memory/episodic"
          else
            echo "No episodic memory directory found. Exiting."
            exit 0
          fi

          python3 << 'PYTHON_SCRIPT'
          import json, re, glob, os, shutil
          from datetime import datetime, timedelta

          try:
              import yaml
          except ImportError:
              print("PyYAML not installed. Skipping.")
              exit(0)

          episodic_dir = os.environ.get("EPISODIC_DIR", ".github/memory/episodic")
          active_days = int(os.environ.get("EPISODIC_ACTIVE_DAYS", "180"))
          archive_days = int(os.environ.get("EPISODIC_ARCHIVE_DAYS", "180"))
          dry_run = os.environ.get("DRY_RUN", "false") == "true"

          archive_dir = os.path.join(episodic_dir, "_archive")
          cutoff_archive = (datetime.now() - timedelta(days=active_days)).strftime("%Y-%m-%d")
          cutoff_delete = (datetime.now() - timedelta(days=active_days + archive_days)).strftime("%Y-%m-%d")

          archived = []
          deleted = []

          # Phase 1: Archive old active entries
          for path in sorted(glob.glob(os.path.join(episodic_dir, "*.md"))):
              if "TEMPLATE" in path:
                  continue
              with open(path) as f:
                  content = f.read()
              match = re.match(r"^---\n(.+?)\n---", content, re.DOTALL)
              if not match:
                  continue
              meta = yaml.safe_load(match.group(1))
              entry_date = str(meta.get("date", ""))
              retain = meta.get("retain", False)
              impact = meta.get("impact", "")

              if retain or impact == "critical":
                  continue
              if entry_date and entry_date < cutoff_archive:
                  dest = os.path.join(archive_dir, os.path.basename(path))
                  if dry_run:
                      print(f"[DRY RUN] Would archive: {path} -> {dest}")
                  else:
                      os.makedirs(archive_dir, exist_ok=True)
                      shutil.move(path, dest)
                      print(f"Archived: {path} -> {dest}")
                  archived.append(os.path.basename(path))

          # Phase 2: Delete old archived entries
          if os.path.isdir(archive_dir):
              for path in sorted(glob.glob(os.path.join(archive_dir, "*.md"))):
                  with open(path) as f:
                      content = f.read()
                  match = re.match(r"^---\n(.+?)\n---", content, re.DOTALL)
                  if not match:
                      continue
                  meta = yaml.safe_load(match.group(1))
                  entry_date = str(meta.get("date", ""))
                  retain = meta.get("retain", False)

                  if retain:
                      continue
                  if entry_date and entry_date < cutoff_delete:
                      if dry_run:
                          print(f"[DRY RUN] Would delete: {path}")
                      else:
                          os.remove(path)
                          print(f"Deleted: {path}")
                      deleted.append(os.path.basename(path))

          # Phase 3: Rebuild _index.json
          if not dry_run and (archived or deleted):
              entries = []
              for path in sorted(glob.glob(os.path.join(episodic_dir, "*.md"))):
                  if "TEMPLATE" in path:
                      continue
                  with open(path) as f:
                      content = f.read()
                  match = re.match(r"^---\n(.+?)\n---\n(.+)", content, re.DOTALL)
                  if not match:
                      continue
                  meta = yaml.safe_load(match.group(1))
                  body = match.group(2)
                  title_match = re.search(r"^# (.+)$", body, re.MULTILINE)
                  entries.append({
                      "file": os.path.basename(path),
                      "date": str(meta.get("date", "")),
                      "category": meta.get("category", ""),
                      "impact": meta.get("impact", ""),
                      "tags": meta.get("tags", []),
                      "title": title_match.group(1) if title_match else os.path.basename(path),
                      "retain": meta.get("retain", False),
                  })
              index_path = os.path.join(episodic_dir, "_index.json")
              with open(index_path, "w") as f:
                  json.dump(entries, f, indent=2)
              print(f"Rebuilt index: {len(entries)} active entries")

          # Summary
          print(f"\n--- Summary ---")
          print(f"Archived: {len(archived)} entries")
          print(f"Deleted:  {len(deleted)} entries")

          with open(os.environ.get("GITHUB_OUTPUT", "/dev/null"), "a") as f:
              f.write(f"archived={len(archived)}\n")
              f.write(f"deleted={len(deleted)}\n")
              f.write(f"changes={'true' if (archived or deleted) and not dry_run else 'false'}\n")
          PYTHON_SCRIPT

      - name: Create PR with clearing changes
        if: steps.clear.outputs.changes == 'true'
        run: |
          BRANCH="chore/memory-clearing-$(date +%Y-%m-%d)"
          git checkout -b "$BRANCH"
          git add -A
          git commit -m "$(cat <<'EOF'
          chore: clear stale episodic memory entries

          Automated memory clearing per memory-clearing-policy.md.
          - Archived entries older than ${{ env.EPISODIC_ACTIVE_DAYS || 180 }} days
          - Deleted entries archived longer than ${{ env.EPISODIC_ARCHIVE_DAYS || 180 }} days
          - Rebuilt _index.json

          Co-Authored-By: github-actions[bot] <github-actions[bot]@users.noreply.github.com>
          EOF
          )"
          git push origin "$BRANCH"
          gh pr create \
            --title "chore: clear stale episodic memory entries" \
            --body "$(cat <<'EOF'
          ## Automated Memory Clearing

          This PR was generated by the memory clearing policy automation.

          - **Archived**: ${{ steps.clear.outputs.archived }} entries moved to `_archive/`
          - **Deleted**: ${{ steps.clear.outputs.deleted }} entries permanently removed
          - **Policy**: entries older than 180 days archived, archived entries older than 360 days deleted
          - Entries with `retain: true` or `impact: critical` are never cleared

          Review the changes and merge if they look correct. See `memory-clearing-policy.md` for details.
          EOF
          )"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  lint-frontmatter:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: pip install pyyaml

      - name: Validate episodic frontmatter
        run: |
          if [ -d ".github/memory/episodic" ]; then
            EPISODIC_DIR=".github/memory/episodic"
          elif [ -d ".claude/memory/episodic" ]; then
            EPISODIC_DIR=".claude/memory/episodic"
          else
            echo "No episodic memory directory found."
            exit 0
          fi

          python3 << 'PYTHON_SCRIPT'
          import re, glob, sys, os

          try:
              import yaml
          except ImportError:
              print("PyYAML not installed.")
              sys.exit(0)

          episodic_dir = os.environ.get("EPISODIC_DIR", ".github/memory/episodic")
          required_keys = {"date", "category", "impact"}
          valid_categories = {"ARCH", "TECH", "INC", "MEET", "DEBUG", "MILE"}
          valid_impacts = {"critical", "high", "medium", "low"}
          errors = []

          for path in sorted(glob.glob(os.path.join(episodic_dir, "*.md"))):
              if "TEMPLATE" in path:
                  continue
              with open(path) as f:
                  content = f.read()
              match = re.match(r"^---\n(.+?)\n---", content, re.DOTALL)
              if not match:
                  errors.append(f"{path}: missing YAML frontmatter")
                  continue
              try:
                  meta = yaml.safe_load(match.group(1))
              except yaml.YAMLError as e:
                  errors.append(f"{path}: invalid YAML: {e}")
                  continue
              missing = required_keys - set(meta.keys())
              if missing:
                  errors.append(f"{path}: missing required keys: {missing}")
              if meta.get("category") not in valid_categories:
                  errors.append(f"{path}: invalid category '{meta.get('category')}' (valid: {valid_categories})")
              if meta.get("impact") not in valid_impacts:
                  errors.append(f"{path}: invalid impact '{meta.get('impact')}' (valid: {valid_impacts})")

          if errors:
              print("Frontmatter validation errors:")
              for e in errors:
                  print(f"  - {e}")
              sys.exit(1)
          else:
              print("All episodic entries have valid frontmatter.")
          PYTHON_SCRIPT
```

## Implementation: Claude Code

### Manual Clearing

**File-based (Track A)**:

Claude Code can perform clearing directly during a session. Add this to your `CLAUDE.md`:

```markdown
## Memory Maintenance Protocol

When asked to perform memory maintenance, or when episodic entries exceed 200:

1. List all episodic entries: `Glob .claude/memory/episodic/*.md`
2. For each entry, read the YAML frontmatter (first 10 lines)
3. Identify entries older than 180 days without `retain: true`
4. Move eligible entries to `.claude/memory/episodic/_archive/`
5. Report what was archived and what was retained
6. Rebuild `_index.json` if it exists
```

**MEMORY.md maintenance**:

```markdown
## MEMORY.md Maintenance

When MEMORY.md exceeds 200 lines or user requests a review:

1. Read current MEMORY.md
2. For each preference: check if it's still observed in recent sessions
3. Remove contradicted or stale entries
4. Consolidate redundant entries
5. Move detailed notes to linked files
6. Verify final line count is under 200
```

**Agent-initiated clearing** — Claude Code can self-trigger maintenance. Add to `CLAUDE.md`:

```markdown
## Auto-Maintenance Trigger

At the start of each session, if you notice:
- More than 200 files when listing `.claude/memory/episodic/*.md`
- MEMORY.md is approaching 200 lines
- Contradictions between memory files and observed code

Then suggest: "Memory maintenance is overdue. Shall I review and clear stale entries?"
```

### Automated Clearing (Same GitHub Action)

The GitHub Actions workflow above detects both `.github/memory/episodic/` (Copilot) and `.claude/memory/episodic/` (Claude Code) directories. It works for both platforms without modification.

For Claude Code projects that don't use GitHub Actions, use a cron job or git hook instead:

```bash
# crontab entry: run weekly on Monday at 9am
0 9 * * 1 cd /path/to/project && python3 .claude/scripts/clear-episodic.py
```

## Git Hook: Rebuild Index on Commit

### File: `.git/hooks/post-commit`

```bash
#!/usr/bin/env bash
# Rebuild episodic _index.json if any episodic files changed in this commit.
set -euo pipefail

# Detect platform directory
if [ -d ".github/memory/episodic" ]; then
  EPISODIC_DIR=".github/memory/episodic"
elif [ -d ".claude/memory/episodic" ]; then
  EPISODIC_DIR=".claude/memory/episodic"
else
  exit 0
fi

# Check if any episodic files were modified in this commit
CHANGED=$(git diff-tree --no-commit-id --name-only -r HEAD -- "$EPISODIC_DIR/*.md" 2>/dev/null || true)
if [ -z "$CHANGED" ]; then
  exit 0
fi

echo "Episodic files changed. Rebuilding _index.json..."

python3 -c "
import json, re, glob, os
try:
    import yaml
except ImportError:
    print('PyYAML not installed, skipping index rebuild.')
    exit(0)

episodic_dir = '$EPISODIC_DIR'
entries = []
for path in sorted(glob.glob(os.path.join(episodic_dir, '*.md'))):
    if 'TEMPLATE' in path:
        continue
    with open(path) as f:
        content = f.read()
    match = re.match(r'^---\n(.+?)\n---\n(.+)', content, re.DOTALL)
    if not match:
        continue
    meta = yaml.safe_load(match.group(1))
    body = match.group(2)
    title_match = re.search(r'^# (.+)$', body, re.MULTILINE)
    entries.append({
        'file': os.path.basename(path),
        'date': str(meta.get('date', '')),
        'category': meta.get('category', ''),
        'impact': meta.get('impact', ''),
        'tags': meta.get('tags', []),
        'title': title_match.group(1) if title_match else os.path.basename(path),
        'retain': meta.get('retain', False),
    })
index_path = os.path.join(episodic_dir, '_index.json')
with open(index_path, 'w') as f:
    json.dump(entries, f, indent=2)
print(f'Rebuilt {len(entries)} entries in {index_path}')
"

# Stage the updated index
git add "$EPISODIC_DIR/_index.json"

# Amend the commit to include the updated index (silent, no editor)
git commit --amend --no-edit --quiet
```

**Installation**:

```bash
# Copy to .git/hooks/ and make executable
cp .github/scripts/post-commit-hook.sh .git/hooks/post-commit
chmod +x .git/hooks/post-commit

# Or use a hook manager like husky:
# npx husky add .husky/post-commit ".github/scripts/post-commit-hook.sh"
```

## Agent Self-Enforcement Instructions

These instructions should be included in `copilot-memory.instructions.md` or `CLAUDE.md` so agents enforce the clearing policy during normal operation.

### For GitHub Copilot (add to `.github/instructions/`)

```markdown
## Memory Clearing Policy

You must respect the following clearing rules:

- **Before creating an episodic entry**: Check if the episodic directory has more than 200 files.
  If yes, suggest memory maintenance before adding more entries.
- **When reading old episodic entries**: If an entry's date is more than 180 days old and it
  does not have `retain: true`, note that it is eligible for archiving.
- **When you notice contradictions**: If a semantic memory file contradicts the current codebase,
  flag it to the user immediately.
- **When updating long-term preferences**: Check if the update contradicts an existing preference.
  If so, remove the old one — do not leave both.
- **Never delete entries silently**: Always inform the user before archiving or removing memory entries.
```

### For Claude Code (add to `CLAUDE.md`)

```markdown
## Memory Clearing Policy

Enforce these rules during normal operation:

- Before creating an episodic entry, run `Glob .claude/memory/episodic/*.md` to count entries.
  If count exceeds 200, suggest maintenance: "There are N episodic entries. Shall I archive stale ones?"
- When reading an episodic entry older than 180 days without `retain: true`, note:
  "This entry is eligible for archiving per the clearing policy."
- When you notice a semantic memory contradicts the codebase, flag it immediately.
- When updating MEMORY.md, check line count. If approaching 200 lines, suggest consolidation.
- Never delete memory entries without user confirmation.
- After archiving entries, rebuild `_index.json` if it exists.
```

## Emergency Clear Procedure

For situations where memory is corrupted, massively stale, or a fresh start is needed.

### Full Reset — GitHub Copilot

```bash
# 1. Clear all file-based memory (preserves git history)
rm -rf .github/memory/episodic/*.md
rm -rf .github/memory/episodic/_archive/
rm -f  .github/memory/episodic/_index.json
# Keep TEMPLATE.md:
git checkout -- .github/memory/episodic/TEMPLATE.md 2>/dev/null || true

# 2. Semantic and procedural: do NOT delete — review and update instead
# These represent project knowledge, not temporal data

# 3. Clear native Copilot memories (must be done in chat)
# @copilot /memories/ view
# Then selectively: @copilot /memories/ delete [each entry]
# Session memories auto-clear — no action needed

# 4. Commit
git add -A
git commit -m "chore: emergency clear of episodic memory — fresh start"
```

### Full Reset — Claude Code

```bash
# 1. Clear all file-based episodic memory
rm -rf .claude/memory/episodic/*.md
rm -rf .claude/memory/episodic/_archive/
rm -f  .claude/memory/episodic/_index.json
# Keep TEMPLATE.md:
git checkout -- .claude/memory/episodic/TEMPLATE.md 2>/dev/null || true

# 2. Semantic and procedural: do NOT delete — review and update
# 3. Reset MEMORY.md to a clean state
cat > ~/.claude/projects/<project-path>/memory/MEMORY.md << 'EOF'
# Project Memory

## User Preferences
<!-- Re-add preferences as they are confirmed -->

## Learned Patterns
<!-- Will be populated as patterns are observed -->

## Project-Specific Knowledge
<!-- Add important context as it emerges -->
EOF

# 4. Commit project changes
git add -A
git commit -m "chore: emergency clear of episodic memory — fresh start"
```

### Partial Reset — Episodic Only

```bash
# Archive everything older than 30 days (aggressive clearing)
CUTOFF=$(date -d '-30 days' +%Y-%m-%d 2>/dev/null || date -v-30d +%Y-%m-%d)
# Then use the jq + git mv commands from the Manual Clearing section above
```

## Policy Documentation: Where This Lives in the Repo

This file (`memory-clearing-policy.md`) is the canonical reference. It should be:

1. **Linked from CLAUDE.md / instructions files**: Add a one-liner reference:
   > Memory clearing follows the policy in `memory-implementation-specifications/memory-clearing-policy.md`.

2. **Not loaded into agent context**: This file is too long for agent context. Agents receive the abbreviated self-enforcement instructions (above) in their instruction files. This file is for human operators.

3. **Reviewed annually**: The policy itself should be reviewed once per year to check if thresholds are still appropriate for the team's activity level.
