# Common Usage Patterns

Complete examples for standard econometric research workflows. These patterns are extracted from the SKILL.md for detailed reference while keeping the main skill file concise.

## Pattern 1: Standard DiD Regression Table

Progressive control addition across specifications.

```python
import pyfixest as pf
from pyfixest_latex import create_regression_table, set_output_path

set_output_path("Results/Tables")

# Fit three models with progressive controls
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
# Saves: Results/Tables/did_main_regression.tex
```

## Pattern 2: Event Study Plot + Table

Dynamic treatment effects visualization and tabulation.

```python
from pyfixest_latex import create_event_study_plot, create_dynamic_table, set_figure_output_path

set_output_path("Results/Tables")
set_figure_output_path("Results/Figures")

# Fit dynamic model with reference period
dynamic = pf.feols(
    "Y ~ i(year, ever_treated, ref=14) | unit + year",
    df, vcov={"CRV1": "unit"}
)

# Generate plot
create_event_study_plot(
    model=dynamic,
    title="Treatment Effects Over Time",
    time_var="year",
    treat_var="ever_treated",
    reference_period=14,
    treatment_period=15,  # Actual treatment time
    style="filled",
    confidence_level=0.05
)
# Saves: Results/Figures/treatment_effects_over_time.png

# Generate table
create_dynamic_table(
    models=dynamic,
    title="Dynamic Treatment Effects",
    label="tab:event_study",
    time_var="year",
    treat_var="ever_treated",
    reference_period=14,
    treatment_period=15,
    felabels={"unit": "Unit FE", "year": "Year FE"}
)
# Saves: Results/Tables/event_study_dynamic.tex
```

## Pattern 3: Summary Statistics

Descriptive statistics for key variables.

```python
from pyfixest_latex import create_summary_statistics_table

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
# Saves: Results/Tables/summary_summary_stats.tex
```

## Pattern 4: Robustness Table with Grouped Columns

Multi-group specifications with grouped column headers.

```python
from pyfixest_latex import create_robustness_table

# Main specification
main = [pf.feols("Y ~ treat | unit + year", df, vcov={"CRV1": "unit"})]

# Robustness checks
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
# Saves: Results/Tables/robustness_robustness.tex
```

## Pattern 5: Treatment Assignment Heatmap

Visualize treatment timing across units.

```python
from pyfixest_latex import create_treatment_assignment_plot

# Prepare panel data (unit × time with treatment indicator)
df_panel = df[['unit', 'time', 'treated']].drop_duplicates()

create_treatment_assignment_plot(
    data=df_panel,
    unit="unit",
    time="time",
    treat="treated",
    title="Treatment Assignment Pattern",
    filename="treatment_assignment.png"
)
# Saves: Results/Figures/treatment_assignment.png
```

## Pattern 6: Coefficient Comparison (Forest Plot)

Compare main coefficient across specifications.

```python
from pyfixest_latex import create_coefficient_comparison_plot

# Different specifications
models = [
    pf.feols("Y ~ did | unit + time", df, vcov={"CRV1": "unit"}),
    pf.feols("Y ~ did + controls | unit + time", df, vcov={"CRV1": "unit"}),
    pf.feols("Y ~ did | unit + time + state", df, vcov={"CRV1": "unit"}),
]

model_names = ["Baseline", "With Controls", "State FE"]

create_coefficient_comparison_plot(
    models=models,
    model_names=model_names,
    title="Specification Robustness",
    filename="coefficient_comparison.png",
    use_ci=True,
    confidence_level=0.05
)
# Saves: Results/Figures/coefficient_comparison.png
```

## Pattern 7: Multiple Outcomes

Generate tables for multiple dependent variables.

```python
outcomes = ['roa', 'leverage', 'market_cap']

for outcome in outcomes:
    models = [
        pf.feols(f"{outcome} ~ did | unit + time", df, vcov={"CRV1": "unit"}),
        pf.feols(f"{outcome} ~ did + controls | unit + time", df, vcov={"CRV1": "unit"})
    ]

    create_regression_table(
        models=models,
        model_names=["(1)", "(2)"],
        title=f"Treatment Effects on {outcome.upper()}",
        label=f"tab:{outcome}",
        filename=f"Table_{outcome}_results.tex",
        variable_labels={'did': 'Treatment × Post'},
        depvar_labels={outcome: outcome.replace('_', ' ').title()}
    )
```

## Pattern 8: Consolidated Table (Multiple Outcomes, Same Spec)

Show multiple outcomes side-by-side.

```python
all_models = []
model_names = []

for outcome in ['roa', 'leverage', 'market_cap']:
    models = [
        pf.feols(f"{outcome} ~ did | unit + time", df, vcov={"CRV1": "unit"}),
        pf.feols(f"{outcome} ~ did + controls | unit + time", df, vcov={"CRV1": "unit"})
    ]
    all_models.extend(models)
    model_names.extend(["(1)", "(2)"])

create_regression_table(
    models=all_models,
    model_names=model_names,
    title="Treatment Effects on Financial Performance",
    label="tab:consolidated",
    variable_labels={'did': 'Treatment × Post'},
    depvar_labels={
        'roa': 'ROA',
        'leverage': 'Leverage',
        'market_cap': 'Market Cap'
    }
)
```

## Pattern 9: Different Treatment Definitions

Test sensitivity to treatment classification.

```python
# Define multiple treatment groups
treatment_definitions = {
    'Main': df['sic'].isin(['6798']),
    'Broad': df['sic'].str.startswith('67'),
    'Narrow': df['sic'].isin(['6798', '6799'])
}

models = []
model_names = []

for name, treated in treatment_definitions.items():
    df[f'did_{name}'] = df['post'] * treated.astype(int)

    model = pf.feols(f"Y ~ did_{name} | unit + time", df, vcov={"CRV1": "unit"})
    models.append(model)
    model_names.append(name)

create_regression_table(
    models=models,
    model_names=model_names,
    title="Sensitivity to Treatment Definition",
    label="tab:treatment_definitions"
)
```

## Pattern 10: Heterogeneous Effects

Treatment effects by subgroup.

```python
# Define subgroups
df['large_firm'] = (df['assets'] > df['assets'].median()).astype(int)

# Estimate for each subgroup
models = [
    pf.feols("Y ~ did | unit + time", df[df['large_firm']==1], vcov={"CRV1": "unit"}),
    pf.feols("Y ~ did | unit + time", df[df['large_firm']==0], vcov={"CRV1": "unit"}),
]

create_regression_table(
    models=models,
    model_names=["Large Firms", "Small Firms"],
    title="Heterogeneous Treatment Effects by Firm Size",
    label="tab:heterogeneous",
    variable_labels={'did': 'Treatment × Post'}
)
```
