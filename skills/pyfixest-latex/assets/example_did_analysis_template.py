"""
Generalized Difference-in-Differences (DiD) Analysis Template
==============================================================

This script provides a complete, production-ready template for conducting and reporting
difference-in-differences analyses using PyFixest with publication-quality LaTeX outputs.

QUICK START:
1. Replace DATA_PATH with your data file path
2. Update TREATMENT_* configuration variables
3. Customize OUTCOME_VARIABLES and CONTROL_VARIABLES
4. Run: python example_did_analysis_template.py

The script generates:
- Summary statistics tables
- DiD regression tables (standard 2x2 design)
- Dynamic effects tables (event study with leads/lags)
- Treatment assignment visualizations
- Event study plots with confidence intervals

Features:
- Cross-platform UTF-8 encoding support (Windows PowerShell compatible)
- Robust error handling with informative diagnostics
- Automatic output to LaTeX format for manuscript integration
- Professional variable labeling and formatting
- Complete workflow from data loading to figure generation

Author: Template Generator
Version: 1.0
"""

# =============================================================================
# ENCODING CONFIGURATION - Ensure UTF-8 support for Unicode characters
# =============================================================================
# This section is CRITICAL for Windows PowerShell compatibility.
# It ensures all console output and file operations use UTF-8 encoding.

import sys
import io
import os

# Set UTF-8 encoding for stdout/stderr (critical for Windows PowerShell)
if sys.platform == 'win32':
    # Windows-specific: Set console code page to UTF-8
    try:
        import codecs
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # Fallback if buffer doesn't exist

    # Set environment variable for subprocess calls
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Set default encoding for file operations
if hasattr(sys, 'setdefaultencoding'):
    sys.setdefaultencoding('utf-8')

# Ensure pandas uses UTF-8
import pandas as pd
pd.options.display.encoding = 'utf-8'


# =============================================================================
# IMPORTS AND DEPENDENCIES
# =============================================================================

import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Optional: Try to import PyFixest for econometric analysis
try:
    import pyfixest as pf
    PYFIXEST_AVAILABLE = True
except ImportError:
    PYFIXEST_AVAILABLE = False
    print("WARNING: PyFixest not installed. Install with: pip install pyfixest")

# Optional: Try to import matplotlib for figures
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("WARNING: Matplotlib/Seaborn not installed. Install with: pip install matplotlib seaborn")


# =============================================================================
# CONFIGURATION: CUSTOMIZE THESE SETTINGS FOR YOUR ANALYSIS
# =============================================================================
# region CUSTOMIZE THIS SECTION

class DidConfig:
    """Configuration class for DiD analysis. Modify these values for your research."""

    # =========================================================================
    # DATA INPUT - CUSTOMIZE THIS
    # =========================================================================
    # Path to your data file. Supports: .parquet, .csv, .xlsx, .dta
    DATA_PATH = "path/to/your/data.parquet"
    # CUSTOMIZE THIS: Replace with your actual data file path
    # Example: "C:/Users/name/Research/data/final_data.parquet"


    # =========================================================================
    # CORE VARIABLE NAMES - MAP THESE TO YOUR DATA COLUMNS
    # =========================================================================
    UNIT_ID = "firm_id"
    # CUSTOMIZE THIS: Column name for units (firms, individuals, regions, etc.)
    # Examples: "gvkey", "permno", "household_id", "county_id"

    TIME_VAR = "year"
    # CUSTOMIZE THIS: Column name for time periods
    # Examples: "year", "year_quarter", "year_month_numeric"

    GROUP_VAR = "treatment_group"
    # CUSTOMIZE THIS: Column name indicating treatment group membership (0/1 or similar)
    # Examples: "treated", "treatment", "policy_exposure"


    # =========================================================================
    # TREATMENT TIMING - WHEN DID THE TREATMENT OCCUR?
    # =========================================================================
    TREATMENT_TIME = 2016
    # CUSTOMIZE THIS: When the treatment event occurred
    # The DiD design creates indicators for:
    # - Post-treatment periods (TIME_VAR >= TREATMENT_TIME)
    # - Treated units (those in treatment_group == 1)
    # Examples: 2016, 2020, 2018


    # =========================================================================
    # OUTCOME VARIABLES - WHAT ARE YOU MEASURING?
    # =========================================================================
    # Dictionary: variable_name -> display_label
    OUTCOME_VARIABLES = {
        "profit_margin": "Profit Margin (%)",
        "total_assets": "Total Assets (log scale)",
        "debt_ratio": "Debt-to-Asset Ratio",
        # CUSTOMIZE THIS: Add your own dependent variables
        # Examples: "roa": "Return on Assets", "revenue": "Revenue (log)"
    }


    # =========================================================================
    # CONTROL VARIABLES - WHAT COVARIATES SHOULD WE INCLUDE?
    # =========================================================================
    # These will be added in the "with controls" specification
    CONTROL_VARIABLES = [
        "firm_size",
        "leverage",
        "liquidity",
        # CUSTOMIZE THIS: Add your own control variables
        # Leave empty [] for baseline specification without controls
    ]


    # =========================================================================
    # FIXED EFFECTS - UNIT AND TIME FIXED EFFECTS
    # =========================================================================
    # Standard DiD design includes both unit and time fixed effects
    # Prevents confounding from time trends and permanent unit characteristics
    INCLUDE_UNIT_FE = True  # Include unit fixed effects (firm/person/region FE)
    INCLUDE_TIME_FE = True  # Include time fixed effects (year/quarter FE)


    # =========================================================================
    # STANDARD ERROR CLUSTERING
    # =========================================================================
    CLUSTER_VAR = "firm_id"
    # CUSTOMIZE THIS: Variable to cluster standard errors on
    # Typically the unit identifier (firm, individual, etc.)
    # Leave None for HC1 robust standard errors


    # =========================================================================
    # EVENT STUDY ANALYSIS (OPTIONAL) - DYNAMIC TREATMENT EFFECTS
    # =========================================================================
    RUN_EVENT_STUDY = True
    # Set to False if you don't need leads/lags analysis

    PERIODS_BEFORE = 4
    # Number of periods before treatment to include in leads specification
    # CUSTOMIZE THIS: 3-5 is typical for quarterly data, 5-10 for annual

    PERIODS_AFTER = 4
    # Number of periods after treatment to include in lags specification

    REFERENCE_PERIOD = -1
    # Reference period for event study (typically -1, the period before treatment)
    # Coefficients are interpreted relative to this period


    # =========================================================================
    # SAMPLE RESTRICTIONS - FILTER YOUR DATA
    # =========================================================================
    # Useful for robustness checks: exclude treatment year, require balanced panel, etc.
    MIN_OBSERVATIONS_PER_UNIT = 0
    # Minimum observations required per unit (0 = no restriction)
    # CUSTOMIZE THIS: Set to enforce balanced panel (e.g., set to 20 for 20 years)

    MIN_TIME_PERIODS = 0
    # Minimum number of unique time periods required (0 = no restriction)


    # =========================================================================
    # OUTPUT CONFIGURATION
    # =========================================================================
    OUTPUT_DIR = "Results/Tables/"
    # Directory where LaTeX tables will be saved

    FIGURES_DIR = "Results/Figures/"
    # Directory where figures (PNG/PDF) will be saved

    PROJECT_NAME = "MyProject"
    # CUSTOMIZE THIS: Used in figure/table filenames for organization


    # =========================================================================
    # VARIABLE LABELS FOR PROFESSIONAL TABLES
    # =========================================================================
    # Maps variable names to publication-ready labels
    VARIABLE_LABELS = {
        "post_treatment": "Post-Treatment",
        "treated": "Treated Unit",
        "did": "Treatment × Post",
        # CUSTOMIZE THIS: Add labels for your variables
        # Example: "ln_size": "Log(Firm Size)"
    }

    # For control variables
    CONTROL_LABELS = {
        "firm_size": "Firm Size",
        "leverage": "Leverage",
        "liquidity": "Liquidity Ratio",
        # CUSTOMIZE THIS: Add labels for control variables
    }

# endregion


# =============================================================================
# DERIVED CONFIGURATION - AUTO-CALCULATED (DON'T MODIFY)
# =============================================================================

def create_treatment_indicators(df: pd.DataFrame, config: DidConfig) -> pd.DataFrame:
    """
    Create binary treatment indicators from raw data.

    Creates three new columns:
    - post_treatment: Binary indicator for periods >= treatment time
    - treated: Binary indicator for units in treatment group
    - did: Interaction term (post_treatment * treated)

    Args:
        df: Input DataFrame
        config: DidConfig with treatment definitions

    Returns:
        DataFrame with treatment indicators added
    """
    df = df.copy()

    # Create post-treatment indicator
    df['post_treatment'] = (df[config.TIME_VAR] >= config.TREATMENT_TIME).astype(int)

    # Create treated group indicator (assuming GROUP_VAR is already 0/1)
    if config.GROUP_VAR in df.columns:
        df['treated'] = df[config.GROUP_VAR].astype(int)
    else:
        raise ValueError(f"Treatment group variable '{config.GROUP_VAR}' not found in data")

    # Create DiD interaction term
    df['did'] = df['post_treatment'] * df['treated']

    return df


def create_sequential_time_variable(df: pd.DataFrame, config: DidConfig) -> pd.DataFrame:
    """
    Create sequential time variable (1, 2, 3, ...) for event study analysis.

    Useful for handling non-contiguous time periods and interpreting
    event study coefficients as leads/lags relative to treatment.

    Args:
        df: Input DataFrame
        config: DidConfig with time variable

    Returns:
        DataFrame with 'time_seq' column added
    """
    df = df.copy()
    unique_times = sorted(df[config.TIME_VAR].unique())
    time_mapping = {t: i+1 for i, t in enumerate(unique_times)}
    df['time_seq'] = df[config.TIME_VAR].map(time_mapping)
    return df


# =============================================================================
# DATA LOADING AND PREPARATION FUNCTIONS
# =============================================================================

def load_data(config: DidConfig) -> pd.DataFrame:
    """
    Load data from file (supports .parquet, .csv, .xlsx, .dta).

    Args:
        config: DidConfig with DATA_PATH specified

    Returns:
        Loaded DataFrame

    Raises:
        FileNotFoundError: If data file doesn't exist
        ValueError: If file format not supported
    """
    path = Path(config.DATA_PATH)

    if not path.exists():
        raise FileNotFoundError(
            f"Data file not found: {config.DATA_PATH}\n"
            f"Please set DATA_PATH to your actual data file location."
        )

    print(f"\n[LOAD] Loading data from: {config.DATA_PATH}")

    if path.suffix == ".parquet":
        df = pd.read_parquet(path)
    elif path.suffix == ".csv":
        df = pd.read_csv(path)
    elif path.suffix == ".xlsx":
        df = pd.read_excel(path)
    elif path.suffix == ".dta":
        df = pd.read_stata(path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")

    print(f"   Loaded: {df.shape[0]:,} observations × {df.shape[1]} variables")
    return df


def validate_data(df: pd.DataFrame, config: DidConfig) -> Tuple[bool, List[str]]:
    """
    Validate that required variables exist in the data.

    Args:
        df: Input DataFrame
        config: DidConfig with variable specifications

    Returns:
        Tuple: (is_valid: bool, errors: List[str])
    """
    errors = []
    required_vars = [config.UNIT_ID, config.TIME_VAR, config.GROUP_VAR]

    for var in required_vars:
        if var not in df.columns:
            errors.append(f"Missing required variable: '{var}'")

    for outcome in config.OUTCOME_VARIABLES.keys():
        if outcome not in df.columns:
            errors.append(f"Missing outcome variable: '{outcome}'")

    for control in config.CONTROL_VARIABLES:
        if control not in df.columns:
            errors.append(f"Missing control variable: '{control}'")

    return len(errors) == 0, errors


def prepare_data(df: pd.DataFrame, config: DidConfig) -> pd.DataFrame:
    """
    Prepare data for analysis:
    1. Validate required variables exist
    2. Create treatment indicators
    3. Create sequential time variable
    4. Handle missing values
    5. Replace infinite values
    6. Apply sample restrictions

    Args:
        df: Raw input DataFrame
        config: DidConfig with analysis settings

    Returns:
        Cleaned DataFrame ready for analysis
    """
    print("\n" + "=" * 80)
    print("DATA PREPARATION")
    print("=" * 80)

    # Validate required variables
    is_valid, errors = validate_data(df, config)
    if not is_valid:
        print("\n[ERROR] Data validation failed:")
        for error in errors:
            print(f"   - {error}")
        raise ValueError("Data validation failed. Check variable names in DidConfig.")
    print("\n[OK] All required variables present")

    # Create treatment indicators
    df = create_treatment_indicators(df, config)
    print("[OK] Created treatment indicators (post_treatment, treated, did)")

    # Create sequential time variable
    df = create_sequential_time_variable(df, config)
    print("[OK] Created sequential time variable")

    # Display data overview
    print(f"\n[INFO] Data Overview:")
    print(f"   Time periods: {df[config.TIME_VAR].nunique()} unique")
    print(f"   Units: {df[config.UNIT_ID].nunique():,} unique")
    print(f"   Total observations: {len(df):,}")
    print(f"   Treatment period: {config.TREATMENT_TIME}")

    # Replace infinite values with NaN
    print(f"\n[CLEAN] Handling infinite and missing values...")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].replace([np.inf, -np.inf], np.nan)

    # Count missing values before dropping
    all_analysis_vars = (
        list(config.OUTCOME_VARIABLES.keys()) +
        config.CONTROL_VARIABLES +
        ['did', 'post_treatment', 'treated']
    )
    missing_before = df[all_analysis_vars].isna().sum().sum()

    # Drop rows with missing analysis variables
    df_clean = df.dropna(subset=all_analysis_vars, how='any').copy()
    dropped = len(df) - len(df_clean)

    print(f"   Dropped {dropped:,} observations with missing values ({missing_before} missing data points)")
    print(f"   Final clean dataset: {len(df_clean):,} observations")

    # Apply sample restrictions
    if config.MIN_OBSERVATIONS_PER_UNIT > 0:
        obs_per_unit = df_clean.groupby(config.UNIT_ID).size()
        units_to_keep = obs_per_unit[obs_per_unit >= config.MIN_OBSERVATIONS_PER_UNIT].index
        df_clean = df_clean[df_clean[config.UNIT_ID].isin(units_to_keep)]
        print(f"   Sample restriction applied: {len(units_to_keep)} units with >= {config.MIN_OBSERVATIONS_PER_UNIT} obs")

    # Summary statistics for treatment variables
    print(f"\n[TREATMENT BALANCE]")
    print(f"   Treated observations: {df_clean['treated'].sum():,} ({df_clean['treated'].mean()*100:.1f}%)")
    print(f"   Post-treatment observations: {df_clean['post_treatment'].sum():,} ({df_clean['post_treatment'].mean()*100:.1f}%)")
    print(f"   DiD (treated × post): {df_clean['did'].sum():,} ({df_clean['did'].mean()*100:.1f}%)")

    return df_clean


# =============================================================================
# REGRESSION ANALYSIS FUNCTIONS
# =============================================================================

def run_did_analysis(df: pd.DataFrame, config: DidConfig) -> Dict:
    """
    Run 2x2 difference-in-differences regression models.

    For each outcome variable, estimates two models:
    1. Baseline: DiD + Fixed Effects
    2. With Controls: DiD + Controls + Fixed Effects

    Args:
        df: Prepared DataFrame
        config: DidConfig with analysis settings

    Returns:
        Dictionary of models for each outcome
    """
    if not PYFIXEST_AVAILABLE:
        print("[ERROR] PyFixest not available. Install with: pip install pyfixest")
        return {}

    print("\n" + "=" * 80)
    print("DIFFERENCE-IN-DIFFERENCES ANALYSIS")
    print("=" * 80)

    # Build fixed effects specification
    fe_spec = []
    if config.INCLUDE_UNIT_FE:
        fe_spec.append(config.UNIT_ID)
    if config.INCLUDE_TIME_FE:
        fe_spec.append(config.TIME_VAR)

    fe_string = " + ".join(fe_spec) if fe_spec else ""

    models_dict = {}

    for outcome, outcome_label in config.OUTCOME_VARIABLES.items():
        print(f"\n[REGRESSION] {outcome_label}:")

        # Model 1: Baseline (DiD + FE)
        formula_1 = f"{outcome} ~ did"
        if fe_string:
            formula_1 += f" | {fe_string}"

        try:
            model_1 = pf.feols(
                formula_1,
                data=df,
                vcov={"CRV1": config.CLUSTER_VAR} if config.CLUSTER_VAR else None
            )
            coef_1 = model_1.coef().get('did', np.nan)
            se_1 = model_1.se().get('did', np.nan)
            print(f"   [1] Baseline: β = {coef_1:.4f} (SE = {se_1:.4f})")
        except Exception as e:
            print(f"   [ERROR] Model 1 failed: {str(e)}")
            model_1 = None

        # Model 2: With Controls
        if config.CONTROL_VARIABLES:
            controls_str = " + ".join(config.CONTROL_VARIABLES)
            formula_2 = f"{outcome} ~ did + {controls_str}"
            if fe_string:
                formula_2 += f" | {fe_string}"

            try:
                model_2 = pf.feols(
                    formula_2,
                    data=df,
                    vcov={"CRV1": config.CLUSTER_VAR} if config.CLUSTER_VAR else None
                )
                coef_2 = model_2.coef().get('did', np.nan)
                se_2 = model_2.se().get('did', np.nan)
                print(f"   [2] With controls: β = {coef_2:.4f} (SE = {se_2:.4f})")
            except Exception as e:
                print(f"   [ERROR] Model 2 failed: {str(e)}")
                model_2 = None
        else:
            model_2 = None
            print(f"   [2] Skipped (no control variables)")

        models_dict[outcome] = {
            'baseline': model_1,
            'with_controls': model_2
        }

    return models_dict


def run_event_study(df: pd.DataFrame, config: DidConfig) -> Dict:
    """
    Run dynamic DiD analysis (event study with leads/lags).

    Creates leads and lags relative to treatment to estimate treatment
    effects at each period before and after treatment.

    Args:
        df: Prepared DataFrame with time_seq variable
        config: DidConfig with event study settings

    Returns:
        Dictionary of dynamic models for each outcome
    """
    if not PYFIXEST_AVAILABLE or not config.RUN_EVENT_STUDY:
        return {}

    print("\n" + "=" * 80)
    print("EVENT STUDY (DYNAMIC EFFECTS) ANALYSIS")
    print("=" * 80)

    # Calculate reference period
    if 'time_seq' not in df.columns:
        df = create_sequential_time_variable(df, config)

    # Find treatment period in sequential time
    treatment_rows = df[df[config.TIME_VAR] == config.TREATMENT_TIME]
    if len(treatment_rows) == 0:
        print("[WARNING] Treatment period not found in data. Skipping event study.")
        return {}

    treatment_seq = treatment_rows['time_seq'].iloc[0]
    ref_seq = treatment_seq + config.REFERENCE_PERIOD

    print(f"\n[CONFIG]")
    print(f"   Treatment period: {config.TREATMENT_TIME} (sequential: {treatment_seq})")
    print(f"   Reference period: {ref_seq}")
    print(f"   Window: {config.PERIODS_BEFORE} periods before to {config.PERIODS_AFTER} after")

    # Build fixed effects specification
    fe_spec = []
    if config.INCLUDE_UNIT_FE:
        fe_spec.append(config.UNIT_ID)
    if config.INCLUDE_TIME_FE:
        fe_spec.append(config.TIME_VAR)

    fe_string = " + ".join(fe_spec) if fe_spec else ""

    models_dict = {}

    for outcome, outcome_label in config.OUTCOME_VARIABLES.items():
        print(f"\n[REGRESSION] {outcome_label} - Dynamic Effects:")

        # Dynamic formula: i(time_seq, treated, ref=ref_seq)
        # This creates coefficients for each time period
        formula = f"{outcome} ~ i(time_seq, treated, ref={ref_seq})"
        if fe_string:
            formula += f" | {fe_string}"

        try:
            model = pf.feols(
                formula,
                data=df,
                vcov={"CRV1": config.CLUSTER_VAR} if config.CLUSTER_VAR else None
            )

            # Count dynamic coefficients
            coef_names = [n for n in model._coefnames if 'time_seq' in n]
            print(f"   [OK] Estimated {len(coef_names)} dynamic effect coefficients")

            models_dict[outcome] = model
        except Exception as e:
            print(f"   [ERROR] Event study failed: {str(e)}")
            models_dict[outcome] = None

    return models_dict


# =============================================================================
# OUTPUT GENERATION FUNCTIONS
# =============================================================================

def generate_summary_statistics(df: pd.DataFrame, config: DidConfig) -> pd.DataFrame:
    """
    Generate summary statistics table for key analysis variables.

    Args:
        df: Analysis DataFrame
        config: DidConfig with variable specifications

    Returns:
        Summary statistics DataFrame
    """
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    all_vars = list(config.OUTCOME_VARIABLES.keys()) + config.CONTROL_VARIABLES + ['treated']

    summary_stats = []
    for var in all_vars:
        if var in df.columns:
            stats = {
                'Variable': config.VARIABLE_LABELS.get(var, var),
                'Mean': df[var].mean(),
                'Std Dev': df[var].std(),
                '25%ile': df[var].quantile(0.25),
                'Median': df[var].quantile(0.50),
                '75%ile': df[var].quantile(0.75),
                'N': df[var].notna().sum()
            }
            summary_stats.append(stats)

    summary_df = pd.DataFrame(summary_stats)
    print(f"\n[OK] Generated summary statistics for {len(summary_df)} variables")
    print(summary_df.to_string(index=False))

    return summary_df


def save_latex_table(summary_df: pd.DataFrame, config: DidConfig) -> None:
    """
    Save summary statistics as LaTeX table.

    Args:
        summary_df: Summary statistics DataFrame
        config: DidConfig with output directory
    """
    Path(config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    filename = f"{config.PROJECT_NAME}_summary_statistics.tex"
    filepath = Path(config.OUTPUT_DIR) / filename

    latex_table = summary_df.to_latex(
        index=False,
        float_format="%.3f",
        escape=False,
        bold_rows=False
    )

    # Wrap in professional table environment
    full_table = f"""
\\begin{{table}}[h!]
\\centering
\\caption{{Summary Statistics}}
\\label{{tab:summary_stats}}
\\begin{{tabular}}{{lrrrrrr}}
\\toprule
{latex_table.split('\\bottomrule')[0].split('\\toprule')[1]}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""

    filepath.write_text(full_table)
    print(f"\n[OUTPUT] Summary statistics saved to: {filepath}")


def create_event_study_plot(model, config: DidConfig, outcome: str) -> None:
    """
    Create event study plot from dynamic model.

    Shows coefficients and confidence intervals across leads/lags.

    Args:
        model: PyFixest feols model from event study
        config: DidConfig with output directory
        outcome: Outcome variable name
    """
    if not MATPLOTLIB_AVAILABLE or model is None:
        return

    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        # Extract coefficients and standard errors for plotting
        coefs = model.coef()
        ses = model.se()

        # Filter to time-treatment interaction terms
        coef_names = [n for n in coefs.index if 'time_seq' in n]
        if not coef_names:
            return

        coef_values = [coefs.get(n, 0) for n in coef_names]
        se_values = [ses.get(n, 0) for n in coef_names]

        # Plot with confidence intervals
        x_pos = np.arange(len(coef_values))
        ax.errorbar(x_pos, coef_values, yerr=1.96*np.array(se_values),
                   fmt='o', markersize=8, capsize=5, capthick=2)
        ax.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        ax.set_xlabel("Time Period")
        ax.set_ylabel("Treatment Effect")
        ax.set_title(f"Event Study: {config.OUTCOME_VARIABLES.get(outcome, outcome)}")
        ax.grid(True, alpha=0.3)

        # Save figure
        Path(config.FIGURES_DIR).mkdir(parents=True, exist_ok=True)
        filepath = Path(config.FIGURES_DIR) / f"{config.PROJECT_NAME}_{outcome}_event_study.png"
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"[OUTPUT] Event study plot saved to: {filepath}")
    except Exception as e:
        print(f"[WARNING] Could not create event study plot: {str(e)}")


# =============================================================================
# MAIN EXECUTION FUNCTION
# =============================================================================

def main(config: Optional[DidConfig] = None) -> None:
    """
    Execute complete DiD analysis workflow.

    Args:
        config: DidConfig object (uses default if None)
    """
    if config is None:
        config = DidConfig()

    print("\n" + "=" * 80)
    print("DIFFERENCE-IN-DIFFERENCES ANALYSIS")
    print("=" * 80)

    try:
        # Load and prepare data
        df_raw = load_data(config)
        df_clean = prepare_data(df_raw, config)

        # Run analyses
        did_models = run_did_analysis(df_clean, config)
        event_models = run_event_study(df_clean, config)

        # Generate outputs
        summary_stats = generate_summary_statistics(df_clean, config)
        save_latex_table(summary_stats, config)

        # Create figures
        for outcome in config.OUTCOME_VARIABLES.keys():
            if outcome in event_models and event_models[outcome] is not None:
                create_event_study_plot(event_models[outcome], config, outcome)

        # Summary
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"\nOutputs saved to:")
        print(f"  Tables: {config.OUTPUT_DIR}")
        print(f"  Figures: {config.FIGURES_DIR}")
        print(f"\nNext steps:")
        print(f"  1. Include LaTeX tables in your manuscript with \\input{{path/to/table.tex}}")
        print(f"  2. Include figures with \\includegraphics{{path/to/figure.png}}")
        print(f"  3. Modify DidConfig for robustness checks (different time windows, etc.)")

    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {str(e)}")
        raise


# =============================================================================
# EXAMPLE: HOW TO CUSTOMIZE FOR YOUR RESEARCH
# =============================================================================

"""
CUSTOMIZATION GUIDE:

1. Update data path:
   config.DATA_PATH = "C:/path/to/your/data.parquet"

2. Map variables to your data:
   config.UNIT_ID = "company_id"
   config.TIME_VAR = "fiscal_year"
   config.GROUP_VAR = "received_treatment"

3. Specify treatment timing:
   config.TREATMENT_TIME = 2018

4. Define outcomes:
   config.OUTCOME_VARIABLES = {
       "revenue": "Revenue (log)",
       "profit": "Profit Margin",
       "employment": "Employment (log)"
   }

5. Specify controls:
   config.CONTROL_VARIABLES = ["size", "age", "debt_ratio"]

6. Run analysis:
   python example_did_analysis_template.py
"""


# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Create custom config for your analysis
    config = DidConfig()

    # Run analysis
    main(config)
