# Document Integration Workflows for CRE Analysis

## Overview

Commercial real estate analysis relies heavily on extracting and validating data from various document sources. This guide provides detailed workflows for integrating the CRE investment analysis skill with Claude's official document processing skills.

## Document Skills Quick Reference

| Skill | Purpose | Common CRE Use Cases |
|-------|---------|---------------------|
| `pdf` | Extract text/tables from PDFs | Offering memos, appraisals, environmental reports, title reports, PCAs |
| `xlsx` | **CREATE/EDIT/READ** Excel files | **BUILD financial models**, analyze T-12 statements, rent rolls, budgets, comps |
| `docx` | Read/create Word documents | Investment memos, market studies, business plans, due diligence reports |
| `pptx` | Create/edit PowerPoint | Investment committee presentations, board decks, marketing materials |

**IMPORTANT**: The `xlsx` skill is used for BOTH extracting data from existing spreadsheets AND creating new professional CRE financial models. When creating models, strict adherence to professional standards is required: use formulas (not hardcoded values), apply proper color coding (blue=inputs, black=formulas), and ensure dynamic calculations.

## Detailed Workflows

### Workflow 1: Complete Multifamily Acquisition Analysis

**Scenario**: Analyzing a 200-unit apartment complex acquisition

**Input Documents**:
1. Offering memorandum (PDF) - 45 pages
2. Trailing 12-month operating statement (Excel)
3. Current rent roll (Excel)
4. Comparable sales analysis (PDF)
5. Market study (PDF or Word)

**Step-by-Step Process**:

#### Step 1: Extract Offering Memo Data (PDF Skill)
```
Use the pdf skill to extract from the offering memorandum:
1. Property address and description
2. Asking price
3. Seller's pro forma NOI
4. Current occupancy
5. List of recent capital improvements
6. Lease terms and concessions
7. Property tax and insurance amounts
```

**What to extract**:
- Executive summary page
- Property details (location, age, condition)
- Financial summary table
- Capital expenditures list
- Market positioning claims

**Validation checks**:
- Does asking price match stated cap rate and NOI?
- Are property details consistent throughout document?
- Any footnotes or disclaimers that modify numbers?

#### Step 2: Analyze Operating Statement (XLSX Skill)
```
Use the xlsx skill to analyze the T-12 operating statement:
1. Extract monthly revenue by category (rent, parking, other income)
2. Extract monthly expenses by category
3. Calculate actual operating expense ratio
4. Identify any unusual or one-time expenses
5. Calculate actual vacancy rate
6. Summarize NOI trend over 12 months
```

**Key calculations**:
- Physical occupancy % per month
- Economic occupancy (revenue / potential revenue)
- OpEx ratio (operating expenses / EGI)
- NOI per unit per month
- Year-over-year trends if multi-year data available

**Red flags to identify**:
- Declining occupancy trend
- Rising vacancy loss
- Increasing uncollected rent (bad debt)
- Unusual expense spikes
- Missing expense categories (e.g., no maintenance costs = deferred)

#### Step 3: Analyze Rent Roll (XLSX Skill)
```
Use the xlsx skill to analyze the current rent roll:
1. Extract: Unit #, unit type, square footage, current rent, move-in date, lease end date
2. Calculate weighted average rent by unit type
3. Identify lease expiration concentrations
4. Calculate average lease term remaining
5. Identify below-market and above-market units
```

**Analysis outputs**:
- Rent per square foot by unit type
- Occupancy by unit type
- Lease expiration schedule (next 24 months)
- Percentage expiring each quarter
- Roll-to-market opportunity ($)

**Market comparison**:
- Compare to market rents (from market study)
- Identify underperforming units
- Calculate potential rent growth

#### Step 4: Extract Market Data (PDF Skill)
```
Use the pdf skill to extract from market study and comps:
1. Submarket occupancy rates
2. Market rent ranges by unit type
3. Recent comparable sales ($/unit, cap rate)
4. New supply pipeline
5. Demographic and employment data
```

**Focus areas**:
- Competitive set definition
- Market rent comparisons
- Absorption trends
- Supply/demand balance

#### Step 5: Cross-Reference and Validate
```
Cross-reference data from all sources:
1. Does offering memo NOI match T-12 actual?
2. Does rent roll match offering memo occupancy claim?
3. Do in-place rents match market study ranges?
4. Are property taxes consistent across documents?
5. Do unit counts match across all sources?
```

**Common discrepancies**:
- Offering memo uses "pro forma" vs. actual T-12
- Rent roll date differs from T-12 period end
- Different vacancy assumptions
- Different treatment of concessions
- Missing or inconsistent expense categories

#### Step 6: Perform Independent Analysis (CRE Skill)
```
Using the cre-investment-analysis skill, create independent analysis:

Property Inputs (validated from documents):
- Purchase price: [from offering memo]
- Current NOI: [from T-12, adjusted if needed]
- Occupancy: [from rent roll]
- In-place rents: [from rent roll]
- Operating expenses: [from T-12]

Market Inputs (from market study):
- Market rents by unit type
- Market vacancy rate
- New supply coming online
- Rent growth forecast

Assumptions:
- Renovation budget: $X/unit (if value-add)
- Stabilized occupancy: 95% (market rate minus buffer)
- Rent growth: 3% annually (validate against market)
- OpEx growth: 2.5% annually
- Exit cap rate: Entry cap + 25 bps

Analysis Required:
1. 10-year pro forma with monthly detail for Year 1
2. Base/downside/upside scenarios
3. Sensitivity analysis (exit cap vs. rent growth)
4. Levered and unlevered IRR
5. Risk assessment
6. Investment recommendation
```

#### Step 7: Create Deliverables

**Investment Memo (DOCX Skill)**:
```
Create a 10-15 page investment memorandum using docx skill:

1. Executive Summary (1-2 pages)
   - Investment highlights
   - Financial summary
   - Recommendation

2. Property Description (2-3 pages)
   - Location and access
   - Physical characteristics
   - Unit mix
   - Condition assessment

3. Market Analysis (2-3 pages)
   - Submarket overview
   - Supply and demand
   - Competitive positioning
   - Market outlook

4. Financial Analysis (3-4 pages)
   - Historical performance
   - Pro forma assumptions
   - Cash flow projections
   - Return metrics
   - Sensitivity analysis

5. Risk Assessment (1-2 pages)
   - Key risks
   - Mitigation strategies

6. Appendices
   - Detailed rent roll
   - T-12 summary
   - Market comps
```

**Financial Model (XLSX Skill)**:
```
Create Excel financial model using xlsx skill with STRICT professional standards:

⚠️ CRITICAL REQUIREMENTS - NON-NEGOTIABLE:
✓ Use FORMULAS for ALL calculations - NO hardcoded values except blue assumptions
✓ Color code: BLUE text = inputs | BLACK text = formulas | GREEN text = cross-sheet links
✓ All formulas MUST reference cells (e.g., =Assumptions!$B$5 * B10, NOT =27000000 * 0.05)
✓ Use absolute ($B$5) and relative (B5) references appropriately
✓ Deliver with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A)
✓ Model must be DYNAMIC - changing any assumption recalculates entire model

Tabs Structure:
1. Summary - All key metrics on one page
2. Assumptions - ALL inputs in BLUE text (e.g., rent growth, cap rates, costs)
   - Document sources for each assumption
   - Use clear labels and units
3. Operating Pro Forma - 10-year projections
   - Example: Year 2 Rent = ='Year 1 Rent' * (1 + Assumptions!$B$9)
   - NOT: =1450000 * 1.03
4. Rent Roll - Unit-level detail
5. Capital Budget - Renovation/capex schedule
6. Sources & Uses - Transaction costs (all formulas)
7. Debt Schedule - Amortization using PMT function and cell references
8. Cash Flow - Before/after tax equity cash flows
9. Sensitivity - Two-way data tables (use Data → What-If Analysis)
10. Returns - IRR/NPV/multiples (all formulas)

Formatting Standards (per xlsx skill requirements):
- Currency: $#,##0 format, specify units in headers ("Revenue ($000s)")
- Percentages: 0.0% (one decimal)
- Zeros: Format to display as "-" not "0"
- Negative numbers: (123) not -123
- Years: Text format "2024" not number "2,024"

Formula Examples:
❌ WRONG: =27000000 * 0.7 * 0.06 / 12
✅ CORRECT: =Assumptions!$B$3 * Assumptions!$B$19 * Assumptions!$B$20 / 12

❌ WRONG: =850000 + 875500 + 901765
✅ CORRECT: =SUM(B5:D5) or individual cell references

❌ WRONG: =IF(A5="Year 3", 1500000, 0)
✅ CORRECT: =IF(A5="Year 1", Assumptions!$B$8, PreviousYear*(1+Assumptions!$B$9))

Quality Verification Tests:
1. Change purchase price from $27M to $30M → all calculations update? ✓
2. Change rent growth from 3% to 4% → all years adjust? ✓
3. Change exit cap from 5.75% to 6.0% → sale price and IRR recalculate? ✓
4. Change LTV from 70% to 65% → debt amount and payments adjust? ✓
5. All cells with BLACK text contain formulas (not numbers)? ✓
6. All cells with BLUE text are in Assumptions tab? ✓
7. Zero formula errors anywhere in workbook? ✓
```

**Investment Committee Presentation (PPTX Skill)**:
```
Create PowerPoint using pptx skill (15-20 slides):

1. Cover slide with property image
2. Executive summary
3. Investment highlights (bullets)
4. Property location map
5. Property photos
6. Market overview
7. Competitive set comparison
8. Financial summary
9. Operating pro forma
10. Capital budget
11. Returns summary
12. Sensitivity analysis
13. Risk factors
14. Recommendation
15. Appendix - detailed financials

Use professional template with consistent branding
```

### Workflow 2: Creating Professional Excel Financial Models

**Scenario**: Building institutional-quality financial models for CRE analysis

**CRITICAL PRINCIPLES**:

1. **NO HARDCODING**: Never hardcode values in formulas (except in dedicated Assumptions cells)
2. **USE FORMULAS**: Every calculation must be a formula with cell references
3. **COLOR CODING**: Follow industry standards strictly
4. **CONSISTENCY**: Same formula structure across all periods
5. **DOCUMENTATION**: Source all assumption inputs

#### Professional Excel Model Standards (xlsx Skill)

**Color Coding Requirements**:
- **Blue text (RGB: 0,0,255)**: ALL assumption inputs that users will change
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: References to other worksheets in same workbook
- **Red text (RGB: 255,0,0)**: External links to other files (avoid if possible)
- **Yellow background (RGB: 255,255,0)**: Key assumptions requiring attention

**Number Formatting**:
- Currency: `$#,##0` (specify units in headers: "Revenue ($000s)")
- Percentages: `0.0%` (one decimal place)
- Zeros: Format to display as `"-"` instead of `0`
- Negative numbers: Use parentheses `(123)` not minus `-123`
- Multiples: `0.0x` for valuation multiples

**Formula Construction Rules**:

❌ **WRONG** - Hardcoded values in formulas:
```
=850000 * 1.03  // BAD: Growth rate hardcoded
=B5 - 340000    // BAD: Expense amount hardcoded
=1650000 / 0.055 // BAD: Cap rate hardcoded
```

✅ **CORRECT** - Cell references:
```
=B5 * (1 + $B$2)        // GOOD: Reference to growth rate assumption
=B5 - Assumptions!B10   // GOOD: Reference to assumption on another sheet
=B20 / $Assumptions.$B$5 // GOOD: Reference to cap rate assumption
```

**Absolute vs. Relative References**:
- **Absolute ($B$5)**: Use for assumptions that don't change when copying formulas
- **Relative (B5)**: Use for values that should adjust when copying across periods
- **Mixed ($B5 or B$5)**: Use when only row or column should be absolute

Example:
```
Year 1: =B10 * (1 + $B$2)  // B10 is relative (Year 1 value), $B$2 is absolute (growth assumption)
Year 2: =C10 * (1 + $B$2)  // When copied, B10 becomes C10, but $B$2 stays the same
```

#### Tab Organization for CRE Models

**Standard Tab Structure**:

1. **Summary** - One-page overview of all key metrics
2. **Assumptions** - All blue inputs in one place
3. **Operating Pro Forma** - Revenue and expense projections
4. **Rent Roll** - Unit-level detail (multifamily)
5. **Lease Schedule** - Tenant-level detail (office/retail/industrial)
6. **Capital Budget** - CapEx and renovation schedule
7. **Sources & Uses** - Acquisition/development costs
8. **Debt Schedule** - Loan amortization
9. **Cash Flow** - Equity cash flows (before/after tax)
10. **Sensitivity** - Return sensitivity to key variables
11. **Returns** - IRR, NPV, multiples calculations

#### Example: Building a Multifamily Acquisition Model

**Step-by-Step Process**:

##### Step 1: Create Assumptions Tab (xlsx skill)

```
Use the xlsx skill to create an Assumptions tab with the following structure:

PROPERTY ASSUMPTIONS (all in BLUE text):
- Purchase Price: $27,000,000
- Acquisition Costs %: 1.5%
- Number of Units: 180
- Current Occupancy %: 88%
- Market Occupancy %: 95%

REVENUE ASSUMPTIONS (all in BLUE text):
- Year 1 Average Rent/Unit/Month: $1,450
- Annual Rent Growth %: 3.0%
- Vacancy & Collection Loss %: 5.0%
- Other Income/Unit/Month: $50

OPERATING EXPENSE ASSUMPTIONS (all in BLUE text):
- Property Tax/Unit/Year: $1,200
- Insurance/Unit/Year: $450
- Utilities/Unit/Year: $600
- Repairs & Maintenance %: 10% of EGI
- Property Management %: 4% of EGI
- Administrative %: 2% of EGI
- Replacement Reserves/Unit/Year: $300

DEBT ASSUMPTIONS (all in BLUE text):
- LTV %: 70%
- Interest Rate %: 6.0%
- Amortization (years): 30
- IO Period (years): 5

EXIT ASSUMPTIONS (all in BLUE text):
- Hold Period (years): 7
- Exit Cap Rate %: 5.75%
- Selling Costs %: 3.0%

All cells above should be formatted with BLUE TEXT.
Include cell addresses (e.g., B5, B6) that will be referenced throughout the model.
```

##### Step 2: Create Operating Pro Forma Tab (xlsx skill)

```
Create Operating Pro Forma tab with 10-year projections.

CRITICAL: Use FORMULAS for all calculations - NO HARDCODED values.

Column Headers: Year 0 (Current) | Year 1 | Year 2 | ... | Year 10

REVENUE SECTION (all BLACK text formulas):
Potential Rental Income:
  Year 1: =Assumptions!$B$5 * Assumptions!$B$7 * Assumptions!$B$8 * 12
  (Translates to: Units × Market Rent × Occupancy × 12 months)
  Copy formula across years, adjusting for rent growth:
  Year 2: =C5 * (1 + Assumptions!$B$9)

Other Income:
  =Assumptions!$B$5 * Assumptions!$B$10 * 12
  (Units × Other Income per Unit × 12 months)

Gross Potential Income:
  =SUM(rental_income + other_income)

Vacancy & Collection Loss:
  =-1 * GrossPotentialIncome * Assumptions!$B$11

Effective Gross Income:
  =GrossPotentialIncome + VacancyLoss

OPERATING EXPENSES SECTION (all BLACK text formulas):
Property Taxes:
  =Assumptions!$B$5 * Assumptions!$B$12

Insurance:
  =Assumptions!$B$5 * Assumptions!$B$13

Utilities:
  =Assumptions!$B$5 * Assumptions!$B$14

Repairs & Maintenance:
  =EffectiveGrossIncome * Assumptions!$B$15

Property Management:
  =EffectiveGrossIncome * Assumptions!$B$16

Administrative:
  =EffectiveGrossIncome * Assumptions!$B$17

Total Operating Expenses:
  =SUM(all expense line items)

NET OPERATING INCOME:
  =EffectiveGrossIncome - TotalOperatingExpenses
  (Format in BOLD)

Capital Reserves:
  =-1 * Assumptions!$B$5 * Assumptions!$B$18

Cash Flow Available for Debt Service:
  =NOI - CapitalReserves

ALL formulas should reference the Assumptions tab.
NO hardcoded values in any formula.
Copy formulas across all years (adjusting for growth where applicable).
```

##### Step 3: Create Debt Schedule Tab (xlsx skill)

```
Create monthly amortization schedule:

Columns: Month | Beginning Balance | Payment | Interest | Principal | Ending Balance

Loan Amount (BLACK text):
  =Assumptions!$B$3 * Assumptions!$B$19
  (Purchase Price × LTV)

Monthly Interest Rate (BLACK text):
  =Assumptions!$B$20 / 12

Number of Payments (BLACK text):
  =Assumptions!$B$21 * 12

IO Period Months (BLACK text):
  =Assumptions!$B$22 * 12

Monthly Payment Calculation:
  IO Period: =Loan_Amount * Monthly_Rate
  Amortizing Period: Use PMT function with remaining balance and periods

Formula for each month:
  Beginning Balance: =Previous_Month_Ending_Balance
  Interest: =Beginning_Balance * Monthly_Rate
  Principal: =Payment - Interest (or 0 for IO period)
  Ending Balance: =Beginning_Balance - Principal

ALL formulas - NO hardcoded values.
```

##### Step 4: Create Cash Flow Tab (xlsx skill)

```
Structure:
Year | NOI | Debt Service | CF Before Tax | Cumulative Cash Flow

NOI (GREEN text - links to Operating Pro Forma):
  ='Operating Pro Forma'!B25

Annual Debt Service (BLACK text):
  =SUM(Debt_Schedule!monthly_payments) for that year

Cash Flow Before Tax (BLACK text):
  =NOI - Annual_Debt_Service

ALL values are formulas referencing other tabs.
NO hardcoded numbers.
```

##### Step 5: Create Sensitivity Analysis Tab (xlsx skill)

```
Two-way sensitivity table for IRR:

Rows: Exit Cap Rate (vary from 5.0% to 6.5%)
Columns: Rent Growth (vary from 1% to 5%)

Use DATA TABLE function in Excel:
1. Set up input cells for Exit Cap and Rent Growth
2. Create table with row/column headers
3. Formula in upper-left: =Returns!$B$5 (reference to IRR calculation)
4. Select entire table → Data → What-If Analysis → Data Table
5. Row input cell: Point to Rent Growth assumption
6. Column input cell: Point to Exit Cap assumption

This creates dynamic sensitivity that recalculates with any assumption changes.
```

#### Common Excel Model Errors to Avoid

**Error 1: Hardcoded Values**
```
❌ WRONG:
=1450 * 180 * 12  // Hardcoded rent and units

✅ CORRECT:
=Assumptions!$B$8 * Assumptions!$B$5 * 12  // Cell references
```

**Error 2: Inconsistent Formulas**
```
❌ WRONG:
Year 1: =B5 * 1.03
Year 2: =C5 * 1.03
Year 3: =D5 * 1.04  // Different growth rate!

✅ CORRECT:
All years: =PreviousYear * (1 + $Assumptions.$B$9)
```

**Error 3: Not Using Absolute References**
```
❌ WRONG:
Copying this formula across: =B10 * B2  // B2 will become C2, D2, etc.

✅ CORRECT:
=B10 * $B$2  // $B$2 stays constant when copied
```

**Error 4: Hardcoded Conditional Logic**
```
❌ WRONG:
=IF(A5="Year 1", 850000, IF(A5="Year 2", 875500, 0))

✅ CORRECT:
=IF(A5="Year 1", Assumptions!$B$8, PreviousYear*(1+Assumptions!$B$9))
```

**Error 5: Missing Cell References**
```
❌ WRONG:
Expense Ratio = Total Expenses / EGI
Then typing "42%" in the cell

✅ CORRECT:
=TotalExpenses / EffectiveGrossIncome  // Calculates automatically
```

#### Quality Control Checklist

Before finalizing any Excel model:

**Formula Verification**:
- [ ] All assumption inputs are in BLUE text
- [ ] All formulas are in BLACK text
- [ ] All cross-sheet references are in GREEN text
- [ ] NO hardcoded values in formula cells
- [ ] All formulas use cell references to Assumptions tab
- [ ] Formulas are consistent when copied across periods
- [ ] No #REF!, #VALUE!, #DIV/0!, or #N/A errors

**Calculation Checks**:
- [ ] Total sources = Total uses
- [ ] Cash flow beginning + in - out = ending balance
- [ ] IRR calculation includes all cash flows (in/out/reversion)
- [ ] Debt balance at exit matches amortization schedule
- [ ] Expense ratios are reasonable (35-45% for multifamily)
- [ ] Returns are mathematically correct (spot check with calculator)

**Formatting Checks**:
- [ ] Currency formatted with appropriate decimals
- [ ] Percentages formatted to one decimal (0.0%)
- [ ] Zeros display as "-"
- [ ] Negative numbers use parentheses
- [ ] Headers clearly state units ($000s, $mm, etc.)
- [ ] Tabs are logically organized
- [ ] Summary tab fits on one page (for printing)

**Documentation**:
- [ ] All assumption sources are documented
- [ ] Model version and date are noted
- [ ] Author/preparer is identified
- [ ] Key limitations or disclaimers are stated

#### Example Prompt for Creating Excel Model

```
Using the xlsx skill, create a professional multifamily acquisition model:

Property: 180 units, $27M purchase price
Financing: 70% LTV, 6.0% rate, 30-year amort, 5-year IO
Hold Period: 7 years
Current Rent: $1,450/unit/month
Rent Growth: 3% annually
Exit Cap: 5.75%

Model Structure:
1. Summary tab (all key metrics on one page)
2. Assumptions tab (ALL inputs in BLUE text with cell addresses)
3. Operating Pro Forma (10-year, monthly for Year 1)
4. Debt Schedule (monthly amortization)
5. Cash Flow (annual equity cash flows)
6. Sensitivity Analysis (IRR vs Exit Cap and Rent Growth)
7. Returns tab (IRR, NPV, equity multiple calculations)

CRITICAL REQUIREMENTS:
- Use FORMULAS for all calculations - NO hardcoded values
- All assumptions must reference Assumptions tab cells
- Color code per professional standards (blue/black/green)
- Format currency, percentages, and zeros properly
- Ensure no formula errors
- Make model dynamic - changing assumptions should flow through entire model

Verify that changing any assumption (e.g., purchase price, rent growth) 
automatically updates all dependent calculations throughout the model.
```

### Workflow 3: Office Property Lease Analysis

**Input Documents**:
- Abstract of leases (PDF)
- Historical operating statements (Excel)
- Lease expiration schedule (Excel)

**Process**:

#### Step 1: Extract Lease Data (PDF Skill)
```
Extract from lease abstracts:
- Tenant name and credit rating
- Leased square footage
- Base rent ($/SF/year)
- Lease commencement and expiration
- Escalation clauses (fixed % or CPI)
- Free rent periods
- TI allowance provided
- Renewal options and terms
- Percentage rent clauses (retail)
- Expense recovery method (NNN, modified gross, full service)
```

#### Step 2: Build Lease Roll (XLSX Skill)
```
Create comprehensive lease roll in Excel:
- Tenant name
- SF leased
- Current rent $/SF
- Annual rent $
- % of total rent
- Lease start/end dates
- Years remaining
- Annual escalations
- Renewal options
- TI/LC at lease-up

Calculate:
- Weighted average lease term (WALT)
- Weighted average rent $/SF
- Expiration schedule by year
- Rollover risk (% expiring each year)
```

#### Step 3: Analyze Lease-Up Assumptions (CRE Skill)
```
For upcoming expirations, analyze:
- Probability of renewal (by tenant type)
- Expected renewal rent (vs. current rent)
- Downtime between leases
- New TI/LC costs for renewal
- Leasing commissions (typically 4-6% of total rent)
- Time to re-lease if tenant vacates

Model cash flow impact:
- Lost rent during downtime
- TI and LC costs (capex)
- New rent vs. old rent (spread)
- Net cash impact over lease term
```

### Workflow 3: Development Feasibility from Market Study

**Input Documents**:
- Market feasibility study (PDF or Word)
- Site plan (PDF)
- Preliminary budget (Excel)

**Process**:

#### Step 1: Extract Market Data (PDF/DOCX Skills)
```
From market study, extract:
- Market rent by unit type
- Market occupancy rates
- New supply pipeline (units and timing)
- Absorption rates
- Demographic trends
- Employment data
- Comparable rental properties

Synthesize into market assumptions:
- Stabilized rent assumptions
- Lease-up pace (units/month)
- Stabilized occupancy
- Operating expense ratio
```

#### Step 2: Extract Development Budget (XLSX Skill)
```
From preliminary budget:
- Land cost
- Site work costs
- Building hard costs ($/SF)
- Parking costs ($/space)
- Soft costs (architecture, engineering, permits, etc.)
- Financing costs during construction
- Developer fee
- Contingency

Validate:
- Hard cost $/SF vs. market benchmarks
- Soft costs as % of hard costs (typically 12-18%)
- Contingency % (5-10%)
```

#### Step 3: Development Pro Forma Analysis (CRE Skill)
```
Create complete development feasibility:

Construction Phase:
- Monthly draw schedule
- Interest carry during construction
- Total project costs

Lease-Up Phase:
- Unit absorption pace
- Free rent concessions
- Marketing costs
- Lease-up operating deficit

Stabilization:
- Stabilized NOI
- Stabilized value (NOI / cap rate)
- Yield on cost
- IRR from start to stabilization
- Return on total project costs

Risk Assessment:
- Construction cost overrun sensitivity
- Lease-up timing sensitivity
- Market rent sensitivity
- Exit cap rate sensitivity
```

## Troubleshooting Common Issues

### Issue: PDF Text Extraction Errors

**Problem**: OCR produces garbled text or incorrect numbers

**Solutions**:
1. Check if PDF is searchable (try copying text manually)
2. If scanned, ensure high image quality
3. Extract tables separately from body text
4. Manually verify critical numbers (purchase price, NOI)
5. Request original editable files from seller

### Issue: Excel Formula Errors

**Problem**: Imported spreadsheet has #REF!, #VALUE!, or #N/A errors

**Solutions**:
1. Use xlsx skill to identify broken links
2. Replace with hardcoded values if external links
3. Recalculate formulas after import
4. Document which cells were corrected
5. Validate outputs against source document totals

### Issue: Inconsistent Data Across Documents

**Problem**: Offering memo shows different NOI than T-12

**Solutions**:
1. Identify which document is source of truth (usually T-12 for historical)
2. Document discrepancies in analysis
3. Use conservative assumption if material difference
4. Flag for due diligence investigation
5. Request reconciliation from seller

### Issue: Missing Key Information

**Problem**: Documents don't include required data points

**Solutions**:
1. Make reasonable assumptions based on market standards
2. Clearly document all assumptions made
3. Perform sensitivity analysis on assumed values
4. Add to due diligence request list
5. Consider impact on deal risk

### Issue: Protected or Encrypted PDFs

**Problem**: Cannot extract text from password-protected PDFs

**Solutions**:
1. Request password from document provider
2. Use pdf skill's decryption capabilities if password known
3. Request unprotected version
4. Manual data entry as last resort
5. Document any data entry performed manually

## Best Practices

### Data Extraction
1. **Always verify extracted numbers** by spot-checking against source
2. **Document data sources** for every number in your analysis
3. **Flag estimated or assumed values** clearly
4. **Maintain audit trail** of document versions used
5. **Cross-reference multiple sources** when available

### Quality Control
1. **Reconcile totals**: Ensure line items sum correctly
2. **Unit consistency**: Verify $/SF vs. $/unit vs. total $
3. **Date verification**: Confirm which period data represents
4. **Calculation checks**: Recalculate key ratios independently
5. **Reasonability tests**: Compare to market benchmarks

### Documentation
1. **List all source documents** with dates and versions
2. **Note any modifications** made to extracted data
3. **Explain assumptions** when data is missing
4. **Highlight discrepancies** between sources
5. **Provide reconciliation** when numbers differ

### Collaboration
1. **Share extracted data** with team for verification
2. **Version control** all documents and analyses
3. **Clear file naming**: Date_PropertyName_DocumentType
4. **Organized folder structure**: By property and document type
5. **Regular backups**: Don't lose work in progress

## Example: Complete Due Diligence Package Analysis

**Received Documents** (typical acquisition data room):
- Offering memorandum (PDF)
- 3-year operating statements (Excel)
- Current and historical rent rolls (Excel)
- Lease abstracts for major tenants (PDF)
- Property tax bills (PDF)
- Insurance policies (PDF)
- Appraisal report (PDF)
- Phase I environmental report (PDF)
- Property condition assessment (PDF)
- Site survey (PDF)
- Title commitment (PDF)

**Extraction and Analysis Workflow**:

```
PHASE 1: FINANCIAL DOCUMENT REVIEW (xlsx & pdf skills)

1. Operating Statements
   - Extract 3 years of monthly data
   - Calculate trends: revenue growth, expense growth, NOI
   - Identify seasonality patterns
   - Flag any unusual items

2. Rent Rolls  
   - Build comprehensive lease database
   - Track occupancy trends
   - Identify rent growth by vintage
   - Calculate roll-to-market potential

3. Lease Abstracts
   - Extract major tenant terms
   - Build expiration schedule
   - Calculate renewal probability
   - Estimate TI/LC on renewals

PHASE 2: VALIDATION (Cross-reference)

1. Verify offering memo claims vs. actual data
2. Reconcile appraisal value vs. asking price
3. Compare historical performance to pro forma
4. Check property tax amount vs. tax bills
5. Confirm insurance costs

PHASE 3: RISK ASSESSMENT (pdf skills)

1. Environmental Report
   - Identify any recognized environmental conditions
   - Assess remediation costs if any
   - Flag ongoing monitoring requirements

2. Property Condition Assessment
   - Extract immediate repairs needed
   - Calculate 1-year capital needs
   - Estimate 5-year capital needs
   - Assess deferred maintenance

3. Title Report
   - Identify any easements or encumbrances
   - Check for title issues
   - Verify legal description

PHASE 4: INDEPENDENT ANALYSIS (cre-investment-analysis skill)

Using all extracted and validated data:
1. Build independent financial model
2. Stress test key assumptions
3. Perform sensitivity analysis
4. Calculate risk-adjusted returns
5. Generate investment recommendation

PHASE 5: DELIVERABLES

Create complete underwriting package:
- Investment memorandum (docx)
- Financial model (xlsx)
- IC presentation (pptx)
- Due diligence summary (docx)
- Risk assessment matrix (xlsx)
```

This comprehensive approach ensures all available data is properly extracted, validated, and incorporated into a thorough investment analysis.
