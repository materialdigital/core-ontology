#!/usr/bin/env python3
"""
run_all.py - Batch builder for PMDco documentation

This script loops through all markdown files in the Md_docs folder and generates
HTML documentation for each one. It reads the navigator.yaml configuration to determine
which files to process and their corresponding output names.

Usage:
    python run_all.py
    
    # Or with custom directories:
    python run_all.py --md-dir ../Md_docs --out-dir ../output
"""

import argparse
import subprocess
import sys
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

import shutil

def copy_assets(src_dir: Path, out_dir: Path, verbose: bool = False) -> None:
    """Copy static assets to output directory."""
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



def load_navigator_config(yaml_path: Path) -> dict:
    """Load navigator.yaml configuration."""
    if not YAML_AVAILABLE:
        print("Error: pyyaml is required. Install with: pip install pyyaml")
        sys.exit(1)
    
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def build_all(
    md_dir: Path = None,
    out_dir: Path = None,
    diagrams_root: Path = None,
    verbose: bool = True
) -> dict:
    """
    Build all HTML documentation from markdown files.
    
    Reads navigator.yaml to get the list of pages to build.
    Each page must have 'md' (markdown source) and 'href' (HTML output) fields.
    
    Args:
        md_dir: Directory containing markdown files (default: ../Md_docs relative to script)
        out_dir: Output directory for HTML files (default: ../output relative to script)
        diagrams_root: Root directory for pattern diagrams (default: parent of script)
        verbose: Print progress messages
    
    Returns:
        Dictionary with 'success', 'failed', and 'skipped' lists of filenames
    """
    script_dir = Path(__file__).parent
    
    # Set default paths
    if md_dir is None:
        md_dir = script_dir.parent.parent
    if out_dir is None:
        out_dir = script_dir.parent / "HTML_Docs"
    if diagrams_root is None:
        diagrams_root = script_dir.parent.parent
    
    # Ensure output directory exists
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Path to build_all.py
    build_script = script_dir / "build_all.py"
    if not build_script.exists():
        print(f"Error: build_all.py not found at {build_script}")
        return {'success': [], 'failed': [], 'skipped': []}
    
    # Load navbar configuration
    navigator_path = md_dir / "navigator.yaml"
    if not navigator_path.exists():
        print(f"Error: navigator.yaml not found at {navigator_path}")
        return {'success': [], 'failed': [], 'skipped': []}
    
    config = load_navigator_config(navigator_path)
    
    # Track results
    results = {
        'success': [],
        'failed': [],
        'skipped': []
    }
    
    # Collect all pages from navbar config with their md sources
    pages_to_build = []
    for section in config.get('sections', []):
        for page in section.get('pages', []):
            href = page.get('href', '')
            md = page.get('md', '')  # Use 'md' field directly from navigator.yaml
            if href and md:
                pages_to_build.append({'href': href, 'md': md})
            elif href:
                # Fallback: try to guess if 'md' not specified
                pages_to_build.append({'href': href, 'md': None})
    
    if verbose:
        print(f"=" * 60)
        print(f"PMDco Documentation Builder")
        print(f"=" * 60)
        print(f"Markdown source: {md_dir}")
        print(f"HTML output: {out_dir}")
        print(f"Pages to build: {len(pages_to_build)}")
        print(f"=" * 60)
    
    # Copy assets
    if verbose:
        print("Copying assets...")
    copy_assets(md_dir, out_dir, verbose)
    
    # Build each page
    for i, page_info in enumerate(pages_to_build, 1):
        href = page_info['href']
        md_name = page_info['md']
        out_file = out_dir / href
        
        # Get markdown file path from 'md' field in navigator.yaml
        if md_name:
            md_file = md_dir / md_name
            if not md_file.exists():
                if verbose:
                    print(f"[{i}/{len(pages_to_build)}] SKIP: {href} (md file not found: {md_name})")
                results['skipped'].append(href)
                continue
        else:
            if verbose:
                print(f"[{i}/{len(pages_to_build)}] SKIP: {href} (no 'md' field in navigator.yaml)")
            results['skipped'].append(href)
            continue
        
        if verbose:
            print(f"[{i}/{len(pages_to_build)}] Building: {md_file.name} -> {href}")
        
        # Determine if this is a patterns page (needs special handling)
        is_patterns = href == 'patterns.html'
        
        # Build command
        cmd = [
            sys.executable,
            str(build_script),
            "--markdown", str(md_file),
            "--out", str(out_file),
        ]
        
        if is_patterns:
            cmd.extend(["--mode", "patterns", "--diagrams-root", str(diagrams_root)])
        
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
                    print(f"         [FAIL] Failed: {result.stderr.strip()[:100]}")
        
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
            import json
            json.dump(search_index, f, ensure_ascii=False)
        print(f"  Search index: {index_path.name} ({len(search_index)} entries)")
    
    # Print summary
    if verbose:
        print(f"\n" + "=" * 60)
        print(f"BUILD COMPLETE")
        print(f"=" * 60)
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


def generate_search_index(md_dir: Path, config: dict, out_dir: Path) -> list:
    """Generate a comprehensive search index from all markdown files.
    
    Returns a list of search entries with title, content, section, href, and headings.
    Each heading also includes a content snippet for better cross-page section search.
    """
    import re
    import html
    
    def clean_markdown(text: str) -> str:
        """Remove markdown syntax from text."""
        text = re.sub(r'```[\s\S]*?```', '', text)  # Remove code blocks
        text = re.sub(r'`[^`]+`', '', text)  # Remove inline code
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links to text
        text = re.sub(r'<!--[\s\S]*?-->', '', text)  # Remove HTML comments
        text = re.sub(r'[#*_~`>\[\]|]', '', text)  # Remove markdown chars
        text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace
        return text
    
    index = []
    
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
                content = md_path.read_text(encoding='utf-8')
                
                # Extract headings with their section content for better search
                headings = []
                heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
                matches = list(heading_pattern.finditer(content))
                
                for i, match in enumerate(matches):
                    heading_level = len(match.group(1))
                    heading_text = match.group(2).strip()
                    
                    # Create slug from heading
                    slug = re.sub(r'[^\w\s-]', '', heading_text.lower())
                    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
                    
                    # Extract content between this heading and the next
                    start_pos = match.end()
                    end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(content)
                    section_content = content[start_pos:end_pos].strip()
                    
                    # Clean and truncate section content for search
                    clean_section = clean_markdown(section_content)
                    section_snippet = clean_section[:500] if len(clean_section) > 500 else clean_section
                    
                    headings.append({
                        'text': heading_text,
                        'slug': slug,
                        'content': section_snippet
                    })
                
                # Clean full content for page-level indexing
                clean_content = clean_markdown(content)
                
                # Truncate content for reasonable index size (keep first 2000 chars)
                indexed_content = clean_content[:2000] if len(clean_content) > 2000 else clean_content
                
                index.append({
                    'title': title,
                    'href': href,
                    'section': section_title,
                    'content': indexed_content,
                    'headings': headings,
                    'type': 'page'
                })
                
            except Exception as e:
                print(f"  Warning: Failed to index {md_name}: {e}")
    
    return index





def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Build all PMDco documentation HTML files from markdown sources."
    )
    parser.add_argument(
        "--md-dir",
        type=Path,
        default=None,
        help="Directory containing markdown files (default: ../Md_docs)"
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
        help="Root directory for pattern diagrams (default: parent of script)"
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
