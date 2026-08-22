---
post_title: "Engineering Intelligence Benchmark: Model Evaluation Approach"
author1: "Engineering Intelligence Team"
post_slug: "engineering-intelligence-benchmark-model-evaluation"
microsoft_alias: ""
featured_image: ""
categories:
  - Engineering
tags:
  - model-evaluation
  - benchmarking
  - engineering-intelligence
  - code-graph
ai_note: "AI-assisted content"
summary: "A proposal for evaluating AI systems that reason about enterprise software using deterministic evidence, code graphs, and calibrated model judges."
post_date: "2026-08-22"
---

## Executive Summary

The core recommendation is to avoid treating a Skill as the benchmark. Instead,
use the Skill as the declarative front door to a model-evaluation harness built
into the existing code-graph platform.

Your existing system already possesses something most generic model benchmarks do not: a structured, lossless representation of the software system plus multiple domain-specific analysis capabilities. That means you can benchmark something much more valuable than “which model writes the nicest answer?” You can measure which model most accurately understands, investigates, reasons about, and reviews a real software system.

This starts to look like a combination of SWE-bench, Artificial Analysis,
Terminal-Bench, and an engineering-specific version of GDPval.

Treat the internal project as an **Engineering Intelligence Benchmark**, with
the code graph acting as the benchmark's evidence and oracle layer.

## Evaluation Lanes

There are actually three different questions hidden inside “which model is better?”

### Raw Model Capability

Given exactly the same task, context and constraints, which model performs best?

This is analogous to a traditional benchmark.

### Optimized Model Capability

If I prompt each model according to its vendor-recommended practices, what is the best performance I can achieve?

This matters because different frontier models genuinely want different prompting strategies. For example, Google’s current Gemini 3 guidance recommends relatively concise/direct instructions and using its thinking controls rather than complicated reasoning prompts; forcing every model through an identical elaborate prompt may therefore disadvantage it.

### Production-System Capability

When the model operates inside your multi-agent orchestration + code graph + retrieval + tools, which model produces the best engineering outcomes?

This is ultimately the most important question for your organization.

Create three benchmark lanes:

| Lane | Prompt | Tools | Measures |
| --- | --- | --- | --- |
| Parity | Identical canonical prompt | Identical | Underlying model capability |
| Optimized | Provider/model-specific template | Identical | Achievable model capability |
| Production | Optimized | Full agent/code-graph orchestration | Actual platform capability |

This distinction is essential.

Otherwise, if Gemini beats Claude, you won’t know whether Gemini is better or whether your Gemini prompt happened to be better.

## Reference Architecture

Conceptually:

                         BENCHMARK SPEC
                              |
                 +------------+-------------+
                 |                          |
           Canonical Task               Run Policy
                 |                          |
                 v                          v
        +------------------+       +------------------+
        | Prompt Compiler  |       | Experiment       |
        | / Model Adapter  |       | Controller       |
        +--------+---------+       +---------+--------+
                 |                           |
       +---------+---------+-----------------+
       |                   |                 |
       v                   v                 v
    OpenAI              Anthropic          Google
       |                   |                 |
       +-------------------+-----------------+
                           |
                           v
                  Agent / Model Harness
                           |
            +--------------+---------------+
            |                              |
            v                              v
      Code Graph APIs                Analysis Tools
      AST / Semantics               Security
      Dependencies                  Architecture
      Data flows                    Controls
      Call graph                    Resiliency
            |                              |
            +--------------+---------------+
                           |
                           v
                    MODEL RESPONSE
                           |
           +---------------+----------------+
           |               |                |
           v               v                v
      Deterministic     Graph-based      LLM Judge
        graders          graders          panel
           |               |                |
           +---------------+----------------+
                           |
                     Human calibration
                           |
                           v
                 Benchmark Score Store
                           |
          +----------------+----------------+
          |                |                |
       Quality          Reliability      Economics
       scores           scores           scores

The key architectural principle is:

Models generate hypotheses. Your graph and deterministic tooling should verify facts whenever possible. LLM judges should judge only what cannot be objectively verified.

Anthropic’s current agent-evaluation guidance recommends essentially this hierarchy: deterministic/code graders where possible, model graders where needed, and human experts for calibration. It also distinguishes the task, trial, transcript, outcome, grader and evaluation harness as separate artifacts.

⸻

## Evidence Model

### Code Graph as the Differentiator

This is where I think your benchmark could become unusually good.

SWE-bench typically asks:

Did the generated patch cause the tests to pass?

Your platform can ask much richer questions:

Did the model correctly understand the system?

For example, suppose the graph contains:

Controller
   |
   v
PaymentService
   |
   v
PaymentRepository
   |
   v
Oracle DB
PaymentService
   |
   +--> FraudService
   |
   +--> Kafka Publisher

You can establish objective truths such as:

PaymentController -> PaymentService     TRUE
PaymentService -> PaymentRepository     TRUE
PaymentService -> Kafka                 TRUE
Kafka -> PaymentRepository              FALSE

Now ask:

Identify the synchronous and asynchronous dependencies involved when a payment is created and identify potential failure-propagation paths.

The response can be automatically decomposed into claims and checked against the graph.

That gives you semantic correctness scoring rather than textual similarity scoring.

This is much stronger.

⸻

## Benchmark Suites

### Create Versioned Benchmark Packs

I would create independently versioned suites.

A. Semantic Understanding

Questions whose answers can be derived directly from the graph.

Examples:

* What calls this API?
* What services depend on this component?
* Trace the data flow from API to persistence.
* Identify transitive dependencies.
* Identify modules affected by changing this interface.
* Identify cross-domain dependencies.
* Find circular dependencies.
* Determine blast radius.

These are largely deterministic.

⸻

### Architecture Reasoning Benchmark

This should go substantially beyond static-analysis rules.

Seed applications with known architectural conditions such as:

Layer violation
UI -> Repository
expected:
UI -> Service -> Repository

Other tasks:

* bounded-context leakage
* domain/service coupling
* cyclic dependencies
* inappropriate database sharing
* synchronous dependency chains
* service-boundary violations
* inappropriate shared libraries
* domain logic in controllers
* distributed monoliths
* single-region dependencies
* lack of isolation
* cell-boundary violations

Each condition becomes a benchmark case with an explicit oracle.

You can then measure whether the model:

1. found it,
2. located it,
3. explained it,
4. understood its consequence,
5. prioritized it correctly,
6. proposed a reasonable remediation.

⸻

### Security Benchmark

This is particularly suitable for objective grading.

Start with repositories containing deliberately seeded vulnerabilities.

For example:

- CWE-89 SQL injection
- CWE-79 XSS
- CWE-798 embedded credentials
- CWE-22 path traversal
- Broken authorization
- Unsafe deserialization
- Missing authentication
- Dependency vulnerability
- Improper cryptography

Each benchmark item has hidden metadata:

```yaml
finding:
  type: CWE-89
  file: OrderRepository.java
  method: findOrders
  severity: high
evidence:
  source: controller.search
  sink: jdbc.execute
expected_root_cause:
  - unparameterized query
```

Now you can calculate:

Precision

valid findings / all findings

Recall

identified known findings / total known findings

And therefore F1.

This prevents a model that reports 100 speculative vulnerabilities from beating a model that reports the correct five.

⸻

### Controls Benchmark

This may ultimately be one of the most valuable internally.

Create controlled applications with known:

Compliant
Non-compliant
Not applicable
Insufficient evidence

conditions.

For example:

```yaml
control: RES-014
requirement: External service calls must define timeout and bounded retries.
oracle:
  status: NON_COMPLIANT
evidence:
  - PaymentClient.java:86
  - no timeout configuration
  - RetryPolicy maxAttempts=unbounded
```

Ask each model to determine compliance.

You now get a confusion matrix:

| Model assessment | Actual compliant | Actual non-compliant |
| --- | --- | --- |
| Model says compliant | TP | FN |
| Model says non-compliant | FP | TN |

This matters tremendously because in enterprise-control analysis, false positives have a real organizational cost.

⸻

### Resiliency Benchmark

Your existing resiliency principles become excellent adversarial benchmark tasks.

For example:

Redundancy

Seed:

Service
   |
single database
single AZ

versus:

Service
   |
multi-AZ database

Capacity under failure

Ask:

Can the surviving region absorb 100% traffic following regional failure?

Give configuration/capacity metadata.

Bulkheads

Create subtle failure coupling:

A ----\
B ----- shared thread pool
C ----/

versus isolated pools.

Rebuildability

Remove an undocumented manual dependency.

Recovery validation

Have infrastructure-as-code but no automated failover testing.

These are substantially better tests of engineering intelligence than generic coding questions.

⸻

### Dynamic Mutations

This is one of the most important pieces.

A weakness of public benchmarks is contamination. LiveCodeBench addresses this by continuously incorporating newer problems, and newer benchmarks such as DeepSWE have explicitly created original unpublished tasks with custom verifiers to avoid training-data leakage.

You have an opportunity to go even further.

Take a known-good application:

reference application

and automatically mutate it:

mutation 001
remove timeout
mutation 002
introduce cycle
mutation 003
bypass authorization
mutation 004
remove retry limit
mutation 005
share persistence across bounded contexts

The mutation engine knows exactly what it changed.

Therefore:

mutation = ground truth

You could generate hundreds or thousands of private, never-published benchmark variants.

That makes memorization almost irrelevant.

⸻

## Response Normalization and Scoring

### Score Findings, Not Documents

Don’t primarily ask a judge:

Rate this architecture report from 1–10.

Force every model into a normalized response schema.

Something resembling:

```json
{
  "findings": [
    {
      "category": "resiliency",
      "type": "missing_timeout",
      "severity": "high",
      "confidence": 0.94,
      "entities": [
        "PaymentClient.callGateway"
      ],
      "evidence": [
        {
          "file": "PaymentClient.java",
          "symbol": "callGateway"
        }
      ],
      "reason": "...",
      "impact": "...",
      "recommendation": "..."
    }
  ]
}
```

Gemini supports structured output, and current Gemini 3 models can combine structured output with tools, which fits this architecture particularly well.

Normalize equivalent structures from Claude/OpenAI into the same canonical representation.

⸻

### Quality Scoring Model

I would initially score each finding approximately as follows:

| Dimension | Weight |
| --- | ---: |
| Detection / correctness | 30% |
| Evidence grounding | 20% |
| Root-cause reasoning | 15% |
| Severity / prioritization | 10% |
| Completeness | 10% |
| Remediation quality | 10% |
| Communication / actionability | 5% |

But detection should incorporate both precision and recall.

For example:

$$
\text{DetectionScore} = F_1(\text{known findings}, \text{reported findings})
$$

Evidence can be much more objective:

$$
\text{EvidenceScore} =
\frac{\text{correct referenced entities}}{\text{total referenced entities}}
$$

You can also assess calibration:

Model says:
confidence = .95
finding wrong
     ↓
large calibration penalty

Over time, a calibrated model is much more useful than a model that confidently hallucinates architecture violations.

⸻

### Report Multiple Outcome Dimensions

Artificial Analysis does provide composite indexes, but importantly retains the underlying dimensions and separately exposes things such as tokens, costs and speed. Its current v4.1.1 Intelligence Index combines multiple evaluations and emphasizes agentic tasks; GDPval-AA v2 uses blind pairwise comparisons, multiple frontier judges and Bradley–Terry ranking.

I would publish at least four numbers.

Engineering Quality

EQI = Engineering Quality Index

0–100.

Reliability

If you run a model five times:

93
92
45
94
91

the average hides something important.

Report:

Mean
Median
Variance
pass@1
pass^3

Anthropic specifically recommends considering both pass@k—whether one of several attempts succeeds—and pass^k—whether repeated attempts all succeed. The latter is particularly relevant when you need predictable production behavior.

Efficiency

Report independently:

Input tokens
Reasoning tokens
Output tokens
Tool calls
Graph queries
Time to first token
Total runtime
API cost

Production Utility

Then optionally calculate an organization-specific index:

                 quality × reliability
Utility = --------------------------------
             normalized cost × latency

I would not make Utility the canonical leaderboard score, because weighting cost versus quality is a business decision.

Instead show the Pareto frontier:

QUALITY
  ^
  |                ● Model A
  |
  |        ● Model B
  |
  |                         ● Model C
  |
  +----------------------------------> COST

⸻

## Judge Design and Calibration

### CO-STORM-Inspired Tribunal

I like this part of your proposal, with a modification.

Don’t create:

5 LLMs discuss answer
        ↓
consensus
        ↓
truth

LLM judges have documented position bias and non-transitive preferences. Research also shows that simply increasing the number of judges does not necessarily create independent evidence: a 2026 Apple study found strong correlated errors across model panels.

Instead create a CO-STORM-inspired tribunal.

Judge 1 — Evidence Auditor

Only asks:

Are the claims actually supported by the code graph/code?

Judge 2 — Domain Expert

For example:

Security Expert
Architecture Expert
Resiliency Expert
Controls Expert

Judge 3 — Adversarial Reviewer

Attempts to disprove each finding.

Deterministic verifier

Checks graph assertions, tests and known benchmark oracle.

Arbiter

Only decides unresolved subjective dimensions.

And ideally:

candidate = OpenAI
judges = Anthropic + Google
candidate = Google
judges = OpenAI + Anthropic

rather than allowing one family to dominate evaluation.

⸻

### Blind the Judging Process

Never provide:

Claude response
Gemini response
OpenAI response

Use:

Candidate A
Candidate B
Candidate C

Randomize order.

For important comparisons, evaluate:

A vs B
B vs A

and detect position inconsistencies.

For the leaderboard, you can then perform round-robin comparisons:

A ↔ B
A ↔ C
A ↔ D
B ↔ C
B ↔ D
C ↔ D

and calculate a Bradley–Terry score.

This is quite close to the stronger parts of Artificial Analysis’ current GDPval-AA methodology.

⸻

### Calibrate the Judges

Before trusting the CO-STORM panel, create perhaps 100–200 responses graded by senior architects/security engineers.

Then measure:

Human verdict
      vs
Judge verdict

Google’s Vertex evaluation tooling explicitly supports this concept: human ratings can serve as ground truth for validating pointwise or pairwise model graders, including balanced accuracy and F1 measures.

You might discover something interesting such as:

Security judge:
Gemini       94% human agreement
Claude       91%
OpenAI       90%
Architecture judge:
Claude       95%
OpenAI       92%
Gemini       89%

Your judging system can then use domain-specific judge weights, rather than declaring one model the universal judge.

⸻

## Skill and Adapter Design

### Skill Package Design

I would absolutely build it—but like this.

GitHub Copilot now supports Agent Skills as directories containing SKILL.md, scripts and resources, including repository skills under .github/skills.

Something like:

.github/
└── skills/
    └── model-benchmark/
        ├── SKILL.md
        │
        ├── schemas/
        │   ├── benchmark.schema.json
        │   ├── task.schema.json
        │   └── response.schema.json
        │
        ├── prompts/
        │   ├── canonical/
        │   │   └── engineering-review.md
        │   │
        │   └── adapters/
        │       ├── anthropic.md
        │       ├── openai.md
        │       └── google.md
        │
        ├── judges/
        │   ├── architecture.md
        │   ├── security.md
        │   ├── resiliency.md
        │   ├── controls.md
        │   └── evidence.md
        │
        ├── suites/
        │   ├── semantic.yaml
        │   ├── architecture.yaml
        │   ├── security.yaml
        │   └── resiliency.yaml
        │
        └── scripts/
            ├── benchmark.py
            ├── invoke.py
            ├── normalize.py
            ├── deterministic_grade.py
            ├── tribunal.py
            ├── rank.py
            └── report.py

But SKILL.md should orchestrate these scripts rather than contain the entire implementation.

⸻

### Model Templates as Adapters

This part of your idea is particularly good.

Instead of:

Prompt → Model

use:

                 Canonical Activity
                        |
                        v
                Prompt Intermediate
                  Representation
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
      OpenAI         Claude        Gemini
      adapter         adapter       adapter

The canonical task might say:

```yaml
task:
  objective: architecture_review
context:
  repository: payment-platform
dimensions:
  - architecture
  - resiliency
requirements:
  evidence_required: true
  confidence_required: true
output:
  schema: findings-v1
```

The model adapter determines:

system instruction placement
reasoning/thinking configuration
tool definitions
structured-output mechanism
token limits
sampling defaults

but cannot alter the semantic requirements.

Store both:

canonical_prompt_hash
rendered_prompt_hash
adapter_version

This gives you auditability.

⸻

## Experiment Management

### Make Every Run Reproducible

A run manifest should capture at least:

```yaml
benchmark:
  suite: architecture-v1.3
  task: ARCH-00291
repository:
  commit: 8acf921
  graph_version: 4.7.2
  graph_hash: ...
model:
  provider: google
  model: ...
  endpoint: ...
  model_version: ...
prompt:
  canonical_version: 3.1
  adapter_version: google-2.4
runtime:
  temperature: ...
  reasoning_effort: ...
  max_tokens: ...
  tools: ...
trial:
  number: 3
metrics:
  latency_ms: ...
  input_tokens: ...
  output_tokens: ...
  cost: ...
result:
  artifact_hash: ...
```

Artificial Analysis’ endpoint work is a useful reminder that even supposedly identical models can behave differently because of endpoint settings, sampling, context handling and other serving configuration.

⸻

### Treat Each Invocation as an Experiment

I’d make the fundamental unit:

Experiment =
 Task
 × Model
 × Model configuration
 × Prompt profile
 × Harness
 × Trial

For example:

SEC-142
× Gemini
× high reasoning
× optimized prompt
× codegraph-agent-v4
× trial-3

This is vastly more useful than saying:

Gemini scored 87.

You will eventually want to answer questions like:

Did Gemini improve because we changed models, changed the prompt, or changed graph retrieval?

Your experiment metadata lets you know.

⸻

### Run Repeated Trials

One result is not sufficient.

Start with something like:

5 trials × each task × each model

and report task-level confidence intervals.

Terminal-Bench has used repeated benchmark runs for leaderboard submissions, while Artificial Analysis explicitly uses repeats and confidence intervals in parts of its methodology.

For comparisons between models, because every candidate runs the same tasks, use paired statistics rather than treating samples as independent.

For example:

Model A vs Model B
mean difference: +4.7
95% CI: [+3.2, +6.1]
P(A > B): 97.8%

That is much more defensible than:

A = 91
B = 87

⸻

### Maintain Two Benchmark Datasets

I strongly recommend:

Development Benchmark

Visible to developers.

Used continuously to improve prompts/orchestration.

And:

Sealed Benchmark

Never exposed to prompt authors or agents.

That gives you:

development score
      vs
generalization score

Over time, rotate problems:

sealed
   ↓
public regression
   ↓
new sealed problems

This is conceptually similar to LiveCodeBench’s approach of refreshing tasks to resist contamination.

⸻

### Measure Code-Graph Uplift

Your architecture allows an experiment that I think would be strategically valuable:

CodeGraph uplift

Run:

Model

versus:

Model + raw repository access

versus:

Model + semantic code graph

versus:

Model + graph + multi-agent orchestration

So:

                  Quality
Model only           54
Repo/RAG             68
Code Graph           81
Graph + agents       89

Now you aren’t merely benchmarking Google versus Anthropic versus OpenAI.

You’re benchmarking your architecture itself.

And you may discover:

Frontier Model A + graph = 92
Frontier Model B + graph = 90
Frontier Model A alone = 69

The strategically important result becomes:

The semantic engineering platform contributes +23 points; model selection contributes only +2.

That is enormously useful information for an enterprise technology strategy.

⸻

### Measure Graph Efficiency

An additional score:

Semantic Retrieval Efficiency

For every successful analysis:

graph queries
nodes examined
files opened
tokens consumed

Then:

Cost per Correct Finding

might become one of your best operational measures:

Model A     $0.083
Model B     $0.041
Model C     $0.119

Similarly:

Tokens per valid finding
Time per valid finding
Graph queries per valid finding

This gives you an Artificial Analysis-like price/performance dimension, but tailored to engineering analysis.

⸻

## Operating Model

### Benchmark Matrix and Model Routing

Your internal dashboard might look like:

| Model | Semantic | Architecture | Security | Controls | Resiliency | Reliability | $ / correct finding |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Model A | 94 | 91 | 88 | 93 | 84 | 96 | $0.08 |
| Model B | 96 | 87 | 94 | 89 | 91 | 92 | $0.11 |
| Model C | 91 | 94 | 90 | 96 | 93 | 97 | $0.06 |

And that leads to something considerably more sophisticated than a winner-takes-all leaderboard.

Your orchestrator could eventually say:

Architecture analysis → Model B
Security analysis     → Model B
Controls              → Model C
Semantic extraction   → Model A
Final synthesis       → Model A

In other words:

The benchmark can eventually become the model-routing control plane for your agent platform.

That is, in my view, one of the most interesting long-term outcomes of the project.

⸻

## Implementation Roadmap

### Minimum Viable Product

I would not begin with every analysis dimension.

Start with three suites where you have strong ground truth:

Phase 1 — Benchmark kernel

Build:

Canonical task schema
Model adapter SPI
Invocation runner
Response schema
Experiment store
Cost/latency collection
Multi-run support

Add OpenAI, Anthropic and Google adapters.

Phase 2 — Semantic benchmark

Create ~50 graph-provable tasks.

These establish that your evaluation pipeline works because grading is almost entirely deterministic.

Anthropic’s current guidance similarly recommends beginning with roughly 20–50 good tasks rather than waiting until hundreds exist.

Phase 3 — Security benchmark

Create ~50–100 known/mutated vulnerabilities.

Introduce precision/recall/F1.

Phase 4 — Architecture benchmark

Create ~50 controlled architecture violations.

Introduce partially subjective scoring and the CO-STORM tribunal.

Phase 5

Add:

Controls
Resiliency
Maintainability
Testing
Observability
Cloud architecture
Agentic system design

Then introduce the sealed benchmark and private mutation engine.

⸻

## Recommended Evolution

### From Skill-First to Evidence-First Evaluation

Your original flow was roughly:

Prompt
  ↓
Model-specific template
  ↓
Model A / B / C
  ↓
CO-STORM evaluation
  ↓
Score

I would evolve it into:

                         Benchmark Task
                               |
                  +------------+------------+
                  |                         |
              Ground Truth             Canonical Prompt
                  |                         |
                  |              +----------+----------+
                  |              |          |          |
                  |           Adapter    Adapter     Adapter
                  |              |          |          |
                  |              A          B          C
                  |              |          |          |
                  |              +-----+----+----------+
                  |                    |
                  |               Normalizer
                  |                    |
                  +--------------------+
                               |
                    +----------+----------+
                    |          |          |
                  Graph     Tests/Rules   CO-STORM
                 grader      grader       tribunal
                    |          |          |
                    +----------+----------+
                               |
                          Score Engine
                               |
              +----------------+----------------+
              |                |                |
           Quality         Reliability       Efficiency
              |                |                |
              +----------------+----------------+
                               |
                         Leaderboard

That small conceptual change—from LLM judging model responses to multi-source evidence evaluating experiments—is what turns the idea from an interesting Skill into a credible benchmark platform.

⸻

## Strategic Opportunity

There are already plenty of benchmarks answering:

How well can an LLM write code?

The more interesting question for your platform is:

How well can an AI system understand and reason about an enterprise software system?

And within that:

Can it reconstruct architecture?
Can it locate risk?
Can it distinguish evidence from assumption?
Can it understand failure propagation?
Can it identify security vulnerabilities?
Can it evaluate controls?
Can it understand architectural intent?
Can it assess blast radius?
Can it prioritize findings correctly?
Can it recommend viable remediation?
Can it do those things repeatedly?
And what does each correct engineering insight cost?

That is a substantially less saturated benchmark space.

SWE-bench gives you the idea of executable truth. Artificial Analysis gives you multi-dimensional scoring, economics and ranking methodology. LiveCodeBench/DeepSWE give you contamination resistance. CO-STORM gives you multi-perspective deliberation. Your semantic graph supplies something the others largely lack: a machine-queryable representation of the architecture itself.

Put those together and you can build something closer to:

SWE-bench for enterprise engineering intelligence rather than software patch generation.

And importantly, the same framework would serve three purposes simultaneously:

1. Model benchmarking — Google vs Anthropic vs OpenAI.
2. Platform benchmarking — graph vs no graph, agents vs no agents, prompt/orchestration versions.
3. Model routing — dynamically select the best model for security, architecture, controls, resiliency, etc.

I would therefore build the GitHub Copilot Skill first, but treat it as the authoring and execution interface for version 0.1 of this larger evaluation architecture, rather than letting the Skill itself become the architecture. GitHub’s current Skill model is actually well suited to this because Skills can package instructions, scripts and resources and are supported across several Copilot agent experiences.

A very natural next step would be to turn this into a concrete model-benchmark Agent Skill package with the actual SKILL.md, canonical benchmark schema, three model adapter templates, CO-STORM judge definitions, normalized response JSON schema, scoring algorithm, repository layout, and a sample Architecture + Security benchmark pack. That would give you something you could drop into .github/skills/model-benchmark/ and have Copilot start implementing against your existing platform.
