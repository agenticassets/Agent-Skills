# Paper Structure Guide

Section-by-section templates for finance, economics, and real estate research papers.

## Table of Contents
- Introduction (3-4 paragraphs)
- Literature Review (strand organization)
- Hypothesis Development (theory → prediction)
- Data & Sample (construction narrative)
- Methodology (specification justification)
- Results (descriptive → main → robustness → mechanisms)
- Discussion & Conclusion

---

## Introduction Section

### Standard Structure (3-4 paragraphs)

**Paragraph 1: Motivation**
- Start with broad economic question or phenomenon
- Establish importance (market size, policy relevance, theoretical puzzle)
- State core research question
- **Example**: "Institutional ownership of real estate has grown from \$X to \$Y over the past decade, raising questions about whether professional management affects property values differently than individual ownership. Understanding this relationship matters for..."

**Paragraph 2: Gap in Literature**
- What do we NOT know? Why is it hard to answer?
- Identification challenge (endogeneity, selection, measurement)
- **Example**: "Prior research has documented correlations between institutional ownership and property performance (Smith 2020; Jones 2021), but causal identification remains elusive due to selection bias—institutions may choose properties with unobservable growth potential."

**Paragraph 3: This Paper (Contribution)**
- What we do: data + method + identification
- What we find: 1-2 key results with magnitudes
- Why it matters: contribution to literature and practice
- **Example**: "We exploit a regulatory change that exogenously shifted institutional demand for certain property types, creating a natural experiment. Using difference-in-differences with X observations spanning Y years, we find that institutional ownership increases property values by Z% (p<0.01)..."

**Paragraph 4: Roadmap** (optional)
- Brief preview of remaining sections
- **Example**: "The remainder of this paper proceeds as follows. Section 2 reviews related literature. Section 3 develops hypotheses. Section 4 describes data. Section 5 presents empirical strategy. Section 6 reports results. Section 7 concludes."

---

## Literature Review Section

### Organization Patterns

**Pattern 1: Strand Organization** (most common)
```latex
\section{Literature Review}

This paper contributes to three strands of literature.

\subsection{Institutional Ownership and Asset Prices}
Prior research documents that institutional investors affect asset prices through [mechanism].
\citet{author2020} find...
\citet{author2019} show...
Our contribution: [how this paper differs/extends]

\subsection{Real Estate Performance and Management}
Studies of property-level outcomes highlight the role of [factor].
\citet{author2021} examine...
We extend this by [contribution]

\subsection{Methodology: Causal Identification in Real Estate}
Recent work has advanced identification strategies for real estate research.
\citet{author2022} use [method]...
We contribute by [methodological innovation]
```

**Pattern 2: Chronological Development**
- Use when field has evolved in clear stages
- Show progression of ideas over time

**Pattern 3: Debate Organization**
- Use when literature has competing views
- Present both sides, then position your contribution

### Positioning Your Contribution

End each subsection with explicit positioning:
- **Gap**: "However, these studies do not address..."
- **Extension**: "We extend this work by..."
- **Difference**: "In contrast to [prior work], we..."
- **Complement**: "Our findings complement [study] by showing..."

---

## Hypothesis Development Section

### Theory → Testable Prediction Flow

**Structure**:
1. Theoretical mechanism
2. Directional prediction
3. Formal hypothesis statement
4. Alternative prediction (if applicable)

**Example**:

```latex
\subsection{Institutional Ownership and Property Values}

\textbf{Mechanism:} Institutional investors possess superior operational expertise,
access to capital, and economies of scale in property management. These advantages
should translate into higher occupancy rates, better tenant quality, and more
efficient capital expenditure decisions.

\textbf{Prediction:} If operational expertise drives value, properties acquired by
institutional investors should experience valuation increases relative to similar
properties retained by individual owners.

\textbf{Hypothesis 1:} \textit{Institutional ownership increases property values.}

\textbf{Alternative hypothesis:} If institutional investors merely select
properties with unobservable growth potential (selection bias), we would observe
correlations but no causal effect once controlling for selection.
```

### Hypothesis Formatting

**Formal statement style**:
```latex
\textbf{Hypothesis 1 (H1):} \textit{Institutional ownership positively affects property values.}
```

**With directional specificity**:
```latex
\textbf{Hypothesis 2 (H2):} \textit{The positive effect of institutional ownership on property
values is stronger for larger, more complex properties where managerial expertise matters most.}
```

### Theory Section Checklist
- [ ] Mechanism clearly explained (not just correlation prediction)
- [ ] Testable prediction stated (can reject with data)
- [ ] Formal hypothesis numbered (H1, H2, H3...)
- [ ] Alternative explanations considered
- [ ] Hypothesis connects to specific empirical test (Table X, Column Y)

---

## Data & Sample Section

### Construction Narrative Pattern

**Structure**:
1. Data sources (where data comes from)
2. Sample construction (filters and restrictions)
3. Variable construction (key measures)
4. Sample characteristics (Table 1 preview)

**Example**:

```latex
\section{Data and Sample}

\subsection{Data Sources}
We construct our sample from three primary sources. Property-level data come from
CoStar (commercial real estate) covering the period 2010-2023. Ownership information
is from property deeds and title records obtained through [source]. Financial data
for publicly traded REITs come from Compustat.

\subsection{Sample Construction}
We begin with the universe of X commercial properties in Y markets. We apply several
filters to ensure data quality: (1) properties with complete transaction history,
(2) markets with at least Z properties to support fixed effects, (3) properties
owned by identifiable entities (excludes trusts and complex structures).

These restrictions yield a final sample of N property-year observations representing
M unique properties across P markets from [START] to [END].

\subsection{Variable Construction}

\textit{Institutional Ownership.} We classify owners as institutional if they meet
any of the following criteria: (1) publicly traded REIT, (2) private equity real
estate fund with AUM > \$X, (3) pension fund or endowment. This definition captures
Q\% of properties in our sample.

\textit{Property Values.} Our primary outcome is log(appraised value) from annual
tax assessments. We validate these using transaction prices for the subset of
properties that trade during the sample period (correlation = 0.XX, see Appendix).

\subsection{Sample Characteristics}
Table \ref{tab:summary_statistics} presents descriptive statistics. The average property
in our sample is [characteristics]. Institutional ownership increased from X\% in 2010
to Y\% in 2023, reflecting growing institutionalization of real estate markets.
```

### Variable Definition Table

Include formal variable definitions in Appendix:
```latex
\begin{longtable}{p{4cm}p{10cm}}
\caption{Variable Definitions} \label{tab:variables} \\
\toprule
\textbf{Variable} & \textbf{Definition} \\
\midrule
\endfirsthead

\textit{Dependent Variables} & \\
Property Value & Log of appraised property value from tax assessor \\
Occupancy Rate & Percentage of leasable space occupied \\
\\
\textit{Treatment Variables} & \\
Institutional Owner & Indicator = 1 if property owned by institution \\
...
\end{longtable}
```

---

## Methodology Section

### Empirical Specification Structure

**Standard pattern**:
1. Baseline specification (equation)
2. Identification strategy
3. Fixed effects rationale
4. Standard error clustering justification
5. Threats to validity

**Example**:

```latex
\section{Empirical Strategy}

\subsection{Baseline Specification}
We estimate the effect of institutional ownership on property values using the
following fixed effects model:

\begin{equation}
\log(Value)_{i,m,t} = \beta_1 Institutional_{i,t} + \gamma X_{i,t} + \alpha_i + \alpha_{m,t} + \epsilon_{i,t}
\end{equation}

where $\log(Value)_{i,m,t}$ is the log appraised value of property $i$ in market $m$
at time $t$. $Institutional_{i,t}$ is an indicator for institutional ownership.
$X_{i,t}$ includes time-varying property characteristics (age, size, renovations).
$\alpha_i$ are property fixed effects controlling for time-invariant unobservables.
$\alpha_{m,t}$ are market×year fixed effects absorbing local demand shocks.

\subsection{Identification Strategy}
Property fixed effects ($\alpha_i$) address selection bias by comparing the same
property before and after institutional acquisition. Market×year fixed effects
($\alpha_{m,t}$) control for local market trends that might correlate with both
institutional entry and property values.

The key identifying assumption is that conditional on fixed effects, the timing of
institutional acquisition is uncorrelated with property-specific value trajectories.
We validate this using event study plots showing no pre-treatment trends
(Figure \ref{fig:event_study}).

\subsection{Standard Errors}
We cluster standard errors at the property level to account for serial correlation
in outcome variables. Results are robust to two-way clustering by property and year
(Table \ref{tab:robustness}).
```

### Identification Checklist
- [ ] Equation clearly displays specification
- [ ] All variables defined (including subscripts)
- [ ] Fixed effects justified economically
- [ ] Identifying assumption stated explicitly
- [ ] Validation provided (pre-trends, placebo, etc.)

---

## Results Section Structure

### Progressive Organization

**Standard sequence**:
1. **Table 1**: Descriptive statistics
2. **Table 2**: Main results (baseline → controls → full spec)
3. **Table 3**: Heterogeneity (interactions)
4. **Table 4**: Robustness (alternative specs)
5. **Table 5**: Mechanisms (why effect occurs)

### Table-by-Table Walkthrough

See `results-discussion.md` for detailed table discussion patterns.

**Key principles**:
- **Coefficient interpretation**: Statistical significance + economic magnitude
- **Hypothesis mapping**: "This supports H1..."
- **Cross-table consistency**: "The effect remains stable across Tables 2-4..."
- **Build narrative**: Each table adds a piece to the story

---

## Discussion & Conclusion

### Discussion Section (when included)

**Structure**:
1. Interpret findings in economic terms
2. Acknowledge limitations
3. Discuss policy/practical implications
4. Suggest future research

**Example limitation acknowledgment**:
```latex
Several limitations warrant mention. First, our institutional ownership measure
may not capture informal management arrangements. Second, while property fixed
effects address selection bias, they rely on properties that change ownership
during the sample period. Third, we focus on commercial real estate; effects may
differ for residential properties.
```

### Conclusion Section

**Standard pattern** (2-3 paragraphs):

**Paragraph 1**: Restate research question and key finding
```latex
This paper examines whether institutional ownership affects property values. Using
a sample of X properties from Y to Z, we find that institutional ownership increases
property values by A%, an economically meaningful effect representing \$B per property.
```

**Paragraph 2**: Contribution summary
```latex
Our findings contribute to literature on institutional investors and real estate markets.
We provide causal evidence that [contribution 1], extend prior work by [contribution 2],
and demonstrate [methodological contribution].
```

**Paragraph 3**: Future research (without undermining current paper)
```latex
Future research could explore the mechanisms through which institutions create value,
examine heterogeneity across property types and markets, or investigate long-term
effects on market structure.
```

**Avoid in conclusions**:
- ❌ "More research is needed" (undermines your contribution)
- ❌ New results not discussed earlier
- ❌ Overgeneralizing beyond your sample
- ✅ Concise summary of what you've demonstrated
