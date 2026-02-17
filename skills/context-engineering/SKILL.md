---
name: context-engineering
description: "Advanced AI agent context engineering: audit, optimize, and architect the context layer (CLAUDE.md files, hooks, slash commands, skills, IDE rules) that governs how AI coding agents understand and operate within any codebase. Use this skill when: (1) auditing or reviewing the current state of context engineering in a project, (2) optimizing, refining, or fixing existing context files (CLAUDE.md, hooks, commands, skills), (3) identifying missing context that would improve agent effectiveness, (4) bootstrapping context engineering from scratch for a new or under-documented project, (5) diagnosing why an AI agent is underperforming or making repeated mistakes, (6) sizing and budgeting context (how much is enough, what types matter most), (7) the user mentions CLAUDE.md strategy, context quality, agent instructions, agent memory, or context architecture."
---

# Context Engineering

Architect, audit, and optimize the context layer that governs AI agent effectiveness in any codebase.

Context engineering is the practice of structuring project information so AI coding agents understand the codebase, follow conventions, and operate effectively without repeated prompting. It encompasses CLAUDE.md files, hooks, slash commands, skills, and IDE rules.

## Core Mechanisms

| Mechanism | Loaded | Persistence | Purpose |
|-----------|--------|-------------|---------|
| **CLAUDE.md** | Auto (startup) | Persistent | Project standards, architecture, rules |
| **Hooks** | Event-triggered | Per-session | Automated enforcement, validation |
| **Slash Commands** | User-invoked | On-demand | Frequent workflows, templates |
| **Skills** | Model-invoked | On-demand | Domain expertise, complex capabilities |
| **IDE Rules** (.cursor/rules, .agent/rules) | Auto/contextual | Persistent | IDE-specific guidance |

## Workflows

This skill supports five primary workflows:

1. **Audit** — Assess the current state and score maturity
2. **Optimize** — Refine and fix existing context for maximum effectiveness
3. **Gap Analysis** — Identify what's missing that should exist
4. **Bootstrap** — Set up context engineering from scratch
5. **Diagnose** — Systematic troubleshooting when an agent is underperforming

---

## Workflow 1: Audit

Assess context engineering maturity and produce a scored report with recommendations.

### Steps

1. **Scan**: Run `scripts/scan-context.sh` at the project root to inventory all context artifacts
2. **Score**: Read `references/audit-checklist.md` and score each item (0/1/2) based on scan results and file quality
3. **Analyze quality**: For each CLAUDE.md file found, evaluate:
   - Signal-to-noise ratio (is every line earning its token cost?)
   - Specificity (actionable instructions vs vague platitudes?)
   - Completeness (critical rules, stack, commands, anti-patterns, architecture?)
   - Structure (headers, scannability, progressive disclosure?)
   - Currency (references to current code, not deprecated patterns?)
4. **Identify anti-patterns**: Read `references/anti-patterns.md` and check for each one
5. **Report**: Produce a structured report:

```
# Context Engineering Audit Report

## Score: XX/70 — [Maturity Level]

## Strengths
- [What's working well]

## Critical Gaps (P0-P1)
- [What's missing or broken, ordered by impact]

## Recommendations
1. [Specific, actionable recommendation]
2. [Next recommendation]

## Detailed Scores
[Section-by-section from checklist]
```

---

## Workflow 2: Optimize

Refine existing context files for maximum agent effectiveness.

### Steps

1. **Read all context files**: Gather every CLAUDE.md, settings.json hooks, slash commands, and skill metadata in the project
2. **Apply anti-pattern checks**: Reference `references/anti-patterns.md` — look for each of the 12 anti-patterns
3. **Apply optimization passes** (in order):

**Pass 1 — Prune**: Remove stale, duplicated, vague, or irrelevant content. Every line must earn its token cost. Ask: "If this line were missing, would the agent make a concrete mistake?"

**Pass 2 — Sharpen**: Replace vague instructions with specific, testable ones:
- Bad: "Follow best practices" → Good: "Server Components by default. `'use client'` only for hooks."
- Bad: "Write clean code" → Good: "Max 40-line functions. Max 3 levels of nesting. Early returns."

**Pass 3 — Structure**: Ensure correct information architecture:
- Critical rules at top of each file (attention decays with position)
- One clear hierarchy: root CLAUDE.md → module CLAUDE.md → reference docs
- No information duplication between files (single source of truth per fact)
- Cross-references using @path or links, not copy-paste

**Pass 4 — Fortify**: Add missing guardrails:
- Anti-patterns section (NEVER/ALWAYS rules with reasons)
- Hooks for deterministic enforcement where text instructions are insufficient
- File protections for sensitive configs

**Pass 5 — Budget**: Check total auto-loaded context size:
- Target: under 30K tokens for auto-loaded content
- Warning: over 15K tokens warrants careful review
- Estimate: character count / 4 = approximate tokens

4. **Preserve structure**: Edit existing files rather than rewriting from scratch. Respect the project's existing organizational decisions.

---

## Workflow 3: Gap Analysis

Identify missing context that would improve agent effectiveness.

### Steps

1. **Determine project archetype**: Read `references/context-patterns.md` and match the project to its archetype (web app, API, library, data pipeline, ML, monorepo, research, mobile)
2. **Compare against archetype template**: Check which "Must-Have Context" items from the matched archetype are present vs missing
3. **Check universal essentials**: Every project needs these regardless of type:
   - Tech stack declaration
   - Essential commands (dev, build, test, lint)
   - Critical anti-patterns (NEVER rules)
   - File/component naming conventions
   - Error handling approach
   - Git workflow
4. **Analyze agent failure patterns**: If available, review recent agent sessions or user complaints. Repeated corrections signal undocumented knowledge (blind spots)
5. **Check feature selection**: Reference `references/feature-selection.md` and evaluate whether each rule/knowledge piece uses the right mechanism. Are deterministic rules in hooks? Is domain reference in skills? Is always-needed context in CLAUDE.md?
6. **Check context layers**: Evaluate which layers are active:

| Layer | Status | Impact if Missing |
|-------|--------|------------------|
| CLAUDE.md (root) | ? | Agent starts blind every session |
| CLAUDE.md (modules) | ? | Agent misses module-specific patterns |
| Hooks | ? | No automated enforcement of standards |
| Slash commands | ? | Frequent workflows require manual prompting |
| Skills | ? | Complex domain tasks are error-prone |
| IDE rules | ? | IDE-specific agent lacks project context |
| Plugins | ? | Distributable context bundles not leveraged |
| Subagents | ? | Complex tasks lack context isolation |

7. **Produce gap report**: List missing items ordered by impact (P0 → P3), using the priority matrix from `references/audit-checklist.md`

---

## Workflow 4: Bootstrap

Set up context engineering from scratch for a project with little or no existing context.

### Steps

1. **Explore the codebase**: Understand the project's tech stack, structure, commands, patterns, and conventions by reading key files (package.json, tsconfig, Dockerfile, Makefile, pyproject.toml, etc.)
2. **Determine archetype**: Match to `references/context-patterns.md` to know what context this project type needs
3. **Create root CLAUDE.md** following this template:

```markdown
# [Project Name]

[One-sentence description]

## Critical Rules

1. **[RULE]**: [Specific, testable instruction]
2. **[RULE]**: [Specific, testable instruction]

## Tech Stack

- **Runtime**: [e.g., Node.js 20, Python 3.12]
- **Framework**: [e.g., Next.js 16, FastAPI]
- **Database**: [e.g., PostgreSQL via Drizzle ORM]
- **Package Manager**: [e.g., pnpm]

## Commands

\`\`\`bash
[cmd]    # [description]
[cmd]    # [description]
[cmd]    # [description]
\`\`\`

## Architecture

### Key Paths
- `[path]` — [purpose]
- `[path]` — [purpose]

### Patterns
- **[Pattern]**: [brief explanation]

## Code Style

- **Files**: [naming convention]
- **Components/Functions**: [naming convention]
- **Imports**: [convention]

## Common Mistakes

- **NEVER** [anti-pattern] — [why]
- **ALWAYS** [required practice] — [why]
```

4. **Create module CLAUDE.md files** for any directory with 10+ files or complex domain logic
5. **Set up hooks**: At minimum, create `.claude/settings.json` with:
   - `PostToolUse` → auto-format edited files (if project uses a formatter)
   - `SessionStart` → dependency installation (if not trivial)
6. **Verify**: Run `scripts/scan-context.sh` to confirm the new context layer scores above "Developing" level

---

## Workflow 5: Diagnose

Systematic troubleshooting when an AI agent is underperforming despite having context files.

### Steps

1. **Establish baseline**: Run `scripts/scan-context.sh` at the project root — does context even exist? What's the inventory?
2. **Quick diagnostic**: Check the Quick Diagnostic checklist in `references/anti-patterns.md` (10-item checklist covering all 12 anti-patterns)
3. **Check feature selection**: Read `references/feature-selection.md` and verify each rule uses the right mechanism. Are deterministic rules in CLAUDE.md instead of hooks? Is domain reference bloating root context instead of living in skills?
4. **Check emphasis and positioning**: Are critical rules at the top of CLAUDE.md with emphasis markers (NEVER, ALWAYS, MUST, IMPORTANT, CRITICAL)? Rules buried deep or lacking emphasis get ignored under attention pressure.
5. **Check for contradictions**: Search NEVER/ALWAYS across all context files for conflicts. Contradicting instructions cause unpredictable agent behavior.
6. **Apply the "remove it" heuristic**: For each CLAUDE.md line, ask: "If removed, would the agent make a concrete mistake?" If no, it's noise competing for attention with the lines that matter.
7. **Check verification**: Does the agent have ways to validate its own work? Tests, linters, type checkers, formatting hooks? Agents without verification loops repeat mistakes.
8. **Produce diagnostic report**: List specific findings ordered by likely impact, with concrete fixes for each issue.

---

## Key Principles

### Token Economy
Every token of context competes for attention. A 200-line CLAUDE.md where every line prevents a concrete mistake beats a 2000-line CLAUDE.md where 80% is noise. Apply the **token cost test**: "Does this line justify its place in the ~120K token attention budget?"

### Specificity Over Generality
The agent is already smart. Don't tell it to "write good code." Tell it the specific conventions, patterns, and constraints unique to THIS project. The value of context is the delta between what the agent already knows and what it needs to know for this codebase.

### Deterministic Over Probabilistic
For rules that must ALWAYS be followed (formatting, file protection, env setup), use hooks rather than CLAUDE.md instructions. Hooks execute deterministically; text instructions are probabilistic (the agent may miss them under attention pressure).

### Progressive Disclosure
Load the minimum context needed for the current task. Critical rules auto-load via CLAUDE.md. Domain details load on demand via module docs, skills, and references. This preserves attention budget for what matters most right now.

### Single Source of Truth
Each fact lives in exactly one place. Root CLAUDE.md defines project-wide rules. Module CLAUDE.md files define module-specific rules. Neither duplicates the other. Cross-reference with @path links.

### Right Tool for the Job
Different context mechanisms serve different purposes. CLAUDE.md is for advisory always-on context. Hooks are for deterministic enforcement. Skills are for on-demand domain knowledge. MCP is for external service connections. Subagents are for context isolation. Choosing the wrong mechanism reduces effectiveness — a critical formatting rule in CLAUDE.md may be ignored, but the same rule as a PostToolUse hook runs every time. See `references/feature-selection.md` for the full decision framework.

---

## Bundled Resources

| Resource | Path | Use When |
|----------|------|----------|
| **Scan Script** | `scripts/scan-context.sh` | Starting any audit — inventories all context artifacts |
| **Audit Checklist** | `references/audit-checklist.md` | Scoring context maturity (70-point rubric) |
| **Context Patterns** | `references/context-patterns.md` | Determining what context a project type needs |
| **Anti-Patterns** | `references/anti-patterns.md` | Diagnosing why context isn't working |
| **Feature Selection** | `references/feature-selection.md` | Choosing the right context mechanism for each rule/knowledge type |

## External Resources

Authoritative references for context engineering and Claude Code:

- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic's definitive guide to context engineering principles
- [Claude Code Overview](https://code.claude.com/docs/en/overview) — Official Claude Code documentation
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices) — Best practices for CLAUDE.md, hooks, and agent effectiveness
- [Claude Code Features Overview](https://code.claude.com/docs/en/features-overview) — Complete feature landscape (skills, hooks, commands, MCP, subagents)
- [Skills Documentation](https://code.claude.com/docs/en/skills) — How skills work, packaging, and distribution
- [Agent Teams](https://code.claude.com/docs/en/agent-teams) — Multi-agent coordination and subagent patterns
- [MCP Integration](https://code.claude.com/docs/en/mcp) — Model Context Protocol server configuration
- [Claude Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) — Foundational prompt engineering for Claude
