#!/usr/bin/env python3
"""
Variable Coverage Report with LaTeX Output
==========================================

Generate publication-quality coverage tables for academic papers.

Usage:
    python coverage_report.py --input data.parquet --output coverage.tex
    python coverage_report.py --input data.csv --output coverage.tex --by-year
"""

import argparse
import pandas as pd
from pathlib import Path


def generate_coverage_table(df, by_year=False):
    """Generate variable coverage statistics."""
    stats = []

    for col in df.columns:
        if col in ['year', 'quarter', 'datacqtr', 'date']:
            continue  # Skip time identifiers

        n_total = len(df)
        n_non_missing = df[col].notna().sum()
        pct_coverage = (n_non_missing / n_total * 100) if n_total > 0 else 0

        stats.append({
            'variable': col,
            'n_obs': n_total,
            'n_non_missing': n_non_missing,
            'coverage_pct': pct_coverage
        })

    return pd.DataFrame(stats).sort_values('coverage_pct', ascending=False)


def format_latex_table(stats_df, caption="Variable Coverage Report"):
    """Format coverage statistics as LaTeX table."""
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        f"\\caption{{{caption}}}",
        "\\label{tab:coverage}",
        "\\begin{tabular}{lrrc}",
        "\\toprule",
        "Variable & Observations & Non-Missing & Coverage \\\\",
        "\\midrule",
    ]

    for _, row in stats_df.iterrows():
        var_name = row['variable'].replace('_', '\\_')
        lines.append(
            f"{var_name} & {row['n_obs']:,} & {row['n_non_missing']:,} & "
            f"{row['coverage_pct']:.1f}\\% \\\\"
        )

    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Generate variable coverage report')
    parser.add_argument('--input', required=True, help='Input data file')
    parser.add_argument('--output', required=True, help='Output LaTeX file')
    parser.add_argument('--by-year', action='store_true', help='Generate by year')

    args = parser.parse_args()

    # Load data
    suffix = Path(args.input).suffix.lower()
    if suffix == '.parquet':
        df = pd.read_parquet(args.input)
    elif suffix == '.csv':
        df = pd.read_csv(args.input)
    else:
        df = pd.read_stata(args.input)

    # Generate coverage stats
    stats = generate_coverage_table(df, args.by_year)

    # Format as LaTeX
    latex_table = format_latex_table(stats)

    # Save
    Path(args.output).write_text(latex_table)
    print(f"✓ Coverage table saved to: {args.output}")
    print(f"  Total variables: {len(stats)}")
    print(f"  Average coverage: {stats['coverage_pct'].mean():.1f}%")


if __name__ == '__main__':
    main()
