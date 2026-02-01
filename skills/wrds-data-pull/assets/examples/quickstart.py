"""
WRDS Data Pull - Quick Start Example
====================================

Minimal working example for pulling Compustat + CRSP data.
"""

import os
import wrds
from pathlib import Path

# Add wrds_data_pull to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from wrds_data_pull import (
    FinancialRatios,
    validate_panel,
    construct_financial_ratios
)


def quickstart_example():
    """
    Minimal example: Pull quarterly Compustat + CRSP, merge, validate, add ratios.
    """

    # 1. Connect to WRDS
    # Set WRDS_USERNAME environment variable or pass username
    username = os.getenv('WRDS_USERNAME')
    if not username:
        username = input("Enter WRDS username: ")

    print("Connecting to WRDS...")
    conn = wrds.Connection(wrds_username=username)

    # 2. Pull Compustat quarterly data (last 5 years, basic variables)
    print("Pulling Compustat data...")
    comp_query = """
    SELECT
        gvkey, cusip, datadate, datacqtr,
        atq, ltq, seqq, revtq, niq, cshoq, prccq
    FROM comp.fundq
    WHERE datadate >= '2019-01-01'
      AND indfmt = 'INDL'
      AND datafmt = 'STD'
      AND consol = 'C'
      AND popsrc = 'D'
    ORDER BY gvkey, datadate
    """
    compustat_df = conn.raw_sql(comp_query)
    print(f"  Retrieved {len(compustat_df):,} Compustat observations")

    # 3. Pull CRSP monthly data
    print("Pulling CRSP data...")

    # Get CUSIPs from Compustat for filtering
    cusips = compustat_df['cusip'].dropna().unique()
    cusip_filter = "', '".join(cusips[:1000])  # Limit for query size

    crsp_query = f"""
    SELECT
        a.permno, a.cusip, a.date, a.prc, a.ret, a.shrout
    FROM crsp.msf a
    WHERE a.date >= '2019-01-01'
      AND a.cusip IN ('{cusip_filter}')
    ORDER BY permno, date
    """
    crsp_df = conn.raw_sql(crsp_query)
    print(f"  Retrieved {len(crsp_df):,} CRSP observations")

    conn.close()

    # 4. Process CRSP: Add year/quarter for merging
    crsp_df['date'] = pd.to_datetime(crsp_df['date'])
    crsp_df['year'] = crsp_df['date'].dt.year
    crsp_df['quarter'] = crsp_df['date'].dt.quarter

    # Aggregate to quarterly (last observation in quarter)
    crsp_quarterly = (
        crsp_df
        .sort_values('date')
        .groupby(['permno', 'cusip', 'year', 'quarter'])
        .last()
        .reset_index()
    )

    # 5. Merge on CUSIP + calendar quarter
    print("Merging Compustat + CRSP...")

    # Extract year/quarter from datacqtr (format: YYYYQ)
    compustat_df['year'] = compustat_df['datacqtr'].astype(str).str[:4].astype(int)
    compustat_df['quarter'] = compustat_df['datacqtr'].astype(str).str[-1].astype(int)

    # Standardize CUSIP to 8 characters
    compustat_df['cusip8'] = compustat_df['cusip'].str[:8]
    crsp_quarterly['cusip8'] = crsp_quarterly['cusip'].str[:8]

    # Merge
    merged_df = compustat_df.merge(
        crsp_quarterly[['cusip8', 'year', 'quarter', 'permno', 'ret']],
        on=['cusip8', 'year', 'quarter'],
        how='left'
    )

    match_rate = merged_df['permno'].notna().mean()
    print(f"  Match rate: {match_rate:.1%}")
    print(f"  Final dataset: {len(merged_df):,} observations")

    # 6. Validate panel structure
    print("\nValidating panel...")
    diagnostics = validate_panel(merged_df, unit_id='gvkey', time_id='datacqtr')
    print(f"  Panel type: {diagnostics['panel_type']}")
    print(f"  Units: {diagnostics['n_units']:,}")
    print(f"  Periods: {diagnostics['n_periods']}")

    if diagnostics['has_duplicates']:
        print(f"  ⚠ Warning: {diagnostics['n_duplicates']} duplicate keys found")

    # 7. Add financial ratios
    print("\nConstructing financial ratios...")
    merged_df = construct_financial_ratios(
        merged_df,
        ratios=['tobins_q', 'leverage', 'roa', 'market_cap']
    )

    # 8. Save output
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / 'compustat_crsp_merged.parquet'
    merged_df.to_parquet(output_file)
    print(f"\n✓ Saved to: {output_file}")

    # Summary statistics
    print("\nSummary:")
    print(f"  Observations: {len(merged_df):,}")
    print(f"  Variables: {len(merged_df.columns)}")
    print(f"  Date range: {merged_df['datadate'].min()} to {merged_df['datadate'].max()}")
    print(f"  Unique firms (GVKEY): {merged_df['gvkey'].nunique():,}")
    print(f"  Unique stocks (PERMNO): {merged_df['permno'].nunique():,}")

    return merged_df


if __name__ == '__main__':
    import pandas as pd

    print("=" * 70)
    print("WRDS Data Pull - Quick Start Example")
    print("=" * 70)

    df = quickstart_example()

    print("\n" + "=" * 70)
    print("Complete! Dataset ready for analysis.")
    print("=" * 70)
