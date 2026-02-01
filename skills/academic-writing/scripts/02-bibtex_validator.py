#!/usr/bin/env python3
"""
BibTeX Citation Validator using OpenAlex API
=============================================
Validates and enriches BibTeX citations using the OpenAlex database
with optional AI assistance via OpenRouter for ambiguous cases.

Author: Dr. Cayman Seagraves
Date: January 2025
"""

import os
import re
import json
import time
import logging
import bibtexparser
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
import requests
from pyalex import Works, Authors, Sources
import pyalex
from difflib import SequenceMatcher
from collections import defaultdict

# BibTeX MCP tools will be available via MCP integration
# from mcp_bibtex import mcp_bibtex_search_reference  # Not needed - using direct tool calls

# ===========================
# CONFIGURATION AND SETTINGS
# ===========================

# File paths
# UPDATE THESE PATHS to point to your files
BIB_FILE_PATH = "References/references_cre_ree.bib"  # Path to your .bib file
MAIN_DOC_PATH = "AI_in_CRE_Nov30.tex"  # Path to your main LaTeX document
OUTPUT_DIR = Path("Tests/citation_validation_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# OpenAlex configuration
OPENALEX_EMAIL = "cayman-seagraves@utulsa.edu"  # Your email for polite pool
pyalex.config.email = OPENALEX_EMAIL
pyalex.config.max_retries = 3
pyalex.config.retry_backoff_factor = 0.5

# OpenRouter configuration (optional AI assistance)
# Check multiple environment variable sources for API key
OPENROUTER_API_KEY = (
    os.environ.get("OPENROUTER_API_KEY") or
    os.environ.get("OPENROUTER_API_KEY_PATH") or  # For path-based keys
    ""  # Default empty string
)

OPENROUTER_MODEL = "x-ai/grok-code-fast-1"  # or "openai/gpt-4" etc.
# OPENROUTER_MODEL = "x-ai/grok-code-fast-1"  # or "openai/gpt-4" etc.
OPENROUTER_MODEL = "x-ai/grok-4.1-fast:free"  # or "openai/gpt-4" etc.


USE_AI_ASSISTANCE = bool(OPENROUTER_API_KEY)  # Enable if API key is set

# Validation thresholds
TITLE_SIMILARITY_THRESHOLD = 0.85  # Minimum similarity for title matching
AUTHOR_SIMILARITY_THRESHOLD = 0.80  # Minimum similarity for author matching
YEAR_TOLERANCE = 1  # Allow ±1 year difference

# Citation processing limit (set to "All" for all citations, or a number for testing)
CITATION_LIMIT = "All"  # Set to "All" or a number (e.g., 5) for testing mode

# BibTeX MCP fallback search (set to True to enable multi-database search as fallback)
# NOTE: MCP tools are not available within Python scripts - they require MCP client integration
USE_BIBTEX_MCP_FALLBACK = False  # Disabled until proper MCP client integration is implemented

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(OUTPUT_DIR / 'validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===========================
# DATA STRUCTURES
# ===========================

@dataclass
class ValidationResult:
    """Stores validation results for a single citation"""
    bib_key: str
    status: str  # 'valid', 'partial', 'not_found', 'error'
    confidence_score: float
    openalex_match: Optional[Dict] = None
    missing_fields: List[str] = field(default_factory=list)
    incorrect_fields: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    suggested_corrections: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    ai_suggestions: Optional[str] = None

@dataclass
class CitationEntry:
    """Parsed citation entry from BibTeX"""
    key: str
    entry_type: str
    title: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    raw_entry: Dict = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

# ===========================
# UTILITY FUNCTIONS
# ===========================

def normalize_text(text: str) -> str:
    """Normalize text for comparison"""
    if not text:
        return ""
    # Remove LaTeX commands, accents, and special characters
    text = re.sub(r'\\[a-zA-Z]+{([^}]*)}', r'\1', text)
    text = re.sub(r'[{}\\]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def clean_title_for_search(title: str) -> str:
    """Clean title for OpenAlex search by removing BibTeX formatting"""
    if not title:
        return ""
    # Remove outer curly braces (BibTeX protection braces like {{title}})
    title = re.sub(r'^{{(.*)}}$', r'\1', title)
    # Remove single curly braces
    title = re.sub(r'[{}]', '', title)
    # Replace LaTeX curly quotes/apostrophes with regular ones
    title = title.replace("'", "'").replace("'", "'")
    title = title.replace('"', '"').replace('"', '"')
    # Remove LaTeX commands
    title = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', title)
    # Clean up whitespace
    title = re.sub(r'\s+', ' ', title)
    return title.strip()

def calculate_similarity(str1: str, str2: str) -> float:
    """Calculate similarity between two strings"""
    str1 = normalize_text(str1)
    str2 = normalize_text(str2)
    return SequenceMatcher(None, str1, str2).ratio()

def parse_authors(author_string: str) -> List[str]:
    """Parse author string from BibTeX format"""
    if not author_string:
        return []
    # Split by 'and' and clean up
    authors = re.split(r'\s+and\s+', author_string)
    parsed_authors = []
    for author in authors:
        # Handle various formats: "Last, First", "First Last", "Last, F.", etc.
        author = normalize_text(author)
        if ',' in author:
            parts = author.split(',')
            # Handle "Last, First M." format
            first_part = parts[0].strip()
            second_part = parts[1].strip() if len(parts) > 1 else ""
            author = f"{second_part} {first_part}".strip()
        # Remove extra spaces and clean up
        author = re.sub(r'\s+', ' ', author).strip()
        if author and author.lower() != 'others':  # Skip "others" entries
            parsed_authors.append(author)
    return parsed_authors

def extract_arxiv_id(text: str) -> Optional[str]:
    """Extract arXiv ID from journal field or note"""
    if not text:
        return None
    match = re.search(r'arxiv[:\s]*(\d{4}\.\d{4,5})', text.lower())
    if match:
        return match.group(1)
    return None

def extract_citations_from_latex(latex_file_path: str) -> Set[str]:
    """Extract all citation keys from a LaTeX document"""
    cited_keys = set()

    try:
        with open(latex_file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Find all \cite, \citet, \citep commands and extract keys
        # Matches patterns like \cite{key1,key2} or \citet{key1}
        cite_patterns = [
            r'\\cite(?:\[.*?\])?\{([^}]+)\}',
            r'\\citet(?:\[.*?\])?\{([^}]+)\}',
            r'\\citep(?:\[.*?\])?\{([^}]+)\}',
            r'\\citeauthor(?:\[.*?\])?\{([^}]+)\}',
            r'\\citeyear(?:\[.*?\])?\{([^}]+)\}',
            r'\\citeyearpar(?:\[.*?\])?\{([^}]+)\}',
        ]

        for pattern in cite_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Split by comma and clean up keys
                keys = [key.strip() for key in match.split(',')]
                cited_keys.update(keys)

        logger.info(f"Extracted {len(cited_keys)} unique citation keys from {latex_file_path}")
        return cited_keys

    except FileNotFoundError:
        logger.warning(f"Main document not found: {latex_file_path}")
        return set()
    except Exception as e:
        logger.error(f"Error extracting citations from {latex_file_path}: {e}")
        return set()

# ===========================
# BIBTEX PARSING
# ===========================

def parse_bibtex_file(filepath: str) -> List[CitationEntry]:
    """Parse BibTeX file and extract citation entries"""
    logger.info(f"Parsing BibTeX file: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as file:
        bib_database = bibtexparser.load(file)
    
    citations = []
    for entry in bib_database.entries:
        citation = CitationEntry(
            key=entry.get('ID', ''),
            entry_type=entry.get('ENTRYTYPE', ''),
            raw_entry=entry
        )
        
        # Extract fields
        raw_title = entry.get('title', '')
        citation.title = clean_title_for_search(raw_title)  # Clean title for better matching
        citation.authors = parse_authors(entry.get('author', ''))
        
        # Parse year
        year_str = entry.get('year', '')
        if year_str:
            try:
                citation.year = int(re.search(r'\d{4}', year_str).group())
            except (AttributeError, ValueError):
                pass
        
        citation.journal = entry.get('journal', entry.get('booktitle', ''))
        citation.volume = entry.get('volume', '')
        citation.pages = entry.get('pages', '')
        citation.doi = entry.get('doi', '')
        
        # Check for arXiv
        citation.arxiv_id = extract_arxiv_id(citation.journal) or extract_arxiv_id(entry.get('note', ''))

        # Validate year - flag future dates and current year (likely errors)
        current_year = datetime.now().year
        logger.debug(f"Checking year for {citation.key}: citation.year={citation.year}, current_year={current_year}")
        if citation.year and citation.year >= current_year:  # Flag current year and future as potentially incorrect
            warning_msg = f"Publication year ({citation.year}) is current or future - may be incorrect or preprint"
            citation.warnings.append(warning_msg)
            logger.debug(f"Added warning for {citation.key}: {warning_msg}")
        else:
            logger.debug(f"No warning added for {citation.key}: year condition not met")

        citations.append(citation)
    
    logger.info(f"Parsed {len(citations)} citations")
    return citations

# ===========================
# OPENALEX SEARCH
# ===========================

def search_bibtex_mcp(title: str, authors: List[str] = None, year: Optional[int] = None) -> Optional[Dict]:
    """Search using BibTeX MCP as fallback when OpenAlex fails

    NOTE: This function is currently disabled because MCP tools cannot be called
    directly from Python scripts. MCP tools require integration through an MCP client
    or server communication protocol.
    """
    logger.warning(f"BibTeX MCP search is DISABLED for '{title}' - returning None immediately")
    return None


def search_openalex_by_doi(doi: str) -> Optional[Dict]:
    """Search OpenAlex by DOI"""
    try:
        if doi.startswith('10.'):
            doi = f"https://doi.org/{doi}"
        work = Works()[doi]
        return work
    except Exception as e:
        logger.debug(f"DOI search failed for {doi}: {e}")
        return None

def search_openalex_by_title_author(title: str, authors: List[str], year: Optional[int] = None, arxiv_id: Optional[str] = None) -> List[Dict]:
    """Search OpenAlex by title and optionally filter by author and year"""
    try:
        results = []

        # Try arXiv ID search first if available (most reliable)
        if arxiv_id:
            try:
                arxiv_doi = f"10.48550/arXiv.{arxiv_id}"
                arxiv_work = Works()[arxiv_doi]
                if arxiv_work:
                    results.append(arxiv_work)
                    logger.info(f"Found arXiv paper by DOI: {arxiv_doi}")
            except Exception as e:
                logger.debug(f"arXiv DOI search failed: {e}")

        # If no arXiv results or no arXiv ID, try title search
        if not results:
            # Clean title for search (remove BibTeX formatting)
            cleaned_title = clean_title_for_search(title)
            # Start with title search
            query = Works().search(cleaned_title)

            # Add year filter if available
            if year:
                query = query.filter(publication_year=year)

            # Get results
            title_results = query.get()
            if title_results:
                results.extend(title_results[:3])  # Take top 3

        # If still no results and we have authors, try author-based search
        if not results and authors and len(authors) > 0:
            primary_author = authors[0]
            try:
                # Try to find the primary author
                author_query = Authors().search(primary_author)
                author_results = author_query.get()

                if author_results:
                    # Get works by this author around the target year
                    author_id = author_results[0]['id']
                    works_query = Works().filter(author_id=author_id)

                    if year:
                        works_query = works_query.filter(publication_year=year)

                    author_works = works_query.get()
                    if author_works:
                        # Find best title match using cleaned title
                        cleaned_title = clean_title_for_search(title)
                        for work in author_works[:5]:
                            work_title = work.get('title', '')
                            if calculate_similarity(cleaned_title, work_title) > 0.6:
                                results.append(work)
                                break
            except Exception as e:
                logger.debug(f"Author-based search failed: {e}")

        # Score and filter results by title and author similarity
        if results:
            scored_results = []
            cleaned_title = clean_title_for_search(title)
            
            for result in results:
                # Calculate title similarity
                oa_title = result.get('title', '')
                title_score = calculate_similarity(cleaned_title, oa_title)
                
                # Calculate author match score if authors available
                max_author_score = 0.5  # Default score if no authors to match
                if authors:
                    openalex_authors = []
                    for authorship in result.get('authorships', []):
                        author_name = authorship.get('author', {}).get('display_name', '')
                        if author_name:
                            openalex_authors.append(normalize_text(author_name))

                    # Calculate best author match
                    for bib_author in authors:
                        for oa_author in openalex_authors:
                            score = calculate_similarity(bib_author, oa_author)
                            max_author_score = max(max_author_score, score)
                
                # Combined score: prioritize title similarity, but consider author match
                # If title similarity is very high (>0.9), include even with weak author match
                # If title similarity is moderate, require better author match
                if title_score > 0.9 or (title_score > 0.7 and max_author_score > 0.3):
                    combined_score = (title_score * 0.7) + (max_author_score * 0.3)
                    scored_results.append((result, combined_score, title_score, max_author_score))

            # Sort by combined score, then by title score
            scored_results.sort(key=lambda x: (x[1], x[2]), reverse=True)
            return [r[0] for r in scored_results[:5]]  # Return top 5 matches

        return []

    except Exception as e:
        logger.error(f"OpenAlex search failed: {e}")
        return []

def validate_with_openalex(citation: CitationEntry) -> ValidationResult:
    """Validate a citation using OpenAlex"""
    result = ValidationResult(
        bib_key=citation.key,
        status='not_found',
        confidence_score=0.0
    )
    
    # Try DOI search first (most reliable)
    if citation.doi:
        logger.info(f"Searching by DOI for {citation.key}: {citation.doi}")
        match = search_openalex_by_doi(citation.doi)
        if match:
            result.openalex_match = match
            result.status = 'valid'
            result.confidence_score = 1.0
    
    # If no DOI or DOI search failed, try title/author search
    if not result.openalex_match and citation.title:
        logger.info(f"Searching by title/author for {citation.key}")
        matches = search_openalex_by_title_author(
            citation.title,
            citation.authors,
            citation.year,
            citation.arxiv_id
        )
        
        if matches:
            # Find best match based on title similarity
            best_match = None
            best_score = 0
            
            for match in matches:
                oa_title = match.get('title', '')
                title_score = calculate_similarity(citation.title, oa_title)
                
                if title_score > best_score:
                    best_score = title_score
                    best_match = match
            
            if best_match and best_score >= TITLE_SIMILARITY_THRESHOLD:
                result.openalex_match = best_match
                result.confidence_score = best_score
                result.status = 'valid' if best_score >= 0.95 else 'partial'
            elif USE_BIBTEX_MCP_FALLBACK:
                # If OpenAlex search was inconclusive, try BibTeX MCP as fallback
                logger.info(f"OpenAlex search inconclusive, trying BibTeX MCP for {citation.key}")
                mcp_match = search_bibtex_mcp(
                    citation.title,
                    citation.authors,
                    citation.year
                )

                if mcp_match:
                    result.openalex_match = mcp_match
                    result.confidence_score = mcp_match.get('confidence_score', 0.5)
                    result.status = 'valid' if result.confidence_score >= 0.8 else 'partial'
                    logger.info(f"BibTeX MCP found match with confidence {result.confidence_score:.2f}")
        elif USE_BIBTEX_MCP_FALLBACK:
            # No OpenAlex results at all, try BibTeX MCP directly
            logger.info(f"No OpenAlex results, trying BibTeX MCP for {citation.key}")
            mcp_match = search_bibtex_mcp(
                citation.title,
                citation.authors,
                citation.year
            )

            if mcp_match:
                result.openalex_match = mcp_match
                result.confidence_score = mcp_match.get('confidence_score', 0.5)
                result.status = 'valid' if result.confidence_score >= 0.8 else 'partial'
                logger.info(f"BibTeX MCP found match with confidence {result.confidence_score:.2f}")

    # Analyze the match and identify issues
    if result.openalex_match:
        analyze_match(citation, result)
    else:
        result.warnings.append("No match found in OpenAlex database")
        # Check if it might be too recent or a preprint
        if citation.arxiv_id:
            result.warnings.append("This appears to be an arXiv preprint - may not be indexed yet")
        if citation.year and citation.year >= datetime.now().year - 1:
            result.warnings.append("Recent publication - may not be indexed in OpenAlex yet")
    
    return result

def analyze_match(citation: CitationEntry, result: ValidationResult):
    """Analyze OpenAlex match and identify discrepancies"""
    match = result.openalex_match

    # Safety check for None match
    if not match:
        result.warnings.append("Match analysis failed - invalid match data")
        return

    # Check title
    oa_title = match.get('title', '')
    if citation.title:
        title_sim = calculate_similarity(citation.title, oa_title)
        if title_sim < 0.95:
            result.incorrect_fields['title'] = {
                'bib_value': citation.title,
                'openalex_value': oa_title,
                'similarity': title_sim
            }
            result.suggested_corrections['title'] = oa_title
    
    # Check year
    oa_year = match.get('publication_year')
    if citation.year and oa_year:
        if abs(citation.year - oa_year) > YEAR_TOLERANCE:
            result.incorrect_fields['year'] = {
                'bib_value': citation.year,
                'openalex_value': oa_year
            }
            result.suggested_corrections['year'] = oa_year
    
    # Check journal/source
    primary_location = match.get('primary_location')
    oa_source = ''
    if primary_location and isinstance(primary_location, dict):
        source = primary_location.get('source')
        if source and isinstance(source, dict):
            oa_source = source.get('display_name', '')

    if citation.journal and oa_source:
        journal_sim = calculate_similarity(citation.journal, oa_source)
        if journal_sim < 0.8:
            result.incorrect_fields['journal'] = {
                'bib_value': citation.journal,
                'openalex_value': oa_source,
                'similarity': journal_sim
            }
            result.suggested_corrections['journal'] = oa_source
    
    # Check for missing DOI
    oa_doi_raw = match.get('doi', '')
    oa_doi = oa_doi_raw.replace('https://doi.org/', '') if oa_doi_raw else ''
    if oa_doi and not citation.doi:
        result.missing_fields.append('doi')
        result.suggested_corrections['doi'] = oa_doi
    
    # Check volume and pages
    biblio = match.get('biblio')
    if biblio and isinstance(biblio, dict) and biblio.get('volume') and not citation.volume:
        result.missing_fields.append('volume')
        result.suggested_corrections['volume'] = biblio.get('volume')
    
    if biblio and isinstance(biblio, dict) and biblio.get('first_page') and not citation.pages:
        pages = biblio.get('first_page')
        if biblio.get('last_page'):
            pages = f"{pages}--{biblio.get('last_page')}"
        result.missing_fields.append('pages')
        result.suggested_corrections['pages'] = pages

# ===========================
# AI ASSISTANCE (OPTIONAL)
# ===========================

def get_ai_suggestions(citation: CitationEntry, validation_result: ValidationResult) -> Optional[str]:
    """Get AI suggestions for ambiguous or problematic citations"""
    if not USE_AI_ASSISTANCE:
        return None
    
    # Only use AI for problematic cases
    if validation_result.status == 'valid' and validation_result.confidence_score > 0.95:
        return None
    
    prompt = f"""
    Analyze this BibTeX citation and provide 2-3 specific, actionable improvements:

    Citation: {citation.key}
    Title: {citation.title}
    Authors: {', '.join(citation.authors) if citation.authors else 'None'}
    Year: {citation.year}
    Journal: {citation.journal or 'None'}
    DOI: {citation.doi or 'None'}

    Status: {validation_result.status} (confidence: {validation_result.confidence_score:.2f})

    Focus on: author formatting, missing fields, entry type, and OpenAlex matching issues.
    Keep suggestions brief and specific.
    """
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://localhost",
            "X-Title": "Citation Validator",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 500
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
        
    except Exception as e:
        logger.warning(f"AI assistance failed for {citation.key}: {e}")
        return None

# ===========================
# REPORT GENERATION
# ===========================

def generate_report(citations: List[CitationEntry], results: List[ValidationResult], cited_keys: Set[str] = None):
    """Generate validation report"""
    report_path = OUTPUT_DIR / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    # Calculate statistics
    total = len(results)
    valid = sum(1 for r in results if r.status == 'valid')
    partial = sum(1 for r in results if r.status == 'partial')
    not_found = sum(1 for r in results if r.status == 'not_found')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# BibTeX Citation Validation Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Citations:** {total}\n")
        f.write(f"**Valid:** {valid} ({valid/total*100:.1f}%)\n")
        f.write(f"**Partial Match:** {partial} ({partial/total*100:.1f}%)\n")
        f.write(f"**Not Found:** {not_found} ({not_found/total*100:.1f}%)\n\n")
        
        # Group results by status
        f.write("## Validation Results\n\n")

        # Initialize cited_keys if None
        if cited_keys is None:
            cited_keys = set()

        # Separate cited vs non-cited results
        cited_results = []
        non_cited_results = []

        for result in results:
            if result.bib_key in cited_keys:
                cited_results.append(result)
            else:
                non_cited_results.append(result)

        # Cited references section (highest priority)
        if cited_results:
            f.write("### 🎯 PRIORITY: Citations Used in Main Document\n\n")
            f.write(f"**Found {len(cited_results)} citations that are actually used in your paper**\n\n")

            # Cited references requiring attention
            cited_problems = [r for r in cited_results if r.status != 'valid' or r.missing_fields or r.incorrect_fields]
            if cited_problems:
                f.write("#### ⚠️ Cited References Needing Attention\n\n")
                for result in cited_problems:
                    citation = next(c for c in citations if c.key == result.bib_key)
                    f.write(f"##### `{result.bib_key}` (USED IN PAPER)\n")
                    f.write(f"- **Status:** {result.status.upper()}\n")
                    f.write(f"- **Confidence:** {result.confidence_score:.2%}\n")
                    f.write(f"- **Title:** {citation.title}\n")

                    if result.missing_fields:
                        f.write(f"- **Missing Fields:** {', '.join(result.missing_fields)}\n")

                    if result.incorrect_fields:
                        f.write("- **Potential Issues:**\n")
                        for field, info in result.incorrect_fields.items():
                            f.write(f"  - {field}: Your value doesn't match OpenAlex\n")

                    if result.suggested_corrections:
                        f.write("- **Suggested Corrections:**\n")
                        for field, value in result.suggested_corrections.items():
                            f.write(f"  - `{field}`: {value}\n")

                    if result.warnings:
                        f.write("- **Warnings:**\n")
                        for warning in result.warnings:
                            f.write(f"  - {warning}\n")

                    if result.ai_suggestions:
                        f.write("- **AI Suggestions:**\n")
                        f.write(f"  {result.ai_suggestions}\n")

                    f.write("\n")

            # Valid cited references
            cited_valid = [r for r in cited_results if r.status == 'valid' and not r.missing_fields and not r.incorrect_fields]
            if cited_valid:
                f.write("#### ✅ Valid Cited References\n\n")
                for result in cited_valid:
                    f.write(f"- `{result.bib_key}` (Confidence: {result.confidence_score:.2%})\n")
                f.write("\n")

        # Non-cited references section
        f.write("### 📚 Other References in Bibliography\n\n")

        # Problems requiring attention
        f.write("#### ⚠️ Citations Requiring Attention\n\n")
        for result in results:
            if result.status != 'valid' or result.missing_fields or result.incorrect_fields:
                citation = next(c for c in citations if c.key == result.bib_key)
                f.write(f"#### `{result.bib_key}`\n")
                f.write(f"- **Status:** {result.status.upper()}\n")
                f.write(f"- **Confidence:** {result.confidence_score:.2%}\n")
                f.write(f"- **Title:** {citation.title}\n")
                
                if result.missing_fields:
                    f.write(f"- **Missing Fields:** {', '.join(result.missing_fields)}\n")
                
                if result.incorrect_fields:
                    f.write("- **Potential Issues:**\n")
                    for field, info in result.incorrect_fields.items():
                        f.write(f"  - {field}: Your value doesn't match OpenAlex\n")
                
                if result.suggested_corrections:
                    f.write("- **Suggested Corrections:**\n")
                    for field, value in result.suggested_corrections.items():
                        f.write(f"  - `{field}`: {value}\n")
                
                if result.warnings:
                    f.write("- **Warnings:**\n")
                    for warning in result.warnings:
                        f.write(f"  - {warning}\n")
                
                if result.ai_suggestions:
                    f.write("- **AI Suggestions:**\n")
                    f.write(f"  {result.ai_suggestions}\n")
                
                f.write("\n")
        
        # Valid citations (summary)
        f.write("### ✅ Valid Citations\n\n")
        valid_citations = [r for r in results if r.status == 'valid' and not r.missing_fields and not r.incorrect_fields]
        for result in valid_citations:
            f.write(f"- `{result.bib_key}` (Confidence: {result.confidence_score:.2%})\n")
    
    logger.info(f"Report generated: {report_path}")
    return report_path

def generate_corrected_bib(citations: List[CitationEntry], results: List[ValidationResult]):
    """Generate corrected BibTeX file with suggestions applied"""
    corrected_path = OUTPUT_DIR / f"corrected_references_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bib"
    
    with open(corrected_path, 'w', encoding='utf-8') as f:
        for citation in citations:
            result = next((r for r in results if r.bib_key == citation.key), None)
            if not result:
                continue
            
            # Start with original entry
            entry = citation.raw_entry.copy()
            
            # Apply corrections
            if result.suggested_corrections:
                for field, value in result.suggested_corrections.items():
                    if field == 'year':
                        entry['year'] = str(value)
                    elif field == 'pages' and '--' in str(value):
                        entry['pages'] = str(value)
                    else:
                        entry[field] = str(value)
            
            # Write entry
            f.write(f"@{entry.get('ENTRYTYPE', 'article')}{{{entry.get('ID', '')},\n")
            
            # Write fields
            field_order = ['author', 'title', 'journal', 'year', 'volume', 'number', 'pages', 'doi']
            written_fields = set()
            
            for field in field_order:
                if field in entry and field not in ['ENTRYTYPE', 'ID']:
                    f.write(f"  {field:<12} = {{{entry[field]}}},\n")
                    written_fields.add(field)
            
            # Write remaining fields
            for field, value in entry.items():
                if field not in written_fields and field not in ['ENTRYTYPE', 'ID']:
                    f.write(f"  {field:<12} = {{{value}}},\n")
            
            f.write("}\n\n")
    
    logger.info(f"Corrected BibTeX file generated: {corrected_path}")
    return corrected_path

# ===========================
# MAIN VALIDATION PIPELINE
# ===========================

def validate_citations(bib_file_path: str, main_doc_path: Optional[str] = None):
    """Main validation pipeline"""
    logger.info("=" * 60)
    logger.info("Starting BibTeX Citation Validation")
    logger.info("=" * 60)

    # Extract citations from main document if provided
    cited_keys = set()
    if main_doc_path:
        logger.info(f"Extracting citations from main document: {main_doc_path}")
        cited_keys = extract_citations_from_latex(main_doc_path)
        logger.info(f"Found {len(cited_keys)} citations in the main document")

    # Parse BibTeX file
    citations = parse_bibtex_file(bib_file_path)

    # Apply citation limit if set
    if CITATION_LIMIT != "All":
        try:
            limit = int(CITATION_LIMIT)
            if limit > 0:
                citations = citations[:limit]
                logger.info(f"Testing mode: Processing only first {limit} citations")
            else:
                logger.warning(f"Invalid CITATION_LIMIT '{CITATION_LIMIT}', processing all citations")
        except (ValueError, TypeError):
            logger.warning(f"Invalid CITATION_LIMIT '{CITATION_LIMIT}', processing all citations")

    # Validate each citation
    results = []
    for i, citation in enumerate(citations, 1):
        logger.info(f"Validating [{i}/{len(citations)}]: {citation.key}")

        # Validate with OpenAlex
        result = validate_with_openalex(citation)

        # Get AI suggestions for problematic cases
        if USE_AI_ASSISTANCE and (result.status != 'valid' or result.confidence_score < 0.95):
            logger.info(f"Getting AI suggestions for {citation.key}")
            result.ai_suggestions = get_ai_suggestions(citation, result)

        results.append(result)

        # Rate limiting
        time.sleep(0.5)  # Be respectful to the API
    
    # Generate reports
    logger.info("Generating validation report...")
    report_path = generate_report(citations, results, cited_keys)
    
    logger.info("Generating corrected BibTeX file...")
    corrected_bib_path = generate_corrected_bib(citations, results)
    
    # Save detailed results as JSON
    json_path = OUTPUT_DIR / f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump([asdict(r) for r in results], f, indent=2, default=str)
    
    logger.info("=" * 60)
    logger.info("Validation Complete!")
    logger.info(f"Report: {report_path}")
    logger.info(f"Corrected BibTeX: {corrected_bib_path}")
    logger.info(f"Detailed Results: {json_path}")
    logger.info("=" * 60)
    
    return results

# ===========================
# ENTRY POINT
# ===========================

if __name__ == "__main__":
    try:
        # Check if BibTeX file exists
        if not Path(BIB_FILE_PATH).exists():
            logger.error(f"BibTeX file not found: {BIB_FILE_PATH}")
            logger.info("Please update BIB_FILE_PATH in the configuration section")
            exit(1)
        
        # Run validation
        results = validate_citations(BIB_FILE_PATH, MAIN_DOC_PATH)
        
        # Print summary
        total = len(results)
        valid = sum(1 for r in results if r.status == 'valid')
        print(f"\n✅ Validation Summary: {valid}/{total} citations validated successfully")
        
    except KeyboardInterrupt:
        logger.info("Validation interrupted by user")
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)