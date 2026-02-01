# Tables API Reference

Complete parameter documentation for the 4 table generation functions and utilities.

## Table of Contents
- [create_regression_table](#create_regression_table)
- [create_dynamic_table](#create_dynamic_table)
- [create_robustness_table](#create_robustness_table)
- [create_summary_statistics_table](#create_summary_statistics_table)
- [Internal Helpers](#internal-helpers)
- [Utilities](#utilities)

---

## create_regression_table()

Standard regression tables with multiple models in columns.

```python
create_regression_table(
    models, model_names, title, label,
    filename=None, custom_notes=None, variable_labels=None,
    depvar_labels=None, felabels=None, model_heads=None,
    include_fe_stats=True, signif_levels=[0.01, 0.05, 0.1],
    digits=3, table_font_size="footnotesize", notes_font_size="footnotesize"
) -> str
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| models | List[pf.Feols] | required | Fitted PyFixest models |
| model_names | List[str] | required | Column headers (e.g., ["Basic", "Controls"]) |
| title | str | required | LaTeX table caption |
| label | str | required | LaTeX label for `\ref{}` (e.g., "tab:main") |
| filename | str | None | Output filename; auto-generated as `{label}_regression.tex` |
| custom_notes | str | None | Table footnotes; defaults to significance star legend |
| variable_labels | dict | None | `{var_name: "Label"}` for coefficient rows |
| depvar_labels | dict | None | `{depvar: "Label"}` for column headers |
| felabels | dict | None | `{fe_var: "FE Label"}` for FE indicator rows |
| model_heads | List[str] | None | Override column headers (overrides model_names) |
| include_fe_stats | bool | True | Show FE indicator rows |
| signif_levels | List[float] | [0.01, 0.05, 0.1] | Significance thresholds for ***, **, * |
| digits | int | 3 | Decimal places |
| table_font_size | str | "footnotesize" | LaTeX font size for table body |
| notes_font_size | str | "footnotesize" | LaTeX font size for parbox notes |

Returns: LaTeX table string. Also saves `.tex` file to output path.

---

## create_dynamic_table()

Event study tables with time-varying treatment effects. Converts coefficient labels to relative time notation ($t_{-2}$, $t_0$, $t_{+3}$).

```python
create_dynamic_table(
    models, title, label,
    filename=None, model_names=None, time_var="year",
    treat_var="ever_treated", reference_period=14,
    treatment_period=None, custom_notes=None,
    variable_labels=None, depvar_labels=None, felabels=None,
    model_heads=None, signif_levels=[0.01, 0.05, 0.1],
    digits=3, table_font_size="footnotesize", notes_font_size="footnotesize"
) -> str
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| models | Any or List[Any] | required | Single or list of dynamic PyFixest models |
| title | str | required | LaTeX caption |
| label | str | required | LaTeX label |
| filename | str | None | Auto-generated as `{label}_dynamic.tex` |
| model_names | List[str] | None | Column headers |
| time_var | str | "year" | Time variable in `i(time_var, treat_var, ref=X)` |
| treat_var | str | "ever_treated" | Treatment variable |
| reference_period | int | 14 | Base period in the model formula |
| treatment_period | int | None | Actual treatment time for relative labels. **Critical**: if provided, labels show $t_{k}$ relative to this period |
| custom_notes | str | None | Auto-generates note about reference/treatment periods |
| variable_labels | dict | None | Coefficient label overrides |
| depvar_labels | dict | None | Dependent variable label overrides |
| felabels | dict | None | Fixed effects label overrides |
| model_heads | List[str] | None | Column header overrides |
| signif_levels | List[float] | [0.01, 0.05, 0.1] | Significance thresholds |
| digits | int | 3 | Decimal places |

Returns: LaTeX table string. Saves `.tex` file.

---

## create_robustness_table()

Multi-group specification tables with `\multicolumn` grouped headers.

```python
create_robustness_table(
    model_groups, group_names, title, label,
    filename=None, custom_notes=None, variable_labels=None,
    depvar_labels=None, felabels=None, model_heads=None,
    signif_levels=[0.01, 0.05, 0.1], digits=3,
    table_font_size="footnotesize", notes_font_size="footnotesize"
) -> str
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| model_groups | List[List[Any]] | required | List of model groups: `[[m1, m2], [m3, m4]]` |
| group_names | List[str] | required | Names for each group: `["Main", "Robustness"]` |
| title | str | required | LaTeX caption |
| label | str | required | LaTeX label |
| filename | str | None | Auto-generated as `{label}_robustness.tex` |
| custom_notes | str | None | Default: robustness note + significance legend |
| variable_labels | dict | None | Coefficient label overrides |
| depvar_labels | dict | None | Dependent variable label overrides |
| felabels | dict | None | Fixed effects label overrides |
| model_heads | List[str] | None | Column header overrides |
| signif_levels | List[float] | [0.01, 0.05, 0.1] | Significance thresholds |
| digits | int | 3 | Decimal places |

Returns: LaTeX table string. Saves `.tex` file.

---

## create_summary_statistics_table()

Descriptive statistics table from a pandas DataFrame. Does NOT require PyFixest models.

```python
create_summary_statistics_table(
    data, variables, variable_labels, title, label,
    filename=None, custom_notes=None, digits=3,
    include_count=True, percentiles=[0.25, 0.5, 0.75],
    table_font_size="footnotesize", notes_font_size="footnotesize"
) -> str
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| data | pd.DataFrame | required | Source dataset |
| variables | List[str] | required | Column names to summarize |
| variable_labels | dict | required | `{var_name: "Professional Label"}` |
| title | str | required | LaTeX caption |
| label | str | required | LaTeX label |
| filename | str | None | Auto-generated as `{label}_summary_stats.tex` |
| custom_notes | str | None | Default: variable count note |
| digits | int | 3 | Decimal places |
| include_count | bool | True | Add N column |
| percentiles | List[float] | [0.25, 0.5, 0.75] | Which percentiles to include |

Columns: Variable | N | Mean | Std Dev | Min | Max | 25% | 50% | 75%

Returns: LaTeX table string. Saves `.tex` file.

---

## Internal Helpers

These are used internally but can be called for customization:

### _normalize_latex_symbols(text: str) -> str
Converts Unicode multiplication sign (x) to LaTeX `$\times$`. Handles both spaced and non-spaced variants.

### _apply_depvar_labels(line: str, depvar_labels: dict) -> str
Replaces dependent variable names in `\multicolumn{}{}{}` headers with custom labels.

### _reorder_fixed_effects(lines: list) -> list
Ensures Unit FE rows always appear before Time FE rows. Recognizes 25+ FE naming patterns (unit, firm, gvkey, year, quarter, etc.).

### _filter_and_format_etable_lines(latex_content, depvar_labels, variable_labels) -> str
Centralized post-processing: removes S.E. type and R^2 Within rows, applies labels, formats observation counts with commas, reorders FE.

---

## Utilities

### list_saved_tables() -> None
Lists all `.tex` files in the output directory with file sizes.

### clean_table_directory(confirm=True) -> None
Deletes all `.tex` files in the output directory. Prompts for confirmation unless `confirm=False`.
