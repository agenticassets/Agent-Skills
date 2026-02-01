# Econometric Analysis Integration

Guide for integrating econometric analysis with academic writing using specialized Claude Code skills.

## Table of Contents
- Available Skills
- Decision Tree
- Complete Workflows
- Quick Reference Commands
- Output Integration Standards
- Common Integration Mistakes
- Skill Interaction Patterns
- Method-Specific Recommendations

## Available Skills

### **Data: `wrds-data-pull`**

**Purpose**: WRDS data extraction and merging

**Use for**:
- Pulling Compustat, CRSP, IBES, BoardEx, etc. from WRDS
- Multi-dataset merging (CCM linking, CUSIP/PERMNO matching)
- Panel data validation
- Financial variable construction

**Not for**: Regression analysis (use pyfixest-latex or stata-accounting-research-master)

### **Python Analysis: `pyfixest-latex`** (Recommended for New Projects)

**Purpose**: PyFixest econometric models → publication-quality LaTeX/figures

**Use for**:
- Regression tables (standard, DiD, event study, robustness)
- Summary statistics tables
- Event study plots, treatment heatmaps, coefficient forest plots
- Fixed effects panel regressions
- LaTeX .tex file output for direct `\input{}` integration

**Output**: `Results/Tables/*.tex`, `Results/Figures/*.pdf`

### **Stata Analysis: `stata-accounting-research-master`**

**Purpose**: Stata code patterns from 126 peer-reviewed JAR papers

**Use for**:
- Replicating published papers using Stata
- Specific Stata procedures (entropy balancing, Fama-MacBeth)
- Working with coauthors who use Stata
- Methods requiring Stata (two-way clustering, bootstrap)

**Coverage**: DiD, RDD, IV, PSM, event studies, reghdfe, esttab formatting

## Decision Tree: Which Skills to Use?

```
Need econometric analysis for paper?
│
├─ Need data from WRDS?
│   YES → Use wrds-data-pull skill to extract and merge data
│   NO → Proceed with existing data
│
├─ Prefer Python or Stata for analysis?
│   │
│   ├─ Python (modern, recommended for new projects)
│   │   → Use pyfixest-latex skill
│   │   → Outputs: LaTeX tables (.tex) and figures (.pdf)
│   │
│   └─ Stata (existing code, replication, specific methods)
│       → Use stata-accounting-research-master skill
│       → Export tables with esttab
│
└─ Use academic-writing skill to write Results section
    → Loads: references/results-discussion.md, econometric-reporting.md
```

## Complete Workflows

### Workflow 1: Python (Recommended)

**Stage 1: Data Acquisition**
```
Use wrds-data-pull to pull Compustat + CRSP from 2010-2023,
merge using CCM linking, construct book-to-market and momentum variables.

Output: Final_Datasets/merged_data.parquet
```

**Stage 2: Analysis → Tables/Figures**
```
Use pyfixest-latex to create:
- Table 1: Summary statistics
- Table 2: Main regression with firm and year FE
- Figure 1: Event study plot

Output:
- Results/Tables/Table_01_summary_stats.tex
- Results/Tables/Table_02_main_regression.tex
- Results/Figures/Figure_01_event_study.pdf
```

**Stage 3: Write Results Section**
```
Use academic-writing skill: "Write Results section describing Table 2."

Loads: references/results-discussion.md, econometric-reporting.md
Output: Writing/sections/Results.tex with coefficient interpretation
```

**Stage 4: Integrate in LaTeX**
```latex
\section{Results}
\input{sections/Results.tex}

\input{../Results/Tables/Table_02_main_regression.tex}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.8\textwidth]{../Results/Figures/Figure_01_event_study.pdf}
\caption{Event Study Analysis}
\label{fig:event}
\end{figure}
```

### Workflow 2: Stata

**Stage 1: Data** (optional if already have .dta files)
```
Use wrds-data-pull to extract data → export df.to_stata("data.dta")
OR use existing Stata .dta files
```

**Stage 2: Analysis**
```
Use stata-accounting-research-master: "Show reghdfe code for DiD
with firm and year FE, clustered at firm level."

Output:
reghdfe outcome treatment##post controls, absorb(firm_id year) cluster(firm_id)
esttab using "Results/Tables/Table_02.tex", booktabs se star(* 0.10 ** 0.05 *** 0.01)
```

**Stage 3-4**: Same as Python workflow (write Results section, compile LaTeX)

### Workflow 3: Referee Response

**Scenario**: Reviewer requests robustness excluding financial crisis

**Python**:
```
1. Use pyfixest-latex: "Re-run Table 2 excluding 2008-2009, save as Table_A1.tex"
2. Use academic-writing: "Draft referee response for crisis robustness concern"
```

**Stata**:
```
1. Use stata-accounting-research-master: "Show code for dropping 2008-2009 and
   re-running regression with esttab output"
2. Use academic-writing: "Draft referee response for crisis robustness concern"
```

## Quick Reference Commands

### Data Acquisition (wrds-data-pull)
```
"Use wrds-data-pull to extract [Compustat/CRSP] from [years],
merge via CCM linking, construct [variables]."
```

### Python Analysis (pyfixest-latex)
```
"Use pyfixest-latex to create regression table:
DV=[outcome], IV=[treatment], controls=[X,Y,Z], FE=[firm,year], cluster=[firm]."

"Generate event study plot from t-5 to t+5 with 95% CI."

"Create summary statistics table for [variables] with mean, SD, min, max."
```

### Stata Analysis (stata-accounting-research-master)
```
"Use stata-accounting-research-master to show [DiD/IV/PSM] code
with [specification details]."

"Show esttab code for Table 2 with booktabs, labeled variables, significance stars."
```

### Writing (academic-writing)
```
"Use academic-writing to write Results section describing Table 2."

"Draft referee response to endogeneity concern."

"Check manuscript consistency before submission."
```

## Output Integration Standards

**Tables** (LaTeX .tex files):
- ✅ Professional formatting (booktabs: `\toprule`, `\midrule`, `\bottomrule`)
- ✅ Significance stars (*** p<0.01, ** p<0.05, * p<0.10)
- ✅ Standard errors in parentheses below coefficients
- ✅ Table notes explaining variables, fixed effects, clustering
- ✅ Cross-references work (`\label{tab:X}` in table, `\ref{tab:X}` in text)

**Figures** (PDF or PNG):
- ✅ Vector format (PDF preferred) or high-res PNG (300+ dpi)
- ✅ Clear axis labels and readable fonts
- ✅ Descriptive captions
- ✅ Grayscale-compatible if journal requires

**Results Text**:
- ✅ Explicit table/figure references ("Table 2, Column 3...")
- ✅ Coefficient interpretation with economic magnitude
- ✅ Statistical significance reported
- ✅ Hypothesis-result mapping

## Common Integration Mistakes

### ❌ Mistake 1: Copy-Pasting Console Output
**Problem**: Copying regression output from Python/Stata console into LaTeX

**✅ Fix**: Always export formatted LaTeX tables
```python
# Python (pyfixest-latex handles this automatically)
# Just invoke: "Use pyfixest-latex to create Table 2"

# Stata
esttab using "Results/Tables/table1.tex", booktabs label
```

### ❌ Mistake 2: Wrong Skill for Task
**Problem**: Using wrds-data-pull for regression analysis

**✅ Fix**: Use correct skill for each stage
- **Data**: wrds-data-pull
- **Analysis/Tables**: pyfixest-latex (Python) OR stata-accounting-research-master (Stata)
- **Writing**: academic-writing

### ❌ Mistake 3: Inconsistent Variable Names
**Problem**: Variable `ai_adopt` in code, "AI Adoption" in Table 1, "AI dummy" in Table 2

**✅ Fix**: Use consistent labels
```python
# pyfixest-latex uses clean variable names in output automatically

# Stata
label variable ai_adopt "AI Adoption"
```

### ❌ Mistake 4: Hard-Coded Coefficients in Text
**Problem**: Text says "12%" but table shows 11.8%

**✅ Fix**: Check table before writing, round consistently

## Skill Interaction Patterns

### Pattern 1: Data → Python Analysis → Writing (Recommended)
```
1. wrds-data-pull: Extract and merge WRDS data
2. pyfixest-latex: Generate tables/figures with PyFixest
3. academic-writing: Write Results section
```

### Pattern 2: Data → Stata Analysis → Writing
```
1. wrds-data-pull: Extract data → export to .dta
2. stata-accounting-research-master: Generate tables with reghdfe/esttab
3. academic-writing: Write Results section
```

### Pattern 3: Python + Stata Validation
```
1. wrds-data-pull: Extract data
2. pyfixest-latex: Main analysis (Python)
3. stata-accounting-research-master: Replicate key table (Stata)
4. Verify results match → mention in robustness
5. academic-writing: Write manuscript
```

### Pattern 4: Iterative Writing + Analysis
```
Loop:
1. academic-writing: Draft hypothesis
2. pyfixest-latex OR stata-accounting-research-master: Test hypothesis
3. academic-writing: Write Results interpreting findings
4. Repeat for H2, H3, etc.
```

## Method-Specific Recommendations

**Standard panel regressions**: Either skill works
- Python: `pyfixest-latex` with `.feols()`
- Stata: `stata-accounting-research-master` with `reghdfe`

**DiD/Event studies**: Prefer Python
- Python: `pyfixest-latex` with event study plots, staggered DiD

**Complex variance structures**: Consider Stata
- Stata: Two-way clustering, Fama-MacBeth, Newey-West

**Matching/Balancing**: Use Stata
- Stata: Entropy balancing, PSM from JAR replication files

**Publication-quality figures**: Use Python
- Python: `pyfixest-latex` for event studies, treatment heatmaps, forest plots

## Dependencies

**wrds-data-pull**:
```bash
pip install pandas numpy wrds sqlalchemy
```

**pyfixest-latex**:
```bash
pip install pyfixest pandas numpy scipy matplotlib
```

**stata-accounting-research-master**:
```stata
ssc install reghdfe
ssc install estout
ssc install winsor2
```

**academic-writing** (this skill):
```bash
pip install bibtexparser pyalex requests  # For citation scripts only
```

## Complete Example: New Paper

```
Step 1: Data
"Use wrds-data-pull to pull Compustat + CRSP from 2015-2023,
merge using CCM, construct ROA, leverage, market-to-book."
→ Output: Final_Datasets/merged_data.parquet

Step 2: Analysis
"Use pyfixest-latex to create:
- Table 1: Summary statistics for all variables
- Table 2: ROA regressed on leverage with firm + year FE
- Figure 1: Event study plot for M&A announcements"
→ Outputs: Results/Tables/*.tex, Results/Figures/*.pdf

Step 3: Introduction
"Use academic-writing to write Introduction for paper on
leverage and profitability."
→ Loads: references/introduction-patterns.md
→ Output: Writing/sections/Introduction.tex

Step 4: Hypotheses
"Use academic-writing to write hypothesis section predicting
leverage negatively affects ROA."
→ Loads: references/hypothesis-development.md
→ Output: Writing/sections/Hypotheses.tex

Step 5: Results
"Use academic-writing to write Results describing Table 2.
Coefficient on leverage is -0.045 (p<0.01)."
→ Loads: references/results-discussion.md, econometric-reporting.md
→ Output: Writing/sections/Results.tex

Step 6: Compile
./Writing/compile_latex.sh
```

## Further Reading

**Skills documentation**:
- Load `pyfixest-latex` SKILL.md for PyFixest table/figure options
- Load `stata-accounting-research-master` SKILL.md for Stata method catalog
- Load `wrds-data-pull` SKILL.md for WRDS database coverage

**Academic writing**:
- Load `references/econometric-reporting.md` for coefficient interpretation
- Load `references/results-discussion.md` for table walkthrough patterns
- Load `references/common-mistakes.md` for integration pitfalls
