"""
Orchestrator: Run All Example Scripts
======================================

This script runs all example scripts in the correct order:
1. Summary Statistics (generates dataset with control variables)
2. Figure Generation (creates plots and visualizations)
3. Enhanced Table Generation (creates regression tables)

Author: AI Assistant
"""

# ==============================================================================
# PROJECT PATH CONFIGURATION
# ==============================================================================
from pathlib import Path
import sys
import subprocess

# Search up to 5 parent directories to find config_paths.py
for p in Path(__file__).resolve().parents[:5]:
    if (p / 'config_paths.py').exists():
        sys.path.insert(0, str(p))
        break

# ==============================================================================
# ORCHESTRATOR MAIN FUNCTION
# ==============================================================================

def run_all_examples():
    """Run all example scripts in sequence."""
    
    print("=" * 80)
    print("RUNNING ALL EXAMPLE SCRIPTS")
    print("=" * 80)
    print()
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    
    # Define scripts to run in order
    scripts = [
        ("1---example_summary_statistics.py", "Summary Statistics & Dataset Generation"),
        ("2---example_figure_usage.py", "Figure Generation"),
        ("3---example_enhanced_table_generator.py", "Enhanced Table Generation")
    ]
    
    # Run each script
    for script_name, description in scripts:
        script_path = script_dir / script_name
        
        if not script_path.exists():
            print(f"WARNING: Script not found: {script_path}")
            print(f"   Skipping: {description}\n")
            continue
        
        print("=" * 80)
        print(f"Running: {description}")
        print(f"   Script: {script_name}")
        print("=" * 80)
        print()
        
        try:
            # Run the script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(script_dir),
                check=True,
                capture_output=False  # Show output in real-time
            )
            
            print()
            print(f"Completed: {description}")
            print()
            
        except subprocess.CalledProcessError as e:
            print()
            print(f"ERROR: {description} failed with exit code {e.returncode}")
            print(f"   Script: {script_name}")
            print()
            # Continue with next script even if one fails
            continue
        except Exception as e:
            print()
            print(f"ERROR: Unexpected error running {description}")
            print(f"   Error: {str(e)}")
            print()
            continue
    
    # Final summary
    print("=" * 80)
    print("ORCHESTRATION COMPLETE")
    print("=" * 80)
    print()
    print("Check the following directories for outputs:")
    print("   - Results/Tables/     (for LaTeX tables)")
    print("   - Results/Figures/    (for plots and visualizations)")
    print("   - Data/Final_Datasets/ (for saved datasets)")
    print()

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    run_all_examples()

