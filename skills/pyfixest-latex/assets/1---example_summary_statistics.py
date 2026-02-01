"""
Example: Summary Statistics Table Generation
============================================

This example demonstrates how to:
1. Load data from PyFixest example dataset
2. Display data summary in console
3. Generate publication-quality summary statistics table

Author: AI Assistant
"""

# ==============================================================================
# PROJECT PATH CONFIGURATION - Automatically locates and imports centralized paths
# ==============================================================================
from pathlib import Path
import sys

# Search up to 5 parent directories to find config_paths.py
for p in Path(__file__).resolve().parents[:5]:
    if (p / 'config_paths.py').exists():
        sys.path.insert(0, str(p))
        break

# Import path configuration module
import config_paths
from config_paths import TABLES_DIR, FINAL_DATASETS_DIR

# =============================================================================
# REGRESSION MODULE IMPORT
# =============================================================================
# Search for and import the regression module
for p in Path(__file__).resolve().parents[:3]:
    module_dir = p / 'pyfixest-regressions-to-latex'
    if module_dir.exists():
        sys.path.insert(0, str(module_dir))
        break

from module import (
    create_summary_statistics_table,
    set_output_path,
    get_output_path
)

import pandas as pd
import numpy as np
import pyfixest as pf
from pyfixest.utils.dgps import get_sharkfin

# =============================================================================
# SET OUTPUT PATH FOR TABLES
# =============================================================================

# Set output path using centralized config_paths
set_output_path(str(TABLES_DIR))
print(f"Tables will be saved to: {get_output_path()}")

# =============================================================================
# LOAD AND DISPLAY DATA
# =============================================================================

print("\n" + "=" * 80)
print("SUMMARY STATISTICS TABLE EXAMPLE")
print("=" * 80)

# Load example synthetic data (replace with your actual data loading)
print("\n📊 Loading example synthetic data from PyFixest...")
print("   Note: This is synthetic data for demonstration purposes.")
print("   Replace get_sharkfin() with your actual data loading code.\n")
df = get_sharkfin()

# Create control variables and alternative dependent variable for demonstration
# These are synthetic variables that will be used in regression examples
print("\n🔧 Generating control variables and alternative dependent variable...")
np.random.seed(42)  # Set seed for reproducibility
df['X1'] = np.random.normal(0, 1, len(df))
df['X2'] = np.random.normal(0, 1, len(df))
df['X3'] = np.random.normal(0, 0.5, len(df))
df['Y2'] = df['Y'] + np.random.normal(0, 0.1, len(df))  # Alternative outcome
print("   ✓ Generated control variables: X1, X2, X3")
print("   ✓ Generated alternative dependent variable: Y2")

# Save dataset to Final_Datasets folder
dataset_filename = "example_sharkfin_data"
dataset_pickle_path = FINAL_DATASETS_DIR / f"{dataset_filename}.pkl"
dataset_csv_path = FINAL_DATASETS_DIR / f"{dataset_filename}.csv"

print(f"\n💾 Saving dataset to Final_Datasets folder...")
df.to_pickle(dataset_pickle_path)
df.to_csv(dataset_csv_path, index=False)
print(f"   ✓ Saved as pickle: {dataset_pickle_path}")
print(f"   ✓ Saved as CSV: {dataset_csv_path}")
print(f"   Dataset location: {FINAL_DATASETS_DIR}")
print(f"   Dataset includes: {list(df.columns)}")

# Display data overview
print("=" * 80)
print("DATA OVERVIEW")
print("=" * 80)
print(f"Shape: {df.shape[0]:,} observations × {df.shape[1]} variables")
print(f"Time periods: {df['year'].nunique()} (years {df['year'].min()} to {df['year'].max()})")
print(f"Units: {df['unit'].nunique():,} unique units")
print(f"\nVariables: {list(df.columns)}")
print("\nFirst 10 rows:")
print(df.head(10))

# Key variable summary
print("\n" + "=" * 80)
print("KEY VARIABLE SUMMARY")
print("=" * 80)
print(f"  Outcome (Y):      mean={df['Y'].mean():.3f}, std={df['Y'].std():.3f}, range=[{df['Y'].min():.3f}, {df['Y'].max():.3f}]")
print(f"  Outcome (Y2):     mean={df['Y2'].mean():.3f}, std={df['Y2'].std():.3f}, range=[{df['Y2'].min():.3f}, {df['Y2'].max():.3f}]")
print(f"  Treatment (treat): {df['treat'].sum():,} treated observations ({df['treat'].mean()*100:.1f}%)")
print(f"  Ever treated:      {df['ever_treated'].sum():,} units ever treated ({df.groupby('unit')['ever_treated'].max().sum():,} unique units)")
print(f"  Control X1:        mean={df['X1'].mean():.3f}, std={df['X1'].std():.3f}")
print(f"  Control X2:        mean={df['X2'].mean():.3f}, std={df['X2'].std():.3f}")
print(f"  Control X3:        mean={df['X3'].mean():.3f}, std={df['X3'].std():.3f}")

# Display basic statistics for key variables
print("\n" + "=" * 80)
print("BASIC DESCRIPTIVE STATISTICS")
print("=" * 80)
key_vars = ['Y', 'Y2', 'treat', 'ever_treated', 'X1', 'X2', 'X3']
if all(var in df.columns for var in key_vars):
    print(df[key_vars].describe())

# =============================================================================
# GENERATE SUMMARY STATISTICS TABLE
# =============================================================================

print("\n" + "=" * 80)
print("GENERATING SUMMARY STATISTICS TABLE")
print("=" * 80)

# Define variables to include in summary statistics table
# Select key variables from the dataset (including control variables)
variables = ['Y', 'Y2', 'treat', 'ever_treated', 'X1', 'X2', 'X3']

# Create descriptive labels for variables
variable_labels = {
    'Y': 'Outcome Variable (Y)',
    'Y2': 'Alternative Outcome (Y2)',
    'treat': 'Treatment Indicator',
    'ever_treated': 'Ever Treated Indicator',
    'X1': 'Control Variable 1',
    'X2': 'Control Variable 2',
    'X3': 'Control Variable 3'
}

# Generate summary statistics table
try:
    latex_table_summary = create_summary_statistics_table(
        data=df,
        variables=variables,
        variable_labels=variable_labels,
        title="Summary Statistics: Key Variables",
        label="tab:summary_stats",
        filename="example_summary_statistics.tex",
        digits=3,
        include_count=True,
        percentiles=[0.25, 0.5, 0.75]
    )

    print("\n✓ Summary statistics table generated successfully!")
    print(f"  - Generated descriptive statistics for {len(variables)} variables")
    print(f"  - Columns: N, Mean, Std Dev, Min, Max, 25%, 50%, 75%")
    print(f"  - Saved to: {get_output_path()}/example_summary_statistics.tex")
    print("\n" + "=" * 80)
    print("TABLE PREVIEW")
    print("=" * 80)
    print("The table has been saved and can be included in LaTeX with:")
    print("  \\input{Results/Tables/example_summary_statistics.tex}")
    print("\n" + "=" * 80)

except Exception as e:
    print(f"\n✗ ERROR generating summary statistics table: {e}")
    import traceback
    traceback.print_exc()

