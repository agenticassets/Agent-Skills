---
name: academic-writing
description: Use when creating or revising academic paper sections, formatting tables/figures for journal submission, writing referee responses, or adapting papers to journal-specific requirements in finance, economics, and real estate research.
triggers:
  - academic writing
  - research paper
  - LaTeX manuscript
  - journal submission
  - referee response
  - literature review
  - hypothesis development
  - methodology section
  - results section
  - discussion section
  - JF
  - JFE
  - RFS
  - JFQA
  - Real Estate Economics
  - JREFE
role: specialist
scope: implementation
output-format: document
---

# Academic Writing Skill

Professional LaTeX manuscript drafting and revision for academic research in finance, economics, and real estate. Transforms template structures into publication-ready manuscripts with proper academic writing conventions.

## Quick Start

### Write a paper section
```latex
% Request: "Write the Results section describing Table 1 (summary statistics)"
% Fills out Writing/sections/Results.tex template with research-specific content
```

### Respond to referee comments
```latex
% Request: "Draft a response to Reviewer 2's endogeneity concern"
% Uses referee-responses.md patterns for point-by-point response
```

### Check internal consistency
```python
# Request: "Check if all tables mentioned in text exist and numbers match"
python scripts/check_consistency.py Writing/Main.tex
```

## Core Workflows

### Workflow 1: Section-by-Section Writing

**When to use**: Writing a new paper or major revision

**Process**:
1. **Identify section type** - Introduction, Methodology, Results, etc.
2. **Load section guidance** - See `references/paper-structure.md` for templates
3. **Fill template with research content** - Replace `[PLACEHOLDER]` text
4. **Apply writing conventions** - See `references/writing-conventions.md`
5. **Verify cross-references** - Tables/figures mentioned exist

**Example sections**:
- **Introduction**: See `references/introduction-patterns.md` for 3-paragraph framing
- **Results**: See `references/results-discussion.md` for table walkthrough structure
- **Hypothesis Development**: See `references/hypothesis-development.md` for theory→prediction flow

### Workflow 2: Referee Response Preparation

**When to use**: R&R (revise and resubmit) stage

**Process**:
1. **Categorize concerns** - Endogeneity, sample selection, alternative explanations, etc.
2. **Load response frameworks** - See `references/referee-responses.md`
3. **Draft point-by-point response** - Concern → Response → Changes → Location
4. **Use response template** - `assets/templates/referee_response.tex`
5. **Track changes in manuscript** - `assets/templates/revision_diff.tex` for highlighting

**Common referee objections covered**:
- Endogeneity concerns (IV arguments, bounds, natural experiments)
- Sample selection bias (robustness with alternative samples)
- Alternative explanations (mechanism tests, placebo designs)
- Generalizability (cross-sectional heterogeneity tests)

### Workflow 3: Journal-Specific Formatting

**When to use**: Preparing submission or resubmission

**Process**:
1. **Identify target journal** - JF, JFE, RFS, Real Estate Economics, etc.
2. **Load journal requirements** - See `references/journal-formats.md`
3. **Adjust formatting** - Bibliography style, table format, section numbering
4. **Verify compliance** - Citation format, word limits, figure requirements

## Reference Files (Load as Needed)

### Writing Guidance
- **`references/paper-structure.md`** - Section-by-section templates with annotated examples
- **`references/introduction-patterns.md`** - Framing patterns (motivation → gap → contribution)
- **`references/hypothesis-development.md`** - Theory to testable prediction scaffolding
- **`references/results-discussion.md`** - Table walkthrough patterns, magnitude interpretation
- **`references/writing-conventions.md`** - Academic tone, active vs passive voice, hedging

### Revision Support
- **`references/referee-responses.md`** - Common objections, response frameworks, tone guidance
- **`references/common-mistakes.md`** - Frequent writing issues (vague contributions, weak hypotheses, poor table discussion)

### Journal Formatting
- **`references/journal-formats.md`** - JF, JFE, RFS, Real Estate Economics, JFQA formatting requirements

### Econometric Reporting
- **`references/econometric-reporting.md`** - Coefficient interpretation, significance reporting, fixed effects notation

### Econometric Analysis Integration
- **`references/econometric-analysis-integration.md`** - Integrating data (wrds-data-pull) and analysis (pyfixest-latex or stata-accounting-research-master) with manuscript writing

**When to use**: Need to run econometric analysis before/during writing Results section, generate regression tables/figures, or address referee requests for additional tests

**Covers**:
- Three-skill workflow: Data (wrds-data-pull) → Analysis (pyfixest-latex or stata-accounting-research-master) → Writing (academic-writing)
- Decision tree: Python vs Stata for analysis
- Complete workflows: Data extraction → Tables/Figures → LaTeX manuscript integration
- Output formatting for journal submission

## Scripts

### `scripts/01-check_citations.py`
Citation key validator - verifies all `\cite{}` commands have corresponding bibliography entries

**Usage**:
```bash
python scripts/01-check_citations.py  # Configure LATEX_FILE path in script
```

**Features**:
- Extracts all citation keys from LaTeX document
- Compares against bibliography file entries
- Reports missing citations (will show as "?" in PDF)
- Moves unused bibliography entries to `unused-references.bib`
- Generates citation check report

**Configuration**: Edit lines 36-48 to set LATEX_FILE path, output options, and behavior flags

### `scripts/02-bibtex_validator.py`
Advanced BibTeX validation using OpenAlex API

**Usage**:
```bash
python scripts/02-bibtex_validator.py  # Configure paths in script
```

**Features**:
- Validates citations against OpenAlex database
- Checks titles, authors, years, DOIs for accuracy
- Suggests corrections for incomplete or incorrect entries
- Extracts citations from main document to prioritize used references
- Optional AI assistance via OpenRouter for ambiguous cases
- Generates corrected .bib file with suggestions applied

**Configuration**: Edit lines 36-73 to set BIB_FILE_PATH, MAIN_DOC_PATH, API keys, and validation thresholds

**Requirements**: `pip install bibtexparser pyalex requests`

### `scripts/latex_section_word_counter.py`
Section-by-section word counter for LaTeX documents

**Usage**:
```bash
python scripts/latex_section_word_counter.py  # Configure file_path in script
```

**Features**:
- Counts words in each `\section{}` of LaTeX document
- Cleans LaTeX markup (citations, commands, math environments)
- Extracts section titles and labels
- Generates summary statistics (total words, average per section)
- Useful for tracking section length during writing

**Configuration**: Edit line 256 to set target .tex file path

### `scripts/check_consistency.py`
Internal consistency validator for cross-references, notation, and hypothesis mapping

**Usage**:
```bash
python scripts/check_consistency.py Writing/Main.tex [--check-citations]
```

**Checks**:
- All `\ref{tab:X}` references point to existing `\label{tab:X}` definitions
- Tables mentioned in text match Results/Tables/ files
- Hypothesis numbering (H1, H2, H3) consistent throughout
- Variable notation consistent (Y_{it} vs Y_it)
- Optional citation check wrapper (calls 01-check_citations.py)

## Templates (`assets/templates/`)

Complete LaTeX manuscript templates with extensive placeholder guidance for new research projects.

### LaTeX Document Templates

- **`assets/templates/Main.tex`** - Full LaTeX preamble and document structure
  - Professional academic formatting (JF, JFE, Real Estate Economics standards)
  - Complete package setup: natbib, booktabs, hyperref, geometry
  - Bibliography integration with JFE/JF style files
  - Ready to compile with `pdflatex → bibtex → pdflatex × 2`

- **`assets/templates/Results.tex`** - Results section with table formatting templates
  - 4 example table types: Summary Statistics, Main Results, Interaction Models, Robustness
  - Progressive specification patterns (baseline → controls → full model)
  - Extensive guidance comments for table captions and notes
  - `\input{}` commands for dynamic table integration from Results/Tables/

- **`assets/templates/Figures.tex`** - Figure formatting and layout examples
  - Multi-panel figures, landscape/portrait orientation
  - Caption formatting for academic journals
  - Figure cross-reference patterns

- **`assets/templates/Appendix.tex`** - Online appendix structure
  - Variable definition tables
  - Supplementary tables and robustness checks
  - Appendix numbering (A.1, A.2, A.3)

- **`assets/templates/Internet_Results.tex`** - Internet appendix tables
  - Extended robustness checks
  - Additional mechanism tests
  - Supplementary analysis

- **`assets/templates/Data_Documentation.tex`** - Data sources and methodology documentation
  - Standalone or integrated into main document
  - Data source descriptions with placeholders
  - Variable construction methodology
  - Sample restrictions and filters

### Specialized Response Templates

- **`assets/templates/referee_response.tex`** - Point-by-point referee response letter
  - Structured format: Comment → Response → Changes Made → Location
  - Professional tone guidance built into template
  - Summary of major revisions section

**Usage**: Copy `assets/templates/` files to your project, replace `[PLACEHOLDER]` content with research-specific details, preserve LaTeX structure.

### BibTeX Styles (`assets/bibtex/`)
- **`assets/bibtex/jfe.bst`** - Journal of Financial Economics style
- **`assets/bibtex/jf.bst`** - Journal of Finance style
- **`assets/bibtex/qje.bst`** - Quarterly Journal of Economics style

## Writing Decision Trees

### When writing Introduction
1. **Paragraph 1** - Motivation (why does this question matter?)
2. **Paragraph 2** - Gap (what don't we know? why is it hard?)
3. **Paragraph 3** - This paper (what we do, what we find, contribution)
4. **Paragraph 4** - Roadmap (section preview)

See `references/introduction-patterns.md` for annotated examples.

### When writing Results
1. **Descriptive statistics** - Table 1 walkthrough, sample characteristics
2. **Main results** - Table 2, hypothesis testing, coefficient interpretation
3. **Economic magnitude** - What does a 1 SD increase mean in real terms?
4. **Robustness** - Alternative specifications, sample restrictions
5. **Mechanisms** - Why does the effect occur?
6. **Heterogeneity** - For whom is the effect stronger/weaker?

See `references/results-discussion.md` for table-by-table walkthrough patterns.

### When responding to referee
1. **Acknowledge concern** - "The reviewer raises an important point about..."
2. **Explain response** - "To address this, we..."
3. **Describe changes** - "We have added Table X showing..."
4. **Reference location** - "See revised Section Y, page Z"

See `references/referee-responses.md` for tone guidance and response frameworks.

## Integration with Existing Templates

This skill works with existing LaTeX templates in Writing/sections/:

- **Results.tex** - Contains table wrapper templates with placeholder guidance
- **Figures.tex** - Figure layout examples (multi-panel, landscape, portrait)
- **Appendix.tex** - Variable definition table templates
- **Internet_Results.tex** - Appendix table numbering (A.1, A.2, A.3)

**Your role**: Fill these templates with research-specific content while preserving LaTeX structure.

## Standalone Requirements

- LaTeX distribution (TeX Live 2023+, MacTeX, MiKTeX)
- Python 3.8+ for consistency checking scripts
- BibTeX for bibliography management
- No project-specific dependencies - works in any LaTeX research project

## Example Usage

**Example 1: Write Results section for Table 2**
```
User: "I just generated Table 2 (main regression results). Write the Results section text describing these findings."

Response process:
1. Read Results/Tables/Table_02_main_results.tex to understand table structure
2. Load references/results-discussion.md for table walkthrough patterns
3. Fill Writing/sections/Results.tex template for Table 2 section
4. Include: coefficient interpretation, economic magnitude, hypothesis testing, significance levels
5. Ensure cross-reference \ref{tab:main_results} matches \label in table
```

**Example 2: Respond to endogeneity concern**
```
User: "Reviewer 2 says treatment is endogenous. How do I respond?"

Response process:
1. Load references/referee-responses.md for endogeneity response frameworks
2. Identify available responses: IV, natural experiment, bounds, robustness
3. Draft point-by-point response using assets/templates/referee_response.tex
4. Suggest additional analyses if needed (placebo tests, event studies)
```

**Example 3: Check paper consistency**
```
User: "Check if my paper has consistency issues before submission"

Response process:
1. Run scripts/check_consistency.py on Writing/Main.tex
2. Report: missing cross-references, table/figure numbering gaps, notation inconsistencies
3. Verify hypothesis-result mapping (H1 tested in Table 2, H2 in Table 3, etc.)
4. Check citation completeness via Tests/check_citations.py wrapper
```

**Example 4: Integrate econometric analysis with writing**
```
User: "I need to run regressions and write my Results section. I have WRDS access."

Response process:
1. Load references/econometric-analysis-integration.md for workflow guidance
2. Recommend three-skill workflow:
   a. "Use wrds-data-pull to pull and merge Compustat + CRSP data"
   b. "Use pyfixest-latex to generate Tables 1-3 with PyFixest → LaTeX output"
   c. "Use academic-writing to write Results section"
3. After tables generated: Load references/results-discussion.md for writing patterns
4. Write Results section with proper coefficient interpretation and economic magnitudes
5. Integrate tables with \input{../Results/Tables/Table_02.tex} commands
```

## Tips for Effective Use

1. **Load references selectively** - Only read the specific .md file needed (e.g., `introduction-patterns.md` when writing introduction)
2. **Preserve LaTeX structure** - Never break booktabs formatting, caption structure, or cross-reference patterns
3. **One sentence per line** - Critical for version control and git diffs
4. **Economic interpretation** - Always translate coefficients to real-world magnitude
5. **Active voice preference** - "We find..." over "It is found..." in academic finance/economics
6. **Hypothesis-result mapping** - Explicitly connect each hypothesis to the table/column testing it

## Progressive Disclosure

This skill uses progressive loading:

1. **SKILL.md** (this file) - Core workflows and file navigation
2. **Reference files** - Load specific .md files as needed for detailed guidance
3. **Templates** - Copy LaTeX/BibTeX templates when creating new documents
4. **Scripts** - Execute consistency checks without loading into context

Load reference files only when actively working on that specific section or task.
