#!/usr/bin/env python3
"""
Setup pyfixest_latex module in a target project.

Usage:
    python setup_module.py [target_directory]

If no target directory is specified, uses the current working directory.
Copies the pyfixest_latex package, creates output directories, and validates dependencies.
"""

import argparse
import importlib
import shutil
import sys
from pathlib import Path

REQUIRED_PACKAGES = ["pyfixest", "pandas", "numpy", "scipy", "matplotlib"]
SKILL_DIR = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description="Setup pyfixest_latex module in a project")
    parser.add_argument("target", nargs="?", default=".", help="Target project directory")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    assets_dir = SKILL_DIR / "assets" / "pyfixest_latex"

    if not assets_dir.exists():
        print(f"ERROR: Assets directory not found: {assets_dir}")
        sys.exit(1)

    # Copy module files
    module_dir = target / "pyfixest_latex"
    module_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    for f in assets_dir.glob("*.py"):
        shutil.copy2(f, module_dir / f.name)
        copied += 1
        print(f"  Copied: {f.name}")

    print(f"Module installed to: {module_dir} ({copied} files)")

    # Create output directories
    tables_dir = target / "output" / "tables"
    figures_dir = target / "output" / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created: {tables_dir}")
    print(f"Created: {figures_dir}")

    # Validate Python dependencies
    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
    else:
        print("\nAll required packages are installed.")

    # Print usage
    print("\n--- Quick Start ---")
    print("from pyfixest_latex import set_output_path, set_figure_output_path")
    print('set_output_path("output/tables")')
    print('set_figure_output_path("output/figures")')
    print("")
    print("import pyfixest as pf")
    print('model = pf.feols("Y ~ treat | unit + year", data, vcov={"CRV1": "unit"})')
    print("")
    print("from pyfixest_latex import create_regression_table")
    print('create_regression_table([model], ["Model 1"], "Title", "tab:main")')


if __name__ == "__main__":
    main()
