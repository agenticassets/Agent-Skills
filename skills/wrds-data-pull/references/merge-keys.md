# Merge Keys and Linking Tables Reference

Cross-database identifier matching: CUSIP, GVKEY, PERMNO, CIK, ISIN linking strategies.

## Table of Contents
- Fundamental Linking Tables
- Many-to-Many Relationship Handling
- Date-Range Matching Logic
- Fuzzy Matching and Exceptions
- Practical Merge Examples

---

## Fundamental Linking Tables

### 1. CUSIP-GVKEY Link (comp.ccmxpf_linkhist)

**Purpose**: Maps CRSP securities (CUSIP) to Compustat companies (GVKEY).

**Key Variables**:
- `cusip`: CRSP 8-digit CUSIP
- `gvkey`: Compustat Global Company Key
- `linkdt`: Link effective date (YYYYMMDD)
- `linkenddt`: Link end date (YYYYMMDD, 99991231 = active)
- `linkprim`: Primary link flag ('C'=primary, others=secondary)
- `liid`: Link issue identifier (distinguishes multiple concurrent links)
- `linktype`: Type of link (LC, LU, LD, etc.)

**Critical Rule**: **Always match on date overlap**.

```sql
-- Correct: Date-aware merge
SELECT c.gvkey, c.datadate, m.permno, m.date
FROM comp.fundq c
INNER JOIN ccmxpf_linkhist l
  ON c.cusip = l.cusip
  AND l.linkdt <= c.datadate
  AND (l.linkenddt >= c.datadate OR l.linkenddt = 99991231)
INNER JOIN crsp.msf m
  ON l.cusip = m.cusip
  AND m.date >= c.datadate
  AND m.date < DATE_ADD(c.datadate, INTERVAL 4 MONTH)
WHERE c.gvkey IN ('000001', '000002')
```

**Many-to-Many Issues**:
1. **One CUSIP → Multiple GVKEYs**:
   - Spinoffs, M&A activity, or historical restatements
   - Use `linkenddt` to identify period of validity
   - Filter on `linkprim = 'C'` for primary link

2. **One GVKEY → Multiple CUSIPs**:
   - Share class changes (common/preferred)
   - Use most recent CUSIP or apply `linkprim` filter
   - Check `liid` to distinguish concurrent classes

**Example: Spinoff Handling**:
```python
# Company XYZ spins off ABC on 2020-06-15
# cusip AAA has gvkey = 123456 until 2020-06-15
#        then gvkey = 789012 from 2020-06-15 onward

# Solution: Always use linkdt/linkenddt in merge condition
df_linked = df_crsp.merge(
    df_link[(df_link['linkdt'] <= df_crsp['date']) &
            ((df_link['linkenddt'] >= df_crsp['date']) |
             (df_link['linkenddt'] == 99991231))],
    on='cusip'
)
```

---

### 2. PERMNO-GVKEY Link (via CUSIP)

**Issue**: CRSP uses PERMNO (permanent ID), Compustat uses GVKEY. No direct table.

**Solution**: Chain through CUSIP.

```sql
-- CRSP daily → CUSIP → GVKEY → Compustat
SELECT
    c.date, c.permno,
    l.cusip,
    cc.gvkey, cc.datadate, cc.at
FROM crsp.dsf c
INNER JOIN (
    -- Get CUSIP for each PERMNO-DATE
    SELECT DISTINCT permno, cusip, ncusip, date
    FROM crsp.mclink
    WHERE linktype IN ('LC', 'LU')  -- Excludes delistings
) m ON c.permno = m.permno
       AND c.date >= m.linkdt
       AND c.date <= m.linkenddt
INNER JOIN ccmxpf_linkhist cc
    ON m.cusip = cc.cusip
    AND cc.linkdt <= c.date
    AND (cc.linkenddt >= c.date OR cc.linkenddt = 99991231)
INNER JOIN comp.fundq cc
    ON cc.gvkey = cc.gvkey
```

**Gotcha**: `crsp.mclink` (PERMNO-CUSIP link) has its own `linkdt/linkenddt`. Match both!

---

### 3. CIK Link (comp.security / comp.ccmxpf_lnkhist)

**Purpose**: Maps Compustat GVKEY to SEC CIK (Central Index Key).

**Key Variables**:
- `gvkey`: Compustat identifier
- `cik`: SEC CIK (0-padded, 10 digits)
- `cik_check_digit`: Validation digit

**Query Pattern**:
```sql
-- Compustat to SEC EDGAR
SELECT g.gvkey, g.conm, c.cik
FROM comp.company g
LEFT JOIN comp.security c ON g.gvkey = c.gvkey
WHERE g.gvkey = '000001'
```

**Use Case**: Accessing SEC EDGAR metadata, DEF 14A proxy filings, 10-K/10-Q timestamps.

---

### 4. ISIN Mapping (comp.g_isin / crsp.mse)

**ISIN** (International Securities Identification Number) links across international exchanges.

**Structure**:
- 2-digit country code + 9-digit CUSIP-like identifier + 1 check digit
- Example: US0378331005 = Apple Inc. in the US market

**Matching Logic**:
```python
# ISIN → CUSIP (remove country code + check digit)
def isin_to_cusip(isin):
    return isin[2:10]  # Strip country prefix and check digit

# However, not all ISINs are CUSIP-convertible
# Use direct ISIN match when available
```

---

## Date-Range Matching Logic

### Quarterly Alignment Problem

**Issue**: CRSP is daily/monthly, Compustat is quarterly.

**Solution 1: Map to Quarter End**
```python
import pandas as pd

# Get quarter end from fiscal date
df['fiscal_qtr'] = pd.PeriodIndex(df['datadate'], freq='Q').to_timestamp() + pd.DateOffset(months=3) - pd.DateOffset(days=1)

# Match CRSP to nearest quarter end (or 4 months after fiscal date)
df['match_date'] = df['datadate'] + pd.DateOffset(months=4)
```

**Solution 2: Merge Within Window**
```sql
-- CRSP to Compustat: Allow 0-120 day lag
SELECT c.*, cmp.*
FROM crsp.msf c
INNER JOIN comp.fundq cmp
    ON c.permno = cmp.permno_link
    AND cmp.datadate <= c.date
    AND cmp.datadate > DATE_ADD(c.date, INTERVAL -120 DAY)
```

### Earnings Announcement Timing

**Key Variables**:
- `datadate`: Fiscal period end (Compustat)
- `rdq`: Report/announcement date (when data became public)
- `rcdate`: Receipt date (SEC filing date)

**Best Practice**: Use `rdq` for event studies
```python
# Event window: use rdq, not datadate
df['event_date'] = df['rdq']
df['post_event'] = df['date'] >= df['event_date']
```

---

## Fuzzy Matching and Exceptions

### 1. Handling Missing CUSIP

~5-10% of CRSP records have no valid CUSIP (mainly delisted firms).

**Workaround**: Use PERMNO-GVKEY historical records
```python
# Check crsp.mse for PERMNO-CUSIP link
# If CUSIP is missing, use permno directly to match historical link records

df_nolnk = df_crsp[df_crsp['cusip'].isna()]
print(f"Missing CUSIP: {len(df_nolnk)} records ({100*len(df_nolnk)/len(df_crsp):.1f}%)")

# Document in output (part of standard QA)
```

### 2. Ticker Symbol Matching (Unreliable)

**DO NOT use ticker as primary key**:
- Multiple companies can have same ticker (after delisting)
- Tickers change, but CUSIP/PERMNO/GVKEY are stable
- Use tickers only for human-readable labels

```python
# OK: Add ticker for reference
df['ticker_label'] = df.merge(comp.security[['gvkey', 'tic']], on='gvkey')['tic']

# NOT OK: Merge on ticker
# df = df.merge(other_df, on='ticker')  # WRONG!
```

### 3. Company Name Matching (String Fuzzy Match)

**When**: Company information is inconsistent across sources.

**Tool**: `difflib` (Python stdlib) or Levenshtein distance

```python
from difflib import SequenceMatcher

def name_match_score(name1, name2):
    # Normalize: uppercase, strip punctuation
    s1 = name1.upper().replace('.', '').replace(',', '').strip()
    s2 = name2.upper().replace('.', '').replace(',', '').strip()
    return SequenceMatcher(None, s1, s2).ratio()

# Match with threshold
if name_match_score(comp_name, crsp_name) > 0.85:
    merge_confirmed = True
```

**Better**: Use Winkler distance (handles typos better)
```bash
pip install fuzzywuzzy python-Levenshtein
```

```python
from fuzzywuzzy import fuzz

score = fuzz.token_set_ratio(comp_name, crsp_name)
# token_set_ratio handles word order and extra words better
```

---

## Practical Merge Examples

### Example 1: Quarterly CRSP-Compustat Panel

```python
import pandas as pd
from datetime import datetime

# 1. Load data
crsp_monthly = pd.read_csv('crsp_monthly.csv', parse_dates=['date'])
compustat = pd.read_csv('compustat_q.csv', parse_dates=['datadate'])
link = pd.read_csv('ccmxpf_linkhist.csv')

# 2. Filter link table for valid periods
link['linkdt'] = pd.to_datetime(link['linkdt'], format='%Y%m%d')
link['linkenddt'] = pd.to_datetime(link['linkenddt'], format='%Y%m%d')

# Replace 99991231 with future date
link.loc[link['linkenddt'].str.startswith('9999'), 'linkenddt'] = pd.Timestamp('2099-12-31')

# 3. Merge CRSP to link (on CUSIP + date overlap)
crsp_month['date_key'] = crsp_month['date']  # For merge condition
crsp_linked = crsp_month.merge(
    link[['cusip', 'gvkey', 'linkdt', 'linkenddt', 'linkprim']],
    on='cusip'
)

# Keep only date-valid matches
crsp_linked = crsp_linked[
    (crsp_linked['linkdt'] <= crsp_linked['date_key']) &
    (crsp_linked['linkenddt'] >= crsp_linked['date_key'])
]

# Keep only primary links (optional, but recommended)
crsp_linked = crsp_linked[crsp_linked['linkprim'] == 'C']

# 4. Convert CRSP monthly to quarterly (last day of quarter)
crsp_linked['year'] = crsp_linked['date'].dt.year
crsp_linked['quarter'] = crsp_linked['date'].dt.quarter
crsp_linked['quarter_end'] = (
    pd.PeriodIndex(crsp_linked['date'], freq='Q').to_timestamp() +
    pd.DateOffset(months=3) - pd.DateOffset(days=1)
)

# Take last row per permno per quarter
crsp_quarterly = crsp_linked.sort_values('date').groupby(
    ['permno', 'year', 'quarter']
).tail(1).reset_index(drop=True)

# 5. Merge to Compustat quarterly
compustat['datacqtr'] = compustat['datadate'].dt.to_period('Q').astype(str)
crsp_quarterly['datacqtr'] = (
    pd.PeriodIndex(crsp_quarterly['quarter_end'], freq='Q').astype(str)
)

# Merge on gvkey + datacqtr
panel = crsp_quarterly.merge(
    compustat[['gvkey', 'datacqtr', 'at', 'ni', 'datadate']],
    on=['gvkey', 'datacqtr'],
    how='inner'
)

print(f"Panel shape: {panel.shape}")
print(f"Unique firms: {panel['gvkey'].nunique()}")
print(f"Time periods: {panel['datacqtr'].nunique()}")
```

### Example 2: Handling Delisting (Survivorship Bias Fix)

```python
# Load delisting info
delist = pd.read_csv('crsp_delist.csv', parse_dates=['dlstdt'])

# Merge delisting returns into panel
panel_with_delist = panel.merge(
    delist[['permno', 'dlstdt', 'dlret', 'dlstcd']],
    on='permno',
    how='left'
)

# Use delisting return for final month of trading
panel_with_delist['ret_final'] = panel_with_delist['ret'].copy()
is_delist = panel_with_delist['date'] == panel_with_delist['dlstdt']
panel_with_delist.loc[is_delist, 'ret_final'] = panel_with_delist.loc[is_delist, 'dlret']

# Flag delisting category
delist_cats = {
    500: 'Liquidation',
    520: 'Bankruptcy',
    580: 'Acquisition',
    581: 'Spinoff',
    582: 'M&A',
    584: 'Merger',
    586: 'Recapitalization',
    590: 'Reorganization',
    591: 'Emergence from bankruptcy'
}
panel_with_delist['delist_type'] = panel_with_delist['dlstcd'].map(delist_cats)
panel_with_delist['is_delist'] = panel_with_delist['dlstcd'].notna()

print(f"Delisted firms: {panel_with_delist['is_delist'].sum()} observations")
print(panel_with_delist[panel_with_delist['is_delist']]['delist_type'].value_counts())
```

---

## References

- **WRDS CCM Linking**: https://wrds-www.wharton.upenn.edu/pages/support/support-articles/crsp/linking-crsp-and-compustat-data/
- **Wharton Research Data Services**: https://wrds-www.wharton.upenn.edu/
- **CRSP Linking Logic**: https://www.crsp.org/
- **Shumway (1997)**: "The Delisting Bias in CRSP Data" (*JF*)
- **Johnson & Zhao (2007)**: "The Long-Run Performance of Acquisitions and Delisting Effects" (*JFE*)
