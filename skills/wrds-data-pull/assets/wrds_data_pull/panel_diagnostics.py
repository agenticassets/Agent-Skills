"""
Panel Data Diagnostics Module
=============================

Functions for validating panel structure, detecting duplicates, and checking coverage.
"""

import pandas as pd
import numpy as np


def validate_panel(df, unit_id, time_id):
    """
    Comprehensive panel validation with balance, duplicates, and coverage checks.

    Parameters
    ----------
    df : pandas.DataFrame
        Panel dataset
    unit_id : str
        Column name for unit identifier (e.g., 'gvkey', 'permno')
    time_id : str
        Column name for time identifier (e.g., 'datacqtr', 'date')

    Returns
    -------
    dict
        Dictionary with validation results including panel_type, duplicates, coverage

    Examples
    --------
    >>> diag = validate_panel(df, unit_id='gvkey', time_id='datacqtr')
    >>> print(f"Panel type: {diag['panel_type']}")
    >>> print(f"Duplicates: {diag['n_duplicates']}")
    """
    results = {}

    # Panel balance
    results.update(check_panel_balance(df, unit_id, time_id))

    # Duplicates
    results.update(check_duplicates(df, unit_id, time_id))

    # Coverage
    results['coverage_summary'] = calculate_coverage(df)

    return results


def check_panel_balance(df, unit_id, time_id):
    """Check if panel is balanced and return structure metrics."""
    panel_structure = df.groupby(unit_id)[time_id].agg(['count', 'nunique'])

    n_units = df[unit_id].nunique()
    n_periods = df[time_id].nunique()
    total_obs = len(df)
    balanced_obs = n_units * n_periods

    balance_ratio = total_obs / balanced_obs if balanced_obs > 0 else 0

    if balance_ratio > 0.95:
        panel_type = "balanced"
    elif balance_ratio > 0.7:
        panel_type = "mostly_balanced"
    else:
        panel_type = "unbalanced"

    return {
        'panel_type': panel_type,
        'n_units': n_units,
        'n_periods': n_periods,
        'total_obs': total_obs,
        'expected_obs_if_balanced': balanced_obs,
        'balance_ratio': balance_ratio
    }


def check_duplicates(df, unit_id, time_id):
    """Identify duplicate observations on primary keys."""
    dup_counts = df.groupby([unit_id, time_id]).size()
    duplicates = dup_counts[dup_counts > 1]

    return {
        'has_duplicates': len(duplicates) > 0,
        'n_duplicates': len(duplicates),
        'duplicate_keys': duplicates.to_dict() if len(duplicates) > 0 else {}
    }


def calculate_coverage(df, threshold=0.25):
    """
    Calculate variable coverage statistics.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset to analyze
    threshold : float
        Threshold for high missing data (default 0.25 = 25%)

    Returns
    -------
    dict
        Coverage statistics by variable
    """
    missing_pct = (df.isnull().sum() / len(df))
    high_missing = missing_pct[missing_pct > threshold].sort_values(ascending=False)

    return {
        'high_missing_vars': high_missing.to_dict(),
        'avg_coverage': (1 - missing_pct.mean()),
        'n_complete_vars': (missing_pct == 0).sum()
    }


def detect_outliers(df, variable, method='iqr', multiplier=3):
    """
    Detect outliers using IQR or z-score method.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset
    variable : str
        Variable name to check
    method : str
        'iqr' or 'zscore'
    multiplier : float
        Multiplier for IQR (default 3) or z-score threshold

    Returns
    -------
    pandas.Series
        Boolean series indicating outliers
    """
    if method == 'iqr':
        Q1 = df[variable].quantile(0.25)
        Q3 = df[variable].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - multiplier * IQR
        upper = Q3 + multiplier * IQR
        return (df[variable] < lower) | (df[variable] > upper)
    elif method == 'zscore':
        z_scores = np.abs((df[variable] - df[variable].mean()) / df[variable].std())
        return z_scores > multiplier
    else:
        raise ValueError(f"Unknown method: {method}. Use 'iqr' or 'zscore'.")


def winsorize_variable(df, variable, lower=0.01, upper=0.99):
    """
    Winsorize variable at specified percentiles.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset
    variable : str
        Variable name
    lower : float
        Lower percentile (default 0.01 = 1%)
    upper : float
        Upper percentile (default 0.99 = 99%)

    Returns
    -------
    pandas.Series
        Winsorized variable
    """
    lower_val = df[variable].quantile(lower)
    upper_val = df[variable].quantile(upper)

    return df[variable].clip(lower=lower_val, upper=upper_val)
