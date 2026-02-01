"""
WRDS Data Configuration Module
===============================

This module contains all configuration settings, paths, and variable lists
for pulling and processing Compustat and CRSP data from WRDS.

Usage:
    import config_wrds_data as cfg
    print(cfg.REFRESH_DATA)
    print(cfg.COMPUSTAT_RAW_FILE)
"""

# ==============================================================================
# PROJECT PATH CONFIGURATION - Automatically locates and imports centralized paths
# ==============================================================================
import os
from pathlib import Path
import sys
from dotenv import load_dotenv

# Search up to 5 parent directories to find and import config_paths.py
for p in Path(__file__).resolve().parents[:5]:
    if (p / 'config_paths.py').exists():
        sys.path.insert(0, str(p))
        break

# Import path configuration module
import config_paths

# Import directory paths for direct use
from config_paths import (
    DATA_DIR,            # Main data directory
    RAW_DATA_DIR,        # Raw data files (untouched from external sources)
    PROCESSED_DATA_DIR,  # Processed and merged data files
    FINAL_DATASETS_DIR,  # Final datasets ready for analysis
    RESULTS_DIR,         # Main output directory for all results
    FIGURES_DIR,         # Plots, charts, and visualizations
    TABLES_DIR           # Regression tables and summary statistics
)

# =============================================================================
# CONFIGURATION SETTINGS
# =============================================================================

# Data refresh settings
REFRESH_DATA = True  # (True/False) Set to False to use cached REIT-filtered data, True to download fresh data

# GVKEY filtering method
USE_PREDEFINED_GVKEYS = True  # (True/False) True = use GVKEY list from merged data, False = download all firms with SIC filter

# SIC code filter (used when USE_PREDEFINED_GVKEYS = False)
# Real estate and related companies SIC codes
SIC_FILTER = [
    # # REITs
    # 6798,
    # # Property Operations
    # 6512, 6513, 6514, 6515, 6519,
    # # Real Estate Services
    # 6531, 6552, 6553, 6541,
    # # Related Financial Services
    # 6162, 6361, 6733,
    # # Other Related
    # 7389, 9531
]

# Define date range (adjust as needed)
start_date = '1970-01-01'
# start_date = '2010-01-01'
# start_date = '2022-01-01'
end_date = '2024-12-31'

# =============================================================================
# GVKEY LIST LOADING FUNCTION
# =============================================================================

def load_gvkey_list(file_path: str = None) -> list[str]:
    """
    Load GVKEY list from CSV file (with header) or text file (backward compatibility).
    
    Args:
        file_path: Path to GVKEY list file. If None, tries CSV first, then text file.
    
    Returns:
        List of GVKEY strings (sorted and deduplicated)
    """
    if file_path is None:
        # Use global path configuration for processed data directory
        # Try CSV first, then fall back to text file for backward compatibility
        csv_path = PROCESSED_DATA_DIR / "merged_chars_crsp_gvkeys.csv"
        txt_path = PROCESSED_DATA_DIR / "merged_chars_crsp_gvkeys.txt"
        
        if csv_path.exists():
            file_path = str(csv_path)
        elif txt_path.exists():
            file_path = str(txt_path)
        else:
            print("WARNING: GVKEY list file not found (tried both CSV and TXT)")
            print(f"  CSV: {csv_path}")
            print(f"  TXT: {txt_path}")
            print("Falling back to empty list. Set USE_PREDEFINED_GVKEYS = False to use SIC filter instead.")
            return []
    
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        print(f"WARNING: GVKEY list file not found: {file_path}")
        print("Falling back to empty list. Set USE_PREDEFINED_GVKEYS = False to use SIC filter instead.")
        return []
    
    try:
        # Try to read as CSV first (if it has a header)
        if file_path_obj.suffix == '.csv':
            import pandas as pd
            df = pd.read_csv(file_path_obj, dtype=str)
            # Check if 'gvkey' column exists
            if 'gvkey' in df.columns:
                gvkeys = df['gvkey'].dropna().astype(str).str.strip().tolist()
            else:
                # If no header, read first column
                gvkeys = df.iloc[:, 0].dropna().astype(str).str.strip().tolist()
        else:
            # Read as text file (backward compatibility)
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                # Skip header if it looks like a header (e.g., "gvkey")
                if lines and lines[0].lower() in ['gvkey', 'gvkeys']:
                    lines = lines[1:]
                gvkeys = lines
        
        # Remove duplicates and sort
        gvkeys = sorted(list(set(gvkeys)))
        
        print(f"Loaded {len(gvkeys)} unique GVKEYs from: {file_path_obj}")
        return gvkeys
    
    except Exception as e:
        print(f"ERROR: Failed to load GVKEY list from {file_path_obj}: {e}")
        print("Falling back to empty list. Set USE_PREDEFINED_GVKEYS = False to use SIC filter instead.")
        return []


# Predefined GVKEY list (used when USE_PREDEFINED_GVKEYS = True)
# Automatically loads from merged_chars_crsp_gvkeys.csv (or .txt for backward compatibility) if available
# Falls back to empty list if file not found (user should set USE_PREDEFINED_GVKEYS = False)
PREDEFINED_GVKEYS = load_gvkey_list() if USE_PREDEFINED_GVKEYS else []

# WRDS username for connection (loaded from environment; set in .env/.local.env)
load_dotenv()
WRDS_USERNAME = os.getenv("WRDS_USERNAME")
if not WRDS_USERNAME:
    raise ValueError(
        "WRDS_USERNAME is not set. Please add it to your .env/.local.env file."
    )

# =============================================================================
# GLOBAL PATH CONFIGURATION - All data paths defined here using centralized paths
# =============================================================================

# Raw data subdirectories (organized by source within RAW_DATA_DIR)
COMPUSTAT_RAW_DIR = RAW_DATA_DIR / 'compustat'
CRSP_RAW_DIR = RAW_DATA_DIR / 'crsp'

# Subdirectories for organized output formats (within PROCESSED_DATA_DIR)
CSV_OUTPUT_DIR = PROCESSED_DATA_DIR / 'csv'
STATA_OUTPUT_DIR = PROCESSED_DATA_DIR / 'stata'

# Create directories if they don't exist
COMPUSTAT_RAW_DIR.mkdir(parents=True, exist_ok=True)
CRSP_RAW_DIR.mkdir(parents=True, exist_ok=True)
CSV_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Raw Compustat data file paths (stored in Data/raw/compustat/)
# Annual data files
COMPUSTAT_ANNUAL_RAW_FILE = COMPUSTAT_RAW_DIR / "compustat_annual_raw.pkl"
COMPUSTAT_ANNUAL_RAW_CSV = COMPUSTAT_RAW_DIR / "compustat_annual_raw.csv"
COMPUSTAT_ANNUAL_RAW_DTA = COMPUSTAT_RAW_DIR / "compustat_annual_raw.dta"

# Quarterly data files
COMPUSTAT_QUARTERLY_RAW_FILE = COMPUSTAT_RAW_DIR / "compustat_quarterly_raw.pkl"
COMPUSTAT_QUARTERLY_RAW_CSV = COMPUSTAT_RAW_DIR / "compustat_quarterly_raw.csv"
COMPUSTAT_QUARTERLY_RAW_DTA = COMPUSTAT_RAW_DIR / "compustat_quarterly_raw.dta"

# Legacy paths (for backward compatibility - point to quarterly)
COMPUSTAT_RAW_FILE = COMPUSTAT_QUARTERLY_RAW_FILE
COMPUSTAT_RAW_CSV = COMPUSTAT_QUARTERLY_RAW_CSV
COMPUSTAT_RAW_DTA = COMPUSTAT_QUARTERLY_RAW_DTA

# Company info files
COMPANY_INFO_RAW_FILE = COMPUSTAT_RAW_DIR / "company_info_raw.pkl"
COMPANY_INFO_RAW_CSV = COMPUSTAT_RAW_DIR / "company_info_raw.csv"

# Raw CRSP data file paths (stored in Data/raw/crsp/)
CRSP_RAW_FILE = CRSP_RAW_DIR / "crsp_identifiers_raw.pkl"
CRSP_RAW_CSV = CRSP_RAW_DIR / "crsp_identifiers_raw.csv"
CRSP_RAW_DTA = CRSP_RAW_DIR / "crsp_identifiers_raw.dta"

# Final cleaned datasets (organized by format)
FINAL_DATA_CSV = CSV_OUTPUT_DIR / "compustat_realestate_cleaned_quarterly.csv"
FINAL_DATA_DTA = STATA_OUTPUT_DIR / "compustat_realestate_cleaned_quarterly.dta"
FINAL_DATA_PKL = PROCESSED_DATA_DIR / "compustat_realestate_cleaned_quarterly.pkl"

# GVKEY list file (from merged Chars-CRSP data)
# Prefer CSV format, but function will fall back to TXT for backward compatibility
GVKEY_LIST_FILE = PROCESSED_DATA_DIR / "merged_chars_crsp_gvkeys.csv"

# =============================================================================
# COMPUSTAT VARIABLE DEFINITIONS
# =============================================================================

# CORE VARIABLES - Actually used in calculations
# NOTE: These are base variable names (without 'q' suffix)
# For quarterly pulls, add 'q' suffix automatically using add_quarterly_suffix()
compustat_vars = [
    # -------------------------------------------------------------------------
    # Identifiers and company info (no suffix needed)
    # -------------------------------------------------------------------------
    'gvkey', 'cusip', 'datadate', 'conm',
    
    # Quarterly date identifiers (quarterly-only, no suffix needed)
    'datacqtr',    # Calendar Data Year and Quarter
    'datafqtr',    # Fiscal Data Year and Quarter
    'fqtr',        # Fiscal Quarter
    'fyearq',      # Fiscal Year
    'rdq',         # Earnings Announcement Date (Report Date Quarterly)

    # -------------------------------------------------------------------------
    # Industry / REIT classification (for sample definition)
    # -------------------------------------------------------------------------
    'sic',         # SIC code
    'sich',        # Historical SIC
    'gsector',     # GICS sector
    'ggroup',      # GICS industry group
    'gsubind',     # GICS sub-industry (Equity REITs live here)
    'naics',       # NAICS code

    # -------------------------------------------------------------------------
    # Core Balance Sheet Items (used in calculations)
    # -------------------------------------------------------------------------
    'at',       # Total Assets - for ratios & filtering
    'lt',       # Total Liabilities - for filtering only
    'che',      # Cash and Short-Term Investments - for cash ratios & EV
    'dlc',      # Debt in Current Liabilities - for total debt
    'dltt',     # Long-Term Debt - for total debt
    'seq',      # Stockholders' Equity - for leverage ratios & Tobin's Q
    'ceq',      # Common Equity - for book-to-market ratio
    'csho',     # Common Shares Outstanding - for EPS & market cap

    # --- Additional capital structure pieces for ROIC & leverage ---
    'dt',       # Total debt including current (for debt / NOI, net debt, etc.)
    'teq',      # Total equity (parent + minority) - for invested capital approx
    'pstk',     # Preferred stock (capital) - for invested capital
    'mib',      # Noncontrolling interest (balance sheet)
    'mibt',     # Noncontrolling interest - total (balance sheet)
    'icapt',    # Invested capital - total (preferred ROIC denominator)

    # --- Real-estate asset base (for NOI yield / cap-rate style metrics) ---
    'ret',      # Total real estate property
    'ip',       # Investment property
    'ppent',    # Net PPE (includes many RE properties, esp. older REIT data)

    # -------------------------------------------------------------------------
    # Core Income Statement Items (used in calculations)
    # -------------------------------------------------------------------------
    'dp',       # Depreciation and Amortization - for FFO
    'ni',       # Net Income (Loss) - for ROA, ROE, EPS, FFO
    'oibdp',    # Operating Income Before Depreciation - for ROA
    'xint',     # Interest Expense - for coverage, cash-flow calculations
    'txt',      # Income Taxes - for ROIC/NOPAT and tax ratios
    'xrd',      # R&D Expense - for RDI calculation
    'ffo',      # Funds From Operations (REIT) - core REIT profitability
    'ib',       # Income Before Extraordinary Items (note: NOT "interest-bearing debt")
    'revt',     # Revenue - for revenue-based ratios
    'sale',     # Sales - for revenue-based ratios
    'cogs',     # Cost of Goods Sold - for gross margin
    'xsga',     # SG&A Expenses - for operating efficiency
    'oiadp',    # Operating Income After Depreciation - for operating/ROIC
    'pi',       # Pretax Income
    'sret',     # Gain or Loss on Sale of Property - for FFO/EBITDAre adjustments
    'wda',      # Writedowns After Tax - add-back in FFO/EBITDAre
    'gdwlia',   # Impairments of Goodwill After-tax - add-back in FFO/EBITDAre

    # --- Minority & preferred income for "pre-minority/preferred" FFO if needed ---
    'mii',      # Noncontrolling interest (income account)
    'dvp',      # Preferred dividends

    # --- Real estate specific income and expenses for NOI ---
    'irent',    # Rental Income
    'iire',     # Investment Income (Real Estate)
    'iore',     # Income – Other (Real Estate) 
    'xore',     # Expense – Other (Real Estate)
    'xdvre',    # Expense – Development (Real Estate)
    'xivre',    # Expense – Investment (Real Estate)
    'xrent',    # Rental Expense (ground leases / occupancy, when applicable)

    # --- EBITDA / EBITDAre components ---
    'ebit',     # Earnings Before Interest and Taxes
    'ebitda',   # EBITDA as defined by Compustat (if populated)

    # -------------------------------------------------------------------------
    # Market Data (used in calculations)
    # -------------------------------------------------------------------------
    'prcc',     # Price Close (base name; expect prccq after suffix) - for market cap & P/FFO
    'mkvalt',   # Market value - total (equity MV) - for FFO yield, EV-like metrics

    # Shares for diluted per-share metrics
    'cshfd',    # Common shares used to calc EPS - fully diluted
    'csho',     # Common shares outstanding (annual) for ME/FFO per share
    'prcc_f',   # Fiscal-year-end price (for Compustat ME alternative)

    # -------------------------------------------------------------------------
    # Cash Flow Items (used in AFFO / coverage / free cash flow proxies)
    # -------------------------------------------------------------------------
    'capx',     # Capital Expenditures - for AFFO and CAPEX ratio
    'oancf',    # Net cash flow from operating activities - CFO-based AFFO proxy

    # -------------------------------------------------------------------------
    # Dividends: level and per-share, for payout ratios
    # -------------------------------------------------------------------------
    'dvpsp',    # Dividends per share - pay date - for payout per share
    'dvpsx',    # Dividends per share - ex-date (often used in REIT work)
    'dvc',      # Total cash dividends on common stock - for payout ratio
]

# Remove duplicates while preserving order
compustat_vars = list(dict.fromkeys(compustat_vars))


def get_annual_compatible_vars(vars_list):
    """
    Filter variable list to only include variables that exist in annual Compustat data (comp.funda).
    
    Some variables like 'prcc' only exist in quarterly data (comp.fundq), not annual.
    
    Parameters:
    -----------
    vars_list : list
        List of variable names (base names without 'q' suffix)
        
    Returns:
    --------
    list
        List of variable names compatible with annual Compustat data
    """
    # Variables that DON'T exist in annual data (comp.funda)
    # These are quarterly-only variables
    annual_exclusions = {
        'prcc',     # Price Close - quarterly only (annual uses 'prc' or 'prca', but we don't need it)
        'dvpsp',    # Common Dividends Paid per Share - quarterly only (annual uses 'dvpdp', but we don't need it)
        'datacqtr', # Calendar Data Year and Quarter - quarterly only
        'datafqtr', # Fiscal Data Year and Quarter - quarterly only
        'fqtr',     # Fiscal Quarter - quarterly only
        'fyearq',   # Fiscal Year - quarterly only
        'rdq',      # Earnings Announcement Date - quarterly only (Report Date Quarterly)
    }
    
    # Filter out quarterly-only variables
    annual_vars = [var for var in vars_list if var.lower() not in annual_exclusions]
    
    return annual_vars


def add_quarterly_suffix(vars_list):
    """
    Add 'q' suffix to variable names for quarterly Compustat pulls.
    
    Identifiers (gvkey, cusip, datadate, conm, quarterly date vars) are returned unchanged.
    Special cases: capx -> capxy (not capxq), dvpsp -> dvpspq
    All other variables get 'q' appended.
    
    Parameters:
    -----------
    vars_list : list
        List of variable names (base names without 'q' suffix)
        
    Returns:
    --------
    list
        List of variable names with 'q' suffix added (except identifiers and special cases)
    """
    # Identifiers that should NOT get 'q' suffix
    identifiers = {
        'gvkey', 'cusip', 'datadate', 'conm',
        'datacqtr', 'datafqtr', 'fqtr', 'fyearq', 'rdq'  # Quarterly date identifiers
    }
    
    # Special cases: variable -> quarterly variable name
    special_cases = {
        'capx': 'capxy',      # Capital Expenditures (quarterly is capxy, not capxq)
        'dvpsp': 'dvpspq'     # Dividends per Share (quarterly)
    }

    # Annual-only variables we should NOT request from quarterly tables
    annual_only = {'prcc_f'}
    
    # Add 'q' suffix to all variables except identifiers
    quarterly_vars = []
    for var in vars_list:
        var_lower = var.lower()
        # Skip annual-only variables for quarterly pulls
        if var_lower in annual_only:
            continue
        if var_lower in identifiers:
            quarterly_vars.append(var)
        elif var_lower in special_cases:
            quarterly_vars.append(special_cases[var_lower])
        else:
            quarterly_vars.append(var + 'q')
    
    return quarterly_vars

# OPTIONAL VARIABLES - Add these if you want more comprehensive analysis
# Uncomment any of these that you might use in future analysis:
optional_vars = [
    # Additional identifiers
    'fyearq', 'fqtr', 'fyr',  # Fiscal period identifiers
    
    # Additional Balance Sheet
    'rectq',    # Receivables - for working capital analysis
    'invtq',    # Inventories - for REITs (usually minimal)
    'ppentq',   # Property Plant Equipment - key for REITs
    'intanq',   # Intangible Assets
    'ceqq',     # Common Equity (alternative to seqq)
    'actq',     # Current Assets - for liquidity ratios
    'lctq',     # Current Liabilities - for liquidity ratios
    
    # Additional Income Statement  
    'revtq',    # Revenue - for revenue-based ratios
    'cogsq',    # Cost of Goods Sold - for gross margin
    'xsgaq',    # SG&A Expenses - for operating efficiency
    'oiadpq',   # Operating Income - for operating ratios
    'piq',      # Pretax Income
    'txtq',     # Income Taxes
    'xintq',    # Interest Expense - for interest coverage
    
    # Additional Market Data
    # 'mkvaltq',  # Market Value (redundant with prccq * cshoq)
    # 'epsfxq',   # EPS Diluted (redundant with niq / cshoq)
    
    # Additional Cash Flow
    # 'oancfy',   # Operating Cash Flow - for cash flow analysis
    # 'ivncfy',   # Investing Cash Flow
    # 'fincfy',   # Financing Cash Flow
]

# To use optional variables, uncomment this line:
# compustat_vars.extend([var for var in optional_vars if not var.startswith('#')])

# =============================================================================
# CRSP VARIABLE DEFINITIONS
# =============================================================================

# CORE CRSP VARIABLES - Configure what to pull from CRSP (crsp.msf table)
# Only including variables that definitely exist in all versions of crsp.msf
crsp_vars = [
    # Identifiers (always needed)
    'cusip', 'permno', 'permco',

    # Date variables
    'date',

    # Price and Returns Data (core variables that exist in all CRSP versions)
    'prc',          # Price (negative if bid/ask average)
    'ret',          # Total Return
    'retx',         # Return without Dividends
    'vol',          # Volume
    'shrout',       # Shares Outstanding (thousands)
]

# OPTIONAL CRSP VARIABLES - Add these if you want more comprehensive market data
# Note: Some variables may not exist in all CRSP versions - test before using
optional_crsp_vars = [
    # Exchange and Share Information (may vary by CRSP version)
    # 'exchcd',     # Exchange Code (may be 'hexcd' in some versions)
    # 'shrcd',      # Share Code (may be 'hshrcd' in some versions)

    # Additional Price Data (may not be available in all CRSP versions)
    # 'openprc',    # Opening Price (not in all versions)
    # 'numtrd',     # Number of Trades (not in all versions)
    # 'bid',        # Bid Price (not in all versions)
    # 'ask',        # Ask Price (not in all versions)

    # Market indices (if available)
    # 'sprtrn',     # S&P 500 Total Return Index
    # 'spretx',     # S&P 500 Return (excl. dividends)

    # Note: For delisting returns, need separate query to crsp.msedelist:
    # 'dlret',      # Delisting Return (requires join with msedelist)
    # 'dlretx',     # Delisting Return without Dividends (requires join with msedelist)
]

# To use optional variables, uncomment this line:
# crsp_vars.extend([var for var in optional_crsp_vars if not var.startswith('#')])

# Remove duplicates and ensure clean variable list
crsp_vars = list(dict.fromkeys(crsp_vars))  # Remove duplicates while preserving order

# =============================================================================
# CONFIGURATION VALIDATION AND DISPLAY
# =============================================================================

def print_config_summary():
    """Print a summary of current configuration settings"""
    print(f"Raw Compustat Data Directory: {COMPUSTAT_RAW_DIR}")
    print(f"Raw CRSP Data Directory: {CRSP_RAW_DIR}")
    print(f"Final Datasets Directory: {FINAL_DATASETS_DIR}")
    print(f"Data refresh mode: {'REFRESH' if REFRESH_DATA else 'USE CACHED'}")
    print(f"Filtering method: {'PREDEFINED GVKEYS' if USE_PREDEFINED_GVKEYS else f'SIC codes {SIC_FILTER}'}")
    if USE_PREDEFINED_GVKEYS:
        if PREDEFINED_GVKEYS:
            # Show the actual file that was loaded (CSV or TXT)
            csv_file = PROCESSED_DATA_DIR / "merged_chars_crsp_gvkeys.csv"
            txt_file = PROCESSED_DATA_DIR / "merged_chars_crsp_gvkeys.txt"
            gvkey_file = csv_file if csv_file.exists() else txt_file
            print(f"GVKEYs to download: {len(PREDEFINED_GVKEYS)} GVKEYs loaded from {gvkey_file}")
            print(f"  Examples: {', '.join(PREDEFINED_GVKEYS[:5])}...")
        else:
            csv_file = PROCESSED_DATA_DIR / "merged_chars_crsp_gvkeys.csv"
            txt_file = PROCESSED_DATA_DIR / "merged_chars_crsp_gvkeys.txt"
            gvkey_file = csv_file if csv_file.exists() else txt_file
            print(f"WARNING: No GVKEYs loaded from {gvkey_file}")
            print("  Set USE_PREDEFINED_GVKEYS = False to use SIC filter instead")
    else:
        print(f"SIC codes to download: {len(SIC_FILTER)} codes (REITs and related companies)")
    print(f"Date range: {start_date} to {end_date}")
    print(f"Compustat variables: {len(compustat_vars)} variables")
    print(f"CRSP variables: {len(crsp_vars)} variables")
    print("="*60)

