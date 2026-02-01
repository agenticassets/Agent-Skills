# Known Data Issues and Workarounds

Database-specific gotchas, restatements, survivorship bias, and adjustments by source.

## Table of Contents
- Compustat Issues
- CRSP Issues
- Linking Table Problems
- Survivorship and Selection Bias
- Restatement Tracking
- Database-Specific Adjustments

---

## Compustat Issues

### 1. Missing Fiscal Year-End Dates

**Problem**: Some companies have inconsistent fiscal year ends (e.g., change from Dec to Sep).

**Impact**: Creates gaps or duplicates in time series.

**Detection**:
```python
# Check for multiple observations same calendar year
df_dup = df.groupby(['gvkey', df['datadate'].dt.year]).size()
df_dup[df_dup > 1]
```

**Solution**:
```python
# Sort by datadate and take last observation per gvkey-year
df_annual = df.sort_values('datadate').groupby(
    ['gvkey', df['datadate'].dt.year]
).tail(1)
```

### 2. Data Revisions and Restatements

**Issue**: Historical Compustat data is updated retroactively (restated earnings, asset revaluations, etc.).

**Your data pull date matters**:
- Same pull date → Reproducible results
- Different pull date → Historical values change (can be substantial)

**Solution**: Document pull date in metadata
```python
import datetime
PULL_DATE = datetime.datetime(2024, 1, 15)

# Tag all data with pull date
df['data_pull_date'] = PULL_DATE

# Save to filename
df.to_csv(f'compustat_q_{PULL_DATE.strftime("%Y%m%d")}.csv')
```

**Academic Citation**: Always cite Compustat data with vintage/pull date.

### 3. Stock Split Adjustments

**Issue**: Compustat prices in `prccq` and `prcc_f` may be nominal (pre-split) or split-adjusted depending on variable.

**Best Practice**: Use CRSP prices instead (fully adjusted) and link back to Compustat fundamentals.

```python
# DO NOT use prccq directly for analysis
# Instead:
# 1. Get prices from CRSP (already adjusted)
# 2. Link CRSP to Compustat via CUSIP-GVKEY
# 3. Use CRSP prices with Compustat fundamentals
```

### 4. Negative Book Value

**Problem**: Distressed firms (losses > equity) have `seq < 0`.

**Common in**: Financial crisis (2008), industry downturns, bankrupt firms.

**Impact**: Distorts ratios like Tobin's Q, Book-to-Market.

**Solution**:
```python
# Option 1: Flag and exclude
df['valid_book_equity'] = df['seq'] > 0
df.loc[~df['valid_book_equity'], 'book_to_market'] = np.nan

# Option 2: Use lagged values (interpolate)
df['seq_lagged'] = df.groupby('gvkey')['seq'].shift(1)
df['seq_use'] = df['seq'].where(df['seq'] > 0, df['seq_lagged'])

# Document treatment in methods section
print(f"Observations with negative equity: {(df['seq'] < 0).sum()}")
```

### 5. Inactive Companies in comp.company

**Issue**: `comp.company` includes all registered companies, not just active/traded.

**Solution**: Filter to securities that traded
```python
# Use only companies that appear in Compustat fundamentals
active_gvkeys = df_fundq['gvkey'].unique()

df_company = df_company[df_company['gvkey'].isin(active_gvkeys)]
```

### 6. Multiple Fiscal Year Ends (Quarterly Mismatch)

**Problem**: Quarterly data (`comp.fundq`) may have inconsistent quarter numbering.

**Example**: Company switches fiscal year from Dec to Mar → `fqtr` numbering changes.

**Detection**:
```python
# Check fqtr distribution
df.groupby('gvkey')['fqtr'].value_counts().unstack(fill_value=0)
```

**Solution**: Use `datacqtr` (calendar quarter) instead of `fqtr`
```python
# datacqtr = YYYYQ (e.g., 2023Q4)
# More reliable than fqtr (fiscal quarter, which can skip)
```

---

## CRSP Issues

### 1. Negative Stock Prices

**Problem**: CRSP codes negative prices to indicate bid/ask averages.

**Not a data error**. Interpretation:
- Positive price: Closing price
- Negative price: (Ask + Bid) / 2
- Absolute value is always the "price"

**Solution**:
```python
# Always use absolute value for analysis
df['price_abs'] = abs(df['prc'])

# For returns, CRSP already handles this in 'ret' column (no adjustment needed)
```

### 2. Delisting Returns

**Problem**: CRSP's `ret` may be missing for delisting month; actual return may be in `dlret` (delisting table).

**Impact**: Survivorship bias (systematically missing negative returns if not handled).

**Solution**:
```python
# Merge delisting data
df_delist = pd.read_sql("""
    SELECT permno, dlstdt, dlret, dlstcd
    FROM crsp.msedelist
""", connection)

df_merged = df.merge(
    df_delist, on='permno', how='left'
)

# Use delisting return if available
df_merged['ret_final'] = df_merged['ret'].fillna(df_merged['dlret'])

# Flag delisting
df_merged['is_delisted'] = df_merged['dlstcd'].notna()

print(f"Delisted observations: {df_merged['is_delisted'].sum()}")
```

**By Delisting Code**:
```python
delist_reasons = {
    500: 'Liquidation',
    520: 'Bankruptcy',
    580: 'Acquisition',
    581: 'Spinoff',
    584: 'Merger',
    586: 'Recapitalization',
    590: 'Reorganization'
}

# Filter by reason if needed
df_bankruptcy = df_merged[df_merged['dlstcd'] == 520]
```

### 3. Trading Halts and Missing Data

**Problem**: Some stocks have gaps in trading (halts, delistings).

**Detection**:
```python
# Identify gaps in date sequence per PERMNO
df['days_since_last'] = (
    df.groupby('permno')['date'].diff().dt.days
)

gaps = df[df['days_since_last'] > 5]  # >5 days without trading
print(f"Trading gaps detected: {len(gaps)} records")
```

### 4. Share Count Changes

**Problem**: `shrout` (shares outstanding) can change due to:
- Stock splits (typically adjusted by CRSP)
- New issuance / buybacks (real change)
- Data reporting lag

**Best Practice**: Use shares as reported; CRSP adjusts for splits.

```python
# Verify consistency: price × shares = market cap
df['implied_mcap'] = abs(df['prc']) * df['shrout'] * 1000  # shrout in thousands

# Compare to Bloomberg if available
```

### 5. PRC = 0 or Missing

**Problem**: Inactive months or delisted firms may have `prc = NaN` or zero.

**Solution**:
```python
# Remove zero/null prices
df_valid = df[df['prc'].notna() & (df['prc'] != 0)]

# Or keep but mark as invalid for analysis
df['price_valid'] = (df['prc'].notna()) & (df['prc'] != 0)
```

### 6. Dividend Adjustments

**Issue**: `ret` = total return (includes dividends); `retx` = return excluding dividends.

**Confusion point**: Which to use?

**Rule**:
- **Use `ret`** for portfolio performance, buy-and-hold analysis
- **Use `retx`** for price momentum analysis (excluding dividends)
- **Be consistent** and document choice

```python
# Document choice in output
use_ret_type = 'ret'  # 'ret' or 'retx'

df['return'] = df[use_ret_type]

# Output
print(f"Return measure: {use_ret_type} (total return with dividends)")
```

---

## Linking Table Problems

### 1. CUSIP-GVKEY Link Gaps

**Problem**: Not all CRSP securities have a valid link to Compustat.

**Frequency**: ~10-15% of CRSP records unmatched.

**Typical Causes**:
- Small/micro-cap stocks not in Compustat
- Delisted companies post-delisting
- Foreign stocks in CRSP (not in US Compustat)
- New IPOs before data inclusion

**Solution**:
```python
# Check merge coverage
df_merged = crsp.merge(link, on='cusip', how='left', indicator=True)

coverage = (df_merged['_merge'] == 'both').sum() / len(df_merged)
print(f"Link coverage: {coverage:.1%}")

# Track unmatched
unmatched = df_merged[df_merged['_merge'] == 'left_only']
print(f"Unmatched CRSP records: {len(unmatched)}")
```

### 2. Duplicate Links

**Problem**: One CUSIP → Multiple GVKEYs (spinoff, recapitalization).

**Solution**: Use `linkdt` and `linkenddt` to select valid period.

```python
# Correct: Filter on date overlap
valid_links = links[
    (links['linkdt'] <= reference_date) &
    ((links['linkenddt'] >= reference_date) | (links['linkenddt'] == 99991231))
]

# If still multiple, use linkprim='C'
if len(valid_links) > 1:
    valid_links = valid_links[valid_links['linkprim'] == 'C']
```

### 3. Stale Link Dates

**Problem**: Some links are very old (pre-1960s data) or have typos in dates.

**Detection**:
```python
# Check for unrealistic link dates
df_links['linkdt'] = pd.to_datetime(df_links['linkdt'], format='%Y%m%d')
old_links = df_links[df_links['linkdt'] < '1950-01-01']

print(f"Pre-1950 links: {len(old_links)}")
```

---

## Survivorship and Selection Bias

### Survivorship Bias (Returns)

**Problem**: Delisted stocks have lower average returns; if excluded, results are upward-biased.

**Solution**: Always include delisting returns.

```python
# Comprehensive: CRSP daily file + delisting file
df_returns = df_daily[['date', 'permno', 'ret']].copy()

# Merge delisting returns
df_delist = pd.read_sql("""
    SELECT permno, dlstdt, dlret
    FROM crsp.msedelist
    WHERE dlret IS NOT NULL
""", conn)

df_returns = df_returns.merge(
    df_delist.rename(columns={'dlstdt': 'date'}),
    on=['permno', 'date'],
    how='left'
)

# Replace returns with delisting return if available
df_returns['ret_final'] = df_returns['ret'].fillna(df_returns['dlret'])

# Verify: average returns should be ~6-7% annualized, not 8-10%
print(f"Median annual return: {df_returns['ret_final'].mean() * 12:.2%}")
```

**Academic Citation**: Shumway (1997, JF): "The Delisting Bias in CRSP Data"

### Listing Bias (Missing IPOs)

**Problem**: Young firms not yet in database; sample is biased toward established companies.

**Severity**: Moderate (CRSP coverage ~5K stocks; ~1-2K IPOs per year).

**Solution**:
```python
# Document: "Includes firms trading on major US exchanges; IPOs added to CRSP ~6 months post-listing"

# If IPO inclusion is critical:
# Use Ritter's IPO database: https://site.warrington.ufl.edu/ritter/ipos/

# Cross-reference: Merge CRSP with IPO dates
df_ipo = pd.read_csv('ritter_ipos.csv')
df = df.merge(df_ipo[['ticker', 'ipo_date']], on='ticker', how='left')

# Flag pre-listing period
df['post_ipo'] = df['date'] > df['ipo_date']
```

### Small Firm Bias

**Problem**: Compustat skews toward larger firms; small firms underrepresented.

**CRSP coverage by size**:
- Market cap > $2B: ~99% coverage
- Market cap $500M-$2B: ~95% coverage
- Market cap $100M-$500M: ~80% coverage
- Market cap < $100M: ~20% coverage

**Solution**: Check representativeness.

```python
# Compare sample distribution to population
df_crsp['size'] = df_crsp['prc'].abs() * df_crsp['shrout'] * 1000

size_deciles = pd.qcut(df_crsp['size'], q=10, labels=False)
sample_deciles = pd.qcut(df[df['matched'] == True]['size'], q=10, labels=False)

comparison = pd.DataFrame({
    'population': size_deciles.value_counts().sort_index(),
    'sample': sample_deciles.value_counts().sort_index()
})
print(comparison)
```

---

## Restatement Tracking

### Identifying Restated Data

**Problem**: Historical Compustat values change when companies restate earnings.

**Solution**: Track restatement dates.

```sql
-- From Compustat footnote database (if available)
SELECT gvkey, datadate, restatement_date, item, old_value, new_value
FROM comp.footnotes
WHERE restatement_date IS NOT NULL
  AND item IN ('ni', 'revt', 'at')  -- Common restatement items
```

**Alternative**: Compare data pulls across time
```python
# If you have two pulls (e.g., Jan 2023 and Jan 2024)
pull_jan23 = pd.read_csv('compustat_20230115.csv')
pull_jan24 = pd.read_csv('compustat_20240115.csv')

# Compare historical values
restatements = pull_jan24[pull_jan24['gvkey'].isin(pull_jan23['gvkey'].unique())].merge(
    pull_jan23, on=['gvkey', 'datadate'], suffixes=('_new', '_old')
)

# Find differences
restatements['ni_change'] = restatements['ni_new'] - restatements['ni_old']
restatements[restatements['ni_change'] != 0][['gvkey', 'datadate', 'ni_change']].head(20)
```

### SEC Restatement Database

**External Source**: SEC (sec.gov) publishes restatement announcements.

```
https://www.sec.gov/cgi-bin/browse-edgar?
action=getcompany&type=8-K&dateb=&owner=exclude&count=100
# Look for Item 4.02: Non-Reliance (restatement indicator)
```

---

## Database-Specific Adjustments

### CRSP to Compustat Timing

| Scenario | Timing | Solution |
|----------|--------|----------|
| Quarterly earnings announcement | `datadate` → `rdq` (0-90 days later) | Use `rdq` for event studies |
| Match to CRSP monthly | Use month-end price (last day of quarter) | Merge on date ≤ quarter end |
| Lagged fundamentals | Use t-1 fundamentals with t prices | Construct with `.shift(1)` |

### Fiscal vs. Calendar Quarter Alignment

```python
# Problem: Compustat fiscal quarters don't align with calendar

# Solution: Standardize to calendar quarters
df['cal_qtr'] = pd.PeriodIndex(df['datadate'], freq='Q')

# Merge fiscal quarter fundamentals to calendar quarter prices
df['qtr_end'] = df['cal_qtr'].to_timestamp() + pd.DateOffset(months=3) - pd.DateOffset(days=1)
```

---

## References

- **Shumway (1997, JF)**: "The Delisting Bias in CRSP Data"
- **Johnson & Zhao (2007, JFE)**: "Delisting Returns and Survivorship Bias"
- **Jegadeesh & Livnat (2006, JFE)**: "Revenue Surprises and Stock Returns"
- **SEC Restatement Database**: https://www.sec.gov/cgi-bin/browse-edgar
- **WRDS Data Documentation**: https://wrds-www.wharton.upenn.edu/pages/support/
