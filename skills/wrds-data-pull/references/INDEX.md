# WRDS Data Pull References - Complete Index

Comprehensive documentation system for financial and real estate data extraction, merging, and variable construction.

**Total Coverage**: 2,600+ lines across 7 reference files
**Format**: Progressive disclosure (Table of Contents in each file)
**Purpose**: Load-as-needed reference for data pulls and analysis

---

## File Organization

### 1. **wrds-databases.md** (208 lines)
**Foundational database schemas**

Quick reference for database structure, common variables, and basic query patterns.

**Contents**:
- Compustat Annual (comp.funda)
- Compustat Quarterly (comp.fundq)
- CRSP Monthly/Daily (crsp.msf, crsp.dsf)
- Linking tables (CCM, CIK)
- REIT-specific variables
- Basic queries

**When to use**: Initial data pull planning, schema exploration

**Key sections**: ~10 SQL query patterns, REIT variable definitions

---

### 2. **compustat-crsp.md** (437 lines)
**Detailed Compustat & CRSP comprehensive guide**

Expanded database documentation with timing, coverage, and integration strategies.

**Contents**:
- Compustat Annual full schema (all variables by section)
- Compustat Quarterly (quarter identifiers, YTD variables, report dates)
- CRSP Monthly/Daily (return calculations, delisting codes)
- Timing alignment strategies (quarterly matching, earnings announcement)
- Coverage comparison tables
- Data quality checks (Python code)

**When to use**: Designing panel structure, merging quarterly data, understanding timing

**Key sections**: Quarterly alignment logic, delisting code reference, ~15 variable tables

---

### 3. **merge-keys.md** (371 lines)
**Linking table strategies and many-to-many relationship handling**

Critical for multi-database integration and complex merge logic.

**Contents**:
- CUSIP-GVKEY linking (comp.ccmxpf_linkhist)
- PERMNO-GVKEY chain linking
- CIK mapping (SEC)
- ISIN conversion
- Date-range matching logic
- Fuzzy matching (company name, ticker warnings)
- 2 complete Python merge examples (quarterly panel, delisting handling)

**When to use**: Cross-database merges, handling spinoffs/M&A, date-aware filtering

**Key sections**: 5 linking table definitions, date overlap logic, 2 production-ready merge scripts

---

### 4. **known-data-issues.md** (474 lines)
**Database-specific gotchas, survivorship bias, and workarounds**

Essential reading before analysis; prevents common mistakes.

**Contents**:
- Compustat issues (revisions, restatements, missing fiscal year-ends, negative equity)
- CRSP issues (negative prices, delisting returns, missing data, share counts)
- Linking table problems (coverage gaps, stale links, duplicates)
- Survivorship bias (returns, listing bias, small-firm bias)
- Restatement tracking (SEC database, comparison pulls)
- Database-specific adjustments (timing, fiscal vs. calendar)

**When to use**: Data validation, diagnostic checks, justifying sample filters

**Key sections**: 8 data quality checks (Python code), survivorship bias fixes, restatement examples

---

### 5. **merge-keys.md** (371 lines)
**See above; contains practical full-pipeline merge examples**

---

### 6. **ibes-thomson.md** (469 lines)
**Analyst forecasts and institutional investor data**

Covers forward-looking and holdings-based datasets.

**Contents**:
- IBES (Institutional Brokers Estimate System)
  - Summary & detail data tables
  - Earnings surprise calculation
  - Data quality issues (missing tickers, stale estimates)
  - Query patterns
- Thomson Reuters 13F Holdings
  - Institutional investor positions
  - Ownership metrics construction
  - Data quality (CUSIP recovery, stale holdings)
- Data filtering & quality checks (Python)
- Full merge example (sentiment + holdings → returns predictability)

**When to use**: Forward guidance analysis, institutional ownership studies, earnings surprise events

**Key sections**: Earnings surprise formula, institutional ownership %, ownership concentration (Herfindahl), full 5-table merge example

---

### 7. **real-estate-databases.md** (376 lines)
**Property transaction and commercial real estate data**

Specialized for real estate research and REIT analysis.

**Contents**:
- CoreLogic Deed & Tax Records
  - Transaction prices, assessments, property characteristics
  - Common issues (missing prices, name standardization, multi-parcel transactions)
- ZTRAX (Zillow Transaction & Assessor)
  - Cleaned transaction data, alternative to CoreLogic
  - Linking strategy (address-based merge)
- CoStar Property Database
  - Commercial property metrics (NOI, cap rate, occupancy)
  - REIT portfolio linkage
- NCREIF (Institutional property index)
  - Quarterly return decomposition
  - Asset class benchmarking
- Linking strategies (cross-database merges, REIT portfolio matching)

**When to use**: Real estate transaction studies, REIT analysis, property-level metrics

**Key sections**: Property ID linking, NCREIF return calculation, address standardization logic

---

### 8. **alternative-data.md** (459 lines)
**News sentiment, SEC text, patents, web traffic**

Newer/alternative data sources for enriched analysis.

**Contents**:
- RavenPack ESG & Sentiment
  - News sentiment scores, ESG composite
  - Sentiment bias issues, look-ahead bias
  - Merge to returns (event study)
- SEC EDGAR Metadata & Filing Analytics
  - Form types, filing dates, report dates
  - Text analysis (MD&A length, risk factor count)
  - Linking 10-K to Compustat
- Patent Data
  - USPTO/Google Patents, NBER pre-matched database
  - Patent productivity metrics (patents per R&D)
- Web Traffic & Sentiment Alternatives
  - Google Trends, GDELT, NewsAPI, free sources
- Full 6-signal merge example (sentiment + patents + EDGAR → returns)

**When to use**: Forward guidance studies, text analysis, patent productivity, ESG analysis

**Key sections**: Sentiment calculation, patent linking, multi-signal merge (6 datasets), EDGAR text metrics

---

### 9. **variable-construction.md** (305 lines)
**Standard financial ratios and metrics with formulas**

Quick reference for metric definitions and implementation.

**Contents**:
- Financial ratios (Tobin's Q, leverage, ROA, ROE, B/M)
- Market-based metrics (market cap, enterprise value, P/E)
- REIT metrics (FFO, AFFO, EBITDAre, NAV discount)
- Return measures (BHAR, CAR, cumulative returns)
- Portfolio construction (Fama-French breakpoints, momentum)
- Common pitfalls (timing, negative equity, share splits, delisting)

**When to use**: Variable coding, metric validation, citing ratio formulas

**Key sections**: 8 variable formulas with Python code, 4 common pitfall fixes, academic references

---

## Navigation Guide

### By Task

**"I need to pull Compustat + CRSP data"**
1. Start: **wrds-databases.md** (schema overview)
2. Deepen: **compustat-crsp.md** (detailed timing, quarterly alignment)
3. Merge: **merge-keys.md** (CUSIP-GVKEY linking, date-aware merge)
4. Validate: **known-data-issues.md** (data quality checks)

**"I'm analyzing earnings surprises or analyst forecasts"**
1. Start: **ibes-thomson.md** (schema, data quality)
2. Construct: **variable-construction.md** (surprise formula)
3. Validate: **known-data-issues.md** (check for survivorship)

**"I'm doing real estate research"**
1. Start: **real-estate-databases.md** (CoreLogic, ZTRAX, CoStar, NCREIF)
2. Link: **merge-keys.md** (address-based merging)
3. Enrich: **alternative-data.md** (patent data for firms, sentiment)

**"I want to add sentiment/ESG/patent data"**
1. Start: **alternative-data.md** (data availability, quality issues)
2. Link: **merge-keys.md** (CIK linking, address linking)
3. Validate: **known-data-issues.md** (survivorship concerns)

**"I need to construct variables"**
1. Start: **variable-construction.md** (formulas, Python code)
2. Deepen: **wrds-databases.md** (raw variable definitions)
3. Validate: **known-data-issues.md** (edge cases, filters)

### By Database

| Database | Primary File | Secondary Files |
|----------|--------------|-----------------|
| **Compustat** | compustat-crsp.md | wrds-databases.md, known-data-issues.md |
| **CRSP** | compustat-crsp.md | wrds-databases.md, known-data-issues.md |
| **Linking (CCM)** | merge-keys.md | compustat-crsp.md |
| **IBES** | ibes-thomson.md | variable-construction.md |
| **13F Holdings** | ibes-thomson.md | merge-keys.md |
| **CoreLogic/ZTRAX** | real-estate-databases.md | merge-keys.md |
| **CoStar** | real-estate-databases.md | merge-keys.md |
| **NCREIF** | real-estate-databases.md | variable-construction.md |
| **RavenPack** | alternative-data.md | merge-keys.md |
| **SEC EDGAR** | alternative-data.md | merge-keys.md |
| **Patents** | alternative-data.md | merge-keys.md |

---

## Quick Reference: Common Queries

### Quarterly CRSP-Compustat Panel
**Files**: compustat-crsp.md (Timing section), merge-keys.md (Example 1)
**Query approach**: Monthly CRSP → quarterly (last day) → lag fundamentals 60 days → merge

### Earnings Surprise Event Study
**Files**: ibes-thomson.md (Earnings Surprise section), variable-construction.md (Return Measures)
**Formula**: (Actual - Median Estimate) / Median Estimate
**Sample filter**: >= 3 analysts, valid actual

### Delisting-Inclusive Returns
**Files**: known-data-issues.md (Survivorship bias), merge-keys.md (Example 2)
**Key step**: Merge CRSP msedelist (dlret) to monthly returns, fillna()

### REIT Portfolio Analysis
**Files**: real-estate-databases.md (CoStar, NCREIF), compustat-crsp.md (REIT SIC codes)
**Sample filter**: SIC 6798 or GICS equivalent
**Metrics**: FFO/share, NAV discount, occupancy from CoStar

### Multi-Signal Predictability
**Files**: alternative-data.md (Full merge example)
**Signals**: Sentiment (RavenPack) + Patents + EDGAR text + IBES + 13F
**Join method**: All on dates (daily/monthly/quarterly depending on signal)

---

## Data Coverage & Limitations Summary

| Source | Coverage | Frequency | Lag | Limitation |
|--------|----------|-----------|-----|-----------|
| **Compustat** | 7K firms, 1950+ | A/Q | 60-90d | Domestic focus |
| **CRSP** | 30K securities, 1925+ | D/M | Live | US only |
| **IBES** | 10K firms | Daily | 1-2d | Survivorship bias |
| **13F** | 3.5K institutions | Q | 45d | > $100M AUM only |
| **CoreLogic** | 150M properties | Q | 3-12m | County lag varies |
| **ZTRAX** | 140M properties | W | 1-2w | Data cleaning issues |
| **CoStar** | 2.5M commercial | M | 1m | Commercial only |
| **NCREIF** | 10K properties | Q | 60d | Institutional only |
| **RavenPack** | 70K securities | Real-time | 0d | Sentiment bias |
| **Patents** | 12M utility | Q | 6-12m | US focus |

---

## Style & Format Notes

- **Code examples**: Python preferred; SQL provided for queries
- **Line length**: 200-460 lines per file (load-as-needed design)
- **Table of Contents**: In each file for files > 100 lines
- **SQL**: Uses WRDS syntax; includes filter logic (date ranges, data formats)
- **Python**: pandas + statsmodels focus; imports specified
- **References**: Academic papers & URLs provided throughout

---

## Version & Maintenance

**Last Updated**: Feb 2026
**Format**: Markdown with code blocks (Python, SQL)
**Total Content**: 2,630 lines

**Maintained for**:
- WRDS platform (Wharton Research Data Services)
- Standard finance/real estate research workflows
- Cross-database linking (Compustat, CRSP, IBES, SEC EDGAR, etc.)

**To add**:
- BoardEx (board composition)
- ISS (shareholder votes, governance)
- Data.World (alternative datasets)
- Custom text analysis (10-K/10-Q)

---

## Quick Links

- **WRDS Platform**: https://wrds-www.wharton.upenn.edu/
- **CRSP Manual**: https://www.crsp.org/
- **Compustat Support**: https://www.spglobal.com/marketintelligence/
- **SEC EDGAR**: https://www.sec.gov/cgi-bin/browse-edgar
- **USPTO Patents**: https://www.uspto.gov/patents-application-process/search-patents
- **CoreLogic**: https://www.corelogic.com/
- **NCREIF**: https://www.ncreif.org/
