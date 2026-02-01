# Alternative Data Reference

RavenPack sentiment, SEC EDGAR metadata, patent data, and web/traffic signals for research.

## Table of Contents
- RavenPack ESG & Sentiment Data
- SEC EDGAR Metadata & Filing Analytics
- Patent Data (USPTO, Google Patents, NBER)
- Web Traffic & Sentiment Alternatives
- Practical Merge Examples

---

## RavenPack ESG & Sentiment Data

**Provider**: RavenPack (news analytics platform)
**Coverage**: ~50K firms globally, ~70K securities
**Frequency**: Real-time (daily aggregates available)
**Data Types**: News sentiment, ESG scores, event detection

### News Sentiment (wrds.ravenpack_sentiment)

| Variable | Definition | Notes |
|----------|-----------|-------|
| `ticker` | Stock ticker | Subject to change; use CUSIP for linking |
| `cusip` | CUSIP identifier | More stable than ticker |
| `event_date` | Date of news event | YYYYMMDD |
| `num_stories` | Number of news stories | Attention measure |
| `sentiment_score` | News sentiment (-100 to +100) | -100 = negative, +100 = positive |
| `sentiment_relevance` | Relevance to firm (0-1) | Filters noise |
| `news_source` | Source categorization | 'Wire', 'Press Release', 'Blog', etc. |
| `event_type` | Category | 'M&A', 'Earnings', 'Litigation', etc. |

### ESG Scores (wrds.ravenpack_esg)

| Variable | Definition | Range | Notes |
|----------|-----------|-------|-------|
| `environmental_score` | Environmental performance | 0-100 | Higher = better |
| `social_score` | Social performance | 0-100 | Labor, community, diversity |
| `governance_score` | Governance performance | 0-100 | Board, compensation, shareholder rights |
| `overall_esg` | Weighted ESG score | 0-100 | Composite |
| `esg_percentile` | Percentile vs. peers | 0-100 | Industry-adjusted |

### Query Pattern (Sentiment)

```sql
SELECT ticker, cusip, event_date, num_stories, sentiment_score, event_type
FROM wrds.ravenpack_sentiment
WHERE event_date >= '2020-01-01'
  AND event_date <= '2023-12-31'
  AND sentiment_relevance > 0.5  -- Filter noise
  AND num_stories >= 2  -- Minimum coverage
ORDER BY cusip, event_date
```

### Data Quality Considerations

1. **Sentiment Bias**: RavenPack algorithms bias toward business news (underweights social media)
   ```python
   # Check for source concentration
   df_rp['source_concentration'] = df_rp.groupby('cusip')['news_source'].apply(
       lambda x: x.value_counts().iloc[0] / len(x)
   )
   print(f"High source concentration: {(df_rp['source_concentration'] > 0.5).mean():.1%}")
   ```

2. **Look-Ahead Bias**: Event date vs. publication date can differ
   ```python
   # Use publication date for event studies (not event_date)
   df_rp['event_date_actual'] = df_rp['publication_date']  # If available
   ```

3. **Survivorship in Sentiment**: Firms with low coverage may have missing sentiment
   ```python
   # Flag low-coverage periods
   df_rp['coverage_flag'] = df_rp['num_stories'].fillna(0) > 0

   low_coverage = df_rp[~df_rp['coverage_flag']].groupby('cusip').size()
   print(f"Low coverage firms: {len(low_coverage[low_coverage > 100])}")
   ```

### Merge to Stock Returns

```python
# Event study: Sentiment → Return predictability
df_sent = pd.read_sql("""
    SELECT cusip, event_date, sentiment_score, num_stories
    FROM wrds.ravenpack_sentiment
    WHERE event_date >= '2020-01-01'
""", conn)

# Get CRSP returns
df_crsp = pd.read_sql("""
    SELECT permno, date, ret, prc
    FROM crsp.dsf
    WHERE date >= '2020-01-01'
""", conn)

# Link via CUSIP
df_crsp['cusip'] = ...  # From crsp.mse

# Merge sentiment to returns (next 5 days)
df_event = df_sent.merge(df_crsp, on='cusip', how='inner')
df_event = df_event[
    (df_event['date'] > df_event['event_date']) &
    (df_event['date'] <= df_event['event_date'] + pd.DateOffset(days=5))
]

# Aggregate returns by event
event_returns = df_event.groupby('event_date')['ret'].agg(['mean', 'count'])
```

---

## SEC EDGAR Metadata & Filing Analytics

**Provider**: SEC (public access via EDGAR system)
**Coverage**: All US public companies
**Frequency**: Real-time (filings as submitted)
**Data Lag**: 1-4 days after filing

### Key Filing Types

| Form | Meaning | Frequency | Lag |
|------|---------|-----------|-----|
| **10-K** | Annual report | Annual | 60-90 days |
| **10-Q** | Quarterly report | 3x/year | 40-50 days |
| **8-K** | Material event | Ad-hoc | 1-4 days |
| **DEF 14A** | Proxy statement | Annual | 30-60 days |
| **4** | Insider trades | Ad-hoc | 1-2 days |
| **S-1** | IPO registration | IPO | 1 month+ |

### EDGAR Metadata (wrds.sec_filings)

| Variable | Definition | Notes |
|----------|-----------|-------|
| `cik` | SEC Central Index Key | Primary key |
| `form_type` | Filing form type | '10-K', '10-Q', '8-K', etc. |
| `filing_date` | Date filed with SEC | YYYYMMDD |
| `report_date` | Fiscal period end | YYYYMMDD |
| `accession_number` | Unique filing ID | For EDGAR retrieval |
| `file_size` | Filing size in bytes | Complexity indicator |
| `filing_url` | Link to full filing | SEC EDGAR |

### Query Pattern (10-K Filings)

```sql
SELECT cik, filing_date, report_date, accession_number, file_size
FROM wrds.sec_filings
WHERE form_type = '10-K'
  AND report_date >= '2015-01-01'
  AND report_date <= '2023-12-31'
ORDER BY cik, report_date DESC
```

### Text Analysis on EDGAR

**Common metrics**:
- **MD&A Length**: Proxy for disclosure quality or litigation risk
- **Risk Factor Count**: Forward-looking risk disclosure
- **Tone/Sentiment**: Readability, optimism bias

```python
# Example: Calculate MD&A length by firm
df_filings['mda_wordcount'] = df_filings['mda_text'].str.split().str.len()

# Risk factors
df_filings['risk_factor_count'] = df_filings['risk_section'].str.count('risk')

# Merge to returns
df_analysis = df_filings.merge(
    df_crsp,
    on='cik',
    suffixes=('_filing', '_crsp')
)

# Regression: Does MD&A length predict post-filing returns?
from statsmodels.api import OLS, add_constant

model = OLS(
    df_analysis['post_filing_return'],
    add_constant(df_analysis[['mda_wordcount', 'risk_factor_count']])
).fit()
print(model.summary())
```

### Linking 10-K/10-Q to Compustat

```python
# 10-K report date ≈ Compustat datadate
df_10k['report_year'] = df_10k['report_date'].dt.year
df_10k['report_qtr'] = df_10k['report_date'].dt.quarter

# Compustat fiscal year-end
df_comp['fiscal_year'] = df_comp['datadate'].dt.year

# Merge on CIK (SEC) to GVKEY (Compustat)
df_10k = df_10k.merge(
    ccm_link[['cik', 'gvkey']],
    on='cik',
    how='left'
)

df_merged = df_10k.merge(
    df_comp[['gvkey', 'fiscal_year', 'at', 'revt']],
    on=['gvkey', 'fiscal_year'],
    how='left'
)

print(f"10-K to Compustat match rate: {df_merged['at'].notna().mean():.1%}")
```

---

## Patent Data

### USPTO/Google Patents

**Provider**: USPTO (direct) or Google Patents (interface)
**Coverage**: ~12M utility patents (US), back to 1976
**Frequency**: Quarterly (with lag)
**Key Data**: Patent counts, citations, technology class

### Patent Database Schema (wrds.patent_data)

| Variable | Definition | Notes |
|----------|-----------|-------|
| `patent_id` | Patent number | Unique identifier |
| `assignee_name` | Company that owns patent | Corporate name |
| `assignee_cik` | SEC CIK of assignee | Links to public companies |
| `filing_date` | Application date | Original priority date |
| `grant_date` | Patent grant date | YYYYMMDD |
| `tech_field` | Technology classification | IPC, CPC, IPC codes |
| `num_claims` | Number of patent claims | Patent scope proxy |
| `num_citations` | Citations to prior patents | Quality/importance indicator |
| `cited_by_count` | Number of follow-on citations | Impact/influence |

### Linking to Companies

```python
# Patents → CIK → CRSP/Compustat
df_patents = pd.read_sql("""
    SELECT assignee_name, assignee_cik, grant_date, tech_field, cited_by_count
    FROM wrds.patent_data
    WHERE grant_date >= '2010-01-01'
""", conn)

# Match to Compustat via CIK
ccm = pd.read_sql("""
    SELECT gvkey, cik, conm
    FROM comp.company
""", conn)

df_patents = df_patents.merge(ccm, left_on='assignee_cik', right_on='cik', how='left')

# Count patents per firm per year
df_patents['patent_year'] = df_patents['grant_date'].dt.year
patent_counts = df_patents.groupby(['gvkey', 'patent_year']).size().reset_index(name='patent_count')

# Merge to Compustat fundamentals
df_comp_patents = df_comp.merge(
    patent_counts,
    on=['gvkey', 'patent_year'],
    how='left'
)
df_comp_patents['patent_count'] = df_comp_patents['patent_count'].fillna(0)
```

### NBER Patent Database

**Advantage**: Pre-matched to Compustat companies
**Source**: https://sites.google.com/site/patentdataproject/

```python
# Load NBER patent data (usually as CSV)
df_nber_patent = pd.read_csv('nber_patent_assignee.csv')

# Columns: patent_id, assignee_id, assignee_name_orig, assignee_name_stripped, gvkey

# Immediate match to Compustat
df_analysis = df_nber_patent.merge(
    df_comp,
    on='gvkey',
    how='inner'
)

# Example: Patent productivity
df_analysis['patents_per_rd'] = df_analysis['patent_count'] / df_analysis['xrd']
```

---

## Web Traffic & Sentiment Alternatives

### Google Trends (Public)

**Coverage**: Aggregate search volumes (no individual data)
**Frequency**: Weekly
**Limitation**: Relative scores (0-100), not absolute searches

```python
# Example: Retrieve Google Trends manually (or via pytrends library)
from pytrends.request import TrendReq

gt = TrendReq(hl='en-US', tz=360)

# Search volume for ticker
gt.build_payload(['AAPL', 'MSFT'], timeframe='2023-01-01 2023-12-31')
df_trends = gt.interest_over_time()

# Merge to stock returns
df_trends['date'] = df_trends.index
df_merged = df_crsp.merge(df_trends[['date', 'AAPL']], on='date', how='left')
```

### News Sources (Alternative to RavenPack)

**Free**: NewsAPI (newsapi.org), GDELT (Global Database of Events, Language & Tone)
**Paid**: Bloomberg, Refinitiv, S&P Capital IQ

```python
# GDELT example: Global event detection
# Daily downloads: http://data.gdeltproject.org/gdeltv2/masterfilelist.txt

df_gdelt = pd.read_csv('gdelt_event_data.csv')
# Columns: event_id, event_date, actor1, actor2, goldstein_scale, etc.

# Filter for financial events
fin_events = df_gdelt[df_gdelt['goldstein_scale'] > 5]  # High impact events

# Cross-reference actors to company names
fin_events['company_mention'] = fin_events['actor1'].str.contains('COMPANY_NAME', case=False)
```

---

## Practical Merge: Multi-Signal Analysis

**Objective**: Predict stock returns using alternative data signals.

```python
import pandas as pd
import numpy as np

# 1. Load signals
df_sentiment = pd.read_sql("""
    SELECT cusip, event_date, sentiment_score
    FROM wrds.ravenpack_sentiment
    WHERE event_date >= '2021-01-01'
""", conn)

df_patents = pd.read_sql("""
    SELECT gvkey, datadate, patent_count
    FROM patent_annual_summary
    WHERE datadate >= '2021-01-01'
""", conn)

df_edgar = pd.read_sql("""
    SELECT cik, filing_date, mda_wordcount
    FROM sec_filing_text_metrics
    WHERE filing_date >= '2021-01-01'
""", conn)

df_crsp = pd.read_sql("""
    SELECT permno, date, ret, prc, shrout
    FROM crsp.msf
    WHERE date >= '2021-01-01'
""", conn)

# 2. Get linking tables
ccm = pd.read_sql("""
    SELECT cusip, gvkey, cik
    FROM ccm_linking
""", conn)

# 3. Merge all signals
df_all = df_crsp.copy()

# Sentiment: Daily to monthly
df_sentiment_m = df_sentiment.copy()
df_sentiment_m['month'] = df_sentiment_m['event_date'].dt.to_period('M')
df_sentiment_agg = df_sentiment_m.groupby(['cusip', 'month'])['sentiment_score'].mean().reset_index()
df_sentiment_agg['date'] = df_sentiment_agg['month'].dt.to_timestamp() + pd.DateOffset(months=1) - pd.DateOffset(days=1)

# Patents: Annual to monthly (forward-fill)
df_patents['month'] = df_patents['datadate'].dt.to_period('M')
df_patents_m = df_patents.groupby(['gvkey', 'month'])['patent_count'].sum().reset_index()
df_patents_m['date'] = df_patents_m['month'].dt.to_timestamp() + pd.DateOffset(months=1) - pd.DateOffset(days=1)

# EDGAR: Link via CIK, aggregate to quarterly
df_edgar_q = df_edgar.copy()
df_edgar_q['quarter'] = df_edgar_q['filing_date'].dt.to_period('Q')
df_edgar_agg = df_edgar_q.groupby(['cik', 'quarter']).agg({
    'mda_wordcount': 'mean'
}).reset_index()
df_edgar_agg['date'] = df_edgar_agg['quarter'].dt.to_timestamp() + pd.DateOffset(months=3) - pd.DateOffset(days=1)

# 4. Merge to CRSP
# CRSP → Sentiment (via CUSIP)
df_all = df_all.merge(
    df_sentiment_agg[['cusip', 'date', 'sentiment_score']],
    on=['cusip', 'date'],
    how='left'
)

# CRSP → Patents (via GVKEY via CCM)
df_all = df_all.merge(
    ccm, on='cusip', how='left'
)
df_all = df_all.merge(
    df_patents_m[['gvkey', 'date', 'patent_count']],
    on=['gvkey', 'date'],
    how='left'
)

# CRSP → EDGAR (via CIK via CCM)
df_all = df_all.merge(
    df_edgar_agg[['cik', 'date', 'mda_wordcount']],
    on=['cik', 'date'],
    how='left'
)

# 5. Panel structure
print(f"Sample: {df_all.shape[0]} permno-months")
print(f"Signal coverage:")
print(f"  Sentiment: {df_all['sentiment_score'].notna().mean():.1%}")
print(f"  Patents: {df_all['patent_count'].notna().mean():.1%}")
print(f"  EDGAR: {df_all['mda_wordcount'].notna().mean():.1%}")

# 6. Predictability analysis
from statsmodels.formula.api import ols

# Forward-looking return
df_all['next_month_ret'] = df_all.groupby('permno')['ret'].shift(-1)

# Regression
model = ols(
    'next_month_ret ~ sentiment_score + np.log(patent_count + 1) + np.log(mda_wordcount)',
    data=df_all.dropna()
).fit(cov_type='HC1')

print(model.summary())
```

---

## References

- **RavenPack**: https://www.ravenpack.com/
- **SEC EDGAR**: https://www.sec.gov/cgi-bin/browse-edgar
- **USPTO Patents**: https://www.uspto.gov/patents-application-process/search-patents
- **NBER Patent Database**: https://sites.google.com/site/patentdataproject/
- **Google Trends**: https://trends.google.com/
- **GDELT**: https://www.gdeltproject.org/
- **NewsAPI**: https://newsapi.org/
- **Academic Papers**:
  - Da, Engelberg & Gao (2015): "The Sum of Small Things: A Theory of Marginal Investors" (*JF*)
  - Tetlock (2007): "Giving Content to Investor Sentiment: The Role of Media in Finance" (*JF*)
  - Bena & Hanousek (2012): "What prompts a firm to go public?" (*REStud*)
