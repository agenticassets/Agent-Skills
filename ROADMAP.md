# Agent Skills Roadmap

## Current Status

**Version:** v<!-- VERSION -->0.4.2<!-- /VERSION -->

- **<!-- SKILL_COUNT -->16<!-- /SKILL_COUNT --> Skills** across 5 domains
- **<!-- REFERENCE_COUNT -->85<!-- /REFERENCE_COUNT --> Reference Files** with progressive disclosure architecture
- **<!-- WORKFLOW_COUNT -->9<!-- /WORKFLOW_COUNT --> Project Workflow Commands**
- **50% Token Reduction** through selective disclosure architecture

This is a personal skill collection customized for Python development, data analysis, econometric research, and AI integration.

---

## Skills by Domain

### 📚 PhD Academic Business Research (3 skills)
- **pyfixest-latex** - PyFixest econometric models to publication-quality LaTeX
- **stata-accounting-research** - STATA code patterns from published accounting research
- **pandas-pro** - Data manipulation and analysis for research datasets

### 💰 Financial Analysis & Services (2 skills)
- **wrds-data-pull** - WRDS data extraction (Compustat, CRSP, IBES, etc.)
- **pandas-pro** - Financial data analysis, portfolio analytics

### 🏢 Real Estate (Residential/Commercial) (1 skill)
- **cre-investment-analysis** - Commercial real estate investment analysis and underwriting

### 🤖 AI/ML/AI Agents (3 skills)
- **ml-pipeline** - ML pipelines with MLflow/Kubeflow, experiment tracking
- **prompt-engineer** - LLM prompt design and optimization
- **mcp-developer** - Model Context Protocol servers/clients for AI integration

### 💻 Development & Technical Writing (5 skills)
- **fastapi-expert** - Async Python APIs with FastAPI, Pydantic V2
- **code-documenter** - Documentation (docstrings, API docs, OpenAPI)
- **code-reviewer** - Code reviews, quality audits, security checks
- **debugging-wizard** - Systematic debugging, error investigation
- **n8n-skills** - n8n workflow automation

---

## Planned Improvements

### Short-term (Next 1-3 months)

**Research & Academia**
- [ ] Add more PyFixest reference files (synthetic DiD, staggered adoption)
- [ ] Expand STATA patterns with more JAR papers
- [ ] Add Fama-French factor construction to wrds-data-pull
- [ ] Create research data validation skill

**Financial Analysis**
- [ ] Add more WRDS database templates (BoardEx, ISS, RavenPack)
- [ ] Create financial modeling skill (valuation, forecasting)
- [ ] Add portfolio optimization reference files

**Development**
- [ ] Add pytest-expert skill for testing
- [ ] Enhance FastAPI with more patterns (background tasks, WebSockets)
- [ ] Add database skills (sqlalchemy-pro, postgres-expert)

### Medium-term (3-6 months)

**Research & Academia**
- [ ] Add spatial econometrics skill
- [ ] Create research writing skill (academic papers, methodology)
- [ ] Build citation management and BibTeX integration

**Real Estate**
- [ ] Expand CRE skill with more property types
- [ ] Add residential real estate analysis
- [ ] Create real estate data analysis skill (CoreLogic, ZTRAX, CoStar)

**AI/ML**
- [ ] Add RAG (Retrieval-Augmented Generation) skill
- [ ] Create fine-tuning skill for LLMs
- [ ] Add time series forecasting skill

**Development**
- [ ] Add visualization skills (matplotlib-pro, plotly-expert, seaborn-expert)
- [ ] Create deployment skills (docker-expert, cloud-deployment)
- [ ] Add data pipeline orchestration (airflow-expert)

### Long-term (6-12 months)

**Research Workflows**
- [ ] Build custom workflow commands for research projects
- [ ] Create end-to-end research pipeline automation
- [ ] Add reproducibility and replication skills

**Integration & Automation**
- [ ] Create skill chains for common research workflows
- [ ] Build integration with LaTeX/Overleaf
- [ ] Add literature review and citation network analysis

**Expansion**
- [ ] Add frontend skills for research dashboards (react-expert, next-js-developer)
- [ ] Create presentation skills (beamer-latex, academic-presentations)
- [ ] Build teaching and pedagogy skills

---

## Contribution Ideas

### New Skills to Consider

**Research & Academia**
- **research-writing** - Academic paper structure, methodology writing, literature reviews
- **latex-expert** - LaTeX document preparation, beamer presentations, academic formatting
- **spatial-econometrics** - Spatial regression, GIS integration, geographic data
- **survey-analysis** - Survey design, Likert scales, psychometrics, SEM
- **bibliometrics** - Citation analysis, co-authorship networks, research impact

**Financial Analysis**
- **financial-modeling** - Valuation models, DCF, LBO, M&A analysis
- **portfolio-optimization** - Modern portfolio theory, factor models, risk parity
- **risk-management** - VaR, CVaR, stress testing, scenario analysis
- **derivatives-pricing** - Options, futures, exotic derivatives, Greeks

**Real Estate**
- **residential-real-estate** - SFR analysis, rental property evaluation, 1031 exchanges
- **real-estate-data** - CoreLogic, ZTRAX, CoStar data extraction and analysis
- **reit-analysis** - REIT valuation, FFO/AFFO, sector analysis

**AI/ML**
- **rag-architect** - Retrieval-Augmented Generation, vector databases, embeddings
- **fine-tuning-expert** - LLM fine-tuning, LoRA, PEFT, model optimization
- **time-series-forecasting** - ARIMA, Prophet, LSTM, state-space models

**Development**
- **pytest-expert** - Python testing, fixtures, mocking, coverage
- **sqlalchemy-pro** - SQLAlchemy ORM, async support, migrations
- **docker-expert** - Containerization, Docker Compose, multi-stage builds
- **matplotlib-pro** - Publication-quality figures, custom styles
- **plotly-expert** - Interactive visualizations, dashboards
- **jupyter-pro** - Jupyter notebooks, interactive analysis, widgets

### Skill Enhancements
- Add more FastAPI patterns (dependency injection, background tasks, testing)
- Expand pandas-pro with advanced techniques (window functions, custom aggregations)
- Add more econometric methods to pyfixest-latex
- Enhance MCP developer with more integration patterns
- Add prompt engineering evaluation frameworks

### Reference File Ideas
- FastAPI testing patterns
- pandas performance optimization
- MLflow best practices
- STATA advanced methods
- Real estate financial modeling templates
- n8n integration patterns

---

## Maintenance Tasks

### Regular Maintenance
- [ ] Update skill documentation as frameworks evolve
- [ ] Add new examples to reference files
- [ ] Validate all skills quarterly
- [ ] Update dependencies and compatibility notes
- [ ] Review and refine skill triggers

### Documentation
- [ ] Keep SKILLS_GUIDE.md up to date
- [ ] Document new workflows as they emerge
- [ ] Create troubleshooting guides
- [ ] Build example projects using skills
- [ ] Create video tutorials for complex skills

### Quality Assurance
- [ ] Run validation script before each update
- [ ] Test skills with real-world use cases
- [ ] Gather feedback and iterate
- [ ] Monitor Claude Code updates for compatibility
- [ ] Track skill usage patterns

---

## Version History

### v0.4.2 (Current)
- Customized from jeffallan/claude-skills template
- Reduced from 65 skills to 12 focused skills
- Updated documentation to reflect personal collection
- Fixed validation issues and standardized frontmatter
- Created domain-specific skill guide

### Future Versions
- **v0.5.0**: Add 3-5 new Python/data skills
- **v0.6.0**: Create custom workflow commands
- **v0.7.0**: Build skill composition framework
- **v1.0.0**: Stable release with comprehensive testing

---

## Contributing

This is a personal skill collection, but I welcome:
- Suggestions for new skills or improvements
- Example code and patterns
- Reference file contributions
- Bug reports and fixes
- Documentation improvements

To suggest changes:
1. Create an issue describing the enhancement
2. For code contributions, submit a pull request
3. Ensure all skills pass validation: `python scripts/validate-skills.py`
4. Update documentation as needed

---

## Acknowledgments

Originally forked from [jeffallan/claude-skills](https://github.com/jeffallan/claude-skills)

Built on the [Agent Skills](https://agentskills.io/specification) specification.

---

*Last updated: February 2026*
