# Feature Selection Guide

Choosing the right context mechanism for each rule, piece of knowledge, or enforcement need.

## Feature Comparison

| Mechanism | Loaded When | Context Cost | Persistence | Best For |
|-----------|------------|--------------|-------------|----------|
| **CLAUDE.md** | Auto (every session) | Always on (~tokens = chars/4) | Persistent (git) | Project standards, architecture, always-needed rules |
| **Module CLAUDE.md** | Auto (when dir files touched) | On-demand | Persistent (git) | Directory-specific patterns, module conventions |
| **Hooks** | Event-triggered (deterministic) | Zero tokens (shell execution) | Persistent (settings.json) | Formatting, file protection, env setup, validation |
| **Slash Commands** | User-invoked | On-demand (only when called) | Persistent (git) | Frequent workflows, templates, guided procedures |
| **Skills** | Model-invoked | ~100 tokens (description) | Persistent (git) | Domain expertise, complex multi-step capabilities |
| **MCP Servers** | Session-connected | Tool list at start | Per-session config | External services, APIs, data sources |
| **Subagents** | Task-delegated | Isolated context window | Per-invocation | Heavy research, parallel work, context isolation |
| **Plugins** | Installed | Varies by plugin content | Persistent (installed) | Distributable bundles of skills + commands + hooks |
| **IDE Rules** | Auto/contextual (IDE-specific) | Always on or contextual | Persistent (git) | IDE-specific agent guidance |

## Decision Tree

**"Where should this information live?"**

Ask these questions in order:

### 1. Does it need deterministic enforcement (must happen EVERY time, no exceptions)?

**Use a Hook** (PreToolUse, PostToolUse, etc.)

Examples: auto-formatting on save, blocking edits to .env files, running type-check before commit

### 2. Is it project-wide knowledge needed in EVERY session?

**Use CLAUDE.md** (root)

Examples: tech stack, essential commands, critical anti-patterns, architecture overview, naming conventions

### 3. Is it specific to one directory or module?

**Use a Module CLAUDE.md** (e.g., `lib/db/CLAUDE.md`)

Examples: ORM patterns for the db module, component conventions for UI, API route patterns

### 4. Is it domain expertise needed only for certain tasks?

**Use a Skill**

Examples: database migration procedures, context engineering audits, complex refactoring workflows

### 5. Does it require external data, APIs, or services?

**Use an MCP Server**

Examples: fetching from databases, calling external APIs, accessing cloud services

### 6. Is it a frequent multi-step procedure the user triggers?

**Use a Slash Command**

Examples: `/deploy`, `/review-pr`, `/create-feature`

### 7. Does it require heavy research or should run in parallel?

**Use a Subagent**

Examples: codebase analysis, security audits, multi-file exploration

### 8. Should it be distributable to other projects/users?

**Use a Plugin** (bundles skills + commands + hooks)

## Context Cost Estimates

| Mechanism | Estimated Token Cost | When Charged |
|-----------|---------------------|--------------|
| Root CLAUDE.md (200 lines) | ~2,000-4,000 tokens | Every session |
| Module CLAUDE.md (50 lines) | ~500-1,000 tokens | When module files referenced |
| Each skill (description only) | ~100 tokens | Every session (for matching) |
| Each skill (full load) | ~1,000-5,000 tokens | Only when invoked |
| Slash command | ~0 tokens (until invoked) | Only when called |
| Hook | 0 tokens (shell execution) | Never (runs externally) |
| MCP tool list | ~50-200 tokens per tool | Session start |

## Common Misplacements

| Misplaced In | Should Be In | Why |
|--------------|-------------|-----|
| CLAUDE.md: "Always run prettier after editing" | Hook (PostToolUse) | Formatting needs deterministic enforcement, not advisory |
| CLAUDE.md: 500 lines of API documentation | Skill or module CLAUDE.md | Domain reference shouldn't auto-load every session |
| CLAUDE.md: "Run `pnpm lint` before committing" | Hook (PreToolUse on commit) or slash command | Procedural steps are better automated |
| Skill: "Use kebab-case for filenames" | CLAUDE.md | Universal rules belong in always-loaded context |
| Slash command: Complex domain workflow | Skill | Skills are model-invoked (more flexible trigger) |
| Root CLAUDE.md: Module-specific patterns | Module CLAUDE.md | Violates progressive disclosure; wastes attention budget |

## Combination Patterns

Mechanisms work best in combination:

| Pattern | When | Example |
|---------|------|---------|
| **CLAUDE.md + Skills** | Rules always-on, deep expertise on-demand | Root defines "use Drizzle ORM"; skill handles migration procedures |
| **CLAUDE.md + Hooks** | Advisory rules + deterministic enforcement | CLAUDE.md says "format with prettier"; hook auto-runs it |
| **Skill + MCP** | Domain workflow needing external data | Skill orchestrates analysis; MCP fetches from database |
| **Skill + Subagent** | Complex skill delegates heavy subtasks | Audit skill delegates codebase scan to subagent |
| **Hook + MCP** | Automated validation against external source | Hook triggers on file save; MCP validates against schema registry |

## The `disable-model-invocation` Pattern

For skills that are **side-effect only** (they run a script, generate a file, or perform an action rather than providing information to the model), set in SKILL.md frontmatter:

```yaml
---
disable-model-invocation: true
---
```

This prevents the skill from consuming context tokens for its full content — it only runs when explicitly invoked. Use for:
- Build/deploy scripts
- File generation templates
- Data export procedures
- Any skill where the output goes to disk, not to the conversation
