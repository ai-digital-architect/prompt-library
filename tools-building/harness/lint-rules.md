# Lint Rule Catalog

The enumerated rules a compliant `toolsmith` implementation enforces. Rule IDs, checks, and messages are part of the user-facing contract: users should be able to switch implementations or languages without their lint output changing meaningfully.

## Table of contents

- [Conventions](#conventions)
- [TS001–TS099: naming](#naming-ts001ts099)
- [TS100–TS199: schema](#schema-ts100ts199)
- [TS200–TS299: description](#description-ts200ts299)
- [TS300–TS399: response](#response-ts300ts399)
- [TS400–TS499: implementation-specific](#implementation-specific-ts400ts499)
- [Severity overrides](#severity-overrides)
- [Adding new rules](#adding-new-rules)

---

## Conventions

### Rule IDs

- Prefix `TS` followed by a three-digit number.
- Range per category fixed (naming = 001–099, schema = 100–199, description = 200–299, response = 300–399, implementation-specific = 400+).
- Once assigned, a rule ID is never repurposed. Retired rules are marked deprecated but their ID stays reserved.

### Severities

Each rule has a default severity. The four valid values:

| Severity | Meaning | Affects exit code? |
|---|---|---|
| `error` | A problem serious enough to block a CI check. | Yes — `lint` exits `1`. |
| `warning` | A concern the user should see but not a hard failure. | No. |
| `info` | A suggestion or stylistic hint. | No. |
| `off` | Rule disabled. | Not applied. |

Users override severities via the config file (see [Severity overrides](#severity-overrides)).

### Message format

Messages are imperative and specific. They name the offending parameter or element when possible. Example:

- Good: `"Parameter 'q' is missing a description."`
- Bad: `"Some parameters need more information."`

Every message is short enough to render in a single terminal line (≤ 80 chars) where reasonable.

---

## Naming (TS001–TS099)

Applied to the tool's `name` field.

| ID | Default | Check | Message |
|---|---|---|---|
| **TS001** | error | `name` matches `^[a-z][a-z0-9_]+$` | "Tool name must be lowercase snake_case." |
| **TS002** | error | `name` contains at least one `_` (namespace prefix) | "Tool name must include a namespace prefix (e.g. `git_status`, not `status`)." |
| **TS003** | warning | First token of `name` is a verb OR is a recognized service namespace from config | "Tool name should start with a verb or registered service prefix." |
| **TS004** | error | No two loaded tools share a `name` | "Duplicate tool name: already defined in `<other-file>`." |
| **TS005** | warning | Name's Levenshtein distance from every other tool name is > 2 | "Tool name is very close to `<other>` — agents will confuse them." |

### TS003 notes

The "recognized service namespaces" list is user-configurable. Common examples: `git`, `repo`, `file`, `search`, `http`, `db`. When this list is empty, TS003 treats any starting verb as valid and only flags non-verb non-listed prefixes.

### TS005 notes

Levenshtein distance is computed between normalized (underscore-split, token-joined) names. A threshold of 2 catches near-typos like `repo_symbols_find` vs `repo_symbol_find`. Below 2 is a near-collision; users should rename or merge.

---

## Schema (TS100–TS199)

Applied to the tool's `input_schema`.

| ID | Default | Check | Message |
|---|---|---|---|
| **TS100** | error | `input_schema.type == "object"` | "Top-level input schema must be an object." |
| **TS101** | error | Every property has a non-empty `description` | "Parameter `<n>` is missing a description." |
| **TS102** | warning | No generic standalone parameter names (`user`, `id`, `data`, `input`, `value`, `name`) where a more specific name would fit | "Parameter `<n>` is too generic; prefer `<n>_id`, `<n>_path`, or similar." |
| **TS103** | warning | String parameters with ≤ 5 known values use `enum` (or Literal/union in typed stacks) | "Parameter `<n>` should probably be an enum." |
| **TS104** | warning | Schema nesting depth ≤ 3 | "Schema is deeply nested (depth `<n>`); flatten where possible." |
| **TS105** | info | Exposes a `response_format` enum with at least `concise` and `detailed` when output is structured | "Consider adding a `response_format` parameter." |
| **TS106** | warning | Tools returning potentially large data expose at least one of: `max_results`, `limit`, `cursor`, `offset`, `filter`, `query`, `path_glob` | "Tool may return large responses but has no pagination or filter parameter." |

### TS102 notes

The generic-names list is `["user", "id", "data", "input", "value", "name", "item", "thing"]` by default. Context matters: if a `name` parameter is actually about a *tool's own* name (the parameter *is* the noun being named), TS102 does not fire. Implementation hint: TS102 fires only when the parameter name matches a generic term *and* the tool's name contains a more specific noun the parameter could be qualified by.

### TS104 notes

Depth counts object nesting, not sibling breadth. A deeply nested structure signals that the schema should be flattened or the tool should accept an opaque JSON blob with an `as_markdown` option — both are better than making the agent build a deep nested input.

### TS106 notes

"Potentially large" is inferred from the tool's action verb: any tool whose name starts with `list_`, `search_`, `fetch_`, `query_`, `find_`, or `scan_` triggers TS106 unless at least one pagination/filter parameter is present. Tools with other action verbs (`get_`, `compute_`, `validate_`) are presumed single-result and do not trigger.

---

## Description (TS200–TS299)

Applied to the tool's `description` field.

| ID | Default | Check | Message |
|---|---|---|---|
| **TS200** | error | Description is non-empty and ≥ 40 characters (after trimming) | "Description is too short to orient the agent." |
| **TS201** | warning | Description contains a "Use when" and a "Do NOT use" / "Don't use" / "Do not use" disambiguation (case-insensitive) | "Description should disambiguate against sibling tools (add a 'Use when' and 'Do NOT use when' section)." |
| **TS202** | warning | Description token count ≤ 400 (estimated via `chars / 4` when offline, or exact via API) | "Description exceeds 400 tokens; trim for context efficiency." |
| **TS203** | info | Description mentions return shape (contains `"returns"`, `"returned"`, `"response"`, or a similar keyword) | "Consider describing what the tool returns." |

### TS201 notes

The check is deliberately lenient on section headers — it matches any occurrence of the phrases regardless of capitalization or punctuation. This rewards descriptions that naturally read like the example in `principles.md` without forcing a rigid template.

For tools that genuinely have no sibling to disambiguate against (sole member of their namespace), users can disable TS201 per-project or annotate the tool with `meta.no_siblings: true` which suppresses the rule for that tool.

---

## Response (TS300–TS399)

Applied only when a sample response file exists alongside the tool (`<tool-name>.sample.json` in the same directory). If no sample exists, TS300–TS302 are silently skipped.

| ID | Default | Check | Message |
|---|---|---|---|
| **TS300** | error | Sample response ≤ `response_token_limit` from config (default 25,000) | "Sample response exceeds configured token limit." |
| **TS301** | warning | Sample response does not contain UUID-shaped strings matching `[0-9a-f]{8}-[0-9a-f]{4}-` | "Response contains opaque IDs; consider semantic identifiers or return them only in `response_format: detailed`." |
| **TS302** | warning | Error-shaped samples (containing an `error` key at the top level, or an `is_error: true` field) include actionable language: at least one of `"try"`, `"use"`, `"pass"`, or the name of a parameter from the tool's `input_schema` | "Error response should tell the agent what to do next." |

### TS302 notes

The rule intentionally matches loose signals. If the implementation finds false negatives in practice, tighten — but err on the side of permissiveness to avoid annoying users with correctly-written errors that happen to use different phrasing.

---

## Implementation-specific (TS400–TS499)

Rules that apply only to a specific implementation stack. These should be namespaced by starting range:

- TS400–TS419: shell-specific
- TS420–TS439: Python-specific
- TS440–TS459: TypeScript-specific
- TS460+: reserved

### Shell (TS400–TS419)

| ID | Default | Check | Message |
|---|---|---|---|
| **TS400** | error | Handler path in JSON exists and is executable | "Handler `<path>` is missing or not executable." |
| **TS401** | warning | Handler passes `shellcheck` (if installed and handler appears to be a shell script) | "Handler has shellcheck warnings (see `shellcheck <path>` for details)." |

### Python (TS420–TS439)

| ID | Default | Check | Message |
|---|---|---|---|
| **TS420** | warning | Handler is `async def` (or compatible coroutine) | "Handler should be async to support concurrent eval runs." |

### TypeScript (TS440–TS459)

| ID | Default | Check | Message |
|---|---|---|---|
| **TS440** | warning | Handler returns a `Promise` | "Handler should return a Promise (declare as `async`)." |

Implementations that don't apply to a stack are simply unregistered on that stack; users do not need to disable them.

---

## Severity overrides

Users customize rule severities in the project config. The format is stack-native but the semantics are identical.

**Python (TOML):**
```toml
[lint.rules]
TS003 = "off"
TS105 = "warning"
TS201 = "error"
```

**TypeScript:**
```typescript
lint: {
  rules: {
    TS003: "off",
    TS105: "warning",
    TS201: "error",
  }
}
```

**Shell:**
```bash
LINT_TS003="off"
LINT_TS105="warning"
LINT_TS201="error"
```

Valid severities in overrides: `"error"`, `"warning"`, `"info"`, `"off"`. Unknown rule IDs are silently ignored (so configs don't break when a rule is added or removed).

---

## Adding new rules

When the principles document gains a new insight that warrants enforcement, follow this process:

1. **Assign an unused ID in the appropriate range.** Do not reuse retired IDs. Do not cross category boundaries.
2. **Document the rule in this file** with ID, default severity, check description, and message template.
3. **Add at least one passing and one failing fixture** to the test suite.
4. **Consider deprecating a redundant rule** if the new rule supersedes an existing one. Mark it deprecated here; keep the ID reserved.

A proposed rule that cannot articulate a check in a single sentence probably needs more design work before it becomes a rule.
