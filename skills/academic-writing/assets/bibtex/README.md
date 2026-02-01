# BibTeX Style Files

## Current Files

- **jfe.bst** - Journal of Financial Economics style (included)

## Missing Files (Download Instructions)

### Journal of Finance (jf.bst)

Download from Richard Stanton's LaTeX resource page:
- **Source**: https://faculty.haas.berkeley.edu/stanton/texintro/src.html
- **Files needed**: jf.bst, jf.sty (optional for full JF formatting)

### Quarterly Journal of Economics (qje.bst)

Download from standard LaTeX repositories or economics style collections:
- **GitHub**: https://github.com/ShiroTakeda/econ-bst
- **CTAN**: Search for "qje" on https://www.ctan.org/

### Alternative: Universal Economics Style (econ.bst)

If journal-specific files are unavailable, use universal economics style:
- **GitHub**: https://github.com/ShiroTakeda/econ-bst
- Provides author-year citations compatible with most economics/finance journals

## Installation

1. Download .bst files from sources above
2. Place files in this directory (`assets/bibtex/`)
3. Reference in LaTeX document:
   ```latex
   \bibliographystyle{jf}    % or jfe, qje, econ
   ```

## Usage Notes

- **JFE style** (included): Standard for most top finance journals
- **JF style**: Specific requirements for Journal of Finance submissions
- **QJE style**: Economics journals following QJE formatting

For journal-specific submission, always check current author guidelines for required citation style.
