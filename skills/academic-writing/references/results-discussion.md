# Results Discussion Patterns

Table-by-table walkthrough structure for presenting empirical findings in finance, economics, and real estate research.

## Table of Contents
- Core Principle
- Table-Specific Patterns
- Economic Magnitude Interpretation
- Robustness Discussion
- Result Integration Across Tables

## Core Principle

**Results sections follow a progressive structure**: Descriptive statistics → Main results → Robustness → Mechanisms → Heterogeneity

Each table requires:
1. Setup (what this table shows)
2. Coefficient interpretation (statistical + economic significance)
3. Cross-reference to hypotheses
4. Comparison to prior literature (where relevant)

---

## Table 1: Summary Statistics

### Standard Discussion Pattern

```latex
Table \ref{tab:summary_statistics} presents descriptive statistics for all variables
used in the analysis. The sample consists of N observations of M unique properties
from [START_YEAR] to [END_YEAR].

[Treatment variable interpretation]
The average property in our sample has institutional ownership in X\% of property-years,
increasing from Y\% in [START] to Z\% in [END]. This growth reflects broader
institutionalization trends documented in [cite: related literature].

[Outcome variables]
Mean property values are \$A (median: \$B), with substantial variation (SD = \$C).
Occupancy rates average D\%, consistent with market-wide benchmarks from [source].

[Control variables highlight]
Properties average E years old and F square feet. The distribution of property types
(G\% office, H\% retail, I\% industrial) matches metropolitan area composition,
suggesting our sample is representative.

[Cross-sectional patterns]
Institutional-owned properties are larger (mean: X vs. Y sq ft, t-stat = Z.ZZ),
located in larger markets, and have higher initial valuations—motivating our
fixed effects approach to address selection bias.
```

**Key elements**:
- **Sample description**: N obs, M units, time period
- **Treatment prevalence**: How common is the treatment?
- **Outcome summary**: Levels, variation, validation against benchmarks
- **Selection patterns**: Observable differences justifying empirical strategy

---

## Table 2: Main Results

### Progressive Specification Pattern

Most empirical papers show 3-6 columns with progressively richer specifications:
- **Column 1**: Baseline (treatment only + FE)
- **Column 2-3**: Add controls in stages
- **Column 4-6**: Alternative outcomes or sample restrictions

### Discussion Template

```latex
Table \ref{tab:main_results} presents our main findings examining the effect of
institutional ownership on property values.

[Baseline specification - Column 1]
Column (1) shows the baseline specification including only property and market×year
fixed effects. The coefficient on Institutional Owner is 0.XXX (SE = 0.YYY, p < 0.01),
indicating that institutional ownership increases property values by approximately X\%.

[Interpreting economic magnitude]
To interpret the economic magnitude: for the average property valued at \$M, this
represents a \$N increase, economically meaningful and consistent with the cost of
professional management upgrades documented in [cite: related work].

[Adding controls - Columns 2-3]
Columns (2) and (3) add property-level controls (age, size, renovations) and
market-level controls (vacancy rates, rental growth). The treatment effect remains
stable at 0.XXX-0.XXX across specifications, suggesting our baseline result is not
driven by omitted variables correlated with both institutional ownership and property
characteristics.

[Statistical comparison]
The consistency of coefficients across columns (0.XXX to 0.XXX, within 1 standard error)
indicates robustness to control variable inclusion. F-tests reject equality with Column 1
only for Column 3 (p = 0.XX), reflecting the additional market controls.

[Alternative outcomes - Columns 4-6]
Columns (4)-(6) examine alternative outcome measures: occupancy rates (Column 4),
rental income (Column 5), and capital expenditures (Column 6). Institutional ownership
increases occupancy by Y percentage points, rental income by Z\%, and capital spending
by W\%, consistent with active property management.

[Hypothesis testing]
These findings support Hypothesis 1 that institutional ownership increases property
values. The positive effects on occupancy and capital spending (Columns 4 and 6) suggest
operational improvements as the underlying mechanism, a question we explore further in
Table [X].
```

**Key principles**:
- **Report magnitudes**: "0.XXX coefficient = X% effect = \$Y increase"
- **Stability across specs**: "Coefficient remains 0.XXX-0.YYY across Columns 1-3"
- **Statistical comparison**: Use standard errors to assess differences
- **Hypothesis mapping**: "This supports H1..."

---

## Coefficient Interpretation Framework

### From Coefficients to Economic Magnitudes

**Log-level specification**: `log(Y) ~ Treatment`
```
Coefficient = 0.15 → Y increases by ~15% when Treatment = 1
Economic magnitude: 15% × \$1M avg = \$150K
```

**Log-log specification**: `log(Y) ~ log(X)`
```
Coefficient = 0.80 → 1% increase in X → 0.80% increase in Y (elasticity)
```

**Level-level specification**: `Y ~ Treatment`
```
Coefficient = 50,000 → Y increases by \$50K when Treatment = 1
```

**Interaction specification**: `Y ~ Treatment + Moderator + Treatment × Moderator`
```
β₁ = baseline effect for Moderator = 0
β₃ = differential effect when Moderator = 1
Total effect when Moderator = 1: β₁ + β₃
```

### Standard Deviation Interpretation

Always provide SD-based interpretation:
```latex
The coefficient of 0.XXX indicates that a one-standard-deviation increase in
[Treatment Variable] (SD = Y.YY, see Table 1) increases [Outcome] by Z\%.
This compares to a sample standard deviation in [Outcome] of W\%, representing
a Z/W = Q standard deviation increase.
```

### Statistical vs. Economic Significance

**Report both**:
```latex
The coefficient is statistically significant at the 1\% level (p < 0.01) and
economically meaningful: a \$M increase represents N\% of average property value,
comparable in magnitude to [benchmark: e.g., "a full property renovation cycle"].
```

---

## Table 3: Heterogeneity Analysis

### Interaction Model Discussion

```latex
Table \ref{tab:heterogeneity} examines whether the treatment effect varies by
[Moderator Variable], testing Hypothesis 2 that effects should be stronger for
[Group A] than [Group B].

[Baseline effect]
Column (1) replicates the main result (Table 2, Column 3) for comparison. The
coefficient of 0.XXX represents the average treatment effect across all properties.

[Interaction specification]
Column (2) adds the interaction term [Treatment] × [Moderator]. The coefficient
on the interaction (β₃ = 0.YYY, p < 0.05) indicates that the treatment effect is
Y.Y percentage points larger for [high moderator group] than [low moderator group].

[Interpreting interaction]
For [low moderator properties], the treatment effect is β₁ = 0.XXX (t-stat = Z.ZZ).
For [high moderator properties], the total effect is β₁ + β₃ = 0.XXX + 0.YYY = 0.WWW
(F-test for β₁ + β₃: p < 0.01). This represents a VV\% stronger effect for [high group],
economically meaningful and consistent with [theoretical mechanism].

[Alternative moderators - Columns 3-4]
Columns (3) and (4) examine alternative moderators: [Moderator 2] and [Moderator 3].
We find [describe pattern]. The differential effects support the interpretation that
[mechanism explanation].

[Cross-sectional heterogeneity interpretation]
These patterns are consistent with [theoretical prediction]. Properties where
[condition] benefit most from institutional ownership, supporting the view that
[mechanism] drives value creation.
```

**Key elements**:
- **Separate main effect and interaction**: β₁ vs. β₃
- **Compute total effects**: β₁ + β₃ for high group
- **Economic interpretation**: "XX% stronger effect"
- **Mechanism connection**: Link heterogeneity to theory

---

## Table 4: Robustness Checks

### Robustness Check Pattern

```latex
Table \ref{tab:robustness} presents robustness checks verifying the stability of
our main finding (Table 2, Column 3, reproduced in Column 1 for comparison).

[Alternative specifications]
Column (2) uses [alternative specification: e.g., continuous treatment intensity
instead of binary indicator]. The coefficient of 0.XXX indicates that each percentage
point increase in institutional ownership share raises values by X\%, consistent with
the YY\% effect for full institutional ownership in Column (1).

Column (3) restricts the sample to [restriction: e.g., large properties, core markets,
pre-2015 period]. The coefficient remains positive and significant (0.XXX, p < 0.01),
suggesting the main result is not driven by [potential concern].

[Alternative clustering]
Column (4) clusters standard errors at the [alternative level] instead of property level.
The coefficient magnitude is unchanged (0.XXX vs. 0.YYY in Column 1), though standard
errors [increase/decrease] slightly, reflecting [interpretation: e.g., "cross-sectional
correlation within markets"].

[Additional fixed effects]
Column (5) includes [additional FE: e.g., property×year FE or industry-specific time
trends]. While the specification is demanding, the coefficient remains positive and
marginally significant (0.XXX, p < 0.10), consistent with the main result.

[Falsification tests - Column 6]
Column (6) presents a placebo test using [placebo outcome that should NOT respond].
The coefficient is small and insignificant (0.0XX, p = 0.YY), supporting the validity
of our identification strategy.

[Overall assessment]
Across specifications, the treatment effect ranges from 0.XXX to 0.YYY (mean = 0.ZZZ,
SD = 0.WWW), demonstrating robustness to alternative modeling choices. The consistency
strengthens confidence in the main finding.
```

**Key principles**:
- **Always reproduce baseline**: Column 1 for comparison
- **Range of estimates**: "Effects range from X to Y"
- **Explain deviations**: Why do estimates differ across specs?
- **Placebo tests**: Show null results where expected

---

## Mechanism Tables (Table 5+)

### Mechanism Testing Discussion

```latex
Having established that institutional ownership increases property values (Table 2),
we investigate the mechanisms driving this effect.

Table \ref{tab:mechanisms} examines potential channels: operational improvements
(Columns 1-2), capital investment (Columns 3-4), and tenant composition (Columns 5-6).

[Operational channel]
Columns (1) and (2) show that institutional ownership increases occupancy rates by
X percentage points (p < 0.01) and reduces tenant turnover by Y\% (p < 0.05). These
operational improvements likely contribute to higher valuations through stable cash flows.

[Capital investment channel]
Columns (3) and (4) reveal that institutions invest \$Z more per square foot annually
(p < 0.01) and are W percentage points more likely to undertake major renovations.
This active capital management may explain value creation through physical improvements.

[Tenant quality channel]
Columns (5) and (6) examine tenant characteristics. Institutional-owned properties
attract tenants with longer lease terms (A months longer, p < 0.01) and higher
credit ratings (B points higher, p < 0.05), reducing cash flow risk and justifying
valuation premiums.

[Mechanism summary]
Collectively, these findings suggest institutional ownership creates value through
multiple channels: better operational management (Columns 1-2), strategic capital
investment (Columns 3-4), and improved tenant selection (Columns 5-6). All three
mechanisms are active, consistent with the multifaceted expertise institutions bring
to property management.
```

---

## Common Patterns and Phrases

### Reporting Significance Levels

```latex
% Standard reporting
The coefficient is significant at the 1\% level (p < 0.01)
The effect is marginally significant (p < 0.10)
The difference is not statistically significant (p = 0.XX)

% Comparing across columns
The coefficients in Columns 1 and 2 are not statistically distinguishable
(F-test: p = 0.XX)

% Economic vs statistical significance
While statistically significant (p < 0.05), the economic magnitude is small,
representing only X\% of the outcome standard deviation
```

### Comparing to Prior Literature

```latex
This XX\% effect is comparable in magnitude to \citet{author2020}, who find
YY\% effects in a similar setting

Our estimate of ZZ\% is larger than \citet{author2019}'s WW\%, likely due to
[difference in sample, time period, or methodology]

This finding extends \citet{author2021} by showing that [contribution]
```

### Transitioning Between Tables

```latex
% Moving to next table
Having established [key finding from Table X], we now examine [research question
for Table Y] in Table \ref{tab:Y}

% Building on previous results
Table \ref{tab:robustness} builds on the main finding (Table 2) by testing...

% Summarizing multiple tables
Tables 2-4 consistently show that [pattern], demonstrating robustness across
[dimensions]
```

---

## Checklist for Results Discussion

- [ ] Each table has clear setup statement
- [ ] All coefficients interpreted (magnitude + significance)
- [ ] Economic magnitudes computed (% effects, \$ amounts)
- [ ] Standard deviation interpretations provided
- [ ] Cross-column comparisons explained
- [ ] Hypotheses explicitly tested and mapped to results
- [ ] Comparisons to prior literature (where relevant)
- [ ] Robustness range documented
- [ ] Mechanisms linked to theory
- [ ] One sentence per line (for git diffs)
- [ ] All cross-references verified (`\ref{tab:X}` exists)
