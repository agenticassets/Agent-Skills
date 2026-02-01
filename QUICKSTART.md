# Quick Start Guide

Get up and running with your personal Agent Skills collection in minutes!

## Installation

### 1. Install Core Skills

```bash
# Copy skills to Claude Code directory
cp -r ./skills/* ~/.claude/skills/

# Restart Claude Code
```

### 2. Install Recommended Document Skills (Highly Recommended)

For document processing in research and real estate workflows, install the official Anthropic skills:

**Option 1: Claude.ai Users**
- These skills are built-in and automatically available
- No installation needed

**Option 2: Claude Code Users**
- Skills are available at `/mnt/skills/public/` in your environment
- They load automatically when needed

**Option 3: Manual Installation** (if needed)
```bash
# Clone official Anthropic skills repository
git clone https://github.com/anthropics/skills.git
cd skills/skills/

# Install essential document skills
cp -r pdf ~/.claude/skills/     # PDF extraction and OCR
cp -r xlsx ~/.claude/skills/    # Excel spreadsheets and financial models
cp -r docx ~/.claude/skills/    # Word documents
cp -r pptx ~/.claude/skills/    # PowerPoint presentations
```

**Why these skills?**
- **pdf**: Extract data from offering memos, appraisals, research papers
- **xlsx**: Analyze rent rolls, create financial models, process data
- **docx**: Create investment memos, business plans
- **pptx**: Build investment committee presentations

### 3. Discover More Skills

Browse the comprehensive skill catalog at **[skills.sh](https://skills.sh/)** for additional skills.

## Test Your Installation

Try these commands to verify skills are working:

```bash
# Test FastAPI Expert
"Help me implement JWT authentication in FastAPI"

# Test pandas-pro
"Clean this DataFrame and handle missing values"

# Test Debugging Wizard
"Debug this Python stack trace"

# Test Code Reviewer
"Review this code for security vulnerabilities"

# Test PyFixest LaTeX
"Generate LaTeX tables from my PyFixest models"

# Test MCP Developer
"Build an MCP server for database access"
```

## First Steps

### 1. Understand What You Have
**<!-- SKILL_COUNT -->16<!-- /SKILL_COUNT --> skills** covering:
- **Development & Code Quality (3)**: code-documenter, code-reviewer, debugging-wizard
- **Python Development (3)**: fastapi-expert, pandas-pro, ml-pipeline
- **AI & Integration (2)**: mcp-developer, prompt-engineer
- **Research & Analysis (3)**: pyfixest-latex, cre-investment-analysis, stata-accounting-research
- **Automation (1)**: n8n-skills

### 2. Common Use Cases

**Python API Development**
```
You: "I need to implement async endpoints in FastAPI with Pydantic V2"
Claude: [Activates fastapi-expert]
```

**Data Analysis**
```
You: "Clean this CSV and create summary statistics with pandas"
Claude: [Activates pandas-pro]
```

**Debugging**
```
You: "My async Python code is throwing errors, help me debug it"
Claude: [Activates debugging-wizard]
```

**Research Analysis**
```
You: "Run DiD analysis and export LaTeX tables"
Claude: [Activates pyfixest-latex]
```

**Real Estate Analysis**
```
You: "Analyze this multifamily acquisition opportunity"
Claude: [Activates cre-investment-analysis]
```

**AI Integration**
```
You: "Build an MCP server for my database"
Claude: [Activates mcp-developer]
```

**Automation**
```
You: "Create an n8n workflow to process webhooks"
Claude: [Activates n8n-skills]
```

### 3. Best Practices

**Be Specific About Tech Stack**
✅ "Help me implement async SQLAlchemy in FastAPI"
❌ "Help me with database access"

**Mention Your Goal**
✅ "Clean this panel data for DiD analysis with PyFixest"
✅ "Review this API code for security issues"

**Combine Skills (Including Document Skills)**
✅ "Extract data from this PDF offering memo, analyze with pandas, and create a CRE investment model in Excel"
✅ "Build a FastAPI endpoint, test it, and document it"
✅ "Read this Excel rent roll, analyze with pandas, and create an investment presentation in PowerPoint"

### 4. Skill Activation Examples

| Your Request | Skills Activated |
|-------------|------------------|
| "Implement async endpoints in FastAPI" | fastapi-expert |
| "Clean and transform this DataFrame" | pandas-pro |
| "Build an ML training pipeline with MLflow" | ml-pipeline |
| "Debug this Python error" | debugging-wizard |
| "Review this code for security" | code-reviewer |
| "Generate LaTeX tables from PyFixest" | pyfixest-latex |
| "Analyze this office building investment" | cre-investment-analysis |
| "Show me STATA code for PSM" | stata-accounting-research |
| "Design prompts for this LLM task" | prompt-engineer |
| "Create an MCP server" | mcp-developer |
| "Build an n8n workflow" | n8n-skills |
| "Add docstrings to these functions" | code-documenter |
| **"Extract data from this PDF offering memo"** | **pdf** (official skill) |
| **"Create a financial model in Excel"** | **xlsx** (official skill) |
| **"Analyze this PDF appraisal + Excel rent roll"** | **pdf + xlsx + cre-investment-analysis** |

## Tips for Maximum Effectiveness

### 1. Provide Context
Include relevant information:
- Language/framework you're using (Python, FastAPI, pandas, etc.)
- What you're trying to accomplish
- Any constraints or requirements
- Error messages (if debugging)

### 2. Ask for Multiple Perspectives
```
"Review this FastAPI code for security and performance"
[Activates: code-reviewer + fastapi-expert]
```

### 3. Follow Recommended Workflows

**API Development: Design → Implement → Test → Document → Review**
1. fastapi-expert (implement)
2. debugging-wizard (troubleshoot)
3. code-documenter (add docs)
4. code-reviewer (review)

**Data Analysis: Clean → Analyze → Document**
1. pandas-pro (clean/transform)
2. pyfixest-latex or stata-accounting-research (analyze)
3. code-documenter (document)

**ML Pipeline: Prepare → Build → Track → Document**
1. pandas-pro (prepare data)
2. ml-pipeline (build pipeline)
3. prompt-engineer (add LLM components if needed)
4. code-documenter (document)

**Business Analysis: Analyze → Model → Report**
1. pandas-pro (data analysis)
2. cre-investment-analysis (financial modeling)
3. code-documenter (create reports)

### 4. Reference the Guides
- `README.md` - Overview and architecture
- `SKILLS_GUIDE.md` - Detailed skill reference
- `CLAUDE.md` - Skill authorship standards
- `CONTRIBUTING.md` - How to customize/extend

## Troubleshooting

### Skills Not Activating?
1. Restart Claude Code after installation
2. Check skill files exist: `ls ~/.claude/skills/`
3. Be more specific with framework/technology names
4. Try explicitly mentioning the skill name: "Use the fastapi-expert to help me..."

### Need Help?
- Check `SKILLS_GUIDE.md` for skill-specific guidance
- Review individual `skills/*/SKILL.md` files
- Check the `references/` folder for deep-dive documentation

## What's Next?

### Explore Skills
Browse `skills/` directory to see what each skill offers and review reference files.

### Customize
Edit any `SKILL.md` to match your preferences. See `CLAUDE.md` for authorship standards.

### Add New Skills
Create your own skills! See `CONTRIBUTING.md` for guidelines.

### Validate Changes
After modifications:
```bash
python scripts/validate-skills.py
python scripts/update-docs.py
```

## Quick Reference Card

Print or save this for quick reference:

```
PYTHON DEVELOPMENT
├─ API: fastapi-expert
├─ Data: pandas-pro
└─ ML: ml-pipeline

AI & INTEGRATION
├─ MCP: mcp-developer
└─ Prompts: prompt-engineer

RESEARCH & ANALYSIS
├─ Econometrics (Python): pyfixest-latex
├─ Econometrics (STATA): stata-accounting-research
└─ Real Estate: cre-investment-analysis

AUTOMATION
└─ Workflows: n8n-skills

CODE QUALITY
├─ Debug: debugging-wizard
├─ Review: code-reviewer
└─ Document: code-documenter

COMMON WORKFLOWS
├─ API Development: fastapi-expert → debugging-wizard → code-documenter → code-reviewer
├─ Data Analysis: pandas-pro → pyfixest-latex/stata-accounting-research → code-documenter
├─ ML Pipeline: pandas-pro → ml-pipeline → prompt-engineer → code-documenter
├─ Business Analysis: pandas-pro → cre-investment-analysis → code-documenter
└─ Automation: n8n-skills → mcp-developer → debugging-wizard
```

## Support

- 📖 Documentation: Check README.md and SKILLS_GUIDE.md
- 🔧 Maintenance: Use scripts/validate-skills.py and scripts/update-docs.py
- 🤝 Contributing: See CONTRIBUTING.md

Happy coding! 🚀
