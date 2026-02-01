# Referee Response Guide

Response frameworks for common reviewer concerns in finance, economics, and real estate research.

## Table of Contents
- Response Letter Structure
- Common Reviewer Objections
- Response Tone Guidance
- Substantive Revision Strategies

## Response Letter Structure

```latex
% Standard point-by-point format
\textbf{Reviewer [X] Comment [Y]:} [Verbatim quote or accurate paraphrase]

\textbf{Response:} [Your response - acknowledge, explain, describe changes]

\textbf{Changes Made:} [Specific additions/revisions]

\textbf{Location:} [Section/page/table where changes appear]
```

---

## Tone and Approach

### General Principles

**Acknowledge validity**: Start by recognizing the reviewer's point
```latex
The reviewer raises an important question about [concern]...
We appreciate the reviewer's suggestion to [improvement]...
This is a valid concern that deserves careful attention...
```

**Explain, don't defend**: Focus on clarification over justification
```latex
% GOOD
We have clarified our identification strategy in the revised manuscript...
% AVOID
Our identification strategy was already clearly explained...
```

**Be specific about changes**: Don't just say "we revised" — show where
```latex
We have added Table X (page Y) showing [specific content]. We have also expanded
the discussion in Section Z (pages A-B, paragraphs 2-3) to address [concern].
```

**Respectful disagreement**: When you disagree, explain why gently
```latex
While we appreciate this suggestion, we respectfully maintain our original approach
for the following reasons: [substantive justification]. However, we have added
discussion of the alternative in [location] to acknowledge this perspective.
```

---

## Common Referee Concerns and Response Frameworks

### 1. Endogeneity / Identification Concerns

**Typical comment**: "Treatment is endogenous. Institutions may select properties with unobservable growth potential."

**Response framework**:
```latex
\textbf{Response:} We acknowledge that selection bias is a central identification
challenge in this setting. Our empirical strategy addresses this through three
complementary approaches:

\textbf{First}, property fixed effects compare the same property before and after
institutional acquisition, controlling for time-invariant unobservables that might
correlate with both institutional selection and property values.

\textbf{Second}, event study analysis (new Figure X) shows no pre-treatment trends
in outcomes, validating the parallel trends assumption underlying our difference-in-
differences identification.

\textbf{Third}, we exploit exogenous variation in institutional demand created by
[regulatory change/natural experiment]. Specifically, [explain instrument/shock].
Results using this quasi-experimental variation (new Table Y) confirm our main findings.

\textbf{Changes Made:} We have added Figure X showing event study estimates, Table Y
presenting IV/quasi-experimental results, and substantially expanded the identification
discussion in Section 4.2 (pages Z-W).

\textbf{Location:} Section 4.2 (identification strategy), Figure X (event study),
Table Y (IV results), Online Appendix A (additional robustness checks).
```

**Additional tactics**:
- **Bounds analysis**: Oster (2019) approach for selection on unobservables
- **Placebo outcomes**: Show null effects where theory predicts none
- **Falsification tests**: Pre-treatment periods, unaffected groups

### 2. Sample Selection Bias

**Typical comment**: "Your sample is limited to [subset]. Results may not generalize."

**Response framework**:
```latex
\textbf{Response:} The reviewer correctly notes that our sample focuses on [subset].
This restriction was imposed because [data availability / identification strategy /
institutional context]. We address generalizability through two analyses:

\textbf{First}, we compare observable characteristics of our sample to the broader
population using [benchmark data]. New Table X shows that our sample is representative
on [key dimensions], though [acknowledged differences].

\textbf{Second}, we re-estimate our main specification on alternative subsamples:
[broader sample / different markets / different time period]. New Table Y shows that
treatment effects are qualitatively similar across subsamples, ranging from [lower bound]
to [upper bound], with our main estimate falling mid-range.

\textbf{Changes Made:} Added Table X (sample representativeness), Table Y (alternative
samples), and discussion in Section 3.3 (pages A-B) addressing generalizability.

\textbf{Location:} Section 3.3 (sample discussion), Table X, Table Y, Online Appendix B.
```

### 3. Alternative Explanations

**Typical comment**: "Effect could be driven by [alternative mechanism] rather than [your proposed mechanism]."

**Response framework**:
```latex
\textbf{Response:} This alternative explanation is plausible and warrants investigation.
We test it directly through several analyses:

\textbf{Mechanism test 1}: If [alternative mechanism] drives the effect, we should
observe [testable implication]. New Table X examines [proxy for alternative mechanism].
We find [result], [supporting/inconsistent with] the alternative explanation.

\textbf{Mechanism test 2}: We exploit heterogeneity in [factor related to alternative
mechanism]. If the alternative is correct, effects should be [stronger/weaker] when
[condition]. New Table Y shows [pattern], which [supports/contradicts] this prediction.

\textbf{Direct comparison}: Table Z presents horse-race regressions including proxies
for both our proposed mechanism and the alternative. We find [result], suggesting
[interpretation].

\textbf{Conclusion}: While we cannot definitively rule out the alternative, the
weight of evidence favors our interpretation because [synthesis of tests].

\textbf{Changes Made:} Added Tables X, Y, Z testing alternative mechanisms, and expanded
Section 6.3 (pages A-B) discussing mechanism evidence.

\textbf{Location:} Section 6.3 (mechanisms), Tables X-Z, Online Appendix C.
```

### 4. Robustness to Specification Choices

**Typical comment**: "Results may be sensitive to [specific modeling choice: clustering, controls, sample period, etc.]."

**Response framework**:
```latex
\textbf{Response:} We agree that demonstrating robustness to modeling choices is
important. New Table X presents extensive robustness checks:

Column (1) reproduces the main specification. Column (2) uses [alternative clustering].
Column (3) adds [additional controls]. Column (4) restricts to [alternative sample].
Column (5) uses [alternative outcome measurement]. Column (6) employs [alternative
estimation method].

Across all specifications, the treatment effect ranges from [lower] to [upper]
(mean = [average], SD = [sd]), demonstrating stability. The main estimate falls
within one standard error of all alternative specifications.

\textbf{Changes Made:} Added comprehensive robustness table (Table X) and discussion
in Section 5.4 (page Y).

\textbf{Location:} Section 5.4 (robustness), Table X.
```

### 5. Missing Control Variables

**Typical comment**: "You should control for [variable X]."

**Response framework (when you agree)**:
```latex
\textbf{Response:} This is a valuable suggestion. We have added [variable] as a
control in our augmented specification (new Table X, Column Y). The treatment
coefficient changes from [original] to [new], suggesting [interpretation]. We have
updated the main text to incorporate this analysis.

\textbf{Changes Made:} Added [variable] to Table X and discussion in Section 5.2.

\textbf{Location:} Table X Column Y, Section 5.2 page Z.
```

**Response framework (when control is problematic)**:
```latex
\textbf{Response:} While [variable] is an interesting factor, we have not included
it as a control for the following reasons: [bad control argument / post-treatment
bias / mediator variable / measurement concerns].

However, to address the reviewer's concern, we present results including [variable]
in Online Appendix Table X. The treatment effect [changes/remains stable], and we
discuss the interpretation challenges in Appendix Section Y.

\textbf{Location:} Online Appendix Table X, Appendix Section Y.
```

### 6. Data Quality / Measurement Concerns

**Typical comment**: "How reliable is your measure of [key variable]?"

**Response framework**:
```latex
\textbf{Response:} We take measurement seriously and have validated [variable] through
multiple approaches:

\textbf{External validation}: We compare our measure to [alternative data source] for
the [subset] where both are available. The correlation is [r] (N = X), suggesting
[interpretation]. New Appendix Table X presents this comparison.

\textbf{Measurement error analysis}: If classical measurement error attenuates our
estimates, the true effect would be [larger/smaller]. We discuss this in new Section Y.

\textbf{Alternative measures}: We re-estimate using [alternative measurement approach]
(new Table Z). Results are qualitatively similar, with [interpretation of differences].

\textbf{Changes Made:} Added Appendix Table X (validation), Section Y (measurement
discussion), Table Z (alternative measures).

\textbf{Location:} Section 3.4 (measurement), Table Z, Appendix Table X.
```

### 7. Economic Magnitudes

**Typical comment**: "The effect size seems [large/small]."

**Response framework**:
```latex
\textbf{Response:} To provide context for the economic magnitude, we offer several
benchmarks:

\textbf{Comparison to prior literature}: Our estimate of [X%] is [comparable to /
larger than / smaller than] effects documented in related settings. \citet{author2020}
find [Y%] for [related treatment], while \citet{author2019} report [Z%] for [similar
context]. Our estimate falls [within/outside] the range of prior work, likely due to
[explanation of differences].

\textbf{Economic significance}: For the average property valued at \$[M], our estimate
implies a \$[N] increase. This represents [context: e.g., X% of typical renovation
costs, Y months of rental income, etc.].

\textbf{Statistical power}: With N = [sample size], we have [power%] power to detect
effects as small as [minimum detectable effect], suggesting we are not simply
underpowered to find [larger/smaller] effects.

\textbf{Changes Made:} Expanded discussion of economic magnitude in Section 5.1
(paragraphs 3-4, page X) with the above benchmarks.

\textbf{Location:} Section 5.1 pages X-Y.
```

### 8. Literature Coverage

**Typical comment**: "You should cite/discuss [paper X]."

**Response framework**:
```latex
\textbf{Response:} Thank you for this reference. We have incorporated \citet{citationkey}
into our literature review (Section 2.2, page X). This work is [related because...].
Our contribution differs/extends by [differentiation].

\textbf{Changes Made:} Added \citet{citationkey} to literature review with discussion
of relationship to our work.

\textbf{Location:} Section 2.2 page X, paragraph 3.
```

### 9. Presentation / Clarity Issues

**Typical comment**: "Section X is unclear" or "Table Y is hard to interpret."

**Response framework**:
```latex
\textbf{Response:} We apologize for the lack of clarity. We have substantially revised
[section/table/figure] to improve exposition:

\textbf{Structural changes}: [Reorganized paragraphs / Added subheadings / Simplified
table layout]

\textbf{Added content}: [New examples / Clearer definitions / Step-by-step explanation]

\textbf{Visual improvements}: [Simplified figure / Added notes to table / Highlighted
key results]

We believe these revisions address the reviewer's concern.

\textbf{Changes Made:} Revised [section/table/figure] with changes described above.

\textbf{Location:} [Section X pages Y-Z / Table X / Figure X].
```

---

## Disagreeing Respectfully

When you fundamentally disagree with a suggestion:

```latex
\textbf{Response:} We appreciate the reviewer's suggestion to [action]. However, we
respectfully maintain our current approach for the following reasons:

\textbf{First}, [substantive reason 1 with citation/evidence if applicable].

\textbf{Second}, [methodological reason / data limitation / theoretical justification].

\textbf{Third}, [potential unintended consequences of suggested change].

To address the underlying concern while maintaining our approach, we have [compromise:
added robustness check / expanded discussion / provided supplementary analysis].

\textbf{Changes Made:} [Specific compromise actions taken].

\textbf{Location:} [Where compromise appears].
```

**Key principles**:
- Never say "the reviewer is wrong"
- Acknowledge the valid underlying concern
- Provide substantive reasons for your choice
- Offer a compromise when possible

---

## Summarizing Changes in Cover Letter

```latex
Dear Editor,

We are pleased to resubmit our manuscript "[Title]" for publication in [Journal].
We thank the reviewers for their constructive feedback, which has substantially
improved the paper.

\textbf{Major Revisions:}

\textbf{Enhanced identification strategy} (Reviewers 1 and 2): We have added event
study analysis (new Figure 3), instrumental variable estimates (new Table 5), and
Oster (2019) bounds analysis (Online Appendix Table A4) to address endogeneity
concerns. These analyses confirm our main findings.

\textbf{Expanded mechanism tests} (Reviewer 1): New Tables 6-7 and Section 6.3 present
direct evidence on the operational improvements and capital investment channels
driving value creation.

\textbf{Additional robustness} (Reviewer 2): New Table 8 presents twelve robustness
checks examining alternative specifications, samples, and measurement approaches.
Effects remain stable across all tests.

\textbf{Improved exposition} (Reviewers 1, 2, and 3): We have clarified the
identification assumption (Section 4.2), expanded the literature review (Section 2),
and simplified Table 2 for readability.

The attached point-by-point response provides detailed explanations of all changes.

Sincerely,
[Authors]
```

---

## Common Pitfalls to Avoid

❌ **Defensive tone**: "The reviewer clearly did not understand..."
✅ **Constructive**: "We apologize for the lack of clarity. We have revised..."

❌ **Dismissive**: "This is beyond the scope of the paper."
✅ **Engaging**: "While [suggestion] is interesting, we focus on [our question] because [reason]. We mention the alternative in Section X for completeness."

❌ **Vague changes**: "We have revised the paper accordingly."
✅ **Specific**: "We have added Table X (page Y), revised Section Z (paragraphs 2-4, pages A-B), and expanded the discussion..."

❌ **Ignoring suggestions**: [No response to a comment]
✅ **Acknowledging all**: "While we have not implemented this specific suggestion, we address the underlying concern by [alternative approach]."

---

## Response Letter Checklist

- [ ] All reviewer comments addressed (number each one)
- [ ] Changes clearly specified with page/table/section references
- [ ] Tone is respectful and constructive throughout
- [ ] Disagreements are justified substantively (not defensively)
- [ ] Compromises offered where you can't fully comply
- [ ] Summary of major changes in cover letter
- [ ] Tracked changes document prepared (if requested)
- [ ] Supplementary materials referenced appropriately
