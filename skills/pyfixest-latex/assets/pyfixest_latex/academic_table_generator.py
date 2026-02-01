"""
Academic Table Generator for PyFixest
=======================================

Professional LaTeX table generation for academic publications.
Clean, robust, and reusable functions for DiD and regression analysis.

Author: AI Assistant
Date: 2024
"""

# =============================================================================
# CONFIGURATION AND IMPORTS
# =============================================================================

import os
import sys
from pathlib import Path
from typing import List, Optional, Union, Any
import pyfixest as pf

# Helper function for dependent variable label replacement
def _normalize_latex_symbols(text: str) -> str:
    """
    Normalize Unicode symbols to proper LaTeX commands.

    Converts common Unicode symbols that should be LaTeX commands:
    - "×" (multiplication sign) → "$\\times$"

    Parameters:
    -----------
    text : str
        Text that may contain Unicode symbols

    Returns:
    --------
    str : Text with Unicode symbols replaced by LaTeX commands
    """
    # Convert multiplication sign to LaTeX times
    # Handle both cases: with spaces ("Treatment × Post") and without ("Treatment×Post")
    # Do without spaces first to avoid double replacement
    if '×' in text:
        # Replace standalone × (without spaces) first
        import re
        # Pattern: × not surrounded by spaces
        text = re.sub(r'([^\s])×([^\s])', r'\1$\\times$\2', text)
        # Pattern: × with spaces
        text = text.replace(' × ', ' $\\times$ ')
    return text

def _apply_depvar_labels(line: str, depvar_labels: dict) -> str:
    """Apply dependent variable labels to table headers with improved pattern matching."""
    if depvar_labels is None:
        return line

    import re
    # Process all dependent variables in the line, don't break after first match
    for depvar, depvar_label in depvar_labels.items():
        # Normalize LaTeX symbols in labels
        depvar_label = _normalize_latex_symbols(depvar_label)

        # Pattern 1: Match multicolumn with any column count and alignment
        pattern1 = rf'\\multicolumn{{(\d+)}}{{(\w+)}}{{{re.escape(depvar)}}}'
        match1 = re.search(pattern1, line)
        if match1:
            col_count = match1.group(1)
            alignment = match1.group(2)
            line = re.sub(pattern1, f'\\\\multicolumn{{{col_count}}}{{{alignment}}}{{{depvar_label}}}', line)
            # Don't break - continue processing other variables in the same line

        # Pattern 2: Match just the variable name in multicolumn context (fallback)
        elif f'{{{depvar}}}' in line and 'multicolumn' in line:
            # Find the multicolumn pattern and replace the variable name
            multicol_pattern = rf'\\multicolumn{{\d+}}{{\w+}}{{{re.escape(depvar)}}}'
            if re.search(multicol_pattern, line):
                line = re.sub(multicol_pattern,
                            lambda m: m.group(0).replace(f'{{{depvar}}}', f'{{{depvar_label}}}'), line)

    return line

def _reorder_fixed_effects(lines: list) -> list:
    """
    Reorder fixed effects rows to ensure Unit FE always appears before Time FE.

    This function identifies FE rows and reorders them so unit-level FE
    (Unit FE, Firm FE, etc.) always comes before time-level FE (Time FE, Year FE, etc.).

    Parameters:
    -----------
    lines : list
        List of LaTeX table lines

    Returns:
    --------
    list : Lines with FE rows reordered
    """
    import re

    # Identify FE rows and their positions
    fe_rows = []
    fe_indices = []

    # Patterns for unit-level FE (should come first)
    # Include both labeled FE (e.g., "Unit FE") and raw variable names (e.g., "unit")
    unit_fe_patterns = [
        r'Unit FE',
        r'Firm FE',
        r'Company FE',
        r'Entity FE',
        r'Individual FE',
        r'County FE',
        r'State FE',
        r'Country FE',
        r'Panel Unit FE',
        r'Cross-sectional FE',
        r'^\s*unit\s*&',  # Raw variable name "unit" (with optional leading whitespace)
        r'^\s*firm\s*&',
        r'^\s*company\s*&',
        r'^\s*entity\s*&',
        r'^\s*individual\s*&',
        r'^\s*county\s*&',
        r'^\s*state\s*&',
        r'^\s*country\s*&',
        r'^\s*gvkey\s*&',  # Common firm identifier
        r'^\s*permno\s*&',  # Common security identifier
        r'^\s*id\s*&'  # Generic identifier
    ]

    # Patterns for time-level FE (should come second)
    # Include both labeled FE (e.g., "Year FE") and raw variable names (e.g., "year")
    time_fe_patterns = [
        r'Time FE',
        r'Year FE',
        r'Period FE',
        r'Quarter FE',
        r'Month FE',
        r'Week FE',
        r'Day FE',
        r'Temporal FE',
        r'^\s*year\s*&',  # Raw variable name "year" (with optional leading whitespace)
        r'^\s*time\s*&',
        r'^\s*period\s*&',
        r'^\s*quarter\s*&',
        r'^\s*month\s*&',
        r'^\s*week\s*&',
        r'^\s*day\s*&',
        r'^\s*date\s*&',
        r'^\s*year_quarter\s*&',
        r'^\s*year_month\s*&'
    ]

    # Find all FE rows - check for FE label OR variable names that typically indicate FE
    for i, line in enumerate(lines):
        line_lower = line.lower()
        # Check if line has table structure (&) and contains FE indicator or common FE variable names
        if '&' in line:
            # Check for explicit FE labels
            has_fe_label = 'fe' in line_lower and ('unit' in line_lower or 'firm' in line_lower or
                                                   'year' in line_lower or 'time' in line_lower or
                                                   'period' in line_lower)
            # Check for raw variable names that indicate FE (unit, year, etc.)
            has_fe_var = any(re.search(pattern, line, re.IGNORECASE) for pattern in unit_fe_patterns + time_fe_patterns)

            if has_fe_label or has_fe_var:
                fe_rows.append((i, line))
                fe_indices.append(i)

    # If no FE rows or only one, return as-is
    if len(fe_rows) <= 1:
        return lines

    # Find consecutive FE rows (they should be grouped together)
    if not fe_indices:
        return lines

    # Group consecutive FE rows
    fe_groups = []
    current_group = [fe_rows[0]]

    for i in range(1, len(fe_rows)):
        # If rows are consecutive (within 2 lines), group them
        if fe_rows[i][0] - fe_rows[i-1][0] <= 2:
            current_group.append(fe_rows[i])
        else:
            fe_groups.append(current_group)
            current_group = [fe_rows[i]]
    fe_groups.append(current_group)

    # Reorder each group
    result_lines = lines.copy()

    for group in fe_groups:
        if len(group) <= 1:
            continue

        unit_fe_rows = []
        time_fe_rows = []
        other_fe_rows = []

        # Classify FE rows
        for idx, line in group:
            line_lower = line.lower()
            # Check unit FE patterns first (more specific)
            is_unit_fe = any(re.search(pattern, line, re.IGNORECASE) for pattern in unit_fe_patterns)
            # Check time FE patterns
            is_time_fe = any(re.search(pattern, line, re.IGNORECASE) for pattern in time_fe_patterns)

            # Prioritize unit FE if both match (shouldn't happen, but safety check)
            if is_unit_fe:
                unit_fe_rows.append((idx, line))
            elif is_time_fe:
                time_fe_rows.append((idx, line))
            else:
                other_fe_rows.append((idx, line))

        # Reorder: Unit FE first, then Time FE, then others
        reordered_group = unit_fe_rows + time_fe_rows + other_fe_rows

        # If order changed, update the lines
        if reordered_group != group:
            # Get the indices
            original_indices = [idx for idx, _ in group]
            reordered_indices = [idx for idx, _ in reordered_group]

            # Replace lines in reverse order to maintain indices
            for orig_idx, (new_idx, new_line) in zip(original_indices, reordered_group):
                result_lines[orig_idx] = new_line

    return result_lines

def _filter_and_format_etable_lines(
    latex_table_content: str,
    depvar_labels: Optional[dict] = None,
    variable_labels: Optional[dict] = None
) -> str:
    """
    Centralized function to filter and format etable LaTeX output.

    Removes unwanted rows, applies custom labels, and formats numbers.
    Used by all table generation functions to avoid code duplication.
    """
    import re
    lines = latex_table_content.split('\n')
    filtered_lines = []
    skip_notes = False

    for line in lines:
        # Skip S.E. type and R² Within rows
        if 'S.E. type' in line or '$R^2$ Within' in line:
            continue

        # Skip PyFixest auto-generated labels (we set our own)
        if '\\label{' in line and line.strip().startswith('\\label{'):
            continue

        # Skip old notes section (after \end{tabular} and before \end{threeparttable})
        if '\\end{tabular}' in line:
            filtered_lines.append(line)
            skip_notes = True
            continue
        elif '\\end{threeparttable}' in line:
            skip_notes = False
            filtered_lines.append(line)
            continue
        elif skip_notes:
            continue

        # Apply dependent variable labels in table headers
        line = _apply_depvar_labels(line, depvar_labels)

        # Apply variable labels if provided
        if variable_labels is not None:
            if (not line.strip().startswith('\\') and
                '\\label{' not in line and
                '\\caption{' not in line):
                for var_name, var_label in variable_labels.items():
                    # Normalize LaTeX symbols in variable labels
                    var_label = _normalize_latex_symbols(var_label)
                    escaped_var = re.escape(var_name)
                    pattern = rf'^{escaped_var}(\s|&)'
                    if re.match(pattern, line):
                        line = re.sub(rf'^{escaped_var}', var_label, line)
                        break

        # Format observations numbers with commas
        if 'Observations' in line:
            def format_number(match):
                num_str = match.group(0)
                if len(num_str) >= 4:
                    return "{:,}".format(int(num_str))
                return num_str
            line = re.sub(r'\b\d{4,}\b', format_number, line)

        filtered_lines.append(line)

    # Reorder fixed effects rows: Unit FE before Time FE
    filtered_lines = _reorder_fixed_effects(filtered_lines)

    return '\n'.join(filtered_lines)

# Import configurable output path from __init__
try:
    from . import get_output_path
    OUTPUT_TABLES = None  # Will be set at runtime
except ImportError:
    OUTPUT_TABLES = Path.cwd() / "output" / "tables"
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

# =============================================================================
# FUNCTION 1: Standard Regression Tables (Multiple Models)
# =============================================================================

def create_regression_table(
    models: List[Any],
    model_names: List[str],
    title: str,
    label: str,
    filename: Optional[str] = None,
    custom_notes: Optional[str] = None,
    variable_labels: Optional[dict] = None,
    depvar_labels: Optional[dict] = None,
    felabels: Optional[dict] = None,
    model_heads: Optional[List[str]] = None,
    include_fe_stats: bool = True,
    signif_levels: List[float] = [0.01, 0.05, 0.1],
    digits: int = 3,
    table_font_size: str = "footnotesize",
    notes_font_size: str = "footnotesize"
) -> str:
    """
    Create professional regression table with multiple models in columns.

    Perfect for: Standard DiD regressions, robustness checks, alternative specifications.

    Parameters:
    -----------
    models : List[pf.FixestMulti]
        List of fitted PyFixest models
    model_names : List[str]
        Names for each model column (e.g., ["Basic", "Robust SE", "Controls"])
    title : str
        Table title for LaTeX
    label : str
        LaTeX label for cross-referencing (e.g., "tab:did_results")
    filename : str, optional
        Custom filename (auto-generated if None)
    custom_notes : str, optional
        Custom table notes (uses default academic format if None)
    variable_labels : dict, optional
        Dictionary mapping variable names to professional labels
        e.g., {'did': 'ASC 842 $\\times$ Treated', 'ln_at': 'Log(Assets)'}
    depvar_labels : dict, optional
        Dictionary mapping dependent variable names to custom labels for table headers
        e.g., {'tbq': "Tobin's Q", 'ffo': 'Funds from Operations'}
    felabels : dict, optional
        Dictionary mapping fixed effects variable names to custom labels
        e.g., {'gvkey': 'Firm FE', 'year_quarter_numeric': 'Time FE'}
    model_heads : List[str], optional
        Custom model column headers (overrides model_names for table headers)
        e.g., ['(1)', '(2)', '(3)'] or ['Basic Specification', 'With Controls']
    include_fe_stats : bool
        Whether to include fixed effects indicators
    signif_levels : List[float]
        Significance levels for stars [***, **, *]
    digits : int
        Decimal places for coefficients
    table_font_size : str
        LaTeX font size command for table content (default: "footnotesize")
    notes_font_size : str
        LaTeX font size command for notes in parbox (default: "footnotesize")

    Returns:
    --------
    str : LaTeX table code

    Example:
    --------
    >>> models = [model1, model2, model3]
    >>> create_regression_table(
    ...     models,
    ...     ["Basic DiD", "Robust SE", "With Controls"],
    ...     "Difference-in-Differences Regression Results",
    ...     "tab:did_main",
    ...     depvar_labels={'tbq': "Tobin's Q"},
    ...     felabels={'gvkey': 'Firm FE', 'year_quarter_numeric': 'Time FE'}
    ... )
    """
    print(f"Generating regression table: {title}")

    # Default academic notes
    if custom_notes is None:
        custom_notes = (
            "Standard errors in parentheses. "
            r"$^{***}$ p $<$ 0.01, $^{**}$ p $<$ 0.05, $^{*}$ p $<$ 0.10."
        )

    # Generate LaTeX table content (without full table environment)
    latex_table_content = pf.etable(
        models,
        type="tex",
        signif_levels=signif_levels,
        digits=digits,
        notes=custom_notes,
        labels=variable_labels,
        felabels=felabels,
        model_heads=model_heads,
        show_fe=include_fe_stats
    )

    # Filter and format output using centralized helper function
    latex_table_content = _filter_and_format_etable_lines(
        latex_table_content,
        depvar_labels=depvar_labels,
        variable_labels=variable_labels
    )

    # Wrap in proper LaTeX table environment with parbox for notes
    latex_table = f"""\\begin{{table}}[ht!]
\\centering
\\caption{{\\\\{title}}}
\\parbox{{\\linewidth}}{{\\{notes_font_size} {custom_notes}}}
\\label{{{label}}}
\\{table_font_size}
{latex_table_content}
\\end{{table}}"""

    # Auto-generate filename if not provided
    if filename is None:
        filename = f"{label.replace('tab:', '')}_regression.tex"

    # Save to file - get output path at runtime
    if OUTPUT_TABLES is None:
        output_path = get_output_path()
    else:
        output_path = OUTPUT_TABLES
    filepath = output_path / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(latex_table)

    print(f"Saved: {filepath}")
    print(f"   File: {filename}")
    print(f"   Location: {filepath}")

    return latex_table

# =============================================================================
# FUNCTION 2: Dynamic Effects/Event Study Tables
# =============================================================================

def create_dynamic_table(
    models: Union[Any, List[Any]],
    title: str,
    label: str,
    filename: Optional[str] = None,
    model_names: Optional[List[str]] = None,
    time_var: str = "year",
    treat_var: str = "ever_treated",
    reference_period: int = 14,
    treatment_period: Optional[int] = None,
    custom_notes: Optional[str] = None,
    variable_labels: Optional[dict] = None,
    depvar_labels: Optional[dict] = None,
    felabels: Optional[dict] = None,
    model_heads: Optional[List[str]] = None,
    signif_levels: List[float] = [0.01, 0.05, 0.1],
    digits: int = 3,
    table_font_size: str = "footnotesize",
    notes_font_size: str = "footnotesize"
) -> str:
    """
    Create professional dynamic effects table for event studies.

    Perfect for: DiD with time-varying treatment effects, event study coefficients,
    staggered adoption designs.

    Parameters:
    -----------
    models : pf.FixestMulti or List[pf.FixestMulti]
        Fitted PyFixest model(s) with dynamic effects (i(time_var, treat_var, ref=X))
    title : str
        Table title for LaTeX
    label : str
        LaTeX label for cross-referencing
    filename : str, optional
        Custom filename (auto-generated if None)
    model_names : List[str], optional
        Names for each model column (auto-detected if None)
    time_var : str
        Name of time variable (default: "year")
    treat_var : str
        Name of treatment variable (default: "ever_treated")
    reference_period : int
        Reference period for dynamic effects (default: 14)
    treatment_period : int, optional
        Treatment period for consistent labeling (if None, uses reference_period)
    custom_notes : str, optional
        Custom table notes
    variable_labels : dict, optional
        Dictionary mapping variable names to professional labels
        e.g., {'did': 'ASC 842 $\\times$ Treated', 'ln_at': 'Log(Assets)'}
    depvar_labels : dict, optional
        Dictionary mapping dependent variable names to custom labels for table headers
        e.g., {'tbq': "Tobin's Q", 'ffo': 'Funds from Operations'}
    felabels : dict, optional
        Dictionary mapping fixed effects variable names to custom labels
        e.g., {'gvkey': 'Firm FE', 'year_quarter_numeric': 'Time FE'}
    model_heads : List[str], optional
        Custom model column headers (overrides model_names for table headers)
        e.g., ['(1)', '(2)', '(3)'] or ['Without Controls', 'With Controls']
    signif_levels : List[float]
        Significance levels for stars
    digits : int
        Decimal places for coefficients
    table_font_size : str
        LaTeX font size command for table content (default: "footnotesize")
    notes_font_size : str
        LaTeX font size command for notes in parbox (default: "footnotesize")

    Returns:
    --------
    str : LaTeX table code

    Example:
    --------
    >>> dynamic_model = pf.feols("Y ~ i(year_quarter_numeric, treated, ref=20184) | gvkey + year", data)
    >>> create_dynamic_table(
    ...     dynamic_model,
    ...     "Dynamic Treatment Effects Over Time",
    ...     "tab:dynamic_effects",
    ...     time_var="year_quarter_numeric",
    ...     treat_var="treated",
    ...     reference_period=20184,
    ...     depvar_labels={'tbq': "Tobin's Q"},
    ...     felabels={'gvkey': 'Firm FE', 'year_quarter_numeric': 'Time FE'}
    ... )
    """
    print(f"Generating dynamic effects table: {title}")

    # Ensure models is a list
    if not isinstance(models, list):
        models = [models]

    # Default notes for dynamic effects
    if custom_notes is None:
        if treatment_period is not None:
            custom_notes = (
                f"Dynamic treatment effects relative to period {reference_period} (treatment at period {treatment_period}). "
                "Standard errors in parentheses. "
                r"$^{***}$ p $<$ 0.01, $^{**}$ p $<$ 0.05, $^{*}$ p $<$ 0.10."
            )
        else:
            custom_notes = (
                f"Dynamic treatment effects relative to period {reference_period}. "
                "Standard errors in parentheses. "
                r"$^{***}$ p $<$ 0.01, $^{**}$ p $<$ 0.05, $^{*}$ p $<$ 0.10."
            )

    # Generate LaTeX table content (without full table environment)
    latex_table_content = pf.etable(
        models,
        type="tex",
        signif_levels=signif_levels,
        digits=digits,
        notes=custom_notes,
        labels=variable_labels,
        felabels=felabels,
        model_heads=model_heads
    )

    # First pass: format coefficient names for dynamic effects
    import re
    lines = latex_table_content.split('\n')
    formatted_lines = []
    escaped_time_var = re.escape(time_var)
    escaped_treat_var = re.escape(treat_var)
    dynamic_coeff_pattern = rf'C\({escaped_time_var}, contr\.treatment\(base=(\d+)\)\)\[(\d+)\]'

    for line in lines:
        match = re.search(dynamic_coeff_pattern, line)
        if match:
            base_period = int(match.group(1))
            coeff_period = int(match.group(2))

            if treatment_period is not None:
                relative_period = coeff_period - treatment_period
            else:
                relative_period = coeff_period - base_period

            if relative_period < 0:
                new_label = f"$t_{{{relative_period}}}$"
            elif relative_period > 0:
                new_label = f"$t_{{{'+' + str(relative_period)}}}$"
            else:
                new_label = f"$t_0$"

            line = re.sub(dynamic_coeff_pattern, new_label, line)

        formatted_lines.append(line)

    latex_table_content = '\n'.join(formatted_lines)

    # Second pass: filter and format using centralized helper
    latex_table_content = _filter_and_format_etable_lines(
        latex_table_content,
        depvar_labels=depvar_labels,
        variable_labels=variable_labels
    )

    # Wrap in proper LaTeX table environment with parbox for notes
    latex_table = f"""\\begin{{table}}[ht!]
\\centering
\\caption{{\\\\{title}}}
\\parbox{{\\linewidth}}{{\\{notes_font_size} {custom_notes}}}
\\label{{{label}}}
\\{table_font_size}
{latex_table_content}
\\end{{table}}"""

    # Auto-generate filename if not provided
    if filename is None:
        filename = f"{label.replace('tab:', '')}_dynamic.tex"

    # Save to file - get output path at runtime
    if OUTPUT_TABLES is None:
        output_path = get_output_path()
    else:
        output_path = OUTPUT_TABLES
    filepath = output_path / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(latex_table)

    print(f"Saved: {filepath}")
    print(f"   File: {filename}")
    print(f"   Location: {filepath}")

    return latex_table

# =============================================================================
# FUNCTION 3: Robustness Check Tables
# =============================================================================

def create_robustness_table(
    model_groups: List[List[Any]],
    group_names: List[str],
    title: str,
    label: str,
    filename: Optional[str] = None,
    custom_notes: Optional[str] = None,
    variable_labels: Optional[dict] = None,
    depvar_labels: Optional[dict] = None,
    felabels: Optional[dict] = None,
    model_heads: Optional[List[str]] = None,
    signif_levels: List[float] = [0.01, 0.05, 0.1],
    digits: int = 3,
    table_font_size: str = "footnotesize",
    notes_font_size: str = "footnotesize"
) -> str:
    """
    Create professional robustness check table with grouped specifications.

    Perfect for: Alternative estimators, different control sets, sensitivity analysis,
    multiple robustness checks in organized groups.

    Parameters:
    -----------
    model_groups : List[List[pf.FixestMulti]]
        List of model groups, each containing multiple specifications
    group_names : List[str]
        Names for each group (e.g., ["Main Results", "Robustness"])
    title : str
        Table title for LaTeX
    label : str
        LaTeX label for cross-referencing
    filename : str, optional
        Custom filename (auto-generated if None)
    custom_notes : str, optional
        Custom table notes
    variable_labels : dict, optional
        Dictionary mapping variable names to professional labels
        e.g., {'did': 'ASC 842 $\\times$ Treated', 'ln_at': 'Log(Assets)'}
    depvar_labels : dict, optional
        Dictionary mapping dependent variable names to custom labels for table headers
        e.g., {'tbq': "Tobin's Q", 'ffo': 'Funds from Operations'}
    felabels : dict, optional
        Dictionary mapping fixed effects variable names to custom labels
        e.g., {'gvkey': 'Firm FE', 'year_quarter_numeric': 'Time FE'}
    model_heads : List[str], optional
        Custom model column headers (overrides group_names for table headers)
        e.g., ['(1)', '(2)', '(3)', '(4)', '(5)']
    signif_levels : List[float]
        Significance levels for stars
    digits : int
        Decimal places for coefficients
    table_font_size : str
        LaTeX font size command for table content (default: "footnotesize")
    notes_font_size : str
        LaTeX font size command for notes in parbox (default: "footnotesize")

    Returns:
    --------
    str : LaTeX table code

    Example:
    --------
    >>> main_models = [model1, model2]
    >>> robust_models = [model3, model4, model5]
    >>> create_robustness_table(
    ...     [main_models, robust_models],
    ...     ["Main Specification", "Robustness Checks"],
    ...     "Robustness Analysis: Alternative Specifications",
    ...     "tab:robustness",
    ...     depvar_labels={'tbq': "Tobin's Q"},
    ...     felabels={'gvkey': 'Firm FE', 'year_quarter_numeric': 'Time FE'}
    ... )
    """
    print(f"Generating robustness table: {title}")

    # Flatten model groups for etable
    all_models = []
    for group in model_groups:
        all_models.extend(group)

    # Create group labels for mgroups
    mgroups = {}
    start_col = 1
    for i, (group, name) in enumerate(zip(model_groups, group_names)):
        end_col = start_col + len(group) - 1
        if len(group) > 1:
            mgroups[name] = [start_col, end_col]
        else:
            mgroups[name] = start_col
        start_col = end_col + 1

    # Default notes for robustness
    if custom_notes is None:
        custom_notes = (
            "Robustness checks using alternative specifications. "
            "Standard errors in parentheses. "
            r"$^{***}$ p $<$ 0.01, $^{**}$ p $<$ 0.05, $^{*}$ p $<$ 0.10."
        )

    # Generate LaTeX table content with groups (without full table environment)
    latex_table_content = pf.etable(
        all_models,
        type="tex",
        mgroups=mgroups,
        signif_levels=signif_levels,
        digits=digits,
        notes=custom_notes,
        labels=variable_labels,
        felabels=felabels,
        model_heads=model_heads
    )

    # Filter and format output using centralized helper function
    latex_table_content = _filter_and_format_etable_lines(
        latex_table_content,
        depvar_labels=depvar_labels,
        variable_labels=variable_labels
    )

    # Wrap in proper LaTeX table environment with parbox for notes
    latex_table = f"""\\begin{{table}}[ht!]
\\centering
\\caption{{\\\\{title}}}
\\parbox{{\\linewidth}}{{\\{notes_font_size} {custom_notes}}}
\\label{{{label}}}
\\{table_font_size}
{latex_table_content}
\\end{{table}}"""

    # Auto-generate filename if not provided
    if filename is None:
        filename = f"{label.replace('tab:', '')}_robustness.tex"

    # Save to file - get output path at runtime
    if OUTPUT_TABLES is None:
        output_path = get_output_path()
    else:
        output_path = OUTPUT_TABLES
    filepath = output_path / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(latex_table)

    print(f"Saved: {filepath}")
    print(f"   File: {filename}")
    print(f"   Location: {filepath}")

    return latex_table

# =============================================================================
# FUNCTION 4: Summary Statistics Tables
# =============================================================================

def create_summary_statistics_table(
    data,
    variables: List[str],
    variable_labels: dict,
    title: str,
    label: str,
    filename: Optional[str] = None,
    custom_notes: Optional[str] = None,
    digits: int = 3,
    include_count: bool = True,
    percentiles: List[float] = [0.25, 0.5, 0.75],
    table_font_size: str = "footnotesize",
    notes_font_size: str = "footnotesize"
) -> str:
    """
    Create professional summary statistics table with variables as rows.

    Perfect for: Descriptive statistics, variable summaries, data overview tables.

    Parameters:
    -----------
    data : pd.DataFrame
        Dataset containing the variables
    variables : List[str]
        List of variable names to include in summary statistics
    variable_labels : dict
        Dictionary mapping variable names to professional labels
        e.g., {'ln_at': 'Log(Assets)', 'tbq': "Tobin's Q"}
    title : str
        Table title for LaTeX
    label : str
        LaTeX label for cross-referencing
    filename : str, optional
        Custom filename (auto-generated if None)
    custom_notes : str, optional
        Custom table notes
    digits : int
        Decimal places for statistics
    include_count : bool
        Whether to include observation count column
    percentiles : List[float]
        List of percentiles to include (default: [0.25, 0.5, 0.75])

    Returns:
    --------
    str : LaTeX table code

    Example:
    --------
    >>> variables = ['tbq', 'ffo', 'ln_at', 'lev']
    >>> labels = {'tbq': "Tobin's Q", 'ffo': 'FFO', 'ln_at': 'Log(Assets)', 'lev': 'Leverage'}
    >>> create_summary_statistics_table(
    ...     data=df,
    ...     variables=variables,
    ...     variable_labels=labels,
    ...     title="Summary Statistics",
    ...     label="tab:summary_stats"
    ... )
    """
    print(f"Generating summary statistics table: {title}")

    import pandas as pd

    # Calculate summary statistics for each variable
    stats_data = []

    for var in variables:
        if var not in data.columns:
            print(f"WARNING: Variable '{var}' not found in data, skipping")
            continue

        # Get clean data (drop missing values for this variable)
        clean_data = data[var].dropna()

        if len(clean_data) == 0:
            print(f"WARNING: Variable '{var}' has no valid observations, skipping")
            continue

        # Check if variable is numeric
        if not pd.api.types.is_numeric_dtype(clean_data):
            print(f"WARNING: Variable '{var}' is not numeric (type: {clean_data.dtype}), skipping")
            continue

        # Calculate statistics
        stats = {
            'Variable': variable_labels.get(var, var),  # Use professional label or variable name
            'Mean': clean_data.mean(),
            'Std Dev': clean_data.std(),
            'Min': clean_data.min(),
            'Max': clean_data.max()
        }

        # Add percentiles
        for p in percentiles:
            pct_name = f"{int(p*100)}\\%"  # Escape percent sign for LaTeX
            stats[pct_name] = clean_data.quantile(p)

        # Add count if requested
        if include_count:
            stats['N'] = len(clean_data)

        stats_data.append(stats)

    # Create DataFrame from statistics
    stats_df = pd.DataFrame(stats_data)

    if stats_df.empty:
        print("ERROR: No valid variables found for summary statistics")
        return ""

    # Format numeric columns
    numeric_cols = [col for col in stats_df.columns if col != 'Variable']
    for col in numeric_cols:
        if col == 'N':
            # Format counts as integers with commas
            stats_df[col] = stats_df[col].apply(lambda x: f"{int(x):,}")
        else:
            # Format other statistics with specified decimal places
            stats_df[col] = stats_df[col].apply(lambda x: f"{x:.{digits}f}")

    # Build LaTeX table manually for precise control
    # Reorder columns: Variable, N (if present), then other statistics
    other_cols = [col for col in stats_df.columns if col not in ['Variable', 'N']]
    if 'N' in stats_df.columns:
        col_headers = ['Variable', 'N'] + other_cols
    else:
        col_headers = ['Variable'] + other_cols
    n_cols = len(col_headers)

    # Table alignment: left for variable names, center for statistics
    alignment = 'l' + 'c' * (n_cols - 1)

    # Build table content
    latex_lines = []
    latex_lines.append(f"\\begin{{tabular}}{{{alignment}}}")
    latex_lines.append("\\toprule")

    # Header row
    header_line = " & ".join(col_headers) + " \\\\"
    latex_lines.append(header_line)
    latex_lines.append("\\midrule")

    # Data rows
    for _, row in stats_df.iterrows():
        row_values = [str(row[col]) for col in col_headers]
        data_line = " & ".join(row_values) + " \\\\"
        latex_lines.append(data_line)

    latex_lines.append("\\bottomrule")
    latex_lines.append("\\end{tabular}")

    # Set default notes if not provided
    if custom_notes is None:
        custom_notes = f"Summary statistics for {len(stats_df)} key variables. Statistics calculated on non-missing observations."

    # Join all lines (notes now handled in parbox)
    table_content = '\n'.join(latex_lines)

    # Wrap in full table environment - NEW FORMAT WITH PARBOX
    latex_table = f"""\\begin{{table}}[ht!]
\\centering
\\caption{{\\\\{title}}}
\\parbox{{\\linewidth}}{{\\{notes_font_size} {custom_notes}}}
\\label{{{label}}}
\\{table_font_size}
{table_content}
\\end{{table}}"""

    # Auto-generate filename if not provided
    if filename is None:
        filename = f"{label.replace('tab:', '')}_summary_stats.tex"

    # Save to file - get output path at runtime
    if OUTPUT_TABLES is None:
        output_path = get_output_path()
    else:
        output_path = OUTPUT_TABLES
    filepath = output_path / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(latex_table)

    print(f"Saved: {filepath}")
    print(f"   File: {filename}")
    print(f"   Variables: {len(stats_df)}")
    print(f"   Location: {filepath}")

    return latex_table

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def list_saved_tables() -> None:
    """List all saved LaTeX tables in the output directory"""
    print("Saved LaTeX Tables:")
    print("=" * 50)

    # Get output path at runtime
    if OUTPUT_TABLES is None:
        output_path = get_output_path()
    else:
        output_path = OUTPUT_TABLES

    if not output_path.exists():
        print("No tables directory found.")
        return

    tex_files = list(output_path.glob("*.tex"))
    if not tex_files:
        print("No .tex files found.")
        return

    for i, file_path in enumerate(sorted(tex_files), 1):
        size = file_path.stat().st_size
        print(f"{i:2d}. {file_path.name} ({size} bytes)")

    print(f"\nLocation: {output_path}")

def clean_table_directory(confirm: bool = True) -> None:
    """Clean all .tex files from the output directory"""
    # Get output path at runtime
    if OUTPUT_TABLES is None:
        output_path = get_output_path()
    else:
        output_path = OUTPUT_TABLES

    if not output_path.exists():
        print("No tables directory found.")
        return

    tex_files = list(output_path.glob("*.tex"))
    if not tex_files:
        print("No .tex files to clean.")
        return

    if confirm:
        response = input(f"Delete {len(tex_files)} .tex files from {output_path}? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            return

    for file_path in tex_files:
        file_path.unlink()
        print(f"Deleted: {file_path.name}")

    print(f"Cleaned {len(tex_files)} files.")
