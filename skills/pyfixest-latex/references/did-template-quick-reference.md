# DiD Analysis Template - Quick Reference

## 30-Second Setup

```python
class DidConfig:
    DATA_PATH = "your_data.parquet"        # 1. Set your data file
    UNIT_ID = "firm_id"                    # 2. Unit identifier
    TIME_VAR = "year"                      # 3. Time identifier
    GROUP_VAR = "treated"                  # 4. Binary treatment indicator
    TREATMENT_TIME = 2016                  # 5. When treatment occurred
    OUTCOME_VARIABLES = {"outcome": "Label"}   # 6. What you're measuring
    CONTROL_VARIABLES = ["var1", "var2"]   # 7. Control variables
```

Then run:
```bash
python example_did_analysis_template.py
```

## Essential Configuration

| Setting | Example | Purpose |
|---------|---------|---------|
| `DATA_PATH` | `"data.parquet"` | Your data file |
| `UNIT_ID` | `"gvkey"` | Unit identifier (firm, person, region) |
| `TIME_VAR` | `"year"` | Time dimension |
| `GROUP_VAR` | `"treated"` | Binary treatment indicator (0/1) |
| `TREATMENT_TIME` | `2016` | When treatment started |
| `OUTCOME_VARIABLES` | `{"roa": "ROA"}` | Dependent variables |
| `CONTROL_VARIABLES` | `["size", "lev"]` | Covariates |
| `CLUSTER_VAR` | `"gvkey"` | Standard error clustering |

## Auto-Generated Treatment Variables

From your `GROUP_VAR` and `TIME_VAR`, the template creates:

```python
df['post_treatment'] = (df[TIME_VAR] >= TREATMENT_TIME)  # After treatment?
df['treated'] = df[GROUP_VAR]                             # In treatment group?
df['did'] = df['post_treatment'] * df['treated']          # DiD term
```

## What You Get

### Outputs

- **Summary Stats Table** → `{PROJECT_NAME}_summary_statistics.tex`
- **Event Study Plot** → `{PROJECT_NAME}_{outcome}_event_study.png`
- **Console Diagnostics** → Sample sizes, treatment breakdown

### Generated Regressions (per outcome)

```
[1] Baseline:     outcome ~ did | unit_FE + time_FE
[2] +Controls:    outcome ~ did + controls | unit_FE + time_FE
[3] Event Study:  outcome ~ i(time_seq, treated) | unit_FE + time_FE
```

## Diagnostic Output

```
DATA PREPARATION
================
[LOAD] Loaded: 50,000 observations × 30 variables
[PREP] Created treatment indicators
[CLEAN] Dropped 2,145 with missing values
[TREATMENT BALANCE]
   Treated observations: 15,000 (30.0%)
   Post-treatment: 25,000 (50.0%)
   DiD (treated × post): 7,500 (15.0%)
```

## Common Customizations

### 1. Multiple Outcomes

```python
OUTCOME_VARIABLES = {
    "roa": "Return on Assets",
    "roe": "Return on Equity",
    "growth": "Revenue Growth"
}
```

**Result:** Separate regressions for each outcome

### 2. No Event Study

```python
RUN_EVENT_STUDY = False
```

**Result:** Skips dynamic effects analysis (faster)

### 3. Balanced Panel

```python
MIN_OBSERVATIONS_PER_UNIT = 11
```

**Result:** Keeps only firms with ≥11 observations

### 4. Minimal Specification

```python
CONTROL_VARIABLES = []
INCLUDE_UNIT_FE = True
INCLUDE_TIME_FE = True
```

**Result:** DiD + Fixed Effects only

### 5. Clustered SEs

```python
CLUSTER_VAR = "firm_id"
```

**Result:** Standard errors clustered at firm level

## Data Requirements Checklist

- [ ] Data file exists at `DATA_PATH`
- [ ] Column exists for unit ID (UNIT_ID)
- [ ] Column exists for time (TIME_VAR)
- [ ] Column exists for treatment group, 0/1 (GROUP_VAR)
- [ ] Outcome columns are numeric, no missing (except allowed)
- [ ] Control columns are numeric, no missing (except allowed)

## Troubleshooting Quick Fixes

| Error | Fix |
|-------|-----|
| "Data file not found" | Check `DATA_PATH` with absolute path |
| "Missing variable" | Verify column names in data: `df.columns` |
| "PyFixest not installed" | `pip install pyfixest` |
| "All observations dropped" | Check for missing values: `df.isna().sum()` |
| "Empty event study plot" | Verify time variation and `RUN_EVENT_STUDY = True` |

## File Structure After Running

```
Results/
├── Tables/
│   └── MyProject_summary_statistics.tex
└── Figures/
    ├── MyProject_roa_event_study.png
    └── MyProject_roe_event_study.png
```

## LaTeX Integration

### Include Summary Stats

```latex
\input{Results/Tables/MyProject_summary_statistics}
```

### Include Event Study Figure

```latex
\begin{figure}[h!]
  \centering
  \includegraphics[width=0.8\textwidth]{Results/Figures/MyProject_roa_event_study.png}
  \caption{Event Study: Treatment Effects on ROA}
  \label{fig:event_roa}
\end{figure}
```

## Interpreting Results

### DiD Coefficient (β₁)

```
y = β₀ + β₁(DID) + FEs
```

- **β₁ > 0, p < 0.05**: Treatment INCREASED outcome (statistically significant)
- **β₁ < 0, p < 0.05**: Treatment DECREASED outcome (statistically significant)
- **p > 0.05**: No significant treatment effect detected

### Standard Errors

- **CRV1 (clustered)**: Conservative, accounts for unit-level correlation
- **HC1 (robust)**: Heteroskedasticity-robust, appropriate if no clustering

### Event Study Coefficients (β_t)

- **t < 0**: Before treatment (should be near zero = no pre-trends)
- **t = 0**: Treatment period (typically omitted)
- **t > 0**: After treatment (estimates dynamic treatment effect)

## Advanced: Robustness Variations

Create subclass of DidConfig:

```python
class DidConfig_Placebo(DidConfig):
    """Test with earlier treatment date"""
    TREATMENT_TIME = 2015

class DidConfig_NoControls(DidConfig):
    """Baseline without controls"""
    CONTROL_VARIABLES = []

class DidConfig_BalancedPanel(DidConfig):
    """Balanced panel only"""
    MIN_OBSERVATIONS_PER_UNIT = 11
```

Run each separately:

```python
for config_class in [DidConfig, DidConfig_Placebo, DidConfig_NoControls]:
    config = config_class()
    main(config)
```

## Key Assumptions

1. **Parallel Trends**: Treated/control groups would follow same path absent treatment
2. **No Anticipation**: Units don't change behavior before treatment (check with event study)
3. **No Treatment Spillovers**: Treatment affects only treated units
4. **Constant Treatment Effect**: Same effect across time and units

**Verify:** Event study should show:
- Near-zero coefficients before treatment
- Change at treatment time
- Persistent effects after

## Module Architecture

```python
# Configuration (customize this)
class DidConfig:
    DATA_PATH = "..."
    UNIT_ID = "..."
    ...

# Workflow (runs automatically)
load_data(config)              # Load from disk
validate_data(df, config)      # Check requirements
prepare_data(df, config)       # Create treatment variables
run_did_analysis(df, config)   # Estimate 2x2 DiD
run_event_study(df, config)    # Estimate dynamic effects
main(config)                   # Orchestrate all
```

## Performance Notes

- **Typical dataset** (50K obs, 20 variables): ~5 seconds
- **Large dataset** (1M+ obs): May take 30-60 seconds
- **Event study** adds ~20% overhead (depends on time periods)

## Next Steps

1. **Copy template** → `my_analysis.py`
2. **Customize config** → Update 7 essential settings
3. **Run analysis** → `python my_analysis.py`
4. **Check outputs** → Look in `Results/`
5. **Integrate with manuscript** → Use `\input{}` for tables, `\includegraphics{}` for figures
6. **Run robustness checks** → Modify config, re-run

## One-Page Example

```python
class DidConfig:
    DATA_PATH = "C:/Research/firms.parquet"
    UNIT_ID = "gvkey"
    TIME_VAR = "year"
    GROUP_VAR = "treated_by_2016_reform"
    TREATMENT_TIME = 2016
    OUTCOME_VARIABLES = {"roa": "ROA (%)", "roe": "ROE (%)"}
    CONTROL_VARIABLES = ["ln_assets", "leverage"]
    CLUSTER_VAR = "gvkey"
    RUN_EVENT_STUDY = True
    PERIODS_BEFORE = 5
    PERIODS_AFTER = 5

if __name__ == "__main__":
    main(DidConfig())
```

## References

- Angrist & Pischke (2009). *Mostly Harmless Econometrics*
- PyFixest: https://github.com/s3alfisc/pyfixest
- This template: `.claude/skills/pyfixest-latex/assets/example_did_analysis_template.py`
