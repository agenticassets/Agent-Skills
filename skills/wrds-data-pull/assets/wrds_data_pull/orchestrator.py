"""
Main Orchestrator for WRDS Data Pipeline
=========================================

This is the main entry point for the WRDS data pulling and processing pipeline.
It coordinates execution of all modules in the correct sequence.

Usage:
    python 5---main_orchestrator.py

Or import and use programmatically:
    import importlib
    orchestrator = importlib.import_module('5---main_orchestrator')
    orchestrator.main()
"""

import sys
import importlib.util
from pathlib import Path

# Get current directory for module loading
current_dir = Path(__file__).parent

def load_module(module_name, file_path):
    """Load a module from file path (handles numbered filenames)."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import modules using file paths (handles numbered filenames)
cfg = load_module("config_wrds_data", current_dir / "1---config_wrds_data.py")
pull_compustat_data_module = load_module("pull_compustat_data", current_dir / "2---pull_compustat_data.py")
pull_crsp_data_module = load_module("pull_crsp_data", current_dir / "3---pull_crsp_data.py")
merge_and_process_data_module = load_module("merge_and_process_data", current_dir / "4---merge_and_process_data.py")

# Extract functions for easier use
pull_compustat_data = pull_compustat_data_module.pull_compustat_data
pull_crsp_data = pull_crsp_data_module.pull_crsp_data
merge_and_process_data = merge_and_process_data_module.merge_and_process_data


def main():
    """
    Main execution function that orchestrates the entire WRDS data pipeline.
    
    Steps:
    1. Print configuration summary
    2. Pull Compustat data
    3. Pull CRSP data (if Compustat data available)
    4. Merge and process data
    5. Print final summary
    """
    print("="*60)
    print("WRDS DATA PIPELINE - QUARTERLY VERSION")
    print("="*60)
    print()
    
    # Print configuration summary
    cfg.print_config_summary()
    print()
    
    try:
        # STEP 1: Pull Compustat data (both annual and quarterly)
        print("\n" + "="*60)
        print("STEP 1: PULLING COMPUSTAT DATA")
        print("="*60)
        compustat_annual_df, compustat_quarterly_df, company_info = pull_compustat_data(cfg)
        
        if compustat_quarterly_df is None or len(compustat_quarterly_df) == 0:
            raise ValueError("Failed to retrieve Compustat quarterly data")
        
        print(f"[OK] Compustat annual data pulled successfully: {len(compustat_annual_df):,} observations")
        print(f"[OK] Compustat quarterly data pulled successfully: {len(compustat_quarterly_df):,} observations")
        print()
        
        # STEP 2: Pull CRSP data (using quarterly Compustat data for CUSIP matching)
        print("\n" + "="*60)
        print("STEP 2: PULLING CRSP DATA")
        print("="*60)
        crsp_quarterly_df = pull_crsp_data(cfg, compustat_quarterly_df)
        
        if crsp_quarterly_df is not None:
            print(f"[OK] CRSP data pulled and aggregated successfully: {len(crsp_quarterly_df):,} quarterly observations")
        else:
            print("[WARNING] CRSP data not available - proceeding with Compustat only")
        print()
        
        # STEP 3: Merge and process data (using quarterly Compustat data)
        print("\n" + "="*60)
        print("STEP 3: MERGING AND PROCESSING DATA")
        print("="*60)
        final_df = merge_and_process_data(cfg, compustat_quarterly_df, crsp_quarterly_df)
        
        if final_df is None or len(final_df) == 0:
            raise ValueError("Failed to process final dataset")
        
        print(f"[OK] Data processing completed successfully: {len(final_df):,} observations")
        print()
        
        # Final summary
        print("\n" + "="*60)
        print("PIPELINE EXECUTION COMPLETE")
        print("="*60)
        print(f"Final dataset: {len(final_df):,} observations")
        print(f"Final dataset saved to: {cfg.FINAL_DATASETS_DIR}")
        print(f"  - CSV: {cfg.FINAL_DATA_CSV}")
        print(f"  - Stata: {cfg.FINAL_DATA_DTA}")
        print(f"  - Pickle: {cfg.FINAL_DATA_PKL}")
        print("="*60)
        
        return final_df
        
    except Exception as e:
        print("\n" + "="*60)
        print("ERROR: Pipeline execution failed")
        print("="*60)
        print(f"Error message: {str(e)}")
        print("\nPlease check:")
        print("  - WRDS connection credentials")
        print("  - Data directory permissions")
        print("  - Configuration settings")
        print("="*60)
        raise


if __name__ == "__main__":
    final_df = main()

