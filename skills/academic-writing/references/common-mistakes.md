# Common Academic Writing Mistakes

Frequent pitfalls in finance, economics, and real estate research manuscripts and how to avoid them.

## Table of Contents
- Introduction Mistakes
- Hypothesis Mistakes
- Results Section Mistakes
- Methodology Mistakes
- Data Section Mistakes
- Tables and Figures Mistakes

## Introduction Mistakes

### ❌ Mistake 1: Vague or Missing Contribution

**Problem**:
```
This paper studies commercial real estate markets.
We examine the effect of technology on property values.
```

**Why it's bad**: Doesn't tell reviewers what's new or why it matters

**✅ Fix**:
```
This paper provides first evidence that AI-based property valuations increase pricing efficiency by 12% but widen bid-ask spreads by 8 basis points in commercial real estate markets.
Our findings contribute to the literature on information technology and asset pricing by documenting both benefits and frictions from algorithmic intermediation.
```

### ❌ Mistake 2: Literature Review in Introduction

**Problem**: Introduction spends 2 pages reviewing prior work before stating research question

**Why it's bad**: Reviewers want to know your contribution first, then see how it relates to literature

**✅ Fix**:
- Paragraph 1-2: Motivation and gap
- Paragraph 3: Your contribution
- Paragraph 4: Roadmap
- Section 2: Detailed literature review

### ❌ Mistake 3: Stating Hypotheses in Introduction

**Problem**:
```
We predict that AI will increase accuracy (H1).
We also hypothesize that effects are stronger for complex properties (H2).
```

**Why it's bad**: Hypotheses belong in Section 2 after developing theory

**✅ Fix**:
```
Introduction: We examine whether AI affects property valuation accuracy.
Section 2: [After theory development] H1: AI increases accuracy.
```

## Hypothesis Development Mistakes

### ❌ Mistake 4: Untestable Hypotheses

**Problem**:
```
H1: AI improves markets.
H2: Technology matters for real estate.
```

**Why it's bad**: Too vague to test empirically

**✅ Fix**:
```
H1: AI adoption increases property valuation accuracy by reducing information asymmetry.
H2: The effect of AI on accuracy is 50% larger for institutionally owned properties than retail properties.
```

### ❌ Mistake 5: Hypotheses Without Theory

**Problem**: Stating H1-H5 without explaining why these predictions follow from theory

**Why it's bad**: Hypotheses must be theory-driven, not ad hoc

**✅ Fix**: For each hypothesis:
1. State theoretical mechanism
2. Derive prediction
3. Formalize as testable hypothesis

### ❌ Mistake 6: Too Many Hypotheses

**Problem**: H1 through H15 covering every possible relationship

**Why it's bad**: Unfocused, appears like data mining

**✅ Fix**: Focus on 3-6 core hypotheses organized thematically

## Results Section Mistakes

### ❌ Mistake 7: Describing Tables Instead of Interpreting

**Problem**:
```
Table 2 shows the results.
Column 1 has the baseline.
Column 2 adds controls.
The coefficient on AI is positive.
```

**Why it's bad**: Just reading table structure, not explaining findings

**✅ Fix**:
```
Table 2 tests Hypothesis 1.
Column 1 shows that AI adoption increases valuation accuracy by 12 percentage points (t = 4.23, p < 0.01).
This effect persists when adding property controls (Column 2) and fixed effects (Column 3).
The magnitude represents 0.8 standard deviations, equivalent to reducing forecast error from $2.4M to $2.1M for the median property.
```

### ❌ Mistake 8: Missing Economic Magnitudes

**Problem**:
```
The coefficient on AI is 0.123 and statistically significant (p < 0.01).
```

**Why it's bad**: Reviewers want to know if effect is economically meaningful

**✅ Fix**:
```
The coefficient on AI is 0.123 (p < 0.01), representing a 12 percentage point increase in accuracy.
This is economically large: a one standard deviation increase in AI adoption reduces valuation error by $300,000 for the median property, representing 1.5% of property value.
```

### ❌ Mistake 9: No Hypothesis-Result Mapping

**Problem**: Results section never explicitly connects findings to hypotheses

**Why it's bad**: Unclear which table tests which hypothesis

**✅ Fix**:
```
Table 2 tests Hypothesis 1. The positive coefficient (β = 0.12, p < 0.01) supports our prediction that AI increases accuracy.
Table 3 examines Hypothesis 2. The interaction term AI × Complexity is positive and significant (β = 0.08, p < 0.05), consistent with stronger effects for complex properties.
```

### ❌ Mistake 10: Ignoring Null Results

**Problem**: Only discussing significant findings, skipping over insignificant coefficients

**Why it's bad**: Reviewers notice omissions and suspect p-hacking

**✅ Fix**:
```
We find no evidence that AI affects trading volume (Column 4, p = 0.42).
This null result suggests that efficiency gains do not translate to increased liquidity, consistent with the fixed costs of transacting in commercial real estate.
```

## Methodology Section Mistakes

### ❌ Mistake 11: Generic Methods Description

**Problem**:
```
We use regression analysis.
We control for relevant variables.
We cluster standard errors.
```

**Why it's bad**: Doesn't explain your specific identification strategy

**✅ Fix**:
```
Our identification strategy exploits staggered AI model deployment across metropolitan areas from 2016-2020.
We estimate difference-in-differences models comparing properties in early-adopting versus late-adopting markets:

Y_{i,m,t} = α + β Post_{m,t} + γ X_{i,t} + α_i + α_t + ε_{i,m,t}

where Post_{m,t} indicates AI availability in market m at time t.
We cluster standard errors at the MSA level to account for within-market correlation.
```

### ❌ Mistake 12: Missing Identification Discussion

**Problem**: Never addressing endogeneity or selection concerns

**Why it's bad**: Reviewers will raise these concerns anyway

**✅ Fix**: Explicitly discuss:
- Potential endogeneity concerns
- Your identification strategy
- Why it generates quasi-random variation
- Alternative explanations and how you rule them out

## Data Section Mistakes

### ❌ Mistake 13: Vague Data Description

**Problem**:
```
We obtained data from industry sources.
The sample covers recent years.
We have information on properties.
```

**Why it's bad**: Not replicable, raises concerns about data quality

**✅ Fix**:
```
We obtain proprietary transaction data from CoStar covering all commercial office sales in the top 50 MSAs from 2015-2023.
The sample includes 45,281 transactions representing $340 billion in aggregate value.
For each property, we observe sale price, building characteristics (square footage, age, class), location (census tract), and buyer/seller identities.
```

### ❌ Mistake 14: No Sample Selection Discussion

**Problem**: Filtering data without explaining why or showing attrition

**Why it's bad**: Reviewers worry about selection bias

**✅ Fix**:
```
We begin with 78,450 transactions (Table 1, Panel A).
We exclude distressed sales (6,234 observations), portfol portfolio transactions (8,912), and properties with missing characteristic data (18,023).
The final sample includes 45,281 arm's-length transactions.
Appendix Table A1 shows that excluded properties are smaller but similar on other observables.
```

## Table and Figure Mistakes

### ❌ Mistake 15: Poor Table Formatting

**Problem**:
- Missing significance stars
- No standard errors
- Unclear variable labels
- Missing table notes

**✅ Fix**: Use professional formatting
```latex
\begin{table}[ht!]
\centering
\caption{Effect of AI on Valuation Accuracy}
\label{tab:main}
\begin{tabular}{lcccc}
\toprule
& (1) & (2) & (3) & (4) \\
& Baseline & + Controls & + Property FE & + MSA×Year FE \\
\midrule
AI Adoption & 0.123*** & 0.118*** & 0.105*** & 0.097*** \\
& (0.028) & (0.026) & (0.024) & (0.023) \\
\\
Controls & No & Yes & Yes & Yes \\
Property FE & No & No & Yes & Yes \\
MSA×Year FE & No & No & No & Yes \\
\midrule
Observations & 45,281 & 45,281 & 45,281 & 45,281 \\
R-squared & 0.124 & 0.287 & 0.534 & 0.612 \\
\bottomrule
\end{tabular}
\parbox{\linewidth}{\footnotesize
\textit{Notes}: This table reports OLS estimates of the effect of AI adoption on property valuation accuracy.
The dependent variable is accuracy, measured as 1 - |forecasted price - actual price| / actual price.
AI Adoption is an indicator for properties valued using AI models.
Standard errors (in parentheses) are clustered at the MSA level.
*** p<0.01, ** p<0.05, * p<0.10.
}
\end{table}
```

### ❌ Mistake 16: Figures Without Context

**Problem**: Dropping in a figure without explaining what it shows or why it matters

**✅ Fix**:
```
Figure 2 plots event study coefficients from Equation (2).
The pre-treatment coefficients are small and statistically insignificant, supporting parallel trends.
After AI adoption (period 0), accuracy increases sharply and remains elevated.
The effect stabilizes after 8 quarters, suggesting rapid market adjustment.
```

## Writing Style Mistakes

### ❌ Mistake 17: Passive Voice Overuse

**Problem**:
```
It was found that AI affects accuracy.
The data were obtained from CoStar.
The results are shown in Table 2.
```

**✅ Fix**:
```
We find that AI affects accuracy.
We obtain data from CoStar.
Table 2 shows the results.
```

### ❌ Mistake 18: Hedge Overload

**Problem**:
```
The results seem to possibly suggest that AI might perhaps affect accuracy to some extent.
```

**✅ Fix**:
```
The results suggest that AI affects accuracy.
```

### ❌ Mistake 19: Unexplained Acronyms

**Problem**:
```
We use CMBS data to examine CRE transactions by REITs.
```

**Why it's bad**: Not everyone knows every acronym

**✅ Fix**:
```
We use Commercial Mortgage-Backed Securities (CMBS) data to examine Commercial Real Estate (CRE) transactions by Real Estate Investment Trusts (REITs).
```

## Conclusion Mistakes

### ❌ Mistake 20: Just Summarizing Without Contributions

**Problem**:
```
This paper examined AI and real estate.
We found that AI affects accuracy.
Future research could study other markets.
```

**✅ Fix**:
```
This paper provides first evidence that AI-based property valuations create a tradeoff between efficiency and liquidity in commercial real estate markets.
While AI increases pricing efficiency by 12%, it widens bid-ask spreads by 8 basis points, consistent with reduced private information gathering.

Our findings contribute to three literatures.
First, we extend work on information technology and asset markets by documenting both benefits and costs of algorithmic intermediation in illiquid markets.
Second, we provide micro-level evidence on AI's market impact, complementing aggregate studies.
Third, we identify a novel channel—reduced private information incentives—through which transparency can paradoxically harm liquidity.

These results inform policy debates about algorithmic disclosure requirements.
While transparency benefits buyers through better information, it may harm sellers through reduced liquidity.
Optimal regulation must balance these tradeoffs.
```

## Citation Mistakes

### ❌ Mistake 21: Citation Format Inconsistency

**Problem**: Mixing citation styles within paper
```
Smith (2020) finds X.
Y is documented in (Jones, 2021).
Brown et al. [2019] show Z.
```

**✅ Fix**: Use consistent LaTeX citation commands
```
\citet{smith2020} finds X.
Y is documented by \citet{jones2021}.
\citet{brown2019} show Z.
```

### ❌ Mistake 22: Missing Citations

**Problem**: Making claims without citing supporting evidence
```
Prior work shows that information affects prices.
Real estate markets are illiquid.
```

**✅ Fix**:
```
Prior work shows that information affects prices \citep{grossman1980, glosten1985}.
Real estate markets are among the least liquid asset classes \citep{garmaise2007}.
```

## Robustness Section Mistakes

### ❌ Mistake 23: Cherry-Picking Robustness Tests

**Problem**: Only showing robustness tests that support main findings

**Why it's bad**: Reviewers suspect specification searching

**✅ Fix**: Show full range of robustness tests
```
Table 6 reports robustness tests.
Results are robust to alternative accuracy measures (Column 1), excluding crisis periods (Column 2), and controlling for property age trends (Column 3).
However, the effect attenuates when restricting to properties sold multiple times (Column 4), suggesting some role for unobserved heterogeneity.
```

### ❌ Mistake 24: Robustness Tests Without Explanation

**Problem**:
```
Table 6 shows robustness tests.
Results are robust.
```

**✅ Fix**:
```
Table 6 addresses three potential concerns.
Column 1 uses alternative accuracy measures to ensure results are not driven by our specific metric.
Column 2 excludes the 2008-2009 financial crisis to rule out crisis-specific effects.
Column 3 controls for property age trends to address concerns about vintage confounds.
Results are consistent across all specifications.
```

## Quick Reference: Common Mistakes Checklist

Before submission, check:

**Introduction**:
- [ ] Clear contribution statement (Paragraph 3)
- [ ] No hypotheses stated (save for Section 2)
- [ ] Literature not overwhelming (save details for Section 2)

**Hypotheses**:
- [ ] Theory-driven (not ad hoc)
- [ ] Testable and directional
- [ ] 3-6 hypotheses (not 15)

**Methods**:
- [ ] Specific identification strategy
- [ ] Endogeneity concerns addressed
- [ ] Standard errors clustered appropriately

**Data**:
- [ ] Clear data sources
- [ ] Sample selection explained
- [ ] Attrition analysis if applicable

**Results**:
- [ ] Interpret, don't just describe
- [ ] Report economic magnitudes
- [ ] Map hypotheses to tables explicitly
- [ ] Discuss null results

**Tables**:
- [ ] Professional formatting (booktabs)
- [ ] Significance stars and standard errors
- [ ] Clear variable labels
- [ ] Comprehensive notes

**Writing**:
- [ ] Active voice ("We find")
- [ ] Moderate hedging (not excessive)
- [ ] One sentence per line
- [ ] Acronyms defined on first use

**Citations**:
- [ ] Consistent LaTeX commands (\citet, \citep)
- [ ] All claims supported by citations
- [ ] Bibliography complete and formatted

**Conclusion**:
- [ ] Contributions clearly stated
- [ ] Limitations acknowledged
- [ ] Policy/practical implications discussed
