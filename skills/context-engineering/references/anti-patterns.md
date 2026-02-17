# Context Engineering Anti-Patterns

Common mistakes that degrade AI agent effectiveness, with symptoms and fixes.

## Table of Contents

1. [The Void (No Context)](#1-the-void)
2. [The Novel (Over-stuffed Context)](#2-the-novel)
3. [The Echo Chamber (Duplicated Context)](#3-the-echo-chamber)
4. [The Fossil (Stale Context)](#4-the-fossil)
5. [The Fog (Vague Context)](#5-the-fog)
6. [The Flat File (No Modularity)](#6-the-flat-file)
7. [The Trust Fall (No Guardrails)](#7-the-trust-fall)
8. [The Kitchen Sink (Irrelevant Context)](#8-the-kitchen-sink)
9. [The Blind Spot (Missing Critical Context)](#9-the-blind-spot)
10. [The Contradiction (Conflicting Context)](#10-the-contradiction)
11. [The Wrong Tool (Misplaced Mechanism)](#11-the-wrong-tool)
12. [The Attention Trap (Buried Critical Rules)](#12-the-attention-trap)

---

## 1. The Void

**What**: No CLAUDE.md or context files. Agent starts every session with zero project knowledge.

**Symptoms**:
- Agent asks the same questions every session
- Generates code in wrong style/patterns
- Doesn't know the tech stack, commands, or project structure
- Makes easily preventable mistakes

**Fix**: Create a root CLAUDE.md with the universal essentials (stack, commands, critical rules, naming conventions, architecture overview). Even 50 well-written lines dramatically improve agent effectiveness.

---

## 2. The Novel

**What**: CLAUDE.md is 3000+ lines of exhaustive documentation. Attention dilution makes the agent miss critical rules.

**Symptoms**:
- Agent ignores rules that ARE documented
- Inconsistent adherence to standards (sometimes follows, sometimes doesn't)
- Critical rules buried in walls of text get overlooked
- Agent performance degrades as context grows

**Fix**:
- Keep root CLAUDE.md under 200 lines of high-signal content
- Move detailed reference material to module-level CLAUDE.md files or `docs/`
- Use progressive disclosure: critical rules at top, details in linked files
- Apply the "token cost" test: does this line justify its place in the attention budget?

---

## 3. The Echo Chamber

**What**: Same information repeated across root CLAUDE.md, module CLAUDE.md files, README, and comments.

**Symptoms**:
- Updates to one location don't propagate to others
- Agent sees slightly different versions of the same rule and gets confused
- Context budget wasted on redundant information
- Contradictions emerge as copies drift apart

**Fix**:
- Single source of truth for each piece of information
- Root CLAUDE.md: cross-project standards and critical rules
- Module CLAUDE.md: module-specific patterns and decisions
- Use @path references to link, not copy

---

## 4. The Fossil

**What**: Context files reference deprecated APIs, removed features, old patterns, or past implementation plans.

**Symptoms**:
- Agent generates code using deprecated patterns
- References files or functions that no longer exist
- Follows migration guides for already-completed migrations
- Implements workarounds for bugs that have been fixed

**Fix**:
- Review context files quarterly (or after major refactors)
- Delete completed implementation plans and migration guides
- Mark context with dates: `_Last Updated: YYYY-MM-DD_`
- Add "docs sync" to your PR/deploy checklist

---

## 5. The Fog

**What**: Instructions are vague, subjective, or unactionable ("write clean code", "follow best practices", "use good patterns").

**Symptoms**:
- Agent's interpretation varies session to session
- Code quality is inconsistent despite having "guidelines"
- Agent adds unnecessary complexity trying to be "best practice"
- Different team members get different results

**Fix**: Replace vague rules with specific, testable instructions:

| Bad | Good |
|-----|------|
| "Write clean code" | "Use early returns. Max function length: 40 lines. Max nesting: 3 levels." |
| "Follow best practices" | "Server Components by default. Add `'use client'` only for hooks/interactivity." |
| "Good error handling" | "Return `{ error: string, code: number }` for user-facing errors. Use Zod for input validation." |
| "Use proper naming" | "Files: kebab-case. Components: PascalCase. Functions: camelCase. Constants: UPPER_SNAKE_CASE." |

---

## 6. The Flat File

**What**: Everything in one giant root CLAUDE.md. No module-level context, no skills, no commands.

**Symptoms**:
- Root CLAUDE.md grows endlessly
- Context about database patterns loads even when working on UI
- Hard to maintain and navigate
- Module-specific details are either missing or bloating the root

**Fix**:
- Root CLAUDE.md: universal rules, stack, commands (100-200 lines)
- Module CLAUDE.md files for each major directory
- Skills for complex domain workflows
- Slash commands for frequent operations
- Reference docs in `docs/` for deep dives

---

## 7. The Trust Fall

**What**: No hooks, no guardrails, no file protections. Relying entirely on CLAUDE.md text instructions for safety.

**Symptoms**:
- Agent occasionally edits production configs
- Code style varies because formatting isn't enforced
- Agent uses wrong tools or makes risky operations
- Mistakes that hooks could have prevented

**Fix**:
- `PostToolUse` hooks for auto-formatting (deterministic, not LLM-dependent)
- `PreToolUse` hooks to block edits to sensitive files
- `SessionStart` hooks for environment setup
- Tool allowlists/denylists in settings.json

---

## 8. The Kitchen Sink

**What**: Context includes information the agent doesn't need: deployment runbooks, team onboarding docs, historical ADRs, verbose changelogs.

**Symptoms**:
- High token usage with low agent effectiveness
- Agent references irrelevant information in responses
- Important context crowded out by noise
- Slow session startup

**Fix**: Apply the relevance test to every line: "Will an AI coding agent need this to write better code in this project?" If no, remove it or move it to human-only docs. Context files are for the agent, not for human onboarding.

---

## 9. The Blind Spot

**What**: Critical project knowledge exists only in team members' heads, not in context files.

**Symptoms**:
- Agent makes mistakes that any team member would avoid
- Certain files or patterns always require manual correction
- Agent doesn't know about unwritten conventions
- "The agent should have known not to do that"

**Common blind spots**:
- Database migration workflow and gotchas
- Environment-specific behavior differences
- Implicit dependencies between modules
- Business logic constraints not obvious from code
- Performance-sensitive code paths
- Security boundaries and threat model
- Third-party API quirks and rate limits

**Fix**: When you find yourself correcting the agent repeatedly on the same topic, that's a blind spot. Document it immediately. Run periodic "what does the agent not know?" sessions with the team.

---

## 10. The Contradiction

**What**: Different context files give conflicting instructions. Root says one thing, module docs say another.

**Symptoms**:
- Agent behavior is unpredictable and inconsistent
- Agent follows one rule in some sessions, the opposite in others
- Team members report different experiences
- Debugging reveals the agent was following a conflicting instruction

**Fix**:
- Establish clear precedence: module overrides root, explicit overrides implicit
- Document precedence rules in root CLAUDE.md
- Audit for contradictions periodically (search for NEVER/ALWAYS across all context files)
- When updating a rule, search for all references to the same topic

---

## 11. The Wrong Tool

**What**: Using CLAUDE.md for rules that need deterministic enforcement (formatting, file protection) or stuffing domain reference material that should be a skill.

**Symptoms**:
- CLAUDE.md is bloated with reference material the agent rarely needs
- Rules are sometimes followed, sometimes not (probabilistic adherence)
- Agent loads domain docs it doesn't need for every task
- Formatting or file protection rules are inconsistently enforced

**Fix**:
- Move deterministic rules to hooks (formatting → PostToolUse, file protection → PreToolUse)
- Move domain reference material to skills (loaded only when relevant)
- Keep only "always needed, advisory" content in CLAUDE.md
- Read `references/feature-selection.md` for the full decision tree

---

## 12. The Attention Trap

**What**: Critical rules buried deep in CLAUDE.md without emphasis markers, or hidden in the middle of long paragraphs.

**Symptoms**:
- Agent ignores specific critical rules even though they're documented
- Follows most rules but misses the important ones
- Behavior is inconsistent on the "must never" items
- Rules work when CLAUDE.md is short, break when it grows

**Fix**:
- Move critical rules to the top of CLAUDE.md (attention decays with position)
- Use emphasis markers: **NEVER**, **ALWAYS**, **IMPORTANT**, **MUST**, **CRITICAL**
- Keep critical rules as standalone bullets, not embedded in paragraphs
- For the most critical rules, consider hooks (deterministic enforcement)
- Test: bold the rule, put it first — if still ignored, it needs a hook

---

## Quick Diagnostic

If the agent is struggling, check these in order:

1. **Does CLAUDE.md exist?** (rules out The Void)
2. **Is it under 200 lines?** (rules out The Novel)
3. **Are critical rules at the top?** (rules out attention decay)
4. **Are instructions specific?** (rules out The Fog)
5. **Are there contradictions?** (search NEVER/ALWAYS across files)
6. **Is the context current?** (check dates, look for deprecated references)
7. **What's the token budget?** (estimate: chars / 4 = tokens)
8. **What's NOT documented?** (the most impactful improvement is usually filling a blind spot)
9. **Is each rule using the right mechanism?** (CLAUDE.md for advisory, hooks for deterministic, skills for on-demand — rules out The Wrong Tool)
10. **Are critical rules emphasized and positioned?** (bold emphasis markers at top, not buried in paragraphs — rules out The Attention Trap)
