# Compustat & CRSP Comprehensive Reference

Detailed database schema, variable definitions, and data collection methodologies.

## Table of Contents
- Compustat Annual (comp.funda)
- Compustat Quarterly (comp.fundq)
- CRSP Stock Files (msf, dsf)
- Compustat vs. CRSP: Timing and Coverage
- Database Selection Guide

---

## Compustat Annual (comp.funda)

**Frequency**: One record per company per fiscal year
**Coverage**: ~25K firm-years annually (includes delisted firms)
**Update**: Quarterly (typically 60 days after fiscal year-end)

### Core Identifiers

| Variable | Definition | Notes |
|----------|-----------|-------|
| `gvkey` | Global Company Key | Permanent Compustat ID; stable across M&A |
| `cusip` | CUSIP identifier | May be missing for some firms; subject to change |
| `conm` | Company name | Not standardized; use for reference only |
| `tic` | Ticker symbol | Not unique; use for labels only |
| `cik` | SEC Central Index Key | For EDGAR linking |
| `datadate` | Fiscal year-end date | YYYYMMDD format |

### Balance Sheet Items (Annual)

**Assets**:
- `at`: Total assets
- `aco`: Current assets
- `che`: Cash and equivalents
- `rect`: Receivables (gross)
- `invt`: Inventories
- `ppe`: Property, plant, equipment (gross)
- `ppent`: Net PP&E (after depreciation)

**Liabilities**:
- `lt`: Total liabilities
- `lco`: Current liabilities
- `dlc`: Debt in current liabilities (short-term)
- `dltt`: Long-term debt
- `ap`: Accounts payable

**Equity**:
- `seq`: Shareholders' equity (book)
- `retainead`: Retained earnings

### Income Statement Items (Annual)

```
Revenue (Top Line)
├─ revt: Total revenue
├─ revts: Subsidiary revenue
└─ revp: Revenue per customer (rare)

Operating Expenses
├─ cogs: Cost of goods sold
├─ xsga: Selling, general, admin expense
├─ dp: Depreciation and amortization
└─ xrd: R&D expense

Operating & Net Income
├─ oiadp: Operating income before depreciation (EBITDA proxy)
├─ oibdp: Operating income before D&A
├─ ebit: Earnings before interest and taxes
├─ nii: Net interest income
└─ ni: Net income
```

### Cash Flow Items (Annual)

- `oancf`: Operating cash flow
- `capx`: Capital expenditures
- `chech`: Change in cash
- `dvpsx_f`: Dividend per share (fiscal year)
- `dv`: Total dividends

### Valuation & Market Data (Annual)

- `prcc_f`: Price at fiscal year-end (CRSP price match)
- `csho`: Common shares outstanding (millions)
- `ajex`: Adjustment factor (for splits)

### Stock-Specific (Annual)

- `exchg`: Exchange code (11=NYSE, 12=AMEX, etc.)
- `conm`: Company name
- `sic`: Standard Industrial Classification
- `gics`: GICS industry code

**Query Pattern**:
```sql
SELECT gvkey, cusip, conm, datadate, at, lt, seq, revt, ni, oancf, capx
FROM comp.funda
WHERE datadate >= '2015-01-01'
  AND datadate <= '2023-12-31'
  AND indfmt = 'INDL'  -- Exclude consolidations
  AND consol = 'C'     -- Consolidated only
  AND popsrc = 'D'     -- Domestic US entities
  AND datafmt = 'STD'  -- Standard format
ORDER BY gvkey, datadate
```

---

## Compustat Quarterly (comp.fundq)

**Frequency**: One record per company per quarter
**Coverage**: ~100K observations annually
**Lag**: 30-60 days after quarter end (varies by company)

### Key Differences from Annual

1. **All quarterly variables have 'q' suffix**:
   - Annual: `at`, Quarterly: `atq`
   - Annual: `ni`, Quarterly: `niq`
   - Exception: `capxy` (capital expenditure, odd naming)

2. **Quarter Identifiers**:
   - `datacqtr`: Calendar quarter (YYYYQ, e.g., '2023Q4')
   - `fqtr`: Fiscal quarter (1-4, can skip if fiscal year misaligned)
   - `rdq`: Report date (earnings announcement; use this for event studies)

3. **Missing Variables**:
   - `prcc_f`: Not available in quarterly (use CRSP prices)
   - `csho`: Shares outstanding (available in some cases)

### Quarterly-Specific Variables

```
niq       Net income (quarterly)
atq       Total assets (quarterly)
revtq     Revenue (quarterly)
oancfy    Operating cash flow (year-to-date)
capxy     Capital expenditure (year-to-date, not capxq!)
ibq       Income before taxes (quarterly)
txt       Total taxes (sometimes null)
```

**Important**: Some quarterly variables are **cumulative YTD**, not quarterly:
- `oancfy`: Operating cash flow year-to-date (not Q only)
- `capxy`: CapEx year-to-date
- To get quarterly: Subtract previous quarter's YTD values

### Report Date (rdq)

**Use for event studies**. The `rdq` is when earnings became public, typically 1-6 weeks after quarter-end.

```python
# Earnings announcement event window
event_date = df['rdq']  # NOT datadate
window_before = event_date - pd.DateOffset(days=2)
window_after = event_date + pd.DateOffset(days=2)

# 5-day CAR: [-2, +2] around rdq
df['event_flag'] = (df['date'] >= window_before) & (df['date'] <= window_after)
```

### Query Pattern (Quarterly)

```sql
SELECT gvkey, datacqtr, datadate, rdq, atq, revtq, niq, capxy
FROM comp.fundq
WHERE datadate >= '2020-01-01'
  AND datadate <= '2023-12-31'
  AND indfmt = 'INDL'
  AND consol = 'C'
ORDER BY gvkey, datacqtr
```

---

## CRSP Stock Files

### Monthly File (crsp.msf)

**Frequency**: Monthly
**Coverage**: ~30K securities (mostly delisted)
**Data points**: ~5M monthly observations

#### Core Variables

| Variable | Definition | Notes |
|----------|-----------|-------|
| `permno` | CRSP Permanent Company ID | Unique to company |
| `permco` | CRSP Permanent Company ID (older) | Same as permno in modern CRSP |
| `date` | Calendar month-end date | YYYYMMDD |
| `ret` | Total return including dividends | -1 = delisting, NaN = no trading |
| `retx` | Return excluding dividends | For momentum analysis |
| `prc` | Closing price | Negative = bid/ask average |
| `bid` | Bid price | Rare; usually reconstructed |
| `ask` | Ask price | Rare; usually reconstructed |
| `shrout` | Shares outstanding | Thousands |
| `vol` | Trading volume | 100s of shares (some exchanges omit) |
| `dlret` | Delisting return | See CRSP delisting file |
| `dlstcd` | Delisting code | See reference table below |

#### Delisting Codes

```
500 = Liquidation
520 = Bankruptcy
540 = Called
560 = Still trading (dropped from exchange)
580 = Merger/Consolidation
581 = Spinoff
582 = Acquisition
583 = Reorganization (Chapter 11)
584 = Merger (tender offer)
586 = Recapitalization (name change, etc.)
590 = Reorganization (other)
591 = Emergence from bankruptcy
592 = Exchange offer
```

#### Data Quality Flags

- `prc < 0`: Bid/ask average (still valid price)
- `ret = NaN`: No trading that month
- `dlret = NaN`: No delisting return (ongoing trading)
- `shrout = 0`: Data not available

### Daily File (crsp.dsf)

**Frequency**: Daily (trading days only)
**Coverage**: Same as monthly
**Data points**: ~80M daily observations

**Additional variables** (vs. monthly):
- More granular `vol`
- `bid`, `ask` (when available)
- Better for event studies

**Query Pattern**:
```sql
SELECT permno, date, ret, prc, shrout, vol
FROM crsp.dsf
WHERE date >= '2020-01-01'
  AND date <= '2023-12-31'
ORDER BY permno, date
```

---

## Compustat vs. CRSP: Timing and Coverage

### Data Availability Timeline

```
Event: Company reports Q4 earnings (Dec 31)
│
├─ Datadate: 2023-12-31 (fiscal period end)
├─ Compustat receives filing: 2024-01-31 (30-45 days)
├─ CRSP timestamp: Pre-existing (monthly to date)
├─ rdq: ~2024-02-15 (earnings announcement)
└─ Both datasets complete: ~2024-02-28

Implication: Must lag fundamentals 1-2 months to match public data!
```

### Matching Strategy: Quarterly CRSP-Compustat

```
Step 1: Convert CRSP monthly to quarterly
  → Take price on last trading day of each quarter (Q-end)

Step 2: Get Compustat quarterly data
  → Use datacqtr (calendar quarter)

Step 3: Lag fundamentals by 1-2 months
  → Use price as of quarter-end + 60 days
  → This ensures market knew the fundamentals

Step 4: Merge on gvkey + quarterly date
```

**Python Implementation**:
```python
# CRSP monthly data
crsp_q = crsp_monthly.copy()
crsp_q['quarter_end'] = pd.PeriodIndex(crsp_q['date'], freq='Q').to_timestamp() + pd.DateOffset(months=3) - pd.DateOffset(days=1)

# Take last price each quarter
crsp_q = crsp_q.sort_values('date').groupby(
    ['permno', crsp_q['quarter_end']]
).tail(1).reset_index(drop=True)

# Lag fundamentals: use price 60-120 days after quarter end
crsp_q['match_date'] = crsp_q['quarter_end'] + pd.DateOffset(days=60)

# Compustat quarterly
comp_q['datacqtr_dt'] = pd.to_datetime(
    comp_q['datacqtr'].str.replace('Q', '') + '-01',
    format='%Y%m-%d'
) + pd.DateOffset(months=3) - pd.DateOffset(days=1)

# Merge: Allow 0-120 days lag
merged = crsp_q.merge(
    comp_q,
    on='gvkey',
    suffixes=('_crsp', '_comp')
)

# Filter valid lags: fundamentals announced before market reaction
merged = merged[
    (merged['comp_q'] >= merged['crsp_q']) &
    (merged['comp_q'] <= merged['crsp_q'] + pd.DateOffset(days=120))
]
```

### Coverage Comparison

| Metric | Compustat | CRSP |
|--------|-----------|------|
| **Start date** | 1950 | 1925 |
| **US Coverage** | ~7K firms | ~30K securities |
| **International** | Yes (Worldscope) | No (US only) |
| **Delisted firms** | Historical only | Full history |
| **Data frequency** | Annual, Quarterly | Daily, Monthly |
| **Financial statements** | Full balance sheet | No |
| **Stock returns** | Fiscal-period only | Continuous |

---

## Database Selection Guide

### Use Compustat When:
- You need financial statement data (balance sheet, income statement, cash flow)
- You analyze firm fundamentals (leverage, profitability, asset size)
- You need accounting identifiers (GVKEY, CUSIP)
- You do annual or quarterly analyses
- You need SEC filing data (CIK link)

### Use CRSP When:
- You need stock prices and returns
- You analyze risk or market-based metrics
- You need daily/monthly frequency
- You include delisted firms (survivorship bias concern)
- You do event studies with precise timing

### Use Both (Linked) When:
- Standard finance empirical work (fundamentals + stock returns)
- You build risk-adjusted return metrics
- You analyze earnings surprises (link rdq to CRSP returns)
- You track delisting returns (CRSP + comp.fundq)

---

## Common Variable Construction

### Market Capitalization (Annual)
```
MCAP = Price (FYE) × Shares Outstanding
     = prcc_f × csho
```

### Tobin's Q (Annual)
```
Q = (Market Value Equity + Total Debt - Cash) / Total Assets
  = (prcc_f × csho + dltt + dlc - che) / at
```

### Book-to-Market (Annual)
```
BTM = Book Equity / Market Value Equity
    = seq / (prcc_f × csho)

# Exclude negative book equity
btm[seq <= 0] = NaN
```

### Return on Assets (Annual)
```
ROA = Net Income / Total Assets
    = ni / at

# Better: Lagged denominator
ROA = ni / L.at  # L. = lagged values
```

### Debt-to-Assets (Annual)
```
Leverage = (Long-term Debt + Current Debt) / Total Assets
         = (dltt + dlc) / at
```

---

## Data Quality Checks

### Compustat
```python
# Check for duplicates
dupes = df.groupby(['gvkey', 'datadate']).size()
assert (dupes == 1).all(), "Duplicate gvkey-datadate combinations"

# Check for missing key variables
missing = df[['at', 'revt', 'ni']].isna().sum()
print(f"Missing assets: {missing['at']}")

# Check data plausibility
assert (df['at'] > 0).all(), "Negative or zero assets"
assert (df['at'] >= df['lt']).all(), "Assets < Liabilities"
assert (df['lt'] >= df['dltt']).all(), "Liabilities < Debt"
```

### CRSP
```python
# Check for duplicates
dupes = df.groupby(['permno', 'date']).size()
assert (dupes == 1).all(), "Duplicate permno-date"

# Check price plausibility
assert (abs(df['prc']) > 0).all(), "Zero prices"

# Check return bounds
assert (-2 <= df['ret'] <= 2).all(), "Extreme returns"

# Check volume consistency
vol_by_exchange = df.groupby('exchg')['vol'].describe()
print(vol_by_exchange)
```

---

## References

- **WRDS Compustat Documentation**: https://wrds-www.wharton.upenn.edu/pages/support/
- **WRDS CRSP Manual**: https://wrds-www.wharton.upenn.edu/pages/support/data-overview/stock-market-data/crsp/
- **CRSP Data**: https://www.crsp.org/
- **Compustat Data**: https://www.spglobal.com/marketintelligence/en/solutions/compustat
- **Academic Use**: Ensure WRDS subscription & compliance with data licensing
