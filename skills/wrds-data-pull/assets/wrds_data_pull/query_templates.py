"""
Compustat Data Puller Module
==============================

This module handles pulling Compustat annual and quarterly data from WRDS,
including caching logic and company info retrieval.

Usage:
    import config_wrds_data as cfg
    from pull_compustat_data import pull_compustat_data
    
    annual_df, quarterly_df, company_info = pull_compustat_data(cfg)
"""

import wrds
import pandas as pd
import os
import importlib

# Import config module (handles numbered filename)
cfg = importlib.import_module('1---config_wrds_data')


def _filter_available_columns(requested_cols, conn, library, table):
    """
    Keep only columns that exist in the WRDS table; warn on any missing.
    """
    try:
        available_cols = {c.lower() for c in conn.list_table_fields(library, table)}
    except AttributeError:
        # Older wrds versions: fetch zero rows to inspect columns
        available_cols = {c.lower() for c in conn.get_table(library, table, obs=0).columns}
    filtered = [col for col in requested_cols if col.lower() in available_cols]
    missing = [col for col in requested_cols if col.lower() not in available_cols]
    if missing:
        print(f"Warning: dropping {missing} because they are not in {library}.{table}")
    return filtered


def _get_company_info(conn, config):
    """
    Helper function to retrieve company info (gvkey, sic) from WRDS.
    
    Parameters:
    -----------
    conn : wrds.Connection
        WRDS connection object
    config : module
        Configuration module
        
    Returns:
    --------
    DataFrame
        Company information DataFrame with columns (gvkey, sic)
    """
    try:
        company_fields = {c.lower() for c in conn.list_table_fields("comp", "company")}
    except AttributeError:
        company_fields = {c.lower() for c in conn.get_table("comp", "company", obs=0).columns}

    select_cols = ["gvkey", "sic"]
    if "cik" in company_fields:
        select_cols.append("cik")

    if config.USE_PREDEFINED_GVKEYS:
        print(f"Getting company info for predefined list of {len(config.PREDEFINED_GVKEYS)} companies...")
        gvkey_list_for_sic = "','".join(config.PREDEFINED_GVKEYS)
        company_info = conn.raw_sql(f"""
            SELECT {', '.join(select_cols)}
            FROM comp.company
            WHERE gvkey IN ('{gvkey_list_for_sic}')
        """)
        print(f"Found {len(company_info)} companies in database")
        if len(company_info) < len(config.PREDEFINED_GVKEYS):
            found_gvkeys = set(company_info['gvkey'].tolist())
            missing_gvkeys = [gvkey for gvkey in config.PREDEFINED_GVKEYS if gvkey not in found_gvkeys]
            print(f"WARNING: {len(missing_gvkeys)} GVKEYs not found in database: {missing_gvkeys}")
    else:
        print(f"Getting company info for SIC codes {config.SIC_FILTER}...")
        sic_list_str = ','.join([f"'{sic}'" for sic in config.SIC_FILTER])
        company_info = conn.raw_sql(f"""
            SELECT {', '.join(select_cols)}
            FROM comp.company
            WHERE sic IN ({sic_list_str})
        """)
        print(f"Found {len(company_info)} companies with real estate and related SIC codes")

    if "cik" in company_info.columns:
        def _normalize_cik(v):
            if pd.isna(v):
                return pd.NA
            s = str(v).strip()
            if (not s) or (s.lower() in {"nan", "none", "<na>"}):
                return pd.NA
            if "." in s:
                s = s.split(".")[0]
            digits = "".join(ch for ch in s if ch.isdigit())
            if not digits:
                return pd.NA
            return digits.zfill(10)

        company_info["cik"] = company_info["cik"].apply(_normalize_cik)
     
    return company_info


def _prepare_stata_export(df):
    """
    Helper function to prepare DataFrame for Stata export.
    
    Parameters:
    -----------
    df : DataFrame
        DataFrame to prepare for Stata export
        
    Returns:
    --------
    DataFrame
        DataFrame prepared for Stata export
    """
    df_for_stata = df.copy()
    
    # Check for duplicate columns first
    if df_for_stata.columns.duplicated().any():
        print("Warning: Found duplicate columns, removing duplicates for Stata export...")
        df_for_stata = df_for_stata.loc[:, ~df_for_stata.columns.duplicated()]
    
    # Convert string columns with potential issues
    string_cols = ['gvkey', 'cusip', 'conm', 'cik']
    for col in string_cols:
        if col in df_for_stata.columns:
            series = df_for_stata[col]
            if isinstance(series, pd.Series):
                df_for_stata[col] = series.astype(str).replace('nan', '').replace('<NA>', '').fillna('')
    
    # Ensure all object columns are proper types for Stata
    for col in df_for_stata.columns:
        series = df_for_stata[col]
        if isinstance(series, pd.Series) and series.dtype == 'object':
            try:
                if series.apply(lambda x: isinstance(x, str) if pd.notna(x) else True).all():
                    df_for_stata[col] = series.astype(str).replace('nan', '').replace('<NA>', '').fillna('')
            except Exception:
                pass
    
    return df_for_stata


def _save_data_files(df, pkl_path, csv_path, dta_path, description):
    """
    Helper function to save DataFrame to pickle, CSV, and Stata formats.
    
    Parameters:
    -----------
    df : DataFrame
        DataFrame to save
    pkl_path : str
        Path for pickle file
    csv_path : str
        Path for CSV file
    dta_path : str
        Path for Stata file
    description : str
        Description of data for logging
    """
    print(f"Saving {description} to {pkl_path}")
    df.to_pickle(pkl_path)
    
    print(f"Saving {description} to {csv_path}")
    df.to_csv(csv_path, index=False)
    
    print(f"Saving {description} to {dta_path}")
    df_for_stata = _prepare_stata_export(df)
    try:
        df_for_stata.to_stata(dta_path, write_index=False, version=118)
        print(f"Successfully saved Stata file: {dta_path}")
    except Exception as e:
        print(f"Warning: Could not save as Stata format: {e}")
        print("Continuing without Stata export...")


def pull_compustat_annual(config=None):
    """
    Pull Compustat annual data from WRDS with caching support.
    
    Parameters:
    -----------
    config : module, optional
        Configuration module (defaults to config_wrds_data if None)
        
    Returns:
    --------
    DataFrame
        Compustat annual data with SIC codes merged
    """
    if config is None:
        config = cfg
    
    # Check if we should refresh data or use cached version
    if config.REFRESH_DATA or not config.COMPUSTAT_ANNUAL_RAW_FILE.exists():
        print("Downloading fresh Compustat annual data from WRDS...")
        
        # Connect to WRDS
        conn = wrds.Connection(wrds_username=config.WRDS_USERNAME)
        
        # Get company info
        company_info = _get_company_info(conn, config)
        
        # Get list of gvkeys for filtering
        filtered_gvkeys = company_info['gvkey'].tolist()
        gvkey_list = "','".join(filtered_gvkeys)
        
        # Construct SQL query for annual data (comp.funda)
        filter_description = f"predefined list ({len(filtered_gvkeys)} companies)" if config.USE_PREDEFINED_GVKEYS else f"real estate SIC codes ({len(filtered_gvkeys)} companies)"
        print(f"Getting annual Compustat data for {filter_description}...")
        
        # Get annual-compatible variables (exclude quarterly-only variables like 'prcc')
        annual_vars = config.get_annual_compatible_vars(config.compustat_vars)
        annual_vars = _filter_available_columns(annual_vars, conn, 'comp', 'funda')
        
        query = f"""
            SELECT {', '.join(annual_vars)}
            FROM comp.funda
            WHERE datadate BETWEEN '{config.start_date}' AND '{config.end_date}'
            AND indfmt = 'INDL'   -- Industrial format
            AND datafmt = 'STD'   -- Standardized format
            AND popsrc = 'D'      -- Domestic companies
            AND consol = 'C'      -- Consolidated statements
            AND gvkey IN ('{gvkey_list}')  -- Filter to selected companies only
        """
        
        # Execute query
        compustat_df = conn.raw_sql(query)
        print(f"Downloaded {len(compustat_df)} annual observations")
        
        # Merge company info (SIC codes) with Compustat data
        print("Merging SIC codes with Compustat annual data...")
        compustat_df = pd.merge(compustat_df, company_info, on='gvkey', how='left')
        
        # Close the WRDS connection
        conn.close()
        
        # Save raw data files
        _save_data_files(
            compustat_df,
            str(config.COMPUSTAT_ANNUAL_RAW_FILE),
            str(config.COMPUSTAT_ANNUAL_RAW_CSV),
            str(config.COMPUSTAT_ANNUAL_RAW_DTA),
            f"Compustat annual data ({filter_description})"
        )
        
    else:
        print("Loading cached Compustat annual data...")
        compustat_df = pd.read_pickle(str(config.COMPUSTAT_ANNUAL_RAW_FILE))
    
    # Process the data
    compustat_df['datadate'] = pd.to_datetime(compustat_df['datadate'])
    compustat_df.sort_values(['gvkey', 'datadate'], inplace=True)
    
    filter_desc = f"predefined list" if config.USE_PREDEFINED_GVKEYS else f"real estate SIC codes"
    print(f"Compustat annual data shape ({filter_desc}): {compustat_df.shape}")
    
    return compustat_df


def pull_compustat_quarterly(config=None):
    """
    Pull Compustat quarterly data from WRDS with caching support.
    
    Parameters:
    -----------
    config : module, optional
        Configuration module (defaults to config_wrds_data if None)
        
    Returns:
    --------
    DataFrame
        Compustat quarterly data with SIC codes merged
    """
    if config is None:
        config = cfg
    
    # Check if we should refresh data or use cached version
    if config.REFRESH_DATA or not config.COMPUSTAT_QUARTERLY_RAW_FILE.exists():
        print("Downloading fresh Compustat quarterly data from WRDS...")
        
        # Connect to WRDS
        conn = wrds.Connection(wrds_username=config.WRDS_USERNAME)
        
        # Get company info
        company_info = _get_company_info(conn, config)
        
        # Get list of gvkeys for filtering
        filtered_gvkeys = company_info['gvkey'].tolist()
        gvkey_list = "','".join(filtered_gvkeys)
        
        # Construct SQL query for quarterly data (comp.fundq)
        # Use add_quarterly_suffix() to add 'q' to variable names
        quarterly_vars = config.add_quarterly_suffix(config.compustat_vars)
        quarterly_vars = _filter_available_columns(quarterly_vars, conn, 'comp', 'fundq')
        
        filter_description = f"predefined list ({len(filtered_gvkeys)} companies)" if config.USE_PREDEFINED_GVKEYS else f"real estate SIC codes ({len(filtered_gvkeys)} companies)"
        print(f"Getting quarterly Compustat data for {filter_description}...")
        
        query = f"""
            SELECT {', '.join(quarterly_vars)}
            FROM comp.fundq
            WHERE datadate BETWEEN '{config.start_date}' AND '{config.end_date}'
            AND indfmt = 'INDL'   -- Industrial format
            AND datafmt = 'STD'   -- Standardized format
            AND popsrc = 'D'      -- Domestic companies
            AND consol = 'C'      -- Consolidated statements
            AND gvkey IN ('{gvkey_list}')  -- Filter to selected companies only
        """
        
        # Execute query
        compustat_df = conn.raw_sql(query)
        print(f"Downloaded {len(compustat_df)} quarterly observations")
        
        # Merge company info (SIC codes) with Compustat data
        print("Merging SIC codes with Compustat quarterly data...")
        compustat_df = pd.merge(compustat_df, company_info, on='gvkey', how='left')
        
        # Close the WRDS connection
        conn.close()
        
        # Save raw data files
        _save_data_files(
            compustat_df,
            str(config.COMPUSTAT_QUARTERLY_RAW_FILE),
            str(config.COMPUSTAT_QUARTERLY_RAW_CSV),
            str(config.COMPUSTAT_QUARTERLY_RAW_DTA),
            f"Compustat quarterly data ({filter_description})"
        )
        
    else:
        print("Loading cached Compustat quarterly data...")
        compustat_df = pd.read_pickle(str(config.COMPUSTAT_QUARTERLY_RAW_FILE))
    
    # Process the data
    compustat_df['datadate'] = pd.to_datetime(compustat_df['datadate'])
    compustat_df.sort_values(['gvkey', 'datadate'], inplace=True)
    
    filter_desc = f"predefined list" if config.USE_PREDEFINED_GVKEYS else f"real estate SIC codes"
    print(f"Compustat quarterly data shape ({filter_desc}): {compustat_df.shape}")
    
    return compustat_df


def pull_compustat_data(config=None):
    """
    Pull both Compustat annual and quarterly data from WRDS with caching support.
    
    Parameters:
    -----------
    config : module, optional
        Configuration module (defaults to config_wrds_data if None)
        
    Returns:
    --------
    tuple : (annual_df, quarterly_df, company_info)
        annual_df : DataFrame
            Compustat annual data with SIC codes merged
        quarterly_df : DataFrame
            Compustat quarterly data with SIC codes merged
        company_info : DataFrame
            Company information (gvkey, sic) DataFrame
    """
    if config is None:
        config = cfg
    
    # Pull annual data
    print("\n" + "="*60)
    print("PULLING COMPUSTAT ANNUAL DATA")
    print("="*60)
    annual_df = pull_compustat_annual(config)
    
    # Pull quarterly data
    print("\n" + "="*60)
    print("PULLING COMPUSTAT QUARTERLY DATA")
    print("="*60)
    quarterly_df = pull_compustat_quarterly(config)
    
    # Get company info
    # If we pulled fresh data, company_info was retrieved during pulls
    # Otherwise, load from cache
    if config.REFRESH_DATA or not config.COMPANY_INFO_RAW_FILE.exists():
        # Company info was already retrieved during pulls, get it from annual_df
        base_cols = ['gvkey', 'sic']
        if 'cik' in annual_df.columns:
            base_cols.append('cik')
        company_info = annual_df[base_cols].drop_duplicates().reset_index(drop=True)
        
        # Save company info
        print(f"Saving company info to {config.COMPANY_INFO_RAW_FILE}")
        company_info.to_pickle(str(config.COMPANY_INFO_RAW_FILE))
        print(f"Saving company info to {config.COMPANY_INFO_RAW_CSV}")
        company_info.to_csv(str(config.COMPANY_INFO_RAW_CSV), index=False)
    else:
        print("Loading cached company info...")
        company_info = pd.read_pickle(str(config.COMPANY_INFO_RAW_FILE))
    
    return annual_df, quarterly_df, company_info


if __name__ == "__main__":
    # Test the module
    annual_df, quarterly_df, company_info = pull_compustat_data()
    print(f"\nCompustat annual data shape: {annual_df.shape}")
    print(f"Compustat quarterly data shape: {quarterly_df.shape}")
    print(f"Company info shape: {company_info.shape}")
