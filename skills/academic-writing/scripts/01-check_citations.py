#!/usr/bin/env python3
"""
Citation Checker Script
=======================

This script automatically verifies all citation keys in a LaTeX document against
the bibliography file specified in the \bibliography{} command.

Usage:
    python check_citations.py

The script will:
1. Parse the LaTeX document for all citation keys
2. Extract the bibliography file path from \bibliography{} command
3. Parse the bibliography file for available citation keys
4. Report missing citations that would cause "?" marks in PDF compilation
5. Show unused bibliography entries (optional, great for cleanup)
6. Move unused bibliography entries to unused-references.bib (optional)
7. Provide a summary of citation usage

Author: Citation Checker Tool
"""

import os
import re
import sys
from pathlib import Path
from typing import Set, List, Optional


# =============================================================================
# CONFIGURATION SECTION - Modify these variables as needed
# =============================================================================

# LaTeX document to check (relative to script directory)
# UPDATE THIS PATH to point to your main .tex file
LATEX_FILE = "../AI_in_CRE_Nov30.tex"

# If you want to override the bibliography path instead of extracting from \bibliography{}
# set this to the path. Leave as None to auto-extract from the .tex file
OVERRIDE_BIB_PATH = None

# Output options
VERBOSE = True  # Set to False for less detailed output
SHOW_UNUSED = True   # Set to True to also show bibliography entries not used in document
MOVE_UNUSED = True   # Set to True to move unused citations to unused-references.bib
EXPORT_RESULTS = True  # Set to True to save results to a file
# Make output file path relative to script location
OUTPUT_FILE = str(Path(__file__).parent / "citation_check_results.txt")

# =============================================================================
# END CONFIGURATION SECTION
# =============================================================================


class CitationChecker:
    """Main class for checking LaTeX citations against bibliography."""

    def __init__(self, latex_file: str, override_bib_path: Optional[str] = None):
        # Handle relative paths more robustly
        if latex_file.startswith("../"):
            # If run from Tests folder, go up one level
            script_dir = Path(__file__).parent
            latex_path = script_dir / latex_file
        else:
            # If run from main directory, use as-is
            latex_path = Path(latex_file)

        # If the file doesn't exist, try alternative locations
        if not latex_path.exists():
            script_dir = Path(__file__).parent
            # Try relative to script directory
            alt_path = script_dir / "../Main6.tex"
            if alt_path.exists():
                latex_path = alt_path

        self.latex_file = latex_path
        self.override_bib_path = override_bib_path
        self.bib_file = None
        self.doc_citations = set()
        self.bib_citations = set()
        self.results = {}

    def extract_bibliography_path(self) -> Optional[Path]:
        """Extract bibliography file path from \bibliography{} command."""
        if self.override_bib_path:
            return Path(self.override_bib_path)

        try:
            with open(self.latex_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find \bibliography{path} command (not commented)
            bib_match = re.search(r'^[^%]*\\bibliography\{([^}]+)\}', content, re.MULTILINE)
            if bib_match:
                bib_path = bib_match.group(1)
                # Handle different path formats
                if not bib_path.endswith('.bib'):
                    bib_path += '.bib'
                # Since we're in Tests folder, adjust path relative to LaTeX file location
                return self.latex_file.parent / bib_path

            print("ERROR: No \\bibliography{} command found in LaTeX file")
            return None

        except FileNotFoundError:
            print(f"ERROR: LaTeX file not found: {self.latex_file}")
            return None
        except Exception as e:
            print(f"ERROR: Failed to read LaTeX file: {e}")
            return None

    def extract_document_citations(self) -> Set[str]:
        """Extract all citation keys from the LaTeX document."""
        citations = set()

        try:
            with open(self.latex_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find all citation commands: \cite, \citep, \citet, \citealp, etc.
            # Pattern matches \citecommand{key1,key2,key3}
            cite_pattern = r'\\[a-z]*cite[a-z]*\{([^}]+)\}'
            matches = re.findall(cite_pattern, content)

            for match in matches:
                # Split on commas and clean up each key
                keys = [key.strip() for key in match.split(',')]
                citations.update(keys)

            # Remove empty strings that might result from extra commas
            citations.discard('')

        except FileNotFoundError:
            print(f"ERROR: LaTeX file not found: {self.latex_file}")
        except Exception as e:
            print(f"ERROR: Failed to read LaTeX file: {e}")

        return citations

    def extract_bibliography_citations(self) -> Set[str]:
        """Extract all citation keys from the bibliography file."""
        citations = set()

        if not self.bib_file:
            return citations

        try:
            with open(self.bib_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find all @entrytype{key, entries
            bib_pattern = r'@\w+\{([^,\s]+),'
            matches = re.findall(bib_pattern, content)
            citations.update(matches)

        except FileNotFoundError:
            print(f"ERROR: Bibliography file not found: {self.bib_file}")
        except Exception as e:
            print(f"ERROR: Failed to read bibliography file: {e}")

        return citations

    def extract_unused_bibliography_entries(self, unused_citations: Set[str]) -> List[str]:
        """Extract full bibliography entries for unused citations."""
        entries = []

        if not self.bib_file or not unused_citations:
            return entries

        try:
            with open(self.bib_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split content into individual entries
            # BibTeX entries start with @ and end before the next @ or end of file
            entry_pattern = r'(@\w+\{[^@]*(?:\n(?![@]).*)*)'
            matches = re.findall(entry_pattern, content, re.MULTILINE | re.DOTALL)

            for entry in matches:
                # Extract the citation key from the entry
                key_match = re.search(r'@\w+\{([^,\s]+),', entry)
                if key_match and key_match.group(1) in unused_citations:
                    entries.append(entry.strip())

        except FileNotFoundError:
            print(f"ERROR: Bibliography file not found: {self.bib_file}")
        except Exception as e:
            print(f"ERROR: Failed to read bibliography file: {e}")

        return entries

    def get_existing_unused_citations(self, unused_file_path: Path) -> Set[str]:
        """Get citation keys that already exist in the unused references file."""
        existing_keys = set()

        if not unused_file_path.exists():
            return existing_keys

        try:
            with open(unused_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find all @entrytype{key, entries in the unused file
            bib_pattern = r'@\w+\{([^,\s]+),'
            matches = re.findall(bib_pattern, content)
            existing_keys.update(matches)

        except Exception as e:
            print(f"⚠️  Warning: Could not read existing unused references file: {e}")

        return existing_keys

    def remove_entries_from_bibliography(self, citations_to_remove: Set[str]):
        """Remove specified citation entries from the main bibliography file."""
        if not citations_to_remove:
            return

        try:
            with open(self.bib_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split content into individual entries
            # BibTeX entries start with @ and end before the next @ or end of file
            entry_pattern = r'(@\w+\{[^@]*(?:\n(?![@]).*)*)'
            matches = re.findall(entry_pattern, content, re.MULTILINE | re.DOTALL)

            # Filter out entries that should be removed
            kept_entries = []
            removed_count = 0

            for entry in matches:
                # Extract the citation key from the entry
                key_match = re.search(r'@\w+\{([^,\s]+),', entry)
                if key_match and key_match.group(1) in citations_to_remove:
                    removed_count += 1
                    continue  # Skip this entry (remove it)
                kept_entries.append(entry.strip())

            # Write back the filtered content
            with open(self.bib_file, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(kept_entries))
                f.write('\n')

            print(f"🗑️  Removed {removed_count} entries from main bibliography file")

        except Exception as e:
            print(f"ERROR: Failed to remove entries from bibliography: {e}")

    def save_unused_citations_to_file(self, unused_citations: Set[str]) -> int:
        """Save unused bibliography entries to a separate file and remove them from main bibliography.
        Returns the number of citations actually moved (excluding duplicates)."""
        if not unused_citations:
            print("ℹ️  No unused citations to move.")
            return 0

        # Create the unused references file path
        unused_file_path = self.bib_file.parent / "unused-references.bib"

        # Get existing citation keys in unused file to avoid duplicates
        existing_unused_keys = self.get_existing_unused_citations(unused_file_path)

        # Filter out citations that are already in the unused file
        new_unused_citations = unused_citations - existing_unused_keys

        if not new_unused_citations:
            print("ℹ️  All unused citations are already in the unused references file.")
            return 0

        # Extract full entries for new unused citations
        unused_entries = self.extract_unused_bibliography_entries(new_unused_citations)

        if not unused_entries:
            print("⚠️  Could not extract entries for unused citations.")
            return 0

        try:
            # Read existing content if file exists, otherwise start fresh
            existing_content = ""
            if unused_file_path.exists():
                with open(unused_file_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read().strip()
                    # Remove the header if it exists to avoid duplication
                    lines = existing_content.split('\n')
                    # Keep only non-comment lines (remove header comments)
                    content_lines = [line for line in lines if not line.startswith('%')]
                    existing_content = '\n'.join(content_lines).strip()

            # Prepare header for new file or add to existing
            header = "% Unused bibliography entries moved by citation checker\n"
            header += "% These entries were not cited in the LaTeX document\n"
            header += f"% Generated: {Path(__file__).name}\n\n"

            # Combine existing content with new entries
            with open(unused_file_path, 'w', encoding='utf-8') as f:
                f.write(header)
                if existing_content:
                    f.write(existing_content)
                    f.write('\n\n')
                f.write("\n\n".join(unused_entries))
                f.write("\n")

            moved_count = len(new_unused_citations)
            print(f"📁 Moved {moved_count} unused citations to: {unused_file_path}")

            return moved_count

        except Exception as e:
            print(f"ERROR: Failed to save unused citations: {e}")
            return 0

    def check_citations(self) -> dict:
        """Main method to check citations and return results."""
        print(f"🔍 Checking citations in: {self.latex_file}")

        # Step 1: Extract bibliography path
        self.bib_file = self.extract_bibliography_path()
        if not self.bib_file:
            return {"error": "Could not determine bibliography file"}

        print(f"📚 Bibliography file: {self.bib_file}")

        # Step 2: Extract citations from document
        self.doc_citations = self.extract_document_citations()
        print(f"📄 Found {len(self.doc_citations)} unique citations in document")

        # Step 3: Extract citations from bibliography
        self.bib_citations = self.extract_bibliography_citations()
        original_bib_count = len(self.bib_citations)
        print(f"📖 Found {original_bib_count} entries in bibliography")

        # Step 4: Compare and analyze
        missing_citations = self.doc_citations - self.bib_citations
        found_citations = self.doc_citations & self.bib_citations
        unused_citations = self.bib_citations - self.doc_citations

        moved_count = 0
        # Move unused citations to separate file if requested
        if MOVE_UNUSED and unused_citations:
            moved_count = self.save_unused_citations_to_file(unused_citations)
            # Always remove ALL unused citations from main bibliography (not just newly moved ones)
            self.remove_entries_from_bibliography(unused_citations)

        # Get final count after modifications
        final_bib_citations = self.extract_bibliography_citations()
        final_bib_count = len(final_bib_citations)

        # Get count of entries in unused references file
        unused_file_path = self.bib_file.parent / "unused-references.bib"
        unused_file_entries = len(self.get_existing_unused_citations(unused_file_path)) if MOVE_UNUSED else 0

        results = {
            "total_doc_citations": len(self.doc_citations),
            "original_bib_entries": original_bib_count,
            "final_bib_entries": final_bib_count,
            "unused_citations": len(unused_citations),
            "moved_citations": moved_count,
            "unused_file_entries": unused_file_entries,
            "found_citations": sorted(list(found_citations)),
            "missing_citations": sorted(list(missing_citations)),
            "unused_citations_list": sorted(list(unused_citations)) if SHOW_UNUSED else [],
            "is_clean": len(missing_citations) == 0
        }

        return results

    def print_results(self, results: dict):
        """Print formatted results to console."""
        if "error" in results:
            print(f"❌ {results['error']}")
            return

        print("\n" + "="*60)
        print("CITATION CHECK RESULTS")
        print("="*60)

        print("📊 Citation Summary:")
        print(f"   • Citations in document: {results['total_doc_citations']}")
        print(f"   • Citations found: {len(results['found_citations'])}")
        print(f"   • Missing citations: {len(results['missing_citations'])}")

        print("\n📚 Bibliography Summary:")
        print(f"   • Original entries in main bibliography: {results['original_bib_entries']}")
        print(f"   • Unused citations detected: {results['unused_citations']}")
        if MOVE_UNUSED:
            print(f"   • Citations moved to unused file this run: {results['moved_citations']}")
            print(f"   • Final entries in main bibliography: {results['final_bib_entries']}")
            print(f"   • Total entries in unused references file: {results['unused_file_entries']}")
        else:
            print("   • Citations moved to unused file: 0 (disabled)")
            print(f"   • Final entries in main bibliography: {results['final_bib_entries']}")

        if results["is_clean"]:
            print("\n✅ SUCCESS: All citations are properly defined!")
            print("   No '?' marks should appear in your PDF compilation.")
        else:
            print("\n❌ ISSUES FOUND: Missing citations detected!")
            print("   These will show as '?' marks in your PDF:")

            for citation in results["missing_citations"]:
                print(f"   • {citation}")

        if SHOW_UNUSED and results.get("unused_citations_list"):
            print(f"\n📝 Unused bibliography entries ({results['unused_citations']}):")
            for citation in results["unused_citations_list"]:
                print(f"   • {citation}")

        if VERBOSE and results["found_citations"]:
            print(f"\n📋 All properly defined citations ({len(results['found_citations'])}):")
            for citation in results["found_citations"]:
                print(f"   ✓ {citation}")

        # Final bibliography summary at the end
        print(f"\n📚 FINAL BIBLIOGRAPHY SUMMARY:")
        print(f"   📖 Original bibliography: {results['original_bib_entries']} entries")
        print(f"   🔍 Unused citations detected: {results['unused_citations']} entries")
        print(f"   🗑️  Unused citations removed this run: {results['moved_citations']} entries")
        print(f"   📚 Final bibliography: {results['final_bib_entries']} entries")
        print(f"   📁 Total in unused references file: {results['unused_file_entries']} entries")

    def save_results(self, results: dict, output_file: str):
        """Save results to a file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("Citation Check Results\n")
                f.write("="*50 + "\n\n")
                f.write(f"LaTeX file: {self.latex_file}\n")
                f.write(f"Bibliography file: {self.bib_file}\n\n")

                f.write("SUMMARY:\n")
                f.write(f"• Citations in document: {results['total_doc_citations']}\n")
                f.write(f"• Original entries in bibliography: {results['original_bib_entries']}\n")
                f.write(f"• Unused citations detected: {results['unused_citations']}\n")
                f.write(f"• Citations moved to unused file this run: {results['moved_citations']}\n")
                f.write(f"• Final entries in bibliography: {results['final_bib_entries']}\n")
                f.write(f"• Total entries in unused references file: {results['unused_file_entries']}\n")
                f.write(f"• Citations found: {len(results['found_citations'])}\n")
                f.write(f"• Missing citations: {len(results['missing_citations'])}\n\n")

                if results["missing_citations"]:
                    f.write("MISSING CITATIONS (will show as '?' in PDF):\n")
                    for citation in results["missing_citations"]:
                        f.write(f"• {citation}\n")
                    f.write("\n")

                if results["found_citations"]:
                    f.write("FOUND CITATIONS:\n")
                    for citation in results["found_citations"]:
                        f.write(f"✓ {citation}\n")

                if SHOW_UNUSED and results.get("unused_citations_list"):
                    f.write(f"\nUNUSED BIBLIOGRAPHY ENTRIES ({results['unused_citations']}):\n")
                    for citation in results["unused_citations_list"]:
                        f.write(f"• {citation}\n")

            print(f"\n💾 Results saved to: {output_file}")

        except Exception as e:
            print(f"ERROR: Failed to save results: {e}")


def main():
    """Main function to run the citation checker."""
    print("🚀 Citation Checker Tool")
    print("="*40)

    # Initialize checker (it will handle path resolution internally)
    checker = CitationChecker(LATEX_FILE, OVERRIDE_BIB_PATH)

    # Check if LaTeX file exists after path resolution
    if not checker.latex_file.exists():
        print(f"❌ Error: LaTeX file not found: {checker.latex_file}")
        print(f"   Current directory: {os.getcwd()}")
        print("   Please check the LATEX_FILE path in the configuration section.")
        print("   The script should be run from either the main directory or Tests folder.")
        sys.exit(1)

    # Run the check
    results = checker.check_citations()

    # Print results
    checker.print_results(results)

    # Save results if requested
    if EXPORT_RESULTS:
        checker.save_results(results, OUTPUT_FILE)

    # Exit with appropriate code
    if "error" in results or not results.get("is_clean", False):
        print("\n❌ Citation check completed with issues.")
        sys.exit(1)
    else:
        print("\n✅ Citation check completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
