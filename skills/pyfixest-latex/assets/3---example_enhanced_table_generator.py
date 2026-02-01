"""
Enhanced Academic Table Generator - Usage Examples
==================================================

This script demonstrates the enhanced table generation capabilities with custom
dependent variable labels, fixed effects labels, and model headers.

Author: AI Assistant
Date: 2024
"""

# =============================================================================
# IMPORTS AND SETUP
# =============================================================================

import pandas as pd
import pyfixest as pf
from pathlib import Path
import sys

# Add the module to path
module_dir = Path(__file__).parent
sys.path.insert(0, str(module_dir))

from module import (
    create_regression_table,
    create_dynamic_table,
    create_robustness_table,
    set_output_path
)

# Import data loading utilities
import pandas as pd
from pathlib import Path
import sys

# Import path configuration for Final_Datasets
for p in Path(__file__).resolve().parents[:5]:
    if (p / 'config_paths.py').exists():
        sys.path.insert(0, str(p))
        break

from config_paths import FINAL_DATASETS_DIR

# =============================================================================
# ENHANCED TABLE GENERATION EXAMPLES
# =============================================================================

def example_enhanced_regression_tables():
    """Demonstrate enhanced regression table generation."""
    print("=" * 80)
    print("ENHANCED REGRESSION TABLE EXAMPLES")
    print("=" * 80)
    
    # Load example synthetic data from Final_Datasets folder
    # This data was prepared by 1---example_summary_statistics.py and includes control variables
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
    print(f"  Outcome (Y2):     mean={df['Y2'].mean():.3f}, std={df['Y2'].std():.3f}, range=[{df['Y2'].min():.3f}, {df['Y2'].max():.3f}]")
    print(f"  Treatment (treat): {df['treat'].sum():,} treated observations ({df['treat'].mean()*100:.1f}%)")
    print(f"  Ever treated:      {df['ever_treated'].sum():,} units ever treated ({df.groupby('unit')['ever_treated'].max().sum():,} unique units)")
    print(f"  Control X1:        mean={df['X1'].mean():.3f}, std={df['X1'].std():.3f}")
    print(f"  Control X2:        mean={df['X2'].mean():.3f}, std={df['X2'].std():.3f}")
    print(f"  Control X3:        mean={df['X3'].mean():.3f}, std={df['X3'].std():.3f}")
    
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
    
    # Define custom labels
    variable_labels = {
        'treat': 'Treatment Effect',
        'X1': 'Control Variable 1',
        'X2': 'Control Variable 2',
        'X3': 'Control Variable 3'
    }
    
    depvar_labels = {
        'Y': 'Outcome Variable',
        'Y2': 'Alternative Outcome'
    }
    
    fe_labels = {
        'unit': 'Unit FE',
        'year': 'Year FE'
    }
    
    # Fit models
    models = [
        pf.feols("Y ~ treat | unit + year", df, vcov={"CRV1": "unit"}),
        pf.feols("Y ~ treat + X1 | unit + year", df, vcov={"CRV1": "unit"}),
        pf.feols("Y2 ~ treat | unit + year", df, vcov={"CRV1": "unit"}),
        pf.feols("Y2 ~ treat + X1 + X2 + X3 | unit + year", df, vcov={"CRV1": "unit"})
    ]
    
    # Example 1: Basic enhanced regression table
    print("\n📊 Example 1: Enhanced Regression Table with Custom Labels")
    create_regression_table(
        models=models,
        model_names=["Basic", "With Controls", "Basic", "With Controls"],
        title="Enhanced Regression Results with Custom Labels",
        label="tab:enhanced_example",
        filename="enhanced_regression_example.tex",
        variable_labels=variable_labels,
        depvar_labels=depvar_labels,
        felabels=fe_labels
    )
    
    # Example 2: Dynamic effects table
    print("\n📈 Example 2: Enhanced Dynamic Effects Table")
    
    # Create dynamic treatment effects using year and ever_treated
    # Note: Using year interaction with ever_treated for event study
    dynamic_models = [
        pf.feols("Y ~ i(year, ever_treated, ref=14) | unit + year", 
                df, vcov={"CRV1": "unit"}),
        pf.feols("Y ~ i(year, ever_treated, ref=14) + X1 + X2 | unit + year", 
                df, vcov={"CRV1": "unit"})
    ]
    
    create_dynamic_table(
        models=dynamic_models,
        model_names=["Without Controls", "With Controls"],
        title="Dynamic Treatment Effects with Custom Labels",
        label="tab:dynamic_enhanced",
        filename="enhanced_dynamic_example.tex",
        treatment_period=14,  # Reference period for consistent labeling
        variable_labels=variable_labels,
        depvar_labels=depvar_labels,
        felabels=fe_labels
    )
    
    # Example 3: Robustness table with groups
    print("\n🔍 Example 3: Enhanced Robustness Table with Groups")
    
    # Create model groups
    main_models = [models[0], models[1]]  # Outcome Y models
    robust_models = [models[2], models[3]]  # Alternative outcome Y2 models
    
    create_robustness_table(
        model_groups=[main_models, robust_models],
        group_names=["Outcome Y", "Alternative Outcome Y2"],
        title="Robustness Analysis with Custom Labels",
        label="tab:robustness_enhanced",
        filename="enhanced_robustness_example.tex",
        variable_labels=variable_labels,
        depvar_labels=depvar_labels,
        felabels=fe_labels
    )
    
    # Example 4: Progressive specification table - building up fixed effects and controls
    print("\n🔍 Example 4: Progressive Specification - Building Up Fixed Effects and Controls")
    
    # Create progressive models: each column adds more fixed effects/controls
    progressive_models = [
        pf.feols("Y ~ treat | year", df, vcov={"CRV1": "unit"}),                    # Column 1: Year FE only
        pf.feols("Y ~ treat | unit", df, vcov={"CRV1": "unit"}),                   # Column 2: Unit FE only
        pf.feols("Y ~ treat | unit + year", df, vcov={"CRV1": "unit"}),            # Column 3: Unit + Year FE
        pf.feols("Y ~ treat + X1 + X2 + X3 | unit + year", df, vcov={"CRV1": "unit"})  # Column 4: Unit + Year FE + Controls
    ]
    
    create_regression_table(
        models=progressive_models,
        model_names=["Year FE", "Unit FE", "Unit + Year FE", "With Controls"],
        title="Progressive Specification: Building Up Fixed Effects and Controls",
        label="tab:progressive_specification",
        filename="enhanced_robustness_comprehensive.tex",
        variable_labels=variable_labels,
        depvar_labels=depvar_labels,
        felabels=fe_labels
    )

def example_custom_style_tables():
    """Demonstrate custom style table generation with treatment interaction."""
    print("\n" + "=" * 80)
    print("CUSTOM STYLE TABLE EXAMPLES")
    print("=" * 80)
    
    # Load example synthetic data from Final_Datasets folder
    # This data was prepared by 1---example_summary_statistics.py and includes control variables
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
    print(f"  Outcome (Y2):     mean={df['Y2'].mean():.3f}, std={df['Y2'].std():.3f}, range=[{df['Y2'].min():.3f}, {df['Y2'].max():.3f}]")
    print(f"  Treatment (treat): {df['treat'].sum():,} treated observations ({df['treat'].mean()*100:.1f}%)")
    print(f"  Ever treated:      {df['ever_treated'].sum():,} units ever treated ({df.groupby('unit')['ever_treated'].max().sum():,} unique units)")
    print(f"  Control X1:        mean={df['X1'].mean():.3f}, std={df['X1'].std():.3f}")
    print(f"  Control X2:        mean={df['X2'].mean():.3f}, std={df['X2'].std():.3f}")
    print(f"  Control X3:        mean={df['X3'].mean():.3f}, std={df['X3'].std():.3f}")
    
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
    
    # Custom style labels with treatment interaction
    custom_variable_labels = {
        'treat': 'Treatment $\\times$ Post',
        'X1': 'Control Variable 1',
        'X2': 'Control Variable 2',
        'X3': 'Control Variable 3'
    }
    
    custom_depvar_labels = {
        'Y': 'Outcome Variable',
        'Y2': 'Alternative Outcome'
    }
    
    custom_fe_labels = {
        'unit': 'Unit FE',
        'year': 'Year FE'
    }
    
    # Custom style models
    models = [
        pf.feols("Y ~ treat | unit + year", df, vcov={"CRV1": "unit"}),
        pf.feols("Y ~ treat + X1 + X2 + X3 | unit + year", df, vcov={"CRV1": "unit"}),
        pf.feols("Y2 ~ treat | unit + year", df, vcov={"CRV1": "unit"}),
        pf.feols("Y2 ~ treat + X1 + X2 + X3 | unit + year", df, vcov={"CRV1": "unit"})
    ]
    
    print("\n📊 Custom Style Regression Table")
    create_regression_table(
        models=models,
        model_names=["Clustered SE", "With Controls", "Clustered SE", "With Controls"],
        title="Treatment Effects on Outcomes",
        label="tab:custom_enhanced",
        filename="custom_enhanced_example.tex",
        variable_labels=custom_variable_labels,
        depvar_labels=custom_depvar_labels,
        felabels=custom_fe_labels
    )

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Run all enhanced table generation examples."""
    print("🎯 ENHANCED ACADEMIC TABLE GENERATOR EXAMPLES")
    print("=" * 80)
    
    # Set output path
    set_output_path("Results/Tables")
    print(f"📁 Tables will be saved to: Results/Tables/")
    
    # Run examples
    example_enhanced_regression_tables()
    example_custom_style_tables()
    
    print("\n" + "=" * 80)
    print("🎉 ALL EXAMPLES COMPLETED!")
    print("=" * 80)
    print("✅ Enhanced table generation with custom labels")
    print("✅ Dependent variable label customization")
    print("✅ Fixed effects label customization")
    print("✅ Model header customization")
    print("✅ Custom style table formatting")
    print("\n📁 Check Results/Tables/ for generated .tex files")

if __name__ == "__main__":
    main()
