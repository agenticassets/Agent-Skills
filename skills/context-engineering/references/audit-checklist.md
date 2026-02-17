# Context Engineering Audit Checklist

Score each item: 0 (absent), 1 (partial), 2 (solid). Maximum score: 70.

## 1. CLAUDE.md Foundation (max 12)

| # | Item | Score |
|---|------|-------|
| 1.1 | Root CLAUDE.md exists and is under 2000 lines | /2 |
| 1.2 | Critical rules section at top (agent reads top-down, attention decays) | /2 |
| 1.3 | Tech stack explicitly declared (framework, language, runtime, package manager) | /2 |
| 1.4 | Essential commands documented (dev, build, test, lint, deploy) | /2 |
| 1.5 | Anti-patterns section with NEVER/ALWAYS rules and explanations | /2 |
| 1.6 | Architecture overview with key file paths and their purposes | /2 |

## 2. Progressive Disclosure & Modularity (max 10)

| # | Item | Score |
|---|------|-------|
| 2.1 | Module-level CLAUDE.md files for complex subdirectories (lib/, app/, components/) | /2 |
| 2.2 | Cross-references between root and module docs (using @path syntax or links) | /2 |
| 2.3 | Information lives in ONE place (no duplication between root and module docs) | /2 |
| 2.4 | Detailed reference material split into separate docs (not bloating CLAUDE.md) | /2 |
| 2.5 | Content ordered by importance (critical rules first, edge cases last) | /2 |

## 3. Automated Enforcement (max 10)

| # | Item | Score |
|---|------|-------|
| 3.1 | .claude/settings.json exists with hook configuration | /2 |
| 3.2 | PostToolUse hooks for auto-formatting (prettier, eslint --fix) | /2 |
| 3.3 | PreToolUse hooks for file protection (production configs, secrets) | /2 |
| 3.4 | SessionStart hooks for environment setup (dependencies, env vars) | /2 |
| 3.5 | Hook commands are fast (<2s), scoped via matchers, and have clear error messages | /2 |

## 4. Workflows & Commands (max 8)

| # | Item | Score |
|---|------|-------|
| 4.1 | Slash commands exist for frequent workflows (review, deploy, feature scaffolding) | /2 |
| 4.2 | Commands have proper frontmatter (description, allowed-tools, argument-hint) | /2 |
| 4.3 | Commands reference project standards (@CLAUDE.md) for consistency | /2 |
| 4.4 | Skills exist for complex domain-specific capabilities | /2 |

## 5. Context Quality (max 10)

| # | Item | Score |
|---|------|-------|
| 5.1 | Instructions are specific and actionable (not vague like "write good code") | /2 |
| 5.2 | Concrete examples of preferred patterns (code snippets, not just descriptions) | /2 |
| 5.3 | Error-prone areas have explicit guardrails (common mistakes section) | /2 |
| 5.4 | Naming conventions are explicit (file naming, variable naming, component naming) | /2 |
| 5.5 | Database/API patterns documented with examples | /2 |

## 6. Context Budget & Hygiene (max 10)

| # | Item | Score |
|---|------|-------|
| 6.1 | Auto-loaded context is under 30K tokens (avoids attention dilution) | /2 |
| 6.2 | No stale, outdated, or contradictory instructions across files | /2 |
| 6.3 | No irrelevant context (implementation plans from past tasks, verbose changelogs) | /2 |
| 6.4 | Security: no secrets, credentials, or sensitive data in context files | /2 |
| 6.5 | Docs stay current: process exists for updating context when code changes | /2 |

## 7. Feature Architecture (max 10)

| # | Item | Score |
|---|------|-------|
| 7.1 | Right mechanism used for each rule type (hooks for deterministic, CLAUDE.md for advisory, skills for on-demand) | /2 |
| 7.2 | @path imports used to keep CLAUDE.md modular (large docs linked, not inlined) | /2 |
| 7.3 | Critical rules use emphasis markers (NEVER, ALWAYS, IMPORTANT, MUST) | /2 |
| 7.4 | Skills have quality descriptions (>50 chars, include trigger scenarios) | /2 |
| 7.5 | Agent has verification workflows (tests, linters, or checks it can run to self-validate) | /2 |

---

## Maturity Levels

| Score | Level | Description |
|-------|-------|-------------|
| 0-17 | **Minimal** | Little to no context engineering. Agent operates blind each session. |
| 18-35 | **Developing** | Basic foundation exists but significant gaps reduce agent effectiveness. |
| 36-52 | **Proficient** | Solid context layer. Agent works effectively for most tasks. |
| 53-64 | **Advanced** | Comprehensive context with automation. Agent operates semi-autonomously. |
| 65-70 | **Expert** | Full context engineering maturity. Agent is maximally effective. |

## Gap Priority Matrix

When addressing gaps, prioritize by impact:

| Priority | Category | Rationale |
|----------|----------|-----------|
| P0 | CLAUDE.md Foundation | Without this, every session starts from zero |
| P1 | Context Quality | Vague instructions cause more harm than no instructions |
| P1 | Anti-patterns | Preventing wrong moves is higher ROI than enabling right ones |
| P2 | Progressive Disclosure | Matters at scale; small projects can defer |
| P2 | Context Budget | Matters when auto-loaded context exceeds ~15K tokens |
| P3 | Hooks & Automation | High value but can be added incrementally |
| P3 | Commands & Skills | Workflow optimization; useful after foundation is solid |
