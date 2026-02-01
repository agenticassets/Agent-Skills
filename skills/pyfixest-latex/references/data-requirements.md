# Data Requirements

Expected DataFrame structure and data preparation guidelines for using pyfixest_latex.

## Table of Contents
- [Minimum Requirements](#minimum-requirements)
- [Panel Data Structure](#panel-data-structure)
- [Variable Types](#variable-types)
- [Treatment Variables for DiD](#treatment-variables-for-did)
- [Data Quality Checks](#data-quality-checks)
- [Common Data Issues](#common-data-issues)

---

## Minimum Requirements

### For Regression Tables

**Required columns**:
- Outcome variable(s): numeric, continuous
- Treatment/independent variables: numeric
- Unit identifier: str or int (for fixed effects)
- Time identifier: int or datetime (for fixed effects)

**Example**:
```python
# Minimal DiD panel data
df = pd.DataFrame({
    'unit_id': [1, 1, 2, 2, 3, 3],
    'time': [2019, 2020, 2019, 2020, 2019, 2020],
    'outcome': [5.2, 6.1, 4.8, 5.5, 6.0, 7.2],
    'treatment': [0, 1, 0, 1, 0, 0]
})
```

### For Event Study Tables/Plots

**Additional requirements**:
- Sequential time variable: int (1, 2, 3, ...) for dynamic effects
- Treatment group indicator: int (0/1)
- Reference period defined in model formula

**Example**:
```python
df = pd.DataFrame({
    'unit_id': [1, 1, 1, 2, 2, 2],
    'time_original': [2019, 2020, 2021, 2019, 2020, 2021],
    'time_seq': [1, 2, 3, 1, 2, 3],  # Sequential time
    'treated_group': [1, 1, 1, 0, 0, 0],  # Treatment group indicator
    'outcome': [5.0, 5.5, 6.2, 4.8, 4.9, 5.1]
})
```

### For Summary Statistics

**Required**:
- Variables to summarize: numeric columns
- No missing identifiers required (operates on full DataFrame)

---

## Panel Data Structure

### Balanced vs Unbalanced Panels

**Balanced panel** (preferred but not required):
- Same number of observations per unit
- No gaps in time periods
- Simplifies interpretation

```python
# Check if balanced
units_per_time = df.groupby('time').size()
is_balanced = units_per_time.nunique() == 1
print(f"Balanced panel: {is_balanced}")
```

**Unbalanced panel** (still works):
- Different observation counts per unit
- May have gaps in coverage
- PyFixest handles automatically

### Sort Order

**Best practice**: Sort by unit → time before analysis

```python
df = df.sort_values(['unit_id', 'time']).reset_index(drop=True)
```

Why: Ensures consistent ordering for:
- Lag/lead variable creation
- Plotting treatment assignment heatmaps
- Debugging panel structure

---

## Variable Types

### Unit Identifiers

**Acceptable types**:
```python
# String identifiers
df['firm_id'] = ['AAPL', 'MSFT', 'GOOG', ...]

# Integer identifiers
df['gvkey'] = [1004, 1045, 1078, ...]

# Categorical
df['unit_id'] = pd.Categorical(['A', 'B', 'C', ...])
```

**Recommendations**:
- Use strings for readability in diagnostics
- Convert to categorical if many unique values (memory efficiency)
- Ensure no missing values in identifier columns

### Time Variables

**For Fixed Effects** (original time periods):
```python
# Year-quarter (numeric)
df['year_quarter'] = [20191, 20192, 20193, 20194, 20201, ...]

# Year-month (datetime)
df['year_month'] = pd.to_datetime(['2019-01', '2019-02', ...])

# Year (integer)
df['year'] = [2019, 2020, 2021, ...]
```

**For Dynamic Effects** (sequential time):
```python
# Must be consecutive integers starting from 1
df['time_seq'] = [1, 2, 3, 4, 5, 6, ...]  # No gaps allowed

# Create from original periods:
unique_periods = sorted(df['year_quarter'].unique())
period_map = {period: i+1 for i, period in enumerate(unique_periods)}
df['time_seq'] = df['year_quarter'].map(period_map)
```

### Outcome Variables

**Type**: Numeric (int or float)

**Range**: Any, but consider:
- Log transformations for skewed distributions
- Winsorization for extreme outliers
- Standardization if comparing effect magnitudes

```python
# Example preprocessing
df['log_assets'] = np.log(df['total_assets'])
df['outcome_winsorized'] = df['outcome'].clip(
    lower=df['outcome'].quantile(0.01),
    upper=df['outcome'].quantile(0.99)
)
```

### Treatment Variables

**Type**: Numeric (0/1 or continuous)

**For DiD**:
```python
df['post'] = (df['time'] >= treatment_time).astype(int)
df['treated'] = df['group'].isin(treated_groups).astype(int)
df['did'] = df['post'] * df['treated']
```

**For continuous treatment**:
```python
# Dose-response: treatment intensity
df['treatment_intensity'] = [0, 0.5, 1.0, 1.5, ...]
```

---

## Treatment Variables for DiD

### Standard DiD Setup

**Three variables required**:
1. `post`: Time dimension (0 before, 1 after treatment)
2. `treated`: Unit dimension (1 if ever treated, 0 if never treated)
3. `did`: Interaction (post × treated)

**Example construction**:
```python
TREATMENT_TIME = 2020  # Treatment starts in 2020
TREATED_UNITS = ['A', 'B', 'C']  # Units that receive treatment

df['post'] = (df['year'] >= TREATMENT_TIME).astype(int)
df['treated'] = df['unit_id'].isin(TREATED_UNITS).astype(int)
df['did'] = df['post'] * df['treated']
```

### Staggered Adoption

**For units treated at different times**:
```python
# Define treatment timing per unit
treatment_map = {'A': 2019, 'B': 2020, 'C': 2021, 'D': np.nan}  # D never treated

df['treatment_year'] = df['unit_id'].map(treatment_map)
df['post'] = (df['year'] >= df['treatment_year']).astype(int)
df['treated'] = df['treatment_year'].notna().astype(int)
```

### Dynamic Treatment Indicator

**For event studies**:
```python
# Treatment group indicator (constant over time)
df['ever_treated'] = df.groupby('unit_id')['treatment'].transform('max')

# Use in formula:
# pf.feols("Y ~ i(time, ever_treated, ref=t0) | unit + time", df)
```

---

## Data Quality Checks

### Pre-Analysis Validation

```python
def validate_panel_data(df, unit_var, time_var, outcome_vars, treatment_vars):
    """
    Comprehensive panel data validation.
    """
    print("=== PANEL DATA VALIDATION ===\n")

    # 1. Check for missing identifiers
    missing_units = df[unit_var].isna().sum()
    missing_time = df[time_var].isna().sum()
    print(f"Missing unit IDs: {missing_units}")
    print(f"Missing time IDs: {missing_time}")

    if missing_units > 0 or missing_time > 0:
        print("⚠️  WARNING: Missing identifiers detected. Remove these rows.\n")

    # 2. Check panel structure
    n_units = df[unit_var].nunique()
    n_periods = df[time_var].nunique()
    n_expected = n_units * n_periods
    n_actual = len(df)

    print(f"\nPanel structure:")
    print(f"  Units: {n_units:,}")
    print(f"  Time periods: {n_periods}")
    print(f"  Expected obs (balanced): {n_expected:,}")
    print(f"  Actual obs: {n_actual:,}")
    print(f"  Balance: {n_actual / n_expected * 100:.1f}%")

    # 3. Check for inf/NaN in analysis variables
    all_vars = outcome_vars + treatment_vars
    for var in all_vars:
        n_missing = df[var].isna().sum()
        n_inf = np.isinf(df[var]).sum()

        if n_missing > 0 or n_inf > 0:
            print(f"\n⚠️  {var}:")
            print(f"    Missing: {n_missing:,} ({n_missing/len(df)*100:.1f}%)")
            print(f"    Infinite: {n_inf:,} ({n_inf/len(df)*100:.1f}%)")

    # 4. Check time variable properties
    periods = sorted(df[time_var].unique())
    gaps = [periods[i+1] - periods[i] for i in range(len(periods)-1)]

    if len(set(gaps)) > 1:
        print(f"\n⚠️  Non-uniform time gaps detected: {set(gaps)}")
        print("    Consider creating sequential time variable for event studies.")

    print("\n=== VALIDATION COMPLETE ===\n")
```

### Example Usage

```python
validate_panel_data(
    df,
    unit_var='gvkey',
    time_var='year_quarter',
    outcome_vars=['roa', 'leverage', 'market_cap'],
    treatment_vars=['post', 'treated', 'did']
)
```

---

## Common Data Issues

### Issue 1: Infinite Values

**Symptom**: Division by zero creates `inf` values

```python
# Problem
df['leverage'] = df['debt'] / df['assets']  # May create inf if assets=0

# Solution
df['leverage'] = np.where(
    df['assets'] > 0,
    df['debt'] / df['assets'],
    np.nan
)
```

**Alternative**: Replace inf before analysis

```python
df = df.replace([np.inf, -np.inf], np.nan)
```

### Issue 2: Non-Sequential Time

**Symptom**: Event study requires consecutive integers but you have year-quarters

```python
# Problem: time variable is [20191, 20192, 20193, 20194, 20201, 20202, ...]
# PyFixest i() function needs [1, 2, 3, 4, 5, 6, ...]

# Solution: Create mapping
unique_periods = sorted(df['year_quarter'].unique())
seq_map = {period: i+1 for i, period in enumerate(unique_periods)}
df['time_seq'] = df['year_quarter'].map(seq_map)
```

### Issue 3: Treatment Leakage

**Symptom**: Treatment variable varies within units over time when it shouldn't

```python
# Check for leakage
leakage = df.groupby('unit_id')['treated'].nunique()
problem_units = leakage[leakage > 1].index.tolist()

if problem_units:
    print(f"⚠️  Treatment varies within units: {problem_units}")

# Solution: Force time-invariant treatment
df['treated'] = df.groupby('unit_id')['treated'].transform('max')
```

### Issue 4: Unbalanced Panels with Gaps

**Symptom**: Missing observations create interpretation issues

```python
# Identify gaps
complete_panel = pd.MultiIndex.from_product(
    [df['unit_id'].unique(), df['time'].unique()],
    names=['unit_id', 'time']
)

actual_panel = df.set_index(['unit_id', 'time']).index
missing_obs = complete_panel.difference(actual_panel)

if len(missing_obs) > 0:
    print(f"Missing observations: {len(missing_obs):,}")

# Solutions:
# 1. Fill forward (if appropriate)
df = df.sort_values(['unit_id', 'time']).groupby('unit_id').ffill()

# 2. Drop units with gaps
min_obs_per_unit = df.groupby('unit_id').size().min()
complete_units = df.groupby('unit_id').filter(lambda x: len(x) == min_obs_per_unit)
```

---

## Quick Checklist

Before running analysis, verify:

- [ ] No missing values in `unit_id` or `time` variables
- [ ] Data sorted by `unit_id` → `time`
- [ ] No `inf` values in outcome/treatment variables
- [ ] Sequential time variable created for event studies (if needed)
- [ ] Treatment variables constructed correctly (post, treated, did)
- [ ] Panel structure validated (expected vs actual observations)
- [ ] Outcome variables have reasonable ranges (consider winsorization)
- [ ] Treatment group is time-invariant (for standard DiD)

**Validation command**:
```python
assert df['unit_id'].notna().all(), "Missing unit IDs"
assert df['time'].notna().all(), "Missing time IDs"
assert not df['outcome'].isin([np.inf, -np.inf]).any(), "Infinite values in outcome"
```
