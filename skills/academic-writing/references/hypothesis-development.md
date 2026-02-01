# Hypothesis Development

Framework for developing testable predictions in empirical finance, economics, and real estate research.

## Table of Contents
- Theory → Hypothesis Flow
- Three-Part Hypothesis Template
- Hypothesis Patterns
- Hypothesis-Test Mapping
- Common Hypothesis Mistakes

## Theory → Hypothesis Flow

### Standard Structure

```
Theory/Mechanism → Prediction → Testable Hypothesis → Empirical Specification
```

**Example (Information Asymmetry)**:
1. **Theory**: Information asymmetry increases transaction costs (Akerlof 1970)
2. **Prediction**: Better information disclosure should reduce bid-ask spreads
3. **Hypothesis**: Properties with public AI valuations have narrower bid-ask spreads
4. **Test**: Regress spread on AI adoption indicator, controlling for property characteristics

## Three-Part Hypothesis Template

### Part 1: Theoretical Mechanism

State the economic force or friction:
```
[Economic force] operates through [specific channel].
Prior work \citep{author} shows that [established relationship].
In our context, this mechanism implies [directional prediction].
```

**Example**:
```
Information asymmetry between buyers and sellers creates adverse selection in real estate markets.
Prior work \citet{garmaise2007} shows that opacity increases transaction costs.
In our context, this mechanism implies that AI-based valuations, by reducing information asymmetry, should decrease search costs and bid-ask spreads.
```

### Part 2: Directional Prediction

Formal hypothesis statement:
```
**Hypothesis [N]**: [Treatment] is [positively/negatively] associated with [Outcome].
```

**Alternatives**:
- **H1a/H1b format**: For competing predictions
- **Conditional hypotheses**: "If [condition], then [prediction]"
- **Magnitude hypotheses**: "Effect is stronger when [moderator]"

### Part 3: Alternative Mechanisms

Acknowledge competing explanations:
```
However, [alternative mechanism] could generate the opposite prediction.
If [condition holds], we would expect [different result].
Our empirical tests distinguish between these mechanisms by [approach].
```

## Common Hypothesis Patterns

### Pattern 1: Main Effect Hypothesis

```
**H1**: AI adoption increases property valuation accuracy.
```

**Empirical translation**:
```latex
Accuracy_{i,t} = \alpha + \beta_1 AI_{i,t} + \gamma X_{i,t} + \epsilon_{i,t}
```
Predict: $\beta_1 > 0$

### Pattern 2: Heterogeneous Effects Hypothesis

```
**H2**: The effect of AI on accuracy is stronger for complex properties.
```

**Empirical translation**:
```latex
Accuracy_{i,t} = \alpha + \beta_1 AI_{i,t} + \beta_2 (AI_{i,t} \times Complex_i) + \gamma X_{i,t} + \epsilon_{i,t}
```
Predict: $\beta_2 > 0$

### Pattern 3: Mechanism Hypothesis

```
**H3**: AI adoption reduces accuracy through information asymmetry reduction.
```

**Empirical translation**: Mediation analysis
```
Step 1: AI_{i,t} → Accuracy_{i,t}  (H1)
Step 2: AI_{i,t} → InfoAsym_{i,t}
Step 3: InfoAsym_{i,t} → Accuracy_{i,t}  (controlling for AI)
```

### Pattern 4: Threshold/Nonlinear Hypothesis

```
**H4**: AI improves accuracy only after critical adoption threshold.
```

**Empirical translation**:
```latex
Accuracy_{i,t} = \alpha + \beta_1 \mathbb{1}(AI > threshold) + \gamma X_{i,t} + \epsilon_{i,t}
```

## Hypothesis Numbering Conventions

**Sequential numbering**: H1, H2, H3, H4...

**Nested alternatives**:
- H1a: AI increases accuracy
- H1b: AI decreases accuracy (if coordination costs dominate)

**Section-based**:
- H1-H3: Main effects
- H4-H6: Mechanisms
- H7-H9: Heterogeneity

## Connecting Hypotheses to Tables

### Explicit Mapping (Critical for Clarity)

In hypothesis section:
```
We test Hypothesis 1 in Table 2, columns (1)-(3).
Hypothesis 2 is examined in Table 3 using interaction terms.
Table 4 reports mechanism tests for Hypothesis 3.
```

In results section:
```
Table 2 presents tests of Hypothesis 1. Column (1) shows...
The positive coefficient on AI adoption (β = 0.12, p < 0.01) supports Hypothesis 1.
```

### Table Design for Hypothesis Testing

**Table 2 Example (Testing H1)**:
- Column (1): Baseline (AI only)
- Column (2): + Property controls
- Column (3): + Market FE
- Column (4): + Time FE
- Column (5): Full specification

**Table 3 Example (Testing H2 - Heterogeneity)**:
- Column (1): Baseline
- Column (2): AI × Complexity interaction
- Column (3): AI × Information Environment interaction
- Column (4): Triple interaction

## Writing Style Guidelines

### ✅ Clear Hypothesis Statements

```
**H1**: AI adoption increases property valuation accuracy.
```

**Good features**:
- Concise (one sentence)
- Directional (increases/decreases)
- Specific variables
- Testable prediction

### ❌ Vague Hypothesis Statements

```
H1: AI affects markets.
```

**Problems**:
- No direction (increases? decreases?)
- Vague outcome (which aspect of markets?)
- Not directly testable

### ✅ Theory-Grounded Development

```
Information asymmetry theory predicts that transparency reduces adverse selection \citep{akerlof1970}.
AI valuations increase transparency by providing standardized, publicly observable price signals.
Therefore, we hypothesize that AI adoption reduces bid-ask spreads.
```

### ❌ Hypothesis Without Theory

```
We think AI might affect spreads, so we test that.
```

## Advanced Patterns

### Competing Hypotheses (When Theory is Ambiguous)

```
Theory suggests two competing predictions.

**H1a (Information View)**: AI adoption decreases spreads by reducing information asymmetry.

**H1b (Coordination View)**: AI adoption increases spreads by reducing private information incentives.

Our empirical tests discriminate between these views by examining [differential prediction].
```

### Conditional Hypotheses

```
**H2**: If market liquidity is low, the effect of AI on accuracy is stronger.

Formally: $\frac{\partial Accuracy}{\partial AI} > 0$ and $\frac{\partial^2 Accuracy}{\partial AI \partial Liquidity} < 0$
```

### Temporal Dynamics

```
**H3**: The effect of AI on accuracy increases over time as market participants learn.

Test: Estimate time-varying coefficients or include AI × Post interactions.
```

## Common Mistakes to Avoid

### 1. Hypothesis-Results Mismatch
❌ H1 predicts increase, but never test it
✅ Clear mapping: "H1 tested in Table 2, Column 3"

### 2. Tautological Hypotheses
❌ "H1: Treatment affects outcome"
✅ "H1: Treatment increases outcome through [mechanism]"

### 3. Untestable Hypotheses
❌ "H1: AI makes markets better"
✅ "H1: AI increases price efficiency by 10%+"

### 4. Hypotheses in Introduction
❌ Stating H1-H5 in introduction paragraph
✅ Introduction states questions; Section 2 develops formal hypotheses

### 5. Too Many Hypotheses
❌ H1-H15 (overwhelming, unfocused)
✅ H1-H5 (focused, coherent narrative)

## Discipline-Specific Conventions

### Finance
- Connect to asset pricing theory (CAPM, APT, behavioral finance)
- Emphasize risk-return tradeoffs
- Use financial metrics (alpha, Sharpe ratio, volatility)

### Economics
- Ground in utility maximization or equilibrium models
- Discuss welfare implications
- Consider general equilibrium effects

### Real Estate
- Integrate spatial economics and finance perspectives
- Consider location/neighborhood heterogeneity
- Bridge micro (property-level) and macro (market-level) predictions

## Example: Complete Hypothesis Section Outline

```latex
\section{Hypothesis Development}

\subsection{Main Effect: AI and Valuation Accuracy}
[Theory] → [Prediction] → **H1**: AI increases accuracy

\subsection{Mechanism: Information Asymmetry Reduction}
[Channel description] → **H2**: AI reduces info asymmetry → **H3**: Info asymmetry mediates accuracy effect

\subsection{Heterogeneity: Property Complexity}
[Moderating factor] → **H4**: Effect stronger for complex properties

\subsection{Alternative Explanation: Algorithmic Herding}
[Competing mechanism] → **H5**: AI could decrease accuracy through herding

Our empirical strategy, described in Section 3, tests these predictions.
```

## Length Guidelines

- **Total section**: 5-8 pages (for 5-7 hypotheses)
- **Per hypothesis**: ~1 page (theory + prediction + alternatives)
- **Subsections**: Use if >3 hypotheses to organize by theme

## LaTeX Formatting

```latex
\textbf{Hypothesis 1:} AI adoption increases property valuation accuracy.

Formally, we predict $\beta_1 > 0$ in:
\begin{equation}
Accuracy_{i,t} = \alpha + \beta_1 AI_{i,t} + \gamma X_{i,t} + \alpha_i + \alpha_t + \epsilon_{i,t}
\end{equation}
```
