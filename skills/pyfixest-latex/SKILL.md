---
name: pyfixest-latex
description: |
  Generate publication-quality LaTeX tables and figures from PyFixest econometric models for academic research papers. Use when the user needs to: (1) Create regression tables (standard, dynamic/event study, robustness with grouped columns) from pyfixest.feols() models, (2) Generate summary statistics tables from pandas DataFrames, (3) Create event study plots with confidence intervals, treatment assignment heatmaps, or coefficient comparison forest plots, (4) Export LaTeX .tex files or publication-quality PNG figures for academic manuscripts. Covers DiD, staggered adoption, panel regression, and general fixed-effects econometric workflows. Standalone module — works in any project with pyfixest, pandas, numpy, scipy, matplotlib installed.
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

## Common Patterns

### Pattern 1: Standard DiD Regression Table

```python
models = [
    pf.feols("Y ~ treat | unit + year", df, vcov={"CRV1": "unit"}),
    pf.feols("Y ~ treat + X1 + X2 | unit + year", df, vcov={"CRV1": "unit"}),
    pf.feols("Y ~ treat + X1 + X2 + X3 | unit + year", df, vcov={"CRV1": "unit"}),
]

create_regression_table(
    models=models,
    model_names=["No Controls", "Base Controls", "Full Controls"],
    title="Difference-in-Differences Results",
    label="tab:did_main",
    variable_labels={"treat": "Treatment $\\times$ Post"},
    depvar_labels={"Y": "Outcome"},
    felabels={"unit": "Unit FE", "year": "Year FE"}
)
```

### Pattern 2: Event Study Plot + Table

```python
# Fit dynamic model
dynamic = pf.feols(
    "Y ~ i(year, ever_treated, ref=14) | unit + year",
    df, vcov={"CRV1": "unit"}
)

# Plot
create_event_study_plot(
    model=dynamic,
    title="Treatment Effects Over Time",
    time_var="year", treat_var="ever_treated",
    reference_period=14, treatment_period=15,
    style="filled", confidence_level=0.05
)

# Table
create_dynamic_table(
    models=dynamic,
    title="Dynamic Treatment Effects",
    label="tab:event_study",
    time_var="year", treat_var="ever_treated",
    reference_period=14, treatment_period=15,
    felabels={"unit": "Unit FE", "year": "Year FE"}
)
```

### Pattern 3: Summary Statistics

```python
create_summary_statistics_table(
    data=df,
    variables=["Y", "treat", "X1", "X2", "X3"],
    variable_labels={
        "Y": "Outcome Variable",
        "treat": "Treatment Indicator",
        "X1": "Log(Assets)",
        "X2": "Leverage",
        "X3": "Market Cap"
    },
    title="Descriptive Statistics",
    label="tab:summary",
    digits=3,
    percentiles=[0.25, 0.5, 0.75]
)
```

### Pattern 4: Robustness Table with Grouped Columns

```python
main = [pf.feols("Y ~ treat | unit + year", df, vcov={"CRV1": "unit"})]
robust = [
    pf.feols("Y ~ treat | unit + year", df, vcov="hetero"),
    pf.feols("Y2 ~ treat | unit + year", df, vcov={"CRV1": "unit"}),
]

create_robustness_table(
    model_groups=[main, robust],
    group_names=["Main Specification", "Robustness Checks"],
    title="Specification Sensitivity Analysis",
    label="tab:robustness",
    variable_labels={"treat": "Treatment Effect"},
    felabels={"unit": "Unit FE", "year": "Year FE"}
)
```

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

## Detailed Reference

- **Table function parameters**: Read `references/tables-api.md` when constructing tables with non-default parameters
- **Figure function parameters**: Read `references/figures-api.md` when customizing plots (colors, styles, CI levels)
- **Stargazer alternative**: Read `references/stargazer-alternative.md` when working with statsmodels (not PyFixest) models
