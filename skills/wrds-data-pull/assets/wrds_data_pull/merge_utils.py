"""
Merge and Process Data Module
==============================

This module handles merging Compustat and CRSP data, performing data cleaning,
creating calculated variables, winsorizing, and generating final outputs.

Usage:
    import config_wrds_data as cfg
    from merge_and_process_data import merge_and_process_data
    import pull_compustat_data
    import pull_crsp_data
    
    compustat_df, _ = pull_compustat_data.pull_compustat_data(cfg)
    crsp_quarterly_df = pull_crsp_data.pull_crsp_data(cfg, compustat_df)
    final_df = merge_and_process_data(cfg, compustat_df, crsp_quarterly_df)
"""

import pandas as pd
import numpy as np
import os
import importlib
from pathlib import Path
from typing import Optional

# Import config module (handles numbered filename)
cfg = importlib.import_module('1---config_wrds_data')


def parse_date_safe(date_str: str | pd.Timestamp | None) -> Optional[pd.Timestamp]:
    """Safely parse date string, handling 'E' (end date) and missing values."""
    if pd.isna(date_str) or date_str is None:
        return None
    if isinstance(date_str, pd.Timestamp):
        return date_str
    if isinstance(date_str, str):
        if date_str.upper() == 'E':  # 'E' means "current" (end date)
            return pd.Timestamp.max.replace(year=2100)  # Use far future as proxy
        try:
            return pd.to_datetime(date_str)
        except (ValueError, TypeError):
            return None
    return None


def load_linking_table(file_path: Path) -> pd.DataFrame:
    """
    Load and process CRSP-Compustat linking table.
    
    Parameters:
    -----------
    file_path : Path
        Path to the CRSP-Compustat linking CSV file
        
    Returns:
    --------
    DataFrame
        Processed linking table with columns: gvkey, permno, LINKDT_parsed, LINKENDDT_parsed
    """
    print(f"\nLoading CRSP-Compustat linking table: {file_path}")
    
    if not file_path.exists():
        raise FileNotFoundError(
            f"Linking table not found at: {file_path}\n"
            f"Please ensure the file exists in the expected location."
        )
    
    linking_df = pd.read_csv(file_path, low_memory=False)
    
    print(f"  Loaded {len(linking_df):,} linking records")
    print(f"  Columns: {list(linking_df.columns)}")
    
    # Validate required columns
    required_cols = ['gvkey', 'LPERMNO']
    missing_cols = [col for col in required_cols if col not in linking_df.columns]
    if missing_cols:
        raise ValueError(f"Linking table missing required columns: {missing_cols}")
    
    # Parse dates
    if 'LINKDT' in linking_df.columns:
        linking_df['LINKDT_parsed'] = linking_df['LINKDT'].apply(parse_date_safe)
    if 'LINKENDDT' in linking_df.columns:
        linking_df['LINKENDDT_parsed'] = linking_df['LINKENDDT'].apply(parse_date_safe)
    
    # Rename LPERMNO to permno for consistency
    if 'LPERMNO' in linking_df.columns:
        linking_df['permno'] = linking_df['LPERMNO'].astype('Int64')  # Nullable integer
    
    # Clean gvkey (keep as string for consistency)
    linking_df['gvkey'] = linking_df['gvkey'].astype(str).str.strip()
    
    print(f"  Unique gvkeys: {linking_df['gvkey'].nunique():,}")
    print(f"  Unique permnos: {linking_df['permno'].nunique():,}")
    
    # Return only the columns we need for merging
    linking_cols = ['gvkey', 'permno', 'LINKDT_parsed', 'LINKENDDT_parsed']
    if 'LINKDT_parsed' not in linking_df.columns:
        linking_cols.remove('LINKDT_parsed')
    if 'LINKENDDT_parsed' not in linking_df.columns:
        linking_cols.remove('LINKENDDT_parsed')
    
    return linking_df[linking_cols].copy()


def merge_and_process_data(config=None, compustat_df=None, crsp_quarterly_df=None):
    """
    Merge Compustat and CRSP data, perform cleaning and variable creation.
    
    Parameters:
    -----------
    config : module, optional
        Configuration module (defaults to config_wrds_data if None)
    compustat_df : DataFrame
        Compustat quarterly data
    crsp_quarterly_df : DataFrame, optional
        CRSP quarterly aggregated data (if None, will proceed with Compustat only)
        
    Returns:
    --------
    DataFrame
        Fully processed final dataset
    """
    if config is None:
        config = cfg
    
    if compustat_df is None:
        raise ValueError("compustat_df is required")
    
    print("="*60)
    print("USING COMPUSTAT AS PRIMARY DATASET")
    print("="*60)

    # Start with Compustat data as the master dataset
    final_df = compustat_df.copy()
    print(f"Starting with Compustat data: {len(final_df):,} observations from {final_df['gvkey'].nunique()} firms")

    # Ensure proper date formatting and time variables
    # IMPORTANT: Use Compustat's official calendar quarter identifier (datacqtr) for merging with CRSP
    # datacqtr is the official Compustat calendar quarter (e.g., "1979Q4"), which is more accurate
    # than deriving calendar quarters from fiscal quarter end dates (datadate)
    final_df['datadate'] = pd.to_datetime(final_df['datadate'])
    
    # Parse datacqtr to extract calendar year and quarter for merging with CRSP
    # datacqtr format: "YYYYQN" (e.g., "1979Q4" = 1979 Q4)
    if 'datacqtr' in final_df.columns:
        print("Using Compustat's official calendar quarter identifier (datacqtr) for date alignment")
        
        # Extract year and quarter from datacqtr (format: "YYYYQN")
        def parse_datacqtr(datacqtr_str):
            """Parse datacqtr string (e.g., '1979Q4') to extract year and quarter."""
            if pd.isna(datacqtr_str) or not isinstance(datacqtr_str, str):
                return None, None
            try:
                parts = datacqtr_str.split('Q')
                if len(parts) == 2:
                    year = int(parts[0])
                    quarter = int(parts[1])
                    return year, quarter
            except (ValueError, AttributeError):
                pass
            return None, None
        
        # Parse datacqtr to get calendar year and quarter
        parsed_dates = final_df['datacqtr'].apply(parse_datacqtr)
        final_df['year'] = parsed_dates.apply(lambda x: x[0] if x and x[0] is not None else None).astype('Int64')
        final_df['quarter'] = parsed_dates.apply(lambda x: x[1] if x and x[1] is not None else None).astype('Int64')
        
        # Handle any missing values by falling back to datadate extraction
        missing_mask = final_df['year'].isna() | final_df['quarter'].isna()
        if missing_mask.sum() > 0:
            print(f"  Warning: {missing_mask.sum()} observations missing datacqtr, using datadate fallback")
            final_df.loc[missing_mask, 'year'] = final_df.loc[missing_mask, 'datadate'].dt.year
            final_df.loc[missing_mask, 'quarter'] = final_df.loc[missing_mask, 'datadate'].dt.quarter
        
        # Create year_quarter string from parsed values
        final_df['year_quarter'] = final_df['year'].astype(str) + 'Q' + final_df['quarter'].astype(str)
        final_df['year_quarter_numeric'] = final_df['year'] * 10 + final_df['quarter']
        
        print(f"  Using datacqtr for calendar quarter alignment with CRSP")
        print(f"  Calendar quarters: {final_df['year_quarter'].nunique()} unique quarters")
        
    else:
        # Fallback: derive calendar quarters from fiscal quarter end dates if datacqtr not available
        print("Warning: datacqtr not found, deriving calendar quarters from fiscal quarter end dates")
        final_df['year'] = final_df['datadate'].dt.year
        final_df['quarter'] = final_df['datadate'].dt.quarter
        final_df['year_quarter'] = final_df['year'].astype(str) + 'Q' + final_df['quarter'].astype(str)
        final_df['year_quarter_numeric'] = final_df['year'] * 10 + final_df['quarter']
    
    # Keep fiscal quarter information for reference
    # datadate: fiscal quarter end date
    # datafqtr: fiscal quarter identifier (e.g., "1980Q2")
    # fqtr: fiscal quarter number (1-4)
    # fyearq: fiscal year
    print(f"  Fiscal quarters (datafqtr): {final_df['datafqtr'].nunique() if 'datafqtr' in final_df.columns else 0} unique fiscal quarters")
    print(f"  Calendar quarters (datacqtr): {final_df['datacqtr'].nunique() if 'datacqtr' in final_df.columns else 0} unique calendar quarters")

    # Remove duplicate columns (keep first occurrence)
    if final_df.columns.duplicated().any():
        print(f"Warning: Found duplicate columns, removing duplicates...")
        final_df = final_df.loc[:, ~final_df.columns.duplicated()]
        print(f"After removing duplicate columns: {len(final_df.columns)} columns")

    print(f"Compustat date range: {final_df['datadate'].min()} to {final_df['datadate'].max()}")
    print(f"Years covered: {final_df['year'].min()} to {final_df['year'].max()}")

    # Merge CRSP data if available
    if crsp_quarterly_df is not None:
        print("\n" + "="*60)
        print("MERGING CRSP DATA INTO COMPUSTAT USING LINKING TABLE")
        print("="*60)

        print(f"Loaded CRSP data: {len(crsp_quarterly_df):,} quarterly observations")
        print(f"CRSP date range: {crsp_quarterly_df['date'].min()} to {crsp_quarterly_df['date'].max()}")

        # Step 1: Load CRSP-Compustat linking table
        # Use global path configuration for raw data directory
        from config_paths import RAW_DATA_DIR
        linking_file_path = RAW_DATA_DIR / 'crsp-compustat-linking' / 'crsp-compustat-linking.csv'
        linking_df = load_linking_table(linking_file_path)

        # Step 2: Merge Compustat data with linking table on gvkey
        print("\nStep 1: Merging Compustat data with linking table on gvkey...")
        # Ensure gvkey is string type for consistent merging
        final_df['gvkey'] = final_df['gvkey'].astype(str).str.strip()
        
        # Merge with linking table (left join to keep all Compustat observations)
        final_df_with_links = pd.merge(
            final_df,
            linking_df,
            on='gvkey',
            how='left',
            suffixes=('', '_link')
        )
        
        print(f"  After linking merge: {len(final_df_with_links):,} observations")
        link_success = final_df_with_links['permno'].notna().mean() * 100
        print(f"  Linking success: {link_success:.1f}% of Compustat observations have permno matches")

        # Step 3: Validate dates fall within LINKDT-LINKENDDT ranges
        print("\nStep 2: Validating dates against LINKDT-LINKENDDT ranges...")
        date_valid_mask = pd.Series(True, index=final_df_with_links.index)
        
        if 'LINKDT_parsed' in final_df_with_links.columns:
            date_valid_mask = date_valid_mask & (
                final_df_with_links['LINKDT_parsed'].isna() | 
                (final_df_with_links['datadate'] >= final_df_with_links['LINKDT_parsed'])
            )
        
        if 'LINKENDDT_parsed' in final_df_with_links.columns:
            date_valid_mask = date_valid_mask & (
                final_df_with_links['LINKENDDT_parsed'].isna() | 
                (final_df_with_links['datadate'] <= final_df_with_links['LINKENDDT_parsed'])
            )
        
        date_valid_pct = date_valid_mask.mean() * 100
        print(f"  Date validation: {date_valid_pct:.1f}% of observations have valid date ranges")
        
        # Keep only valid links (where permno exists and dates are valid)
        valid_link_mask = final_df_with_links['permno'].notna() & date_valid_mask
        print(f"  Valid links (permno + date range): {valid_link_mask.sum():,} observations ({valid_link_mask.mean() * 100:.1f}%)")

        # Step 4: Merge with CRSP quarterly data on permno, year, quarter
        # NOTE: Both datasets use CALENDAR quarters (year, quarter) for proper alignment
        # - Compustat: calendar quarter from official datacqtr variable (e.g., "1979Q4")
        # - CRSP: calendar quarter derived from trading date (date)
        # The year and quarter columns are parsed from datacqtr for accurate calendar quarter matching
        print("\nStep 3: Merging with CRSP quarterly data on permno, year, quarter...")
        print("        (Both datasets use calendar quarters for proper alignment)")
        print("        (Compustat calendar quarters from datacqtr, CRSP from trading dates)")
        
        # Ensure permno is consistent type for merging
        crsp_quarterly_df['permno'] = crsp_quarterly_df['permno'].astype('Int64')
        final_df_with_links['permno'] = final_df_with_links['permno'].astype('Int64')
        
        # Merge with CRSP data using calendar quarters
        final_df = pd.merge(
            final_df_with_links,
            crsp_quarterly_df,
            on=['permno', 'year', 'quarter'],
            how='left',
            suffixes=('', '_crsp')
        )

        merge_success = final_df['permno'].notna().mean() * 100
        crsp_var_success = final_df['permno'].notna() & final_df['prc'].notna()
        crsp_var_success_pct = crsp_var_success.mean() * 100
        print(f"  CRSP merge success: {merge_success:.1f}% of Compustat observations matched")
        print(f"  CRSP data available: {crsp_var_success_pct:.1f}% of observations have CRSP variables")

        # Clean up linking table columns (no longer needed after merge)
        linking_cols_to_drop = ['LINKDT_parsed', 'LINKENDDT_parsed']
        for col in linking_cols_to_drop:
            if col in final_df.columns:
                final_df = final_df.drop(columns=[col])

        # Report on CRSP variable availability
        crsp_vars_in_final = [col for col in crsp_quarterly_df.columns if col in final_df.columns]
        print(f"\nCRSP variables in final dataset: {len(crsp_vars_in_final)}")
        print(f"CRSP variables: {crsp_vars_in_final}")

        # Show sample of key CRSP variables
        key_crsp_vars = ['permno', 'prc', 'ret_quarterly', 'retx_quarterly', 'vol', 'shrout', 'mktcap_crsp']
        available_key_vars = [var for var in key_crsp_vars if var in final_df.columns]
        if available_key_vars:
            print(f"\nKey CRSP variables coverage:")
            for var in available_key_vars:
                non_missing = final_df[var].notna().sum()
                pct_coverage = (non_missing / len(final_df)) * 100
                print(f"  {var}: {non_missing:,} obs ({pct_coverage:.1f}% coverage)")
    else:
        print("\nNo CRSP data available - proceeding with Compustat only")

    # Sort data by gvkey and datadate for proper ordering
    final_df = final_df.sort_values(['gvkey', 'datadate'])
    print(f"\nData sorted by GVKEY and date: {len(final_df):,} total observations")
    print(f"Final dataset columns: {len(final_df.columns)}")
    print(f"Final dataset firms: {final_df['gvkey'].nunique()}")
    if 'permno' in final_df.columns:
        print(f"CRSP coverage: {final_df['permno'].notna().sum():,} obs with CRSP data")

    # ========================================================================
    # DATA CLEANING AND VARIABLE CREATION
    # ========================================================================
    print("\n" + "="*60)
    print("DATA CLEANING AND VARIABLE CREATION")
    print("="*60)

    # Convert datadate to datetime format
    final_df['datadate'] = pd.to_datetime(final_df['datadate'])

    print(f"Starting dataset: {len(final_df):,} observations from {final_df['gvkey'].nunique()} firms")

    # Check SIC code distribution if available from Compustat merge
    if 'sic' in final_df.columns:
        print("\nSIC Code Distribution (real estate and related companies):")
        sic_counts = final_df['sic'].value_counts().head(15)
        print(sic_counts)
        print(f"\nExpected SIC codes: {sorted(config.SIC_FILTER)}")
        expected_sics = set(config.SIC_FILTER)
        actual_sics = set(final_df['sic'].dropna().astype(int).unique())
        print(f"SIC codes found in data: {sorted(actual_sics)}")
        missing_sics = expected_sics - actual_sics
        if missing_sics:
            print(f"Missing SIC codes: {sorted(missing_sics)}")
    else:
        print("\nNo SIC codes available (Compustat merge may not have worked)")

    print(f"Date range: {final_df['datadate'].min()} to {final_df['datadate'].max()}")

    # Sort data by gvkey and datadate
    final_df.sort_values(['gvkey', 'datadate'], inplace=True)

    # Remove duplicate entries if any
    print(f"Before duplicate removal: {len(final_df):,} observations")
    final_df.drop_duplicates(subset=['gvkey', 'datadate'], inplace=True)
    print(f"After duplicate removal: {len(final_df):,} observations")

    # Reset index
    final_df.reset_index(drop=True, inplace=True)

    # Handle missing values - focus on essential variables only
    print(f"\nBefore data filtering: {len(final_df):,} observations")

    # Check what Compustat variables we actually have
    compustat_vars_available = [col for col in ['atq', 'cshoq', 'ltq', 'niq', 'prccq', 'seqq', 'ceqq'] if col in final_df.columns]
    print(f"Available Compustat variables: {compustat_vars_available}")

    # Only filter on variables that actually exist
    # Filter only if we have essential Compustat data
    if 'gvkey' in final_df.columns:
        # Remove rows with missing gvkey (should not happen but safe check)
        initial_count = len(final_df)
        final_df = final_df[final_df['gvkey'].notna()]
        print(f"After removing missing GVKEYs: {len(final_df):,} observations (dropped {initial_count - len(final_df)})")

    # Check missing patterns for important variables
    important_vars = ['atq', 'cshoq', 'ltq', 'niq', 'prccq', 'seqq', 'ceqq', 'oibdpq']
    existing_important_vars = [var for var in important_vars if var in final_df.columns]
    print(f"\nMissing value patterns for important Compustat variables:")
    for var in existing_important_vars:
        missing_count = final_df[var].isna().sum()
        missing_pct = (missing_count / len(final_df)) * 100
        print(f"  {var}: {missing_count:,} missing ({missing_pct:.1f}%)")

    print(f"\nMissing value patterns for CRSP variables:")
    crsp_vars_check = ['permno', 'prc', 'ret_quarterly', 'vol', 'shrout', 'mktcap_crsp']
    existing_crsp_vars = [var for var in crsp_vars_check if var in final_df.columns]
    for var in existing_crsp_vars:
        missing_count = final_df[var].isna().sum()
        missing_pct = (missing_count / len(final_df)) * 100
        print(f"  {var}: {missing_count:,} missing ({missing_pct:.1f}%)")

    # Create additional financial ratios and variables - only if data is available
    print("\nCalculating financial ratios from available data...")

    # Create variables only if the required components exist
    if 'dlttq' in final_df.columns and 'dlcq' in final_df.columns:
        # Total Debt (Total Liabilities)
        final_df['td'] = final_df['dlttq'].fillna(0) + final_df['dlcq'].fillna(0)
        print("+ Total debt calculated")
    elif 'debt_at' in final_df.columns and 'assets' in final_df.columns:
        # Use REIT debt ratio if available
        final_df['td'] = final_df['debt_at'] * final_df['assets']
        print("+ Total debt calculated from REIT data")

    if 'prccq' in final_df.columns and 'cshoq' in final_df.columns:
        # Market Capitalization from Compustat
        final_df['mktcap'] = final_df['prccq'] * final_df['cshoq']
        print("+ Market cap calculated from Compustat")
    elif 'prc' in final_df.columns and 'shares' in final_df.columns:
        # Market Capitalization from REIT data
        final_df['mktcap'] = final_df['prc'] * final_df['shares']
        print("+ Market cap calculated from REIT data")

    # Enterprise Value (EV) - include preferred equity and minority interest when available
    if 'mktcap' in final_df.columns and 'td' in final_df.columns:
        pref_component = final_df['pstkq'].fillna(0) if 'pstkq' in final_df.columns else 0
        mib_component = final_df['mibq'].fillna(0) if 'mibq' in final_df.columns else 0
        cash_component = final_df['cheq'].fillna(0) if 'cheq' in final_df.columns else 0
        final_df['ev'] = final_df['mktcap'] + final_df['td'] + pref_component + mib_component - cash_component
        print("+ Enterprise value calculated (includes preferred + minority interest when available)")

    # ----------------------------------------------------------------------
    # REIT-specific profitability foundations (FFO/AFFO/NOI proxies)
    # ----------------------------------------------------------------------
    if 'ffoq' in final_df.columns:
        # FFO per share (quarterly)
        if 'cshoq' in final_df.columns:
            final_df['ffopsq'] = final_df['ffoq'] / final_df['cshoq']
            print("+ FFO per share (quarterly) calculated")

        # AFFO proxy: FFO minus maintenance CAPEX (approx using capxy)
        if 'capxy' in final_df.columns:
            final_df['affoq'] = final_df['ffoq'] - final_df['capxy'].fillna(0)
            if 'atq' in final_df.columns:
                final_df['affo_atq'] = final_df['affoq'] / final_df['atq']
        # FFO / assets
        if 'atq' in final_df.columns:
            final_df['ffo_atq'] = final_df['ffoq'] / final_df['atq']
            print("+ FFO/AT (quarterly) calculated")

    # NOI proxy (operating income before depreciation)
    if 'oibdpq' in final_df.columns:
        if 'atq' in final_df.columns:
            final_df['oibdp_atq'] = final_df['oibdpq'] / final_df['atq']
            print("+ NOI proxy / AT calculated")

    # Invested capital components for ROIC^{FFO}
    if all(col in final_df.columns for col in ['dlttq', 'dlcq', 'ceqq']):
        pref_component = final_df['pstkq'].fillna(0) if 'pstkq' in final_df.columns else 0
        mib_component = final_df['mibq'].fillna(0) if 'mibq' in final_df.columns else 0
        final_df['invested_capital_q'] = (
            final_df['dlttq'].fillna(0)
            + final_df['dlcq'].fillna(0)
            + pref_component
            + mib_component
            + final_df['ceqq'].fillna(0)
        )
        print("+ Invested capital (quarterly) calculated")

    # Leverage Ratios
    if 'td' in final_df.columns:
        if 'seqq' in final_df.columns:
            final_df['debt_equity_ratio'] = final_df['td'] / final_df['seqq']
            print("+ Debt-to-equity ratio calculated")
        
        if 'atq' in final_df.columns:
            final_df['debt_assets_ratio'] = final_df['td'] / final_df['atq']
            final_df['lev'] = final_df['debt_assets_ratio']  # Alias
            print("+ Debt-to-assets ratio calculated")
        elif 'assets' in final_df.columns:
            final_df['debt_assets_ratio'] = final_df['td'] / final_df['assets']
            final_df['lev'] = final_df['debt_assets_ratio']  # Alias
            print("+ Debt-to-assets ratio calculated from REIT data")

    # Return on Assets (ROA) - quarterly
    if 'niq' in final_df.columns and 'atq' in final_df.columns:
        final_df['roa'] = final_df['niq'] / final_df['atq']
        print("+ ROA calculated from Compustat")
    elif 'ni' in final_df.columns and 'assets' in final_df.columns:
        final_df['roa'] = final_df['ni'] / final_df['assets']
        print("+ ROA calculated from REIT data")

    # Return on Equity (ROE) - quarterly
    if 'niq' in final_df.columns and 'seqq' in final_df.columns:
        final_df['roe'] = final_df['niq'] / final_df['seqq']
        print("+ ROE calculated")

    # Earnings per Share (EPS) - quarterly
    if 'niq' in final_df.columns and 'cshoq' in final_df.columns:
        final_df['eps'] = final_df['niq'] / final_df['cshoq']
        print("+ EPS calculated")

    # Dividend Payout Ratio - quarterly
    if 'dvpspq' in final_df.columns:
        final_df['dividend_per_share'] = final_df['dvpspq']
        if 'eps' in final_df.columns:
            final_df['dividend_payout_ratio'] = final_df['dividend_per_share'] / final_df['eps']
            print("+ Dividend payout ratio calculated")

    # Price-to-Earnings Ratio (P/E) - quarterly
    if 'prccq' in final_df.columns and 'eps' in final_df.columns:
        final_df['pe_ratio'] = final_df['prccq'] / final_df['eps']
        print("+ P/E ratio calculated")

    # Additional Financial Ratios
    print("\nCalculating additional financial ratios...")

    # 1. Log of Size (ln_at)
    if 'atq' in final_df.columns:
        final_df['ln_at'] = np.log(final_df['atq'])
        print("+ Log assets calculated from Compustat")
    elif 'assets' in final_df.columns:
        final_df['ln_at'] = np.log(final_df['assets'])
        print("+ Log assets calculated from REIT data")

    # 4. Return on Assets (using operating income before depreciation)
    if 'oibdpq' in final_df.columns and 'atq' in final_df.columns:
        final_df['roa_oibdp'] = final_df['oibdpq'].fillna(0) / final_df['atq']
        print("+ ROA (operating) calculated")

    # 5. R&D Intensity (RDI)
    if 'xrdq' in final_df.columns and 'atq' in final_df.columns:
        final_df['RDI'] = final_df['xrdq'] / final_df['atq']
        final_df['RDI_no_fill'] = final_df['RDI'].copy()
        final_df['RDI'] = final_df['RDI'].fillna(0)
        print("+ R&D intensity calculated")

    # 6. Tobin's Q - quarterly version
    if 'atq' in final_df.columns and 'mktcap' in final_df.columns:
        if 'seqq' in final_df.columns:
            final_df['tbq'] = (final_df['atq'] - final_df['seqq'].fillna(0) + final_df['mktcap'].fillna(0)) / final_df['atq']
        else:
            final_df['tbq'] = final_df['mktcap'] / final_df['atq']
        print("+ Tobin's Q calculated")

    # 7. Capital Expenditures ratio
    if 'capxy' in final_df.columns and 'atq' in final_df.columns:
        final_df['CAPEX'] = final_df['capxy'] / final_df['atq']
        print("+ CAPEX ratio calculated")

    # 8. Cash holdings (need lagged assets for proper calculation)
    asset_col = 'atq' if 'atq' in final_df.columns else ('assets' if 'assets' in final_df.columns else None)
    if 'cheq' in final_df.columns and asset_col:
        final_df = final_df.sort_values(['gvkey', 'datadate'])
        final_df[f'lag_{asset_col}'] = final_df.groupby('gvkey')[asset_col].shift(1)
        final_df['cash'] = final_df['cheq'] / final_df[f'lag_{asset_col}']
        print("+ Cash ratio calculated")

    # Ensure unique index before arithmetic operations
    # Reset index to ensure no duplicate labels that could cause alignment issues
    final_df.reset_index(drop=True, inplace=True)

    # 9. Cash Flow ratio
    if 'oibdpq' in final_df.columns and 'atq' in final_df.columns:
        # Use direct array access to avoid index alignment issues
        # Access columns by position to handle duplicate column names if they exist
        n_rows = len(final_df)
        oibdpq_vals = final_df['oibdpq'].to_numpy()
        xintq_vals = final_df['xintq'].fillna(0).to_numpy() if 'xintq' in final_df.columns else np.zeros(n_rows)
        txtq_vals = final_df['txtq'].fillna(0).to_numpy() if 'txtq' in final_df.columns else np.zeros(n_rows)
        capxy_vals = final_df['capxy'].fillna(0).to_numpy() if 'capxy' in final_df.columns else np.zeros(n_rows)
        atq_vals = final_df['atq'].to_numpy()
        final_df['CF'] = (oibdpq_vals - xintq_vals - txtq_vals - capxy_vals) / atq_vals
        print("+ Cash flow ratio calculated")

    # 10. Book-to-Market ratio
    if 'mktcap' in final_df.columns:
        if 'ceqq' in final_df.columns:
            final_df['bm'] = final_df['ceqq'].fillna(0) / final_df['mktcap'].replace(0, np.nan)
            print("+ Book-to-market calculated from Compustat")
        elif 'book_equity' in final_df.columns:
            final_df['bm'] = final_df['book_equity'].fillna(0) / final_df['mktcap'].replace(0, np.nan)
            print("+ Book-to-market calculated from REIT data")

    # 11. Tax ratio
    if 'txtq' in final_df.columns and 'oibdpq' in final_df.columns:
        final_df['tax'] = final_df['txtq'].fillna(0) / final_df['oibdpq'].fillna(1).replace(0, np.nan)
        print("+ Tax ratio calculated")

    # 12. Market-to-Book ratio
    if 'mktcap' in final_df.columns:
        if 'seqq' in final_df.columns:
            final_df['mtb'] = final_df['mktcap'] / final_df['seqq'].fillna(1).replace(0, np.nan)
            print("+ Market-to-book calculated")

    print("\n+ Financial ratio calculations completed")

    # Additional Variables for Analysis
    # Create year_quarter string variable (year and quarter already extracted above)
    final_df['year_quarter'] = final_df['year'].astype(str) + 'Q' + final_df['quarter'].astype(str)

    # Create numeric year-quarter variable for fixed effects (YYYY * 10 + Q)
    # Examples: 2019Q1 -> 20191, 2020Q4 -> 20204
    final_df['year_quarter_numeric'] = final_df['year'] * 10 + final_df['quarter']

    # Count the number of observations per gvkey
    obs_per_gvkey = final_df['gvkey'].value_counts()
    print("\nObservations per gvkey summary:")
    print(obs_per_gvkey.describe())

    # Check the range of dates
    print(f"\nData spans from {final_df['datadate'].min().date()} to {final_df['datadate'].max().date()}")

    # Check unique years per gvkey
    years_per_gvkey = final_df.groupby('gvkey')['year'].nunique()
    print("\nYears per gvkey summary:")
    print(years_per_gvkey.describe())

    # ========================================================================
    # REORDER VARIABLES
    # ========================================================================
    print("\nReordering variables...")
    print(f"Current dataset has {len(final_df.columns)} columns")
    print(f"Sample of current columns: {list(final_df.columns)[:20]}")

    # Define the order of important variables (Compustat + CRSP focus)
    key_vars_order = [
        # Identifiers
        'gvkey', 'cusip', 'permno', 'permco', 'conm',

        # Dates and Time Variables
        'datadate', 'year', 'quarter', 'year_quarter', 'year_quarter_numeric',

        # Classification Variables
        'sic',

        # CRSP Market Data (quarterly aggregated)
        'prc', 'ret_quarterly', 'retx_quarterly', 'vol', 'shrout', 'mktcap_crsp',

        # Core Compustat Variables
        'atq', 'ltq', 'cheq', 'dlcq', 'dlttq', 'seqq', 'ceqq', 'cshoq',
        'dpq', 'niq', 'oibdpq', 'xintq', 'txtq', 'xrdq', 'prccq', 'capxy', 'dvpspq',
        'ffoq', 'affoq', 'ffopsq',

        # Calculated Financial Ratios
        'td', 'mktcap', 'ev', 'debt_equity_ratio', 'debt_assets_ratio', 'lev',
        'roa', 'roe', 'eps', 'dividend_per_share', 'dividend_payout_ratio', 'pe_ratio',
        'ln_at', 'roa_oibdp', 'RDI', 'RDI_no_fill', 'tbq', 'CAPEX',
        'cash', 'CF', 'bm', 'tax', 'mtb',
        'ffo_atq', 'affo_atq', 'oibdp_atq', 'invested_capital_q',

        # Lagged variables (if created)
        'lag_atq',
    ]

    # Filter key_vars_order to only include columns that actually exist in the dataset
    existing_key_vars = [col for col in key_vars_order if col in final_df.columns]

    # Get all remaining columns that aren't in the existing key vars
    remaining_cols = [col for col in final_df.columns if col not in existing_key_vars]

    # Final column order (only existing columns)
    final_col_order = existing_key_vars + remaining_cols

    print(f"Reordering columns: {len(existing_key_vars)} priority columns + {len(remaining_cols)} remaining columns")

    # Reorder the columns
    final_df = final_df[final_col_order]

    # ========================================================================
    # WINSORIZE DATA
    # ========================================================================
    print("\nWinsorizing data at 1st and 99th percentiles...")

    # Get numeric columns only (exclude identifiers and categorical variables)
    numeric_cols = final_df.select_dtypes(include=[np.number]).columns

    # Define columns to exclude from winsorization (identifiers, dummies, counts)
    exclude_cols = ['gvkey', 'year', 'quarter', 'year_quarter_numeric', 'ptype', 'psub'] + \
                   [col for col in numeric_cols if col.startswith(('psub_', 'Property_'))]

    # Filter to columns that should be winsorized
    winsorize_cols = [col for col in numeric_cols if col not in exclude_cols]

    print(f"Winsorizing {len(winsorize_cols)} numeric variables...")

    # Winsorize at 1st and 99th percentiles
    for col in winsorize_cols:
        if final_df[col].notna().sum() > 0:  # Only if column has non-null values
            # Check if column is integer type - convert to float for winsorization
            is_integer = pd.api.types.is_integer_dtype(final_df[col])
            if is_integer:
                final_df[col] = final_df[col].astype('float64')
            
            lower_bound = final_df[col].quantile(0.01)
            upper_bound = final_df[col].quantile(0.99)
            final_df[col] = final_df[col].clip(lower=lower_bound, upper=upper_bound)

    print("+ Data winsorized at 1st and 99th percentiles")

    # ========================================================================
    # HANDLE INFINITE VALUES FOR STATA COMPATIBILITY
    # ========================================================================
    print("\nHandling infinite values for Stata compatibility...")

    # Replace infinite values with NaN for all numeric columns
    numeric_cols = final_df.select_dtypes(include=[np.number]).columns
    final_df[numeric_cols] = final_df[numeric_cols].replace([np.inf, -np.inf], np.nan)

    # Check for any remaining infinite values
    infinite_counts = final_df[numeric_cols].isin([np.inf, -np.inf]).sum()
    if infinite_counts.sum() > 0:
        print("Warning: Still found infinite values in columns:")
        print(infinite_counts[infinite_counts > 0])
    else:
        print("+ All infinite values successfully replaced with NaN")

    # ========================================================================
    # SAVE FINAL DATASETS
    # ========================================================================
    # Save the DataFrame as a CSV file
    final_df.to_csv(str(config.FINAL_DATA_CSV), index=False)
    print(f"Quarterly data saved to '{config.FINAL_DATA_CSV}' as a CSV file.")

    # Prepare data for Stata export (handle problematic columns)
    final_df_for_stata = final_df.copy()

    # Convert Property_Type to string, replacing NaN with empty string for Stata compatibility
    if 'Property_Type' in final_df_for_stata.columns:
        final_df_for_stata['Property_Type'] = final_df_for_stata['Property_Type'].fillna('').astype(str)

    # Handle problematic columns for Stata export
    problem_columns = ['cusip', 'conm', 'year_quarter', 'sic']
    for col in problem_columns:
        if col in final_df_for_stata.columns:
            # Convert to string and handle missing values
            final_df_for_stata[col] = final_df_for_stata[col].astype(str).replace('nan', '')
            final_df_for_stata[col] = final_df_for_stata[col].fillna('').replace('<NA>', '')
            
            # If column is all missing/empty, drop it to avoid Stata export errors
            if final_df_for_stata[col].replace('', pd.NA).isna().all():
                print(f"Dropping column '{col}' for Stata export (all missing values)")
                final_df_for_stata = final_df_for_stata.drop(columns=[col])

    # Save the DataFrame as a .dta (Stata) file
    final_df_for_stata.to_stata(str(config.FINAL_DATA_DTA), write_index=False)
    print(f"Quarterly data saved to '{config.FINAL_DATA_DTA}' as a .dta file.")

    # Save the DataFrame as a pickle file
    final_df.to_pickle(str(config.FINAL_DATA_PKL))
    print(f"Quarterly data saved to '{config.FINAL_DATA_PKL}' as a pickle file.")

    # Print final dataset summary
    print(f"\n" + "="*60)
    print("FINAL QUARTERLY DATASET SUMMARY")
    print("="*60)
    print(f"DATA: {len(final_df):,} observations | {final_df['gvkey'].nunique():,} firms | {final_df['datadate'].min().date()} to {final_df['datadate'].max().date()}")
    print(f"QUARTERS: {final_df['year_quarter'].nunique():,} quarters | {len(final_df)/final_df['gvkey'].nunique():.1f} avg obs/firm | {len(final_df.columns)} variables")

    # Property coverage summary
    if 'ptype' in final_df.columns:
        ptype_coverage = final_df['ptype'].notna().mean() * 100
        ptype_unique = final_df['ptype'].nunique()
        print(f"PROPERTY TYPES: {ptype_coverage:.1f}% coverage, {ptype_unique} unique types")
        
        # Show property type distribution
        if ptype_coverage > 0:
            print("   Property type distribution:")
            ptype_dist = final_df['ptype'].value_counts().head(5)
            for ptype, count in ptype_dist.items():
                print(f"     - Type {ptype}: {count:,} observations")

    if 'psub' in final_df.columns:
        psub_coverage = final_df['psub'].notna().mean() * 100
        psub_dummies = [col for col in final_df.columns if col.startswith('psub_') and col[5:].isdigit()]
        print(f"PROPERTY SUBTYPES: {psub_coverage:.1f}% coverage, {len(psub_dummies)} dummy variables")

    # Data source summary
    compustat_vars_check = ['atq', 'niq', 'prccq', 'cshoq', 'seqq', 'dlttq', 'dlcq']
    compustat_available = [var for var in compustat_vars_check if var in final_df.columns]
    compustat_coverage = len([var for var in compustat_available if final_df[var].notna().sum() > 0])

    reit_vars = ['ffo', 'assets', 'beta_60m', 'dolvol', 'ret_exc_lead1m', 'prc', 'sales']
    reit_available = [var for var in reit_vars if var in final_df.columns]
    reit_coverage = len([var for var in reit_available if final_df[var].notna().sum() > 0])

    print(f"REIT VARIABLES: {reit_coverage}/{len(reit_vars)} key variables available")
    print(f"COMPUSTAT VARIABLES: {compustat_coverage}/{len(compustat_vars_check)} key variables available")

    # Calculated variables summary
    calculated_vars = ['td', 'mktcap', 'lev', 'roa', 'roe', 'ln_at', 'tbq']
    calculated_available = [var for var in calculated_vars if var in final_df.columns]
    print(f"CALCULATED VARIABLES: {len(calculated_available)}/{len(calculated_vars)} ratios created")

    # Data quality check
    if len(compustat_available) > 0:
        merge_success = (final_df[compustat_available].notna().any(axis=1).sum() / len(final_df)) * 100
        print(f"MERGE SUCCESS: {merge_success:.1f}% of observations have some Compustat data")

    print("="*60)
    
    return final_df


if __name__ == "__main__":
    # Test the module
    pull_compustat_data_module = importlib.import_module('2---pull_compustat_data')
    pull_crsp_data_module = importlib.import_module('3---pull_crsp_data')
    
    compustat_df, _ = pull_compustat_data_module.pull_compustat_data(cfg)
    crsp_quarterly_df = pull_crsp_data_module.pull_crsp_data(cfg, compustat_df)
    final_df = merge_and_process_data(cfg, compustat_df, crsp_quarterly_df)
    print(f"\nFinal dataset shape: {final_df.shape}")

