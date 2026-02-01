# WRDS Databases Reference
Query patterns, linking logic, and data construction for finance and real estate research.

## Compustat Databases

### Annual Data (comp.funda)
Primary balance sheet and income statement for annual financial statements.

**Key Variables**:
- Identifiers: `gvkey`, `cusip`, `datadate`, `conm` (company name)
- Income: `revt` (revenue), `ni` (net income), `oiadp` (operating income)
- Balance Sheet: `at` (total assets), `lt` (liabilities), `seq` (equity)
- Cash Flow: `oancf` (operating cash flow), `capx` (capital expenditure)

**Query Pattern**:
```sql
SELECT gvkey, cusip, datadate, at, lt, revt, ni
FROM comp.funda
WHERE gvkey IN ('000001', '000002')
  AND datadate >= '2010-01-01'
  AND datadate <= '2024-12-31'
ORDER BY gvkey, datadate
```

### Quarterly Data (comp.fundq)
Quarterly financials with additional quarterly-specific variables.

**Key Variables** (add 'q' suffix):
- `atq`, `ltq`, `revtq`, `niq` (quarterly equivalents)
- `datacqtr`: Calendar quarter (format: YYYYQ)
- `datafqtr`: Fiscal quarter
- `fqtr`: Fiscal quarter number (1-4)
- `rdq`: Report date (earnings announcement)

**Special Cases**:
- `capxy`: Capital expenditure (quarterly, not `capxq`)
- `prcc_f`: Fiscal year-end price (annual only, not in quarterly)

### Company Information (comp.company)
Static company-level identifiers and classifications.

**Useful Fields**:
- `sic`: Standard Industrial Classification code
- `gics`: GICS sector/industry codes
- `cik`: SEC Central Index Key
- `conm`: Legal company name
- `state`: State of incorporation

**Sample Query**:
```sql
SELECT gvkey, cusip, sic, cik
FROM comp.company
WHERE sic >= 6500 AND sic < 6800  -- Real estate
```

## CRSP Databases

### Monthly Stock File (crsp.msf)
Monthly stock prices, returns, and trading activity.

**Core Variables**:
- `permno`, `permco`: CRSP permanent identifiers
- `date`: Calendar date
- `prc`: Stock price (negative if bid/ask average)
- `ret`: Total return (including dividends)
- `retx`: Return excluding dividends
- `shrout`: Shares outstanding (thousands)
- `vol`: Trading volume

**Query Pattern**:
```sql
SELECT permno, date, prc, ret, shrout
FROM crsp.msf
WHERE permno IN (10001, 10002)
  AND date >= '2010-01-01'
  AND date <= '2024-12-31'
ORDER BY permno, date
```

### Delisting Information (crsp.msedelist)
Delisting codes, returns, and removal dates.

**Key Variables**:
- `permno`, `dlstdt`: Delisting date
- `dlret`: Delisting return
- `dlretx`: Delisting return without dividends
- `dlstcd`: Delisting code (500=liquidation, 520=bankruptcy, 580=acquisition)

## Linking Tables

### CUSIP-GVKEY Linking (comp.ccmxpf_linkhist)
Maps CUSIP (CRSP) to GVKEY (Compustat) with link history and effective dates.

**Logic**:
- One CUSIP can map to multiple GVKEYs (company changes)
- One GVKEY can map to multiple CUSIPs (share class changes)
- Use `linkdt` (link date) and `linkenddt` (link end date) for period matching

**Best Practice - Quarterly CRSP-Compustat Merge**:
```sql
-- 1. Convert CRSP monthly to quarterly (take last date in quarter)
-- 2. Merge CRSP to CUSIP-GVKEY link based on date overlap
-- 3. Match to Compustat quarterly on GVKEY + datacqtr
-- 4. Handle many-to-one and many-to-many relationships
-- 5. Track coverage: expect 85-90% successful matches
```

**Common Issues**:
- **Multiple matches**: Use link priority (`linkprim`) or manual inspection
- **Timing mismatches**: CRSP is monthly, Compustat quarterly; align to quarters carefully
- **Missing links**: Firms with recent IPOs or delisted companies may have incomplete history

### CIK Link (comp.ccmxpf_lnkhist)
Maps between Compustat GVKEY and SEC CIK numbers (via CUSIP).

**Use Case**: Merging with SEC EDGAR or other CIK-based sources.

## REIT-Specific Variables

### Funds From Operations (FFO)
- `ffo`: FFO reported by company (or construct as `ni + dp`)
- Adjustments: Add back depreciation, impairments; subtract gains on sales

**Construction**:
```
FFO = Net Income + Depreciation - Gains on Sale of RE
    = ni + dp - sret (approximately)
```

### Real Estate Assets
- `ret`: Total real estate property
- `ip`: Investment property
- `ppent`: Net property, plant, equipment (includes RE for older REITs)

### EBITDA-re
Extension of EBITDA with RE adjustments:
```
EBITDAre = EBIT + Depreciation + Amortization + RE-specific adjustments
         = oiadp + dp + (impairment adjustments)
```

## Panel Structure Validation

### Completeness Check
- **Balanced**: Every firm-quarter appears for all periods
- **Unbalanced**: Firms enter/exit at different dates (typical)
- Expected coverage: 85-90% of CRSP matched to Compustat

### Identifying Issues
```python
# Check for duplicates
df.groupby(['gvkey', 'datacqtr']).size().value_counts()

# Missing periods
periods = df.groupby('gvkey')['datacqtr'].nunique()
periods[periods < expected_count]

# Stale data (lagged reporting)
df.groupby('datacqtr')['rdq'].apply(lambda x: (x - x.index).days.describe())
```

## Variable Construction Formulas

### Market Capitalization
```
Market Cap = Price (end of quarter) × Shares Outstanding
           = prccq × cshoq
```

### Leverage
```
Debt-to-Assets = (dlc + dltt) / at
Debt-to-Equity = (dlc + dltt) / seq
```

### Return on Assets
```
ROA = Net Income / Lagged Total Assets
    = ni / L.at  (in year-on-year or quarterly form)
```

### Tobin's Q
```
Q = (Market Value of Equity + Total Debt - Cash) / Total Assets
  = (prcc × csho + dltt + dlc - che) / at
```

## Common Data Issues

1. **Missing CUSIP**: ~5-10% of CRSP records lack valid CUSIP (delisted firms)
2. **Duplicate GVKEYs**: Company spinoffs, mergers; use link dates to resolve
3. **Stale Fundamentals**: Quarterly data reported 30-90 days after period end (use `rdq`)
4. **Data Revisions**: Compustat updates historical data; use pull date to track versions
5. **Survivorship Bias**: Always include delisted firms; use CRSP delisting file for returns

## SQL Query Building Tips

- **Always filter date range** before joining (huge performance gain)
- **Use lowercase** for Compustat identifiers internally
- **Convert dates** to YYYYMMDD format early (avoids sorting issues)
- **Handle nulls carefully**: Missing = not reported (not zero)
- **Test on small sample** (100-1000 records) before full pull

## References

- WRDS Compustat Documentation: https://wrds-www.wharton.upenn.edu/pages/support/
- CRSP Manual: https://www.crsp.org/
- Industry Research: REIT data typically in SIC 6798, property operations 6512-6519
