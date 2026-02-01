# Writing Conventions

Academic writing style guide for finance, economics, and real estate research.

## Table of Contents
- Voice and Tone
- Tense Usage
- Technical Writing Standards
- LaTeX-Specific Conventions
- Discipline-Specific Style
- Common Phrasing Patterns

## Voice and Tone

### Active vs Passive Voice

**✅ Prefer active voice** (especially in finance/economics)

```
We estimate the effect of AI on accuracy.  [Active - Clear]
The effect of AI on accuracy is estimated.  [Passive - Weak]
```

**When passive is acceptable**:
- Describing established facts: "REITs are regulated under the Investment Company Act"
- Methods section: "Standard errors are clustered at the MSA level"
- When actor is unknown or irrelevant: "The property was sold in 2015"

### First Person ("We")

**Modern academic convention**: Use "we" freely

```
✅ We find that AI adoption increases accuracy by 12%.
✅ We test this prediction in Table 3.
✅ Our results suggest that information asymmetry mediates this effect.

❌ This paper finds that...  [Dated, awkward]
❌ It is shown that...  [Passive, unclear]
```

**Exception**: Avoid "I" in co-authored papers (use "we" even for single-author in some journals)

## Hedging and Certainty

### Appropriate Hedging

**Use hedging for**:
- Interpretation: "This finding *suggests* that information frictions matter"
- Causality claims: "The results are *consistent with* a causal effect"
- Generalization: "This effect *appears* to hold across markets"

**Common hedging words**:
- suggest, indicate, appear, seem
- may, might, could
- consistent with, in line with
- broadly, generally, typically

### Avoid Over-Hedging

```
❌ Our results might possibly suggest that AI could perhaps affect accuracy.
✅ Our results suggest that AI affects accuracy.
```

### When to Be Direct

**State facts directly**:
```
✅ The sample includes 45,000 properties.
✅ Table 2 reports summary statistics.
✅ REITs face mandatory distribution requirements.
```

**Strong empirical findings**:
```
✅ We find a statistically significant positive effect.
✅ This coefficient is economically large.
```

## Common Verb Patterns

### Describing Your Work

**What you do**:
- examine, investigate, analyze, test, estimate
- document, demonstrate, show, provide evidence
- explore, study, assess, evaluate

**What you find**:
- find, show, document, demonstrate
- observe, detect, identify, uncover
- report, present, obtain

**What results indicate**:
- suggest, indicate, imply, support
- are consistent with, align with, corroborate
- provide evidence for, lend support to

### Describing Prior Literature

**Neutral description**:
```
\citet{smith2020} examines the effect of...
\citet{jones2021} documents that...
\citet{brown2019} shows evidence of...
```

**Contrasting/building**:
```
While \citet{smith2020} focuses on X, we examine Y.
In contrast to \citet{jones2021}, we find...
Extending \citet{brown2019}, we test...
```

## Sentence Structure

### One Sentence Per Line (Critical)

**Why**: Version control, git diffs, collaborative editing

```latex
✅ CORRECT:
We test this prediction using property-level transaction data.
The sample covers 45,000 commercial office buildings from 2015 to 2023.
Our identification strategy exploits staggered AI model deployment.

❌ WRONG:
We test this prediction using property-level transaction data. The sample
covers 45,000 commercial office buildings from 2015 to 2023. Our
identification strategy exploits staggered AI model deployment.
```

### Vary Sentence Length

```
✅ Mix short and long:
We find a positive effect. This result is robust to alternative specifications and sample restrictions. It holds.

❌ All long or all short:
We find a positive effect that is robust to alternative specifications and sample restrictions and holds across subsamples. [Too long]

We find a positive effect. It is robust. It holds. [Too choppy]
```

### Avoid Sprawling Sentences

```
❌ We estimate the effect of AI adoption on property valuation accuracy using proprietary data from a major valuation platform covering 45,000 commercial office buildings across 150 metropolitan areas from 2015 to 2023, exploiting staggered AI model deployment as a quasi-natural experiment with a difference-in-differences identification strategy. [78 words - too long]

✅ We estimate the effect of AI adoption on property valuation accuracy.
We use proprietary data from a major valuation platform covering 45,000 commercial office buildings across 150 metropolitan areas from 2015 to 2023.
Our identification strategy exploits staggered AI model deployment in a difference-in-differences framework. [Split into 3 clear sentences]
```

## Precision and Clarity

### Be Specific

```
❌ Vague: AI affects markets.
✅ Specific: AI adoption increases price efficiency by 12% but widens bid-ask spreads by 8 basis points.

❌ Vague: The sample is large.
✅ Specific: The sample includes 45,000 properties representing $340 billion in transaction value.

❌ Vague: Prior work studies this topic.
✅ Specific: \citet{garmaise2007} documents information asymmetry effects in commercial real estate using 1990s transactions data.
```

### Avoid Ambiguous Pronouns

```
❌ AI valuations affect prices. This increases efficiency.  [What does "this" refer to?]

✅ AI valuations affect prices. This price impact increases market efficiency.
✅ AI valuations affect prices, which increases market efficiency.
```

### Define Terms on First Use

```
✅ We focus on Real Estate Investment Trusts (REITs), which are pass-through entities required to distribute 90% of taxable income.

✅ We measure liquidity using the Amihud (2002) illiquidity ratio, defined as the daily ratio of absolute return to dollar volume.
```

## LaTeX-Specific Conventions

### Math and Equations

**Inline math** for simple expressions:
```latex
The coefficient $\beta_1$ captures the treatment effect.
```

**Display equations** for key specifications:
```latex
\begin{equation}
Y_{i,t} = \alpha + \beta_1 Treatment_{i,t} + \gamma X_{i,t} + \alpha_i + \alpha_t + \epsilon_{i,t}
\end{equation}
```

**Number important equations**:
```latex
\begin{equation} \label{eq:main}
Y_{i,t} = \alpha + \beta_1 Treatment_{i,t} + \epsilon_{i,t}
\end{equation}

As shown in Equation \ref{eq:main}, we estimate...
```

### Cross-References

**Always use \ref{} for cross-references**:
```latex
✅ Table \ref{tab:summary} reports summary statistics.
✅ Figure \ref{fig:event} plots event study coefficients.
✅ As discussed in Section \ref{sec:data}, we obtain...

❌ Table 1 reports... [Hard-coded - breaks if you reorder tables]
```

### Citations

**In-text**:
```latex
\citet{smith2020} finds...          % Smith (2020) finds...
Recent work \citep{smith2020}...    % Recent work (Smith, 2020)...
```

**Multiple citations** (order chronologically or alphabetically):
```latex
\citep{smith2018, jones2019, brown2021}
```

## Numbers and Magnitudes

### Report Key Numbers

**Always report**:
1. **Point estimate**: "AI increases accuracy by 12%"
2. **Statistical significance**: "p < 0.01" or "t = 4.23"
3. **Economic magnitude**: "This represents a 0.8 standard deviation change"

**Example**:
```
We find that AI adoption increases valuation accuracy by 12 percentage points (t = 4.23, p < 0.01).
This effect represents 0.8 standard deviations and is equivalent to reducing forecast error from $2.4M to $2.1M for the median property.
```

### Number Formatting

**Large numbers**: Use commas or words
```
✅ 45,000 properties
✅ forty-five thousand properties
❌ 45000 properties
```

**Percentages vs percentage points**:
```
✅ Accuracy increases by 12 percentage points (from 60% to 72%)
❌ Accuracy increases by 12% (ambiguous - 12% of what?)
```

**Decimal precision**: Match precision to context
```
✅ Coefficient: 0.123 (3 decimals for regression output)
✅ Percentage: 12.3% (1 decimal usually sufficient)
✅ Dollar amounts: $2.4 million (round large numbers)
```

## Common Mistakes to Avoid

### 1. Overuse of "However"

```
❌ We find X. However, Y. However, Z. However... [Too many "however"s]

✅ We find X. Nevertheless, Y. By contrast, Z. [Vary transition words]
```

**Alternatives**: Nevertheless, nonetheless, in contrast, conversely, on the other hand, yet

### 2. Weak Opening Sentences

```
❌ In this section, we discuss the results.
❌ Table 2 shows the results.

✅ We find a statistically significant positive effect of AI on accuracy.
✅ AI adoption increases valuation accuracy by 12% (p < 0.01).
```

### 3. Redundancy

```
❌ We jointly collaborate together to estimate...
✅ We collaborate to estimate... OR We jointly estimate...

❌ The results clearly demonstrate and show that...
✅ The results demonstrate that... OR The results show that...

❌ First, we first examine...
✅ First, we examine... OR We first examine...
```

### 4. Nominalizations (Turning Verbs into Nouns)

```
❌ We conduct an examination of the effect...
✅ We examine the effect...

❌ We make an assumption that...
✅ We assume that...

❌ We provide an analysis of...
✅ We analyze...
```

### 5. Unclear Antecedents

```
❌ AI affects prices and liquidity. This is important. [What is "this"?]

✅ AI affects prices and liquidity. This dual impact is important for market efficiency.
✅ AI affects prices and liquidity, both of which matter for market efficiency.
```

## Discipline-Specific Conventions

### Finance

**Emphasis**:
- Asset pricing implications
- Risk-return tradeoffs
- Market efficiency
- Trading strategies and portfolio implications

**Common phrases**:
- "economically significant"
- "risk-adjusted returns"
- "abnormal performance"
- "market microstructure"

### Economics

**Emphasis**:
- Causal identification
- Welfare implications
- Policy relevance
- External validity

**Common phrases**:
- "identification strategy"
- "exogenous variation"
- "general equilibrium effects"
- "welfare consequences"

### Real Estate

**Bridge finance and urban economics**:
- Spatial aspects (location, agglomeration)
- Market segmentation
- Information frictions specific to real estate
- Institutional features (REITs, CMBS, property types)

**Common phrases**:
- "property-level characteristics"
- "location fixed effects"
- "commercial real estate markets"
- "capitalization rates"

## Transition Patterns

### Between Paragraphs

**Sequential**:
- Next, Moreover, Additionally, Furthermore

**Contrast**:
- However, Nevertheless, In contrast, Conversely, On the other hand

**Causal**:
- Therefore, Thus, Consequently, As a result, Hence

**Example/Illustration**:
- For example, For instance, Specifically, In particular

### Within Sections

**Roadmap sentences**:
```
We proceed in three steps.
First, we establish...
Second, we test...
Third, we examine...
```

**Signposting**:
```
Turning to robustness tests, we...
To assess mechanisms, we...
We next explore heterogeneity by...
```

## Checklist for Each Section

### Introduction
- [ ] Active voice ("We examine...")
- [ ] Clear contribution statement
- [ ] Specific magnitudes reported
- [ ] No hypotheses (save for Section 2)

### Hypothesis Development
- [ ] Theory clearly explained
- [ ] Directional predictions stated
- [ ] Hypotheses numbered and formatted
- [ ] Alternative mechanisms acknowledged

### Results
- [ ] Each table explicitly discussed
- [ ] Coefficients interpreted with magnitudes
- [ ] Statistical significance reported
- [ ] Economic significance discussed
- [ ] Hypothesis-result mapping clear

### Conclusion
- [ ] Findings summarized clearly
- [ ] Contributions restated
- [ ] Limitations acknowledged
- [ ] Future research directions suggested
