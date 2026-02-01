# Stargazer Alternative (statsmodels)

An alternative table generation approach using `statsmodels` + `stargazer` instead of PyFixest. This is NOT bundled as an asset — generate inline if needed.

## When to Use
- Models fitted with `statsmodels.api.OLS` (not PyFixest)
- Need `tabularx` formatting (wider tables with auto-column width)
- Need `\sym{}` significance star commands instead of superscript

## Dependencies
```
pip install statsmodels stargazer
```

## AcademicTableGenerator Class

```python
from stargazer.stargazer import Stargazer

gen = AcademicTableGenerator(
    models=[model1, model2],          # statsmodels fitted results
    model_names=["(1)", "(2)"],       # Column headers
    dep_var_name="Stock Returns",     # Dependent variable label
    title="Regression Results",       # Caption
    label="tab:results",             # LaTeX label
    note="Standard errors in ...",   # Footnote
    table_position="ht!"            # LaTeX positioning
)

gen.add_control_rows(
    control_dict={"Firm Controls": [False, True]},
    fe_dict={"Firm FE": [True, True], "Year FE": [True, True]}
)

latex = gen.generate_table(filename="table.tex", return_string=True)
```

## Convenience Functions

```python
# Full-featured finance table
create_finance_regression_table(
    models, dep_var_name, model_names, title, label, note,
    controls={"Controls": [False, True]},
    fixed_effects={"FE": [True, True]},
    filename="table.tex"
)

# Simple table (no controls/FE rows)
create_basic_regression_table(models, model_names, title, label, filename)

# Event study table
create_event_study_table(models, model_names, title, label, filename)

# Robustness table
create_stargazer_robustness_table(models, model_names, title, label, filename)
```

## Key Differences from PyFixest Tables

| Feature | PyFixest tables | Stargazer tables |
|---------|----------------|-----------------|
| Input models | `pf.feols()` | `sm.OLS().fit()` |
| Table env | `threeparttable` | `tabularx` |
| Stars | Superscript (`^{***}`) | `\sym{***}` |
| FE indicators | Auto from model | Manual via `add_control_rows()` |
| Notes | `\parbox` above table | `\parbox` below |
