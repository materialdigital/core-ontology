#!/usr/bin/env python3
"""
run_all.py - Batch Documentation Builder for PMDco
===================================================

This script serves as the main entry point for building the complete PMDco
documentation website. It orchestrates the build process by reading the
navigator.yaml configuration and invoking build_all.py for each documentation
page.

Architecture Overview
---------------------
The build pipeline consists of three main components:

1. **run_all.py** (this file) - Orchestration layer
   - Reads navigator.yaml to discover all pages
   - Manages build order and dependencies
   - Generates cross-page search index
   - Copies static assets to output directory

2. **build_all.py** - Page builder
   - Transforms markdown to HTML
   - Processes special tags (@module_indicator, @Graphviz_renderer, etc.)
   - Generates interactive components (trees, diagrams)

3. **ttl_to_graphviz.py** - Diagram generator
   - Converts TTL/RDF files to Graphviz DOT format
   - Provides ontology label resolution and hierarchy expansion

Directory Structure
-------------------
Expected project layout::

    docs/
    ├── navigator.yaml          # Site structure configuration
    ├── *.md                    # Markdown source files
    ├── Logo.svg                # Static assets
    └── docs_HTML/
        ├── scripts/
        │   ├── run_all.py      # This file
        │   ├── build_all.py    # Page builder
        │   └── ttl_to_graphviz.py  # Diagram generator
        └── HTML_Docs/          # Output directory (generated)
            ├── *.html          # Generated HTML pages
            ├── search-index.json  # Cross-page search data
            └── Logo.svg        # Copied assets

Usage Examples
--------------
Build all documentation with default paths::

    python run_all.py

Build with custom directories::

    python run_all.py --md-dir ../Md_docs --out-dir ../output

Quiet mode (suppress progress messages)::

    python run_all.py --quiet

Dependencies
------------
Required:
    - Python 3.8+
    - pyyaml (for navigator.yaml parsing)
    - markdown2 (used by build_all.py)

Optional:
    - rdflib (for RDF/OWL parsing in build_all.py)

Exit Codes
----------
    0 - All pages built successfully
    1 - One or more pages failed to build

Author: PMDco Documentation Team
License: CC BY 4.0
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# =============================================================================
# YAML DEPENDENCY HANDLING
# =============================================================================
# PyYAML is required for reading navigator.yaml configuration.
# The script will exit with an error if YAML is not available.
# =============================================================================

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# =============================================================================
# ASSET MANAGEMENT
# =============================================================================

def copy_assets(src_dir: Path, out_dir: Path, verbose: bool = False) -> None:
    """Copy static assets (images, logos, etc.) to the output directory.

    This function copies essential static files that are referenced by the
    generated HTML pages. Currently copies the PMDco logo which appears in
    the site header.

    Args:
        src_dir: Source directory containing the original asset files.
            Typically the docs/ directory containing markdown sources.
        out_dir: Destination directory for the HTML output.
            Assets are copied to the root of this directory.
        verbose: If True, print progress messages for each copied file.
            Also prints warnings for missing assets.

    Note:
        Missing assets are logged as warnings but do not cause build failure.
        This allows the build to continue even if optional assets are absent.

    Example:
        >>> copy_assets(Path("docs"), Path("output"), verbose=True)
          Copied asset: Logo.svg
    """
    # List of static assets to copy
    # Add new assets here as needed (e.g., favicon.ico, custom fonts)
    assets = ['Logo.svg']

    for asset in assets:
        src = src_dir / asset
        if src.exists():
            dest = out_dir / asset
            shutil.copy2(src, dest)
            if verbose:
                print(f"  Copied asset: {asset}")
        elif verbose:
            print(f"  Warning: Asset not found: {asset} in {src_dir}")


# =============================================================================
# CONFIGURATION LOADING
# =============================================================================

def load_navigator_config(yaml_path: Path) -> dict:
    """Load and parse the navigator.yaml configuration file.

    The navigator.yaml file defines the complete site structure including:
    - Navigation sections and their ordering
    - Page titles and icon assignments
    - Mapping between markdown sources and HTML outputs
    - Full ontology path for hierarchy resolution

    Args:
        yaml_path: Absolute path to the navigator.yaml file.

    Returns:
        Parsed YAML content as a Python dictionary.
        The structure typically includes:
        - 'sections': List of navigation sections with pages
        - 'icons': Icon definitions (Feather icons SVG paths)
        - 'defaults': Default icon rotation settings
        - 'full_ontology_path': URL or path to PMDco full ontology

    Raises:
        SystemExit: If PyYAML is not installed.
        FileNotFoundError: If the YAML file doesn't exist.
        yaml.YAMLError: If the YAML file contains invalid syntax.

    Example:
        >>> config = load_navigator_config(Path("docs/navigator.yaml"))
        >>> print(config['sections'][0]['title'])
        'Getting Started'
    """
    if not YAML_AVAILABLE:
        print("Error: pyyaml is required. Install with: pip install pyyaml")
        sys.exit(1)

    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# =============================================================================
# MAIN BUILD ORCHESTRATION
# =============================================================================

def build_all(
    md_dir: Optional[Path] = None,
    out_dir: Optional[Path] = None,
    diagrams_root: Optional[Path] = None,
    verbose: bool = True
) -> Dict[str, List[str]]:
    """Build all HTML documentation pages from markdown sources.

    This is the main orchestration function that coordinates the build of
    the entire documentation site. It reads the navigator.yaml configuration
    to determine which pages to build, invokes build_all.py for each page,
    and generates the cross-page search index.

    Build Process:
        1. Locate and load navigator.yaml configuration
        2. Create output directory if needed
        3. Copy static assets (Logo.svg, etc.)
        4. Build each page by invoking build_all.py subprocess
        5. Generate cross-page search index (search-index.json)
        6. Report build summary

    Args:
        md_dir: Directory containing markdown source files and navigator.yaml.
            Default: Two levels up from this script (../.. relative to scripts/).
        out_dir: Directory for generated HTML files.
            Default: ../HTML_Docs relative to scripts/.
        diagrams_root: Base directory for resolving @Graphviz_renderer paths.
            Used for patterns.html which references TTL pattern files.
            Default: Same as md_dir.
        verbose: If True, print detailed progress messages including:
            - File paths and sizes
            - Success/failure status for each page
            - Build summary statistics

    Returns:
        Dictionary with three keys:
        - 'success': List of successfully built HTML filenames
        - 'failed': List of filenames that failed to build
        - 'skipped': List of filenames skipped (missing markdown source)

    Example:
        >>> results = build_all(verbose=True)
        ============================================================
        PMDco Documentation Builder
        ============================================================
        Markdown source: /path/to/docs
        HTML output: /path/to/docs/docs_HTML/HTML_Docs
        Pages to build: 14
        ============================================================
        [1/14] Building: index.md -> index.html
                 [OK] Generated (195.2 KB)
        ...
        ============================================================
        BUILD COMPLETE
        ============================================================
        [OK] Success: 14 files
        [X]  Failed:  0 files
        [O]  Skipped: 0 files
    """
    script_dir = Path(__file__).parent

    # Set default paths relative to script location
    if md_dir is None:
        md_dir = script_dir.parent.parent  # docs/ directory
    if out_dir is None:
        out_dir = script_dir.parent / "HTML_Docs"  # docs_HTML/HTML_Docs/
    if diagrams_root is None:
        diagrams_root = script_dir.parent.parent  # Same as md_dir

    # Create output directory if it doesn't exist
    out_dir.mkdir(parents=True, exist_ok=True)

    # Locate build_all.py in the same directory as this script
    build_script = script_dir / "build_all.py"
    if not build_script.exists():
        print(f"Error: build_all.py not found at {build_script}")
        return {'success': [], 'failed': [], 'skipped': []}

    # Load navigation configuration
    navigator_path = md_dir / "navigator.yaml"
    if not navigator_path.exists():
        print(f"Error: navigator.yaml not found at {navigator_path}")
        return {'success': [], 'failed': [], 'skipped': []}

    config = load_navigator_config(navigator_path)

    # Initialize result tracking
    results = {
        'success': [],
        'failed': [],
        'skipped': []
    }

    # Extract all pages from navigator.yaml sections
    # Each page entry should have 'md' (source) and 'href' (output) fields
    pages_to_build = []
    for section in config.get('sections', []):
        for page in section.get('pages', []):
            href = page.get('href', '')
            md = page.get('md', '')  # Markdown source filename
            if href and md:
                pages_to_build.append({'href': href, 'md': md})
            elif href:
                # No 'md' field - cannot build this page
                pages_to_build.append({'href': href, 'md': None})

    # Print build header
    if verbose:
        print("=" * 60)
        print("PMDco Documentation Builder")
        print("=" * 60)
        print(f"Markdown source: {md_dir}")
        print(f"HTML output: {out_dir}")
        print(f"Pages to build: {len(pages_to_build)}")
        print("=" * 60)

    # Copy static assets to output directory
    if verbose:
        print("Copying assets...")
    copy_assets(md_dir, out_dir, verbose)

    # Build each page sequentially
    for i, page_info in enumerate(pages_to_build, 1):
        href = page_info['href']
        md_name = page_info['md']
        out_file = out_dir / href

        # Validate markdown source file exists
        if md_name:
            md_file = md_dir / md_name
            if not md_file.exists():
                if verbose:
                    print(f"[{i}/{len(pages_to_build)}] SKIP: {href} "
                          f"(md file not found: {md_name})")
                results['skipped'].append(href)
                continue
        else:
            if verbose:
                print(f"[{i}/{len(pages_to_build)}] SKIP: {href} "
                      f"(no 'md' field in navigator.yaml)")
            results['skipped'].append(href)
            continue

        if verbose:
            print(f"[{i}/{len(pages_to_build)}] Building: {md_file.name} -> {href}")

        # Determine build mode - patterns.html needs special handling
        is_patterns = href == 'patterns.html'

        # Construct build command
        cmd = [
            sys.executable,
            str(build_script),
            "--markdown", str(md_file),
            "--out", str(out_file),
        ]

        # Add patterns-specific arguments
        if is_patterns:
            cmd.extend(["--mode", "patterns", "--diagrams-root", str(diagrams_root)])

        # Execute build command
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(script_dir)
            )

            if result.returncode == 0:
                results['success'].append(href)
                if verbose and out_file.exists():
                    size_kb = out_file.stat().st_size / 1024
                    print(f"         [OK] Generated ({size_kb:.1f} KB)")
            else:
                results['failed'].append(href)
                if verbose:
                    # Truncate error message for readability
                    error_msg = result.stderr.strip()[:100]
                    print(f"         [FAIL] Failed: {error_msg}")

        except Exception as e:
            results['failed'].append(href)
            if verbose:
                print(f"         [ERROR] Error: {e}")

    # Generate cross-page search index
    if results['success'] and verbose:
        print(f"\n" + "-" * 60)
        print("Generating search index...")
        print("-" * 60)
        search_index = generate_search_index(md_dir, config, out_dir)
        index_path = out_dir / "search-index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(search_index, f, ensure_ascii=False)
        print(f"  Search index: {index_path.name} ({len(search_index)} entries)")

    # Print build summary
    if verbose:
        print(f"\n" + "=" * 60)
        print("BUILD COMPLETE")
        print("=" * 60)
        print(f"[OK] Success: {len(results['success'])} files")
        print(f"[X]  Failed:  {len(results['failed'])} files")
        print(f"[O]  Skipped: {len(results['skipped'])} files")

        if results['failed']:
            print(f"\nFailed files:")
            for f in results['failed']:
                print(f"  - {f}")

        if results['skipped']:
            print(f"\nSkipped files (no markdown source found):")
            for f in results['skipped']:
                print(f"  - {f}")

        print(f"\nOutput directory: {out_dir}")

    return results


# =============================================================================
# SEARCH INDEX GENERATION
# =============================================================================

def generate_search_index(md_dir: Path, config: dict, out_dir: Path) -> List[dict]:
    """Generate a comprehensive FULL-TEXT search index from all markdown files.

    This function creates a complete, untruncated search index that enables
    sophisticated cross-page search functionality. Unlike basic search systems,
    this indexes ALL content from every page and section, allowing users to
    find any term anywhere in the documentation.

    Design Philosophy:
        - NO content truncation: Every word is searchable
        - Full section indexing: Each heading section is independently searchable
        - Keyword extraction: Technical terms, acronyms, and ontology concepts
        - Code content: Technical code examples are preserved for search
        - Hierarchical structure: Page > Section > Content

    Index Structure:
        Each page entry contains:
        - title: Page title for display
        - href: URL path to the page
        - section: Navigation section name
        - content: FULL cleaned text content of the entire page
        - keywords: Extracted technical terms and acronyms
        - headings: List of all sections with FULL content each
        - type: 'page'

        Each heading in the headings array contains:
        - text: Heading text
        - slug: URL fragment for deep linking
        - level: Heading level (1-6)
        - content: FULL content of that section

    Args:
        md_dir: Directory containing markdown source files.
        config: Parsed navigator.yaml configuration dictionary.
        out_dir: Output directory (used for logging purposes).

    Returns:
        List of search index entry dictionaries with complete content.

    Note:
        The resulting index file may be larger (typically 200-500KB for
        comprehensive documentation), but enables true full-text search
        across all documentation content.
    """

    def clean_markdown(text: str) -> str:
        """Remove markdown syntax while preserving all searchable text.

        This function cleans markdown formatting while retaining:
        - All text content including code
        - Technical terms and identifiers
        - Punctuation-separated compound terms

        Args:
            text: Raw markdown text.

        Returns:
            Clean text optimized for full-text search indexing.
        """
        # Extract and preserve code block content (important for technical docs)
        code_blocks = re.findall(r'```(?:\w+)?\n([\s\S]*?)```', text)
        code_content = ' '.join(code_blocks)

        # Remove fenced code block markers but keep inline structure
        text = re.sub(r'```(?:\w+)?\n[\s\S]*?```', ' [code] ', text)

        # Keep inline code content
        text = re.sub(r'`([^`]+)`', r' \1 ', text)

        # Convert links to text - keep both link text and URL for searchability
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 \2', text)

        # Remove HTML comments and special tags
        text = re.sub(r'<!--[\s\S]*?-->', '', text)
        text = re.sub(r'<[^>]+>', ' ', text)

        # Remove markdown formatting but keep content
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        text = re.sub(r'~~([^~]+)~~', r'\1', text)

        # Clean special chars but keep useful punctuation
        text = re.sub(r'[>\[\]|]', ' ', text)

        # Add code content back
        text = text + ' ' + code_content

        # Normalize whitespace (single spaces only)
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def extract_keywords(text: str, title: str = '') -> str:
        """Extract important keywords and technical terms for search boosting.

        Comprehensive keyword extraction including:
        - Title words (highest priority)
        - CamelCase identifiers (class names, method names)
        - Underscore-separated identifiers (variable names, constants)
        - Acronyms (technical abbreviations)
        - Known ontology vocabulary
        - Technical prefixes (pmd:, bfo:, obi:, etc.)

        Args:
            text: The full text to extract keywords from.
            title: The page/section title.

        Returns:
            Space-separated string of unique keywords.
        """
        keywords = set()

        # Add all title words (most important)
        if title:
            keywords.update(word for word in title.split() if len(word) > 2)

        # Extract CamelCase identifiers
        camel_case = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b', text)
        keywords.update(camel_case)

        # Extract underscore_separated identifiers
        underscore_words = re.findall(r'\b\w+_\w+\b', text)
        keywords.update(underscore_words)

        # Extract ALLCAPS acronyms (2+ chars)
        acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
        keywords.update(acronyms)

        # Extract prefixed terms (like pmd:Process, bfo:Entity)
        prefixed = re.findall(r'\b([a-z]+:[A-Za-z_]+)\b', text)
        keywords.update(prefixed)

        # Extract URIs/IRIs for technical searches
        uris = re.findall(r'https?://[^\s<>"]+', text)
        for uri in uris[:20]:  # Limit to prevent explosion
            # Extract meaningful parts of URIs
            parts = re.findall(r'/([A-Za-z_]+)(?:/|#|$)', uri)
            keywords.update(parts)

        # Ontology and semantic web vocabulary
        ontology_terms = [
            'ontology', 'class', 'property', 'instance', 'triple', 'subject',
            'predicate', 'object', 'RDF', 'OWL', 'SPARQL', 'TTL', 'turtle',
            'BFO', 'PMD', 'PMDco', 'SHACL', 'graph', 'node', 'edge', 'relation',
            'hierarchy', 'taxonomy', 'semantic', 'entity', 'attribute', 'axiom',
            'restriction', 'domain', 'range', 'subclass', 'superclass', 'datatype',
            'annotation', 'individual', 'namespace', 'prefix', 'IRI', 'URI',
            'literal', 'blank', 'inference', 'reasoning', 'validation', 'shape',
            'constraint', 'cardinality', 'pattern', 'module', 'import', 'export'
        ]
        text_lower = text.lower()
        for term in ontology_terms:
            if term.lower() in text_lower:
                keywords.add(term)

        # Materials science terms (PMDco specific)
        materials_terms = [
            'material', 'process', 'measurement', 'specimen', 'sample', 'device',
            'experiment', 'parameter', 'unit', 'quantity', 'value', 'metadata',
            'dataset', 'workflow', 'analysis', 'characterization', 'property'
        ]
        for term in materials_terms:
            if term.lower() in text_lower:
                keywords.add(term)

        return ' '.join(sorted(keywords))

    def extract_all_terms(text: str) -> str:
        """Extract all unique meaningful terms from text for comprehensive indexing.

        Creates a deduplicated list of all words and terms that appear in the text,
        useful for exact-match searches.

        Args:
            text: The text to process.

        Returns:
            Space-separated string of unique terms.
        """
        # Extract all word-like tokens
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9_]*\b', text)
        # Filter very short words and deduplicate
        unique_words = set(w.lower() for w in words if len(w) > 2)
        return ' '.join(sorted(unique_words))

    index = []
    total_content_size = 0
    total_sections = 0

    # Process each page defined in navigator.yaml
    for section in config.get('sections', []):
        section_title = section.get('title', '')

        for page in section.get('pages', []):
            title = page.get('title', '')
            href = page.get('href', '')
            md_name = page.get('md', '')

            if not md_name or not href:
                continue

            md_path = md_dir / md_name
            if not md_path.exists():
                continue

            try:
                raw_content = md_path.read_text(encoding='utf-8')

                # Extract headings with their FULL section content (NO TRUNCATION)
                headings = []
                heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
                matches = list(heading_pattern.finditer(raw_content))

                for i, match in enumerate(matches):
                    heading_level = len(match.group(1))
                    heading_text = match.group(2).strip()

                    # Create URL-safe slug from heading text
                    slug = re.sub(r'[^\w\s-]', '', heading_text.lower())
                    slug = re.sub(r'[-\s]+', '-', slug).strip('-')

                    # Extract FULL content between this heading and the next
                    start_pos = match.end()
                    end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(raw_content)
                    section_content = raw_content[start_pos:end_pos].strip()

                    # Clean section content - NO TRUNCATION for full-text search
                    clean_section = clean_markdown(section_content)

                    # Extract section-specific keywords
                    section_keywords = extract_keywords(section_content, heading_text)

                    headings.append({
                        'text': heading_text,
                        'slug': slug,
                        'level': heading_level,
                        'content': clean_section,  # FULL content, no truncation
                        'keywords': section_keywords
                    })
                    total_sections += 1

                # Clean FULL page content for comprehensive indexing
                clean_content = clean_markdown(raw_content)

                # Extract comprehensive keywords from full content
                keywords = extract_keywords(raw_content, title)

                # Extract all unique terms for exact-match capability
                all_terms = extract_all_terms(clean_content)

                # Add page entry with COMPLETE content
                page_entry = {
                    'title': title,
                    'href': href,
                    'section': section_title,
                    'content': clean_content,  # FULL content, no truncation
                    'keywords': keywords,
                    'terms': all_terms,  # All unique terms for exact matching
                    'headings': headings,
                    'type': 'page',
                    'headingCount': len(headings),
                    'wordCount': len(clean_content.split())
                }

                index.append(page_entry)
                total_content_size += len(clean_content)

                # Also add section content size
                for h in headings:
                    total_content_size += len(h.get('content', ''))

            except Exception as e:
                print(f"  Warning: Failed to index {md_name}: {e}")

    # Print comprehensive index statistics
    if index:
        total_words = sum(p.get('wordCount', 0) for p in index)
        print(f"  Indexed {len(index)} pages with {total_sections} sections")
        print(f"  Total indexed content: {total_content_size / 1024:.1f} KB")
        print(f"  Total searchable words: {total_words:,}")

    return index


# =============================================================================
# COMMAND-LINE INTERFACE
# =============================================================================

def main() -> int:
    """Main entry point for command-line usage.

    Parses command-line arguments and invokes the build_all() function
    with the specified configuration.

    Command-Line Arguments:
        --md-dir: Directory containing markdown files (default: ../Md_docs)
        --out-dir: Output directory for HTML files (default: ../HTML_Docs)
        --diagrams-root: Root directory for pattern diagrams (default: parent of script)
        --quiet, -q: Suppress progress output

    Returns:
        Exit code: 0 if all builds succeeded, 1 if any builds failed.

    Example:
        Command line::

            python run_all.py --md-dir ./docs --out-dir ./output --quiet

        Programmatic::

            sys.exit(main())
    """
    parser = argparse.ArgumentParser(
        description="Build all PMDco documentation HTML files from markdown sources.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all.py                          # Build with defaults
  python run_all.py --md-dir ../Md_docs      # Custom source directory
  python run_all.py -q                       # Quiet mode

The script reads navigator.yaml to determine which pages to build
and generates a search-index.json for cross-page search functionality.
        """
    )
    parser.add_argument(
        "--md-dir",
        type=Path,
        default=None,
        help="Directory containing markdown files (default: ../../ relative to script)"
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory for HTML files (default: ../HTML_Docs)"
    )
    parser.add_argument(
        "--diagrams-root",
        type=Path,
        default=None,
        help="Root directory for pattern diagrams (default: same as md-dir)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output"
    )

    args = parser.parse_args()

    results = build_all(
        md_dir=args.md_dir,
        out_dir=args.out_dir,
        diagrams_root=args.diagrams_root,
        verbose=not args.quiet
    )

    # Return non-zero exit code if any builds failed
    if results['failed']:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
