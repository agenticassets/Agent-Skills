---
name: pyfixest-latex
description: Use when generating publication-quality LaTeX tables and figures from PyFixest econometric models, including regression tables, event study plots, and summary statistics for academic research papers.
triggers:
  - PyFixest
  - LaTeX tables
  - econometric
  - regression table
  - event study
  - DiD
  - difference-in-differences
  - fixed effects
  - panel regression
  - research paper
  - academic publication
role: specialist
scope: implementation
output-format: code
---

# PyFixest LaTeX Generator

7 functions for converting PyFixest models to publication-quality LaTeX tables and figures.

**Tables** (4): regression, dynamic/event study, robustness (grouped), summary statistics
**Figures** (3): event study plot, treatment assignment heatmap, coefficient comparison

## Setup

### Option A: Run setup script
```bash
python <skill-path>/scripts/setup_module.py /path/to/project
```

### Option B: Manual copy
1. Copy `assets/pyfixest_latex/` to your project root
2. Install dependencies: `pip install pyfixest pandas numpy scipy matplotlib`
3. Create output dirs: `output/tables/` and `output/figures/`

### Configure paths (required before generating output)
```python
from pyfixest_latex import set_output_path, set_figure_output_path
set_output_path("Results/Tables")           # or any absolute/relative path
set_figure_output_path("Results/Figures")   # or any absolute/relative path
```

## Core Workflow

```python
import pyfixest as pf
from pyfixest_latex import (
    set_output_path, set_figure_output_path,
    create_regression_table, create_event_study_plot,
    create_summary_statistics_table
)

# 1. Configure output paths
set_output_path("Results/Tables")
set_figure_output_path("Results/Figures")

# 2. Fit models
m1 = pf.feols("Y ~ treat | unit + year", data, vcov={"CRV1": "unit"})
m2 = pf.feols("Y ~ treat + X1 | unit + year", data, vcov={"CRV1": "unit"})

# 3. Generate table
create_regression_table(
    models=[m1, m2],
    model_names=["Basic", "Controls"],
    title="Treatment Effects",
    label="tab:main",
    variable_labels={"treat": "Treatment Effect", "X1": "Control Variable"},
    depvar_labels={"Y": "Outcome Variable"},
    felabels={"unit": "Unit FE", "year": "Year FE"}
)
# → Saves: Results/Tables/main_regression.tex
```

## Function Quick Reference

### Tables

| Function | Purpose | Key Params |
|----------|---------|------------|
| `create_regression_table()` | Multi-model comparison | models, model_names, title, label |
| `create_dynamic_table()` | Event study coefficients | models, time_var, treat_var, reference_period, treatment_period |
| `create_robustness_table()` | Grouped specifications | model_groups, group_names |
| `create_summary_statistics_table()` | Descriptive stats | data (DataFrame), variables, variable_labels |

### Figures

| Function | Purpose | Key Params |
|----------|---------|------------|
| `create_event_study_plot()` | Dynamic effects plot | model, style (errorbar/filled/step), confidence_level |
| `create_treatment_assignment_plot()` | Treatment timing heatmap | data, unit, time, treat |
| `create_coefficient_comparison_plot()` | Forest plot across specs | models, model_names, use_ci |

### Utilities

| Function | Purpose |
|----------|---------|
| `set_output_path(path)` | Configure table output directory |
| `set_figure_output_path(path)` | Configure figure output directory |
| `list_saved_tables()` | List generated .tex files |
| `list_saved_figures()` | List generated .png/.pdf files |

Full API: See `references/tables-api.md` and `references/figures-api.md`

## Example Templates & Assets

**Complete DiD Analysis Template** (849 lines):
- `assets/example_did_analysis_template.py` - Production-ready DiD analysis with DidConfig class
- Quick start: Copy, customize 7 settings in DidConfig, run
- See [references/did-template-quick-reference.md](references/did-template-quick-reference.md) for 30-second setup
- See [references/did-template-guide.md](references/did-template-guide.md) for comprehensive documentation

**Modular Function Examples**:
- `assets/1---example_summary_statistics.py` - Standalone summary stats demonstration
- `assets/2---example_figure_usage.py` - Standalone figure generation examples
- `assets/3---example_enhanced_table_generator.py` - Standalone table generation examples
- `assets/4---run_all_examples.py` - Orchestrator to run all modular examples

**Which to use?**
- **DiD template**: Copy for complete analysis workflow (data → tables → figures)
- **Modular examples**: Learn individual functions in isolation, mix-and-match

## Reference Documentation

Use these guides to learn specific patterns and troubleshoot issues:

**Starting Out?**
- Read [workflow-patterns.md](references/workflow-patterns.md) for complete analysis structure, UTF-8 setup, and best practices

**Preparing Data?**
- Read [data-requirements.md](references/data-requirements.md) for DataFrame structure, panel data setup, and validation

**Need Usage Examples?**
- Read [common-patterns.md](references/common-patterns.md) for 10 complete patterns (DiD, event studies, robustness checks, multiple outcomes)

**DiD Template Documentation?**
- Read [did-template-quick-reference.md](references/did-template-quick-reference.md) for 30-second DiD setup
- Read [did-template-guide.md](references/did-template-guide.md) for comprehensive DiD guide

**Customizing Functions?**
- Read [tables-api.md](references/tables-api.md) for all table function parameters
- Read [figures-api.md](references/figures-api.md) for plot customization (colors, styles, CI levels)

**Troubleshooting?**
- Read [troubleshooting.md](references/troubleshooting.md) for common issues and solutions

**Using Statsmodels Instead of PyFixest?**
- Read [stargazer-alternative.md](references/stargazer-alternative.md)

## Critical Rules

1. **Set output paths BEFORE calling any generation function** — paths are resolved at call time
2. **Use `type="tex"` in PyFixest** — the module calls `pf.etable(..., type="tex")` internally
3. **Pass `treatment_period`** to `create_dynamic_table()` and `create_event_study_plot()` for correct relative-time labels ($t_{-2}$, $t_0$, $t_{+1}$)
4. **Unit FE before Time FE** — automatic reordering in all tables (recognizes 25+ FE naming patterns)
5. **CI distribution** — t-distribution for n<30, normal for n>=30 (proper small-sample inference)
6. **Figure backend** — uses matplotlib 'Agg' (non-interactive); no GUI required
7. **Windows** — UTF-8 encoding handled automatically in figure generator
8. **Filenames** — auto-generated from `label` parameter: `{label}_regression.tex`, `{label}_dynamic.tex`, etc.

## LaTeX Integration

### Required packages in preamble
```latex
\usepackage{booktabs}
\usepackage{threeparttable}
\usepackage{graphicx}
\usepackage{makecell}    % for multi-line cells with \makecell
```

### Include generated outputs
```latex
% Tables
\input{Results/Tables/main_regression.tex}
\input{Results/Tables/event_study_dynamic.tex}

% Figures
\begin{figure}[ht!]
\centering
\includegraphics[width=0.9\textwidth]{Results/Figures/event_study.png}
\caption{Event Study: Treatment Effects Over Time}
\label{fig:event_study}
\end{figure}
```

### Table output structure
All tables use this LaTeX structure:
```latex
\begin{table}[ht!]
\centering
\caption{\\Title}
\parbox{\linewidth}{\footnotesize Notes text here}
\label{tab:label}
\footnotesize
\begin{threeparttable}
\begin{tabular}{lccc}
...
\end{tabular}
\end{threeparttable}
\end{table}
```

