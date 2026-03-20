# Domain 4: Prompt Engineering & Structured Output
**Weight: 20% of scored content**

---

## Overview

This domain tests your ability to craft precise prompts that reduce false positives, apply few-shot examples strategically, enforce structured output via JSON schemas and tool use, design validation and retry loops, build efficient batch processing strategies, and architect multi-pass review systems. It is heavily practical — questions present real output quality problems and ask for the correct engineering intervention.

**Source coverage:** The exam guide source list is well-matched. Key sources: *Prompt Engineering Overview*, the interactive tutorial (`anthropics/prompt-eng-interactive-tutorial`), and the Anthropic docs on tool use, structured outputs, and batch processing.

---

## 4.1 Designing Prompts with Explicit Criteria

### The Problem with Vague Instructions

Vague instructions ("be thorough," "be conservative," "only report high-confidence findings") do not reliably improve precision. They leave the model to interpret what those phrases mean — leading to inconsistent behavior.

### From Vague to Explicit Criteria

```
# ❌ VAGUE — Open to interpretation
"Check that comments are accurate."
"Be conservative — only flag issues you're confident about."

# ✅ EXPLICIT — No interpretation required
"Flag a comment ONLY when the comment's claimed behavior
directly contradicts what the code actually does.

Do NOT flag:
- Comments that describe intent rather than implementation
- Comments using different terminology but same semantics
- Out-of-date comments that are simply stale (mark separately)
- Style preferences for comment phrasing"
```

### Defining Severity Criteria with Examples

Vague severity labels ("critical," "high") are inconsistently applied. Provide concrete examples for each level:

```markdown
## Severity Definitions

**CRITICAL** — Exploitable security vulnerability or certain data loss.
Example: SQL injection via unsanitized user input.
Example: Writing user data to a publicly accessible S3 bucket.

**HIGH** — Runtime crash likely in production conditions.
Example: NullPointerException when `userId` is missing (common case).
Example: Unhandled exception in payment processing flow.

**MEDIUM** — Incorrect behavior only in specific edge cases.
Example: Off-by-one error only triggered when list has exactly 0 items.
Example: Timezone bug only visible for users in UTC-12.

**LOW** — Maintainability concern only; no user-facing impact.
Example: Variable name `x` used where `transactionAmount` would be clearer.
```

### Temporarily Disabling High-FP Categories

When a category produces too many false positives, it erodes developer trust in ALL categories. Temporarily disable the high-FP category while you improve its criteria:

```markdown
# DO report:
- Security vulnerabilities (injection, auth bypass, data exposure)
- Null pointer dereferences and unhandled exceptions

# DO NOT report this sprint:
- Comment accuracy issues (temporarily disabled — high false-positive rate)
  NOTE: These will be re-enabled after criteria refinement in Sprint 12.
```

---

## 4.2 Few-Shot Prompting for Consistency and Quality

### Why Few-Shot Examples Work

Few-shot examples (also called multishot prompting) are the most effective technique for:
- Achieving **consistently formatted output** when detailed instructions alone fail
- **Demonstrating ambiguous-case handling** — showing Claude how to handle unclear situations
- **Reducing hallucination** in extraction tasks with varied document structures
- Enabling **generalization** to novel patterns (not just pre-specified cases)

### Example Structure: Code Review Findings

```python
system_prompt = """
Review code changes and report findings. Use the format demonstrated below.

<examples>
<example>
<code_change>
function processPayment(amount) {
  db.query("SELECT * FROM users WHERE id = " + userId);
}
</code_change>
<finding>
{
  "file": "src/payments.ts",
  "line": 2,
  "severity": "CRITICAL",
  "issue": "SQL injection vulnerability via string concatenation. User-supplied `userId` is not sanitized.",
  "suggested_fix": "Use parameterized query: db.query('SELECT * FROM users WHERE id = ?', [userId])"
}
</finding>
</example>

<example>
<code_change>
// Returns user's total spend
function getTotalSpend(userId) {
  return orders.filter(o => o.userId === userId)
               .reduce((sum, o) => sum + o.amount, 0);
}
</code_change>
<finding>
No issues found. The comment accurately describes the function's behavior.
The implementation is correct for its stated purpose.
</finding>
</example>
</examples>
"""
```

**Key design choices in the example above:**
- Shows both a positive finding AND a "no issues" example — teaching when NOT to flag
- Demonstrates the exact output format (fields, structure, severity labels)
- Explains the reasoning (not just the verdict)

### How Many Examples?

| Scenario | Examples Needed |
|---|---|
| Simple format consistency | 2–3 |
| Ambiguous case handling | 3–5 with clear disambiguation |
| Complex extraction with varied formats | 4–6 covering each format variant |
| Reducing hallucination in missing-data cases | Include at least 1 "null output" example |

### Few-Shot Examples for Extraction with Varied Formats

When source documents have inconsistent structure, show examples of each format:

```python
"""
Extract study participant counts from research papers.

<examples>
<example>
<document>We enrolled 248 participants across three sites...</document>
<extraction>{"participants": 248, "source_location": "enrollment section"}</extraction>
</example>

<example>
<document>N=84 patients were randomized to the treatment arm.</document>
<extraction>{"participants": 84, "source_location": "randomization description"}</extraction>
</example>

<example>
<document>The sample consisted of volunteers recruited via social media.</document>
<extraction>{"participants": null, "source_location": null, "note": "Sample size not stated"}</extraction>
</example>
</examples>
"""
```

The last example is critical: it teaches the model to return `null` rather than fabricating a number when the information is absent.

---

## 4.3 Enforcing Structured Output via Tool Use and JSON Schemas

### Tool Use as the Gold Standard for Structured Output

**Tool use (`tool_use`) with JSON schemas is the most reliable approach for guaranteed schema-compliant output.** It eliminates JSON syntax errors (missing brackets, unescaped characters, trailing commas) that plague text-based JSON prompting.

```python
extraction_tool = {
    "name": "extract_invoice_data",
    "description": "Extract structured data from an invoice document.",
    "input_schema": {
        "type": "object",
        "properties": {
            "invoice_number": {
                "type": "string",
                "description": "Invoice identifier (e.g., INV-2024-0042)"
            },
            "vendor_name": {
                "type": "string",
                "description": "Name of the vendor or supplier"
            },
            "total_amount": {
                "type": ["number", "null"],
                "description": "Total invoice amount in USD. Null if not stated."
            },
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": ["integer", "null"]},
                        "unit_price": {"type": ["number", "null"]},
                        "total": {"type": ["number", "null"]}
                    }
                }
            },
            "payment_terms": {
                "type": "string",
                "enum": ["net_30", "net_60", "net_90", "immediate", "other"],
                "description": "Payment terms if specified"
            },
            "payment_terms_detail": {
                "type": ["string", "null"],
                "description": "If payment_terms is 'other', specify here"
            }
        },
        "required": ["invoice_number", "vendor_name"]
    }
}
```

### Extracting the Tool Use Result

```python
response = client.messages.create(
    model="claude-opus-4-6",
    tools=[extraction_tool],
    tool_choice={"type": "tool", "name": "extract_invoice_data"},
    messages=[{"role": "user", "content": f"Extract data from this invoice:\n{invoice_text}"}]
)

# Extract the structured data from the tool_use block
extracted_data = None
for block in response.content:
    if block.type == "tool_use" and block.name == "extract_invoice_data":
        extracted_data = block.input
        break
```

### `tool_choice` Options for Structured Output

| Value | When to Use |
|---|---|
| `{"type": "tool", "name": "extract_invoice_data"}` | You know exactly which schema to use |
| `"any"` | Multiple extraction schemas exist; document type is unknown; must call *a* tool |
| `"auto"` | Do NOT use when you need guaranteed structured output — model may return plain text |

### Schema Design: Required vs. Optional Fields

**Critical:** Mark fields as optional (nullable) when the source document may not contain that information. If required fields are always expected, the model may **fabricate values** to satisfy the schema.

```python
# ❌ RISKY: All fields required — model may hallucinate missing values
"required": ["invoice_number", "vendor_name", "total_amount", "due_date"]

# ✅ SAFE: Only truly required fields; optional fields use nullable types
"required": ["invoice_number", "vendor_name"],
# total_amount: {"type": ["number", "null"]}  ← nullable
# due_date: {"type": ["string", "null"]}      ← nullable
```

### Enum Fields with "Other" + Detail Pattern

For extensible categorization, use an `"other"` enum value paired with a detail string field:

```python
"payment_status": {
    "type": "string",
    "enum": ["paid", "pending", "overdue", "disputed", "cancelled", "unclear", "other"]
},
"payment_status_detail": {
    "type": ["string", "null"],
    "description": "If payment_status is 'other' or 'unclear', explain here"
}
```

This prevents fabrication for ambiguous cases while keeping the schema extensible.

### What Tool Use Does NOT Prevent

Tool use eliminates **syntax errors** but does not prevent **semantic errors**:
- Line items that don't sum to the stated total
- Values placed in wrong fields (unit_price in the total field)
- Dates extracted from wrong part of the document

These require separate semantic validation — see Domain 4.4.

---

## 4.4 Validation, Retry, and Feedback Loops

### Retry-with-Error-Feedback Pattern

When extraction fails validation, don't just retry — include the specific errors:

```python
def extract_with_retry(document: str, max_retries: int = 2) -> dict:
    messages = [
        {"role": "user", "content": f"Extract invoice data:\n{document}"}
    ]

    for attempt in range(max_retries + 1):
        response = client.messages.create(
            model="claude-opus-4-6",
            tools=[extraction_tool],
            tool_choice={"type": "tool", "name": "extract_invoice_data"},
            messages=messages
        )

        extracted = get_tool_result(response)
        messages.append({"role": "assistant", "content": response.content})

        errors = validate_semantics(extracted)
        if not errors:
            return extracted

        if attempt < max_retries:
            # Include specific validation errors in the retry prompt
            messages.append({
                "role": "user",
                "content": (
                    f"The extraction had validation errors. Please re-extract "
                    f"and fix these specific issues:\n"
                    f"{format_errors(errors)}\n\n"
                    f"Original document:\n{document}"
                )
            })

    return extracted  # Return best effort after max retries
```

### When Retries Will and Won't Work

| Situation | Retry Useful? | Reason |
|---|---|---|
| Format mismatch (e.g., date in wrong format) | ✅ Yes | Model can fix with specific feedback |
| Schema structure errors (field in wrong place) | ✅ Yes | Model can fix with specific feedback |
| Required information not in source document | ❌ No | Model cannot generate what doesn't exist |
| External document referenced but not provided | ❌ No | Information is genuinely unavailable |

**Exam trap:** A retry loop will not help when the required information simply isn't in the provided document. Recognize when to stop retrying and mark the field as null or flag for human review.

### Self-Correction Validation for Semantic Errors

Design the schema to surface potential semantic errors:

```python
"extraction_schema": {
    "properties": {
        "line_items_total": {
            "type": ["number", "null"],
            "description": "Sum of all line item totals as calculated from line_items array"
        },
        "stated_total": {
            "type": ["number", "null"],
            "description": "Total amount as stated in the document"
        },
        "totals_match": {
            "type": "boolean",
            "description": "True if line_items_total equals stated_total (within $0.01)"
        },
        "conflict_detected": {
            "type": "boolean",
            "description": "True if any field values appear contradictory in the source"
        }
    }
}
```

### `detected_pattern` for False Positive Analysis

Add a `detected_pattern` field to findings to enable systematic analysis of what's triggering false positives:

```python
"finding_schema": {
    "properties": {
        "issue": {"type": "string"},
        "severity": {"type": "string"},
        "detected_pattern": {
            "type": "string",
            "description": "The specific code construct that triggered this finding"
        }
    }
}
```

When developers dismiss findings, analyze `detected_pattern` values to identify which patterns consistently produce false positives.

---

## 4.5 Batch Processing Strategies

### Message Batches API: Key Facts

| Property | Value |
|---|---|
| Cost savings | 50% vs. synchronous API |
| Maximum processing time | Up to 24 hours |
| Latency guarantee | None (often faster, but no SLA) |
| Multi-turn tool calling | Not supported within a single batch request |
| Request correlation | Use `custom_id` field |

### Matching API to Workflow Latency Requirements

| Workflow | Correct API | Reason |
|---|---|---|
| Pre-merge code review (blocking) | **Synchronous** | Developers wait for result — latency matters |
| Overnight technical debt report | **Batch** | Not time-sensitive; 50% cost savings |
| Weekly audit report | **Batch** | Overnight processing acceptable |
| Nightly test generation | **Batch** | Non-blocking; 24-hour window is fine |

**Exam trap:** "Use batch API for both workflows with status polling" — wrong, because polling doesn't give a latency guarantee. Pre-merge checks require the synchronous API.

### Calculating Batch Submission Frequency for SLA Compliance

```
SLA requirement: Results available within 30 hours of document submission
Batch processing window: Up to 24 hours

Required submission frequency:
30-hour SLA - 24-hour max processing = 6-hour submission window

To guarantee SLA: Submit batches at least every 6 hours
```

### Handling Batch Failures

```python
# Submit initial batch
batch = client.beta.messages.batches.create(requests=[
    {"custom_id": f"doc_{i}", "params": {"model": "claude-opus-4-6", ...}}
    for i, doc in enumerate(documents)
])

# Check results after processing
results = client.beta.messages.batches.results(batch.id)

failed_ids = []
for result in results:
    if result.result.type == "error":
        failed_ids.append(result.custom_id)

# Resubmit failed documents only (with modifications if needed)
failed_docs = [get_doc_by_custom_id(fid) for fid in failed_ids]
retry_batch = client.beta.messages.batches.create(requests=[
    {
        "custom_id": f"{fid}_retry",
        "params": {
            "messages": [{"role": "user", "content": chunk_large_doc(doc)}]
        }
    }
    for fid, doc in zip(failed_ids, failed_docs)
])
```

### Prompt Refinement Before Batch Submission

Before processing 10,000 documents, refine your prompt on a sample set:

```
1. Sample 50–100 representative documents (include edge cases)
2. Run synchronous extractions with current prompt
3. Review accuracy — identify failure patterns
4. Refine prompt (add few-shot examples for failure patterns)
5. Re-validate on sample
6. Submit full batch only when sample accuracy is satisfactory
```

This maximizes first-pass success rate and avoids costly batch resubmissions.

---

## 4.6 Multi-Instance and Multi-Pass Review Architectures

### Self-Review Limitations

A model that generated code **retains reasoning context** from that generation. This makes it less likely to question its own decisions in the same session — it will defend rather than critique its choices.

**Solution:** Use a **second independent Claude instance** for review. The reviewer has no access to the generator's reasoning chain and approaches the code fresh.

```python
# Step 1: Generate code
generation_response = client.messages.create(
    model="claude-opus-4-6",
    system="You are an expert Python developer.",
    messages=[{"role": "user", "content": f"Implement: {specification}"}]
)
generated_code = extract_code(generation_response)

# Step 2: Independent review (NEW session — no shared context with generation)
review_response = client.messages.create(
    model="claude-opus-4-6",
    system="You are a security-focused code reviewer.",
    # IMPORTANT: Fresh messages list — no history from generation session
    messages=[{
        "role": "user",
        "content": f"Review this code for security vulnerabilities:\n{generated_code}"
    }]
)
```

### Multi-Pass Review Architecture

For large PRs (10+ files), split into focused passes:

```
Pass 1: Per-file local analysis (one request per file)
  └── File A → local issues (bugs, null checks, error handling)
  └── File B → local issues
  └── File C → local issues
  ...

Pass 2: Cross-file integration analysis (single request with all file summaries)
  └── Input: summaries from all per-file passes
  └── Output: cross-file issues (API contract violations, data flow bugs,
             inconsistent error handling across modules, shared state mutations)
```

This prevents:
- **Attention dilution**: Superficial coverage of some files when too many are reviewed at once
- **Contradictory findings**: Flagging a pattern as bad in File A while approving it in File B
- **Missed cross-file issues**: Bugs that span multiple files (hidden when reviewing files together)

### Confidence Scoring for Review Routing

Have Claude report confidence alongside each finding:

```python
finding_schema = {
    "finding": "SQL injection vulnerability via string concatenation",
    "severity": "CRITICAL",
    "confidence": 0.95,
    "confidence_rationale": "Clear unsanitized user input in query string"
}

# Route by confidence:
# High confidence (>0.85) → post immediately as PR comment
# Medium confidence (0.60–0.85) → queue for human secondary review
# Low confidence (<0.60) → discard or flag for discussion
```

---

## Exam Practice Questions

**Q1:** Your code review tool flags 40% false positives for the "comment accuracy" category. Developers are starting to ignore ALL review findings. What's the correct response?
> Temporarily disable the high-FP "comment accuracy" category while improving its criteria, and define explicit severity criteria with concrete code examples. Disabling high-FP categories restores trust while you fix the root cause.

**Q2:** Your extraction pipeline consistently returns empty values for `participant_count` in papers with inline text (e.g., "We enrolled 248 participants"). Using JSON schema alone hasn't fixed it. What's most effective?
> Add few-shot examples showing correct extraction from varied document structures (inline text, table format, methods section). Few-shot examples are most effective for variable document structure issues.

**Q3:** You need guaranteed schema-compliant JSON output from Claude. What's the most reliable approach?
> Use tool use (`tool_use`) with a JSON schema as the tool's `input_schema`. Set `tool_choice: "any"` (or forced tool selection) to guarantee the tool is called. This eliminates JSON syntax errors.

**Q4:** A batch job generates technical debt reports overnight. A pre-merge check must complete before developers can merge. How should you handle each?
> Use the **Batch API** for the overnight technical debt report (non-blocking, 50% cost savings). Use the **synchronous API** for pre-merge checks (developers wait for results — latency guarantee required).

**Q5:** Your code generation + review system misses subtle security bugs. What architecture change helps most?
> Use a second independent Claude instance for review (a fresh session with no access to the generation session's reasoning context). Independent review instances catch more issues than self-review.

---

## Key Terms Checklist

- [ ] Explicit vs. vague review criteria
- [ ] False positive impact on developer trust
- [ ] Few-shot examples: purpose, count (2–5), structure (`<examples>` tags)
- [ ] Null example — teaches model to return null, not fabricate
- [ ] Tool use for guaranteed schema-compliant output
- [ ] `tool_choice: "any"` vs. forced tool selection vs. `"auto"`
- [ ] Required vs. nullable (optional) schema fields
- [ ] Enum + "other" + detail string pattern
- [ ] Semantic errors vs. syntax errors (tool use only prevents syntax)
- [ ] Retry-with-error-feedback pattern
- [ ] When retries are ineffective (information absent from document)
- [ ] `detected_pattern` field for false positive analysis
- [ ] Message Batches API: 50% cost savings; 24-hour max; no latency SLA
- [ ] Batch for non-blocking; synchronous for blocking workflows
- [ ] `custom_id` for batch request/response correlation
- [ ] Prompt refinement on sample before full batch submission
- [ ] Self-review limitations; independent review instance
- [ ] Multi-pass review: per-file local passes + cross-file integration pass
- [ ] Confidence scoring for review routing

---

## Recommended Sources

| Source | Focus |
|---|---|
| [Prompt Engineering Overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) | Core techniques; XML tagging; few-shot prompting |
| [Interactive Tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial) | Hands-on practice with all techniques |
| [Tool Use Documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) | JSON schema design; tool_choice options |
| [Batch Processing](https://docs.anthropic.com/en/docs/build-with-claude/batch-processing) | Batch API; custom_id; failure handling |
| [Introducing Advanced Tool Use](https://www.anthropic.com/research/advanced-tool-use) | Real-world tool use patterns |
| Exam Guide — Task Statements 4.1–4.6 (Pages 17–20) | Authoritative task definitions |
