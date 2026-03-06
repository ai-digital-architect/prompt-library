# CLAUDE.md — Memory-Enabled Project Configuration

> Drop this into any repository's root as `CLAUDE.md`. Fill in the [PLACEHOLDERS] with your project's specifics. Remove this header comment after customizing.

## Project Identity
- **Name**: [PROJECT_NAME]
- **Type**: [web-app | api | library | cli | mobile]
- **Language**: [TypeScript | Python | Go | Rust | Java]
- **Framework**: [React | Next.js | Express | FastAPI | Django | etc.]
- **Database**: [PostgreSQL | MongoDB | MySQL | SQLite | etc.]
- **Hosting**: [AWS | GCP | Azure | Vercel | Fly.io | etc.]
- **CI/CD**: [GitHub Actions | CircleCI | GitLab CI | etc.]

## Architecture
- **Style**: [monolith | microservices | serverless | modular-monolith]
- **Key Services**: [list main services/modules and their responsibilities]
- **External Integrations**: [Stripe, SendGrid, etc.]

## Coding Standards
- **Naming**: [camelCase | snake_case] for variables/functions, [PascalCase] for types/classes
- **Max Function Length**: [30] lines
- **Max File Length**: [300] lines
- **Import Order**: [stdlib, external, internal, relative — separated by blank lines]
- **Error Handling**: [typed errors | Result type | exceptions — describe pattern]
- **Testing**: [framework], co-located test files `*.test.ts`, [coverage target]%

## API Standards
- **Style**: [REST | GraphQL | gRPC]
- **Base Path**: [/api/v1/]
- **Auth**: [Bearer JWT | API Key | OAuth2]
- **Response Shape**: `{ data: T, error?: { code: string, message: string }, meta?: { page, total } }`
- **Pagination**: [cursor-based | offset-based]

## Business Rules
<!-- Add the 5-10 most important business rules that affect code generation -->
- [Rule 1: e.g., "All monetary values stored in cents (integer)"]
- [Rule 2: e.g., "User emails must be verified before any write operations"]
- [Rule 3: e.g., "Orders cannot be modified after payment processing begins"]

## Development Workflows
- **Feature Branch**: `feat/ISSUE-slug` from main, draft PR immediately, conventional commits, squash-merge
- **Bug Fix**: Write failing test first, fix, verify, PR with `Fixes #ISSUE`
- **Database Migration**: Generate migration, review SQL, test rollback, update seeds, verify staging
- **Deployment**: Merge to main triggers CI; staging auto-deploy; production requires manual approval

## Commands
```
[npm run dev]          # Start development server
[npm test]             # Run test suite
[npm run lint]         # Lint check
[npm run build]        # Production build
[npm run db:migrate]   # Run database migrations
[npm run db:seed]      # Seed database
```

---

## Memory System

This project uses a structured memory system with six types. Follow these protocols to maintain project knowledge across sessions.

### Memory Locations
- **Episodic**: `.claude/memory/episodic/` — Past decisions, incidents, milestones
- **Semantic**: This file (core rules) + `.claude/memory/semantic/` (detailed domain knowledge)
- **Procedural**: This file (workflow rules) + `.claude/memory/procedural/` (detailed guides)
- **Working**: Conversation context + TodoWrite (current session only)
- **Short-term**: Conversation context (current session only)
- **Long-term**: `~/.claude/projects/*/memory/MEMORY.md` (personal preferences, auto-loaded)

### Memory Read Protocol

**Before generating code**: Apply rules from this file (semantic) and preferences from MEMORY.md (long-term).

**Before architectural decisions**:
1. List `.claude/memory/episodic/*.md` for relevant past decisions
2. Read matching entries
3. Reference past decisions and lessons in your reasoning

**Before starting a standard task**:
1. Check this file's Development Workflows section
2. Read relevant `.claude/memory/procedural/*.md` for detailed steps

**During multi-step problems**: Use TodoWrite to decompose and track. Log hypotheses in conversation.

### Memory Write Protocol

**After significant decisions**: Create `.claude/memory/episodic/YYYY-MM-DD-slug.md` with:
- Category (ARCH/TECH/INC/DEBUG/MILE), impact level
- Context, decision, rationale, alternatives considered, outcome, lessons

**When discovering new project rules**: Update this file (if concise) or add to `.claude/memory/semantic/`

**When refining workflows**: Update `.claude/memory/procedural/` guides

**When user states a preference**: Update `MEMORY.md` immediately

**When user corrects you**: Fix the relevant memory entry (MEMORY.md, this file, or semantic files)

### Memory Promotion Rules
- Working memory finding that reveals a pattern → Episodic entry
- Episodic pattern observed 3+ times → Semantic rule (add to this file)
- Semantic rule that defines a workflow → Procedural guide
- Repeated preference → Long-term memory (MEMORY.md)

### Memory Maintenance
- Keep this file under 200 lines of actionable content
- Keep MEMORY.md under 200 lines (link to detail files for depth)
- Review `.claude/memory/episodic/` quarterly — archive entries older than 1 year
- After user corrections, update or remove incorrect memory entries immediately
