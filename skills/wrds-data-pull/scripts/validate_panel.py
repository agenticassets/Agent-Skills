#!/usr/bin/env python3
"""
Panel Data Validation Script
============================

Comprehensive panel diagnostics: balance, duplicates, coverage, known issues.

Usage:
    python validate_panel.py --input data.parquet --unit_id gvkey --time_id datacqtr
    python validate_panel.py --input data.csv --unit_id permno --time_id date --output report.txt
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np


def detect_panel_balance(df, unit_id, time_id):
    """Classify panel as balanced or unbalanced."""
    panel_structure = df.groupby(unit_id)[time_id].agg(['count', 'nunique'])
    max_periods = panel_structure['nunique'].max()
    min_periods = panel_structure['nunique'].min()

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
        'type': panel_type,
        'n_units': n_units,
        'n_periods': n_periods,
        'total_obs': total_obs,
        'expected_obs': balanced_obs,
        'balance_ratio': balance_ratio,
        'min_periods_per_unit': min_periods,
        'max_periods_per_unit': max_periods,
    }


def detect_duplicates(df, unit_id, time_id):
    """Identify duplicate observations on primary keys."""
    duplicates = df.groupby([unit_id, time_id]).size()
    dup_keys = duplicates[duplicates > 1]

    if len(dup_keys) == 0:
        return {'has_duplicates': False, 'n_duplicate_keys': 0, 'sample': None}

    return {
        'has_duplicates': True,
        'n_duplicate_keys': len(dup_keys),
        'total_duplicate_obs': dup_keys.sum() - len(dup_keys),  # Extra obs
        'sample': dup_keys.head(10).to_dict()
    }


def coverage_report(df, unit_id, time_id):
    """Calculate missing data coverage statistics."""
    # Overall missingness
    missing_pct = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
    high_missing = missing_pct[missing_pct > 25]

    # Time-series coverage (obs per period)
    period_counts = df.groupby(time_id).size()

    return {
        'vars_with_high_missing': high_missing.to_dict() if len(high_missing) > 0 else {},
        'period_obs_min': period_counts.min(),
        'period_obs_max': period_counts.max(),
        'period_obs_mean': period_counts.mean(),
    }


def check_known_issues(df):
    """Flag common data quality issues."""
    issues = {}

    # Negative book equity
    if 'seq' in df.columns or 'seqq' in df.columns:
        seq_col = 'seqq' if 'seqq' in df.columns else 'seq'
        neg_equity = (df[seq_col] < 0).sum()
        issues['negative_book_equity'] = {
            'count': neg_equity,
            'pct': neg_equity / len(df) * 100
        }

    # Zero shares outstanding
    if 'csho' in df.columns or 'cshoq' in df.columns:
        csho_col = 'cshoq' if 'cshoq' in df.columns else 'csho'
        zero_shares = (df[csho_col] == 0).sum() + df[csho_col].isnull().sum()
        issues['zero_or_missing_shares'] = {
            'count': zero_shares,
            'pct': zero_shares / len(df) * 100
        }

    # Missing CUSIPs
    if 'cusip' in df.columns:
        missing_cusip = df['cusip'].isnull().sum()
        issues['missing_cusip'] = {
            'count': missing_cusip,
            'pct': missing_cusip / len(df) * 100
        }

    # Negative assets (data error)
    if 'at' in df.columns or 'atq' in df.columns:
        at_col = 'atq' if 'atq' in df.columns else 'at'
        neg_assets = (df[at_col] < 0).sum()
        if neg_assets > 0:
            issues['negative_assets'] = {
                'count': neg_assets,
                'pct': neg_assets / len(df) * 100,
                'note': 'DATA ERROR - investigate these observations'
            }

    return issues


def validate_panel(input_file, unit_id, time_id, output_file=None):
    """Run full panel validation suite."""
    # Load data
    print(f"Loading data from: {input_file}")
    suffix = Path(input_file).suffix.lower()

    if suffix == '.parquet':
        df = pd.read_parquet(input_file)
    elif suffix == '.csv':
        df = pd.read_csv(input_file)
    elif suffix == '.dta':
        df = pd.read_stata(input_file)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")

    print(f"Loaded {len(df):,} observations, {len(df.columns)} variables\n")

    # Validate column existence
    if unit_id not in df.columns:
        raise ValueError(f"Unit ID '{unit_id}' not found in data")
    if time_id not in df.columns:
        raise ValueError(f"Time ID '{time_id}' not found in data")

    # Run diagnostics
    results = []

    # 1. Panel balance
    results.append("=" * 70)
    results.append("PANEL STRUCTURE")
    results.append("=" * 70)
    balance = detect_panel_balance(df, unit_id, time_id)
    results.append(f"Panel type: {balance['type'].upper()}")
    results.append(f"Units: {balance['n_units']:,}")
    results.append(f"Periods: {balance['n_periods']:,}")
    results.append(f"Observations: {balance['total_obs']:,} / {balance['expected_obs']:,} expected")
    results.append(f"Balance ratio: {balance['balance_ratio']:.1%}")
    results.append(f"Periods per unit: {balance['min_periods_per_unit']} to {balance['max_periods_per_unit']}")

    # 2. Duplicates
    results.append("\n" + "=" * 70)
    results.append("DUPLICATE DETECTION")
    results.append("=" * 70)
    dups = detect_duplicates(df, unit_id, time_id)
    if dups['has_duplicates']:
        results.append(f"⚠ DUPLICATES FOUND: {dups['n_duplicate_keys']} unique keys")
        results.append(f"Total extra observations: {dups['total_duplicate_obs']}")
        results.append("\nSample duplicate keys (showing up to 10):")
        for key, count in dups['sample'].items():
            results.append(f"  {key}: {count} occurrences")
    else:
        results.append("✓ No duplicates detected")

    # 3. Coverage
    results.append("\n" + "=" * 70)
    results.append("DATA COVERAGE")
    results.append("=" * 70)
    coverage = coverage_report(df, unit_id, time_id)
    results.append(f"Observations per period: {coverage['period_obs_min']:,} to {coverage['period_obs_max']:,}")
    results.append(f"Average: {coverage['period_obs_mean']:.0f}")

    if coverage['vars_with_high_missing']:
        results.append("\nVariables with >25% missing data:")
        for var, pct in sorted(coverage['vars_with_high_missing'].items(),
                             key=lambda x: x[1], reverse=True)[:10]:
            results.append(f"  {var}: {pct:.1f}% missing")
    else:
        results.append("\n✓ No variables with >25% missing data")

    # 4. Known issues
    results.append("\n" + "=" * 70)
    results.append("KNOWN DATA ISSUES")
    results.append("=" * 70)
    issues = check_known_issues(df)
    if issues:
        for issue_name, issue_data in issues.items():
            results.append(f"\n{issue_name.replace('_', ' ').title()}:")
            results.append(f"  Count: {issue_data['count']:,} ({issue_data['pct']:.1f}%)")
            if 'note' in issue_data:
                results.append(f"  {issue_data['note']}")
    else:
        results.append("✓ No known issues detected")

    results.append("\n" + "=" * 70)

    # Output results
    output_text = "\n".join(results)
    print(output_text)

    if output_file:
        Path(output_file).write_text(output_text)
        print(f"\nReport saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Validate panel data structure and quality',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--input', required=True,
                       help='Input data file (parquet, csv, or dta)')
    parser.add_argument('--unit_id', required=True,
                       help='Unit identifier column (e.g., gvkey, permno)')
    parser.add_argument('--time_id', required=True,
                       help='Time identifier column (e.g., datacqtr, date)')
    parser.add_argument('--output', help='Output file for report (optional)')

    args = parser.parse_args()

    try:
        validate_panel(args.input, args.unit_id, args.time_id, args.output)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
