# Real Estate Databases Reference

CoreLogic, ZTRAX, CoStar, NCREIF property data schemas and linking patterns.

## Table of Contents
- CoreLogic Deed & Tax Records
- ZTRAX (Zillow Transaction & Assessor)
- CoStar Property Database
- NCREIF (National Council REITs)
- Linking Strategies

---

## CoreLogic Deed & Tax Records

**Provider**: CoreLogic (largest US property database)
**Coverage**: ~150M properties, all counties
**Frequency**: Quarterly updates
**Data Lag**: 3-12 months (varies by county)

### Key Tables

**Deed Records** (wrds.corelogic_deed):

| Variable | Definition | Notes |
|----------|-----------|-------|
| `property_id` | Unique parcel identifier | CoreLogic property key |
| `transaction_id` | Unique transaction ID | Primary key for deed |
| `transaction_date` | Date of recorded deed | YYYYMMDD |
| `buyer_name` | Buyer/grantee name | Varies by county; not standardized |
| `seller_name` | Seller/grantor name | Often missing or abbreviated |
| `sale_price` | Recorded transaction price | $0 = non-arm's-length (gift, inheritance) |
| `property_address` | Full property address | Standardized |
| `county_code` | County FIPS code | For county-level aggregation |
| `property_type` | Property category | 'Single Family', 'Condo', 'Multi-Family', etc. |
| `land_use_code` | Land use classification | 'Residential', 'Commercial', 'Industrial' |

**Tax/Assessment Records** (wrds.corelogic_tax):

| Variable | Definition | Notes |
|----------|-----------|-------|
| `property_id` | Parcel identifier | Links to deed records |
| `tax_year` | Assessment year | YYYY |
| `assessed_value` | County-assessed property value | Basis for taxes |
| `estimated_value` | Automated estimate (AVM) | Alternative to assessed |
| `total_baths` | Number of bathrooms | Useful proxy for size |
| `total_rooms` | Total rooms (bedrooms + others) | Rough proxy for size |
| `bed_count` | Number of bedrooms | |
| `building_sqft` | Building square footage | Primary size measure |
| `lot_sqft` | Lot size in sqft | Land value component |
| `year_built` | Year of construction | For age calculations |
| `property_age` | Calculated age (tax_year - year_built) | Direct age variable |
| `msa_code` | Metropolitan Statistical Area | Links to CRSP/Census |

### Query Pattern (CoreLogic Deed)

```sql
SELECT property_id, transaction_date, buyer_name, seller_name, sale_price,
       property_address, county_code, property_type, land_use_code
FROM wrds.corelogic_deed
WHERE transaction_date >= '2010-01-01'
  AND transaction_date <= '2023-12-31'
  AND property_type = 'Single Family'
  AND sale_price > 10000  -- Exclude gifts, low-value transfers
ORDER BY county_code, transaction_date
```

### Common Issues

1. **Missing Prices**: ~15% of deeds have $0 recorded price (gifts, inheritance)
   ```python
   # Filter to arm's-length transactions
   df_deed = df_deed[df_deed['sale_price'] > 10000]
   ```

2. **Name Standardization**: Buyer/seller names are messy
   ```python
   # Upper case and strip whitespace
   df_deed['buyer_name'] = df_deed['buyer_name'].str.upper().str.strip()

   # Use company name detection to filter institutional buyers
   institutional = df_deed['buyer_name'].str.contains('CORP|LLC|LTD|INC|TRUST|FUND')
   df_individual = df_deed[~institutional]
   ```

3. **Multiple Parcels Per Address**: Some deeds involve multiple properties
   ```python
   # Group by transaction_id to get all parcels in single transaction
   transaction_totals = df_deed.groupby('transaction_id')['sale_price'].sum()
   ```

4. **Data Lag by County**: Urban counties ~2-3 months, rural ~6-12 months
   ```python
   # For current analysis, use data > 12 months old
   analysis_date = pd.Timestamp.now() - pd.DateOffset(months=12)
   df = df[df['transaction_date'] <= analysis_date]
   ```

---

## ZTRAX (Zillow Transaction & Assessor)

**Provider**: Zillow (acquired Zestimate + public records)
**Coverage**: ~140M properties, all US states
**Frequency**: Weekly updates
**Uniqueness**: Smaller parcels, newer construction

### Key Differences from CoreLogic

| Feature | CoreLogic | ZTRAX |
|---------|-----------|-------|
| **Price Standardization** | County recording, varies | Standardized, cleaned |
| **Non-arms-length filtering** | Manual needed | Pre-filtered |
| **International investors** | Limited tracking | Better coverage |
| **Speed** | 3-12 month lag | 1-2 week lag |
| **Property ID** | CoreLogic property_id | Zillow zestimate_id |

### ZTRAX Schema (wrds.zillow_txn)

| Variable | Definition | Notes |
|----------|-----------|-------|
| `zestimate_id` | Zillow property ID | Unique across all properties |
| `transaction_id` | Transaction ID | Per-deed unique |
| `transaction_date` | Recorded transaction date | Same as CoreLogic |
| `price` | Sale price | Cleaned, non-zero |
| `price_per_sqft` | Price divided by building sqft | Normalized metric |
| `buyer_seller_same_name` | Flag for flip detection | 1 = likely rental investment |
| `days_on_market` | Listing days (if MLS) | Liquidity measure |
| `transaction_type` | 'Purchase', 'Refinance', 'Transfer' | Standardized |
| `property_age_yrs` | Age at transaction | pre-computed |
| `pool_flag` | 1 if has pool | Amenity indicator |
| `fireplace_flag` | 1 if has fireplace | Amenity indicator |

### Query Pattern (ZTRAX Transactions)

```sql
SELECT zestimate_id, transaction_date, price, price_per_sqft,
       transaction_type, property_age_yrs, days_on_market
FROM wrds.zillow_txn
WHERE transaction_date >= '2015-01-01'
  AND transaction_date <= '2023-12-31'
  AND transaction_type = 'Purchase'
  AND price BETWEEN 50000 AND 1000000
```

### Linking CoreLogic to ZTRAX

```python
# Both use address standardization; can merge on:
# (address, city, state, zip_code)

df_corelogic['address_key'] = (
    df_corelogic['property_address'].str.upper() +
    '|' + df_corelogic['city'].str.upper() +
    '|' + df_corelogic['state'] +
    '|' + df_corelogic['zip_code']
)

df_ztrax['address_key'] = (
    df_ztrax['property_address'].str.upper() +
    '|' + df_ztrax['city'].str.upper() +
    '|' + df_ztrax['state'] +
    '|' + df_ztrax['zip_code']
)

# Merge on address + date (within 30 days)
df_merged = df_corelogic.merge(
    df_ztrax[['address_key', 'transaction_date', 'price_ztrax']],
    on='address_key',
    suffixes=('_cl', '_ztrax')
)

df_merged = df_merged[
    (df_merged['transaction_date_ztrax'] - df_merged['transaction_date_cl']).dt.days.abs() <= 30
]

# Reconcile prices
df_merged['price_diff_pct'] = abs(
    (df_merged['sale_price'] - df_merged['price_ztrax']) / df_merged['sale_price']
)
print(f"Prices match (within 5%): {(df_merged['price_diff_pct'] < 0.05).mean():.1%}")
```

---

## CoStar Property Database

**Provider**: CoStar (commercial real estate data)
**Coverage**: ~2.5M commercial properties (office, retail, industrial, apartment)
**Frequency**: Monthly updates
**Focus**: Institutional-grade commercial data

### Core Tables (wrds.costar_properties)

| Variable | Definition | Notes |
|----------|-----------|-------|
| `costar_property_id` | Unique CoStar ID | Primary key |
| `property_name` | Official property name | |
| `property_type` | Office, Retail, Industrial, Apartment | |
| `city`, `state`, `zip`, `county` | Location fields | Standardized |
| `total_sqft` | Building square footage | Primary size metric |
| `year_built` | Year of construction | |
| `number_of_buildings` | Multi-building properties | 1+ |
| `occupancy_rate` | Current occupancy % | 0-100, monthly |
| `average_rent_sqft` | Rent per sqft/year | Pricing metric |
| `noi` | Net operating income | Annual, $millions |
| `cap_rate` | NOI / Property Value | Expected yield |

### Linking to REIT Portfolios

```python
# Many commercial properties owned by REITs
# Link via address or REIT disclosure

reit_properties = pd.read_sql("""
    SELECT costar_property_id, property_name, noi, cap_rate, occupancy_rate
    FROM wrds.costar_properties
    WHERE property_type IN ('Office', 'Apartment')
      AND year >= 2015
""", conn)

# Link to CRSP REITs
reit_gvkeys = pd.read_sql("""
    SELECT DISTINCT gvkey, tic, conm
    FROM comp.company
    WHERE sic >= 6798 AND sic < 6800  -- REIT SIC codes
""", conn)

# Cross-reference via public disclosures (manual or OCR 10-K filings)
```

---

## NCREIF (National Council of Real Estate Investment Fiduciaries)

**Provider**: NCREIF (institutional investor consortium)
**Coverage**: ~10K institutional properties
**Frequency**: Quarterly (Q1, Q2, Q3, Q4)
**Quality**: Institutional-grade, audited returns

### NCREIF Property Index (NPI)

**Composition**:
- Diversified institutional investor properties
- 8 property types: Office, Retail, Industrial, Apartment, Hotel, Mixed-use, Land, Special-use
- ~10K properties (varies by period)

### Data Available (wrds.ncreif_npi)

| Variable | Definition | Notes |
|----------|-----------|-------|
| `property_id` | NCREIF property ID | Primary key |
| `property_name` | Official name | |
| `property_type` | 8-type classification | Standardized |
| `period` | Quarter (YYYYQ) | 1989-present |
| `acquisition_value` | Original purchase price | Baseline |
| `market_value` | Market value EOQ | Property valuation |
| `capital_improvements` | Additions/improvements | |
| `noi` | Net Operating Income | Quarterly |
| `operating_expense_ratio` | OpEx / Revenue | Efficiency metric |
| `total_return` | Quarterly total return (%) | (EOQ Value - BOQ Value + Dividends) / BOQ Value |
| `appreciation` | Property value appreciation | Market appreciation |
| `income_return` | Income component of return | NOI / BOQ Value |

### Return Calculation (NCREIF)

```
Total Return (Quarter) = (Market Value (EOQ) - Market Value (BOQ) + NOI - Capex) / Market Value (BOQ)
                       = Appreciation Return + Income Return

Annualized = (1 + Quarterly Return)^4 - 1
```

**Example**:
```python
# Calculate annualized return
ncreif['quarterly_return'] = (
    (ncreif['market_value_eoq'] - ncreif['market_value_boq'] + ncreif['noi']) /
    ncreif['market_value_boq']
)

ncreif['annual_return'] = ncreif.groupby('property_id')['quarterly_return'].apply(
    lambda x: (1 + x).prod() - 1
)
```

### Asset Class Benchmarks

```python
# Group NPI by property type and compute average index
ncreif_index = ncreif.groupby(['property_type', 'period']).agg({
    'total_return': 'mean',
    'appreciation': 'mean',
    'income_return': 'mean'
})

# Track indices: Office, Retail, Industrial, Apartment (most common)
ncreif_index_wide = ncreif_index.unstack(level=0)
ncreif_index_wide.plot()
```

---

## Linking Strategies

### Cross-Database Merge (Property Transaction Analysis)

**Goal**: Combine CoreLogic + ZTRAX + CoStar for comprehensive property view.

```python
# 1. Standardize addresses
def clean_address(addr):
    return addr.upper().replace('.', '').replace(',', '').replace('  ', ' ')

df_cl['addr_clean'] = df_cl['property_address'].apply(clean_address)
df_ztrax['addr_clean'] = df_ztrax['property_address'].apply(clean_address)
df_costar['addr_clean'] = (
    df_costar['street'] + ' ' + df_costar['city'] + ' ' + df_costar['state']
).apply(clean_address)

# 2. Merge on address + location
merge_key = ['addr_clean', 'city', 'state', 'zip_code']

df_all = df_cl.merge(
    df_ztrax, on=merge_key, how='outer', suffixes=('_cl', '_ztrax')
)
df_all = df_all.merge(
    df_costar, on=merge_key, how='left', suffixes=('', '_costar')
)

# 3. Reconcile values (choose best source for each field)
df_all['price_final'] = df_all['price_ztrax'].fillna(df_all['sale_price'])
df_all['sqft_final'] = df_all['building_sqft_costar'].fillna(df_all['building_sqft_cl'])

print(f"Merge coverage: {df_all.notna().sum() / len(df_all)}")
```

### REIT-Property Linking

```python
# REITs publicly disclose property holdings
# Extract from 10-K filings (manual or NLP-based)

reit_portfolio = pd.DataFrame({
    'gvkey': [123456],
    'tic': ['XYZ'],
    'property_name': ['Main Street Office Tower'],
    'city': ['New York'],
    'state': ['NY'],
    'property_type': ['Office']
})

# Match to CoStar
reit_costar = reit_portfolio.merge(
    df_costar[['property_name', 'costar_property_id', 'noi', 'occupancy_rate']],
    on=['property_name'],
    how='left'
)

# Calculate REIT portfolio metrics
portfolio_noi = reit_costar.groupby('gvkey')['noi'].sum()
portfolio_occupancy = reit_costar.groupby('gvkey')['occupancy_rate'].mean()
```

---

## References

- **CoreLogic**: https://www.corelogic.com/
- **Zillow ZTRAX**: https://www.zillow.com/research/ztrax/
- **CoStar**: https://www.cbre.com/services/technology
- **NCREIF**: https://www.ncreif.org/
- **Academic Research**:
  - Davis, Lehnert & Martin (2008): "Equity and Housing Wealth with Sticky Prices" (*QJE*)
  - Genesove & Mayer (1997): "Equity and Time to Sale in the Real Estate Market" (*AER*)
  - Hilbers, Lei & Zacho (2001): "Real Estate Market Spillovers in the New EU Member States" (*IMF*)
