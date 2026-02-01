# Variable Construction Reference

Standard financial ratios and metrics with formulas and academic citations.

## Table of Contents
- Financial Ratios
- Market-Based Metrics
- REIT-Specific Metrics
- Return Measures
- Size/Value/Momentum Portfolios

## Financial Ratios

### Tobin's Q
**Formula**: (Market Value of Equity + Total Debt - Cash) / Total Assets

```python
market_equity = abs(prcc) * csho  # abs() for negative prices
total_debt = dltt + dlc
tobins_q = (market_equity + total_debt - che) / at
```

**References**:
- Chung & Pruitt (1994, FAJ) - Simplified approximation
- Kaplan & Zingales (1997, QJE) - Investment-cash flow sensitivity

### Leverage

**Book Leverage**: Total Debt / Total Assets

```python
leverage_book = (dltt + dlc) / at
```

**Market Leverage**: Total Debt / Market Equity

```python
leverage_market = (dltt + dlc) / (prcc * csho)
```

**References**:
- Rajan & Zingales (1995, JF) - Cross-country leverage determinants
- Frank & Goyal (2009, JFE) - Capital structure survey

### Return on Assets (ROA)

**Formula**: Net Income / Total Assets

```python
roa = ni / at
```

**Lagged assets** (preferred):

```python
df['roa'] = df['ni'] / df.groupby('gvkey')['at'].shift(1)
```

### Return on Equity (ROE)

**Formula**: Net Income / Book Equity

```python
roe = ni / seq
```

**DuPont Decomposition**:

```
ROE = (NI / Sales) × (Sales / Assets) × (Assets / Equity)
    = Profit Margin × Asset Turnover × Equity Multiplier
```

### Book-to-Market Ratio

**Formula**: Book Equity / Market Equity

```python
book_to_market = seq / (prcc * csho)
```

**References**:
- Fama & French (1992, JF) - Cross-section of expected stock returns
- Davis, Fama & French (2000, JF) - Characteristics, covariances, and average returns

## Market-Based Metrics

### Market Capitalization

**Formula**: Price × Shares Outstanding (in millions)

```python
market_cap = abs(prcc) * csho
```

**Note**: CRSP prices are negative when they represent bid/ask average. Use `abs()`.

### Enterprise Value

**Formula**: Market Cap + Total Debt - Cash

```python
enterprise_value = (prcc * csho) + (dltt + dlc) - che
```

### Price-to-Earnings Ratio

**Formula**: Price / Earnings Per Share

```python
eps = ni / csho
pe_ratio = prcc / eps
```

## REIT-Specific Metrics

### Funds From Operations (FFO)

**NAREIT Definition**: Net Income + Depreciation & Amortization - Gains on Sale

```python
ffo = ni + dp  # Simplified (gains not always available)
ffo_per_share = ffo / csho
```

**References**:
- NAREIT: https://www.reit.com/data-research/reit-indexes
- Geltner et al. (2007) - Commercial Real Estate Analysis

### Adjusted Funds From Operations (AFFO)

**Formula**: FFO - Recurring Capital Expenditures

```python
affo = ffo - recurring_capex
affo_per_share = affo / csho
```

### EBITDAre (REIT-adjusted EBITDA)

**Formula**: EBIT + Depreciation + Amortization + RE-specific adjustments

```python
ebitdare = oiadp + dp  # Approximation
```

### NAV Discount/Premium

**Formula**: (Price - NAV per share) / NAV per share

```python
nav_per_share = seq / csho  # Book equity as NAV proxy
nav_discount = (prcc - nav_per_share) / nav_per_share
```

## Return Measures

### Buy-and-Hold Returns

**Formula**: Cumulative product of (1 + return)

```python
# Compound returns over period
df['ret_bh'] = df.groupby('permno')['ret'].apply(lambda x: (1 + x).cumprod() - 1)
```

### Cumulative Abnormal Returns (CAR)

**Event Study Formula**: Sum of abnormal returns over event window

```python
# Market-adjusted returns
df['abnormal_ret'] = df['ret'] - df['mkt_ret']

# CAR over [-1, +1] window
df['car_3day'] = (
    df.groupby('permno')['abnormal_ret']
    .rolling(window=3, min_periods=3)
    .sum()
)
```

**References**:
- Fama et al. (1969, IJF) - Adjustment of stock prices to new information
- MacKinlay (1997, JEL) - Event studies in economics and finance

### Buy-and-Hold Abnormal Returns (BHAR)

**Formula**: (1 + Ri) / (1 + Rm) - 1 over holding period

```python
# Size-matched BHAR
df['bhar'] = (
    (1 + df.groupby('permno')['ret'].transform(lambda x: (1 + x).cumprod())) /
    (1 + df.groupby('permno')['benchmark_ret'].transform(lambda x: (1 + x).cumprod()))
    - 1
)
```

**References**:
- Barber & Lyon (1997, JFE) - Detecting long-run abnormal stock returns

## Size/Value/Momentum Portfolios

### Fama-French Size Breakpoints

**Formula**: NYSE median market cap for small vs. big

```python
# Calculate NYSE median
nyse_median = df[df['exchange'] == 'NYSE']['market_cap'].median()

# Assign size portfolio
df['size_port'] = np.where(df['market_cap'] <= nyse_median, 'small', 'big')
```

### Fama-French B/M Breakpoints

**Formula**: NYSE 30th and 70th percentiles of book-to-market

```python
nyse_btm = df[df['exchange'] == 'NYSE']['book_to_market']
p30 = nyse_btm.quantile(0.30)
p70 = nyse_btm.quantile(0.70)

df['value_port'] = pd.cut(df['book_to_market'],
                          bins=[-np.inf, p30, p70, np.inf],
                          labels=['growth', 'neutral', 'value'])
```

**References**:
- Fama & French (1993, JFE) - Common risk factors in returns
- Fama & French (2015, JFE) - Five-factor asset pricing model

### Momentum

**Formula**: 12-month return excluding most recent month

```python
# Calculate 12-month return (t-12 to t-2)
df['ret_12m'] = (
    df.groupby('permno')['ret']
    .rolling(window=12)
    .apply(lambda x: (1 + x[:-1]).prod() - 1)  # Exclude last month
)

# Decile portfolios
df['momentum_port'] = pd.qcut(df['ret_12m'], q=10, labels=False) + 1
```

**References**:
- Jegadeesh & Titman (1993, JF) - Returns to buying winners and selling losers
- Carhart (1997, JF) - Four-factor model

## Common Pitfalls

### 1. Timing Issues

**Problem**: Using contemporaneous prices with lagged fundamentals

**Solution**: Align data dates properly

```python
# Use datadate (fundamental date) to match with CRSP
# CRSP should be 3-6 months after fiscal period end
df['match_date'] = df['datadate'] + pd.DateOffset(months=4)
```

### 2. Negative Book Equity

**Problem**: Distressed firms have negative equity

**Solution**: Flag or exclude these observations

```python
df['valid_btm'] = df['book_to_market'] > 0
df.loc[~df['valid_btm'], 'book_to_market'] = np.nan
```

### 3. Share Splits

**Problem**: CRSP adjusts prices/shares retrospectively

**Solution**: Always use CRSP-adjusted data (cfacpr, cfacshr)

### 4. Delisting Returns

**Problem**: Missing returns for delisted firms create survivorship bias

**Solution**: Merge with CRSP msedelist for delisting returns

```python
# Merge delisting returns
df = df.merge(msedelist[['permno', 'dlstdt', 'dlret']],
             left_on=['permno', 'date'],
             right_on=['permno', 'dlstdt'],
             how='left')

# Use delisting return if available
df['ret_final'] = df['ret'].fillna(df['dlret'])
```

**References**:
- Shumway (1997, JF) - Upward bias in NASDAQ delisting returns
- Johnson & Zhao (2007, JFE) - Delisting return biases
