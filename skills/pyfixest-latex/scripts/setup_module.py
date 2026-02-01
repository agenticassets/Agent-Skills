#!/usr/bin/env python3
"""
Enhanced setup script for pyfixest_latex module with version checking and validation.

Usage:
    python setup_module.py [target_directory] [options]

Options:
    --create-example    Copy example template to target directory
    --python-version    Show Python version check
    -h, --help         Show this help message

If no target directory is specified, uses the current working directory.
Copies the pyfixest_latex package, creates output directories, validates
dependencies, and optionally creates an example analysis script.
"""

import argparse
import importlib.metadata
import importlib.util
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Package version requirements: (package_name, minimum_version)
REQUIRED_PACKAGES: Dict[str, str] = {
    "pyfixest": "0.20.0",
    "pandas": "1.5.0",
    "numpy": "1.20.0",
    "scipy": "1.9.0",
    "matplotlib": "3.5.0",
}

MINIMUM_PYTHON_VERSION = (3, 8)
SKILL_DIR = Path(__file__).resolve().parent.parent


class Colors:
    """Terminal color codes for colored output."""

    RESET = "\033[0m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"

    @staticmethod
    def green(text: str) -> str:
        """Return green colored text."""
        return f"{Colors.GREEN}{text}{Colors.RESET}"

    @staticmethod
    def red(text: str) -> str:
        """Return red colored text."""
        return f"{Colors.RED}{text}{Colors.RESET}"

    @staticmethod
    def yellow(text: str) -> str:
        """Return yellow colored text."""
        return f"{Colors.YELLOW}{text}{Colors.RESET}"

    @staticmethod
    def blue(text: str) -> str:
        """Return blue colored text."""
        return f"{Colors.BLUE}{text}{Colors.RESET}"

    @staticmethod
    def cyan(text: str) -> str:
        """Return cyan colored text."""
        return f"{Colors.CYAN}{text}{Colors.RESET}"

    @staticmethod
    def bold(text: str) -> str:
        """Return bold text."""
        return f"{Colors.BOLD}{text}{Colors.RESET}"


def parse_version(version_string: str) -> Tuple[int, ...]:
    """
    Parse a version string into a tuple of integers.

    Parameters
    ----------
    version_string : str
        Version string like "1.2.3" or "1.2.3rc1"

    Returns
    -------
    tuple
        Tuple of integers from the version string (e.g., (1, 2, 3))
    """
    # Extract only numeric parts before any pre-release markers
    parts = []
    current = ""
    for char in version_string:
        if char.isdigit():
            current += char
        elif current:
            parts.append(int(current))
            current = ""
        elif char not in ".-+":
            # Stop at first non-numeric, non-separator character
            break
    if current:
        parts.append(int(current))
    return tuple(parts) if parts else (0,)


def get_installed_version(package_name: str) -> Optional[str]:
    """
    Get the installed version of a package.

    Parameters
    ----------
    package_name : str
        Package name (e.g., 'numpy')

    Returns
    -------
    str or None
        Version string if found, None if package not installed
    """
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None


def version_meets_requirement(installed: str, required: str) -> bool:
    """
    Check if installed version meets the minimum requirement.

    Parameters
    ----------
    installed : str
        Installed version string
    required : str
        Required minimum version string

    Returns
    -------
    bool
        True if installed >= required, False otherwise
    """
    return parse_version(installed) >= parse_version(required)


def check_python_version() -> bool:
    """
    Check if Python version meets minimum requirement.

    Returns
    -------
    bool
        True if version is acceptable, False otherwise
    """
    current = sys.version_info[:2]
    if current < MINIMUM_PYTHON_VERSION:
        min_version = ".".join(map(str, MINIMUM_PYTHON_VERSION))
        current_version = ".".join(map(str, current))
        print(
            Colors.yellow(
                f"WARNING: Python {current_version} detected, "
                f"but {min_version}+ is recommended"
            )
        )
        return False
    return True


def check_dependencies() -> Tuple[bool, List[Tuple[str, Optional[str], str]]]:
    """
    Validate all required packages and their versions.

    Returns
    -------
    tuple
        (all_ok: bool, details: list of (package, installed_version, status))
    """
    all_ok = True
    details = []

    for package, min_version in REQUIRED_PACKAGES.items():
        installed = get_installed_version(package)

        if installed is None:
            all_ok = False
            status = Colors.red("NOT INSTALLED")
            details.append((package, None, status))
        elif version_meets_requirement(installed, min_version):
            status = Colors.green(f"OK (v{installed})")
            details.append((package, installed, status))
        else:
            all_ok = False
            status = Colors.red(f"OUTDATED (v{installed}, need v{min_version}+)")
            details.append((package, installed, status))

    return all_ok, details


def validate_module_imports(module_dir: Path) -> Tuple[bool, str]:
    """
    Validate that the module can be imported and key functions exist.

    Parameters
    ----------
    module_dir : Path
        Path to the pyfixest_latex module directory

    Returns
    -------
    tuple
        (success: bool, message: str)
    """
    try:
        # Add module directory to path temporarily
        import sys as sys_module

        sys_module.path.insert(0, str(module_dir.parent))

        # Try to import the module
        spec = importlib.util.spec_from_file_location(
            "pyfixest_latex", module_dir / "__init__.py"
        )
        if spec is None or spec.loader is None:
            return False, "Failed to load module spec"

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for key functions
        required_functions = [
            "create_regression_table",
            "create_event_study_plot",
            "create_summary_statistics_table",
            "set_output_path",
        ]

        missing_functions = [
            func for func in required_functions if not hasattr(module, func)
        ]

        if missing_functions:
            msg = f"Missing functions: {', '.join(missing_functions)}"
            return False, msg

        # Verify functions are callable
        for func_name in required_functions:
            func = getattr(module, func_name)
            if not callable(func):
                return False, f"'{func_name}' is not callable"

        sys_module.path.pop(0)
        return True, "All required functions found and callable"

    except ImportError as e:
        return False, f"Import error: {e}"
    except Exception as e:
        return False, f"Validation error: {e}"


def copy_module_files(assets_dir: Path, target_module_dir: Path) -> Tuple[int, str]:
    """
    Copy module files from assets to target directory.

    Parameters
    ----------
    assets_dir : Path
        Source assets directory
    target_module_dir : Path
        Target module directory

    Returns
    -------
    tuple
        (num_files_copied: int, status_message: str)
    """
    try:
        target_module_dir.mkdir(parents=True, exist_ok=True)

        # Copy all Python files
        py_files = list(assets_dir.glob("*.py"))
        if not py_files:
            return 0, "No Python files found in assets directory"

        for f in py_files:
            try:
                shutil.copy2(f, target_module_dir / f.name)
            except PermissionError:
                return 0, f"Permission denied copying {f.name}. Check file permissions."
            except OSError as e:
                return (
                    0,
                    f"Error copying {f.name}: {e}. Check disk space and permissions.",
                )

        return len(py_files), "All files copied successfully"

    except Exception as e:
        return 0, f"Unexpected error during copy: {e}"


def create_example_analysis(target: Path, example_source: Path) -> Tuple[bool, str]:
    """
    Create an example analysis script in the target directory.

    Parameters
    ----------
    target : Path
        Target project directory
    example_source : Path
        Source example template file

    Returns
    -------
    tuple
        (success: bool, message: str)
    """
    if not example_source.exists():
        return (
            False,
            f"Example template not found at {example_source}",
        )

    try:
        output_path = target / "example_analysis.py"
        shutil.copy2(example_source, output_path)
        return True, f"Example template created at: {output_path}"
    except PermissionError:
        return (
            False,
            f"Permission denied. Cannot write to {target}. Check directory permissions.",
        )
    except OSError as e:
        return (
            False,
            f"Failed to create example: {e}. Check disk space and permissions.",
        )


def create_output_directories(target: Path) -> Tuple[List[Path], str]:
    """
    Create output directories for tables and figures.

    Parameters
    ----------
    target : Path
        Target project directory

    Returns
    -------
    tuple
        (created_dirs: list, status_message: str)
    """
    try:
        created = []
        tables_dir = target / "output" / "tables"
        figures_dir = target / "output" / "figures"

        tables_dir.mkdir(parents=True, exist_ok=True)
        created.append(tables_dir)

        figures_dir.mkdir(parents=True, exist_ok=True)
        created.append(figures_dir)

        return created, "Output directories created"
    except OSError as e:
        return [], f"Failed to create directories: {e}"


def print_summary_report(
    target: Path,
    module_dir: Path,
    copied_count: int,
    dep_details: List[Tuple[str, Optional[str], str]],
    all_deps_ok: bool,
    module_valid: bool,
    module_validation_msg: str,
    example_created: bool = False,
    example_path: Optional[Path] = None,
) -> None:
    """
    Print a comprehensive summary report.

    Parameters
    ----------
    target : Path
        Target directory
    module_dir : Path
        Module directory
    copied_count : int
        Number of files copied
    dep_details : list
        Dependency check details
    all_deps_ok : bool
        Whether all dependencies are satisfied
    module_valid : bool
        Whether module validation passed
    module_validation_msg : str
        Module validation message
    example_created : bool
        Whether example was created
    example_path : Path, optional
        Path to example file if created
    """
    print("\n" + "=" * 70)
    print(Colors.bold("SETUP SUMMARY"))
    print("=" * 70)

    # Installation status
    print(f"\n{Colors.cyan('Installation Status:')}")
    print(f"  Target directory:  {target}")
    print(f"  Module location:   {module_dir}")
    print(f"  Files copied:      {Colors.green(str(copied_count))}")
    print(f"  Output dirs:       {Colors.green('tables/ + figures/')}")

    # Python version
    current_version = ".".join(map(str, sys.version_info[:2]))
    print(f"\n{Colors.cyan('Python Environment:')}")
    print(f"  Current version:   {current_version}")
    print(f"  Minimum required:  {'.'.join(map(str, MINIMUM_PYTHON_VERSION))}")

    # Dependencies
    print(f"\n{Colors.cyan('Package Dependencies:')}")
    for pkg, version, status in dep_details:
        if version:
            print(f"  {pkg:20} {status}")
        else:
            print(f"  {pkg:20} {status}")

    if not all_deps_ok:
        print(
            f"\n{Colors.yellow('⚠ Missing or outdated packages. Install with:')}"
        )
        missing_packages = [
            pkg for pkg, _, status in dep_details if "NOT INSTALLED" in status or "OUTDATED" in status
        ]
        print(f"  pip install --upgrade {' '.join(missing_packages)}")

    # Module validation
    print(f"\n{Colors.cyan('Module Validation:')}")
    if module_valid:
        print(f"  {Colors.green('✓ Module import successful')}")
        print(f"  {Colors.green('✓ All required functions found')}")
    else:
        print(f"  {Colors.red('✗ Validation failed')}")
        print(f"  {Colors.red(f'  {module_validation_msg}')}")

    # Example creation
    if example_created and example_path:
        print(f"\n{Colors.cyan('Example Template:')}")
        print(f"  {Colors.green('✓ Example created at:')}")
        print(f"    {example_path}")

    # Next steps
    print(f"\n{Colors.cyan('Next Steps:')}")
    print("  1. Import and configure output paths:")
    print("     from pyfixest_latex import set_output_path, set_figure_output_path")
    print('     set_output_path("output/tables")')
    print('     set_figure_output_path("output/figures")')
    print("")
    print("  2. Fit PyFixest models:")
    print('     import pyfixest as pf')
    print('     model = pf.feols("Y ~ treat | unit + year", data, vcov={"CRV1": "unit"})')
    print("")
    print("  3. Generate tables/figures:")
    print("     from pyfixest_latex import create_regression_table")
    print('     create_regression_table([model], ["Model 1"], "Title", "tab:main")')
    print("")
    print("  4. Read documentation:")
    print(
        f"     See {SKILL_DIR / 'SKILL.md'} for full API and examples"
    )

    # Final status
    status_color = Colors.green if (all_deps_ok and module_valid) else Colors.yellow
    final_status = "SUCCESS" if (all_deps_ok and module_valid) else "PARTIAL (see above)"
    print("\n" + "=" * 70)
    print(f"Final Status: {status_color(final_status)}")
    print("=" * 70 + "\n")


def main():
    """Main entry point for the setup script."""
    parser = argparse.ArgumentParser(
        description="Setup pyfixest_latex module in a project with validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
        "  python setup_module.py /path/to/project\n"
        "  python setup_module.py . --create-example\n"
        "  python setup_module.py --python-version",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target project directory (default: current directory)",
    )
    parser.add_argument(
        "--create-example",
        action="store_true",
        help="Copy example template to target directory",
    )
    parser.add_argument(
        "--python-version",
        action="store_true",
        help="Show Python version check and exit",
    )

    args = parser.parse_args()

    # Handle --python-version flag
    if args.python_version:
        current = sys.version_info[:2]
        min_req = MINIMUM_PYTHON_VERSION
        current_str = ".".join(map(str, current))
        min_str = ".".join(map(str, min_req))
        print(f"Python {current_str} (minimum required: {min_str})")
        status = "OK" if current >= min_req else "TOO OLD"
        print(f"Status: {status}")
        return

    # Resolve target directory
    target = Path(args.target).resolve()
    assets_dir = SKILL_DIR / "assets" / "pyfixest_latex"

    # Validate assets directory
    if not assets_dir.exists():
        print(Colors.red(f"ERROR: Assets directory not found"))
        print(f"Expected: {assets_dir}")
        print(f"Skill should be located at: {SKILL_DIR}")
        sys.exit(1)

    # Create target directory if it doesn't exist
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(Colors.red(f"ERROR: Cannot create target directory {target}"))
        print(f"Details: {e}")
        sys.exit(1)

    # Copy module files
    module_dir = target / "pyfixest_latex"
    copied_count, copy_status = copy_module_files(assets_dir, module_dir)

    if copied_count == 0:
        print(Colors.red(f"ERROR: Failed to copy module files"))
        print(f"Details: {copy_status}")
        sys.exit(1)

    # Create output directories
    output_dirs, _ = create_output_directories(target)

    # Check Python version
    check_python_version()

    # Check dependencies
    all_deps_ok, dep_details = check_dependencies()

    # Validate module imports
    module_valid, module_validation_msg = validate_module_imports(module_dir)

    # Handle --create-example flag
    example_created = False
    example_path = None
    if args.create_example:
        # Look for example template
        templates_dir = SKILL_DIR / "assets" / "templates"
        if templates_dir.exists():
            example_source = templates_dir / "1---example_summary_statistics.py"
            if example_source.exists():
                success, msg = create_example_analysis(target, example_source)
                example_created = success
                if success:
                    example_path = target / "example_analysis.py"
                    print(Colors.green(f"✓ {msg}"))
                else:
                    print(Colors.yellow(f"⚠ {msg}"))
            else:
                print(
                    Colors.yellow(
                        f"⚠ Example template not found at {example_source}"
                    )
                )
        else:
            print(Colors.yellow(f"⚠ Templates directory not found at {templates_dir}"))

    # Print comprehensive summary
    print_summary_report(
        target=target,
        module_dir=module_dir,
        copied_count=copied_count,
        dep_details=dep_details,
        all_deps_ok=all_deps_ok,
        module_valid=module_valid,
        module_validation_msg=module_validation_msg,
        example_created=example_created,
        example_path=example_path,
    )

    # Exit with appropriate code
    if all_deps_ok and module_valid:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
