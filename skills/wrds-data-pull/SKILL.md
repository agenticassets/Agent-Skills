---
name: wrds-data-pull
description: Use when pulling data from WRDS databases, merging financial datasets via linking tables, validating panel structure, or constructing financial variables for finance and real estate research.
triggers:
  - WRDS
  - Compustat
  - CRSP
  - IBES
  - Thomson Reuters
  - BoardEx
  - ISS
  - CoreLogic
  - ZTRAX
  - CoStar
  - NCREIF
  - RavenPack
  - SEC EDGAR
  - CUSIP
  - GVKEY
  - PERMNO
  - CCM
  - ICLINK
  - financial data extraction
  - panel data
role: specialist
scope: implementation
output-format: code
---

# WRDS Data Pull

Automated WRDS data extraction with pre-built query templates, merge logic, validation, and variable documentation for finance and real estate research.

## Overview

This skill packages 20+ years of WRDS research patterns into reusable components: parameterized SQL queries for major databases, step-by-step merge sequences with proper key handling, automated panel diagnostics, and standard financial variable construction with citations.

**Saves 20-40 hours per project** by eliminating repetitive query writing, merge debugging, and data validation setup.

## Quick Start

### Install Existing WRDS Pipeline

Copy the production-tested pipeline from an existing project:

```python
# Copy existing scripts to your project
import shutil
src = "path/to/---Overleaf_Template/Code/Python/1---wrds-direct-connection"
dst = "your_project/data_pipeline"
shutil.copytree(src, dst)

# Configure credentials
# Add to .env file: WRDS_USERNAME=your_username

# Run full pipeline
python data_pipeline/5---main_orchestrator.py
```

The pipeline includes:
- `1---config_wrds_data.py`: Configuration with 100+ Compustat/CRSP variables
- `2---pull_compustat_data.py`: Annual and quarterly pulls with caching
- `3---pull_crsp_data.py`: Monthly data aggregated to quarterly
- `4---merge_and_process_data.py`: CUSIP-based linking (99% PERMNO coverage)
- `5---main_orchestrator.py`: Coordinated execution

### Standalone Usage Pattern

For custom workflows, use the modular components:

```python
from wrds_data_pull import query_templates, merge_utils

# 1. Pull data with template
comp_query = query_templates.compustat_quarterly(
    variables=["gvkey", "datadate", "atq", "ltq"],
    start_date="2020-01-01",
    end_date="2023-12-31"
)

# 2. Execute query
import wrds
conn = wrds.Connection(wrds_username="username")
comp_df = conn.raw_sql(comp_query)

# 3. Validate panel
from wrds_data_pull.panel_diagnostics import validate_panel
diag = validate_panel(comp_df, unit_id="gvkey", time_id="datadate")
print(f"Panel type: {diag['panel_type']}, Duplicates: {diag['n_duplicates']}")
```

## Core Workflow

### 1. Database Selection

**Compustat + CRSP** (most common):
- Use for standard firm panels with financial statements and stock returns
- See [compustat-crsp.md](references/compustat-crsp.md) for query templates

**IBES + Thomson Reuters**:
- Analyst forecasts, institutional holdings, insider trading
- See [ibes-thomson.md](references/ibes-thomson.md)

**Real estate databases**:
- CoreLogic, ZTRAX, CoStar, NCREIF for property-level data
- See [real-estate-databases.md](references/real-estate-databases.md)

**Alternative data**:
- RavenPack sentiment, SEC EDGAR, patent data
- See [alternative-data.md](references/alternative-data.md)

### 2. Query Execution

All query templates are parameterized:

```python
from wrds_data_pull.query_templates import compustat_quarterly

# Basic pull
query = compustat_quarterly(
    variables=["gvkey", "datadate", "atq", "niq"],
    start_date="2020-01-01",
    end_date="2023-12-31"
)

# With filters
query = compustat_quarterly(
    variables=["gvkey", "datadate", "atq", "niq"],
    start_date="2020-01-01",
    end_date="2023-12-31",
    gvkey_list=["001045", "001078"],  # Filter to specific firms
    filters={"indfmt": "INDL", "datafmt": "STD"}  # Standard filters
)
```

### 3. Data Merging

**Compustat-CRSP via CCM linking table**:
- See [merge-keys.md](references/merge-keys.md) for linking table logic
- Date-range validation (LINKDT to LINKENDDT)
- Link type filtering (LC=primary, LU=secondary)

```python
from wrds_data_pull.merge_utils import merge_compustat_crsp_via_ccm

merged_df = merge_compustat_crsp_via_ccm(
    compustat_df=comp_df,
    crsp_df=crsp_df,
    link_type="LC"  # Primary links only
)
```

**CUSIP-based linking** (alternative, higher coverage):
- Production-tested: 99% PERMNO coverage vs. 86.8% for CCM
- Handles CUSIP 8-character matching, date alignment via calendar quarters

```python
from wrds_data_pull.merge_utils import merge_via_cusip

merged_df = merge_via_cusip(
    compustat_df=comp_df,  # Must have 'cusip' column
    crsp_df=crsp_df,       # Must have 'cusip', 'year', 'quarter'
    merge_on=["cusip", "year", "quarter"]
)
```

### 4. Panel Validation

Run diagnostics after every pull:

```bash
python scripts/validate_panel.py \
    --input merged_data.parquet \
    --unit_id gvkey \
    --time_id year_quarter
```

Checks:
- **Balance**: Balanced vs. unbalanced panel classification
- **Duplicates**: Primary key violations
- **Coverage**: % non-missing by variable, by year
- **Known issues**: Negative book equity, zero shares, missing CUSIPs

### 5. Variable Construction

Standard formulas with academic citations:

```python
from wrds_data_pull.variable_builders import FinancialRatios

ratios = FinancialRatios(df)
df['tobins_q'] = ratios.tobins_q()    # (ME + BV_debt) / BV_assets
df['leverage'] = ratios.leverage()     # Total debt / Total assets
df['roa'] = ratios.roa()               # Net income / Total assets
```

See [variable-construction.md](references/variable-construction.md) for complete formulas.

## Scripts

### setup_wrds.py
Configure WRDS connection, validate credentials, test database access.

```bash
python scripts/setup_wrds.py --username your_username
```

### validate_panel.py
Panel diagnostics (balance, duplicates, coverage, known issues).

```bash
python scripts/validate_panel.py \
    --input data.parquet \
    --unit_id gvkey \
    --time_id year_quarter \
    --output diagnostics.txt
```

### coverage_report.py
Variable-level missing data report with LaTeX output for papers.

```bash
python scripts/coverage_report.py \
    --input data.parquet \
    --output coverage_table.tex
```

## Reference Documentation

### Database-Specific Templates
- **[compustat-crsp.md](references/compustat-crsp.md)**: Query templates, variable definitions, known quirks for Compustat (funda/fundq) and CRSP (msf/dsf/msedelist)
- **[ibes-thomson.md](references/ibes-thomson.md)**: IBES analyst forecasts (summary/detail), Thomson Reuters 13F institutional holdings
- **[real-estate-databases.md](references/real-estate-databases.md)**: CoreLogic deed/tax, ZTRAX, CoStar, NCREIF patterns
- **[alternative-data.md](references/alternative-data.md)**: RavenPack sentiment, SEC EDGAR metadata, NBER/PatentsView

### Technical Documentation
- **[merge-keys.md](references/merge-keys.md)**: CCM/ICLINK linking tables, date-range matching, CUSIP/GVKEY/PERMNO handling, fuzzy matching
- **[variable-construction.md](references/variable-construction.md)**: Financial ratios, return measures, size/value/momentum portfolios, real estate metrics with formulas and citations
- **[known-data-issues.md](references/known-data-issues.md)**: Survivorship bias, restatements, backfill, delisting adjustments by database

## Production-Tested Examples

### Example 1: Compustat + CRSP Quarterly Panel

Full pipeline from existing codebase (tested on 35K observations, 280+ variables):

```python
# Use existing pipeline
import importlib.util

# Load orchestrator
spec = importlib.util.spec_from_file_location(
    "orchestrator",
    "Code/Python/1---wrds-direct-connection/5---main_orchestrator.py"
)
orch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(orch)

# Run full pipeline
final_df = orch.main()  # Returns merged Compustat + CRSP data
```

Pipeline includes:
- CUSIP-based linking (99% PERMNO match rate)
- Calendar quarter alignment (datacqtr for Compustat, derived for CRSP)
- Automated data validation and caching
- Multi-format export (parquet, CSV, Stata .dta)

### Example 2: Custom Variables + Validation

```python
# Pull specific variables
from wrds_data_pull.query_templates import compustat_quarterly
import wrds

conn = wrds.Connection(wrds_username="username")

query = compustat_quarterly(
    variables=["gvkey", "datadate", "atq", "ltq", "seqq", "niq"],
    start_date="2015-01-01",
    end_date="2023-12-31"
)

df = conn.raw_sql(query)

# Construct ratios
from wrds_data_pull.variable_builders import construct_financial_ratios
df = construct_financial_ratios(df, ratios=["leverage", "roa"])

# Validate
from wrds_data_pull.panel_diagnostics import validate_panel
diag = validate_panel(df, unit_id="gvkey", time_id="datadate")
print(f"Coverage: {diag['coverage_summary']}")
```

### Example 3: Real Estate Panel

```python
# Pull NCREIF property-level returns
from wrds_data_pull.query_templates import ncreif_property_returns

query = ncreif_property_returns(
    start_date="2010-01-01",
    end_date="2023-12-31",
    property_types=["Office", "Retail", "Apartment"]
)

# Execute and validate
import wrds
conn = wrds.Connection(wrds_username="username")
ncreif_df = conn.raw_sql(query)

# Merge with CoreLogic (requires separate access)
# See real-estate-databases.md for CoreLogic patterns
```

## Known Data Issues

### Compustat
- **Restated data**: Use `datafmt='STD'` for unrestated (standardized) data
- **Fiscal vs. calendar quarters**: Use `datacqtr` for calendar quarters, `datafqtr` for fiscal
- **Negative book equity**: Flag observations where `seqq < 0` (common for distressed firms)

### CRSP
- **Delisting returns**: Merge with `msedelist` table for complete return history
- **Negative prices**: Indicate bid/ask average (use absolute value for market cap)
- **Share codes**: Filter `shrcd IN (10,11)` for common stock only

### CCM Linking Table
- **Date validation**: Always check `datadate BETWEEN LINKDT AND LINKENDDT`
- **Multiple links**: Some firm-quarters have multiple PERMNOs (choose primary: `LINKTYPE='LC'`)
- **Coverage**: CCM achieves ~86.8% match rate; CUSIP-based linking reaches ~99%

See [known-data-issues.md](references/known-data-issues.md) for comprehensive documentation.

## Troubleshooting

### Connection Errors
```python
# Test WRDS access
import wrds
conn = wrds.Connection(wrds_username="username")
print(conn.list_libraries())  # Should show: comp, crsp, ibes, taqm, etc.
conn.close()
```

### Missing Variables
```python
# Check if variable exists in table
conn = wrds.Connection(wrds_username="username")
fields = conn.list_table_fields("comp", "fundq")
print("atq" in [f.lower() for f in fields])  # True if exists
```

### Merge Failures
```python
# Diagnose merge issues
from wrds_data_pull.merge_utils import diagnose_merge

diagnosis = diagnose_merge(
    left_df=comp_df,
    right_df=crsp_df,
    merge_keys=["cusip", "year", "quarter"]
)

print(f"Match rate: {diagnosis['match_rate']:.1%}")
print(f"Left-only: {diagnosis['left_only_count']} observations")
print(f"Right-only: {diagnosis['right_only_count']} observations")
```

## Python Package

The `assets/wrds_data_pull/` directory contains a standalone Python package with modular components:

- `query_templates.py`: Parameterized SQL for all major WRDS databases
- `merge_utils.py`: Merge functions with date validation and diagnostics
- `panel_diagnostics.py`: Balance checks, duplicate detection, coverage stats
- `variable_builders.py`: Financial ratios with formulas and citations
- `__init__.py`: Convenient imports

### Installation
```bash
pip install wrds pandas numpy scipy
```

Add to Python path:
```python
import sys
sys.path.insert(0, "/path/to/wrds-data-pull/assets")
from wrds_data_pull import query_templates, merge_utils
```

Or copy `assets/wrds_data_pull/` directly into your project.
