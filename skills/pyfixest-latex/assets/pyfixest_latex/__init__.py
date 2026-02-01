"""
PyFixest Academic Table & Figure Generator
==========================================

Standalone module for generating publication-quality LaTeX tables
and figures from PyFixest econometric models.

Dependencies: pyfixest, pandas, numpy, scipy, matplotlib
"""

import os
import sys
from pathlib import Path

# =============================================================================
# CONFIGURABLE OUTPUT PATHS
# =============================================================================

# Default output paths (relative to working directory)
DEFAULT_TABLES_PATH = Path.cwd() / "output" / "tables"
DEFAULT_FIGURES_PATH = Path.cwd() / "output" / "figures"

# For backward compatibility
DEFAULT_OUTPUT_PATH = DEFAULT_TABLES_PATH

# Global variables for output paths (user configures these)
_OUTPUT_TABLES_PATH = None
_OUTPUT_FIGURES_PATH = None


def set_output_path(path: str) -> None:
    """
    Set the output path for saving LaTeX tables.

    Parameters
    ----------
    path : str
        Path where LaTeX tables will be saved. Absolute or relative to cwd.
    """
    global _OUTPUT_TABLES_PATH
    path_obj = Path(path)
    if not path_obj.is_absolute():
        path_obj = Path.cwd() / path_obj
    path_obj.mkdir(parents=True, exist_ok=True)
    _OUTPUT_TABLES_PATH = path_obj
    print(f"LaTeX tables will be saved to: {path_obj}")


def get_output_path() -> Path:
    """Get the current output path for LaTeX tables."""
    if _OUTPUT_TABLES_PATH is None:
        DEFAULT_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
        return DEFAULT_OUTPUT_PATH
    return _OUTPUT_TABLES_PATH


def reset_output_path() -> None:
    """Reset output path to default."""
    global _OUTPUT_TABLES_PATH
    _OUTPUT_TABLES_PATH = None
    print(f"Output path reset to default: {DEFAULT_OUTPUT_PATH}")


# =============================================================================
# IMPORT FUNCTIONS
# =============================================================================

from .academic_table_generator import (
    create_regression_table,
    create_dynamic_table,
    create_robustness_table,
    create_summary_statistics_table,
    list_saved_tables,
    clean_table_directory,
)

from .academic_figure_generator import (
    create_event_study_plot,
    create_treatment_assignment_plot,
    create_coefficient_comparison_plot,
    list_saved_figures,
    clean_figure_directory,
    set_figure_output_path,
    get_figure_output_path,
)

__version__ = "1.0.0"

__all__ = [
    # Table functions
    "create_regression_table",
    "create_dynamic_table",
    "create_robustness_table",
    "create_summary_statistics_table",
    "list_saved_tables",
    "clean_table_directory",
    # Path configuration
    "set_output_path",
    "get_output_path",
    "reset_output_path",
    # Figure functions
    "create_event_study_plot",
    "create_treatment_assignment_plot",
    "create_coefficient_comparison_plot",
    "list_saved_figures",
    "clean_figure_directory",
    "set_figure_output_path",
    "get_figure_output_path",
]
