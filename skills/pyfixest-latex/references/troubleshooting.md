# Troubleshooting Guide for PyFixest-LaTeX

Common issues and solutions when using the pyfixest_latex module for generating publication-quality tables and figures.

## Table of Contents
- [Quick Diagnostics](#quick-diagnostics)
- [Installation & Dependency Issues](#installation--dependency-issues)
- [Path Configuration Errors](#path-configuration-errors)
- [UTF-8 Encoding Issues (Windows)](#utf-8-encoding-issues-windows)
- [Model Fitting Errors](#model-fitting-errors)
- [LaTeX Compilation Issues](#latex-compilation-issues)
- [Data Structure Issues](#data-structure-issues)
- [Import Errors](#import-errors)
- [Output Issues](#output-issues)

---

## Quick Diagnostics

Run this diagnostic script before troubleshooting to identify your environment:

```python
#!/usr/bin/env python3
"""Quick diagnostic check for pyfixest-latex setup."""

import sys
import os
from pathlib import Path

print("=" * 80)
print("PYFIXEST-LATEX DIAGNOSTIC CHECK")
print("=" * 80)

# 1. Python version
print(f"\nPython version: {sys.version}")
print(f"Platform: {sys.platform}")

# 2. Check required packages
packages = ['pyfixest', 'pandas', 'numpy', 'scipy', 'matplotlib']
print("\nDependency check:")
for pkg in packages:
    try:
        mod = __import__(pkg)
        version = getattr(mod, '__version__', 'installed')
        print(f"  ✓ {pkg}: {version}")
    except ImportError:
        print(f"  ✗ {pkg}: NOT INSTALLED")

# 3. Check pyfixest_latex availability
print("\nModule availability:")
try:
    from pyfixest_latex import set_output_path, create_regression_table
    print(f"  ✓ pyfixest_latex: Importable")
except ImportError as e:
    print(f"  ✗ pyfixest_latex: {e}")

# 4. Check output directories
print("\nOutput directories:")
try:
    from pyfixest_latex import get_output_path, get_figure_output_path
    tables_dir = get_output_path()
    figures_dir = get_figure_output_path()
    print(f"  Tables: {tables_dir}")
    print(f"  Figures: {figures_dir}")
    print(f"  Writable: {os.access(str(tables_dir), os.W_OK)}")
except Exception as e:
    print(f"  Error: {e}")

# 5. UTF-8 configuration (Windows)
print(f"\nUTF-8 configuration:")
print(f"  Default encoding: {sys.getdefaultencoding()}")
print(f"  File system encoding: {sys.getfilesystemencoding()}")

print("\n" + "=" * 80)
```

**Run it**:
```bash
python diagnostic.py
```

---

## Installation & Dependency Issues

### Issue 1: ModuleNotFoundError: No module named 'pyfixest'

**Symptom**:
```
ModuleNotFoundError: No module named 'pyfixest'
```

**Cause**: PyFixest not installed or installed in wrong environment

**Solution**:
```bash
# 1. Activate correct virtual environment
.venv\Scripts\Activate.ps1          # Windows
source .venv/bin/activate            # Linux/Mac

# 2. Install PyFixest with econometrics extras
pip install pyfixest[matrix]

# 3. Verify installation
python -c "import pyfixest; print(pyfixest.__version__)"
```

**Advanced**: If using conda:
```bash
conda create -n research python=3.11
conda activate research
conda install pyfixest pandas numpy scipy matplotlib
```

---

### Issue 2: ImportError: cannot import name 'create_regression_table'

**Symptom**:
```
ImportError: cannot import name 'create_regression_table' from 'pyfixest_latex'
```

**Cause**: Module not in Python path or not installed

**Solution**:

**Option A: Copy module to project** (recommended for standalone projects)
```bash
# Navigate to skill directory and run setup
python .claude/skills/pyfixest-latex/scripts/setup_module.py /path/to/project
```

**Option B: Manual path addition** (temporary, for testing)
```python
import sys
from pathlib import Path

# Add module to path
module_path = Path(__file__).parent / ".claude" / "skills" / "pyfixest-latex" / "assets"
sys.path.insert(0, str(module_path))

# Now import works
from pyfixest_latex import create_regression_table
```

**Option C: Install as editable package**
```bash
cd .claude/skills/pyfixest-latex/assets
pip install -e .
```

---

### Issue 3: RuntimeError: ... missing dependencies

**Symptom**:
```
RuntimeError: Missing required packages: matplotlib, scipy
```

**Cause**: Incomplete pip installation

**Solution**:
```bash
# Install all dependencies explicitly
pip install pyfixest pandas numpy scipy matplotlib

# Or use requirements.txt (create in project root)
pip install -r requirements.txt
```

**Sample requirements.txt**:
```
pyfixest>=0.2.0
pandas>=1.5.0
numpy>=1.23.0
scipy>=1.9.0
matplotlib>=3.6.0
```

---

## Path Configuration Errors

### Issue 4: Output files saved to wrong location

**Symptom**: Tables/figures saved to unexpected directory or not saved at all

**Cause**: Output path not configured before generating output

**Solution**: **Always configure paths BEFORE calling generation functions**

```python
from pyfixest_latex import set_output_path, set_figure_output_path, create_regression_table

# 1. Configure paths first
set_output_path("Results/Tables")           # Tables
set_figure_output_path("Results/Figures")   # Figures

# 2. Then generate output
create_regression_table(
    models=[m1, m2],
    model_names=["(1)", "(2)"],
    title="Results",
    label="tab:main"
)
```

**Absolute paths recommended**:
```python
from pathlib import Path

project_root = Path(__file__).parent.parent
tables_dir = project_root / "Results" / "Tables"
figures_dir = project_root / "Results" / "Figures"

set_output_path(str(tables_dir.absolute()))
set_figure_output_path(str(figures_dir.absolute()))
```

---

### Issue 5: FileNotFoundError: [Errno 2] No such file or directory

**Symptom**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'Results/Tables'
```

**Cause**: Output directory doesn't exist and module can't create it

**Solution**:
```python
from pathlib import Path
import os

# Method 1: Module auto-creates directory
from pyfixest_latex import set_output_path
set_output_path("Results/Tables")  # Creates if doesn't exist

# Method 2: Create manually before setting
Path("Results/Tables").mkdir(parents=True, exist_ok=True)
from pyfixest_latex import set_output_path
set_output_path("Results/Tables")

# Method 3: Use absolute path with config_paths
from config_paths import TABLES_DIR
set_output_path(str(TABLES_DIR))  # Assumes config_paths.py creates dirs
```

---

### Issue 6: Relative vs absolute path confusion

**Symptom**: Path works in one script but not another; relative paths behave unexpectedly

**Cause**: Relative paths resolve to current working directory, which varies across scripts

**Solution**:
```python
from pathlib import Path

# Always use absolute paths in production code
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent  # Adjust depth as needed
tables_dir = project_root / "Results" / "Tables"

from pyfixest_latex import set_output_path
set_output_path(str(tables_dir.absolute()))

# Verify it worked
from pyfixest_latex import get_output_path
print(f"Saving tables to: {get_output_path()}")
```

**For centralized projects** (using `config_paths.py`):
```python
import sys
from pathlib import Path

# Auto-detect project root
for p in Path(__file__).resolve().parents[:5]:
    if (p / 'config_paths.py').exists():
        sys.path.insert(0, str(p))
        break

from config_paths import TABLES_DIR, FIGURES_DIR
from pyfixest_latex import set_output_path, set_figure_output_path

set_output_path(str(TABLES_DIR))
set_figure_output_path(str(FIGURES_DIR))
```

---

## UTF-8 Encoding Issues (Windows)

### Issue 7: LaTeX symbols render as garbage characters in figures

**Symptom**:
- Figure titles show `ÃÂ` instead of Greek letters (α, β, etc.)
- Mathematical symbols display incorrectly
- Console output shows encoding warnings

**Cause**: Windows PowerShell defaults to non-UTF-8 encoding

**Solution**: Add UTF-8 configuration at **top of script** (before any imports that produce output)

```python
#!/usr/bin/env python3
"""
UTF-8 Configuration for Windows Compatibility
Place BEFORE all other imports
"""
import sys
import io
import os

# Windows-specific UTF-8 configuration
if sys.platform == 'win32':
    try:
        # Reconfigure stdout/stderr for UTF-8
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # Fallback if buffer doesn't exist

    # Set environment variable for subprocess calls
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Now safe to import pandas and other modules
import pandas as pd
pd.options.display.encoding = 'utf-8'

# Rest of imports...
import pyfixest as pf
from pyfixest_latex import create_event_study_plot
```

**Why this works**:
- `io.TextIOWrapper` replaces stdout/stderr with UTF-8 versions
- `PYTHONIOENCODING` environment variable ensures subprocess compatibility
- pandas display encoding prevents truncation of unicode characters

**Verify it's working**:
```python
import sys
print(f"Encoding: {sys.stdout.encoding}")  # Should show: utf-8
print("Test: α β γ μ σ")  # Should display correctly
```

---

### Issue 8: Matplotlib figure titles show unicode errors

**Symptom**:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte...
```
when saving figures with special characters

**Cause**: Figure backend or font doesn't support UTF-8

**Solution**:
```python
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend (faster, no GUI)

import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False  # Prevent minus sign issues

# Now generate figures
from pyfixest_latex import create_event_study_plot
create_event_study_plot(
    model=dynamic_model,
    title="Treatment Effects Over Time",  # UTF-8 now works
    style="filled"
)
```

---

## Model Fitting Errors

### Issue 9: PyfixestError: Unfitted model - cannot generate table

**Symptom**:
```
PyfixestError: Model has not been fitted. Call .fit() first.
```

**Cause**: Passing unfitted model objects to table generation functions

**Solution**: Fit models BEFORE passing to generation functions

```python
import pyfixest as pf
from pyfixest_latex import create_regression_table

# CORRECT: Models are fitted before use
m1 = pf.feols("Y ~ treat | unit + year", data, vcov={"CRV1": "unit"})
m2 = pf.feols("Y ~ treat + X1 | unit + year", data, vcov={"CRV1": "unit"})

# Now generate table
create_regression_table(
    models=[m1, m2],
    model_names=["(1)", "(2)"],
    label="tab:main"
)
```

**Common mistake to avoid**:
```python
# WRONG: Passing model class instead of fitted instance
models = [pf.feols, pf.feols]  # This won't work!

# WRONG: Formula string instead of fitted model
model = "Y ~ treat | unit + year"  # This won't work!
```

---

### Issue 10: Model formula error - "treat not in data"

**Symptom**:
```
KeyError: 'treat' not in DataFrame
```
when fitting model

**Cause**: Variable name doesn't match DataFrame columns; typo in formula

**Solution**:
```python
import pyfixest as pf
import pandas as pd

# 1. Verify column names
print(data.columns.tolist())

# 2. Use correct names in formula
# If column is actually 'treatment', not 'treat':
model = pf.feols("Y ~ treatment | unit + year", data, vcov={"CRV1": "unit"})

# 3. Check for spaces or special characters
print(data.columns)  # Look for unexpected spaces/characters
# Rename if needed:
data = data.rename(columns={' treat ': 'treat'})
```

---

### Issue 11: Formula error - missing fixed effects

**Symptom**:
```
Error: Fixed effect 'unit' not found in data
```

**Cause**: Fixed effect variable doesn't exist or has wrong name

**Solution**:
```python
# 1. Check available variables
print(data.columns.tolist())

# 2. Use correct FE variable names
m = pf.feols("Y ~ treat | firm_id + year_quarter", data, vcov={"CRV1": "firm_id"})

# 3. For data without string names, convert first
data['unit_str'] = data['unit_id'].astype(str)
m = pf.feols("Y ~ treat | unit_str + year", data, vcov={"CRV1": "unit_str"})
```

---

### Issue 12: Event study formula error - invalid reference period

**Symptom**:
```
Error: reference period X not found in time variable
```
when using `i(time_var, treat_var, ref=X)` syntax

**Cause**: Reference period value not in actual data

**Solution**:
```python
import pyfixest as pf

# 1. Check available time periods
unique_times = sorted(data['year'].unique())
print(f"Time periods: {unique_times}")

# 2. Use period that actually exists
# If data has years [2015, 2016, 2017, 2018], use those
model = pf.feols(
    "Y ~ i(year, treated, ref=2015) | unit + year",
    data,
    vcov={"CRV1": "unit"}
)

# 3. For event study with sequential time variable
# Ensure reference period matches sequential mapping
unique_periods = sorted(data['year_quarter'].unique())
seq_map = {p: i+1 for i, p in enumerate(unique_periods)}
data['time_seq'] = data['year_quarter'].map(seq_map)

# Use sequential reference period
ref_seq = seq_map[2020]  # If 2020 is your reference year-quarter
model = pf.feols(
    f"Y ~ i(time_seq, treated, ref={ref_seq}) | unit + year_quarter",
    data,
    vcov={"CRV1": "unit"}
)
```

---

### Issue 13: Model convergence or singularity error

**Symptom**:
```
LinearAlgebra Error: Singular matrix
```
or model fails to converge

**Cause**:
- Perfect multicollinearity (one variable is linear combination of others)
- Data has structural problems (missing groups, no variation)

**Solution**:
```python
import pyfixest as pf
import pandas as pd

# 1. Check for missing variation in treatment
treated_units = data[data['treated'] == 1]['unit'].nunique()
control_units = data[data['treated'] == 0]['unit'].nunique()
print(f"Treated units: {treated_units}, Control units: {control_units}")

if treated_units == 0 or control_units == 0:
    print("ERROR: No variation in treatment group assignment!")

# 2. Check for collinear variables
correlation_matrix = data[['Y', 'treat', 'X1', 'X2']].corr()
print(correlation_matrix)  # Look for correlations near 1.0

# 3. Remove problematic variables
# If X2 = 2*X1, drop X2
data = data.drop(columns=['X2'])

# 4. Drop rows with critical missing values
data = data.dropna(subset=['Y', 'treat', 'unit', 'year'])

# 5. Fit simpler model first to diagnose
m_simple = pf.feols("Y ~ treat | unit + year", data, vcov={"CRV1": "unit"})
print(m_simple.summary())
```

---

## LaTeX Compilation Issues

### Issue 14: LaTeX compilation fails - "Unknown control sequence"

**Symptom** (in LaTeX compiler):
```
! Undefined control sequence. \multicolumn
```

**Cause**: Required LaTeX packages not included in preamble

**Solution**: Add required packages to your LaTeX manuscript preamble

```latex
\documentclass{article}
\usepackage{booktabs}        % For \toprule, \midrule, \bottomrule
\usepackage{threeparttable}  % For table notes
\usepackage{graphicx}        % For \includegraphics
\usepackage{makecell}        % For \makecell in multi-line cells

\begin{document}
...
\input{Results/Tables/main_regression.tex}
...
\end{document}
```

**Complete minimal working example**:
```latex
\documentclass[12pt]{article}
\usepackage[utf-8]{inputenc}
\usepackage{booktabs}
\usepackage{threeparttable}
\usepackage{graphicx}
\usepackage{makecell}

\title{My Research Paper}
\author{Name}
\date{\today}

\begin{document}
\maketitle

\section{Results}

\input{Results/Tables/main_regression.tex}

\input{Results/Tables/summary_summary_stats.tex}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.9\textwidth]{Results/Figures/event_study.png}
\caption{Event Study Results}
\label{fig:event_study}
\end{figure}

\end{document}
```

---

### Issue 15: Generated .tex file won't compile - column mismatch

**Symptom**:
```
Extra alignment tab has been changed to \cr
```

**Cause**: Generated table has mismatched number of columns in header vs data rows

**Solution**: This is usually an internal module bug. Workaround:

```python
from pyfixest_latex import create_regression_table

# Add detailed debugging
create_regression_table(
    models=[m1, m2, m3],
    model_names=["(1)", "(2)", "(3)"],
    title="Results",
    label="tab:main",
    variable_labels={'treat': 'Treatment'},
    depvar_labels={'Y': 'Outcome'},
    felabels={'unit': 'Unit FE', 'year': 'Year FE'}
)

# Check generated file
with open("Results/Tables/main_regression.tex", "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines[:50]):
        print(f"{i}: {line.rstrip()}")
```

If columns don't match, manually edit the .tex file or report as bug to repo maintainer.

---

### Issue 16: Table styling issues - wrong column widths or alignment

**Symptom**: Tables look misaligned or text overflows

**Cause**: LaTeX table configuration; column widths not specified

**Solution**:
```latex
% Use tabularx for automatic column width adjustment
\documentclass{article}
\usepackage{tabularx}
\usepackage{booktabs}

\begin{table}[ht!]
\centering
\small
% Use tabularx with auto-width columns
\begin{tabularx}{0.95\textwidth}{Xcccc}
\toprule
% ... table contents ...
\bottomrule
\end{tabularx}
\caption{My Results}
\label{tab:results}
\end{table}
```

Or adjust in Python before saving:
```python
# Check the actual .tex output
table_path = "Results/Tables/main_regression.tex"
with open(table_path, "r") as f:
    content = f.read()

# Look for column specification line: \begin{tabular}{lccc}
# If needed, wrap in table environment with proper sizing
```

---

## Data Structure Issues

### Issue 17: Event study fails - non-sequential time variable

**Symptom**:
```
IndexError: Index X not found in dynamic interaction
```
when using `i(time, treat)` in event study formula

**Cause**: Time variable isn't sequential (has gaps or non-integer values)

**Solution**: Create sequential time variable

```python
import pandas as pd
import numpy as np

# Original time: [20191, 20192, 20194, 20195, 20201, 20202, ...]
# (Note: 20193 is missing - quarterly data with gap)

# Create sequential mapping
unique_times = sorted(data['year_quarter'].unique())
time_seq_map = {t: i+1 for i, t in enumerate(unique_times)}

data['time_seq'] = data['year_quarter'].map(time_seq_map)

# Verify it's sequential
print(sorted(data['time_seq'].unique()))  # Should be [1, 2, 3, 4, 5, ...]

# Now use in formula
m = pf.feols(
    "Y ~ i(time_seq, treated, ref=3) | unit + year_quarter",
    data,
    vcov={"CRV1": "unit"}
)
```

**See also**: `@.claude/skills/pyfixest-latex/references/workflow-patterns.md` for Sequential Time Variables section

---

### Issue 18: Missing values break regression

**Symptom**:
```
ValueError: Input contains NaN or infinite values
```

**Cause**: Missing values (NaN) or infinite values in data

**Solution**:
```python
import pandas as pd
import numpy as np

# 1. Check for missing values
print(data[['Y', 'treat', 'unit', 'year']].isnull().sum())

# 2. Remove rows with NaN in analysis variables
data = data.dropna(subset=['Y', 'treat', 'unit', 'year'])

# 3. Check for infinite values
print(np.isinf(data[['Y', 'treat']]).any())

# 4. Replace infinite with NaN, then drop
data = data.replace([np.inf, -np.inf], np.nan)
data = data.dropna(subset=['Y', 'treat'])

# 5. Report data loss
print(f"Dropped {initial_rows - len(data)} rows ({100*(1-len(data)/initial_rows):.1f}%)")
```

**See also**: `@.claude/skills/pyfixest-latex/references/data-requirements.md` for Data Quality Checks section

---

### Issue 19: Panel structure error - mismatched unit/time dimensions

**Symptom**:
- Clustering errors
- Unexpected FE counts
- "Expected N×T panel but got M observations"

**Cause**: Data not properly structured as balanced panel; gaps or duplicates

**Solution**:
```python
import pandas as pd

# Check panel structure
n_units = data['unit'].nunique()
n_periods = data['year'].nunique()
expected_obs = n_units * n_periods

print(f"Units: {n_units}, Periods: {n_periods}")
print(f"Expected obs (balanced): {expected_obs:,}")
print(f"Actual obs: {len(data):,}")
print(f"Balance ratio: {len(data)/expected_obs*100:.1f}%")

# Check for duplicate unit-time observations
duplicates = data.groupby(['unit', 'year']).size()
if (duplicates > 1).any():
    print("ERROR: Duplicate observations detected!")
    print(duplicates[duplicates > 1])

# Sort and reset index for consistency
data = data.sort_values(['unit', 'year']).reset_index(drop=True)

# If panel is unbalanced, identify missing obs
complete_panel = pd.MultiIndex.from_product(
    [data['unit'].unique(), data['year'].unique()],
    names=['unit', 'year']
)
actual_panel = data.set_index(['unit', 'year']).index
missing = complete_panel.difference(actual_panel)
print(f"Missing observations: {len(missing)}")
```

---

### Issue 20: Treatment variable has time variation (should be time-invariant)

**Symptom**: Treatment group assignment changes within units over time

**Cause**: Incorrectly constructed treatment dummy

**Solution**:
```python
import pandas as pd

# Check for variation in treatment within units
treatment_variation = data.groupby('unit')['treated'].nunique()
problem_units = treatment_variation[treatment_variation > 1].index.tolist()

if problem_units:
    print(f"ERROR: Treatment varies within units: {problem_units}")
    print(data[data['unit'].isin(problem_units[0])][['unit', 'year', 'treated']])

# FIX: Enforce time-invariant treatment
data['treated'] = data.groupby('unit')['treated'].transform('max')

# Verify fix
print(data.groupby('unit')['treated'].nunique().unique())  # Should be [1]
```

---

## Import Errors

### Issue 21: Circular import or "ImportError: cannot import pyfixest_latex in script"

**Symptom**:
```
ImportError: cannot import name 'create_regression_table' from pyfixest_latex
```
or circular import error

**Cause**: Module path not set correctly; pyfixest_latex folder in wrong location

**Solution**:

**Option A: Use centralized config_paths** (recommended for projects with `CLAUDE.md`)
```python
import sys
from pathlib import Path

# Auto-detect project root
for p in Path(__file__).resolve().parents[:5]:
    if (p / 'config_paths.py').exists():
        sys.path.insert(0, str(p))
        break

from config_paths import TABLES_DIR, FIGURES_DIR
from pyfixest_latex import create_regression_table, set_output_path

set_output_path(str(TABLES_DIR))
```

**Option B: Direct path addition** (for standalone scripts)
```python
import sys
from pathlib import Path

# Add pyfixest_latex to path
pyfixest_latex_path = Path(__file__).parent / "pyfixest_latex"
sys.path.insert(0, str(pyfixest_latex_path.absolute()))

from pyfixest_latex import create_regression_table
```

**Option C: Install with setup script** (see Issue 2)
```bash
python .claude/skills/pyfixest-latex/scripts/setup_module.py /path/to/project
```

---

### Issue 22: "ModuleNotFoundError: No module named 'pyfixest_latex.academic_table_generator'"

**Symptom**:
```
ModuleNotFoundError: No module named 'pyfixest_latex.academic_table_generator'
```

**Cause**: pyfixest_latex package not installed properly; missing files

**Solution**:
```bash
# 1. Verify file structure
ls -la pyfixest_latex/
# Should show:
#   __init__.py
#   academic_table_generator.py
#   academic_figure_generator.py

# 2. If files exist but import fails, reinstall
pip install --force-reinstall --no-cache-dir pyfixest

# 3. Check Python path
python -c "import sys; print(sys.path)"

# 4. Run diagnostic (from Quick Diagnostics section above)
python diagnostic.py
```

---

## Output Issues

### Issue 23: Table generated but filename is wrong or not found

**Symptom**: Can't find generated table; filename doesn't match expected

**Cause**: Filename auto-generated from `label` parameter; doesn't match expected name

**Solution**:
```python
from pyfixest_latex import create_regression_table, list_saved_tables

# Generate with specific label
create_regression_table(
    models=[m1, m2],
    model_names=["(1)", "(2)"],
    title="Results",
    label="tab:main_results"
)

# Check what was actually saved
saved_files = list_saved_tables()
print(f"Saved files: {saved_files}")

# Filename will be: main_results_regression.tex
# (label: 'tab:main_results' → filename: 'main_results_regression.tex')
```

**Naming convention**:
- `create_regression_table` with `label="tab:xyz"` → `xyz_regression.tex`
- `create_dynamic_table` with `label="tab:xyz"` → `xyz_dynamic.tex`
- `create_summary_statistics_table` with `label="tab:xyz"` → `xyz_summary_stats.tex`
- `create_robustness_table` with `label="tab:xyz"` → `xyz_robustness.tex`

---

### Issue 24: Figure not saved or saved to wrong location

**Symptom**: PNG/PDF figure file not found in expected directory

**Cause**: Figure output path not configured; default path used

**Solution**:
```python
from pyfixest_latex import (
    set_figure_output_path, get_figure_output_path,
    create_event_study_plot, list_saved_figures
)

# MUST configure before generating figures
set_figure_output_path("Results/Figures")

# Generate figure
create_event_study_plot(
    model=dynamic_model,
    title="Treatment Effects Over Time",
    style="filled"
)

# Verify it was saved
saved_figures = list_saved_figures()
print(f"Saved figures: {saved_figures}")

figure_dir = get_figure_output_path()
print(f"Figures saved to: {figure_dir}")
```

---

### Issue 25: Special characters in table don't render in LaTeX

**Symptom**: Variable labels with underscores, special characters, or Greek letters don't display correctly

**Cause**: LaTeX special characters not escaped

**Solution**:
```python
from pyfixest_latex import create_regression_table

# Use proper LaTeX escaping in labels
variable_labels = {
    'log_assets': r'Log(Assets)',           # Use raw string for backslashes
    'roe': r'Return on Equity (\%)',        # Escape special chars with backslash
    'sic_67': r'SIC $\\in$ [6700, 6799]',   # Math mode for symbols
    'treat_x_post': r'Treatment $\\times$ Post',  # Use $...$ for math
}

create_regression_table(
    models=[m1, m2],
    variable_labels=variable_labels,
    title="Results",
    label="tab:main"
)
```

**Common LaTeX escapes**:
| Input | LaTeX Output |
|-------|------|
| `_` (underscore) | Use raw string: `r'log_assets'` or escape: `'log\_assets'` |
| `%` (percent) | `'Return on Equity (\%)'` |
| `&` (ampersand) | `'A \& B'` |
| `$` (dollar) | `'Cost = \$100'` |
| `~` (tilde) | `'A $\\sim$ B'` |

---

### Issue 26: Console output has encoding errors

**Symptom**:
```
UnicodeEncodeError: 'cp1252' codec can't encode character...
```
when printing diagnostics

**Cause**: Default Windows encoding not UTF-8

**Solution**: Add UTF-8 config at script start (see Issue 7)

```python
import sys
import io
import os

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Now safe to print unicode
print("Results: α = 0.05, β = 2.3")
```

---

## Summary Checklist

Before running analysis, verify:

- [ ] Python 3.8+ installed and activated
- [ ] All dependencies installed: `pip install pyfixest pandas numpy scipy matplotlib`
- [ ] `pyfixest_latex` module copied to project or installed
- [ ] UTF-8 encoding configured at script start (Windows)
- [ ] Output paths configured BEFORE generating output
- [ ] All required LaTeX packages in manuscript preamble
- [ ] Data cleaned: no NaN/inf values in analysis variables
- [ ] Panel structure validated: units, time periods, no duplicates
- [ ] PyFixest models fitted successfully before passing to generation functions
- [ ] Variable names match DataFrame columns exactly

For additional help, see:
- `@.claude/skills/pyfixest-latex/references/workflow-patterns.md` - Best practices and project setup
- `@.claude/skills/pyfixest-latex/references/data-requirements.md` - Data structure and validation
- `@.claude/skills/pyfixest-latex/SKILL.md` - Function reference and critical rules
