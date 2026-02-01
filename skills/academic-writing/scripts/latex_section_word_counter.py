#!/usr/bin/env python3
"""
LaTeX Section Word Counter for Main8.tex
Counts words in each section of the Main8.tex literature review document.

This script parses the LaTeX file, identifies section boundaries,
cleans LaTeX markup, and counts words in each section.

Usage: Simply run this script directly (no command line arguments needed)
"""

import re
import os
from collections import defaultdict
from typing import Dict, List, Tuple


class LatexSectionWordCounter:
    """
    A class to count words in LaTeX document sections.
    """

    def __init__(self):
        # LaTeX section patterns (case insensitive)
        self.section_patterns = [
            r'\\section\{([^}]+)\}',
            r'\\section\*\{([^}]+)\}',
        ]

        # LaTeX commands to remove (with their arguments)
        self.commands_to_remove = [
            r'\\cite\{[^}]+\}',
            r'\\citet\{[^}]+\}',
            r'\\citep\{[^}]+\}',
            r'\\ref\{[^}]+\}',
            r'\\label\{[^}]+\}',
            r'\\begin\{[^}]+\}',
            r'\\end\{[^}]+\}',
            r'\\item',
            r'\\[a-zA-Z]+\{[^}]*\}',  # General command with braces
            r'\\[a-zA-Z]+\[[^\]]*\]\{[^}]*\}',  # Command with optional and required args
        ]

        # Math environments to remove
        self.math_patterns = [
            r'\$\$.*?\$\$',  # Display math
            r'\$.*?\$',      # Inline math
            r'\\\[.*?\\\]',  # LaTeX display math
            r'\\\(.*?\\\)',  # LaTeX inline math
        ]

    def clean_text(self, text: str) -> str:
        """
        Clean LaTeX text by removing commands, comments, and formatting.

        Args:
            text: Raw LaTeX text

        Returns:
            Cleaned plain text
        """
        # Remove LaTeX comments
        text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)

        # Remove math environments
        for pattern in self.math_patterns:
            text = re.sub(pattern, '', text, flags=re.DOTALL)

        # Remove LaTeX commands
        for pattern in self.commands_to_remove:
            text = re.sub(pattern, '', text)

        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    def extract_sections(self, content: str) -> List[Tuple[str, str, str]]:
        """
        Extract sections and their content from LaTeX document.

        Args:
            content: Full LaTeX document content

        Returns:
            List of tuples (section_title, section_label, section_content)
        """
        sections = []

        # Split content into lines for processing
        lines = content.split('\n')
        current_section = None
        current_label = None
        current_content = []

        for i, line in enumerate(lines):
            # Check if this line starts a new section
            section_match = None
            for pattern in self.section_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    section_match = match
                    break

            if section_match:
                # Save previous section if exists
                if current_section and current_content:
                    sections.append((current_section, current_label or '', '\n'.join(current_content)))

                # Start new section
                raw_section = section_match.group(1).strip()
                current_content = []

                # Check if the section title continues on next lines (rare but possible)
                if not line.strip().endswith('}'):
                    # Look ahead for closing brace
                    j = i + 1
                    while j < len(lines) and '}' not in lines[j]:
                        raw_section += ' ' + lines[j].strip()
                        j += 1
                    if j < len(lines):
                        raw_section += ' ' + lines[j].split('}')[0]

                # Extract title and label
                if '\\label{' in raw_section:
                    title_part, label_part = raw_section.split('\\label{', 1)
                    current_section = title_part.strip()
                    # Extract label name (remove closing brace)
                    current_label = label_part.split('}')[0].strip() if '}' in label_part else label_part.strip()
                else:
                    current_section = raw_section
                    current_label = None

                # Remove any remaining LaTeX commands in the title
                current_section = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', current_section)
                # Clean up extra whitespace
                current_section = re.sub(r'\s+', ' ', current_section).strip()

            elif current_section:
                # Add line to current section content
                current_content.append(line)

        # Add the last section
        if current_section and current_content:
            sections.append((current_section, current_label or '', '\n'.join(current_content)))

        return sections

    def count_words(self, text: str) -> int:
        """
        Count words in cleaned text.

        Args:
            text: Text to count words in

        Returns:
            Number of words
        """
        if not text.strip():
            return 0

        # Split on whitespace and count non-empty tokens
        words = re.split(r'\s+', text.strip())
        return len([word for word in words if word.strip()])

    def analyze_file(self, file_path: str) -> Dict[str, Dict]:
        """
        Analyze a LaTeX file and count words in each section.

        Args:
            file_path: Path to LaTeX file

        Returns:
            Dictionary with section analysis
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract sections
        sections = self.extract_sections(content)

        # Analyze each section
        results = {}
        total_words = 0

        for section_title, section_label, section_content in sections:
            # Clean the content
            cleaned_content = self.clean_text(section_content)

            # Count words
            word_count = self.count_words(cleaned_content)

            # Use title + label as key for uniqueness
            display_key = f"{section_title} [{section_label}]" if section_label else section_title

            results[display_key] = {
                'word_count': word_count,
                'section_title': section_title,
                'section_label': section_label,
                'cleaned_content_preview': cleaned_content[:200] + '...' if len(cleaned_content) > 200 else cleaned_content
            }

            total_words += word_count

        results['_summary'] = {
            'total_sections': len(sections),
            'total_words': total_words,
            'average_words_per_section': total_words / len(sections) if sections else 0
        }

        return results

    def print_results(self, results: Dict[str, Dict]) -> None:
        """
        Print analysis results in a formatted way.

        Args:
            results: Analysis results from analyze_file
        """
        print("=" * 80)
        print("LaTeX Section Word Count Analysis")
        print("=" * 80)

        # Print summary
        summary = results.get('_summary', {})
        print(f"\nSUMMARY:")
        print(f"Total sections: {summary.get('total_sections', 0)}")
        print(f"Total words: {summary.get('total_words', 0):,}")
        avg_words = summary.get('average_words_per_section', 0)
        print(f"Average words per section: {avg_words:.1f}")
        print()

        # Print section details
        print("SECTION BREAKDOWN:")
        print("-" * 80)

        for section_title, data in results.items():
            if section_title != '_summary':
                word_count = data.get('word_count', 0)
                print(f"{section_title}: {word_count:4d} words")

        print("-" * 80)


def main():
    """
    Main function to run the LaTeX section word counter.
    """
    # UPDATE THIS PATH to point to your main .tex file
    file_path = "Main8.tex"

    try:
        counter = LatexSectionWordCounter()
        results = counter.analyze_file(file_path)
        counter.print_results(results)

    except Exception as e:
        print(f"Error: {e}")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
