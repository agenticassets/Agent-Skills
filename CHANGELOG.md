# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.2-custom] - 2026-02-01

### Changed
- **Customized from jeffallan/claude-skills template** for personal use focused on PhD research, finance, real estate, and AI/ML
- Reduced from 65 skills to 12 domain-focused skills:
  - **📚 PhD Academic Business Research**: pyfixest-latex, stata-accounting-research, pandas-pro
  - **💰 Financial Analysis & Services**: wrds-data-pull, pandas-pro
  - **🏢 Real Estate**: cre-investment-analysis
  - **🤖 AI/ML/AI Agents**: ml-pipeline, prompt-engineer, mcp-developer
  - **💻 Development & Technical Writing**: fastapi-expert, code-documenter, code-reviewer, debugging-wizard, n8n-skills
- Reorganized all documentation around domain-specific categories
- Updated SKILLS_GUIDE.md with domain-focused workflows and examples
- Simplified README.md with research/finance/real-estate focus
- Updated QUICKSTART.md with domain-relevant examples
- Updated ROADMAP.md with research and finance improvement plans

### Fixed
- Added missing `triggers` field to skill frontmatter (cre-investment-analysis, n8n-skills, pyfixest-latex, stata-accounting-research)
- Fixed skill frontmatter descriptions to follow "Use when" trigger-only format
- Added missing `role`, `scope`, and `output-format` fields
- Renamed stata-accounting-research-master directory to stata-accounting-research
- Removed empty claude-equity-research-main directory
- Created missing references/ directory for n8n-skills
- Updated version.json and ran documentation update scripts

### Added
- **CREDITS.md** - Attribution for community-contributed skills
- Source URLs in skill metadata (stata-accounting-research, n8n-skills)
- References to related skill collections (K-Dense-AI/claude-scientific-skills, quant-sentiment-ai/claude-equity-research)

### Stats
- **16 skills** (down from 65 in template, customized for PhD research/finance/real estate/AI)
- **85 reference files** (down from 356)
- **9 workflows** (unchanged)
- All skills passing validation (0 errors, 5 minor warnings)

### Attribution & Community Skills
- **stata-accounting-research** from [@jusi-aalto](https://github.com/jusi-aalto/stata-accounting-research)
- **n8n-skills** from [@haunchen](https://github.com/haunchen/n8n-skills)
- **matplotlib** + **scientific-visualization** from [K-Dense Inc.](https://github.com/K-Dense-AI/claude-scientific-skills)

---

## Original Template History

This repository was forked from [jeffallan/claude-skills](https://github.com/jeffallan/claude-skills) v0.4.2.

See the original repository for full version history prior to customization.

---

*Customized for personal use by Dr. Cayman Seagraves*
