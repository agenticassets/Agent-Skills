# Generalized Difference-in-Differences Analysis Template

**A production-ready Python template for conducting and reporting publication-quality DiD analyses using PyFixest.**

## Overview

This template provides everything needed to run a complete difference-in-differences analysis on your data and generate professional LaTeX output for academic manuscripts. It implements best practices for:

- Data validation and cleaning
- Treatment indicator construction
- 2x2 DiD regression design
- Event study (dynamic effects) analysis
- Summary statistics tables
- Publication-quality figures

## Quick Start

### 1. Copy the Template

```bash
cp example_did_analysis_template.py my_analysis.py
```

### 2. Customize Configuration

Edit the `DidConfig` class in your script:

```python
class DidConfig:
    # YOUR DATA FILE
    DATA_PATH = "path/to/your/data.parquet"

    # VARIABLE NAMES (map to your data)
    UNIT_ID = "firm_id"           # Examples: gvkey, permno, household_id
    TIME_VAR = "year"             # Examples: year, year_quarter, year_month
    GROUP_VAR = "treatment_group" # Binary indicator (0/1)

    # TREATMENT TIMING
    TREATMENT_TIME = 2016         # When treatment occurred

    # OUTCOMES (what you're measuring)
    OUTCOME_VARIABLES = {
        "profit_margin": "Profit Margin (%)",
        "total_assets": "Total Assets (log)"
    }

    # CONTROLS (covariates)
    CONTROL_VARIABLES = ["firm_size", "leverage", "liquidity"]
```

### 3. Run Analysis

```bash
python my_analysis.py
```

## Configuration Guide

### Core Variables

These must exist in your data:

```python
UNIT_ID = "firm_id"        # Identifies units (firms, people, regions)
TIME_VAR = "year"          # Identifies time periods
GROUP_VAR = "treated"      # Binary treatment group indicator (0/1)
```

**Common Examples:**

| Type | Unit ID | Time Var | Group Var |
|------|---------|----------|-----------|
| Firms | gvkey | year | treated |
| Individuals | person_id | year_month | received_treatment |
| Regions | county_id | quarter | policy_exposure |
| Schools | school_id | academic_year | intervention |

### Treatment Definition

```python
TREATMENT_TIME = 2016
```

The template creates:
- `post_treatment`: 1 if TIME_VAR >= TREATMENT_TIME, 0 otherwise
- `treated`: Binary indicator (from GROUP_VAR)
- `did`: Interaction term (post_treatment × treated)

### Outcome Variables

```python
OUTCOME_VARIABLES = {
    "variable_name": "Display Label",
    "profit": "Profit (millions)",
    "employment": "Employment (log)"
}
```

The template estimates separate regressions for each outcome with both:
1. Baseline specification (DiD + FE)
2. With-controls specification (DiD + Controls + FE)

### Control Variables

```python
CONTROL_VARIABLES = ["var1", "var2", "var3"]
```

Leave empty `[]` for baseline specification without controls.

### Fixed Effects

```python
INCLUDE_UNIT_FE = True   # Unit fixed effects (removes permanent unit characteristics)
INCLUDE_TIME_FE = True   # Time fixed effects (removes common time trends)
```

This implements the standard 2x2 DiD design.

### Standard Error Clustering

```python
CLUSTER_VAR = "firm_id"  # Cluster at unit level
```

Leave `None` for HC1 robust standard errors.

## Output Files

### LaTeX Tables

Saved to `OUTPUT_DIR` (default: `Results/Tables/`):

- `{PROJECT_NAME}_summary_statistics.tex` - Summary stats table

### Figures

Saved to `FIGURES_DIR` (default: `Results/Figures/`):

- `{PROJECT_NAME}_{outcome}_event_study.png` - Event study plots (if event study enabled)

## Advanced Customization

### Sample Restrictions

```python
MIN_OBSERVATIONS_PER_UNIT = 20  # Require 20+ obs per unit
MIN_TIME_PERIODS = 10           # Require 10+ time periods
```

Useful for ensuring balanced panel or minimum observation requirements.

### Event Study Configuration

```python
RUN_EVENT_STUDY = True          # Enable dynamic effects
PERIODS_BEFORE = 4              # Leads before treatment
PERIODS_AFTER = 4               # Lags after treatment
REFERENCE_PERIOD = -1           # Reference period (typically -1)
```

The event study creates leads/lags relative to treatment:
- Negative periods: before treatment
- Zero: treatment period (omitted)
- Positive periods: after treatment

**Interpretation:** Coefficients show treatment effect relative to reference period.

### Variable Labels

```python
VARIABLE_LABELS = {
    "did": "Treatment × Post",
    "firm_size": "Log(Assets)",
    "leverage": "Debt-to-Equity"
}

CONTROL_LABELS = {
    "firm_size": "Firm Size",
    "leverage": "Leverage Ratio"
}
```

These appear in table headers and legends.

## Data Requirements

### Required Columns

Your data must contain:
- Unit identifier (e.g., firm_id)
- Time identifier (e.g., year)
- Treatment group indicator (binary: 0/1)
- Outcome variables (numeric)
- Control variables (numeric)

### Data Format

Supports: `.parquet`, `.csv`, `.xlsx`, `.dta`

```python
DATA_PATH = "data.parquet"  # or data.csv, data.xlsx, data.dta
```

### Data Quality

The template automatically:
1. Replaces infinite values with NaN
2. Drops observations with missing analysis variables
3. Validates required variables exist
4. Reports sample composition

## Workflow

```
1. Load Data
   ├─ Verify required variables
   └─ Check variable types

2. Prepare Data
   ├─ Create treatment indicators (post, treated, did)
   ├─ Create sequential time variable
   ├─ Handle missing/infinite values
   └─ Apply sample restrictions

3. Run Regressions
   ├─ 2x2 DiD for each outcome (baseline + with controls)
   └─ Dynamic effects (if enabled)

4. Generate Output
   ├─ Summary statistics table (LaTeX)
   ├─ Event study plots (PNG)
   └─ Print diagnostics to console
```

## Regression Specifications

### Baseline DiD

```
outcome = β₀ + β₁(DID) + α(unit FE) + γ(time FE) + ε
```

Where DID = post_treatment × treated

### With Controls

```
outcome = β₀ + β₁(DID) + β₂...ₖ(Controls) + α(unit FE) + γ(time FE) + ε
```

### Event Study

```
outcome = Σ β_t × 1(t=τ, treated=1) + α(unit FE) + γ(time FE) + ε
```

Coefficients β_t show treatment effect in each period relative to reference period.

## Example: Complete Customization

```python
class DidConfig:
    # Data
    DATA_PATH = "C:/Research/data/firms_2010_2020.parquet"

    # Variables
    UNIT_ID = "gvkey"
    TIME_VAR = "fiscal_year"
    GROUP_VAR = "treated_by_regulation"

    # Treatment: New regulation in 2016
    TREATMENT_TIME = 2016

    # Outcomes: Firm performance
    OUTCOME_VARIABLES = {
        "roa": "Return on Assets (%)",
        "roe": "Return on Equity (%)",
        "growth": "Revenue Growth (%)"
    }

    # Controls: Firm characteristics
    CONTROL_VARIABLES = [
        "ln_assets",    # Firm size
        "leverage",     # Debt level
        "cash_ratio",   # Liquidity
        "age"          # Firm age
    ]

    # Clustering
    CLUSTER_VAR = "gvkey"

    # Event study: 8 quarters before/after
    RUN_EVENT_STUDY = True
    PERIODS_BEFORE = 8
    PERIODS_AFTER = 8

    # Output
    OUTPUT_DIR = "Results/Tables/"
    FIGURES_DIR = "Results/Figures/"
    PROJECT_NAME = "RegulationEffect_2016"
```

## Robustness Checks

Modify `DidConfig` to run robustness variations:

### Exclude Treatment Year

```python
class DidConfig_NoTreatmentYear(DidConfig):
    # Add to prepare_data():
    # df_clean = df_clean[df_clean[TIME_VAR] != TREATMENT_TIME]
```

### Balanced Panel Only

```python
MIN_OBSERVATIONS_PER_UNIT = 11  # Exactly 11 years per unit
```

### Alternative Controls

```python
CONTROL_VARIABLES = ["ln_assets", "leverage"]  # Minimal
# vs
CONTROL_VARIABLES = ["ln_assets", "leverage", "cash", "age", "industry_sales_growth"]  # Full
```

### Different Treatment Time (Placebo)

```python
TREATMENT_TIME = 2015  # Run with different treatment date
```

## Interpreting Output

### Summary Statistics Table

Shows mean, std dev, percentiles for each variable. Use to describe sample composition.

### DiD Coefficient

- **Positive & significant**: Treatment increased outcome
- **Negative & significant**: Treatment decreased outcome
- **Insignificant**: No detectable treatment effect

### Standard Errors

- **CRV1 (Clustered)**: Accounts for repeated observations per unit
- **HC1 (Robust)**: Conservative heteroskedasticity-robust SEs

### Event Study Plot

- **Dashed line at 0**: Reference period
- **Dots with error bars**: Point estimates + 95% CIs
- **Slope**: Trajectory of treatment effect

**Example interpretation:**
- Flat before treatment (pre-trends)
- Sharp change at treatment
- Sustained effect after

## Integration with LaTeX Manuscript

### Include Summary Statistics

```latex
\input{Results/Tables/MyProject_summary_statistics}
```

### Include Event Study Plot

```latex
\begin{figure}[h!]
  \centering
  \caption{Event Study: Treatment Effects on ROA}
  \includegraphics[width=0.8\textwidth]{Results/Figures/MyProject_roa_event_study.png}
  \label{fig:event_study_roa}
\end{figure}
```

### Reference in Text

```latex
As shown in Figure \ref{fig:event_study_roa}, the treatment effect on return on assets
becomes statistically significant in the period immediately following implementation.
```

## Troubleshooting

### "Data file not found"

```python
DATA_PATH = "path/to/your/data.parquet"
```

Use absolute path or verify relative path is correct.

### "Missing required variable"

Check variable names in DidConfig match your data exactly (case-sensitive):

```python
df.columns  # Print all column names
```

### "PyFixest not installed"

```bash
pip install pyfixest
```

### "All observations dropped"

Too many missing values in analysis variables. Check:

```python
df[outcome_vars].isna().sum()  # Count missing per variable
```

### Empty event study plot

Not enough variation in time dimension or control variables. Verify:
- Multiple time periods in data
- Variation in treatment group indicator

## Citation

If using this template in published work, please cite:

```
DiD Analysis Template v1.0
Generated from pyfixest-latex skill
https://github.com/[repo]/skills/pyfixest-latex
```

## Further Reading

### Difference-in-Differences

- Angrist & Pischke (2009). *Mostly Harmless Econometrics*
- Callaway & Sant'Anna (2021). "Difference-in-Differences with multiple time periods"

### PyFixest Documentation

- https://github.com/s3alfisc/pyfixest

### LaTeX Table Integration

- https://www.overleaf.com/learn/latex/tables

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Verify data column names
3. Print intermediate DataFrames: `print(df.head())`
4. Run with diagnostic output enabled

## Version History

**v1.0** (2025-02-01)
- Initial template release
- 2x2 DiD + event study support
- Summary stats and event study plots
- UTF-8 Windows compatibility
