# Figures API Reference

Complete parameter documentation for the 3 figure generation functions, CI helper, and utilities.

## Table of Contents
- [create_event_study_plot](#create_event_study_plot)
- [create_treatment_assignment_plot](#create_treatment_assignment_plot)
- [create_coefficient_comparison_plot](#create_coefficient_comparison_plot)
- [_get_ci_critical_value](#_get_ci_critical_value)
- [ACADEMIC_STYLE](#academic_style)
- [Path Configuration](#path-configuration)
- [Utilities](#utilities)

---

## create_event_study_plot()

Event study visualization with confidence intervals. Extracts dynamic coefficients from PyFixest models fitted with `i(time_var, treat_var, ref=X)`.

```python
create_event_study_plot(
    model, title=None, filename=None,
    time_var="year", treat_var="ever_treated",
    reference_period=14, treatment_period=None,
    style="errorbar", colors=None, figsize=(12, 6),
    add_treatment_line=True, confidence_level=0.05,
    time_labels="relative", signif_levels=[0.01, 0.05, 0.1]
) -> str
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| model | pf.Feols | required | Fitted model with dynamic effects |
| title | str | None | Plot title (no title if None) |
| filename | str | None | Custom filename; auto-generated from title |
| time_var | str | "year" | Time variable name |
| treat_var | str | "ever_treated" | Treatment variable name |
| reference_period | int | 14 | Reference period in model formula |
| treatment_period | int | None | Actual treatment time for labels/vertical line |
| style | str | "errorbar" | Plot style: `"errorbar"`, `"filled"`, `"step"` |
| colors | dict | None | Custom colors: `{line, fill, zero_line, treatment_line, grid}` |
| figsize | tuple | (12, 6) | Figure dimensions in inches |
| add_treatment_line | bool | True | Add vertical line at treatment time |
| confidence_level | float | 0.05 | Alpha for CI: 0.05 = 95%, 0.01 = 99%, 0.10 = 90% |
| time_labels | str | "relative" | X-axis: `"relative"` (-2, -1, 0, 1, 2) or `"actual"` |

**Plot styles:**
- `"errorbar"`: Points with error bar caps (classic)
- `"filled"`: Line with shaded CI region (modern)
- `"step"`: Step function with shaded CI region

**CI calculation:** Uses t-distribution for n<30, normal for n>=30 (via `_get_ci_critical_value`).

**Reference period:** Automatically inserted at zero with coefficient=0, SE=0.

Returns: File path string. Saves PNG at 300 DPI.

---

## create_treatment_assignment_plot()

Heatmap of treatment status across units and time periods. Treated units sorted by first treatment time (earliest first), untreated at bottom.

```python
create_treatment_assignment_plot(
    data, unit="unit", time="year", treat="treat",
    title=None, filename=None, figsize=(10, 6),
    colors=None
) -> str
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| data | pd.DataFrame | required | Panel data with unit, time, treatment columns |
| unit | str | "unit" | Unit identifier column name |
| time | str | "year" | Time variable column name |
| treat | str | "treat" | Treatment indicator (0/1) column name |
| title | str | None | Plot title (no title if None) |
| filename | str | None | Custom filename; auto-generated from title |
| figsize | tuple | (10, 6) | Figure dimensions in inches |
| colors | dict | None | Custom colors: `{treated, untreated, grid}` |

**Sorting strategy:** Treated units sorted by first treatment period (ascending), then untreated units at bottom.

**Tick labels:** Automatically subsets labels when >20 units or >20 time periods.

Returns: File path string. Saves PNG at 300 DPI.

---

## create_coefficient_comparison_plot()

Forest plot comparing coefficients across multiple model specifications. Horizontal bars with error bars.

```python
create_coefficient_comparison_plot(
    models, model_names, title=None, filename=None,
    figsize=(12, 8), colors=None, use_ci=False,
    confidence_level=0.05
) -> str
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| models | List[pf.Feols] | required | Models to compare |
| model_names | List[str] | required | Model specification labels |
| title | str | None | Plot title (no title if None) |
| filename | str | None | Custom filename; auto-generated from title |
| figsize | tuple | (12, 8) | Figure dimensions in inches |
| colors | List[str] | None | Custom colors per model (default: matplotlib tab10) |
| use_ci | bool | False | If True: confidence intervals; if False: standard errors |
| confidence_level | float | 0.05 | Alpha for CI when use_ci=True |

**Variable matching:** Finds common variables across all models. Removes fixed-effects indicators (anything with `[` brackets).

Returns: File path string. Saves PNG at 300 DPI.

---

## _get_ci_critical_value()

```python
_get_ci_critical_value(n_obs, k_params=0, alpha=0.05) -> float
```

Returns the critical value (z-score or t-score) for confidence interval construction.

| Condition | Distribution | Rationale |
|-----------|-------------|-----------|
| n_obs < 30 | t-distribution (df = n_obs - k_params) | Conservative for small samples |
| n_obs >= 30 | Normal distribution | CLT convergence |

**Examples:**
- n=20, k=3, alpha=0.05 → t-score ≈ 2.110 (wider CI)
- n=100, k=3, alpha=0.05 → z-score ≈ 1.960

---

## ACADEMIC_STYLE

Default matplotlib rcParams applied to all figures:

```python
ACADEMIC_STYLE = {
    'figure.figsize': (10, 6),
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'font.size': 12,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'lines.linewidth': 2,
    'lines.markersize': 6,
    'errorbar.capsize': 4,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.transparent': False
}
```

---

## Path Configuration

### set_figure_output_path(path: str) -> None
Set output directory for figure files. Accepts absolute or relative (to cwd) paths. Creates directory if needed.

### get_figure_output_path() -> Path
Returns current figure output path. Falls back to default if not set.

---

## Utilities

### list_saved_figures() -> None
Lists all `.png` and `.pdf` files in the output directory with sizes in KB.

### clean_figure_directory(confirm=True) -> None
Deletes all image files. Prompts for confirmation unless `confirm=False`.

---

## Default Color Schemes

**Event study:**
```python
{'line': '#1f77b4', 'fill': '#aec7e8', 'zero_line': '#d62728',
 'treatment_line': '#2ca02c', 'grid': '#cccccc'}
```

**Treatment assignment:**
```python
{'treated': '#d62728', 'untreated': '#1f77b4', 'grid': '#cccccc'}
```

**Coefficient comparison:**
```python
['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
```
