"""
Academic Figure Generator for PyFixest - STANDALONE VERSION
===========================================================

Professional publication-quality figure generation for academic publications.
Creates event study plots, treatment assignment visualizations, and coefficient comparisons.

This is a standalone version optimized for use in skill assets and libraries.
Simplified configuration without project root detection.

Author: AI Assistant
Date: 2024
"""

# =============================================================================
# ENCODING CONFIGURATION FOR WINDOWS COMPATIBILITY
# =============================================================================
import sys
import io

# Set UTF-8 encoding for Windows PowerShell compatibility
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# =============================================================================
# CONFIGURATION AND IMPORTS
# =============================================================================

import os
from pathlib import Path
from typing import List, Optional, Union, Any, Dict
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for saving
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
import pyfixest as pf
from scipy import stats

# Default output path (user should configure via set_figure_output_path)
OUTPUT_FIGURES = Path.cwd() / "output" / "figures"
OUTPUT_FIGURES.mkdir(parents=True, exist_ok=True)

# Global variable for output path (user can set this)
_OUTPUT_FIGURES_PATH = None

def set_figure_output_path(path: str) -> None:
    """
    Set the output path for saving figures.

    Parameters:
    -----------
    path : str
        Path where figures will be saved (absolute path recommended, or relative to current working directory)
    """
    global _OUTPUT_FIGURES_PATH

    path_obj = Path(path)

    # If absolute path provided, use it directly
    if path_obj.is_absolute():
        _OUTPUT_FIGURES_PATH = path_obj
    else:
        # If relative path, resolve relative to Path.cwd()
        path_obj = Path.cwd() / path_obj

    # Create directory if it doesn't exist
    path_obj.mkdir(parents=True, exist_ok=True)

    _OUTPUT_FIGURES_PATH = path_obj
    print(f"Figures will be saved to: {path_obj}")

def get_figure_output_path() -> Path:
    """Get the current output path for figures."""
    if _OUTPUT_FIGURES_PATH is not None:
        return _OUTPUT_FIGURES_PATH
    else:
        # Use the default output path
        return OUTPUT_FIGURES

# Academic style defaults
ACADEMIC_STYLE = {
    'figure.figsize': (10, 6),
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'font.size': 12,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'lines.linewidth': 2,
    'lines.markersize': 6,
    'errorbar.capsize': 4,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.transparent': False
}

# =============================================================================
# FUNCTION 1: Event Study Plots
# =============================================================================

def create_event_study_plot(
    model: Any,
    title: Optional[str] = None,
    filename: Optional[str] = None,
    time_var: str = "year",
    treat_var: str = "ever_treated",
    reference_period: int = 14,
    treatment_period: Optional[int] = None,
    style: str = "errorbar",
    colors: Optional[Dict[str, str]] = None,
    figsize: tuple = (12, 6),
    add_treatment_line: bool = True,
    confidence_level: float = 0.05,
    time_labels: str = "relative",
    signif_levels: List[float] = [0.01, 0.05, 0.1],
    **kwargs
) -> str:
    """
    Create professional event study plot for dynamic treatment effects.

    Perfect for: DiD with time-varying effects, staggered adoption designs,
    policy evaluation with dynamic responses.

    Parameters:
    -----------
    model : pf.FixestMulti
        Fitted PyFixest model with dynamic effects
    title : str, optional
        Plot title for academic presentation (no title if None)
    filename : str, optional
        Custom filename (auto-generated if None)
    time_var : str
        Name of time variable (default: "year")
    treat_var : str
        Name of treatment variable (default: "ever_treated")
    reference_period : int
        Reference period for dynamic effects (default: 14)
    treatment_period : int, optional
        Treatment period for consistent labeling (if None, uses reference_period)
    style : str
        Plot style: 'errorbar', 'filled', 'step' (default: 'errorbar')
    colors : dict, optional
        Custom color scheme for plot elements
    figsize : tuple
        Figure size (width, height) in inches
    add_treatment_line : bool
        Add vertical line at treatment time
    confidence_level : float
        Significance level for confidence intervals (default: 0.05 for 95% CI)
        Examples: 0.01 = 99% CI, 0.05 = 95% CI, 0.10 = 90% CI
        Note: Automatically uses t-distribution for small samples (n < 30) and
        normal distribution for large samples (n ≥ 30) to ensure proper inference.
    time_labels : str
        X-axis label format: "relative" (default) shows -2, -1, 0, 1, 2...
        or "actual" shows actual time periods
    signif_levels : List[float]
        Significance levels for confidence intervals

    Returns:
    --------
    str : Path to saved figure file

    Example:
    --------
    >>> dynamic_model = pf.feols("Y ~ i(year, ever_treated, ref=14) | unit + year", data)
    >>> create_event_study_plot(
    ...     dynamic_model,
    ...     title="ASC 842 Implementation Effects",  # Optional: no title if omitted
    ...     reference_period=44,  # Reference period
    ...     treatment_period=45,  # Actual treatment period for consistent labeling
    ...     style="filled",
    ...     confidence_level=0.01,  # 99% confidence intervals
    ...     time_labels="relative"  # Show -2, -1, 0, 1, 2... (default)
    ... )
    """
    print(f"Generating event study plot: {title if title else 'No title'}")

    # Set academic style defaults
    plt.rcParams.update(ACADEMIC_STYLE)
    plt.rcParams['figure.figsize'] = figsize

    # Extract sample size and parameter count from model for proper CI calculation
    try:
        n_obs = model.nobs if hasattr(model, 'nobs') else model._nobs
        k_params = model.k_params if hasattr(model, 'k_params') else len(model._coefnames)
    except:
        # Fallback: assume large sample if we can't get nobs
        n_obs = 1000
        k_params = 0
        print(f"   WARNING: Could not extract sample size from model. Assuming large sample (n={n_obs}).")

    # Calculate critical value using t-distribution for small samples, normal for large samples
    ci_level = int((1 - confidence_level) * 100)
    critical_value = _get_ci_critical_value(n_obs, k_params, alpha=confidence_level)
    print(f"   Using {ci_level}% confidence intervals (alpha = {confidence_level})")

    # Default colors
    if colors is None:
        colors = {
            'line': '#1f77b4',
            'fill': '#aec7e8',
            'zero_line': '#d62728',
            'treatment_line': '#2ca02c',
            'grid': '#cccccc'
        }

    # Extract coefficients and standard errors
    try:
        coefs = model.coef()
        se = model.se()
        coef_names = model._coefnames
    except:
        raise ValueError("Model must be a fitted PyFixest model with coef(), se(), and _coefnames attributes")

        # Extract time periods from coefficient names
    time_periods = []
    coef_indices = []

    for i, name in enumerate(coef_names):
        if time_var in name and treat_var in name:
            # Extract year from pattern like: C(year, contr.treatment(base=14))[15]:ever_treated
            if '[' in name and ']:' in name:
                year_str = name.split('[')[1].split(']')[0]
                try:
                    year_val = int(year_str)
                    if year_val != reference_period:  # Skip reference period from coefficients
                        time_periods.append(year_val)
                        coef_indices.append(i)
                except ValueError:
                    continue

    if not time_periods:
        raise ValueError(f"No dynamic coefficients found for {time_var} and {treat_var}")

    # Sort by time period
    sorted_indices = np.argsort(time_periods)
    time_periods = [time_periods[i] for i in sorted_indices]
    coef_values = [coefs.iloc[coef_indices[i]] for i in sorted_indices]
    se_values = [se.iloc[coef_indices[i]] for i in sorted_indices]

    # Add reference period with zero coefficient and zero standard error
    # Insert it at the correct position to maintain sorted order
    ref_insert_pos = 0
    for i, period in enumerate(time_periods):
        if period > reference_period:
            ref_insert_pos = i
            break
        ref_insert_pos = i + 1

    time_periods.insert(ref_insert_pos, reference_period)
    coef_values.insert(ref_insert_pos, 0.0)  # Reference period coefficient is 0
    se_values.insert(ref_insert_pos, 0.0)    # Reference period SE is 0

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Find the reference period index for special styling
    ref_idx = time_periods.index(reference_period) if reference_period in time_periods else None

    if style == 'errorbar':
        ci_values = [se * critical_value for se in se_values]
        ax.errorbar(time_periods, coef_values, yerr=ci_values,
                   fmt='o-', color=colors['line'], capsize=4, linewidth=2, markersize=6)

        # Highlight reference period with same marker style as others
        if ref_idx is not None:
            ax.errorbar([time_periods[ref_idx]], [coef_values[ref_idx]],
                       yerr=[ci_values[ref_idx]], fmt='o-', color=colors['line'],
                       capsize=4, linewidth=2, markersize=6, alpha=0.8)

    elif style == 'filled':
        # Main line
        ax.plot(time_periods, coef_values, 'o-', color=colors['line'],
               linewidth=2, markersize=6)
        # Confidence intervals
        ci_values = np.array(se_values) * critical_value
        ax.fill_between(time_periods,
                       np.array(coef_values) - ci_values,
                       np.array(coef_values) + ci_values,
                       alpha=0.3, color=colors['fill'])

        # Highlight reference period with same marker style as others
        if ref_idx is not None:
            ax.plot([time_periods[ref_idx]], [coef_values[ref_idx]],
                   'o-', color=colors['line'], linewidth=2, markersize=6, alpha=0.8)

    elif style == 'step':
        ax.step(time_periods, coef_values, where='mid', color=colors['line'],
               linewidth=2, markersize=6)
        ci_values = np.array(se_values) * critical_value
        ax.fill_between(time_periods,
                       np.array(coef_values) - ci_values,
                       np.array(coef_values) + ci_values,
                       alpha=0.2, color=colors['fill'], step='mid')

        # Highlight reference period with same marker style as others
        if ref_idx is not None:
            ax.plot([time_periods[ref_idx]], [coef_values[ref_idx]],
                   'o-', color=colors['line'], linewidth=2, markersize=6, alpha=0.8)

    # Add reference lines
    ax.axhline(y=0, color=colors['zero_line'], linestyle='--', alpha=0.7, linewidth=1.5)

    if add_treatment_line and treatment_period is not None:
        # Treatment line is at the actual treatment period position on the x-axis
        if time_labels == "relative":
            treatment_label = 'Treatment (t=0)'
        else:
            treatment_label = f'Treatment (t={treatment_period})'

        ax.axvline(x=treatment_period, color=colors['treatment_line'],
                  linestyle='--', alpha=0.7, linewidth=1.5)

    # Formatting
    ax.set_ylabel('Treatment Effect', fontsize=12, fontweight='bold')
    if title:  # Only add title if provided
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, color=colors['grid'])

    # Set x-ticks and labels
    ax.set_xticks(time_periods)

    if time_labels == "relative":
        # Create relative time labels (-2, -1, 0, 1, 2, etc.)
        # Use treatment_period if provided, otherwise fall back to reference_period
        base_period = treatment_period if treatment_period is not None else reference_period
        relative_labels = [t - base_period for t in time_periods]
        ax.set_xticklabels(relative_labels)
        ax.set_xlabel('Time Relative to Treatment (t)', fontsize=12, fontweight='bold')
    else:  # time_labels == "actual"
        # Use actual time periods as labels
        ax.set_xticklabels(time_periods)
        ax.set_xlabel('Time Period (t)', fontsize=12, fontweight='bold')

    # Legend
    legend_elements = []
    if add_treatment_line and treatment_period is not None:
        legend_elements.append(plt.Line2D([0], [0], color=colors['treatment_line'],
                                        linestyle='--', alpha=0.7, linewidth=1.5,
                                        label=treatment_label))

    # Add confidence interval note to legend
    if style in ['filled', 'step']:
        legend_elements.append(patches.Patch(color=colors['fill'], alpha=0.3,
                                           label=f'{ci_level}% Confidence Intervals'))
    elif style == 'errorbar':
        legend_elements.append(plt.Line2D([0], [0], color='gray', linewidth=0,
                                        marker='|', markersize=8,
                                        label=f'{ci_level}% Confidence Intervals'))

    if legend_elements:
        ax.legend(handles=legend_elements, loc='best', framealpha=0.9)

    plt.tight_layout()

    # Auto-generate filename if not provided
    if filename is None:
        if title:
            safe_title = title.replace(':', '').replace(' ', '_').lower()[:30]
            filename = f"{safe_title}_event_study.png"
        else:
            filename = "event_study_plot.png"

    # Save figure
    filepath = get_figure_output_path() / filename
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Saved: {filepath}")
    print(f"   File: {filename}")
    print(f"   Location: {filepath}")

    return str(filepath)

# =============================================================================
# FUNCTION 2: Treatment Assignment Visualization
# =============================================================================

def create_treatment_assignment_plot(
    data: pd.DataFrame,
    unit: str = "unit",
    time: str = "year",
    treat: str = "treat",
    title: Optional[str] = None,
    filename: Optional[str] = None,
    figsize: tuple = (10, 6),
    colors: Optional[Dict[str, str]] = None,
    **kwargs
) -> str:
    """
    Create professional treatment assignment visualization.

    Perfect for: Understanding treatment timing, staggered adoption patterns,
    visualizing treatment heterogeneity across units.

    Parameters:
    -----------
    data : pd.DataFrame
        Panel data with unit, time, and treatment variables
    unit : str
        Column name for unit identifier
    time : str
        Column name for time variable
    treat : str
        Column name for treatment indicator (0/1)
    title : str, optional
        Plot title for academic presentation (no title if None)
    filename : str, optional
        Custom filename (auto-generated if None)
    figsize : tuple
        Figure size (width, height) in inches
    colors : dict, optional
        Custom color scheme

    Returns:
    --------
    str : Path to saved figure file

    Example:
    --------
    >>> create_treatment_assignment_plot(
    ...     data=df,
    ...     title="ASC 842 Adoption Patterns",
    ...     unit="gvkey",
    ...     time="year",
    ...     treat="asc842_treated"
    ... )
    """
    print(f"Generating treatment assignment plot: {title if title else 'No title'}")

    # Set academic style defaults
    plt.rcParams.update(ACADEMIC_STYLE)
    plt.rcParams['figure.figsize'] = figsize

    # Default colors
    if colors is None:
        colors = {
            'treated': '#d62728',
            'untreated': '#1f77b4',
            'grid': '#cccccc'
        }

    # Create treatment timing matrix
    try:
        # Get unique units and time periods
        all_units = sorted(data[unit].unique())
        times = sorted(data[time].unique())

        # Calculate which units are ever treated and their first treatment period
        unit_treatment_status = data.groupby(unit)[treat].max().to_dict()

        # Calculate first treatment period for each unit (for sorting by timing)
        # For treated units: find the first period where treat == 1
        # For untreated units: assign a very large number so they sort to the bottom
        unit_first_treatment = {}
        for u in all_units:
            unit_data = data[data[unit] == u].sort_values(time)
            treated_periods = unit_data[unit_data[treat] > 0][time]
            if len(treated_periods) > 0:
                unit_first_treatment[u] = treated_periods.iloc[0]  # First treatment period
            else:
                unit_first_treatment[u] = float('inf')  # Never treated - sort to bottom

        # Sort units: treated units by first treatment period (earliest first), then untreated units
        treated_units = [u for u in all_units if unit_treatment_status.get(u, 0) > 0]
        untreated_units = [u for u in all_units if unit_treatment_status.get(u, 0) == 0]

        # Sort treated units by first treatment period (ascending: earliest treated first)
        treated_units_sorted = sorted(treated_units, key=lambda u: unit_first_treatment[u])

        # Combine: treated units (sorted by timing) + untreated units (at bottom)
        units = treated_units_sorted + untreated_units

        # Create treatment status matrix
        treatment_matrix = np.zeros((len(units), len(times)))

        for i, u in enumerate(units):
            unit_data = data[data[unit] == u].sort_values(time)
            for j, t in enumerate(times):
                treat_val = unit_data[unit_data[time] == t][treat].iloc[0] if len(unit_data[unit_data[time] == t]) > 0 else 0
                treatment_matrix[i, j] = treat_val

    except Exception as e:
        raise ValueError(f"Error processing data: {e}. Check column names and data types.")

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Create heatmap-style visualization
    im = ax.imshow(treatment_matrix, aspect='auto', cmap='RdYlBu_r',
                   vmin=0, vmax=1, alpha=0.8)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Treatment Status', fontsize=11, fontweight='bold')
    cbar.set_ticks([0, 1])
    cbar.set_ticklabels(['Untreated', 'Treated'])

    # Formatting
    ax.set_xlabel('Time Period', fontsize=12, fontweight='bold')
    ax.set_ylabel('Unit', fontsize=12, fontweight='bold')
    if title:  # Only add title if provided
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

    # Set tick labels (show subset for readability)
    n_units = len(units)
    n_times = len(times)

    if n_units > 20:
        unit_indices = np.linspace(0, n_units-1, 20, dtype=int)
        ax.set_yticks(unit_indices)
        ax.set_yticklabels([units[i] for i in unit_indices])
    else:
        ax.set_yticks(range(n_units))
        ax.set_yticklabels(units)

    if n_times > 20:
        time_indices = np.linspace(0, n_times-1, 10, dtype=int)
        ax.set_xticks(time_indices)
        ax.set_xticklabels([times[i] for i in time_indices])
    else:
        ax.set_xticks(range(n_times))
        ax.set_xticklabels(times)

    plt.tight_layout()

    # Auto-generate filename if not provided
    if filename is None:
        if title:
            safe_title = title.replace(':', '').replace(' ', '_').lower()[:30]
            filename = f"{safe_title}_treatment_assignment.png"
        else:
            filename = "treatment_assignment_plot.png"

    # Save figure
    filepath = get_figure_output_path() / filename
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Saved: {filepath}")
    print(f"   File: {filename}")
    print(f"   Location: {filepath}")

    return str(filepath)

# =============================================================================
# FUNCTION 3: Coefficient Comparison Plot
# =============================================================================

def create_coefficient_comparison_plot(
    models: List[Any],
    model_names: List[str],
    title: Optional[str] = None,
    filename: Optional[str] = None,
    figsize: tuple = (12, 8),
    colors: Optional[List[str]] = None,
    use_ci: bool = False,
    confidence_level: float = 0.05,
    **kwargs
) -> str:
    """
    Create professional coefficient comparison plot across multiple models.

    Perfect for: Robustness checks, alternative specifications, sensitivity analysis.

    Parameters:
    -----------
    models : List[pf.FixestMulti]
        List of fitted PyFixest models to compare
    model_names : List[str]
        Names for each model specification
    title : str, optional
        Plot title for academic presentation (no title if None)
    filename : str, optional
        Custom filename (auto-generated if None)
    figsize : tuple
        Figure size (width, height) in inches
    colors : List[str], optional
        Custom colors for each model
    use_ci : bool, optional
        If True, plot confidence intervals instead of standard errors (default: False)
    confidence_level : float, optional
        Significance level for confidence intervals when use_ci=True (default: 0.05 for 95% CI)
        Note: Automatically uses t-distribution for small samples (n < 30) and
        normal distribution for large samples (n ≥ 30) to ensure proper inference.

    Returns:
    --------
    str : Path to saved figure file

    Example:
    --------
    >>> models = [basic_model, robust_model, controls_model]
    >>> create_coefficient_comparison_plot(
    ...     models,
    ...     ["Basic DiD", "Robust SE", "With Controls"],
    ...     title="ASC 842 Effect Robustness",
    ...     use_ci=True,  # Plot 95% CIs instead of SEs
    ...     confidence_level=0.05
    ... )
    """
    print(f"Generating coefficient comparison plot: {title if title else 'No title'}")

    # Set academic style defaults
    plt.rcParams.update(ACADEMIC_STYLE)
    plt.rcParams['figure.figsize'] = figsize

    # Default colors
    if colors is None:
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

    # Extract coefficients and standard errors
    all_coefs = []
    all_se = []
    common_vars = set()

    for model in models:
        try:
            coefs = model.coef()
            se = model.se()
            coef_names = model._coefnames

            # Store coefficients by variable name
            model_coefs = {}
            model_se = {}

            for i, name in enumerate(coef_names):
                # Clean variable name (remove fixed effects indicators)
                clean_name = name.split('[')[0] if '[' in name else name
                model_coefs[clean_name] = coefs.iloc[i]
                model_se[clean_name] = se.iloc[i]

            all_coefs.append(model_coefs)
            all_se.append(model_se)
            common_vars.update(model_coefs.keys())

        except Exception as e:
            raise ValueError(f"Error extracting coefficients from model: {e}")

    # Find variables present in all models
    common_vars = [var for var in common_vars if all(var in model_coefs for model_coefs in all_coefs)]

    if not common_vars:
        raise ValueError("No common variables found across all models")

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Plot each model's coefficients
    y_positions = np.arange(len(common_vars))
    bar_height = 0.8 / len(models)

    for i, (model_coefs, model_se, model_name, model) in enumerate(zip(all_coefs, all_se, model_names, models)):
        coef_values = [model_coefs[var] for var in common_vars]
        se_values = [model_se[var] for var in common_vars]

        # Calculate error bars (either SE or CI)
        if use_ci:
            # Extract sample size for proper CI calculation
            try:
                n_obs = model.nobs if hasattr(model, 'nobs') else model._nobs
                k_params = model.k_params if hasattr(model, 'k_params') else len(model._coefnames)
            except:
                n_obs = 1000
                k_params = 0

            critical_value = _get_ci_critical_value(n_obs, k_params, alpha=confidence_level)
            error_values = [se * critical_value for se in se_values]
            ci_level = int((1 - confidence_level) * 100)
            error_label = f'{ci_level}% CI' if i == 0 else model_name
        else:
            error_values = se_values
            error_label = model_name

        # Calculate bar positions
        positions = y_positions + (i - len(models)/2 + 0.5) * bar_height

        # Plot bars with error bars
        ax.barh(positions, coef_values,
                height=bar_height,
                xerr=error_values,
                color=colors[i % len(colors)],
                alpha=0.8,
                capsize=3,
                label=error_label if i == 0 and use_ci else model_name)

    # Add zero line
    ax.axvline(x=0, color='black', linestyle='-', alpha=0.8, linewidth=1)

    # Formatting
    ax.set_yticks(y_positions)
    ax.set_yticklabels(common_vars)
    ax.set_xlabel('Coefficient Value', fontsize=12, fontweight='bold')
    if title:  # Only add title if provided
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, axis='x')
    ax.legend(loc='best', framealpha=0.9)

    plt.tight_layout()

    # Auto-generate filename if not provided
    if filename is None:
        if title:
            safe_title = title.replace(':', '').replace(' ', '_').lower()[:30]
            filename = f"{safe_title}_coefficient_comparison.png"
        else:
            filename = "coefficient_comparison_plot.png"

    # Save figure
    filepath = get_figure_output_path() / filename
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Saved: {filepath}")
    print(f"   File: {filename}")
    print(f"   Location: {filepath}")

    return str(filepath)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _get_ci_critical_value(n_obs: int, k_params: int = 0, alpha: float = 0.05) -> float:
    """
    Get critical value for confidence intervals using t-distribution for small samples,
    normal distribution for large samples.

    Statistical Rationale:
    ---------------------
    - For small samples (n < 30): Use t-distribution to account for uncertainty in estimating
      the population variance. The t-distribution has heavier tails, producing wider (more
      conservative) confidence intervals appropriate for limited data.
    - For large samples (n ≥ 30): Use normal distribution as the t-distribution converges
      to the standard normal distribution by the Central Limit Theorem.

    Degrees of Freedom:
    ------------------
    df = n_obs - k_params (sample size minus number of estimated parameters)

    Parameters:
    -----------
    n_obs : int
        Number of observations in the sample
    k_params : int, optional
        Number of estimated parameters (default: 0)
        For regression models, this is the number of coefficients including intercept
    alpha : float, optional
        Significance level for two-tailed test (default: 0.05 for 95% CI)
        Examples: 0.01 = 99% CI, 0.05 = 95% CI, 0.10 = 90% CI

    Returns:
    --------
    float
        Critical value (z-score or t-score) for constructing confidence intervals

    Examples:
    ---------
    >>> # Small sample: use t-distribution
    >>> _get_ci_critical_value(20, k_params=3, alpha=0.05)
    2.110  # t-score with df=17

    >>> # Large sample: use normal distribution
    >>> _get_ci_critical_value(100, k_params=3, alpha=0.05)
    1.960  # z-score (approximately)

    Notes:
    ------
    This follows standard statistical practice in econometrics textbooks:
    - Wooldridge (2020): Introductory Econometrics, Chapter 4
    - Stock & Watson (2020): Introduction to Econometrics, Chapter 5

    Impact on Inference:
    -------------------
    Small samples will have WIDER confidence intervals (more conservative),
    which properly reflects the greater uncertainty when estimating from limited data.
    """
    df = n_obs - k_params  # Degrees of freedom

    # For very small samples, ensure we have positive df
    if df < 1:
        df = 1
        print(f"   WARNING: Degrees of freedom < 1 (n={n_obs}, k={k_params}). Using df=1.")

    # Decision rule: Use t-distribution for small samples (n < 30)
    # This is conservative and follows standard statistical practice
    if n_obs < 30:
        critical_value = stats.t.ppf(1 - alpha / 2, df=df)
        print(f"   Small sample (n={n_obs}): Using t-distribution with df={df}, t={critical_value:.3f}")
    else:
        critical_value = stats.norm.ppf(1 - alpha / 2)
        print(f"   Large sample (n={n_obs}): Using normal distribution, z={critical_value:.3f}")

    return critical_value

def list_saved_figures() -> None:
    """List all saved figures in the output directory"""
    print("Saved Figures:")
    print("=" * 50)

    if not get_figure_output_path().exists():
        print("No figures directory found.")
        return

    image_files = list(get_figure_output_path().glob("*.png")) + list(get_figure_output_path().glob("*.pdf"))
    if not image_files:
        print("No image files found.")
        return

    for i, file_path in enumerate(sorted(image_files), 1):
        size = file_path.stat().st_size / 1024  # Size in KB
        print(f"{i:2d}. {file_path.name} ({size:.1f} KB)")

    print(f"\nLocation: {get_figure_output_path()}")

def clean_figure_directory(confirm: bool = True) -> None:
    """Clean all image files from the figure output directory"""
    if not get_figure_output_path().exists():
        print("No figures directory found.")
        return

    image_files = list(get_figure_output_path().glob("*.png")) + list(get_figure_output_path().glob("*.pdf"))
    if not image_files:
        print("No image files to clean.")
        return

    if confirm:
        response = input(f"Delete {len(image_files)} image files from {get_figure_output_path()}? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            return

    for file_path in image_files:
        file_path.unlink()
        print(f"Deleted: {file_path.name}")

    print(f"Cleaned {len(image_files)} files.")
