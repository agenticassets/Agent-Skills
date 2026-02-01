"""
WRDS Data Pull Module
=====================

Automated WRDS data extraction with pre-built query templates, merge logic, and validation
for finance and real estate research.

Provides:
- Configuration management (paths, credentials, variable definitions)
- Compustat and CRSP data pulling with caching
- CUSIP/GVKEY/PERMNO linking and panel validation
- Data merging and cleaning utilities
- Panel diagnostics and variable construction
- Orchestrated execution pipeline

Usage:
    from wrds_data_pull import WRDSPipeline, FinancialRatios
    from wrds_data_pull.config import WRDSConfig
    from wrds_data_pull.panel_diagnostics import validate_panel

    # Configure and run
    config = WRDSConfig(refresh_data=True)
    pipeline = WRDSPipeline(config)
    result = pipeline.run()

    # Add financial ratios
    ratios = FinancialRatios(result)
    result['tobins_q'] = ratios.tobins_q()

    # Validate panel
    diag = validate_panel(result, unit_id='gvkey', time_id='datacqtr')

Modules:
    config: Configuration, paths, and variable definitions
    query_templates: Compustat data pulling and query construction
    crsp_utils: CRSP data pulling and processing
    merge_utils: Data merging and cleaning
    panel_diagnostics: Panel validation and coverage checks
    variable_builders: Financial ratios and REIT metrics
    orchestrator: Coordinated execution of full pipeline
"""

__version__ = "1.0.0"
__author__ = "Academic Research Team"

# Import main components for convenient access
from .config import (
    WRDSConfig,
    load_gvkey_list,
    add_quarterly_suffix,
    get_annual_compatible_vars,
)

from .orchestrator import (
    WRDSPipeline,
    run_wrds_pipeline,
)

from .panel_diagnostics import (
    validate_panel,
    check_panel_balance,
    check_duplicates,
    calculate_coverage,
    winsorize_variable,
)

from .variable_builders import (
    FinancialRatios,
    REITMetrics,
    construct_financial_ratios,
)

__all__ = [
    # Configuration
    "WRDSConfig",
    "load_gvkey_list",
    "add_quarterly_suffix",
    "get_annual_compatible_vars",
    # Pipeline
    "WRDSPipeline",
    "run_wrds_pipeline",
    # Panel diagnostics
    "validate_panel",
    "check_panel_balance",
    "check_duplicates",
    "calculate_coverage",
    "winsorize_variable",
    # Variable construction
    "FinancialRatios",
    "REITMetrics",
    "construct_financial_ratios",
]
