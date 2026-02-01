"""
CRSP Data Puller Module
========================

This module handles pulling CRSP monthly data from WRDS and aggregating
it to quarterly frequency, including caching logic.

Usage:
    import config_wrds_data as cfg
    from pull_crsp_data import pull_crsp_data
    from pull_compustat_data import pull_compustat_data
    
    compustat_df, _ = pull_compustat_data(cfg)
    crsp_quarterly_df = pull_crsp_data(cfg, compustat_df)
"""

import wrds
import pandas as pd
import os
import importlib

# Import config module (handles numbered filename)
cfg = importlib.import_module('1---config_wrds_data')


def pull_crsp_data(config=None, compustat_df=None):
    """
    Pull CRSP monthly data from WRDS and aggregate to quarterly frequency.
    
    Parameters:
    -----------
    config : module, optional
        Configuration module (defaults to config_wrds_data if None)
    compustat_df : DataFrame, optional
        Compustat DataFrame to extract CUSIPs from. If None, will try to load
        from cache or skip CRSP pull if not available.
        
    Returns:
    --------
    DataFrame
        Quarterly aggregated CRSP data
    """
    if config is None:
        config = cfg
    
    # Check if we should refresh CRSP data or use cached version
    if config.REFRESH_DATA or not config.CRSP_RAW_FILE.exists():
        print("Downloading fresh CRSP data from WRDS...")
        
        # Get CUSIPs from Compustat data if provided
        if compustat_df is None:
            # Try to load from cache
            if config.COMPUSTAT_RAW_FILE.exists():
                compustat_df = pd.read_pickle(str(config.COMPUSTAT_RAW_FILE))
                print("Loaded Compustat data from cache to extract CUSIPs")
            else:
                print("ERROR: Cannot pull CRSP data without Compustat data or cached Compustat file")
                return None
        
        # Connect to WRDS
        conn = wrds.Connection(wrds_username=config.WRDS_USERNAME)
        
        # Get CUSIPs for real estate companies from Compustat data
        realestate_cusips = compustat_df['cusip'].dropna().str[:8].unique().tolist()
        cusip_list = "','".join(realestate_cusips)
        print(f"Filtering CRSP data for {len(realestate_cusips)} real estate company CUSIPs...")

        # Get CRSP data using configurable variables list
        # Filter to only real estate companies by using CUSIP list from Compustat
        print(f"Step 1: Getting CRSP data for real estate companies...")

        # Add derived time variables to the query
        crsp_query_vars = config.crsp_vars.copy()

        # Construct SQL query with configurable variables
        query = f"""
            SELECT
                {', '.join(crsp_query_vars)},
                EXTRACT(YEAR FROM date) as year,
                EXTRACT(QUARTER FROM date) as quarter,
                EXTRACT(YEAR FROM date) || 'Q' || EXTRACT(QUARTER FROM date) as year_quarter
            FROM crsp.msf
            WHERE date BETWEEN '{config.start_date}' AND '{config.end_date}'
            AND SUBSTR(cusip, 1, 8) IN ('{cusip_list}')
            ORDER BY permno, date
        """

        # Execute query and fetch CRSP data
        crsp_identifiers = conn.raw_sql(query)
        print(f"Downloaded {len(crsp_identifiers)} CRSP observations for real estate companies")

        # Close the WRDS connection
        conn.close()

        # Save filtered CRSP data to WRDS folder (pickle, CSV, and Stata formats)
        print(f"Saving filtered CRSP data (real estate companies) to {config.CRSP_RAW_FILE}")
        crsp_identifiers.to_pickle(str(config.CRSP_RAW_FILE))

        print(f"Saving filtered CRSP data (real estate companies) to {config.CRSP_RAW_CSV}")
        crsp_identifiers.to_csv(str(config.CRSP_RAW_CSV), index=False)

        print(f"Saving filtered CRSP data (real estate companies) to {config.CRSP_RAW_DTA}")
        # Prepare data for Stata export (handle problematic columns)
        crsp_identifiers_for_stata = crsp_identifiers.copy()
        
        # Check for duplicate columns first
        if crsp_identifiers_for_stata.columns.duplicated().any():
            print("Warning: Found duplicate columns, removing duplicates for Stata export...")
            crsp_identifiers_for_stata = crsp_identifiers_for_stata.loc[:, ~crsp_identifiers_for_stata.columns.duplicated()]
        
        # Convert string columns with potential issues
        string_cols = ['cusip']
        for col in string_cols:
            if col in crsp_identifiers_for_stata.columns:
                # Ensure it's a Series (not DataFrame) and handle missing values
                series = crsp_identifiers_for_stata[col]
                if isinstance(series, pd.Series):
                    crsp_identifiers_for_stata[col] = series.astype(str).replace('nan', '').replace('<NA>', '').fillna('')
        
        # Ensure all columns are proper types for Stata
        # Convert any object columns to string if they contain strings
        for col in crsp_identifiers_for_stata.columns:
            if col in crsp_identifiers_for_stata.columns:  # Double check column exists
                series = crsp_identifiers_for_stata[col]
                if isinstance(series, pd.Series) and series.dtype == 'object':
                    # Check if it's actually string data
                    try:
                        if series.apply(lambda x: isinstance(x, str) if pd.notna(x) else True).all():
                            crsp_identifiers_for_stata[col] = series.astype(str).replace('nan', '').replace('<NA>', '').fillna('')
                    except Exception:
                        pass  # Skip if can't convert
        
        try:
            crsp_identifiers_for_stata.to_stata(str(config.CRSP_RAW_DTA), write_index=False, version=118)
            print(f"Successfully saved Stata file: {config.CRSP_RAW_DTA}")
        except Exception as e:
            print(f"Warning: Could not save as Stata format: {e}")
            print("Continuing without Stata export...")
        
    else:
        print("Loading cached CRSP data from WRDS folder...")
        crsp_identifiers = pd.read_pickle(str(config.CRSP_RAW_FILE))
    
    # Aggregate monthly CRSP data to quarterly frequency
    print("\nAggregating CRSP data from monthly to quarterly frequency...")
    
    # Convert CRSP date to datetime and ensure proper formatting
    crsp_identifiers['date'] = pd.to_datetime(crsp_identifiers['date'])
    
    # Define aggregation strategy for CRSP variables
    crsp_agg_rules = {
        # Identifiers: take first non-null value
        'cusip': 'first',
        'permco': 'first',

        # Price data: use end-of-quarter values (last)
        'prc': 'last',  # Price at quarter-end

        # Volume: average daily volume over the quarter
        'vol': 'mean',

        # Shares outstanding: use end-of-quarter value
        'shrout': 'last',

        # Time variables (derived, not groupby vars)
        'year_quarter': 'first',
        'date': 'last'  # Last trading date of quarter
    }

    # Handle returns separately for proper compounding
    # For quarterly returns: (1+ret1)*(1+ret2)*(1+ret3) - 1
    print("Computing quarterly compounded returns...")

    # Create quarterly returns by compounding monthly returns
    crsp_identifiers['ret_plus1'] = crsp_identifiers['ret'].fillna(0) + 1
    crsp_identifiers['retx_plus1'] = crsp_identifiers['retx'].fillna(0) + 1

    # Group by permno, year, quarter for aggregation
    crsp_quarterly = crsp_identifiers.groupby(['permno', 'year', 'quarter']).agg({
        **crsp_agg_rules,
        'ret_plus1': lambda x: x.prod(),      # Compound returns (product of 1+ret)
        'retx_plus1': lambda x: x.prod()      # Compound returns ex-dividends
    }).reset_index()

    # Convert compounded returns back to return format (subtract 1)
    crsp_quarterly['ret_plus1'] = crsp_quarterly['ret_plus1'] - 1
    crsp_quarterly['retx_plus1'] = crsp_quarterly['retx_plus1'] - 1

    # Rename compounded returns back to original names
    crsp_quarterly = crsp_quarterly.rename(columns={
        'ret_plus1': 'ret_quarterly',
        'retx_plus1': 'retx_quarterly'
    })

    # Calculate market capitalization (price * shares outstanding)
    # Convert shrout from thousands to actual shares and handle missing prices
    crsp_quarterly['mktcap_crsp'] = (crsp_quarterly['prc'].abs() *
                                    crsp_quarterly['shrout'] * 1000).fillna(0)

    print(f"Aggregated to quarterly: {len(crsp_quarterly):,} quarterly observations")
    print(f"CRSP quarterly coverage: {crsp_quarterly['permno'].nunique()} unique firms")
    print(f"CRSP variables: {list(crsp_quarterly.columns)}")
    
    return crsp_quarterly


if __name__ == "__main__":
    # Test the module
    pull_compustat_data_module = importlib.import_module('2---pull_compustat_data')
    compustat_df, _ = pull_compustat_data_module.pull_compustat_data()
    crsp_quarterly = pull_crsp_data(cfg, compustat_df)
    if crsp_quarterly is not None:
        print(f"\nCRSP quarterly data shape: {crsp_quarterly.shape}")

