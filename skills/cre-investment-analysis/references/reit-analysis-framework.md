# REIT Analysis Framework

## Overview

Real Estate Investment Trusts (REITs) are companies that own, operate, or finance income-producing real estate. REITs must distribute at least 90% of taxable income to shareholders as dividends, making them income-focused investments with unique valuation metrics.

## Key REIT Metrics

### Funds From Operations (FFO)

**Definition**: Net income + depreciation & amortization - gains on property sales

**Formula**:
```
FFO = Net Income
    + Depreciation & Amortization
    + Losses on Property Sales
    - Gains on Property Sales
    - Gains on Sale of Unconsolidated JVs
```

**Purpose**: Better measure of REIT operating performance than net income (which is distorted by non-cash depreciation)

**Industry Standard**: NAREIT definition

### Adjusted Funds From Operations (AFFO)

**Definition**: FFO adjusted for recurring capital expenditures and straight-line rent adjustments

**Formula**:
```
AFFO = FFO
     - Recurring Capital Expenditures
     - Straight-Line Rent Adjustments
     + Non-Cash Compensation (if added back)
```

**Purpose**: Represents sustainable cash flow available for distribution

**Alternative Names**: Cash Available for Distribution (CAD), Funds Available for Distribution (FAD)

### Net Operating Income (NOI)

**Definition**: Rental revenue - property operating expenses (excluding debt service, depreciation, capex)

**Same-Store NOI Growth**: NOI growth for properties owned in both comparison periods
- Most important operational metric
- Typically reported quarterly and annually
- Indicates organic growth and operational efficiency

### Occupancy Metrics

- **Economic Occupancy**: Actual rent collected / potential rent if fully leased
- **Physical Occupancy**: % of space with signed leases
- **Average Occupancy**: Typically reported as weighted average across portfolio

### Lease Metrics

- **Weighted Average Lease Term (WALT)**: Average remaining lease term weighted by rental income
- **Lease Renewal Rate**: % of expiring leases that renew
- **Lease Spreads**: Difference between new/renewal rents and expiring rents
  - Cash spread: Based on actual rent paid
  - GAAP spread: Based on straight-line rent

## Valuation Methods

### 1. FFO/AFFO Multiples

**P/FFO Multiple**:
```
Price per Share / FFO per Share
```

**Typical Ranges**:
- Residential REITs: 15-20x FFO
- Industrial/Logistics: 20-25x FFO
- Retail: 10-15x FFO
- Office: 10-18x FFO
- Data Centers: 20-30x FFO

**P/AFFO Multiple**:
```
Price per Share / AFFO per Share
```
- Typically 1-3 multiple points higher than P/FFO

### 2. Dividend Yield Analysis

**Dividend Yield**:
```
Annual Dividend per Share / Current Stock Price
```

**Relative Yield**:
- Compare to 10-year Treasury yield
- Compare to REIT sector average
- Compare to company's historical yield

**Payout Ratio**:
```
Dividend per Share / AFFO per Share
```
- Target range: 70-90%
- Higher ratio = less retained earnings for growth
- Lower ratio = potential for dividend growth

### 3. Net Asset Value (NAV)

**Calculation**:
```
NAV = (Total Property Value at Market Cap Rates
     - Total Debt
     - Preferred Equity) / Common Shares Outstanding
```

**NAV per Share vs. Stock Price**:
- Premium to NAV: Stock overvalued or market expects strong growth
- Discount to NAV: Stock undervalued, liquidity concern, or execution risk

**Cap Rate Estimation**:
- Use market cap rates for each property type/market
- Adjust for property quality and location
- Compare to recent transaction cap rates

### 4. Discounted Cash Flow (DCF)

**Approach**:
1. Project AFFO for 5-10 years
2. Estimate terminal value using exit multiple or perpetuity growth
3. Discount at WACC

**WACC Calculation**:
```
WACC = (E/V × Cost of Equity) + (D/V × Cost of Debt × (1-Tax Rate))
```

**Cost of Equity**: CAPM or implied from dividend discount model

**Terminal Value**:
```
Terminal Value = Final Year AFFO × Exit Multiple
```
or
```
Terminal Value = Final Year AFFO × (1 + g) / (WACC - g)
```

## Financial Health Metrics

### Leverage Ratios

**Debt-to-EBITDA**:
```
Total Debt / (NOI or EBITDA)
```
- Target: <6.0x for investment grade
- Office/Retail: May run higher (7-8x)
- Residential/Industrial: Typically lower (4-6x)

**Net Debt to EBITDA**:
```
(Total Debt - Cash) / EBITDA
```

**Loan-to-Value (LTV)**:
```
Total Debt / Gross Asset Value
```
- Target: 30-50% for most REITs
- Higher LTV = higher financial risk

**Debt-to-Equity**:
```
Total Debt / Total Equity
```

### Coverage Ratios

**Fixed Charge Coverage**:
```
(EBITDA - Recurring CapEx) / (Interest + Preferred Dividends)
```
- Target: >2.5x

**Interest Coverage**:
```
EBITDA / Interest Expense
```
- Target: >3.0x

**Dividend Coverage**:
```
AFFO per Share / Dividend per Share
```
- Target: >1.1x (90%+ payout is acceptable for stable REITs)

### Liquidity Metrics

**Unencumbered Asset Ratio**:
```
Unencumbered Assets / Unsecured Debt
```
- Important for unsecured debt issuers
- Target: >2.0x

**Variable Rate Debt %**:
- Target: <25% of total debt
- Higher exposure = higher interest rate risk

## Growth Metrics

### Internal Growth

**Same-Store NOI Growth**:
- Organic growth from existing portfolio
- Target: 2-4% annually (stable markets)
- Driven by: rent growth, occupancy gains, operating efficiencies

**Rent Growth Components**:
- Market rent growth
- Renewal spreads
- Lease escalators

**Occupancy Improvement**:
- Impact on NOI
- Watch for elevated capex during lease-up

### External Growth

**Development Pipeline**:
- Yields on new projects (8-10% typical target)
- % of GAV in development (<10% is conservative)
- Pre-leasing %

**Acquisition Activity**:
- Cap rates on acquisitions vs. in-place cap rates
- Integration risk
- Market timing

**Capital Recycling**:
- Disposition proceeds
- Redeployment into higher-growth markets/assets
- Timing and execution

## Sector-Specific Considerations

### Apartment REITs
- Key metrics: Revenue per available room (RevPAR), occupancy, rent growth
- Watch: New supply, job growth, household formation
- Typical P/FFO: 15-20x
- Same-store NOI target: 3-5%

### Industrial REITs
- Key metrics: Occupancy, lease renewals, rent spreads
- Watch: E-commerce penetration, supply chain trends
- Typical P/FFO: 20-25x
- Same-store NOI target: 4-7%

### Office REITs
- Key metrics: Leasing spreads, WALT, tenant retention
- Watch: Return-to-office trends, quality (Class A vs B/C)
- Typical P/FFO: 10-18x
- Same-store NOI target: 1-3%

### Retail REITs
- Key metrics: Sales per square foot, occupancy cost ratio
- Watch: E-commerce impact, retailer health
- Typical P/FFO: 10-15x
- Same-store NOI target: 1-3%

### Healthcare REITs
- Key metrics: Occupancy, coverage ratios (tenant EBITDARM/rent)
- Watch: Regulatory changes, demographics, operator quality
- Typical P/FFO: 12-18x
- Same-store NOI target: 2-4%

### Self-Storage REITs
- Key metrics: Occupancy, RevPAU (revenue per available unit)
- Watch: New supply, street rates vs. in-place rates
- Typical P/FFO: 18-23x
- Same-store NOI target: 3-6%

### Data Center REITs
- Key metrics: Utilization, renewal rates, power capacity
- Watch: Cloud adoption, AI demand, power costs
- Typical P/FFO: 20-30x
- Same-store NOI target: 3-5%

## Credit Analysis

### Investment Grade Characteristics
- Debt/EBITDA: <6.0x
- Fixed charge coverage: >2.5x
- Unencumbered assets: >60% of total
- Interest coverage: >4.0x
- Diversified portfolio
- Strong management track record

### High Yield Characteristics
- Debt/EBITDA: >7.0x
- Fixed charge coverage: <2.0x
- Higher leverage
- Concentration risk
- Development/redevelopment risk

## Tax Efficiency

### Dividend Classification
- Ordinary income: ~60-80% of REIT dividends (taxed at ordinary rates)
- Return of capital: ~10-30% (reduces cost basis)
- Capital gains: ~5-15% (taxed at capital gains rates)

**Qualified REIT Dividends**: 20% deduction under TCJA (through 2025)
- Effective top federal rate: 29.6% (37% × 80%)

### Tax-Advantaged Accounts
- REITs are ideal for IRAs, 401(k)s due to high ordinary income component
- Minimize tax drag in taxable accounts

## Comparative Analysis Framework

### Peer Comparison Checklist
1. FFO/AFFO multiples vs. sector peers
2. Dividend yield vs. peers and historical average
3. Same-store NOI growth vs. peers
4. Leverage metrics vs. peers
5. Occupancy and operational metrics vs. peers
6. Management quality and track record
7. Portfolio quality (vintage, location, tenancy)
8. Balance sheet strength (debt maturities, access to capital)

### Relative Value Indicators
- **Cheap**: P/FFO <15x, dividend yield >5%, trading at discount to NAV
- **Fair Value**: P/FFO 15-20x, dividend yield 3-5%, near NAV
- **Expensive**: P/FFO >20x, dividend yield <3%, premium to NAV

## Investment Decision Framework

### Buy Signals
- Trading at significant discount to NAV (>10%)
- P/FFO below historical average and peer group
- Dividend yield above historical average
- Strong same-store NOI growth trajectory
- Improving operational metrics (occupancy, spreads)
- Deleveraging balance sheet
- Accretive external growth pipeline

### Sell Signals
- Trading at significant premium to NAV (>10%)
- P/FFO above historical average and peer group
- Dividend yield below historical average
- Declining same-store NOI growth
- Deteriorating operational metrics
- Increasing leverage
- Elevated development risk

### Risk Factors to Monitor
- Overleveraged balance sheet
- Concentrated exposure (geography, tenant, property type)
- Aggressive development pipeline (>15% of GAV)
- Declining dividend coverage (<1.1x AFFO/dividend)
- Management turnover or governance issues
- Sector headwinds (e.g., retail disruption, office obsolescence)

## Data Sources

- **NAREIT**: Industry standards, market data, research
- **SNL Financial (S&P Global)**: Comprehensive REIT financials and analytics
- **Green Street**: REIT research, NAV estimates, market outlook
- **Bloomberg**: Real-time pricing, financial data, analytics
- **Company Earnings Calls**: Management guidance and commentary
- **Investor Presentations**: Portfolio composition, strategy updates
- **10-K/10-Q Filings**: Detailed financial and operational data
