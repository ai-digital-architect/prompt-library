# Resiliency & NFR Ontology System — Architecture Layers

> Extracted from the system-design reference for the resiliency-ontology.owl system.
> Each layer is identified with its components, responsibilities, and integration contracts.

---

## Layer Overview (Top → Bottom)

```
L0  Ontology Resources         ← foundational knowledge artifacts
L1  Triplestore / Graph Store   ← ontology persistence
L2  Domain Ontology Services   ← semantic reasoning & routing
L3a Java Spring Backend        ← domain operations & REST API
L3b Python Agent Backend       ← agentic workflows & LLM orchestration
L4  MCP Server                 ← tool surface for agent interop
L5  External Agents / Systems  ← consumers of MCP tools
L6  API / BFF Layer            ← aggregation, shaping, gateway
L7  React Frontend (CDD)       ← component-driven UI
```

---

## L0 — Ontology Resources

**Role**: Foundational knowledge layer. Defines the canonical concepts, taxonomies, and relationships that every other layer reasons against.

**Components**

| File | Type | Purpose |
|---|---|---|
| `resiliency-ontology.owl` | OWL ontology | Core resiliency concept model (circuit breakers, bulkheads, degradation, etc.) |
| `nfr-ontology.ttl` | RDF/Turtle | Non-functional requirements taxonomy and inter-NFR relationships |
| `financial-instruments.ttl` | RDF/Turtle | Domain concepts for financial instrument types (Equity, Bond, Derivative…) |
| `agent-capabilities.ttl` | RDF/Turtle | Capability concepts for agent routing and task classification |
| `task-types.ttl` | RDF/Turtle | Taxonomy of task types for agentic workflow dispatch |
| `core-ontology.owl` | OWL ontology | Shared base classes and properties reused across domain ontologies |

**Lifecycle**: Loaded at application startup. Immutable at runtime unless a hot-reload mechanism is configured.

**Integration Contract**: All downstream layers treat concepts from these files as canonical URIs (e.g., `resiliency:CircuitBreaker`, `nfr:Availability`).

---

## L1 — Triplestore / Graph Store

**Role**: Persistence and query layer for ontology data. Provides SPARQL or Cypher query access to the loaded ontology graph.

**Supported Implementations**

| Engine | Protocol | Notes |
|---|---|---|
| Oxigraph | SPARQL 1.1 | Embedded, zero-dependency option |
| GraphDB | SPARQL 1.1 + RDF4J | Enterprise RDF store |
| Neo4j | Cypher / Bolt | Property graph; ontology via APOC/n10s plugin |

**Responsibilities**
- Ingest and index all ontology resources from L0 at startup
- Serve SPARQL queries from domain services (L2) and backend services (L3a)
- Persist runtime-asserted triples (e.g., trade classifications, agent task records)

**Integration Contract**: Exposed to L2 exclusively through **driven ports** (repository interfaces). No layer above L2 queries the triplestore directly.

---

## L2 — Domain Ontology Services

**Role**: Core semantic reasoning layer. Abstracts raw triplestore queries into domain-meaningful operations consumed by both backend stacks.

**Components**

| Service | Responsibility |
|---|---|
| `SemanticRouter` | Classifies incoming tasks/requests to canonical concept URIs; drives agent routing in L3b |
| `ConceptGrounding` | Validates and anchors free-text or LLM-generated terms to ontology-defined concepts |
| `TaxonomyService` | Traverses and exposes broader/narrower SKOS hierarchies; drives UI taxonomy widgets |

**Hexagonal Ports**
- **Driven port (outbound)**: `OntologyRepository` — delegates graph queries to L1
- **Driving ports (inbound)**: Called by L3a (Spring) and L3b (Python) via internal API

**Key Patterns**
- Concept identity is always a URI, never a free string
- All taxonomy navigation uses SKOS `broader` / `narrower` / `related` predicates
- NFR traceability links (`resiliency:tracesTo`, `nfr:measuredBy`) are resolved here

---

## L3a — Java Spring Backend

**Role**: Domain-driven backend for structured business operations. Enforces ontology constraints on writes and issues SPARQL-backed regulatory reports.

**Architecture Style**: Hexagonal Architecture on Domain-Driven Design

**Components**

| Component | Responsibility |
|---|---|
| Domain Model | `Trade`, `Portfolio`, `Instrument` — value objects typed by ontology `Concept` |
| Ontology Validator | Validates `Trade.instrumentType = Concept(Equity)` against L2 on every write |
| SPARQL Report Service | Generates regulatory reports via SPARQL queries through L2 → L1 |
| REST Controllers | Exposes HTTP endpoints to L6 (BFF) |

**Exposed API Endpoints**

| Endpoint | Method | Description |
|---|---|---|
| `/api/trades` | GET / POST | Trade blotter read and trade submission |
| `/api/ontology` | GET | Taxonomy and concept query surface |
| `/api/portfolio` | GET | Portfolio summary with concept-labelled positions |

**Integration Contract**: Communicates upward to L6 via REST. Communicates downward to L2 via injected domain service interfaces (hexagonal driven port).

---

## L3b — Python Agent Backend

**Role**: Agentic workflow orchestration layer. Manages LLM-driven agents, grounds their outputs to ontology concepts, and streams results via SSE.

**Architecture Style**: Hexagonal Architecture for Agentic Systems

**Components**

| Component | Responsibility |
|---|---|
| Task Classifier | Receives task → calls `SemanticRouter` (L2) → returns concept URI for routing |
| Agent Dispatcher | Routes classified tasks to the correct specialist agent (e.g., `EquityAgent`) |
| LLM Orchestrator | Manages prompt construction, injects ontology context into system prompts, calls LLM |
| Ontology Context Injector | Serialises relevant ontology sub-graphs into LLM system prompt as structured context |
| Concept Grounder | Post-processes LLM output → anchors free-text results to canonical concept URIs via L2 |
| Workflow Engine | Sequences multi-step agentic workflows; tracks step status |

**Exposed API Endpoints**

| Endpoint | Protocol | Description |
|---|---|---|
| `/api/agents/run` | REST / SSE | Submit a task; stream agent execution events |
| `/api/workflows/execute` | REST / SSE | Execute a named multi-step workflow |

**Integration Contract**: Communicates upward to L6 and L4. Communicates downward to L2 for semantic operations.

---

## L4 — MCP Server

**Role**: Exposes ontology and agent operations as MCP (Model Context Protocol) tools, making the system consumable by any MCP-compatible agent or model.

**Architecture Style**: Adapter layer (hexagonal secondary adapter — driving port)

**Exposed MCP Tools**

| Tool | Signature | Description |
|---|---|---|
| `classify_concept()` | `(text: str) → ConceptURI` | Classifies free text to a canonical ontology concept |
| `get_taxonomy_tree()` | `(root: ConceptURI) → Tree` | Returns a SKOS taxonomy sub-tree from a given root concept |
| `check_relationship()` | `(a: URI, rel: str, b: URI) → bool` | Asserts whether a named relationship holds between two concepts |

**Integration Contract**: Sits alongside L3b as a secondary surface. Delegates all semantic operations to L2 services. Consumed by L5.

---

## L5 — External Agents / Systems

**Role**: External consumers of the MCP server surface. Not an internal layer — represents the boundary of the system.

**Known Consumers**

| Consumer | Integration |
|---|---|
| Claude (Anthropic) | MCP client — calls tools to ground its reasoning in the ontology |
| Other specialist agents | MCP clients — use taxonomy and classification tools for routing |
| Third-party systems | REST clients — consume L3a or L3b REST endpoints directly |

---

## L6 — API / BFF Layer

**Role**: Backend for Frontend. Aggregates responses from L3a and L3b into a single, UI-consumable graph. Performs DTO shaping and ontology concept → display model mapping.

**Implementation Options**
- GraphQL gateway (Apollo Federation / Spring GraphQL)
- REST aggregator / API composition layer

**Responsibilities**

| Responsibility | Detail |
|---|---|
| Response aggregation | Combines Spring (L3a) and Agent (L3b) data into a single query response |
| DTO shaping | Transforms internal domain models into UI-safe display models |
| Concept label resolution | Maps ontology concept URIs → human-readable labels for all UI components |
| Transport support | REST, GraphQL, WebSocket, SSE — all exposed to L7 |

**Integration Contract**: L7 consumes this layer exclusively via typed API clients (React Query for REST, Apollo Client for GraphQL). L7 never calls L3a or L3b directly.

---

## L7 — React Frontend (Component-Driven Design)

**Role**: UI layer. Fully component-driven using the Salt Design System. Ontology concepts flow through all levels as typed values (ConceptId URIs).

**Architecture Style**: Component-Driven Design (CDD) with vertical Feature Slices

---

### L7.1 — Atoms (Salt-DS Primitives)

**Role**: Lowest-level, stateless UI building blocks. Re-exported from Salt Design System with application-level defaults.

| Component | Origin |
|---|---|
| `Button` | Salt re-export |
| `Input` | Salt re-export |
| `Badge` | Salt re-export |
| `Spinner` | Salt re-export |
| `Tooltip` | Salt re-export |
| `Text` | Salt re-export |

---

### L7.2 — Molecules (Composite Primitives)

**Role**: Combinations of atoms with light ontology awareness. Key ontology integration point: concept selection and classification display.

| Component | Ontology Integration |
|---|---|
| `TradeForm` | Fields typed by ontology concepts; `instrumentType` accepts only valid `ConceptId` |
| `ConceptSelect` | Dropdown options fully driven by taxonomy API (`/api/ontology`); value is a `ConceptURI` |
| `AgentMessageBubble` | Renders SSE-streamed agent message with concept badges |
| `ClassificationBadge` | Displays the concept URI used by the agent for task routing |
| `WorkflowStepCard` | Shows status of a single workflow step |
| `OntologyBreadcrumb` | Renders SKOS broader-chain as a navigation breadcrumb |

---

### L7.3 — Organisms (Domain-Complete Panels)

**Role**: Fully functional domain panels composed from molecules and atoms. Ontology domains are exposed as complete UI surfaces.

| Component | Ontology Integration |
|---|---|
| `TradeBlotter` | Column labels sourced from ontology concept labels |
| `PortfolioSummary` | Position groupings use ontology concept hierarchy |
| `AgentChatPanel` | Streams SSE from L3b; renders `ClassificationBadge` per message |
| `WorkflowStatusBoard` | Tracks multi-step workflow execution state |
| `TaxonomyBrowser` | Full SKOS taxonomy browse: broader/narrower navigation, concept detail |
| `ConceptSearchBar` | Full-text concept search against `/api/ontology` |

---

### L7.4 — Templates (Page Scaffolds)

**Role**: Layout shells. `SaltProvider` wraps everything at this level, establishing the design-system theme boundary.

| Template | Wraps |
|---|---|
| `DashboardLayout` | Top-level shell; `SaltProvider` root |
| `TradingLayout` | Trading feature scaffold |
| `AgentLayout` | Agent workspace scaffold |

---

### L7.5 — Features (Vertical Slices)

**Role**: Business-capability pages. Each feature slice owns its data-fetching, composes organisms/molecules, and wires ontology end-to-end.

#### `trading/` — Trade Execution

```
TradeExecutionPage
  ├── TradeForm          (fields typed by ontology concepts)
  ├── ConceptSelect      (options from taxonomy API → value = ConceptId URI)
  └── on submit → REST POST /api/trades
                 → Spring (L3a) validates ConceptId against ontology on write
```

#### `agents/` — Agent Workspace

```
AgentWorkspacePage
  ├── AgentChatPanel         (task input + SSE stream from /api/agents/run)
  ├── WorkflowStatusBoard    (step-by-step execution state)
  └── ClassificationBadge   (concept the agent used to route the task)
```

#### `knowledge/` — Taxonomy Explorer

```
TaxonomyExplorerPage
  ├── TaxonomyBrowser        (browse/search the full ontology)
  ├── broader/narrower       (SKOS hierarchy navigation)
  └── ConceptDetail          (related entities, NFR traceability links)
```

---

### L7.6 — Storybook (Living Design System)

**Role**: Component development, documentation, and visual regression surface. MSW (Mock Service Worker) stubs ontology API for isolated story rendering.

| Story | Notes |
|---|---|
| `Design System/Atoms/Button` | Base atom documentation |
| `Design System/Molecules/ConceptSelect` | Taxonomy-driven options; MSW mocks `/api/ontology` |
| `Design System/Organisms/TaxonomyBrowser` | Full SKOS browse with mocked data |
| `Features/Trading/TradeExecutionPage` | Full feature story with concept submission flow |
| `Features/Agents/AgentWorkspacePage` | SSE stream simulation |
| `Salt Design System` | Composed via Storybook refs — declares upstream dependency |

---

## Cross-Cutting Concerns

| Concern | Mechanism | Layers Affected |
|---|---|---|
| Concept identity | All concept values are canonical URIs, never free strings | L0 → L7 |
| Ontology validation | Spring (L3a) validates every domain write against L2 | L3a, L2, L1 |
| LLM grounding | Python backend (L3b) anchors all LLM output to concept URIs | L3b, L2 |
| NFR traceability | `resiliency:tracesTo` and `nfr:measuredBy` properties in ontology | L0, L2, L3a |
| Design system boundary | `SaltProvider` scoped at Template level (L7.4) | L7.1–L7.5 |
| API type safety | Typed API clients (React Query / Apollo) enforce DTO contracts | L6, L7 |
| Observability / SSE streaming | Real-time agent and workflow state over SSE | L3b, L6, L7 |

---

## Layer Integration Map

```
L0  Ontology Resources
  └─loaded at startup──► L1  Triplestore
                           └─via driven ports──► L2  Domain Ontology Services
                                                   ├──────────────────────► L3a Java Spring Backend
                                                   │                          └─REST──► L6 BFF Layer
                                                   │                                      └─React Query/Apollo──► L7 Frontend
                                                   └──────────────────────► L3b Python Agent Backend
                                                                               ├─REST/SSE──► L6 BFF Layer
                                                                               └─MCP adapter──► L4 MCP Server
                                                                                                  └─tools──► L5 External Agents
```

---

*Generated from system-design-reference for the resiliency-ontology.owl system.*
