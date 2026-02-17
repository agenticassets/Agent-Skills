# Context Patterns by Project Archetype

Use this reference to determine what context a specific project type needs, how much, and how to structure it.

## Table of Contents

1. [Web Application (Next.js / React)](#web-application)
2. [Backend API / Service](#backend-api)
3. [Library / Package](#library--package)
4. [Data Pipeline / ETL](#data-pipeline)
5. [ML / AI Project](#ml--ai-project)
6. [Monorepo](#monorepo)
7. [Research / Academic](#research--academic)
8. [Mobile / PWA](#mobile--pwa)
9. [Universal Essentials](#universal-essentials)

---

## Web Application

**Context weight**: Heavy (30-60 items). Web apps have the most surface area.

### Must-Have Context

| Category | What to Document | Why |
|----------|-----------------|-----|
| Routing | File-based routing conventions, dynamic routes, middleware | Agent creates routes in wrong locations without this |
| Components | Server vs client boundary rules, component naming, composition patterns | Prevents hydration errors and bundle bloat |
| Styling | CSS approach (Tailwind, CSS modules, etc.), spacing system, responsive breakpoints | Prevents style inconsistency |
| State | Client state approach, server state (cache, revalidation), form handling | Prevents architectural drift |
| Auth | Auth provider, session handling, protected route patterns | Security-critical; mistakes are dangerous |
| API | Route handler patterns, streaming requirements, error response format | Consistency across endpoints |
| Database | ORM patterns, migration workflow, connection handling | Prevents schema drift and connection leaks |
| Deployment | Build command, environment variables, CI/CD pipeline | Prevents broken deploys |

### Recommended Hooks

- `PostToolUse`: Auto-format with prettier/eslint after edits
- `PreToolUse`: Block edits to production configs
- `SessionStart`: Install dependencies, verify dev server

### Structure Template

```
CLAUDE.md                    # 100-200 lines: stack, commands, critical rules
app/CLAUDE.md               # Routing, API patterns, page structure
components/CLAUDE.md        # Component conventions, styling rules
lib/CLAUDE.md               # Utility organization, shared patterns
```

---

## Backend API

**Context weight**: Medium (20-40 items).

### Must-Have Context

| Category | What to Document | Why |
|----------|-----------------|-----|
| Endpoints | Route naming, HTTP methods, request/response schemas | Consistency across API surface |
| Auth/AuthZ | Authentication mechanism, role-based access, middleware chain | Security-critical |
| Validation | Input validation approach (Zod, Joi, etc.), error format | Prevents injection and bad data |
| Database | Query patterns, transaction handling, migration workflow | Data integrity |
| Error handling | Error codes, structured error format, logging levels | Debuggability |
| Testing | Test strategy (unit/integration/e2e), mocking patterns | Quality assurance |

### Structure Template

```
CLAUDE.md                    # 80-150 lines: stack, commands, API conventions
src/routes/CLAUDE.md        # Endpoint patterns, middleware
src/db/CLAUDE.md            # Schema, queries, migrations
```

---

## Library / Package

**Context weight**: Light-Medium (15-30 items). Libraries need precision over breadth.

### Must-Have Context

| Category | What to Document | Why |
|----------|-----------------|-----|
| Public API | Exported functions/types, API design principles, breaking change policy | Agent must not break consumers |
| Compatibility | Supported runtimes, peer dependencies, tree-shaking requirements | Platform-critical |
| Testing | Test coverage requirements, test patterns, benchmark thresholds | Library quality bar is high |
| Build | Build targets (CJS/ESM/types), bundling config | Distribution correctness |
| Versioning | Semver policy, changelog format | Release management |

### Structure Template

```
CLAUDE.md                    # 60-100 lines: API principles, build, test
src/CLAUDE.md               # Internal architecture, module boundaries
```

---

## Data Pipeline

**Context weight**: Medium (20-35 items). Focus on data flow and reliability.

### Must-Have Context

| Category | What to Document | Why |
|----------|-----------------|-----|
| Data flow | Pipeline stages, input/output schemas, transformation rules | Prevents data corruption |
| Sources | Connection details (redacted), data formats, refresh schedules | Integration correctness |
| Idempotency | Retry logic, deduplication, checkpoint strategy | Reliability |
| Quality | Validation rules, data quality checks, alerting thresholds | Data integrity |
| Orchestration | Scheduler (Airflow, cron, etc.), dependency graph, failure handling | Operational correctness |

### Structure Template

```
CLAUDE.md                    # 80-120 lines: pipeline overview, commands, data rules
pipelines/CLAUDE.md         # Stage-specific patterns
config/CLAUDE.md            # Environment-specific configuration
```

---

## ML / AI Project

**Context weight**: Medium-Heavy (25-45 items).

### Must-Have Context

| Category | What to Document | Why |
|----------|-----------------|-----|
| Models | Model registry, versioning, serving infrastructure | Reproducibility |
| Data | Dataset sources, preprocessing pipeline, feature definitions | Training correctness |
| Experiments | Experiment tracking tool, metric definitions, comparison methodology | Scientific rigor |
| Evaluation | Eval metrics, benchmark datasets, quality thresholds | Model quality |
| Deployment | Model serving pattern, A/B testing, rollback procedure | Production safety |
| SDK/API | AI SDK version, provider configuration, prompt patterns | Integration correctness |

### Structure Template

```
CLAUDE.md                    # 100-150 lines: stack, experiment workflow, model patterns
src/models/CLAUDE.md        # Model architecture, training patterns
src/data/CLAUDE.md          # Data pipeline, feature engineering
experiments/CLAUDE.md       # Experiment tracking, evaluation
```

---

## Monorepo

**Context weight**: Heavy (40-70 items across packages). Coordination is the challenge.

### Must-Have Context

| Category | What to Document | Why |
|----------|-----------------|-----|
| Package map | Which packages exist, their purpose, dependency relationships | Navigation |
| Shared code | Where shared utilities live, import conventions across packages | Prevents duplication |
| Build order | Package dependency graph, build orchestration (Turborepo, Nx, etc.) | Build correctness |
| Versioning | Linked vs independent versioning, release process | Coordination |
| Testing | Per-package vs integrated test strategy, shared test utilities | Quality at scale |

### Structure Template

```
CLAUDE.md                    # 80-120 lines: repo overview, package map, workspace commands
packages/shared/CLAUDE.md   # Shared code conventions
packages/web/CLAUDE.md      # Web-specific context
packages/api/CLAUDE.md      # API-specific context
```

---

## Research / Academic

**Context weight**: Light-Medium (15-30 items). Focus on reproducibility.

### Must-Have Context

| Category | What to Document | Why |
|----------|-----------------|-----|
| Structure | Directory layout (Code/, Data/, Results/, LaTeX/) | Consistent organization |
| Data | Data sources, immutability rules, transformation documentation | Reproducibility |
| Analysis | Statistical methods, software versions, random seed management | Scientific rigor |
| Output | Figure/table export format, LaTeX conventions, citation style | Publication readiness |
| Environment | Dependency management (requirements.txt, conda env), platform notes | Reproducibility |

### Structure Template

```
CLAUDE.md                    # 60-100 lines: project overview, directory layout, commands
Code/CLAUDE.md              # Analysis scripts, coding standards
LaTeX/CLAUDE.md             # Document structure, BibTeX conventions
```

---

## Mobile / PWA

**Context weight**: Medium (20-40 items).

### Must-Have Context

| Category | What to Document | Why |
|----------|-----------------|-----|
| Platform targets | iOS/Android versions, PWA requirements, browser support | Compatibility |
| Touch/input | Touch target sizes, gesture patterns, keyboard handling | Usability |
| Offline | Caching strategy, service worker patterns, sync logic | PWA compliance |
| Performance | Bundle budgets, image optimization, lazy loading patterns | Mobile performance |
| Safe areas | Viewport handling, notch/island accommodation, orientation | Device compatibility |

---

## Universal Essentials

Every project, regardless of type, should document these in CLAUDE.md:

1. **Tech stack** (framework, language version, package manager)
2. **Essential commands** (dev, build, test, lint, deploy)
3. **Critical rules** (what the agent must NEVER do)
4. **File naming conventions**
5. **Error handling approach**
6. **Git workflow** (branching, commit message format, PR process)

### @path Imports

For projects where CLAUDE.md approaches 500 lines, use `@path/to/details.md` imports to keep the root file lean. The referenced file's content loads only when explicitly imported, preserving the attention budget.

- **Official recommendation**: Keep root CLAUDE.md under ~500 lines (Anthropic docs)
- **Best practice**: Root CLAUDE.md contains rules and summaries; detailed references live in linked files
- **Syntax**: `@path/to/file.md` in CLAUDE.md to reference without inlining

### Context Sizing Guide

| Project Size | CLAUDE.md Lines | Module Docs | Skills | Hooks |
|-------------|----------------|-------------|--------|-------|
| Small (<20 files) | 40-80 | 0 | 0 | 0-1 |
| Medium (20-100 files) | 80-150 | 1-3 | 0-2 | 1-3 |
| Large (100-500 files) | 120-200 | 3-8 | 2-5 | 3-5 |
| Very Large (500+ files) | 150-250 | 8-15 | 5+ | 5+ |

Note: These are guidelines, not hard rules. A 50-file project with complex domain logic may need more context than a 200-file CRUD app.

### Feature Combination by Project Scale

| Project Scale | Recommended Mechanisms |
|--------------|----------------------|
| **Small** (<20 files) | CLAUDE.md only |
| **Medium** (20-100 files) | CLAUDE.md + hooks + 1-3 skills |
| **Large** (100-500 files) | CLAUDE.md + module docs + hooks + skills + subagents |
| **Very Large** (500+ files) | All of the above + plugins for distribution |

As projects grow, the need for progressive disclosure increases. Small projects can keep everything in one CLAUDE.md. Large projects need the full hierarchy: root CLAUDE.md for universal rules, module docs for local patterns, hooks for enforcement, skills for domain workflows, and subagents for context isolation during complex tasks.
