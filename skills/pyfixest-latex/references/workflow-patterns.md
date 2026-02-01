# Workflow Patterns for Academic Research

Proven patterns extracted from production research code for robust, reproducible econometric analysis.

## Table of Contents
- [UTF-8 Encoding Configuration](#utf-8-encoding-configuration)
- [Project Root Detection](#project-root-detection)
- [Data Loading & Cleaning](#data-loading--cleaning)
- [Sequential Time Variables](#sequential-time-variables)
- [Treatment Variable Construction](#treatment-variable-construction)
- [Analysis Workflow](#analysis-workflow)
- [Complete Example Structure](#complete-example-structure)

---

## UTF-8 Encoding Configuration

**Problem**: Windows PowerShell defaults to non-UTF-8 encoding, causing issues with mathematical symbols in LaTeX output.

**Solution**: Configure UTF-8 at script start (before any imports that produce output).

```python
"""
UTF-8 Encoding Configuration - Place at top of script
=====================================================
Ensures Windows PowerShell compatibility for LaTeX symbols
"""
import sys
import io
import os

# Windows-specific UTF-8 configuration
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # Fallback if buffer doesn't exist

    # Set environment variable for subprocess calls
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Set pandas to use UTF-8
import pandas as pd
pd.options.display.encoding = 'utf-8'
```

**When to use**: Always include this at the top of analysis scripts that generate LaTeX output.

---

## Project Root Detection

**Problem**: Scripts need to find project-level configuration (`config_paths.py`) regardless of where they're located in the directory tree.

**Solution**: Search parent directories automatically.

```python
"""
Project Path Auto-Detection
============================
Searches up to 5 parent directories for config_paths.py
"""
from pathlib import Path
import sys

# Search parent directories for config file
for p in Path(__file__).resolve().parents[:5]:
    if (p / 'config_paths.py').exists():
        sys.path.insert(0, str(p))
        break

# Now import from project root
import config_paths
from config_paths import DATA_DIR, RESULTS_DIR, TABLES_DIR, FIGURES_DIR

# Configure output paths for pyfixest_latex
from pyfixest_latex import set_output_path, set_figure_output_path
set_output_path(str(TABLES_DIR))
set_figure_output_path(str(FIGURES_DIR))
```

**Alternative (Standalone Project)**: If not using centralized config:

```python
from pathlib import Path
from pyfixest_latex import set_output_path, set_figure_output_path

# Define paths relative to script location
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent  # Or adjust as needed

# Configure output paths
set_output_path(str(PROJECT_ROOT / "Results" / "Tables"))
set_figure_output_path(str(PROJECT_ROOT / "Results" / "Figures"))
```

---

## Data Loading & Cleaning

**Pattern**: Clean data upfront, handle edge cases systematically.

```python
def load_and_prepare_data(data_path: str) -> pd.DataFrame:
    """
    Load and clean panel data with robust error handling.

    Returns clean dataset ready for econometric analysis.
    """
    print(f"\n[LOAD] Loading data from {data_path}...")
    df = pd.read_parquet(data_path)
    print(f"   [OK] Loaded: {df.shape[0]:,} observations × {df.shape[1]} variables")

    # 1. Replace infinite values with NaN
    df = df.replace([np.inf, -np.inf], np.nan)

    # 2. Drop rows with missing values in analysis variables
    analysis_vars = ['outcome', 'treatment', 'control1', 'control2', 'unit_id', 'time_id']
    initial_count = len(df)
    df = df.dropna(subset=analysis_vars).copy()
    dropped = initial_count - len(df)

    if dropped > 0:
        print(f"   [CLEAN] Dropped {dropped:,} observations with missing values")
        print(f"   Retention rate: {len(df)/initial_count*100:.1f}%")

    # 3. Ensure correct data types
    df['unit_id'] = df['unit_id'].astype(str)
    df['time_id'] = df['time_id'].astype(int)
    df['treatment'] = df['treatment'].astype(int)

    # 4. Sort by unit and time (important for panel structure)
    df = df.sort_values(['unit_id', 'time_id']).reset_index(drop=True)

    print(f"   [OK] Clean dataset: {len(df):,} observations")
    print(f"   Units: {df['unit_id'].nunique():,}, Time periods: {df['time_id'].nunique()}")

    return df
```

**Key principles**:
- Handle `inf` values before dropping NaN
- Report data loss transparently
- Ensure proper data types for categorical/numeric variables
- Sort panel data for consistency

---

## Sequential Time Variables

**Problem**: Event study plots need sequential time (1, 2, 3...) but data often uses year-quarter format (20191, 20192, etc.).

**Solution**: Create mapping to sequential time while preserving original for fixed effects.

```python
def create_sequential_time_variable(
    df: pd.DataFrame,
    time_var: str = 'year_quarter_numeric',
    new_var: str = 'quarter_seq'
) -> pd.DataFrame:
    """
    Create sequential time variable from non-sequential periods.

    Example: {20191: 1, 20192: 2, 20193: 3, 20194: 4, 20201: 5, ...}
    """
    # Get sorted unique time periods
    unique_periods = sorted(df[time_var].unique())

    # Create mapping: original period → sequential number
    period_mapping = {period: i+1 for i, period in enumerate(unique_periods)}

    # Apply mapping
    df = df.assign(**{new_var: df[time_var].map(period_mapping)})

    print(f"\n[PREP] Created sequential time variable: {new_var}")
    print(f"   Mapping: {time_var} → {new_var}")
    print(f"   Example: {list(period_mapping.items())[:5]}")
    print(f"   Total periods: {len(unique_periods)}")

    return df, period_mapping
```

**Usage in event study**:

```python
# Use sequential time in dynamic effects specification
dynamic_model = pf.feols(
    f"Y ~ i({sequential_time}, treatment_group, ref={ref_seq}) | unit_id + {original_time}",
    data,
    vcov={"CRV1": "unit_id"}
)
```

---

## Treatment Variable Construction

**Pattern**: Create treatment variables systematically with clear definitions.

```python
# Configuration (at script top)
TREATMENT_YEAR_QUARTER = 20201  # 2020 Q1
TREATED_SIC_CODES = ['6798']    # REITs

def create_treatment_variables(
    df: pd.DataFrame,
    time_var: str,
    classification_var: str,
    treatment_time: int,
    treated_values: list
) -> pd.DataFrame:
    """
    Create DiD treatment variables: post, treated, did.

    Returns DataFrame with three new columns:
    - post_treatment: 1 if time >= treatment_time
    - treated: 1 if classification_var in treated_values
    - did: post_treatment × treated
    """
    df = df.assign(**{
        'post_treatment': (df[time_var] >= treatment_time).astype(int),
        'treated': df[classification_var].isin(treated_values).astype(int)
    })
    df['did'] = df['post_treatment'] * df['treated']

    print(f"\n[TREATMENT] Created DiD variables:")
    print(f"   Post-treatment obs: {df['post_treatment'].sum():,} ({df['post_treatment'].mean()*100:.1f}%)")
    print(f"   Treated units: {df[df['treated']==1]['unit_id'].nunique():,}")
    print(f"   Control units: {df[df['treated']==0]['unit_id'].nunique():,}")
    print(f"   DiD treated obs: {df['did'].sum():,} ({df['did'].mean()*100:.1f}%)")

    return df
```

---

## Analysis Workflow

**Pattern**: Modular functions for each analysis component.

```python
def run_main_analysis(df: pd.DataFrame):
    """Standard DiD regression analysis."""
    models = [
        pf.feols("Y ~ did | unit + time", df, vcov={"CRV1": "unit"}),
        pf.feols("Y ~ did + controls | unit + time", df, vcov={"CRV1": "unit"})
    ]

    create_regression_table(
        models=models,
        model_names=["Basic", "With Controls"],
        title="Treatment Effects on Outcome",
        label="tab:main",
        variable_labels={'did': 'Treatment × Post'},
        felabels={'unit': 'Unit FE', 'time': 'Time FE'}
    )

def run_event_study(df: pd.DataFrame, ref_period: int, treatment_period: int):
    """Dynamic effects analysis."""
    dynamic = pf.feols(
        f"Y ~ i(quarter_seq, treated, ref={ref_period}) | unit + time",
        df, vcov={"CRV1": "unit"}
    )

    # Table
    create_dynamic_table(
        models=dynamic,
        title="Dynamic Treatment Effects",
        label="tab:event_study",
        time_var="quarter_seq",
        treat_var="treated",
        reference_period=ref_period,
        treatment_period=treatment_period
    )

    # Figure
    create_event_study_plot(
        model=dynamic,
        reference_period=ref_period,
        treatment_period=treatment_period,
        time_var="quarter_seq",
        treat_var="treated",
        style="filled"
    )

def run_robustness_checks(df: pd.DataFrame):
    """Specification sensitivity analysis."""
    main = [pf.feols("Y ~ did | unit + time", df, vcov={"CRV1": "unit"})]
    robust = [
        pf.feols("Y ~ did | unit + time", df, vcov="hetero"),
        pf.feols("Y_alt ~ did | unit + time", df, vcov={"CRV1": "unit"})
    ]

    create_robustness_table(
        model_groups=[main, robust],
        group_names=["Main", "Robustness"],
        title="Specification Sensitivity",
        label="tab:robustness"
    )

def generate_summary_statistics(df: pd.DataFrame, variables: list):
    """Descriptive statistics table."""
    create_summary_statistics_table(
        data=df,
        variables=variables,
        variable_labels={var: f"Label for {var}" for var in variables},
        title="Summary Statistics",
        label="tab:summary"
    )
```

---

## Complete Example Structure

```python
#!/usr/bin/env python3
"""
Academic Research Analysis Template
====================================
Complete workflow: Load → Clean → Analyze → Generate Outputs
"""

# 1. UTF-8 encoding configuration (Windows compatibility)
import sys, io, os
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 2. Standard imports
import pandas as pd
import numpy as np
import pyfixest as pf
from pathlib import Path

# 3. Project path configuration
from config_paths import TABLES_DIR, FIGURES_DIR, DATA_DIR
from pyfixest_latex import (
    create_regression_table, create_dynamic_table, create_event_study_plot,
    create_summary_statistics_table, set_output_path, set_figure_output_path
)

set_output_path(str(TABLES_DIR))
set_figure_output_path(str(FIGURES_DIR))

# 4. Configuration constants
DATA_PATH = DATA_DIR / 'final_data.parquet'
TREATMENT_TIME = 20201
TREATED_VALUES = ['6798']

# 5. Helper functions
def load_and_prepare_data(): ...
def create_treatment_variables(): ...
def run_main_analysis(): ...
def run_event_study(): ...

# 6. Main execution
def main():
    """Execute complete analysis pipeline."""
    print("\n" + "="*80)
    print("STARTING ANALYSIS PIPELINE")
    print("="*80)

    # Load and clean data
    df = load_and_prepare_data()
    df = create_treatment_variables(df)

    # Generate outputs
    generate_summary_statistics(df)
    run_main_analysis(df)
    run_event_study(df)
    run_robustness_checks(df)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nTables: {TABLES_DIR}")
    print(f"Figures: {FIGURES_DIR}")

if __name__ == "__main__":
    main()
```

**Key organizational principles**:
1. UTF-8 config first (before pandas import)
2. Group imports logically
3. Define configuration constants
4. Modular helper functions
5. Clear main() orchestration
6. Informative console output

---

## Best Practices Summary

1. **Always configure UTF-8 on Windows** - prevents LaTeX symbol encoding issues
2. **Use project root detection** - makes scripts portable across directory structures
3. **Clean data upfront** - handle inf/NaN systematically before analysis
4. **Create sequential time for event studies** - while preserving original for FE
5. **Modular analysis functions** - one function per table/figure type
6. **Informative console output** - report data loss, sample sizes, diagnostics
7. **Clear variable naming** - `post_treatment`, `treated`, `did` are self-documenting
8. **Sort panel data** - ensures consistent ordering for merges and visualizations
