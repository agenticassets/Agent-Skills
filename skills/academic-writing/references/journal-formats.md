# Journal-Specific Formatting Requirements

Quick reference for finance, economics, and real estate journal submission requirements.

## Table of Contents
- Journal of Finance (JF)
- Journal of Financial Economics (JFE)
- Review of Financial Studies (RFS)
- Journal of Financial and Quantitative Analysis (JFQA)
- Real Estate Economics
- Journal of Real Estate Finance and Economics (JREFE)

## Journal of Finance (JF)

**Bibliography Style**: `jf.bst` (Author-year in text, alphabetical reference list)
**Citation Commands**: `\citep{}`, `\citet{}`
**Line Spacing**: Double-spaced throughout
**Margins**: 1 inch all sides
**Tables**: Centered, single-spaced within tables, double-spaced between tables
**Figures**: Separate from main text, numbered consecutively
**Footnotes**: End of text before references
**Abstract**: 150 words max
**Keywords**: 4-6 keywords
**JEL Codes**: Required

**LaTeX Setup**:
```latex
\bibliographystyle{jf}
\setstretch{2.0}  % Double spacing
```

---

## Journal of Financial Economics (JFE)

**Bibliography Style**: `jfe.bst` (Author-year)
**Citation Commands**: `\citep{}`, `\citet{}`
**Line Spacing**: 1.5 or double-spaced
**Margins**: 1 inch all sides
**Tables**: Professional formatting with booktabs, centered
**Abstract**: 200 words max
**Keywords**: 4-6 keywords
**JEL Codes**: Required

**LaTeX Setup**:
```latex
\bibliographystyle{jfe}
\onehalfspacing  % or \doublespacing
\usepackage{booktabs}  % Professional tables
```

---

## Review of Financial Studies (RFS)

**Bibliography Style**: Similar to JFE (author-year)
**Citation Commands**: `\citep{}`, `\citet{}`
**Line Spacing**: Double-spaced
**Tables**: Numbered, captioned, professional formatting
**Figures**: Numbered, captioned, grayscale or color
**Abstract**: 200 words max
**Keywords**: Required
**JEL Codes**: Required

**LaTeX Setup**:
```latex
\bibliographystyle{rfs}  % or jfe if rfs unavailable
\doublespacing
```

---

## Journal of Financial and Quantitative Analysis (JFQA)

**Bibliography Style**: Author-year style
**Citation Commands**: `\citep{}`, `\citet{}`
**Line Spacing**: Double-spaced
**Margins**: 1 inch all sides
**Tables**: Single-spaced within, professional formatting
**Abstract**: 150 words max
**Keywords**: Required

---

## Real Estate Economics (REE)

**Bibliography Style**: Author-year (APA-like)
**Citation Commands**: `\citep{}`, `\citet{}`
**Line Spacing**: 1.5 spacing
**Tables**: Numbered consecutively, clear headers
**Abstract**: 150-200 words
**Keywords**: 4-6 keywords
**JEL Codes**: Recommended

**LaTeX Setup**:
```latex
\bibliographystyle{apalike}  % Closest standard style
\onehalfspacing
```

---

## Journal of Real Estate Finance and Economics (JREFE)

**Bibliography Style**: Author-year
**Line Spacing**: 1.5 or double-spaced
**Tables**: Professional formatting, clear notes
**Abstract**: 150 words max
**Keywords**: 4-6 keywords

---

## Quarterly Journal of Economics (QJE)

**Bibliography Style**: `qje.bst` (Author-year)
**Citation Commands**: `\citep{}`, `\citet{}`
**Line Spacing**: Double-spaced
**Tables**: Centered, professional formatting
**Abstract**: 150 words max
**JEL Codes**: Required

**LaTeX Setup**:
```latex
\bibliographystyle{qje}
\doublespacing
```

---

## Common Elements Across Journals

### Abstract Requirements
- **Length**: 150-200 words (journal-specific)
- **Structure**: Single paragraph summarizing question, method, findings, contribution
- **Avoid**: Citations, equations, abbreviations, jargon

### Keywords and JEL Codes
- **Keywords**: 4-6 substantive terms describing paper content
- **JEL Codes**: 2-3 codes from American Economic Association classification
- **Placement**: After abstract, before main text

### Table Formatting Standards
All journals require:
- **booktabs** package for professional horizontal rules
- Column headers clearly labeled
- Variable definitions in notes below table
- Significance levels clearly marked (*** p<0.01, ** p<0.05, * p<0.10)
- Standard errors in parentheses below coefficients
- Sample size (N) reported
- Fixed effects and clustering documented

**Universal LaTeX pattern**:
```latex
\begin{table}[ht!]
\centering
\caption{Descriptive Title}
\label{tab:label_name}
\footnotesize
\begin{tabular}{lcccc}
\toprule
Variable & Mean & SD & Min & Max \\
\midrule
Treatment & 0.25 & 0.43 & 0 & 1 \\
Outcome & 12.3 & 4.5 & 2 & 45 \\
\bottomrule
\end{tabular}
\medskip
\parbox{\linewidth}{\footnotesize
Notes: Table notes explaining variables, sample restrictions, data sources.
Statistical significance: *** p<0.01, ** p<0.05, * p<0.10.
}
\end{table}
```

### Figure Requirements
- **Format**: PDF (vector) or high-resolution PNG (300+ dpi)
- **Sizing**: Fit within text width or column width
- **Labels**: Clear axis labels, legend if needed
- **Captions**: Descriptive, explaining what figure shows
- **Grayscale**: Some journals require grayscale-compatible figures

**LaTeX pattern**:
```latex
\begin{figure}[ht!]
\centering
\includegraphics[width=0.8\textwidth]{path/to/figure.pdf}
\caption{Descriptive caption explaining the figure}
\label{fig:label_name}
\end{figure}
```

### Citation Styles

**In-text citations** (all journals):
```latex
\citet{author2020} find that...          % Author (2020) find that...
Recent work \citep{author2019} shows...  % Recent work (Author, 2019) shows...
Multiple: \citep{author2019, author2020} % (Author, 2019; Author, 2020)
```

**Bibliography entries** — use BibTeX with journal-specific .bst file

### Section Numbering
Most finance/economics journals prefer:
- Section 1: Introduction
- Section 2: Literature Review / Institutional Background
- Section 3: Data and Sample
- Section 4: Methodology
- Section 5: Results
- Section 6: Conclusion

Some journals allow unnumbered sections (use `\section*{}`)

---

## Converting Between Journals

When reformatting for a different journal:

1. **Change bibliography style** in Main.tex:
   ```latex
   \bibliographystyle{jf}  % Change to target journal
   ```

2. **Adjust line spacing**:
   ```latex
   \onehalfspacing  % or \doublespacing
   ```

3. **Recompile**: `pdflatex → bibtex → pdflatex × 2`

4. **Check abstract length**: Trim if exceeds journal limit

5. **Verify table/figure formatting**: Ensure compliance with journal style

6. **Update header**: Change running head if required

---

## Working Paper / SSRN Format

When posting to SSRN or sharing as working paper:

**Recommended settings**:
```latex
\onehalfspacing
\bibliographystyle{jfe}  % Or your preferred style
% Add author affiliations and contact info
% Include "PRELIMINARY DRAFT" or "WORKING PAPER" watermark if desired
```

**Best practices**:
- Include full author affiliations and emails on title page
- Add acknowledgments footnote
- Date the draft (use `\today` or specific date)
- Number pages continuously
- Include "Preliminary" or "Working Paper" designation if still in progress

---

## Checklist for Journal Submission

- [ ] Correct bibliography style (.bst file)
- [ ] Proper line spacing (1.5x or 2x as required)
- [ ] Abstract within word limit
- [ ] Keywords and JEL codes included
- [ ] Tables use booktabs formatting
- [ ] Figures are high resolution (vector or 300+ dpi)
- [ ] All cross-references work (`\ref{}` and `\label{}`)
- [ ] Citations compile without errors
- [ ] Page numbers included
- [ ] Title page includes all author info
- [ ] Manuscript anonymized if journal requires blind review
- [ ] Supplementary materials prepared (if applicable)
- [ ] Cover letter drafted

---

## Resources

**BibTeX Style Files**: Available in `assets/bibtex/` folder
- `jf.bst` — Journal of Finance
- `jfe.bst` — Journal of Financial Economics
- `qje.bst` — Quarterly Journal of Economics

**LaTeX Templates**: Standard academic article templates available in `assets/templates/`

**Journal Submission Pages** (always check current requirements):
- Journal of Finance: https://afajof.org
- JFE: https://www.journals.elsevier.com/journal-of-financial-economics
- RFS: https://academic.oup.com/rfs
