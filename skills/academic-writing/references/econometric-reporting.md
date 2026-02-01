# Econometric Reporting Conventions

Standards for reporting regression results, coefficient interpretation, and fixed effects notation in finance, economics, and real estate research.

## Table of Contents
- Coefficient Interpretation
- Statistical Significance Reporting
- Standard Errors and Clustering
- Fixed Effects Notation
- Model Specification Reporting
- Economic Magnitude Interpretation
- Regression Table Structure

## Coefficient Interpretation

### Basic Interpretation Template

**Level-level model**:
```latex
Y_{i,t} = \alpha + \beta_1 X_{i,t} + \epsilon_{i,t}
```
**Interpretation**: A one-unit increase in X is associated with a β₁-unit change in Y.

**Example**:
```
The coefficient on AI adoption (β = 0.123, p < 0.01) indicates that properties with AI valuations have 12.3 percentage point higher accuracy.
```

### Log Transformations

**Log-log model**:
```latex
\ln(Y_{i,t}) = \alpha + \beta_1 \ln(X_{i,t}) + \epsilon_{i,t}
```
**Interpretation**: A 1% increase in X is associated with a β₁% change in Y (elasticity).

**Example**:
```
The elasticity of accuracy with respect to AI usage is 0.45, indicating that a 10% increase in AI adoption increases accuracy by 4.5%.
```

**Log-level model**:
```latex
\ln(Y_{i,t}) = \alpha + \beta_1 X_{i,t} + \epsilon_{i,t}
```
**Interpretation**: A one-unit increase in X is associated with a (100 × β₁)% change in Y.

**Example**:
```
The coefficient of 0.015 implies that AI adoption increases property values by 1.5%.
```

**Level-log model**:
```latex
Y_{i,t} = \alpha + \beta_1 \ln(X_{i,t}) + \epsilon_{i,t}
```
**Interpretation**: A 1% increase in X is associated with a (β₁/100)-unit change in Y.

### Interaction Terms

**Standard interaction**:
```latex
Y_{i,t} = \alpha + \beta_1 Treatment_i + \beta_2 Moderator_i + \beta_3 (Treatment_i \times Moderator_i) + \epsilon_{i,t}
```

**Interpretation**:
- β₁: Effect of Treatment when Moderator = 0
- β₂: Effect of Moderator when Treatment = 0
- β₃: Additional effect of Treatment when Moderator increases by one unit

**Example**:
```
The interaction coefficient (β₃ = 0.082, p < 0.05) indicates that the effect of AI on accuracy is 8.2 percentage points larger for complex properties relative to simple properties.
```

**Marginal effects for interactions**:
```
∂Y/∂Treatment = β₁ + β₃ × Moderator
```

At mean Moderator value:
```
The marginal effect of AI at mean complexity (5.2) is 0.123 + (0.082 × 5.2) = 0.549.
```

### Difference-in-Differences

**Standard DiD**:
```latex
Y_{i,t} = \alpha + \beta_1 Treat_i + \beta_2 Post_t + \beta_3 (Treat_i \times Post_t) + \epsilon_{i,t}
```

**Interpretation**:
- β₃: DiD estimator = (Treat_post - Treat_pre) - (Control_post - Control_pre)

**Example**:
```
The DiD coefficient (β = 0.097, p < 0.01) indicates that AI adoption increased accuracy by 9.7 percentage points relative to control properties over the same period.
```

## Statistical Significance Reporting

### Standard Significance Levels

**Convention**:
- *** p < 0.01 (1% level)
- ** p < 0.05 (5% level)
- * p < 0.10 (10% level)

**Table formatting**:
```latex
AI Adoption & 0.123*** & 0.118** & 0.105* \\
& (0.028) & (0.046) & (0.056) \\
```

### In-Text Reporting

**Full reporting** (preferred for main results):
```
AI adoption increases accuracy by 12.3 percentage points (β = 0.123, SE = 0.028, t = 4.39, p < 0.01).
```

**Compact reporting** (for secondary results):
```
AI adoption increases accuracy (β = 0.123, p < 0.01).
```

**Never report**:
- "p = 0.000" → Use "p < 0.01"
- Exact p-values unless close to threshold (e.g., p = 0.052)

### Statistical vs Economic Significance

**Always distinguish**:
```
The coefficient is statistically significant (p < 0.01) but economically small, representing only 0.1% of mean property value.
```

## Standard Errors and Clustering

### Reporting Standard Errors

**In tables**: Parentheses below coefficients
```latex
AI Adoption & 0.123*** \\
& (0.028) \\
```

**In text**: SE or parenthetical
```
β = 0.123 (SE = 0.028)
β = 0.123 (0.028)
```

### Clustering

**Table notes template**:
```
Standard errors (in parentheses) are clustered at the [level].
*** p<0.01, ** p<0.05, * p<0.10.
```

**Common clustering levels**:
- Firm-level: "clustered at the firm level"
- MSA-level: "clustered at the metropolitan statistical area (MSA) level"
- Two-way: "two-way clustered by firm and year"

**In-text description**:
```
We cluster standard errors at the MSA level to account for within-market correlation in unobservables.
```

### Robust Standard Errors

**When to use**:
- Heteroskedasticity concerns
- No natural clustering unit

**Table notes**:
```
Robust standard errors (in parentheses) are reported.
*** p<0.01, ** p<0.05, * p<0.10.
```

## Fixed Effects Notation

### Standard Fixed Effects Notation

**Firm fixed effects**:
```latex
Y_{i,t} = \alpha + \beta_1 X_{i,t} + \alpha_i + \epsilon_{i,t}
```
- α_i = firm fixed effects

**Time fixed effects**:
```latex
Y_{i,t} = \alpha + \beta_1 X_{i,t} + \alpha_t + \epsilon_{i,t}
```
- α_t = year (or quarter/month) fixed effects

**Two-way fixed effects**:
```latex
Y_{i,t} = \alpha + \beta_1 X_{i,t} + \alpha_i + \alpha_t + \epsilon_{i,t}
```

**Industry × year fixed effects**:
```latex
Y_{i,t} = \alpha + \beta_1 X_{i,t} + \alpha_{j(i),t} + \epsilon_{i,t}
```
- α_{j(i),t} = industry j × year t fixed effects

### Table Reporting

**Fixed effects rows**:
```latex
\midrule
Property FE & No & No & Yes & Yes \\
Year FE & No & Yes & No & Yes \\
MSA×Year FE & No & No & No & Yes \\
```

**Alternative notation**:
```latex
\midrule
Fixed Effects: & & & & \\
\quad Property & & & \checkmark & \checkmark \\
\quad Year & & \checkmark & & \checkmark \\
\quad MSA×Year & & & & \checkmark \\
```

### Absorbed Fixed Effects

**When fixed effects are absorbed (not reported)**:

Table notes:
```
All regressions include property and year fixed effects.
```

Or in specification row:
```latex
FE: Property, Year & Yes & Yes & Yes & Yes \\
```

## Model Specification Reporting

### Progressive Specification Tables

**Column structure** (common pattern):
1. Baseline: Treatment only
2. + Basic controls
3. + Property fixed effects
4. + Time fixed effects
5. + Industry×Time fixed effects

**Example table header**:
```latex
& (1) & (2) & (3) & (4) & (5) \\
& Baseline & + Controls & + Property FE & + Year FE & Full Spec \\
```

### Control Variables

**Grouped reporting**:
```latex
\midrule
Property Controls & No & Yes & Yes & Yes & Yes \\
Market Controls & No & No & Yes & Yes & Yes \\
```

**Detailed reporting** (if space allows):
```latex
Building Size & & 0.023*** & 0.018** & 0.015** \\
& & (0.006) & (0.007) & (0.007) \\
Property Age & & -0.012* & -0.009 & -0.008 \\
& & (0.007) & (0.008) & (0.008) \\
```

### Diagnostics

**Essential diagnostics**:
```latex
\midrule
Observations & 45,281 & 45,281 & 45,281 & 45,281 \\
R-squared & 0.124 & 0.287 & 0.534 & 0.612 \\
Adjusted R-squared & 0.123 & 0.285 & 0.498 & 0.576 \\
```

**Optional diagnostics** (if relevant):
```latex
F-statistic & 145.3 & 98.7 & & \\
Prob > F & 0.000 & 0.000 & & \\
First-stage F & & & 23.4 & 28.9 \\
```

## Economic Magnitude Interpretation

### Standard Deviation Changes

**Template**:
```
A one standard deviation increase in X (σ_X = [value]) increases Y by [β × σ_X] units, representing [interpretation].
```

**Example**:
```
A one standard deviation increase in AI adoption (0.42) increases accuracy by 5.2 percentage points (0.123 × 0.42), representing 0.8 standard deviations of the outcome.
```

### Percentage of Mean/Median

**Template**:
```
The [magnitude] effect represents [X]% of the mean (median) [outcome].
```

**Example**:
```
The 12.3 percentage point increase represents a 20% improvement over the mean baseline accuracy of 60%.
```

### Dollar Magnitudes

**Template**:
```
For the median property valued at $[value], this translates to $[dollar amount].
```

**Example**:
```
For the median property valued at $25 million, the 1.5% price increase translates to $375,000.
```

### Comparison to Benchmark

**Template**:
```
This effect is [larger/smaller] than [comparison benchmark].
```

**Example**:
```
This 12% effect is comparable to the 15% effect documented by \citet{smith2020} for residential properties but larger than the 8% effect found by \citet{jones2021} for industrial properties.
```

## Regression Table Structure

### Complete Table Template

```latex
\begin{table}[ht!]
\centering
\caption{Effect of AI Adoption on Property Valuation Accuracy}
\label{tab:main}
\footnotesize
\begin{tabular}{lccccc}
\toprule
& (1) & (2) & (3) & (4) & (5) \\
& Baseline & + Controls & + Property FE & + Year FE & Full Spec \\
\midrule
AI Adoption & 0.123*** & 0.118*** & 0.105*** & 0.097*** & 0.091*** \\
& (0.028) & (0.026) & (0.024) & (0.023) & (0.022) \\
\\
Building Size & & 0.023*** & 0.018** & 0.015** & 0.013* \\
& & (0.006) & (0.007) & (0.007) & (0.007) \\
\\
Property Age & & -0.012* & -0.009 & -0.008 & -0.007 \\
& & (0.007) & (0.008) & (0.008) & (0.008) \\
\midrule
Property FE & No & No & Yes & Yes & Yes \\
Year FE & No & No & No & Yes & Yes \\
MSA×Year FE & No & No & No & No & Yes \\
\midrule
Observations & 45,281 & 45,281 & 45,281 & 45,281 & 45,281 \\
R-squared & 0.124 & 0.287 & 0.534 & 0.612 & 0.658 \\
\bottomrule
\end{tabular}
\medskip
\parbox{\linewidth}{\footnotesize
\textit{Notes}: This table reports OLS estimates of the effect of AI adoption on property valuation accuracy.
The dependent variable is Accuracy, measured as 1 - |forecasted price - actual price| / actual price, ranging from 0 to 1.
AI Adoption is an indicator equal to 1 if the property was valued using AI models, 0 otherwise.
Building Size is log of square footage. Property Age is years since construction.
All regressions include the full set of property characteristic controls listed in Table 1.
Standard errors (in parentheses) are clustered at the MSA level.
*** p<0.01, ** p<0.05, * p<0.10.
}
\end{table}
```

### Panel Regression Notation

**Standard panel specification**:
```latex
\begin{equation}
Y_{i,t} = \alpha + \beta_1 X_{i,t} + \gamma Z_{i,t} + \alpha_i + \alpha_t + \epsilon_{i,t}
\end{equation}
where i indexes properties, t indexes time periods, α_i are property fixed effects, α_t are year fixed effects, and ε_{i,t} is the error term.
```

### Subscript Conventions

**Common subscripts**:
- i: individual unit (firm, property, person)
- t: time (year, quarter, month)
- j: group (industry, MSA, category)
- m: market

**Example**:
```latex
Y_{i,m,t} = outcome for property i in market m at time t
```

## Special Reporting Cases

### Instrumental Variables

**First-stage reporting**:
```latex
\midrule
First-stage F-statistic & & & 23.4 & 28.9 \\
```

**Table notes**:
```
Columns (3)-(4) report 2SLS estimates with [instrument] as the instrument for [endogenous variable].
First-stage F-statistics exceed 10, indicating strong instruments.
```

### Event Study

**Coefficient plot**: Include figure showing pre/post coefficients with confidence intervals

**Table alternative**: Report coefficients for relative time periods

```latex
& Coefficient & SE \\
\midrule
Event Time -4 & -0.012 & (0.018) \\
Event Time -3 & -0.008 & (0.015) \\
Event Time -2 & -0.003 & (0.014) \\
Event Time -1 & 0.000 & [omitted] \\
Event Time 0 & 0.087*** & (0.019) \\
Event Time +1 & 0.094*** & (0.021) \\
```

### Quantile Regression

**Multiple quantiles**:
```latex
& (1) & (2) & (3) & (4) & (5) \\
& Q10 & Q25 & Q50 & Q75 & Q90 \\
\midrule
AI Adoption & 0.045* & 0.078*** & 0.123*** & 0.156*** & 0.187*** \\
& (0.024) & (0.021) & (0.028) & (0.032) & (0.041) \\
```

**Interpretation**:
```
Effects are larger at higher quantiles, indicating that AI disproportionately benefits properties with already-high accuracy.
```

## Quality Checklist

Before finalizing tables, verify:

- [ ] All coefficients have standard errors in parentheses
- [ ] Significance stars follow standard convention (***/***)
- [ ] Table notes explain all variables and methods
- [ ] Fixed effects clearly indicated
- [ ] Clustering level specified
- [ ] Sample size (N) reported
- [ ] R-squared reported (if applicable)
- [ ] Variable names are readable (not code_variable_name)
- [ ] Economic magnitudes interpreted in text
- [ ] Hypothesis-table mapping explicit
