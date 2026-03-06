# Known Gaps and Limitations: GitHub Copilot Memory

## Platform Limitations

- **No programmatic memory API**: Copilot's `/memories/` system can only be accessed through chat interaction. There is no REST API, CLI, or SDK to read/write memories programmatically. Automation scripts cannot directly create or query native Copilot memories.

- **Repo-scoped memories are create-only by Copilot**: The `/memories/repo/` scope does not support user-initiated `str_replace`, `insert`, or `delete` operations. Corrections require deleting and recreating entries, which Copilot must do.

- **No conditional memory loading**: `.github/instructions/` files with `applyTo` patterns are file-glob-based only. You cannot conditionally load instructions based on task type, conversation context, or memory state (e.g., "only load security standards when working on auth code").

- **Session memory has no persistence escape hatch**: When a Copilot session ends, all `/memories/session/` entries are lost. There is no built-in mechanism to auto-promote important session memories to permanent scopes before session close.

- **No memory capacity visibility**: There is no way to query how many memories exist, how much capacity remains, or whether memories are being silently truncated. The system provides no feedback on memory limits.

- **No cross-session working memory**: Working memory (problem-solving state) cannot span sessions natively. If a debugging session is interrupted, the investigation context is lost unless manually re-entered.

- **No memory search/filter API**: Native memories cannot be searched by tag, date, type, or content. Retrieval depends on Copilot's internal relevance matching, which is opaque.

- **Instruction file size limits**: `.github/instructions/` files have practical size limits. Very large knowledge bases (10K+ lines) may be truncated or cause performance degradation in Copilot's context window.

## Migration Risks from Existing Templates

The `co-pilot-memory-implementation/` templates were designed for a pre-native-memory era. Migrating to the native system introduces these risks:

- **Over-engineered confidence scoring**: The existing templates include elaborate confidence levels (60%, 80%, 95%) with decimal precision. Copilot's native memory has no confidence metadata. Simplify to 3 tiers (suggest, apply with mention, apply silently) or track confidence externally in file-based entries.

- **Template bloat in instruction files**: The original templates contain hundreds of lines of structure (testing frameworks, ROI metrics, validation checklists). Loading all of this as Copilot instructions would waste context window capacity. Extract only the actionable rules; archive the frameworks as reference documentation.

- **Cross-memory coordination complexity**: The original system defines intricate cross-memory hooks (e.g., "episodic feeds into semantic via pattern validation"). Copilot has no mechanism for automated cross-memory coordination. This must be implemented as agent instructions ("after resolving a problem, check if the solution should become a rule").

- **Testing frameworks are not executable**: The original testing frameworks (e.g., "Context Capture Accuracy > 90%") define metrics but no automation. In the native system, these become qualitative checklists rather than quantitative tests.

- **Procedural memory automation levels don't map**: The original system defines four automation confidence levels (95%+, 80-94%, 60-79%, <60%) with specific behaviors. Copilot skills don't have configurable confidence thresholds. Simplify to "always suggest" or "always execute" based on the skill's maturity.

- **Multi-perspective capture is impractical**: Episodic memory templates include "other perspectives" and "relationship context mapping." Copilot interacts with one user at a time and cannot capture team dynamics. Strip these sections or populate them manually.

## Capabilities Not Yet Available

- **Automatic memory consolidation**: No mechanism to automatically merge related memories, deduplicate similar entries, or summarize old memories into compact forms.

- **Memory versioning**: Native memories have no version history. Once overwritten, the previous content is gone. File-based memories (Track A) preserve history via git, but native scopes do not.

- **Memory expiration/TTL**: No way to set time-to-live on memories. Short-term context that should expire after a sprint or release cycle must be manually cleaned up.

- **Team-shared memory scope**: Copilot's `/memories/repo/` is the closest to team-shared, but it cannot be browsed, searched, or managed collaboratively. There is no "team memories" scope visible to all org members.

- **Memory import/export**: No bulk operations for migrating memories between repositories, users, or Copilot instances.

- **Feedback loop on memory quality**: No way to mark a memory as "helpful" or "outdated" through the interface, which would help Copilot prioritize retrieval.

- **Structured metadata on native memories**: Native memory entries are plain text. No support for structured fields (date, category, impact, tags) that would enable filtered retrieval.

- **Event-triggered memory writes**: No mechanism for Copilot to automatically create memories based on events (e.g., "when a PR is merged, create an episodic entry"). All memory writes require explicit instruction or manual triggering.

## Gaps Introduced by the Format Decision (Markdown + YAML Frontmatter)

- **No native YAML frontmatter parsing in Copilot**: Copilot does not parse YAML frontmatter as structured data. It reads the entire file as Markdown, including the frontmatter block. Structured queries require the derived `_index.json` file or external tooling (Python/yq).

- **`_index.json` must be kept in sync**: The episodic index is a derived artifact. If someone creates an episodic entry but forgets to regenerate the index, queries against `_index.json` will be stale. Mitigation: use the provided git hook or GitHub Action to auto-regenerate on push.

- **No schema validation for frontmatter**: YAML frontmatter fields (date, category, impact, tags) are convention-enforced, not schema-validated. A typo like `categorry: ARCH` will silently pass. Mitigation: add a CI lint step that validates frontmatter keys against a known schema (see the clearing policy's GitHub Action).

- **Frontmatter adds authoring friction for non-technical contributors**: The `---` delimited YAML block requires correct YAML syntax (quoted dates, proper array notation). Non-developers may find this harder than plain Markdown bullet points. Mitigation: provide the TEMPLATE.md and document the exact format.

- **No built-in clearing mechanism**: Neither Copilot's native memory nor file-based Markdown have TTL or expiration semantics. Clearing must be implemented externally via the memory clearing policy (see `memory-clearing-policy.md`). Without enforcement, episodic memory grows unbounded.

- **`_index.json` adds a binary-like artifact to git**: While JSON is text-based and diffable, the `_index.json` file changes whenever any episodic entry is added or modified. This creates noise in PRs. Mitigation: add `_index.json` to `.gitattributes` as `merge=union` or regenerate it only in CI.

## Workarounds

| Gap | Workaround |
|---|---|
| No programmatic API | Use file-based Track A as primary store; sync to vector store for search |
| No memory search | Use vector store (Track B) for similarity search; use grep on `.github/memory/` files |
| Session memory loss | Instruct Copilot to summarize session at end; manually promote key findings |
| No memory versioning | Track A files in git provide full version history |
| No team-shared scope | Use `.github/memory/` files in shared repository; PR-based updates |
| Template bloat | Extract only actionable rules into `.github/instructions/`; keep frameworks as separate reference docs |
| No memory expiration | Periodic manual review; calendar reminders for quarterly memory maintenance. See `memory-clearing-policy.md` for automated clearing via GitHub Actions. |
| `_index.json` sync drift | Add the `rebuild-episodic-index.sh` script as a post-commit hook or CI step |
| No frontmatter schema validation | Add a CI lint step that parses YAML frontmatter and checks for required keys |
