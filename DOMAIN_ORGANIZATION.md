# Agent Skills - Domain Organization

This repository contains 12 specialized Claude Code skills organized around five professional domains:

## 📚 PhD Academic Business Research (3 skills)

**Primary Focus**: Econometric analysis, publication-ready output, research data manipulation

1. **pyfixest-latex** - Generate publication-quality LaTeX tables and figures from PyFixest models
   - DiD, event studies, panel regression
   - Regression tables, summary statistics
   - Publication-ready plots

2. **stata-accounting-research** - STATA code patterns from 126+ published JAR papers
   - Entropy balancing, PSM, DiD, RDD, IV
   - Event studies (CAR/BHAR), survival analysis
   - Fama-MacBeth, fixed effects, clustering

3. **pandas-pro** - Data manipulation and analysis for research datasets
   - Data cleaning, transformation, aggregation
   - Time series analysis
   - Panel data preparation

**Common Workflow**: wrds-data-pull → pandas-pro → pyfixest-latex/stata-accounting-research → code-documenter

---

## 💰 Financial Analysis & Services (2 skills)

**Primary Focus**: Financial data extraction, portfolio analytics, market analysis

1. **wrds-data-pull** - Automated WRDS data extraction
   - Compustat, CRSP, IBES, Thomson Reuters
   - BoardEx, ISS, CoreLogic, ZTRAX, CoStar
   - CUSIP/GVKEY/PERMNO linking via CCM, ICLINK
   - Financial variable construction

2. **pandas-pro** - Financial data analysis
   - Portfolio analytics, return calculations
   - Risk metrics, performance attribution
   - Event study analysis

**Common Workflow**: wrds-data-pull → pandas-pro → code-documenter → code-reviewer

---

## 🏢 Real Estate (Residential/Commercial) (1 skill)

**Primary Focus**: Investment analysis, underwriting, business planning

1. **cre-investment-analysis** - Commercial real estate investment analysis
   - Property types: multifamily, office, retail, industrial, mixed-use
   - DCF/IRR analysis, NPV, cash-on-cash returns
   - Market feasibility studies, investment memos
   - Institutional-grade underwriting

**Common Workflow**: pandas-pro → cre-investment-analysis → code-documenter

---

## 🤖 AI/ML/AI Agents (3 skills)

**Primary Focus**: Machine learning pipelines, LLM integration, AI tooling

1. **ml-pipeline** - ML pipeline development and orchestration
   - MLflow, Kubeflow integration
   - Experiment tracking, feature stores
   - Model lifecycle management
   - Hyperparameter tuning

2. **prompt-engineer** - LLM prompt design and optimization
   - Chain-of-thought, few-shot learning
   - Structured outputs, prompt evaluation
   - Systematic prompt design

3. **mcp-developer** - Model Context Protocol server/client development
   - AI tool integration
   - Resource providers, tool functions
   - TypeScript/Python SDKs

**Common Workflow**: pandas-pro → ml-pipeline → prompt-engineer → mcp-developer → code-documenter

---

## 💻 Development & Technical Writing (5 skills)

**Primary Focus**: API development, code quality, documentation, automation

1. **fastapi-expert** - Async Python API development
   - FastAPI with Pydantic V2
   - Async SQLAlchemy, JWT authentication
   - OpenAPI documentation, WebSockets

2. **code-documenter** - Documentation creation
   - Docstrings, API documentation
   - OpenAPI/Swagger specs
   - Documentation sites, user guides

3. **code-reviewer** - Code quality and security
   - PR reviews, security audits
   - Refactoring suggestions
   - Best practices enforcement

4. **debugging-wizard** - Systematic debugging
   - Error investigation, stack trace analysis
   - Root cause analysis
   - Scientific debugging methodology

5. **n8n-skills** - Workflow automation
   - n8n node configuration
   - Trigger setup, data transformation
   - Workflow patterns, AI integration

**Common Workflow**: fastapi-expert → debugging-wizard → code-documenter → code-reviewer

---

## Cross-Domain Workflows

### Research Data Pipeline
```
wrds-data-pull → pandas-pro → pyfixest-latex → code-documenter → code-reviewer
```

### Financial Analysis Platform
```
wrds-data-pull → pandas-pro → fastapi-expert → code-documenter → code-reviewer
```

### AI-Powered Research Tool
```
wrds-data-pull → pandas-pro → ml-pipeline → mcp-developer → prompt-engineer → code-documenter
```

### Real Estate + Financial Analysis
```
wrds-data-pull → pandas-pro → cre-investment-analysis → code-documenter
```

---

## Recommended Complementary Skills

### Official Anthropic Document Skills

**Essential for research and real estate workflows:**

- **[pdf](https://github.com/anthropics/skills/tree/main/skills/pdf)** - Extract text/tables from PDFs, OCR scanned documents
  - Use for: Offering memos, appraisals, research papers, reports

- **[xlsx](https://github.com/anthropics/skills/tree/main/skills/xlsx)** - Read/write Excel spreadsheets, create financial models
  - Use for: Rent rolls, operating statements, financial models
  - Critical for CRE: Creates professional models with formulas and formatting

- **[docx](https://github.com/anthropics/skills/tree/main/skills/docx)** - Process Word documents, create reports
  - Use for: Investment memos, business plans, market reports

- **[pptx](https://github.com/anthropics/skills/tree/main/skills/pptx)** - Create/analyze PowerPoint presentations
  - Use for: Investment committee presentations, board decks

**Installation**: Built-in to Claude.ai, available at `/mnt/skills/public/` in Claude Code

**Example Integration**:
```
pdf (extract offering memo) → pandas-pro (analyze) →
cre-investment-analysis (model) → xlsx (create Excel) →
pptx (presentation)
```

### Discover More

Browse hundreds of skills at **[skills.sh](https://skills.sh/)**

---

## Skill Statistics

- **Total Skills**: 12
- **Reference Files**: 52
- **Workflows**: 9
- **Version**: 0.4.2-custom
- **Recommended Additions**: 4 official document skills (pdf, xlsx, docx, pptx)

---

## Future Expansion Plans

### Research & Academia
- Spatial econometrics, research writing, LaTeX expert
- Survey analysis, bibliometrics

### Financial Analysis
- Financial modeling, portfolio optimization
- Risk management, derivatives pricing

### Real Estate
- Residential real estate, real estate data analysis
- REIT analysis

### AI/ML
- RAG architect, fine-tuning expert
- Time series forecasting

### Development
- Testing (pytest-expert), database (sqlalchemy-pro)
- Visualization (matplotlib-pro, plotly-expert)
- Deployment (docker-expert)

---

**Last Updated**: February 2026
**Repository**: [Agent-Skills](https://github.com/cas3526/Agent-Skills)
**Based on**: [jeffallan/claude-skills](https://github.com/jeffallan/claude-skills)
