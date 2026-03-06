# Memory Management Skill

## Description
Manage the project's structured memory system across six memory types: episodic, semantic, procedural, working, short-term, and long-term. Provides read, write, search, and maintenance operations for project knowledge.

## Triggers
- User asks to "remember" something or references past decisions
- User starts a new task that benefits from historical context
- User asks about project conventions, standards, or past events
- User wants to update or review project knowledge
- A significant decision, incident, or milestone occurs

## Operations

### recall
Search memory for relevant context.

**Inputs**:
- `query`: What to search for (natural language)
- `type` (optional): episodic | semantic | procedural | working | short-term | long-term
- `scope` (optional): repo | user | session

**Steps**:
1. Determine which memory types are relevant to the query
2. For semantic: Read `.github/instructions/*.instructions.md` and `.github/memory/semantic/*.md`
3. For episodic: Search `.github/memory/episodic/*.md` for matching events
4. For procedural: Check `.github/memory/procedural/workflows.md` and `.github/skills/*.skill.md`
5. For working/short-term: Check `/memories/session/` entries tagged `[WORKING]` or `[SESSION]`
6. For long-term: Check `/memories/` entries tagged `[PREFERENCE]` or `[LEARNED]`
7. Return consolidated results ranked by relevance

### store_episodic
Record a significant event or decision.

**Inputs**:
- `title`: Event title
- `category`: ARCH | TECH | INC | MEET | DEBUG | MILE
- `impact`: critical | high | medium | low
- `context`: What prompted this event
- `decision`: What was decided or done
- `rationale`: Why this approach
- `participants` (optional): Who was involved

**Steps**:
1. Generate filename: `.github/memory/episodic/YYYY-MM-DD-{slug}.md`
2. Write the episodic memory file using the standard template
3. Create a summary `/memories/repo/` entry:
   `[EPISODIC] YYYY-MM-DD: {category} - {title}. {one-line summary}`
4. Confirm storage with file path

### store_semantic
Add or update project knowledge.

**Inputs**:
- `category`: architecture | standards | business-rules | domain | api | infrastructure
- `content`: The knowledge to store
- `file` (optional): Which file to update (defaults to appropriate file by category)

**Steps**:
1. Determine target file based on category:
   - architecture/standards/api → `.github/instructions/project-knowledge.instructions.md`
   - business-rules/domain → `.github/memory/semantic/domain-models.md`
   - infrastructure → `.github/memory/semantic/infrastructure.md`
2. Check if content already exists or conflicts with existing knowledge
3. Add or update the content in the appropriate section
4. Create a `/memories/repo/` entry: `[SEMANTIC] {category}: {summary}`
5. Confirm update

### store_procedural
Define or update a workflow.

**Inputs**:
- `name`: Workflow name
- `steps`: Ordered list of steps
- `trigger` (optional): When this workflow applies

**Steps**:
1. Check if workflow already exists in `.github/memory/procedural/workflows.md`
2. Add or update the workflow entry
3. If the workflow is complex enough for a skill file, create `.github/skills/{name}.skill.md`
4. Create a `/memories/` user entry: `[PROCEDURAL] {name}: {summary of steps}`
5. Confirm storage

### track_working
Manage active problem-solving state.

**Inputs**:
- `action`: problem | hypothesis | evidence | resolved
- `content`: The working memory content
- `status` (optional for hypothesis): investigating | eliminated | confirmed

**Steps**:
1. Create a `/memories/session/` entry with appropriate tag:
   - problem: `[WORKING] Problem: {content}`
   - hypothesis: `[WORKING] Hypothesis: {content} - Status: {status}`
   - evidence: `[WORKING] Evidence: {content}`
   - resolved: `[WORKING] Resolved: {content}`
2. If resolved, check if the solution should be promoted:
   - Reusable pattern → promote to procedural
   - New rule discovered → promote to semantic
   - Significant event → promote to episodic
3. Confirm entry

### update_session
Track session context.

**Inputs**:
- `action`: task | modified | decision | context_save
- `content`: The session context

**Steps**:
1. Create a `/memories/session/` entry:
   - task: `[SESSION] Task: {content}`
   - modified: `[SESSION] Modified: {content}`
   - decision: `[SESSION] Decision: {content}`
   - context_save: `[SESSION] Context saved: {content}`
2. Check session entry count; if > 15, prune completed items
3. Confirm entry

### learn_preference
Record or update a long-term preference.

**Inputs**:
- `category`: code-style | architecture | testing | git | tooling | workflow
- `preference`: The preference description
- `confidence`: 0.0 to 1.0 (based on observation count)

**Steps**:
1. Check if a similar preference already exists in `/memories/`
2. If exists: update with `str_replace` and increase confidence
3. If new: create entry `[PREFERENCE] {category}: {preference}`
4. Confirm storage with confidence level

### maintenance
Review and maintain memory health.

**Steps**:
1. List all memory files and their last-modified dates
2. Identify stale entries (> 6 months without update)
3. Check for contradictions between episodic and semantic entries
4. Report memory statistics:
   - Total episodic entries
   - Semantic knowledge sections
   - Procedural workflows defined
   - Long-term preferences stored
5. Suggest maintenance actions (archive, update, consolidate)

## Validation
After any store operation:
- Verify the file was written or memory entry was created
- Check for conflicts with existing memories
- Confirm the memory type and scope are correct
- Report success or failure with details
