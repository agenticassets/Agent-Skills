#!/usr/bin/env bash
# scan-context.sh - Scan a codebase for all AI agent context engineering artifacts
# Usage: bash scan-context.sh [project-root]
# Outputs a structured inventory to stdout

set -uo pipefail

ROOT="${1:-.}"
ROOT="$(cd "$ROOT" && pwd)"

# Colors (disabled if not a terminal)
if [ -t 1 ]; then
  BOLD='\033[1m' DIM='\033[2m' GREEN='\033[32m' YELLOW='\033[33m' RED='\033[31m' CYAN='\033[36m' RESET='\033[0m'
else
  BOLD='' DIM='' GREEN='' YELLOW='' RED='' CYAN='' RESET=''
fi

header() { echo -e "\n${BOLD}${CYAN}=== $1 ===${RESET}"; }
found() { echo -e "  ${GREEN}[FOUND]${RESET} $1"; }
missing() { echo -e "  ${YELLOW}[MISSING]${RESET} $1"; }
warn() { echo -e "  ${RED}[WARN]${RESET} $1"; }
info() { echo -e "  ${DIM}$1${RESET}"; }

# Counters
TOTAL_FOUND=0
TOTAL_MISSING=0
TOTAL_WARNINGS=0

track_found() { TOTAL_FOUND=$((TOTAL_FOUND + 1)); }
track_missing() { TOTAL_MISSING=$((TOTAL_MISSING + 1)); }
track_warn() { TOTAL_WARNINGS=$((TOTAL_WARNINGS + 1)); }

# ─── GIT LAST-MODIFIED HELPERS ───
# Detect if project is a git repo
HAS_GIT=false
if git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then
  HAS_GIT=true
fi

# git_age <file-path>
# Prints relative date string (e.g., "3 days ago") or "untracked" / "no git"
# Sets global GIT_DAYS_AGO to integer days since last commit touching this file
GIT_DAYS_AGO=0
git_age() {
  local file="$1"
  GIT_DAYS_AGO=0
  if [ "$HAS_GIT" = false ]; then
    echo "no git"
    return
  fi
  local rel_path="${file#$ROOT/}"
  # Get the epoch timestamp of the last commit that touched this file
  local epoch
  epoch=$(git -C "$ROOT" log -1 --format='%at' -- "$rel_path" 2>/dev/null)
  if [ -z "$epoch" ]; then
    echo "untracked"
    return
  fi
  # Calculate days ago
  local now
  now=$(date +%s 2>/dev/null || echo 0)
  GIT_DAYS_AGO=$(( (now - epoch) / 86400 ))
  # Get human-readable relative date
  local relative
  relative=$(git -C "$ROOT" log -1 --format='%cr' -- "$rel_path" 2>/dev/null)
  echo "$relative"
}

# Staleness thresholds (days)
STALE_WARN=90
STALE_CRITICAL=180
TOTAL_STALE=0

echo -e "${BOLD}Context Engineering Scan${RESET}"
echo "Project: $ROOT"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date)"
if [ "$HAS_GIT" = true ]; then
  info "Git detected: last-modified dates from commit history"
else
  info "Not a git repo: last-modified dates unavailable"
fi

# ─── 1. CLAUDE.md FILES ───
header "CLAUDE.md Files"

check_claude_md() {
  local path="$1" label="$2"
  if [ -f "$path" ]; then
    local lines size
    lines=$(wc -l < "$path" 2>/dev/null || echo 0)
    size=$(wc -c < "$path" 2>/dev/null || echo 0)
    local age
    age=$(git_age "$path")
    found "$label ($lines lines, $size bytes, ${age})"
    track_found

    # Staleness check
    if [ "$GIT_DAYS_AGO" -ge "$STALE_CRITICAL" ]; then
      warn "$label last updated ${GIT_DAYS_AGO}d ago - likely contains stale context"
      track_warn
      TOTAL_STALE=$((TOTAL_STALE + 1))
    elif [ "$GIT_DAYS_AGO" -ge "$STALE_WARN" ]; then
      warn "$label last updated ${GIT_DAYS_AGO}d ago - review for staleness"
      track_warn
      TOTAL_STALE=$((TOTAL_STALE + 1))
    fi

    # Quality checks
    if [ "$lines" -gt 2000 ]; then
      warn "$label exceeds 2000 lines - consider splitting into modular docs"
      track_warn
    fi
    if [ "$lines" -lt 10 ]; then
      warn "$label is very short ($lines lines) - may lack essential context"
      track_warn
    fi

    # Check for key sections
    local has_commands=false has_architecture=false has_antipatterns=false has_stack=false
    if grep -qi "command\|script\|pnpm\|npm\|yarn\|make" "$path" 2>/dev/null; then has_commands=true; fi
    if grep -qi "architect\|pattern\|structure\|layout" "$path" 2>/dev/null; then has_architecture=true; fi
    if grep -qi "never\|don't\|avoid\|anti.pattern\|mistake" "$path" 2>/dev/null; then has_antipatterns=true; fi
    if grep -qi "stack\|framework\|runtime\|language" "$path" 2>/dev/null; then has_stack=true; fi

    if [ "$has_commands" = false ]; then info "  Missing: essential commands section"; fi
    if [ "$has_architecture" = false ]; then info "  Missing: architecture/patterns section"; fi
    if [ "$has_antipatterns" = false ]; then info "  Missing: anti-patterns / 'never do' rules"; fi
    if [ "$has_stack" = false ]; then info "  Missing: tech stack definition"; fi
  else
    missing "$label"
    track_missing
  fi
}

check_claude_md "$ROOT/CLAUDE.md" "Root CLAUDE.md"
check_claude_md "$ROOT/.claude/CLAUDE.md" ".claude/CLAUDE.md"

# Scan for module-level CLAUDE.md files
MODULE_MDS=$(find "$ROOT" -name "CLAUDE.md" -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*" -not -path "*/.next/*" -not -path "*/vendor/*" 2>/dev/null || true)
MODULE_COUNT=$(echo "$MODULE_MDS" | grep -c . 2>/dev/null || echo 0)
info "Total CLAUDE.md files found: $MODULE_COUNT"
if [ "$MODULE_COUNT" -gt 0 ]; then
  echo "$MODULE_MDS" | while read -r f; do
    rel="${f#$ROOT/}"
    lines=$(wc -l < "$f" 2>/dev/null || echo 0)
    age=$(git_age "$f")
    local_stale=""
    if [ "$GIT_DAYS_AGO" -ge "$STALE_CRITICAL" ]; then
      local_stale=" ${RED}STALE${RESET}"
    elif [ "$GIT_DAYS_AGO" -ge "$STALE_WARN" ]; then
      local_stale=" ${YELLOW}aging${RESET}"
    fi
    info "  $rel ($lines lines, ${age})${local_stale}"
  done
fi

# @path Import Validation
PATH_REFS_FOUND=0
BROKEN_REFS=0
while IFS= read -r claude_file; do
  if [ -f "$claude_file" ]; then
    while IFS= read -r raw_match; do
      # Strip leading @ to get the actual file path
      ref_path="${raw_match#@}"
      if [ -n "$ref_path" ]; then
        PATH_REFS_FOUND=$((PATH_REFS_FOUND + 1))
        full_path="$ROOT/$ref_path"
        if [ ! -f "$full_path" ] && [ ! -d "$full_path" ]; then
          warn "Broken @path reference: @$ref_path (in $(basename "$claude_file"))"
          track_warn
          BROKEN_REFS=$((BROKEN_REFS + 1))
        fi
      fi
    done <<< "$(grep -oE '@[a-zA-Z][a-zA-Z0-9_/.-]+\.(md|tsx?|jsx?|json|yaml|yml|sh)' "$claude_file" 2>/dev/null || true)"
  fi
done <<< "$MODULE_MDS"
if [ "$PATH_REFS_FOUND" -gt 0 ]; then
  if [ "$BROKEN_REFS" -eq 0 ]; then
    found "@path references: $PATH_REFS_FOUND found, all valid"
    track_found
  else
    warn "@path references: $BROKEN_REFS of $PATH_REFS_FOUND broken"
  fi
fi

# Emphasis Marker Analysis
for claude_file in "$ROOT/CLAUDE.md" "$ROOT/.claude/CLAUDE.md"; do
  if [ -f "$claude_file" ]; then
    label="$(basename "$(dirname "$claude_file")")/$(basename "$claude_file")"
    if [ "$claude_file" = "$ROOT/CLAUDE.md" ]; then label="Root CLAUDE.md"; fi
    emphasis_count=$(grep -ciE '\bNEVER\b|\bALWAYS\b|\bIMPORTANT\b|\bMUST\b|\bCRITICAL\b' "$claude_file" 2>/dev/null || echo 0)
    if [ "$emphasis_count" -eq 0 ]; then
      warn "$label has zero emphasis markers (NEVER/ALWAYS/MUST/IMPORTANT/CRITICAL) — critical rules may lack weight"
      track_warn
    else
      info "$label: $emphasis_count emphasis markers found"
    fi
  fi
done

# CLAUDE.local.md Detection
for local_file in "$ROOT/CLAUDE.local.md" "$ROOT/.claude/CLAUDE.local.md"; do
  if [ -f "$local_file" ]; then
    local_lines=$(wc -l < "$local_file" 2>/dev/null || echo 0)
    found "$(basename "$local_file") ($local_lines lines) — personal overrides"
    track_found
  fi
done

# ─── 2. HOOKS (.claude/settings.json) ───
header "Hooks Configuration"

SETTINGS="$ROOT/.claude/settings.json"
if [ -f "$SETTINGS" ]; then
  settings_age=$(git_age "$SETTINGS")
  found ".claude/settings.json (${settings_age})"
  track_found

  # Check for hook events
  for event in SessionStart SessionEnd PreToolUse PostToolUse PreAgentLoop PostAgentLoop UserPromptSubmit AgentMessage; do
    if grep -q "\"$event\"" "$SETTINGS" 2>/dev/null; then
      found "Hook: $event"
      track_found
    fi
  done

  # Check for allowed/denied tools
  if grep -q "allowedTools\|denyList\|permissions" "$SETTINGS" 2>/dev/null; then
    found "Tool permissions configured"
    track_found
  fi
else
  missing ".claude/settings.json (no hooks configured)"
  track_missing
fi

# ─── 3. SLASH COMMANDS ───
header "Slash Commands"

CMD_DIR="$ROOT/.claude/commands"
if [ -d "$CMD_DIR" ]; then
  CMD_COUNT=$(find "$CMD_DIR" -name "*.md" 2>/dev/null | wc -l)
  found "Commands directory ($CMD_COUNT command files)"
  track_found
  find "$CMD_DIR" -name "*.md" 2>/dev/null | while read -r f; do
    rel="${f#$ROOT/}"
    age=$(git_age "$f")
    has_frontmatter=false
    if head -1 "$f" 2>/dev/null | grep -q "^---"; then has_frontmatter=true; fi
    if [ "$has_frontmatter" = true ]; then
      info "  $rel (has frontmatter, ${age})"
    else
      info "  $rel (no frontmatter, ${age})"
    fi
  done
else
  missing "No .claude/commands/ directory"
  track_missing
fi

# ─── 4. SKILLS ───
header "Skills"

SKILL_DIR="$ROOT/.claude/skills"
if [ -d "$SKILL_DIR" ]; then
  SKILL_COUNT=$(find "$SKILL_DIR" -name "SKILL.md" 2>/dev/null | wc -l)
  found "Skills directory ($SKILL_COUNT skills)"
  track_found
  find "$SKILL_DIR" -name "SKILL.md" 2>/dev/null | while read -r f; do
    skill_dir="$(dirname "$f")"
    skill_name="$(basename "$skill_dir")"
    age=$(git_age "$f")
    has_scripts=$(find "$skill_dir/scripts" -type f 2>/dev/null | wc -l)
    has_refs=$(find "$skill_dir/references" -type f 2>/dev/null | wc -l)
    has_assets=$(find "$skill_dir/assets" -type f 2>/dev/null | wc -l)
    info "  $skill_name (scripts:$has_scripts refs:$has_refs assets:$has_assets, ${age})"
    # Skill description quality check
    local_desc=""
    if head -20 "$f" 2>/dev/null | grep -q "^---"; then
      local_desc=$(sed -n '/^---$/,/^---$/p' "$f" 2>/dev/null | grep -i "^description:" | sed 's/^description:[[:space:]]*//' | tr -d "\"'" || true)
    fi
    if [ -n "$local_desc" ]; then
      desc_len=${#local_desc}
      if [ "$desc_len" -lt 50 ]; then
        warn "  $skill_name: description too short ($desc_len chars) — poor trigger matching"
        track_warn
      fi
    else
      info "  $skill_name: no description in frontmatter"
    fi
    # Check for disable-model-invocation
    if head -20 "$f" 2>/dev/null | grep -qi "disable-model-invocation"; then
      info "  $skill_name: disable-model-invocation set (side-effect skill)"
    fi
  done
else
  missing "No .claude/skills/ directory"
  track_missing
fi

# ─── 5. CURSOR/AGENT RULES ───
header "IDE & Agent Rules"

CURSOR_RULES="$ROOT/.cursor/rules"
if [ -d "$CURSOR_RULES" ]; then
  RULE_COUNT=$(find "$CURSOR_RULES" -name "*.mdc" -o -name "*.md" 2>/dev/null | wc -l)
  found ".cursor/rules/ ($RULE_COUNT rule files)"
  track_found
else
  missing "No .cursor/rules/ directory"
  track_missing
fi

AGENT_RULES="$ROOT/.agent/rules"
if [ -d "$AGENT_RULES" ]; then
  RULE_COUNT=$(find "$AGENT_RULES" -name "*.md" 2>/dev/null | wc -l)
  found ".agent/rules/ ($RULE_COUNT rule files)"
  track_found
else
  info "No .agent/rules/ directory (optional)"
fi

# ─── 6. SUBAGENTS ───
header "Subagents"

AGENTS_DIR="$ROOT/.claude/agents"
if [ -d "$AGENTS_DIR" ]; then
  AGENT_COUNT=$(find "$AGENTS_DIR" -name "*.md" -o -name "*.yml" -o -name "*.yaml" 2>/dev/null | wc -l)
  found ".claude/agents/ ($AGENT_COUNT agent definitions)"
  track_found
else
  info "No .claude/agents/ directory (optional)"
fi

# Check for AGENTS.md / CLAUDE_AGENTS.md
for f in AGENTS.md CLAUDE_AGENTS.md; do
  if [ -f "$ROOT/$f" ]; then
    age=$(git_age "$ROOT/$f")
    found "$f (agent registry, ${age})"
    track_found
  fi
done

# ─── 7. SUPPORTING DOCS ───
header "Supporting Documentation"

for f in README.md CONTRIBUTING.md docs/ARCHITECTURE.md .env.example; do
  if [ -f "$ROOT/$f" ]; then
    age=$(git_age "$ROOT/$f")
    found "$f (${age})"
    track_found
  else
    info "No $f"
  fi
done

DOCS_DIR="$ROOT/docs"
if [ -d "$DOCS_DIR" ]; then
  DOC_COUNT=$(find "$DOCS_DIR" -name "*.md" 2>/dev/null | wc -l)
  found "docs/ directory ($DOC_COUNT markdown files)"
  track_found
fi

# ─── 8. CONTEXT BUDGET ESTIMATE ───
header "Context Budget Estimate"

TOTAL_CONTEXT_BYTES=0
while IFS= read -r f; do
  if [ -f "$f" ]; then
    bytes=$(wc -c < "$f" 2>/dev/null || echo 0)
    TOTAL_CONTEXT_BYTES=$((TOTAL_CONTEXT_BYTES + bytes))
  fi
done <<EOF
$ROOT/CLAUDE.md
$ROOT/.claude/CLAUDE.md
EOF

# Add module CLAUDE.md files
if [ -n "$MODULE_MDS" ]; then
  while IFS= read -r f; do
    if [ -f "$f" ]; then
      bytes=$(wc -c < "$f" 2>/dev/null || echo 0)
      TOTAL_CONTEXT_BYTES=$((TOTAL_CONTEXT_BYTES + bytes))
    fi
  done <<< "$MODULE_MDS"
fi

# Add estimated skill description overhead (~100 tokens per skill)
if [ -d "$SKILL_DIR" ]; then
  skill_overhead_count=$(find "$SKILL_DIR" -name "SKILL.md" 2>/dev/null | wc -l)
  skill_overhead=$((skill_overhead_count * 400))
  TOTAL_CONTEXT_BYTES=$((TOTAL_CONTEXT_BYTES + skill_overhead))
  info "Skill descriptions: ~$skill_overhead_count skills (~$((skill_overhead / 4)) tokens overhead)"
fi

# Check for MCP servers
if [ -f "$SETTINGS" ] && grep -qi "mcp\|mcpServers" "$SETTINGS" 2>/dev/null; then
  info "MCP servers configured — tool lists add to session context (variable cost)"
fi

# Rough token estimate (1 token ~ 4 chars)
EST_TOKENS=$((TOTAL_CONTEXT_BYTES / 4))
info "Auto-loaded context: ~${TOTAL_CONTEXT_BYTES} bytes (~${EST_TOKENS} tokens)"

if [ "$EST_TOKENS" -gt 30000 ]; then
  warn "Auto-loaded context exceeds ~30K tokens - risk of attention dilution"
  track_warn
elif [ "$EST_TOKENS" -gt 15000 ]; then
  info "Auto-loaded context is moderate (~${EST_TOKENS} tokens) - monitor for growth"
elif [ "$EST_TOKENS" -lt 500 ]; then
  warn "Auto-loaded context is very small (~${EST_TOKENS} tokens) - likely insufficient"
  track_warn
fi

# ─── 9. PLUGINS ───
header "Plugins"

PLUGIN_DIR="$ROOT/.claude/plugins"
if [ -d "$PLUGIN_DIR" ]; then
  PLUGIN_COUNT=$(find "$PLUGIN_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
  found "Plugins directory ($PLUGIN_COUNT plugins)"
  track_found
  find "$PLUGIN_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | while read -r p; do
    info "  $(basename "$p")"
  done
else
  info "No .claude/plugins/ directory (optional)"
fi

# ─── SUMMARY ───
header "Summary"
echo -e "  ${GREEN}Found:${RESET}    $TOTAL_FOUND artifacts"
echo -e "  ${YELLOW}Missing:${RESET}  $TOTAL_MISSING artifacts"
echo -e "  ${RED}Warnings:${RESET} $TOTAL_WARNINGS issues"
if [ "$TOTAL_STALE" -gt 0 ]; then
  echo -e "  ${YELLOW}Stale:${RESET}    $TOTAL_STALE files not updated in ${STALE_WARN}+ days"
fi
echo ""

if [ "$TOTAL_MISSING" -gt 3 ]; then
  echo -e "  ${RED}Context engineering is MINIMAL.${RESET} Significant gaps exist."
  echo "  Run this skill's audit workflow for detailed recommendations."
elif [ "$TOTAL_MISSING" -gt 1 ]; then
  echo -e "  ${YELLOW}Context engineering is DEVELOPING.${RESET} Some gaps to address."
elif [ "$TOTAL_WARNINGS" -gt 2 ]; then
  echo -e "  ${YELLOW}Context engineering is GOOD but has quality issues.${RESET}"
else
  echo -e "  ${GREEN}Context engineering is STRONG.${RESET} Well-structured context layer."
fi
