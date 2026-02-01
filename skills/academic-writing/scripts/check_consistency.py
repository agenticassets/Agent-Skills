#!/usr/bin/env python3
"""
Academic Paper Consistency Checker
===================================

Validates internal consistency in LaTeX academic manuscripts:
- Cross-references (\\ref{} matches \\label{})
- Table/figure numbering
- Hypothesis-result mapping (H1, H2, H3 referenced in text)
- Notation consistency (variable subscripts)
- Citation completeness (wraps existing citation checker)

Usage:
    python check_consistency.py /path/to/Main.tex [--check-numbers] [--check-citations]

Author: Academic Writing Skill
"""

import os
import re
import sys
from pathlib import Path
from typing import Set, List, Tuple, Dict
from collections import defaultdict


class ConsistencyChecker:
    """Check internal consistency of LaTeX academic manuscript."""

    def __init__(self, main_tex_path: str):
        self.main_tex = Path(main_tex_path)
        self.project_root = self.main_tex.parent
        self.all_content = ""
        self.refs = set()
        self.labels = set()
        self.hypotheses = defaultdict(list)
        self.tables_mentioned = set()
        self.figures_mentioned = set()
        self.notation_patterns = defaultdict(set)

    def read_all_tex_files(self) -> str:
        """Read main tex and all \\input{} files."""
        content = self._read_single_tex(self.main_tex)

        # Find all \input{} commands
        input_pattern = r'\\input\{([^}]+)\}'
        inputs = re.findall(input_pattern, content)

        for input_file in inputs:
            # Handle paths like sections/Introduction.tex or ../Results/Tables/Table01.tex
            if not input_file.endswith('.tex'):
                input_file += '.tex'

            input_path = self.project_root / input_file
            if input_path.exists():
                input_content = self._read_single_tex(input_path)
                content += "\n" + input_content

        return content

    def _read_single_tex(self, path: Path) -> str:
        """Read a single tex file, handling different encodings."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(path, 'r', encoding='latin-1') as f:
                return f.read()

    def extract_refs_and_labels(self):
        """Extract all \\ref{} and \\label{} commands."""
        self.all_content = self.read_all_tex_files()

        # Extract \ref{key} commands
        ref_pattern = r'\\ref\{([^}]+)\}'
        self.refs = set(re.findall(ref_pattern, self.all_content))

        # Extract \label{key} commands
        label_pattern = r'\\label\{([^}]+)\}'
        self.labels = set(re.findall(label_pattern, self.all_content))

    def check_cross_references(self) -> List[str]:
        """Check for broken cross-references."""
        issues = []

        missing_labels = self.refs - self.labels
        if missing_labels:
            issues.append(f"Missing labels (referenced but not defined): {len(missing_labels)}")
            for label in sorted(missing_labels):
                issues.append(f"  • {label}")

        unused_labels = self.labels - self.refs
        if unused_labels and len(unused_labels) > 0:
            # This is just a warning, not an error
            pass

        return issues

    def extract_hypothesis_references(self):
        """Extract hypothesis mentions (H1, H2, H3, etc.)."""
        # Pattern: H1, H2, H3 (potentially with formatting)
        hyp_pattern = r'\b(H\d+)\b'
        matches = re.finditer(hyp_pattern, self.all_content)

        for match in matches:
            hyp = match.group(1)
            # Get surrounding context (50 chars before and after)
            start = max(0, match.start() - 50)
            end = min(len(self.all_content), match.end() + 50)
            context = self.all_content[start:end].replace('\n', ' ')
            self.hypotheses[hyp].append(context)

    def check_hypothesis_mapping(self) -> List[str]:
        """Check hypothesis-result mapping."""
        issues = []

        if not self.hypotheses:
            issues.append("Warning: No hypothesis references found (H1, H2, H3, etc.)")
            return issues

        # Count references to each hypothesis
        for hyp in sorted(self.hypotheses.keys()):
            count = len(self.hypotheses[hyp])
            if count == 1:
                issues.append(f"Warning: {hyp} mentioned only once (should appear in both hypothesis development and results)")

        return issues

    def extract_table_figure_mentions(self):
        """Extract tables and figures mentioned in text."""
        # Match \ref{tab:name} or explicit "Table 1" mentions
        table_ref_pattern = r'\\ref\{tab:([^}]+)\}|Table\s+(\d+)'
        figure_ref_pattern = r'\\ref\{fig:([^}]+)\}|Figure\s+(\d+)'

        for match in re.finditer(table_ref_pattern, self.all_content):
            if match.group(1):
                self.tables_mentioned.add(f"tab:{match.group(1)}")
            if match.group(2):
                self.tables_mentioned.add(f"Table {match.group(2)}")

        for match in re.finditer(figure_ref_pattern, self.all_content):
            if match.group(1):
                self.figures_mentioned.add(f"fig:{match.group(1)}")
            if match.group(2):
                self.figures_mentioned.add(f"Figure {match.group(2)}")

    def check_table_figure_existence(self) -> List[str]:
        """Check if mentioned tables/figures have corresponding \\label{}."""
        issues = []

        for table in self.tables_mentioned:
            if table.startswith("tab:") and table not in self.labels:
                issues.append(f"Table referenced but label not found: {table}")

        for figure in self.figures_mentioned:
            if figure.startswith("fig:") and figure not in self.labels:
                issues.append(f"Figure referenced but label not found: {figure}")

        return issues

    def extract_notation_patterns(self):
        """Extract mathematical notation patterns for consistency checks."""
        # Look for common variable patterns with subscripts
        # Pattern: Y_{it}, Y_{i,t}, Y_it (inconsistent subscript formatting)
        var_pattern = r'([A-Z][a-z]*)_\{?([^}]+)\}?'

        for match in re.finditer(var_pattern, self.all_content):
            var_name = match.group(1)
            subscript = match.group(2)
            self.notation_patterns[var_name].add(subscript)

    def check_notation_consistency(self) -> List[str]:
        """Check for inconsistent mathematical notation."""
        issues = []

        for var_name, subscripts in self.notation_patterns.items():
            if len(subscripts) > 1:
                # Check for common inconsistencies: "it" vs "i,t" vs "i, t"
                normalized = set()
                for sub in subscripts:
                    # Remove spaces and normalize
                    norm = sub.replace(' ', '').replace(',', '')
                    normalized.add(norm)

                if len(normalized) > 1:
                    issues.append(f"Inconsistent notation for {var_name}: {sorted(subscripts)}")

        return issues

    def run_all_checks(self, check_citations: bool = False) -> Dict[str, List[str]]:
        """Run all consistency checks."""
        results = {}

        print("🔍 Running consistency checks...")
        print(f"📄 Main file: {self.main_tex}")

        # Cross-references
        print("\n1. Checking cross-references...")
        self.extract_refs_and_labels()
        results['cross_refs'] = self.check_cross_references()

        # Hypotheses
        print("2. Checking hypothesis mapping...")
        self.extract_hypothesis_references()
        results['hypotheses'] = self.check_hypothesis_mapping()

        # Tables and figures
        print("3. Checking table/figure references...")
        self.extract_table_figure_mentions()
        results['tables_figures'] = self.check_table_figure_existence()

        # Notation
        print("4. Checking notation consistency...")
        self.extract_notation_patterns()
        results['notation'] = self.check_notation_consistency()

        # Citations (if requested)
        if check_citations:
            print("5. Checking citations...")
            results['citations'] = self._check_citations()

        return results

    def _check_citations(self) -> List[str]:
        """Wrap Tests/check_citations.py if it exists."""
        issues = []

        # Look for Tests/check_citations.py in project
        citation_checker = self.project_root.parent / "Tests" / "check_citations.py"

        if citation_checker.exists():
            import subprocess
            try:
                result = subprocess.run(
                    ["python", str(citation_checker)],
                    cwd=str(citation_checker.parent),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    issues.append("Citation check found issues (run Tests/check_citations.py for details)")
            except Exception as e:
                issues.append(f"Could not run citation checker: {str(e)}")
        else:
            issues.append("Citation checker not found at Tests/check_citations.py")

        return issues

    def print_results(self, results: Dict[str, List[str]]):
        """Print formatted results."""
        print("\n" + "="*60)
        print("CONSISTENCY CHECK RESULTS")
        print("="*60)

        total_issues = sum(len(issues) for issues in results.values())

        if total_issues == 0:
            print("\n✅ SUCCESS: No consistency issues found!")
        else:
            print(f"\n⚠️  Found {total_issues} potential issues:\n")

            for check_name, issues in results.items():
                if issues:
                    print(f"\n{check_name.upper().replace('_', ' ')}:")
                    for issue in issues:
                        print(f"  {issue}")

        print("\n" + "="*60)


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_consistency.py /path/to/Main.tex [--check-citations]")
        sys.exit(1)

    main_tex = sys.argv[1]
    check_citations = "--check-citations" in sys.argv

    if not Path(main_tex).exists():
        print(f"❌ Error: File not found: {main_tex}")
        sys.exit(1)

    checker = ConsistencyChecker(main_tex)
    results = checker.run_all_checks(check_citations=check_citations)
    checker.print_results(results)

    # Exit with error code if issues found
    total_issues = sum(len(issues) for issues in results.values())
    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()
