"""
Example Usage of Academic Figure Generator
===========================================

This file shows how to use the academic_figure_generator.py module
for creating professional publication-quality figures.

Author: AI Assistant
"""

# =============================================================================
# IMPORT THE FUNCTIONS
# =============================================================================

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
from config_paths import FIGURES_DIR

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
    create_event_study_plot,
    create_treatment_assignment_plot,
    create_coefficient_comparison_plot,
    list_saved_figures,
    set_figure_output_path,
    get_figure_output_path
)

import pandas as pd
import pyfixest as pf
from config_paths import FINAL_DATASETS_DIR

# =============================================================================
# SET OUTPUT PATH FOR FIGURES
# =============================================================================

# Set output path for figures using centralized config_paths
set_figure_output_path(str(FIGURES_DIR))
print(f"🖼️  Figures will be saved to: {get_figure_output_path()}")

# =============================================================================
# EXAMPLE 1: Event Study Plot
# =============================================================================

print("📈 EXAMPLE 1: Event Study Plot")
print("=" * 50)

# Load example synthetic data from Final_Datasets folder
# This data was prepared by 1---example_summary_statistics.py
print("\n📊 Loading example synthetic data from Final_Datasets folder...")
print("   Note: This data includes control variables (X1, X2, X3) and alternative outcome (Y2)")
print("   that were generated in 1---example_summary_statistics.py\n")
dataset_filename = "example_sharkfin_data"
dataset_pickle_path = FINAL_DATASETS_DIR / f"{dataset_filename}.pkl"

try:
    df = pd.read_pickle(dataset_pickle_path)
    print(f"   ✓ Loaded dataset from: {dataset_pickle_path}")
    print(f"   ✓ Dataset includes: {list(df.columns)}")
except FileNotFoundError:
    print(f"   ⚠️  Dataset not found at {dataset_pickle_path}")
    print("   Please run 1---example_summary_statistics.py first to generate the dataset.")
    raise

# Display data overview
print("=" * 50)
print("DATA OVERVIEW")
print("=" * 50)
print(f"Shape: {df.shape[0]:,} observations × {df.shape[1]} variables")
print(f"Time periods: {df['year'].nunique()} (years {df['year'].min()} to {df['year'].max()})")
print(f"Units: {df['unit'].nunique():,} unique units")
print(f"\nVariables: {list(df.columns)}")
print("\nFirst 10 rows:")
print(df.head(10))
print("\nKey Variable Summary:")
print(f"  Outcome (Y):      mean={df['Y'].mean():.3f}, std={df['Y'].std():.3f}, range=[{df['Y'].min():.3f}, {df['Y'].max():.3f}]")
print(f"  Treatment (treat): {df['treat'].sum():,} treated observations ({df['treat'].mean()*100:.1f}%)")
print(f"  Ever treated:      {df['ever_treated'].sum():,} units ever treated ({df.groupby('unit')['ever_treated'].max().sum():,} unique units)")

# Find and display example unit with ever_treated == 1
print("\n" + "=" * 50)
print("EXAMPLE UNIT: Complete Panel Data for Treated Unit")
print("=" * 50)
# Find a unit that was ever treated
treated_units = df[df['ever_treated'] == 1]['unit'].unique()
if len(treated_units) > 0:
    example_unit = treated_units[0]
    unit_data = df[df['unit'] == example_unit].sort_values('year')
    print(f"\nShowing all {len(unit_data)} time periods for unit {example_unit} (ever_treated == 1):")
    print(unit_data.to_string(index=False))
    print(f"\nTreatment timeline: First treated in year {unit_data[unit_data['treat'] == 1]['year'].min()}")
    print(f"  Pre-treatment periods: {len(unit_data[unit_data['treat'] == 0])}")
    print(f"  Post-treatment periods: {len(unit_data[unit_data['treat'] == 1])}")
else:
    print("No treated units found in example data.")
print("=" * 50)
print()

# Fit dynamic model (replace with your actual model specification)
dynamic_model = pf.feols(
    "Y ~ i(year, ever_treated, ref=14) | unit + year",
    df,
    vcov={"CRV1": "unit"}
)

# Generate professional event study plot
create_event_study_plot(
    model=dynamic_model,
    title="Treatment Effects on Outcome Over Time",
    filename="event_study.png",
    style="filled",  # Options: 'errorbar', 'filled', 'step'
    reference_period=14
)

# =============================================================================
# EXAMPLE 2: Treatment Assignment Visualization
# =============================================================================

print("\n🎯 EXAMPLE 2: Treatment Assignment Plot")
print("=" * 50)

# Generate treatment assignment visualization
create_treatment_assignment_plot(
    data=df,
    title="Treatment Assignment Patterns Across Units",
    filename="treatment_assignment.png",
    unit="unit",
    time="year",
    treat="treat"
)

# =============================================================================
# EXAMPLE 3: Coefficient Comparison Plot
# =============================================================================

print("\n📊 EXAMPLE 3: Coefficient Comparison Plot")
print("=" * 50)

# Fit multiple models for comparison (replace with your specifications)
models = [
    pf.feols("Y ~ treat | unit + year", df, vcov={"CRV1": "unit"}),  # Basic DiD
    pf.feols("Y ~ treat | unit + year", df, vcov="hetero"),         # Robust SE
    pf.feols("Y ~ treat | unit", df, vcov={"CRV1": "unit"})         # Only unit FE
]

model_names = ["Basic DiD", "Robust SE", "Unit FE Only"]

# Generate coefficient comparison plot
create_coefficient_comparison_plot(
    models=models,
    model_names=model_names,
    title="Treatment Effect Robustness Across Specifications",
    filename="coefficient_comparison.png"
)

# =============================================================================
# UTILITIES
# =============================================================================

print("\n🖼️  LISTING ALL GENERATED FIGURES")
print("=" * 50)
list_saved_figures()

print("\n" + "=" * 80)
print("🎉 SUCCESS! All academic figures generated!")
print("=" * 80)
print("🖼️  Figures saved to Results/Figures/")
print("\nInclude in your LaTeX manuscript:")
print("\\begin{figure}[ht!]")
print("\\centering")
print("\\includegraphics[width=0.8\\textwidth]{Results/Figures/event_study.png}")
print("\\caption{Treatment Effects Over Time}")
print("\\label{fig:event_study}")
print("\\end{figure}")
print()
print("Reference in text:")
print("As shown in Figure \\ref{fig:event_study}, the treatment effect becomes significant after treatment implementation.")
print()
print("📖 Full documentation: https://github.com/py-econometrics/pyfixest")
