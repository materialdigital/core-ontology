#!/usr/bin/env python3
"""
build_all.py - Unified Static Site Builder for PMDCore Documentation
===================================================================

A comprehensive documentation builder that transforms markdown files into
interactive HTML pages with support for ontology visualization, diagrams,
and semantic web technologies.

Architecture Overview
---------------------
This script is the main page builder in the PMDCore documentation pipeline:

1. **run_all.py** - Batch orchestrator (calls this script for each page)
2. **build_all.py** (this file) - Individual page builder
3. **ttl_to_graphviz.py** - TTL to diagram conversion (used by patterns mode)

The builder supports two primary modes:

1. **Docs Mode**: Standard documentation pages with:
   - Interactive ontology class trees
   - Property hierarchy trees
   - Remote content injection

2. **Patterns Mode**: Pattern visualization pages with:
   - Auto-generated Graphviz diagrams from TTL files
   - SHACL constraint visualization
   - Interactive pan/zoom viewers

Usage Examples
--------------
Auto-detect mode based on content (recommended)::

    python build_all.py --markdown input.md --out output.html

Explicit docs mode::

    python build_all.py --mode docs --markdown Md_docs/index.md --out output/index.html

Explicit patterns mode with TTL diagram source::

    python build_all.py --mode patterns --markdown patterns.md \\
        --diagrams-root ./patterns --out patterns.html

Supported Markdown Extensions
-----------------------------
Ontology Visualization:
    ``@module_indicator:URL``
        Fetch OWL file from URL and generate interactive class hierarchy tree.
        Example: <!--@module_indicator:https://example.org/ontology.owl-->

    ``@property_indicator:TYPE``
        Generate property tree where TYPE is 'object', 'data', or 'annotation'.
        Example: <!--@property_indicator:object-->

Diagram Rendering:
    ``@Graphviz_renderer:PATH``
        Convert TTL/SHACL file at PATH to interactive Graphviz diagram.
        Requires patterns mode and --diagrams-root argument.
        Example: <!--@Graphviz_renderer:temporal-region-->

    ``@Graphviz_renderer_manual:TITLE``
        Render embedded DOT code following the tag as a Graphviz diagram.
        Works in any mode without external TTL files.
        Example:
            <!--@Graphviz_renderer_manual: My Diagram -->
            ```dot
            digraph G { A -> B }
            ```

    ``@Mermaid_renderer_manual:TITLE``
        Render embedded Mermaid code following the tag as a diagram.
        Works in any mode without external dependencies.
        Example:
            <!--@Mermaid_renderer_manual: Process Flow -->
            ```mermaid
            graph TD
                A --> B
            ```

Content Injection:
    ``@md_file_renderer:URL``
        Fetch markdown from URL and inject inline before HTML conversion.
        Example: <!--@md_file_renderer:https://example.org/section.md-->

    ``@source_code_renderer:URL``
        Fetch source code from URL and inject as fenced code block.
        Language is auto-detected from file extension.
        Example: <!--@source_code_renderer:https://example.org/example.ttl-->

Output Features
---------------
Layout:
    - Responsive design with mobile-first sidebar
    - Header with logo, navigation links, and theme toggle
    - Sidebar with search and hierarchical navigation
    - Table of contents (TOC) with scroll-spy highlighting
    - Previous/next page navigation

Interactivity:
    - Light/dark theme toggle with localStorage persistence
    - Full-text search with fuzzy matching and result highlighting
    - Collapsible ontology/property trees with expand/collapse all
    - Pan/zoom diagrams with mouse wheel and drag
    - SVG and PNG export for all diagrams
    - Fullscreen diagram viewer
    - Node tooltips with URI information

Directory Structure
-------------------
Expected project layout::

    docs/
    ├── navigator.yaml          # Site structure configuration
    ├── *.md                    # Markdown source files
    ├── patterns/               # TTL pattern files (for patterns mode)
    │   ├── *.ttl              # Individual pattern definitions
    │   └── *_full.ttl         # Full ontology for label resolution
    └── docs_HTML/
        ├── scripts/
        │   ├── run_all.py     # Batch orchestrator
        │   ├── build_all.py   # This file
        │   └── ttl_to_graphviz.py  # Diagram generator
        └── HTML_Docs/         # Generated output

Dependencies
------------
Required:
    - Python 3.8+
    - markdown2: Markdown to HTML conversion

Optional (for full functionality):
    - rdflib: RDF/XML, Turtle, OWL parsing for ontology trees
    - pyyaml: navigator.yaml configuration loading

Configuration
-------------
The navigator.yaml file controls site structure:

.. code-block:: yaml

    schema: "pmdco-nav/v1"
    full_ontology_path: "https://raw.githubusercontent.com/..."
    sections:
      - id: getting-started
        title: "Getting Started"
        pages:
          - title: Home
            href: index.html
            md: index.md
            icon: home

Exit Codes
----------
    0 - Page built successfully
    1 - Build failed (invalid arguments, missing files, etc.)

Author: PMDCore Team
License: CC BY 4.0
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
import importlib.util
import sys
import tempfile
import html as html_module
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from collections import defaultdict

try:
    import markdown2
except ImportError:
    raise ImportError("markdown2 is required. Install with: pip install markdown2")

try:
    from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef, Literal
    from rdflib.namespace import SKOS
    RDFLIB_AVAILABLE = True
except ImportError:
    RDFLIB_AVAILABLE = False

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("Warning: pyyaml not available. Install with: pip install pyyaml")


# =============================================================================
# SECTION 1: NAVIGATION AND SIDEBAR CONFIGURATION
# =============================================================================
# Functions for loading navigator.yaml and generating dynamic sidebar HTML,
# page navigation, and search index. The navigator.yaml file defines the
# site structure, page titles, and icon assignments.
# =============================================================================

# Global cache for navigator configuration (loaded once per process)
_NAVIGATOR_CONFIG = None

def get_feather_icon_svg(icon_name: str, navigator_config: dict) -> str:
    """Generate inline SVG markup for a Feather icon.

    Looks up the icon definition in navigator.yaml's icons section and
    generates the corresponding SVG element. Icons are rendered at 18x18px
    with stroke-based rendering (no fill).

    Args:
        icon_name: The icon identifier (e.g., 'home', 'file-text', 'book').
        navigator_config: The parsed navigator.yaml configuration dict.

    Returns:
        SVG element string ready for HTML embedding. Falls back to a
        default file icon if the specified icon is not found.

    Note:
        Icon paths in navigator.yaml support multi-path definitions
        separated by ' M' for complex icons composed of multiple shapes.
    """
    icons = navigator_config.get('icons', {})
    icon_data = icons.get(icon_name, {})
    path_data = icon_data.get('path', '')
    
    if not path_data:
        # Fallback to a default file icon
        path_data = "M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z M14 2v6h6"
    
    # Convert path string to SVG elements (multiple paths separated by space+M)
    paths = []
    for p in path_data.split(' M'):
        if not p.startswith('M'):
            p = 'M' + p
        paths.append(f'<path d="{p}"></path>')
    
    return f'''<svg fill="none" height="18" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" width="18">
    {''.join(paths)}
</svg>'''


def load_NAVIGATOR_CONFIG(script_dir: Path = None) -> dict:
    """Load and cache the navigator.yaml configuration.

    Searches for navigator.yaml in multiple locations relative to the
    script directory and caches the result for subsequent calls.

    Search order:
        1. {script_dir}/../../navigator.yaml (docs/ directory)
        2. {script_dir}/../Md_docs/navigator.yaml
        3. {script_dir}/../navigator.yaml
        4. {script_dir}/navigator.yaml

    Args:
        script_dir: Base directory for path resolution. Defaults to the
            directory containing this script.

    Returns:
        Parsed YAML configuration as a dictionary. Returns empty dict
        if YAML is unavailable or the file cannot be found/parsed.

    Note:
        Results are cached globally (_NAVIGATOR_CONFIG) to avoid
        repeated file I/O across multiple page builds.
    """
    global _NAVIGATOR_CONFIG
    
    if _NAVIGATOR_CONFIG is not None:
        return _NAVIGATOR_CONFIG
    
    if not YAML_AVAILABLE:
        print("  Warning: YAML not available, using fallback sidebar")
        return {}
    
    if script_dir is None:
        script_dir = Path(__file__).parent
    
    # Try multiple possible locations for navigator.yaml
    yaml_paths = [
        script_dir.parent.parent / "navigator.yaml",
        script_dir.parent / "Md_docs" / "navigator.yaml",
        script_dir.parent / "navigator.yaml",
        script_dir / "navigator.yaml",
    ]
    
    yaml_path = None
    for p in yaml_paths:
        if p.exists():
            yaml_path = p
            break
    
    if yaml_path is None:
        print("  Warning: navigator.yaml not found, using fallback sidebar")
        return {}
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            _NAVIGATOR_CONFIG = yaml.safe_load(f)
        print(f"  Loaded navbar configuration from: {yaml_path.name}")
        return _NAVIGATOR_CONFIG
    except Exception as e:
        print(f"  Warning: Failed to load navigator.yaml: {e}")
        return {}


def generate_sidebar_html(active_page: str = None, script_dir: Path = None) -> str:
    """Generate dynamic sidebar navigation HTML from navigator.yaml.

    Creates a hierarchical navigation menu organized by sections, with
    visual indicators for the currently active page and icons for each
    navigation item.

    Args:
        active_page: Filename of the currently active page (e.g., 'index.html').
            Used to apply the 'active' CSS class for visual highlighting.
        script_dir: Base directory for loading navigator.yaml configuration.

    Returns:
        Complete HTML string for the sidebar navigation, wrapped in a
        <nav class="nav-sections"> element. Falls back to a minimal
        single-link sidebar if navigator.yaml is unavailable.

    Generated Structure:
        <nav class="nav-sections">
          <div class="nav-section">
            <h3 class="nav-section-title">Section Name</h3>
            <ul class="nav-list">
              <li><a class="nav-link [active]" href="...">...</a></li>
            </ul>
          </div>
        </nav>
    """
    config = load_NAVIGATOR_CONFIG(script_dir)
    
    if not config:
        # Return a minimal fallback sidebar
        return '''<nav class="nav-sections">
            <div class="nav-section">
                <h3 class="nav-section-title">Navigation</h3>
                <ul class="nav-list">
                    <li><a class="nav-link" href="./index.html">Home</a></li>
                </ul>
            </div>
        </nav>'''
    
    sections = config.get('sections', [])
    
    # Get default icons (supports both old single icon and new rotating list)
    defaults = config.get('defaults', {})
    if isinstance(defaults.get('icons'), list):
        default_icons = defaults['icons']
    else:
        # Fallback to single icon or file-text
        default_icons = [defaults.get('icon', 'file-text')]
    
    html_parts = ['<nav class="nav-sections">']
    
    # Global page counter for rotating icons
    page_index = 0
    
    for section in sections:
        section_title = section.get('title', 'Section')
        pages = section.get('pages', [])
        
        html_parts.append(f'''
            <div class="nav-section">
                <h3 class="nav-section-title">{html_module.escape(section_title)}</h3>
                <ul class="nav-list">''')
        
        for page in pages:
            title = page.get('title', 'Page')
            href = page.get('href', '#')
            
            # Use explicit icon or rotate through defaults
            if 'icon' in page:
                icon_name = page['icon']
            else:
                icon_name = default_icons[page_index % len(default_icons)]
            
            # Normalize href for comparison
            href_normalized = href.replace('./', '').replace('\\', '/')
            active_normalized = (active_page or '').replace('./', '').replace('\\', '/')
            
            is_active = href_normalized == active_normalized
            active_class = ' active' if is_active else ''
            
            icon_svg = get_feather_icon_svg(icon_name, config)
            
            html_parts.append(f'''
                    <li><a class="nav-link{active_class}" href="./{html_module.escape(href)}">
                            {icon_svg}
                            {html_module.escape(title)}
                        </a></li>''')
            
            page_index += 1
        
        html_parts.append('''
                </ul>
            </div>''')
    
    html_parts.append('</nav>')
    return ''.join(html_parts)


def generate_search_index_json(script_dir: Path = None) -> str:
    """Generate JSON search index from navigator.yaml for cross-page search."""
    config = load_NAVIGATOR_CONFIG(script_dir)
    
    if not config:
        return '[]'
    
    index = []
    sections = config.get('sections', [])
    
    for section in sections:
        section_title = section.get('title', '')
        pages = section.get('pages', [])
        
        for page in pages:
            index.append({
                'title': page.get('title', ''),
                'href': page.get('href', ''),
                'section': section_title,
                'type': 'page'
            })
    
    return json.dumps(index)


def generate_page_nav_html(active_page: str, script_dir: Path = None) -> str:
    """Generate previous/next page navigation HTML based on navigator.yaml order."""
    config = load_NAVIGATOR_CONFIG(script_dir)
    
    if not config:
        return '<nav class="page-nav"></nav>'
    
    # Flatten all pages into a single ordered list
    all_pages = []
    for section in config.get('sections', []):
        for page in section.get('pages', []):
            href = page.get('href', '')
            title = page.get('title', '')
            if href and title:
                all_pages.append({'href': href, 'title': title})
    
    # Find current page index
    active_normalized = (active_page or '').replace('./', '').replace('\\', '/')
    current_index = -1
    
    for i, page in enumerate(all_pages):
        page_href = page['href'].replace('./', '').replace('\\', '/')
        if page_href == active_normalized:
            current_index = i
            break
    
    if current_index == -1:
        return '<nav class="page-nav"></nav>'
    
    # Get previous and next pages
    prev_page = all_pages[current_index - 1] if current_index > 0 else None
    next_page = all_pages[current_index + 1] if current_index < len(all_pages) - 1 else None
    
    # Build navigation HTML
    nav_parts = ['<nav class="page-nav">']
    
    if prev_page:
        nav_parts.append(f'''
                <a class="page-nav-link prev" href="./{html_module.escape(prev_page['href'])}">
                    <span class="page-nav-label">&larr; Previous</span>
                    <span class="page-nav-title">{html_module.escape(prev_page['title'])}</span>
                </a>''')
    else:
        nav_parts.append('<div></div>')  # Empty placeholder for grid layout
    
    if next_page:
        nav_parts.append(f'''
                <a class="page-nav-link next" href="./{html_module.escape(next_page['href'])}">
                    <span class="page-nav-label">Next &rarr;</span>
                    <span class="page-nav-title">{html_module.escape(next_page['title'])}</span>
                </a>''')
    else:
        nav_parts.append('<div></div>')  # Empty placeholder for grid layout
    
    nav_parts.append('</nav>')
    return ''.join(nav_parts)


# =============================================================================
# SECTION 2: HTML TEMPLATE
# =============================================================================
# The main HTML template containing:
# - CSS variables and theme definitions (light/dark mode)
# - Layout styles (header, sidebar, content area, TOC)
# - Interactive component styles (trees, graphs, search modal)
# - JavaScript for Graphviz rendering, pan/zoom, search, and theme toggle
#
# Placeholders replaced during build:
# - __SIDEBAR_HTML__: Dynamic navigation from navigator.yaml
# - __ARTICLE_CONTENT__: Rendered markdown content
# - __TOC_LIST_ITEMS__: Table of contents links
# - __PAGE_NAV__: Previous/next page navigation
# - __DIAGRAMS_OBJECT__: Graphviz DOT source code (patterns mode)
# - __NODEDATA_OBJECT__: Node metadata for graph tooltips (patterns mode)
# =============================================================================

TEMPLATE_HTML = r'''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8" />
    <meta content="width=device-width, initial-scale=1.0" name="viewport" />
    <meta content="Usage Patterns - PMDco Documentation" name="description" />
    <title>Usage Patterns | PMDco Documentation</title>
    <link href="https://fonts.googleapis.com" rel="preconnect" />
    <link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect" />
    <link
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Merriweather:wght@400;700&family=Source+Serif+Pro:wght@400;600;700&display=swap"
        rel="stylesheet" />
    <style>
        /* =====================================================
       PMDco DOCUMENTATION STYLES
       =====================================================
       
       OVERVIEW:
       This stylesheet controls the entire documentation appearance including:
       - CSS Variables (lines ~15-100): Color themes, spacing, typography
       - Theme switching (lines ~80-180): Light/dark mode overrides
       - Layout components: Header, Sidebar, Main content, TOC
       - Mermaid graph containers: Interactive diagram styling
       - Edge/Arrow colors: Theme-dependent stroke colors
       - Edge labels: Theme-dependent text colors (black in light, white in dark)
       
       KEY PATTERNS:
       - Use CSS variables (--color-*) for consistent theming
       - body:not(.theme-dark) class toggles light mode styles
       - Graph edges use !important to override Mermaid defaults
       
       CRITICAL SECTIONS:
       - Lines ~125-180: Edge and arrow color overrides for light/dark modes
       - Lines ~825-875: Edge label color overrides for light/dark modes
       
       ===================================================== */

        /* === CSS VARIABLES - Core design tokens === */
        :root {
            --color-primary: #00a0e3;
            --color-primary-dark: #0077b3;
            --color-primary-light: #33b5eb;
            --color-accent: #7dd3fc;
            --color-surface: rgba(255, 255, 255, 0.92);
            --color-bg-primary: #f7f9fc;
            --color-bg-secondary: #ffffff;
            --color-bg-tertiary: #edf2f7;
            --color-bg-card: #ffffff;
            --color-bg-hover: rgba(0, 160, 227, 0.08);
            --color-text-primary: #0f172a;
            --color-text-secondary: #1f2937;
            --color-text-muted: #475569;
            --color-border: rgba(15, 23, 42, 0.1);
            --color-border-hover: rgba(0, 160, 227, 0.5);
            --color-success: #10b981;
            --color-warning: #f59e0b;
            --color-error: #ef4444;
            --color-info: #3b82f6;
            --color-code-bg: #f3f4f6;
            --spacing-xs: 0.25rem;
            --spacing-sm: 0.5rem;
            --spacing-md: 1rem;
            --spacing-lg: 1.5rem;
            --spacing-xl: 2rem;
            --spacing-2xl: 3rem;
            --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-family-heading: 'Source Serif Pro', Georgia, 'Times New Roman', serif;
            --font-family-body: 'Merriweather', Georgia, serif;
            --font-family-mono: 'JetBrains Mono', monospace;
            --font-size-xs: 0.75rem;
            --font-size-sm: 0.875rem;
            --font-size-base: 1rem;
            --font-size-lg: 1.125rem;
            --font-size-xl: 1.25rem;
            --font-size-2xl: 1.5rem;
            --font-size-3xl: 1.875rem;
            --font-size-4xl: 2.25rem;
            --radius-sm: 0.25rem;
            --radius-md: 0.5rem;
            --radius-lg: 0.75rem;
            --radius-xl: 1rem;
            --radius-full: 9999px;
            --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
            --shadow-glow: 0 0 20px rgba(0, 160, 227, 0.3);
            --transition-fast: 150ms ease;
            --transition-normal: 250ms ease;
            --sidebar-width: 280px;
            --header-height: 64px;
            --toc-width: 240px;
            --z-sticky: 200;
            --z-modal: 300;
            --z-tooltip: 400;

            /* Mermaid graph variables */
            --dim: 0.12;
            --pop-header: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
            --pop-header-text: #ffffff;
            --card-bg: #f1f5f9;
            --card-border: #cbd5e1;
            --card-hover: #e2e8f0;
            --pred-color: #0079BA;  /* EXACT Protege blue for object properties */
            --val-color: #1e293b;
        }

        body.theme-dark {
            --color-bg-primary: #0a1628;
            --color-bg-secondary: #0d1f35;
            --color-bg-tertiary: #132743;
            --color-bg-card: rgba(19, 39, 67, 0.8);
            --color-bg-hover: rgba(0, 160, 227, 0.1);
            --color-surface: rgba(10, 22, 40, 0.95);
            --color-text-primary: #ffffff;
            --color-text-secondary: #94a3b8;
            --color-text-muted: #64748b;
            --color-border: rgba(148, 163, 184, 0.2);
            --color-code-bg: #1e293b;
            --card-bg: #0f172a;
            --card-border: #475569;
            --card-hover: #334155;
            --pred-color: #5BC0EB;  /* Lighter Protege blue for dark mode visibility */
            --val-color: #e2e8f0;
        }

        /* ===========================================
       LIGHT MODE GRAPH CONTAINER OVERRIDES
       Pure white backgrounds per user preference.
       Ensures clean, professional appearance for diagrams.
       =========================================== */
        body:not(.theme-dark) .mermaid-graph-container {
            background: #ffffff;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        body:not(.theme-dark) .graph-header {
            background: #ffffff;
        }

        body:not(.theme-dark) .graph-viewport {
            background: #ffffff;
        }

        body:not(.theme-dark) .graph-legend {
            background: #ffffff;
        }

        body:not(.theme-dark) .zoom-controls {
            background: #ffffff;
        }

        body:not(.theme-dark) .zoom-btn {
            background: #f8fafc;
        }

        /* ===========================================
       EDGE AND ARROW COLOR OVERRIDES
       =========================================== 
       
       CRITICAL: These styles override Mermaid's default edge colors
       to ensure proper visibility in both light and dark themes.
       
       Dark mode (default): White edges (#ffffff) on dark backgrounds
       Light mode: Black edges (#1e293b) on white backgrounds
       
       The !important flag is necessary to override Mermaid's inline styles.
       
       Components affected:
       - path.flowchart-link: Main edge lines connecting nodes
       - .edgePath path: Alternative edge path selector
       - marker path: Arrowheads at edge endpoints
       
       Both .graph-wrapper (inline view) and .fullscreen-wrapper 
       (fullscreen modal) need separate rules.
       =========================================== */

        /* DARK MODE EDGES (default) - White for visibility on dark backgrounds */
        .graph-wrapper svg path.flowchart-link {
            stroke: #ffffff !important;
        }

        .graph-wrapper svg .edgePath path {
            stroke: #ffffff !important;
        }

        /* Dark mode arrowheads */
        .graph-wrapper svg marker path {
            fill: #ffffff !important;
            stroke: #ffffff !important;
        }

        /* Fullscreen modal - dark mode edges */
        .fullscreen-wrapper svg path.flowchart-link {
            stroke: #ffffff !important;
        }

        .fullscreen-wrapper svg .edgePath path {
            stroke: #ffffff !important;
        }

        .fullscreen-wrapper svg marker path {
            fill: #ffffff !important;
            stroke: #ffffff !important;
        }

        /* LIGHT MODE EDGES - Black (#1e293b) for visibility on white backgrounds */
        body:not(.theme-dark) .graph-wrapper svg path.flowchart-link {
            stroke: #1e293b !important;
        }

        body:not(.theme-dark) .graph-wrapper svg .edgePath path {
            stroke: #1e293b !important;
        }

        /* Light mode arrowheads */
        body:not(.theme-dark) .graph-wrapper svg marker path {
            fill: #1e293b !important;
            stroke: #1e293b !important;
        }

        /* Fullscreen modal - light mode edges */
        body:not(.theme-dark) .fullscreen-wrapper svg path.flowchart-link {
            stroke: #1e293b !important;
        }

        body:not(.theme-dark) .fullscreen-wrapper svg .edgePath path {
            stroke: #1e293b !important;
        }

        body:not(.theme-dark) .fullscreen-wrapper svg marker path {
            fill: #1e293b !important;
            stroke: #1e293b !important;
        }

        *,
        *::before,
        *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            font-family: var(--font-family);
            font-size: var(--font-size-base);
            line-height: 1.5;
            color: var(--color-text-primary);
            background: var(--color-bg-primary);
            min-height: 100vh;
        }

        body::before {
            content: '';
            position: fixed;
            inset: 0;
            background: radial-gradient(circle at 20% 50%, rgba(0, 160, 227, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(0, 160, 227, 0.05) 0%, transparent 40%);
            pointer-events: none;
            z-index: -1;
        }

        /* Typography */
        h1,
        h2,
        h3,
        h4 {
            font-weight: 600;
            line-height: 1.25;
            color: var(--color-text-primary);
            margin-bottom: var(--spacing-md);
        }

        h1 {
            font-size: var(--font-size-4xl);
            font-weight: 700;
            background: linear-gradient(135deg, var(--color-text-primary), var(--color-primary-light));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        h2 {
            font-size: var(--font-size-2xl);
            margin-top: var(--spacing-2xl);
            padding-bottom: var(--spacing-sm);
            border-bottom: 1px solid var(--color-border);
        }

        h3 {
            font-size: var(--font-size-xl);
            margin-top: var(--spacing-xl);
        }

        p {
            margin-bottom: var(--spacing-md);
            color: var(--color-text-secondary);
        }

        a {
            color: var(--color-primary);
            text-decoration: none;
            transition: color var(--transition-fast);
        }

        a:hover {
            color: var(--color-primary-light);
            text-decoration: underline;
        }

        strong {
            font-weight: 600;
            color: var(--color-text-primary);
        }

        ul,
        ol {
            margin-bottom: var(--spacing-md);
            padding-left: var(--spacing-xl);
            color: var(--color-text-secondary);
        }

        code:not(pre code) {
            padding: 2px 6px;
            font-size: 0.9em;
            font-family: var(--font-family-mono);
            color: var(--color-primary-light);
            background: var(--color-code-bg);
            border-radius: var(--radius-sm);
        }

        pre {
            margin: var(--spacing-lg) 0;
            padding: var(--spacing-lg);
            background: var(--color-code-bg);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-lg);
            overflow-x: auto;
        }

        pre code {
            font-family: var(--font-family-mono);
            font-size: var(--font-size-sm);
            color: #e2e8f0;
        }

        body:not(.theme-dark) pre code {
            color: #1e293b;
        }

        body:not(.theme-dark) pre {
            background: #f8fafc;
            border-color: #e2e8f0;
        }

        hr {
            border: none;
            border-top: 1px solid var(--color-border);
            margin: var(--spacing-xl) 0;
        }

        /* Header */
        .header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: var(--header-height);
            background: var(--color-surface);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--color-border);
            z-index: var(--z-sticky);
            display: flex;
            align-items: center;
            padding: 0 var(--spacing-lg);
        }

        .header-logo {
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
            font-size: var(--font-size-lg);
            font-weight: 700;
            color: var(--color-text-primary);
        }

        .header-nav {
            display: flex;
            gap: var(--spacing-xl);
            margin-left: auto;
        }

        .header-nav a {
            font-size: var(--font-size-sm);
            font-weight: 500;
            color: var(--color-text-secondary);
        }

        .header-nav a:hover {
            color: var(--color-text-primary);
            text-decoration: none;
        }

        .theme-toggle {
            display: flex;
            align-items: center;
            gap: var(--spacing-xs);
            margin-left: var(--spacing-md);
            padding: 8px 12px;
            border-radius: var(--radius-full);
            border: 1px solid var(--color-border);
            background: var(--color-bg-secondary);
            color: var(--color-text-secondary);
            cursor: pointer;
            transition: all var(--transition-fast);
        }

        .theme-toggle:hover {
            color: var(--color-text-primary);
            border-color: var(--color-border-hover);
        }

        .theme-toggle svg {
            width: 18px;
            height: 18px;
        }

        .theme-label {
            font-size: var(--font-size-sm);
            font-weight: 500;
        }

        .mobile-menu-btn {
            display: none;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            background: transparent;
            border: none;
            color: var(--color-text-primary);
            cursor: pointer;
        }

        /* Sidebar */
        .sidebar {
            position: fixed;
            top: var(--header-height);
            left: 0;
            bottom: 0;
            width: var(--sidebar-width);
            background: var(--color-bg-secondary);
            border-right: 1px solid var(--color-border);
            overflow-y: auto;
            padding: var(--spacing-lg);
            z-index: var(--z-sticky);
        }

        .sidebar::-webkit-scrollbar {
            width: 6px;
        }

        .sidebar::-webkit-scrollbar-thumb {
            background: var(--color-border);
            border-radius: var(--radius-full);
        }

        .sidebar-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: calc(var(--z-modal) - 1);
        }

        .sidebar-overlay.active {
            display: block;
        }

        /* Navigation */
        .nav-section {
            margin-bottom: var(--spacing-md);
        }

        .nav-section-title {
            font-size: var(--font-size-xs);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--color-text-muted);
            margin-bottom: var(--spacing-xs);
        }

        .nav-list {
            list-style: none;
            padding-left: 0;
        }

        .nav-list li {
            margin-bottom: 2px;
        }

        .nav-link {
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
            padding: var(--spacing-sm) var(--spacing-md);
            font-size: var(--font-size-sm);
            color: var(--color-text-secondary);
            border-radius: var(--radius-md);
            transition: all var(--transition-fast);
        }

        .nav-link:hover {
            color: var(--color-text-primary);
            background: var(--color-bg-hover);
            text-decoration: none;
        }

        .nav-link.active {
            color: var(--color-primary);
            background: rgba(0, 160, 227, 0.15);
            font-weight: 500;
        }

        .nav-link svg {
            width: 18px;
            height: 18px;
            opacity: 0.7;
        }

        /* Search - Modern & Classic Design */
        .search-container {
            position: relative;
            margin-bottom: var(--spacing-xl);
        }

        .search-input {
            width: 100%;
            padding: 12px 16px;
            padding-left: 44px;
            padding-right: 70px;
            font-size: var(--font-size-sm);
            font-weight: 500;
            color: var(--color-text-primary);
            background: linear-gradient(135deg, var(--color-bg-tertiary) 0%, var(--color-bg-secondary) 100%);
            border: 1px solid var(--color-border);
            border-radius: 12px;
            outline: none;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
        }

        .search-input::placeholder {
            color: var(--color-text-muted);
            font-weight: 400;
        }

        .search-input:hover {
            border-color: var(--color-primary);
            background: var(--color-bg-secondary);
            box-shadow: 0 2px 8px rgba(0, 160, 227, 0.1);
        }

        .search-input:focus {
            border-color: var(--color-primary);
            background: var(--color-bg-secondary);
            box-shadow: 0 0 0 3px rgba(0, 160, 227, 0.15), 0 4px 12px rgba(0, 160, 227, 0.1);
        }

        .search-icon {
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            width: 18px;
            height: 18px;
            color: var(--color-text-muted);
            pointer-events: none;
            transition: color 0.2s;
        }

        .search-container:hover .search-icon,
        .search-input:focus ~ .search-icon {
            color: var(--color-primary);
        }

        .search-shortcut {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            padding: 4px 8px;
            font-size: 11px;
            font-family: var(--font-family-mono);
            font-weight: 600;
            letter-spacing: 0.02em;
            color: var(--color-text-muted);
            background: var(--color-bg-primary);
            border: 1px solid var(--color-border);
            border-radius: 6px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }

        /* Search Modal */
        .search-modal {
            position: fixed;
            inset: 0;
            z-index: var(--z-modal);
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(4px);
            display: none;
            align-items: flex-start;
            justify-content: center;
            padding-top: 15vh;
        }

        .search-modal.active {
            display: flex;
        }

        .search-modal-content {
            width: 100%;
            max-width: 640px;
            max-height: 70vh;
            background: var(--color-bg-secondary);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-xl);
            box-shadow: 0 20px 25px rgba(0, 0, 0, 0.6);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        .search-modal-header {
            display: flex;
            align-items: center;
            gap: var(--spacing-md);
            padding: var(--spacing-lg) var(--spacing-xl);
            border-bottom: 1px solid var(--color-border);
            background: var(--color-bg-tertiary);
        }

        .search-modal-header svg {
            flex-shrink: 0;
            color: var(--color-primary);
        }

        .search-modal-input {
            flex: 1;
            padding: var(--spacing-sm) 0;
            font-size: var(--font-size-lg);
            font-weight: 500;
            color: var(--color-text-primary);
            background: transparent;
            border: none;
            outline: none;
        }
        
        .search-modal-input::placeholder {
            color: var(--color-text-muted);
            font-weight: 400;
        }

        .search-results {
            max-height: 400px;
            overflow-y: auto;
            padding: var(--spacing-sm);
        }

        .search-result-item {
            display: block;
            padding: var(--spacing-md);
            border-radius: var(--radius-md);
            transition: background var(--transition-fast);
        }

        .search-result-item:hover,
        .search-result-item.selected {
            background: var(--color-bg-hover);
            text-decoration: none;
        }

        .search-result-title {
            font-weight: 500;
            color: var(--color-text-primary);
            margin-bottom: var(--spacing-xs);
        }

        .search-result-path {
            font-size: var(--font-size-sm);
            color: var(--color-text-muted);
        }

        .search-no-results {
            padding: var(--spacing-xl);
            text-align: center;
            color: var(--color-text-muted);
        }

        .search-section-label {
            padding: var(--spacing-sm) var(--spacing-md);
            font-size: var(--font-size-xs);
            font-weight: 600;
            color: var(--color-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid var(--color-border);
            background: var(--color-bg-tertiary);
        }

        .search-result-title mark {
            background: rgba(0, 160, 227, 0.3);
            color: var(--color-primary-light);
            padding: 0 2px;
            border-radius: 2px;
        }

        .search-footer {
            display: flex;
            justify-content: space-between;
            gap: var(--spacing-lg);
            padding: var(--spacing-sm) var(--spacing-lg);
            border-top: 1px solid var(--color-border);
            font-size: var(--font-size-xs);
            color: var(--color-text-muted);
        
            flex-wrap: wrap;}

        
        .search-index-status {
            margin-left: auto;
            white-space: nowrap;
            opacity: 0.9;
        }
.search-footer kbd {
            padding: 2px 6px;
            background: var(--color-bg-tertiary);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            font-family: var(--font-family-mono);
        }

        /* Search Target Flash - visual feedback when navigating to search result */
        .search-target-flash {
            outline: 3px solid rgba(0, 160, 227, 0.4);
            outline-offset: 4px;
            border-radius: 8px;
            transition: outline-color 0.6s ease;
            animation: flash-fade 1.5s ease-out forwards;
        }

        @keyframes flash-fade {
            0% { outline-color: rgba(0, 160, 227, 0.6); }
            100% { outline-color: transparent; }
        }

        /* Smooth scrolling for the entire page */
        html {
            scroll-behavior: smooth;
        }

        /* Enhanced focus states for accessibility */
        a:focus-visible,
        button:focus-visible,
        input:focus-visible {
            outline: 2px solid var(--color-primary);
            outline-offset: 2px;
        }

        /* Image Viewer */
        .image-viewer-overlay {
            position: fixed;
            inset: 0;
            background: rgba(255, 255, 255, 0.98);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s, visibility 0.3s;
        }

        .image-viewer-overlay.active {
            opacity: 1;
            visibility: visible;
        }

        .image-viewer-container {
            position: absolute;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: visible;
            cursor: grab;
        }

        .image-viewer-container:active {
            cursor: grabbing;
        }

        .image-viewer-container img,
        .image-viewer-container svg {
            max-width: 95vw;
            max-height: 90vh;
            width: auto;
            height: auto;
            object-fit: contain;
            transform-origin: center center;
            transition: transform 0.05s ease-out;
            user-select: none;
            -webkit-user-drag: none;
            pointer-events: auto;
        }

        .image-viewer-controls {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 10001;
            display: flex;
            gap: 8px;
            background: rgba(0, 0, 0, 0.8);
            padding: 12px 16px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }

        .image-viewer-btn {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: background 0.2s;
        }

        .image-viewer-btn:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        .image-viewer-close {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10001;
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid rgba(0, 0, 0, 0.3);
            color: white;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }

        .image-viewer-close:hover {
            background: rgba(0, 0, 0, 0.9);
        }

        .content img {
            display: block;
            max-width: 100%;
            height: auto;
            margin: var(--spacing-lg) auto;
            cursor: zoom-in;
            transition: transform 0.2s;
            border-radius: var(--radius-md);
            image-rendering: -webkit-optimize-contrast;
            image-rendering: crisp-edges;
        }

        .content img:hover {
            transform: scale(1.02);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        }

        /* Image caption styling */
        .content img + em,
        .content p > img + br + em {
            display: block;
            text-align: center;
            color: var(--color-text-muted);
            font-size: var(--font-size-sm);
            margin-top: calc(-1 * var(--spacing-md));
            margin-bottom: var(--spacing-lg);
        }

        /* Ontology Tree Styles */
        .ontology-tree-container {
            background: var(--color-bg-tertiary);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-lg);
            padding: var(--spacing-lg);
            margin: var(--spacing-lg) 0;
            max-height: 500px;
            overflow-y: auto;
        }

        .ontology-tree {
            list-style: none;
            padding-left: 0;
            margin: 0;
            font-family: var(--font-family-mono);
            font-size: var(--font-size-sm);
        }

        .ontology-tree ul {
            list-style: none;
            padding-left: 20px;
            margin: 0;
            border-left: 1px dashed var(--color-border);
            margin-left: 8px;
        }

        .ontology-tree li { margin: 4px 0; position: relative; }

        .tree-node {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 8px;
            border-radius: var(--radius-sm);
            cursor: default;
            transition: background var(--transition-fast);
        }

        .tree-node:hover { background: var(--color-bg-hover); }

        .tree-toggle {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 18px;
            height: 18px;
            border: none;
            background: var(--color-bg-secondary);
            color: var(--color-text-muted);
            border-radius: 3px;
            cursor: pointer;
            font-size: 10px;
            flex-shrink: 0;
        }

        .tree-toggle:hover { background: var(--color-primary); color: white; }
        .tree-toggle.collapsed::before { content: '▶'; }
        .tree-toggle.expanded::before { content: '▼'; }
        .tree-toggle-placeholder { width: 18px; height: 18px; flex-shrink: 0; }
        .tree-prefix { color: var(--color-text-muted); font-size: 0.85em; }
        .tree-label { color: var(--color-primary-light); font-weight: 500; }
        .tree-node.has-definition { cursor: help; }
        .tree-node.has-definition .tree-label { border-bottom: 1px dotted var(--color-text-muted); }
        .tree-children { overflow: hidden; transition: max-height 0.2s ease-out; }
        .tree-children.collapsed { max-height: 0 !important; }

        .tree-toolbar {
            display: flex;
            gap: var(--spacing-sm);
            margin-bottom: var(--spacing-md);
            padding-bottom: var(--spacing-sm);
            border-bottom: 1px solid var(--color-border);
            flex-wrap: wrap;
            align-items: center;
        }

        .tree-toolbar-btn {
            padding: 6px 12px;
            font-size: var(--font-size-xs);
            font-weight: 500;
            color: var(--color-text-secondary);
            background: var(--color-bg-secondary);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            cursor: pointer;
        }

        .tree-toolbar-btn:hover { color: var(--color-text-primary); border-color: var(--color-primary); }

        .tree-search {
            flex: 1;
            max-width: 250px;
            padding: 6px 12px;
            font-size: var(--font-size-sm);
            color: var(--color-text-primary);
            background: var(--color-bg-secondary);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            outline: none;
        }

        .tree-search:focus { border-color: var(--color-primary); }
        .tree-stats { font-size: var(--font-size-xs); color: var(--color-text-muted); margin-left: auto; }
        .tree-node.search-match .tree-label { background: rgba(0, 160, 227, 0.3); padding: 0 2px; border-radius: 2px; }

        .tree-tooltip {
            position: fixed;
            z-index: 1000;
            max-width: 400px;
            padding: 12px 16px;
            background: var(--color-bg-primary);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-lg);
            font-size: var(--font-size-sm);
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.15s;
        }

        .tree-tooltip.visible { opacity: 1; }
        .tree-tooltip-title { font-weight: 600; color: var(--color-text-primary); margin-bottom: 6px; }
        .tree-tooltip-uri { font-family: var(--font-family-mono); font-size: var(--font-size-xs); color: var(--color-text-muted); word-break: break-all; margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--color-border); }

        /* Main Content - Optimized spacing for better use of screen real estate */
        .main-content {
            margin-left: var(--sidebar-width);
            margin-top: var(--header-height);
            padding: var(--spacing-xl) var(--spacing-lg);
            padding-right: calc(var(--toc-width) + var(--spacing-xl) + var(--spacing-lg));
            flex: 1;
            min-height: calc(100vh - var(--header-height));
            display: flex;
            justify-content: center;
        }

        .content-wrapper {
            width: 100%;
            max-width: 1100px;
        }

        /* When TOC is hidden, reclaim the right padding */
        @media (max-width: 1280px) {
            .main-content {
                padding-right: var(--spacing-lg);
            }
        }

        .breadcrumbs {
            display: flex;
            gap: var(--spacing-sm);
            margin-bottom: var(--spacing-lg);
            font-size: var(--font-size-sm);
        }

        .breadcrumbs a {
            color: var(--color-text-muted);
        }

        .breadcrumbs .current {
            color: var(--color-text-secondary);
        }

        /* Content Box with Background */
        .content, .article-content {
            background: var(--color-bg-card);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-xl);
            padding: var(--spacing-2xl);
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
        }

        .content h1, .content h2, .content h3, .article-content h1, .article-content h2, .article-content h3 {
            font-family: var(--font-family-heading);
            letter-spacing: -0.02em;
        }

        .content p, .content li, .article-content p, .article-content li {
            font-family: var(--font-family-body);
            line-height: 1.8;
            letter-spacing: 0.01em;
        }

        /* TOC */
        .toc {
            position: fixed;
            top: calc(var(--header-height) + var(--spacing-2xl));
            right: var(--spacing-xl);
            width: var(--toc-width);
            max-height: calc(100vh - var(--header-height) - 4rem);
            overflow-y: auto;
            padding: var(--spacing-md);
            background: var(--color-bg-card);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-lg);
            backdrop-filter: blur(8px);
        }

        .toc-title {
            font-size: var(--font-size-xs);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--color-text-muted);
            margin-bottom: var(--spacing-md);
        }

        .toc-list {
            list-style: none;
            padding-left: 0;
        }

        .toc-list a {
            display: block;
            font-size: var(--font-size-sm);
            color: var(--color-text-muted);
            padding: var(--spacing-xs) var(--spacing-sm);
            border-left: 2px solid transparent;
            transition: all var(--transition-fast);
        }

        .toc-list a:hover,
        .toc-list a.active {
            color: var(--color-primary);
            border-left-color: var(--color-primary);
            background: var(--color-bg-hover);
            text-decoration: none;
        }

        .toc-list .toc-h3 {
            padding-left: var(--spacing-lg);
        }

        /* Page Nav */
        .page-nav {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: var(--spacing-lg);
            margin-top: var(--spacing-2xl);
            padding-top: var(--spacing-xl);
            border-top: 1px solid var(--color-border);
        }

        .page-nav-link {
            display: flex;
            flex-direction: column;
            gap: var(--spacing-xs);
            padding: var(--spacing-lg);
            background: var(--color-bg-card);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-lg);
            transition: all var(--transition-fast);
        }

        .page-nav-link:hover {
            border-color: var(--color-primary);
            text-decoration: none;
            box-shadow: var(--shadow-glow);
        }

        .page-nav-link.next {
            text-align: right;
        }

        .page-nav-label {
            font-size: var(--font-size-xs);
            font-weight: 500;
            color: var(--color-text-muted);
            text-transform: uppercase;
        }

        .page-nav-title {
            font-size: var(--font-size-lg);
            font-weight: 600;
            color: var(--color-primary);
        }

        /* Footer */
        .footer {
            margin-top: var(--spacing-2xl);
            padding: var(--spacing-xl) 0;
            border-top: 1px solid var(--color-border);
            text-align: center;
        }

        .footer-links {
            display: flex;
            justify-content: center;
            gap: var(--spacing-xl);
            margin-bottom: var(--spacing-md);
        }

        .footer-links a {
            font-size: var(--font-size-sm);
            color: var(--color-text-muted);
        }

        .footer-copyright {
            font-size: var(--font-size-sm);
            color: var(--color-text-muted);
        }

        /* === MERMAID GRAPH CONTAINER === */
        .mermaid-graph-container {
            position: relative;
            margin: var(--spacing-xl) 0;
            background: linear-gradient(135deg, var(--color-bg-card) 0%, rgba(13, 31, 53, 0.95) 100%);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-xl);
            overflow: hidden;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }

        .graph-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: var(--spacing-sm) var(--spacing-lg);
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.03) 0%, transparent 100%);
            border-bottom: 1px solid var(--color-border);
            flex-wrap: wrap;
            gap: var(--spacing-sm);
        }

        .graph-title {
            font-size: var(--font-size-sm);
            font-weight: 600;
            color: var(--color-text-primary);
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
        }

        .graph-title::before {
            content: '';
            width: 8px;
            height: 8px;
            background: var(--color-primary);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--color-primary);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {

            0%,
            100% {
                opacity: 1;
            }

            50% {
                opacity: 0.5;
            }
        }

        .graph-controls {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }

        .graph-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 36px;
            height: 32px;
            padding: 0 10px;
            font-size: var(--font-size-sm);
            font-weight: 500;
            color: var(--color-text-secondary);
            background: linear-gradient(180deg, var(--color-bg-tertiary) 0%, var(--color-bg-secondary) 100%);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md);
            cursor: pointer;
            transition: all var(--transition-fast);
        }

        .graph-btn:hover {
            color: var(--color-text-primary);
            border-color: var(--color-primary);
            background: var(--color-bg-hover);
            box-shadow: 0 0 12px rgba(0, 160, 227, 0.2);
        }

        .graph-viewport {
            position: relative;
            min-height: 450px;
            max-height: 600px;
            overflow: hidden;
            background: radial-gradient(ellipse at center, rgba(0, 160, 227, 0.03) 0%, transparent 70%);
            cursor: grab;
        }

        .graph-viewport:active {
            cursor: grabbing;
        }

        .graph-wrapper {
            transform-origin: 0 0;
            transition: transform 0.05s;
            will-change: transform;
            display: flex;
            align-items: flex-start;
            justify-content: flex-start;
            min-width: 100%;
            min-height: 100%;
        }

        .graph-wrapper svg {
            max-width: none;
            display: block;
            overflow: visible;
            min-width: 100px;
            min-height: 100px;
        }

        .mermaid-diagram {
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 100%;
            min-height: 100%;
        }

        .mermaid-diagram svg {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
        }

        
        /* Graphviz (Viz.js) edge & label theming */
        :root {
            --graph-edge-color: #ffffff;
            --graph-edge-label-color: #5BC0EB;  /* Lighter Protege blue for dark mode */
        }

        body:not(.theme-dark) {
            --graph-edge-color: #1e293b;
            --graph-edge-label-color: #0079BA;  /* EXACT Protege blue for object properties */
        }

        /* Graphviz uses g.edge, g.node (similar to Mermaid), but with different internal shapes */
        .graph-wrapper svg g.edge path,
        .fullscreen-wrapper svg g.edge path {
            stroke: var(--graph-edge-color) !important;
        }

        .graph-wrapper svg g.edge polygon,
        .fullscreen-wrapper svg g.edge polygon {
            fill: var(--graph-edge-color) !important;
            stroke: var(--graph-edge-color) !important;
        }

        .graph-wrapper svg g.edge text,
        .graph-wrapper svg g.edge tspan,
        .fullscreen-wrapper svg g.edge text,
        .fullscreen-wrapper svg g.edge tspan {
            fill: var(--graph-edge-label-color) !important;
        }

        /* Focus + search states */
        .graph-wrapper svg g.edge.dimmed,
        .fullscreen-wrapper svg g.edge.dimmed {
            opacity: 0.12 !important;
        }

        .graph-wrapper svg g.edge.highlight-edge path,
        .fullscreen-wrapper svg g.edge.highlight-edge path {
            stroke: var(--color-primary) !important;
            stroke-width: 2.5px !important;
        }

        .graph-wrapper svg g.edge.highlight-edge polygon,
        .fullscreen-wrapper svg g.edge.highlight-edge polygon {
            fill: var(--color-primary) !important;
            stroke: var(--color-primary) !important;
        }

        .graph-wrapper svg g.node.search-match rect,
        .graph-wrapper svg g.node.search-match polygon,
        .graph-wrapper svg g.node.search-match ellipse {
            stroke: var(--color-success) !important;
            stroke-width: 3px !important;
            filter: drop-shadow(0 0 8px rgba(34, 197, 94, 0.55));
        }

        /* Search UI */
        .graph-search {
            height: 32px;
            min-width: 160px;
            padding: 0 10px;
            border-radius: var(--radius-md);
            border: 1px solid var(--color-border);
            background: var(--color-bg-secondary);
            color: var(--color-text-primary);
            outline: none;
            font-size: var(--font-size-sm);
        }

        .graph-search:focus {
            border-color: var(--color-primary);
            box-shadow: 0 0 0 3px rgba(0, 160, 227, 0.15);
        }

        .graph-search-clear {
            min-width: 32px;
            padding: 0 8px;
            opacity: 0.8;
        }

        .graph-search-clear:hover {
            opacity: 1;
        }

/* Mermaid node styles */
        .graph-wrapper svg g.node {
            cursor: pointer;
            transition: all 0.2s;
        }

        .graph-wrapper svg g.node:hover {
            filter: brightness(1.1);
        }

        .graph-wrapper svg g.node.selected rect,
        .graph-wrapper svg g.node.selected polygon,
        .graph-wrapper svg g.node.selected ellipse {
            stroke-width: 3px !important;
            filter: drop-shadow(0 0 8px var(--color-primary));
        }

        .graph-wrapper svg g.node.dim {
            opacity: var(--dim) !important;
        }

        .graph-wrapper svg g.node.hovered rect,
        .graph-wrapper svg g.node.hovered polygon,
        .graph-wrapper svg g.node.hovered ellipse {
            stroke: var(--color-primary) !important;
            stroke-width: 3px !important;
            filter: drop-shadow(0 0 10px var(--color-primary));
        }

        .graph-wrapper svg g.node.ancestor rect,
        .graph-wrapper svg g.node.ancestor polygon,
        .graph-wrapper svg g.node.ancestor ellipse {
            stroke: var(--color-primary) !important;
            stroke-width: 2.5px !important;
            stroke-dasharray: 6 4;
        }

        /* ===========================================
       EDGE LABEL STYLES
       Controls the text color of relationship labels on graph edges.
       - Dark mode: white labels for visibility on dark backgrounds
       - Light mode: black labels for visibility on white backgrounds
       =========================================== */

        /* Dark mode edge labels - lighter Protege blue for visibility */
        .graph-wrapper svg g.edgeLabel text,
        .graph-wrapper svg g.edgeLabel tspan {
            fill: #5BC0EB !important;
        }

        .fullscreen-wrapper svg g.edgeLabel text,
        .fullscreen-wrapper svg g.edgeLabel tspan {
            fill: #5BC0EB !important;
        }

        /* Light mode edge labels - EXACT Protege blue #0079BA */
        body:not(.theme-dark) .graph-wrapper svg g.edgeLabel text,
        body:not(.theme-dark) .graph-wrapper svg g.edgeLabel tspan {
            fill: #0079BA !important;
        }

        body:not(.theme-dark) .fullscreen-wrapper svg g.edgeLabel text,
        body:not(.theme-dark) .fullscreen-wrapper svg g.edgeLabel tspan {
            fill: #0079BA !important;
        }

        /* Edge dimming for focus/highlight interactions */
        .graph-wrapper svg g.edgePath.dim {
            opacity: var(--dim) !important;
        }

        .graph-wrapper svg g.edgeLabel.dim {
            opacity: var(--dim) !important;
        }

        .graph-wrapper svg g.edgePath.dim path {
            opacity: var(--dim) !important;
        }

        /* Edge highlighting when connected nodes are selected */
        .graph-wrapper svg g.edgePath.highlight {
            opacity: 1 !important;
        }

        .graph-wrapper svg g.edgePath.highlight path {
            opacity: 1 !important;
        }

        .graph-wrapper svg g.edgeLabel.highlight {
            opacity: 1 !important;
        }

        .graph-wrapper svg g.edgePath.highlight path {
            stroke: var(--color-primary) !important;
            stroke-width: 2.5px !important;
        }

        .graph-wrapper svg g.edgeLabel.highlight text,
        .graph-wrapper svg g.edgeLabel.highlight tspan {
            fill: var(--color-primary) !important;
            font-weight: 700;
        }

        .graph-wrapper svg g.edgePath.typeEdge path {
            stroke-dasharray: 1.2 6 !important;
            stroke-linecap: round !important;
        }

        .graph-wrapper svg g.edgeLabel.typeEdge text,
        .graph-wrapper svg g.edgeLabel.typeEdge tspan {
            fill: var(--color-primary) !important;
        }

        .zoom-controls {
            position: absolute;
            top: 12px;
            right: 12px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            background: var(--color-bg-secondary);
            padding: 8px;
            border-radius: var(--radius-lg);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            border: 1px solid var(--color-border);
            z-index: 100;
        }

        .zoom-btn {
            background: var(--color-bg-tertiary);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md);
            padding: 8px;
            cursor: pointer;
            font-size: 16px;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all var(--transition-fast);
            color: var(--color-text-primary);
            user-select: none;
        }

        .zoom-btn:hover {
            background: var(--color-primary);
            color: white;
            transform: scale(1.05);
        }

        .zoom-level {
            text-align: center;
            font-size: var(--font-size-xs);
            color: var(--color-text-muted);
            padding: 4px;
            font-weight: 500;
        }

        /* Fullscreen modal */
        .fullscreen-overlay {
            position: fixed;
            inset: 0;
            z-index: 9999;
            background: var(--color-bg-primary);
            display: none;
            flex-direction: column;
        }

        .fullscreen-overlay.active {
            display: flex;
        }

        .fullscreen-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: var(--spacing-md) var(--spacing-lg);
            background: var(--color-bg-secondary);
            border-bottom: 1px solid var(--color-border);
        }

        .fullscreen-title {
            font-size: var(--font-size-lg);
            font-weight: 600;
            color: var(--color-text-primary);
        }

        .fullscreen-close {
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
            padding: 8px 16px;
            font-size: var(--font-size-sm);
            font-weight: 500;
            color: var(--color-text-primary);
            background: var(--color-bg-tertiary);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md);
            cursor: pointer;
            transition: all var(--transition-fast);
        }

        .fullscreen-close:hover {
            background: var(--color-error);
            border-color: var(--color-error);
            color: white;
        }

        .fullscreen-viewport {
            flex: 1;
            position: relative;
            overflow: hidden;
            cursor: grab;
        }

        .fullscreen-viewport:active {
            cursor: grabbing;
        }

        .fullscreen-wrapper {
            transform-origin: 0 0;
            transition: transform 0.05s;
            will-change: transform;
            display: flex;
            align-items: flex-start;
            justify-content: flex-start;
            min-width: 100%;
            min-height: 100%;
        }

        .fullscreen-wrapper svg {
            max-width: none;
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
        }

        .fullscreen-zoom-controls {
            position: absolute;
            top: 16px;
            right: 16px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            background: var(--color-bg-secondary);
            padding: 10px;
            border-radius: var(--radius-lg);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            border: 1px solid var(--color-border);
            z-index: 100;
        }

        .fullscreen-zoom-btn {
            background: var(--color-bg-tertiary);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md);
            padding: 10px;
            cursor: pointer;
            font-size: 18px;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all var(--transition-fast);
            color: var(--color-text-primary);
            user-select: none;
        }

        .fullscreen-zoom-btn:hover {
            background: var(--color-primary);
            color: white;
            transform: scale(1.05);
        }

        .fullscreen-zoom-level {
            text-align: center;
            font-size: var(--font-size-sm);
            color: var(--color-text-muted);
            padding: 6px;
            font-weight: 500;
        }

        /* Popover */
        .graph-popover {
            position: fixed;
            z-index: 1000;
            display: none;
            min-width: 340px;
            max-width: 420px;
            max-height: 70vh;
            overflow-y: auto;
            background: var(--color-bg-secondary);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-xl);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
            animation: popIn 0.2s;
        }

        @keyframes popIn {
            from {
                opacity: 0;
                transform: translateY(-10px) scale(0.95);
            }

            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        .graph-popover.visible {
            display: block;
        }

        .pop-head {
            padding: 16px 20px;
            border-bottom: 1px solid var(--color-border);
            background: var(--pop-header);
            border-radius: var(--radius-xl) var(--radius-xl) 0 0;
            color: var(--pop-header-text);
            position: relative;
        }

        .pop-title {
            font-size: 16px;
            font-weight: 600;
            margin: 0 0 8px 0;
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--pop-header-text);
        }

        .badge {
            display: inline-block;
            padding: 3px 8px;
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.25);
            border-radius: 6px;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: rgba(255, 255, 255, 0.95);
        }

        .pop-uri {
            font-size: 11px;
            opacity: 0.85;
            word-break: break-all;
            font-family: var(--font-family-mono);
            background: rgba(0, 0, 0, 0.2);
            padding: 8px 12px;
            border-radius: 6px;
            margin-top: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: rgba(255, 255, 255, 0.9);
        }

        .pop-actions {
            margin-top: 12px;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .chip {
            border: 1px solid rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }

        .chip:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-1px);
        }

        .close-btn {
            position: absolute;
            top: 12px;
            right: 12px;
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            width: 28px;
            height: 28px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }

        .close-btn:hover {
            background: rgba(255, 255, 255, 0.25);
            transform: scale(1.05);
        }

        .pop-body {
            padding: 16px 20px;
        }

        .section {
            margin-bottom: 16px;
        }

        .section:last-child {
            margin-bottom: 0;
        }

        .sec-title {
            font-size: 11px;
            font-weight: 700;
            color: var(--color-text-muted);
            text-transform: uppercase;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
            letter-spacing: 0.5px;
        }

        .count {
            background: var(--color-primary);
            color: white;
            padding: 2px 7px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: 600;
        }

        .trips {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .trip {
            background: var(--card-bg);
            padding: 12px 14px;
            border-radius: 8px;
            border: 1px solid var(--card-border);
            transition: all 0.2s;
        }

        .trip:hover {
            border-color: var(--color-primary);
            background: var(--card-hover);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }

        .pred {
            font-size: 10px;
            color: var(--pred-color);
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 4px;
            letter-spacing: 0.5px;
        }

        .val {
            font-size: 13px;
            color: var(--val-color);
            font-weight: 500;
            font-family: var(--font-family-mono);
        }

        .empty {
            text-align: center;
            padding: 20px;
            color: var(--color-text-muted);
            font-size: 12px;
            background: var(--card-bg);
            border-radius: 8px;
            border: 1px dashed var(--card-border);
        }

        /* Toast */
        .graph-toast {
            position: fixed;
            left: 50%;
            bottom: 18px;
            transform: translateX(-50%);
            background: rgba(15, 23, 42, 0.92);
            color: rgba(255, 255, 255, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 999px;
            padding: 10px 14px;
            font-size: 13px;
            font-weight: 600;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
            display: none;
            z-index: 2000;
            backdrop-filter: blur(6px);
            max-width: min(520px, calc(100% - 24px));
            text-align: center;
        }

        body:not(.theme-dark) .graph-toast {
            background: rgba(255, 255, 255, 0.94);
            color: rgba(0, 0, 0, 0.86);
            border: 1px solid rgba(0, 0, 0, 0.10);
            box-shadow: 0 10px 26px rgba(0, 0, 0, 0.18);
        }

        /* Legend */
        .graph-legend {
            display: flex;
            flex-wrap: wrap;
            gap: var(--spacing-sm);
            padding: var(--spacing-sm) var(--spacing-lg);
            background: linear-gradient(180deg, transparent 0%, rgba(0, 0, 0, 0.2) 100%);
            border-top: 1px solid var(--color-border);
        }

        .legend-item {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: var(--font-size-xs);
            font-weight: 500;
            color: var(--color-text-secondary);
            padding: 6px 12px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: var(--radius-full);
        }

        .legend-swatch {
            width: 16px;
            height: 16px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        /* Shape indicators: square for TBox classes, oval for ABox individuals */
        .legend-swatch.shape-square {
            border-radius: 3px;
        }

        .legend-swatch.shape-oval {
            border-radius: 50%;
        }

        .legend-swatch.shape-note {
            border-radius: 3px;
            clip-path: polygon(0 0, 75% 0, 100% 25%, 100% 100%, 0 100%);
        }

        /* Legend swatches – ontology color scheme */
        .swatch-bfo {
            background: #F556CB;  /* BFO - pink rgba(245,86,203) */
        }

        .swatch-iao {
            background: #F6A252;  /* IAO - orange rgba(246,162,82) */
        }

        .swatch-obi {
            background: #F5D5B1;  /* OBI - warm peach rgba(245,213,177) */
        }

        .swatch-cob {
            background: #93AFF3;  /* COB - periwinkle blue rgba(147,175,243) */
        }

        .swatch-individual {
            background: #E6E6E6;  /* ABox - light gray rgba(230,230,230) */
        }

        .swatch-literal {
            background: #93D053;  /* Literals - green rgba(147,208,83) */
        }

        .swatch-qudt {
            background: #C9DBFE;  /* QUDT - light blue rgba(201,219,254) */
        }

        .swatch-pmd {
            background: #46CAD3;  /* PMD - cyan rgba(70,202,211) */
        }

        .swatch-ro {
            background: #F43F5E;  /* RO - rose */
        }

        .swatch-class {
            background: #FDFDC8;  /* Default class - light yellow rgba(253,253,200) */
        }

        .swatch-property {
            background: var(--graph-edge-label-color, #0079BA);  /* Object Property - matches edge label color */
        }

        .swatch-type {
            background: var(--graph-edge-color, #1e293b);  /* rdf:type - matches edge line color (dashed) */
        }

        .swatch-categorical {
            background: #99F6E4;  /* Teal - Categorical */
        }

        .swatch-shacl {
            background: #A5F3FC;  /* Cyan - SHACL */
        }

        .swatch-constraint {
            background: #FED7AA;  /* Orange - Constraints */
        }

        /* ===========================================
           RESPONSIVE DESIGN - Multi-breakpoint Layout
           ===========================================
           Breakpoints:
           - 1600px+: Full layout with TOC
           - 1280-1600px: Content expands, TOC visible
           - 1024-1280px: No TOC, optimized content width
           - 768-1024px: Tablet mode, narrower sidebar
           - <768px: Mobile mode, collapsed sidebar
           =========================================== */

        /* Extra large screens (1600px+) - Full layout */
        @media (min-width: 1600px) {
            :root {
                --sidebar-width: 300px;
                --toc-width: 260px;
            }

            .content-wrapper {
                max-width: 1200px;
            }
        }

        /* Large screens (1280-1600px) - Slightly compact */
        @media (max-width: 1600px) and (min-width: 1280px) {
            :root {
                --sidebar-width: 260px;
                --toc-width: 220px;
            }

            .content-wrapper {
                max-width: 1000px;
                padding: 0 var(--spacing-md);
            }

            .main-content {
                padding: var(--spacing-xl);
            }
        }

        /* Medium-large screens (1024-1280px) - No TOC */
        @media (max-width: 1280px) {
            .toc {
                display: none;
            }

            :root {
                --sidebar-width: 250px;
            }

            .content-wrapper {
                max-width: 100%;
                margin: 0;
                padding: 0;
            }

            .main-content {
                padding: var(--spacing-xl) var(--spacing-lg);
                margin-right: 0;
            }
        }

        /* Tablet screens (768-1024px) - Narrower sidebar */
        @media (max-width: 1024px) and (min-width: 768px) {
            :root {
                --sidebar-width: 220px;
            }

            .sidebar {
                padding: var(--spacing-md);
            }

            .nav-link {
                padding: var(--spacing-xs) var(--spacing-sm);
                font-size: var(--font-size-xs);
            }

            .main-content {
                padding: var(--spacing-lg);
            }

            .content, .article-content {
                padding: var(--spacing-xl);
            }

            h1 {
                font-size: var(--font-size-3xl);
            }

            h2 {
                font-size: var(--font-size-xl);
            }

            .graph-header {
                flex-direction: column;
                gap: var(--spacing-xs);
            }

            .graph-controls {
                width: 100%;
                justify-content: flex-start;
            }
        }

        /* Mobile screens (<768px) - Collapsed sidebar */
        @media (max-width: 768px) {
            :root {
                --header-height: 56px;
            }

            .sidebar {
                transform: translateX(-100%);
                transition: transform var(--transition-normal);
                z-index: var(--z-modal);
                width: 280px;
            }

            .sidebar.open {
                transform: translateX(0);
            }

            .main-content {
                margin-left: 0;
                padding: var(--spacing-md);
            }

            .content, .article-content {
                padding: var(--spacing-lg);
                border-radius: var(--radius-lg);
            }

            .header-nav {
                display: none;
            }

            .mobile-menu-btn {
                display: flex;
            }

            .page-nav {
                grid-template-columns: 1fr;
            }

            .page-nav-link {
                padding: var(--spacing-md);
            }

            h1 {
                font-size: var(--font-size-2xl);
            }

            h2 {
                font-size: var(--font-size-lg);
                margin-top: var(--spacing-xl);
            }

            h3 {
                font-size: var(--font-size-base);
            }

            .mermaid-graph-container {
                margin: var(--spacing-md) calc(-1 * var(--spacing-lg));
                border-radius: 0;
                border-left: none;
                border-right: none;
            }

            .graph-viewport {
                min-height: 300px;
            }

            .search-modal-content {
                margin: var(--spacing-sm);
                max-height: calc(100vh - var(--spacing-lg));
                border-radius: var(--radius-lg);
            }

            .search-modal {
                padding-top: var(--spacing-md);
            }

            .ontology-tree-container {
                margin: var(--spacing-md) calc(-1 * var(--spacing-lg));
                border-radius: 0;
                border-left: none;
                border-right: none;
                max-height: 350px;
            }

            .tree-toolbar {
                flex-direction: column;
                align-items: stretch;
            }

            .tree-search {
                max-width: none;
            }

            .tree-stats {
                margin-left: 0;
                margin-top: var(--spacing-sm);
            }
        }

        /* Small mobile screens (<480px) */
        @media (max-width: 480px) {
            .main-content {
                padding: var(--spacing-sm);
            }

            .content, .article-content {
                padding: var(--spacing-md);
            }

            .header-logo span {
                font-size: var(--font-size-base);
            }

            .theme-toggle {
                padding: 6px 10px;
            }

            .theme-label {
                display: none;
            }

            pre {
                padding: var(--spacing-md);
                font-size: var(--font-size-xs);
                margin-left: calc(-1 * var(--spacing-md));
                margin-right: calc(-1 * var(--spacing-md));
                border-radius: 0;
            }
        }

        /* Image Viewer */
        .image-viewer-overlay {
            position: fixed;
            inset: 0;
            background: rgba(255, 255, 255, 0.98);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s, visibility 0.3s;
        }

        .image-viewer-overlay.active {
            opacity: 1;
            visibility: visible;
        }

        .image-viewer-container {
            position: absolute;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            cursor: grab;
        }

        .image-viewer-container:active {
            cursor: grabbing;
        }

        .image-viewer-container img,
        .image-viewer-container svg {
            max-width: 90vw;
            max-height: 85vh;
            object-fit: contain;
            transform-origin: center center;
            transition: transform 0.1s ease-out;
            user-select: none;
            -webkit-user-drag: none;
        }

        .image-viewer-controls {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 10001;
            display: flex;
            gap: 8px;
            background: rgba(0, 0, 0, 0.8);
            padding: 12px 16px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }

        .image-viewer-btn {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: background 0.2s;
        }

        .image-viewer-btn:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        .image-viewer-close {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10001;
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid rgba(0, 0, 0, 0.3);
            color: white;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }

        .image-viewer-close:hover {
            background: rgba(0, 0, 0, 0.9);
        }

        .viewable-image,
        .article-content svg {
            cursor: zoom-in;
            transition: transform 0.2s;
        }

        .viewable-image:hover,
        .article-content svg:hover {
            transform: scale(1.02);
        }

        body.no-scroll {
            overflow: hidden;
        }
    

        /* ===========================================
           ENHANCED SEARCH RESULTS STYLING
           =========================================== */
        .search-result-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: var(--spacing-sm);
        }

        .search-result-badge {
            font-size: 10px;
            letter-spacing: 0.08em;
            font-weight: 700;
            text-transform: uppercase;
            color: var(--color-primary);
            background: rgba(0, 160, 227, 0.1);
            border: 1px solid rgba(0, 160, 227, 0.3);
            padding: 2px 8px;
            border-radius: 999px;
            flex: 0 0 auto;
            user-select: none;
        }

        .search-result-badge.page {
            color: var(--color-primary);
            background: rgba(0, 160, 227, 0.1);
            border-color: rgba(0, 160, 227, 0.3);
        }

        .search-result-badge.section {
            color: var(--color-success);
            background: rgba(16, 185, 129, 0.1);
            border-color: rgba(16, 185, 129, 0.3);
        }

        .search-result-badge.graph {
            color: #8b5cf6;
            background: rgba(139, 92, 246, 0.1);
            border-color: rgba(139, 92, 246, 0.3);
        }

        .search-result-section {
            font-size: var(--font-size-xs);
            color: var(--color-text-muted);
            margin-top: 2px;
        }

        .search-result-snippet {
            margin-top: 8px;
            font-size: var(--font-size-sm);
            line-height: 1.5;
            color: var(--color-text-secondary);
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .search-result-snippet mark {
            background: rgba(0, 160, 227, 0.25);
            color: var(--color-primary-light);
            padding: 1px 3px;
            border-radius: 3px;
            font-weight: 500;
        }

        .search-result-item {
            display: block;
            padding: var(--spacing-md) var(--spacing-lg);
            border-radius: var(--radius-md);
            transition: all var(--transition-fast);
            border-left: 3px solid transparent;
        }

        .search-result-item:hover,
        .search-result-item.selected {
            background: var(--color-bg-hover);
            text-decoration: none;
            border-left-color: var(--color-primary);
        }

        .search-result-title {
            font-weight: 600;
            color: var(--color-text-primary);
            font-size: var(--font-size-base);
        }

        .search-result-title mark {
            background: rgba(0, 160, 227, 0.3);
            color: var(--color-primary);
            padding: 0 2px;
            border-radius: 2px;
        }

        .search-results {
            max-height: 450px;
            overflow-y: auto;
            padding: var(--spacing-xs) 0;
        }

        .search-results::-webkit-scrollbar {
            width: 6px;
        }

        .search-results::-webkit-scrollbar-thumb {
            background: var(--color-border);
            border-radius: var(--radius-full);
        }

        .search-no-results {
            padding: var(--spacing-2xl);
            text-align: center;
            color: var(--color-text-muted);
        }

        .search-no-results svg {
            width: 48px;
            height: 48px;
            margin-bottom: var(--spacing-md);
            opacity: 0.4;
        }

        .search-target-flash {
            outline: 3px solid rgba(0, 160, 227, 0.4);
            outline-offset: 4px;
            border-radius: 8px;
            animation: search-flash 1.5s ease-out forwards;
        }

        @keyframes search-flash {
            0% {
                outline-color: rgba(0, 160, 227, 0.6);
                background: rgba(0, 160, 227, 0.1);
            }
            100% {
                outline-color: transparent;
                background: transparent;
            }
        }

        /* Search keyboard hints */
        .search-footer {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: var(--spacing-lg);
            padding: var(--spacing-sm) var(--spacing-lg);
            border-top: 1px solid var(--color-border);
            font-size: var(--font-size-xs);
            color: var(--color-text-muted);
            flex-wrap: wrap;
            background: var(--color-bg-tertiary);
        }

        .search-footer kbd {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 20px;
            padding: 2px 6px;
            background: var(--color-bg-secondary);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            font-family: var(--font-family-mono);
            font-size: 11px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }

        .search-index-status {
            margin-left: auto;
            white-space: nowrap;
            opacity: 0.8;
            font-size: 11px;
        }

        /* Collapsible code blocks */
        details.code-block {
            margin: var(--spacing-lg) 0;
            border: 1px solid var(--color-border);
            border-radius: var(--radius-lg);
            background: var(--color-code-bg);
            overflow: hidden;
        }

        details.code-block summary {
            padding: var(--spacing-sm) var(--spacing-md);
            background: var(--color-bg-tertiary);
            border-bottom: 1px solid var(--color-border);
            cursor: pointer;
            font-size: var(--font-size-sm);
            font-weight: 500;
            color: var(--color-text-muted);
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
            user-select: none;
            transition: all var(--transition-fast);
        }

        details.code-block summary:hover {
            background: var(--color-bg-hover);
            color: var(--color-text-primary);
        }

        details.code-block summary::marker,
        details.code-block summary::-webkit-details-marker {
            display: none;
        }

        details.code-block summary::before {
            content: '▶';
            font-size: 10px;
            transition: transform 0.2s ease;
        }

        details.code-block[open] summary::before {
            transform: rotate(90deg);
        }

        details.code-block pre {
            margin: 0;
            border: none;
            border-radius: 0;
            max-height: 400px;
            overflow: auto;
        }

        details.code-block code {
            font-size: var(--font-size-sm);
        }

        /* ===========================================
           HIGH-END UI ENHANCEMENTS
           Premium micro-interactions and polish
           =========================================== */

        /* === SCROLL PROGRESS INDICATOR === */
        .scroll-progress {
            position: fixed;
            top: 0;
            left: 0;
            width: 0%;
            height: 3px;
            background: linear-gradient(90deg, var(--color-primary) 0%, var(--color-primary-light) 50%, var(--color-accent) 100%);
            z-index: calc(var(--z-sticky) + 10);
            transition: width 0.1s ease-out;
            box-shadow: 0 0 10px rgba(0, 160, 227, 0.5);
        }

        /* === BACK TO TOP BUTTON === */
        .back-to-top {
            position: fixed;
            bottom: 32px;
            right: 32px;
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
            color: white;
            border: none;
            border-radius: var(--radius-full);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            visibility: hidden;
            transform: translateY(20px) scale(0.8);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 20px rgba(0, 160, 227, 0.4);
            z-index: var(--z-sticky);
        }

        .back-to-top:hover {
            transform: translateY(-4px) scale(1.1);
            box-shadow: 0 8px 30px rgba(0, 160, 227, 0.5);
        }

        .back-to-top:active {
            transform: translateY(0) scale(0.95);
        }

        .back-to-top.visible {
            opacity: 1;
            visibility: visible;
            transform: translateY(0) scale(1);
        }

        .back-to-top svg {
            width: 24px;
            height: 24px;
            transition: transform 0.2s ease;
        }

        .back-to-top:hover svg {
            transform: translateY(-2px);
        }

        /* === TABLE STYLING - Elegant & Professional === */
        .content table,
        .article-content table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: var(--spacing-xl) 0;
            background: var(--color-bg-secondary);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-lg);
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        .content table thead,
        .article-content table thead {
            background: linear-gradient(135deg, var(--color-bg-tertiary) 0%, var(--color-bg-secondary) 100%);
        }

        .content table th,
        .article-content table th {
            padding: var(--spacing-md) var(--spacing-lg);
            text-align: left;
            font-weight: 600;
            font-size: var(--font-size-sm);
            color: var(--color-text-primary);
            text-transform: uppercase;
            letter-spacing: 0.03em;
            border-bottom: 2px solid var(--color-border);
        }

        .content table td,
        .article-content table td {
            padding: var(--spacing-md) var(--spacing-lg);
            font-size: var(--font-size-sm);
            color: var(--color-text-secondary);
            border-bottom: 1px solid var(--color-border);
            transition: background var(--transition-fast);
        }

        .content table tbody tr,
        .article-content table tbody tr {
            transition: all var(--transition-fast);
        }

        .content table tbody tr:hover,
        .article-content table tbody tr:hover {
            background: var(--color-bg-hover);
        }

        .content table tbody tr:last-child td,
        .article-content table tbody tr:last-child td {
            border-bottom: none;
        }

        /* Zebra striping for tables */
        .content table tbody tr:nth-child(even),
        .article-content table tbody tr:nth-child(even) {
            background: rgba(0, 0, 0, 0.015);
        }

        body.theme-dark .content table tbody tr:nth-child(even),
        body.theme-dark .article-content table tbody tr:nth-child(even) {
            background: rgba(255, 255, 255, 0.02);
        }

        /* === BLOCKQUOTE STYLING === */
        .content blockquote,
        .article-content blockquote {
            position: relative;
            margin: var(--spacing-xl) 0;
            padding: var(--spacing-lg) var(--spacing-xl);
            padding-left: calc(var(--spacing-xl) + 4px);
            background: linear-gradient(135deg, rgba(0, 160, 227, 0.05) 0%, rgba(0, 160, 227, 0.02) 100%);
            border-left: 4px solid var(--color-primary);
            border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
            font-style: italic;
            color: var(--color-text-secondary);
        }

        .content blockquote::before,
        .article-content blockquote::before {
            content: '"';
            position: absolute;
            top: -10px;
            left: 16px;
            font-size: 4rem;
            font-family: Georgia, serif;
            color: var(--color-primary);
            opacity: 0.2;
            line-height: 1;
        }

        .content blockquote p:last-child,
        .article-content blockquote p:last-child {
            margin-bottom: 0;
        }

        /* === ENHANCED LINK STYLING === */
        .content a:not(.nav-link):not(.page-nav-link):not(.header-logo),
        .article-content a:not(.nav-link):not(.page-nav-link):not(.header-logo) {
            position: relative;
            text-decoration: none;
            background-image: linear-gradient(var(--color-primary), var(--color-primary));
            background-size: 0% 2px;
            background-position: 0 100%;
            background-repeat: no-repeat;
            transition: background-size 0.3s ease, color 0.2s ease;
        }

        .content a:not(.nav-link):not(.page-nav-link):not(.header-logo):hover,
        .article-content a:not(.nav-link):not(.page-nav-link):not(.header-logo):hover {
            background-size: 100% 2px;
            text-decoration: none;
        }

        /* External link indicator */
        .content a[href^="http"]:not([href*="materialdigital"])::after,
        .article-content a[href^="http"]:not([href*="materialdigital"])::after {
            content: '↗';
            display: inline-block;
            margin-left: 3px;
            font-size: 0.75em;
            opacity: 0.7;
            transition: transform 0.2s ease, opacity 0.2s ease;
        }

        .content a[href^="http"]:not([href*="materialdigital"]):hover::after,
        .article-content a[href^="http"]:not([href*="materialdigital"]):hover::after {
            transform: translate(2px, -2px);
            opacity: 1;
        }

        /* === PAGE LOAD ANIMATION === */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .content-wrapper {
            animation: fadeInUp 0.5s ease-out;
        }

        /* === SIDEBAR MICRO-INTERACTIONS === */
        .nav-link {
            position: relative;
            overflow: hidden;
        }

        .nav-link::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            height: 100%;
            width: 3px;
            background: var(--color-primary);
            transform: scaleY(0);
            transition: transform 0.2s ease;
        }

        .nav-link:hover::before,
        .nav-link.active::before {
            transform: scaleY(1);
        }

        .nav-link svg {
            transition: transform 0.2s ease, color 0.2s ease;
        }

        .nav-link:hover svg {
            transform: scale(1.1);
            color: var(--color-primary);
        }

        /* === TOC ENHANCED INTERACTIONS === */
        .toc-list a {
            position: relative;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .toc-list a::before {
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 0;
            height: 0;
            border-left: 4px solid var(--color-primary);
            border-top: 4px solid transparent;
            border-bottom: 4px solid transparent;
            opacity: 0;
            transition: opacity 0.2s ease;
        }

        .toc-list a.active::before {
            opacity: 1;
        }

        .toc-list a:hover {
            padding-left: calc(var(--spacing-sm) + 8px);
        }

        /* === HEADER ENHANCEMENT === */
        .header {
            transition: box-shadow 0.3s ease, background 0.3s ease;
        }

        .header.scrolled {
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }

        .header-logo {
            transition: transform 0.2s ease;
        }

        .header-logo:hover {
            transform: scale(1.02);
        }

        /* === ENHANCED CODE BLOCKS === */
        pre {
            position: relative;
        }

        pre::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light), var(--color-accent));
            opacity: 0.6;
        }

        /* Code copy button */
        pre:hover::after {
            opacity: 0.6;
        }

        /* === CARD HOVER EFFECTS === */
        .content, .article-content {
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        /* === PAGE NAV ENHANCED === */
        .page-nav-link {
            position: relative;
            overflow: hidden;
        }

        .page-nav-link::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light));
            transform: scaleX(0);
            transform-origin: left;
            transition: transform 0.3s ease;
        }

        .page-nav-link.next::before {
            transform-origin: right;
        }

        .page-nav-link:hover::before {
            transform: scaleX(1);
        }

        .page-nav-link:hover .page-nav-title {
            transform: translateX(4px);
        }

        .page-nav-link.next:hover .page-nav-title {
            transform: translateX(-4px);
        }

        .page-nav-title {
            transition: transform 0.2s ease;
        }

        /* === BUTTON RIPPLE EFFECT === */
        .btn-ripple {
            position: relative;
            overflow: hidden;
        }

        .btn-ripple::after {
            content: '';
            position: absolute;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
            transform: scale(0);
            opacity: 0;
            transition: transform 0.5s ease, opacity 0.3s ease;
        }

        .btn-ripple:active::after {
            transform: scale(2);
            opacity: 1;
            transition: transform 0s, opacity 0s;
        }

        /* === SEARCH MODAL ENHANCEMENT === */
        .search-modal-content {
            animation: modalSlideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        @keyframes modalSlideIn {
            from {
                opacity: 0;
                transform: translateY(-20px) scale(0.95);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        .search-result-item {
            position: relative;
            transition: all 0.2s ease;
        }

        .search-result-item::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 3px;
            background: var(--color-primary);
            transform: scaleY(0);
            transition: transform 0.2s ease;
        }

        .search-result-item:hover::before,
        .search-result-item.selected::before {
            transform: scaleY(1);
        }

        /* === THEME TOGGLE ENHANCEMENT === */
        .theme-toggle {
            position: relative;
            overflow: hidden;
        }

        .theme-toggle::before {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(0, 160, 227, 0.1), transparent);
            opacity: 0;
            transition: opacity 0.2s ease;
        }

        .theme-toggle:hover::before {
            opacity: 1;
        }

        .theme-toggle svg {
            transition: transform 0.3s ease;
        }

        .theme-toggle:hover svg {
            transform: rotate(15deg);
        }

        /* === SKELETON LOADING === */
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }

        .skeleton {
            background: linear-gradient(90deg,
                var(--color-bg-tertiary) 25%,
                var(--color-bg-secondary) 50%,
                var(--color-bg-tertiary) 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            border-radius: var(--radius-sm);
        }

        /* === FOCUS RING ENHANCEMENT === */
        :focus-visible {
            outline: 2px solid var(--color-primary);
            outline-offset: 3px;
            border-radius: var(--radius-sm);
        }

        /* === SELECTION STYLING === */
        ::selection {
            background: rgba(0, 160, 227, 0.3);
            color: var(--color-text-primary);
        }

        /* === SMOOTH SCROLL OFFSET FOR ANCHORS === */
        :target {
            scroll-margin-top: calc(var(--header-height) + var(--spacing-lg));
        }

        /* === TOOLTIP STYLING === */
        [data-tooltip] {
            position: relative;
        }

        [data-tooltip]::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%) translateY(-8px);
            padding: 6px 12px;
            background: var(--color-bg-primary);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md);
            font-size: var(--font-size-xs);
            white-space: nowrap;
            opacity: 0;
            visibility: hidden;
            transition: all 0.2s ease;
            box-shadow: var(--shadow-md);
            z-index: var(--z-tooltip);
        }

        [data-tooltip]:hover::after {
            opacity: 1;
            visibility: visible;
            transform: translateX(-50%) translateY(-4px);
        }

        /* === NOTIFICATION BADGE PULSE === */
        @keyframes badgePulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }

        .badge-pulse {
            animation: badgePulse 2s infinite;
        }

        /* === LOADING SPINNER === */
        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .spinner {
            width: 24px;
            height: 24px;
            border: 3px solid var(--color-border);
            border-top-color: var(--color-primary);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        /* ===========================================
           PREMIUM MODERN UI ENHANCEMENTS
           High-end production-ready styling
           =========================================== */

        /* === GLASSMORPHISM EFFECTS === */
        .sidebar {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }

        body.theme-dark .sidebar {
            background: rgba(13, 31, 53, 0.9);
        }

        .header {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
        }

        body.theme-dark .header {
            background: rgba(10, 22, 40, 0.85);
        }

        .toc {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
        }

        body.theme-dark .toc {
            background: rgba(13, 31, 53, 0.9);
        }

        /* === LAYERED SHADOW SYSTEM === */
        .content, .article-content {
            box-shadow:
                0 1px 2px rgba(0, 0, 0, 0.02),
                0 2px 4px rgba(0, 0, 0, 0.02),
                0 4px 8px rgba(0, 0, 0, 0.02),
                0 8px 16px rgba(0, 0, 0, 0.02),
                0 16px 32px rgba(0, 0, 0, 0.02);
        }

        body.theme-dark .content,
        body.theme-dark .article-content {
            box-shadow:
                0 1px 2px rgba(0, 0, 0, 0.1),
                0 2px 4px rgba(0, 0, 0, 0.1),
                0 4px 8px rgba(0, 0, 0, 0.1),
                0 8px 16px rgba(0, 0, 0, 0.08),
                0 16px 32px rgba(0, 0, 0, 0.06);
        }

        /* === PREMIUM TYPOGRAPHY === */
        .content h1, .article-content h1 {
            font-size: clamp(2rem, 5vw, 2.75rem);
            font-weight: 800;
            letter-spacing: -0.03em;
            line-height: 1.1;
            margin-bottom: var(--spacing-xl);
        }

        .content h2, .article-content h2 {
            font-size: clamp(1.5rem, 3vw, 1.875rem);
            font-weight: 700;
            letter-spacing: -0.02em;
            line-height: 1.2;
            position: relative;
            padding-bottom: var(--spacing-md);
        }

        .content h2::after, .article-content h2::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 60px;
            height: 3px;
            background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light));
            border-radius: 2px;
        }

        .content h3, .article-content h3 {
            font-size: clamp(1.125rem, 2vw, 1.375rem);
            font-weight: 600;
            letter-spacing: -0.01em;
            color: var(--color-text-primary);
        }

        .content p, .article-content p {
            font-size: 1.0625rem;
            line-height: 1.8;
            color: var(--color-text-secondary);
        }

        /* === PREMIUM LIST STYLING === */
        /* Exclude ontology-tree from premium list styling */
        .content ul:not(.ontology-tree), .article-content ul:not(.ontology-tree),
        .content ol, .article-content ol {
            list-style: none;
            padding-left: 0;
            margin-bottom: var(--spacing-md);
        }

        /* Ordered lists use CSS counters for numbering */
        .content ol, .article-content ol {
            counter-reset: list-counter;
        }

        .content ul:not(.ontology-tree) > li, .article-content ul:not(.ontology-tree) > li,
        .content ol > li, .article-content ol > li {
            position: relative;
            padding-left: 1.5em;
            margin-bottom: 0.5em;
            line-height: 1.7;
        }

        /* Unordered list bullets (dot) */
        .content ul:not(.ontology-tree) > li::before, .article-content ul:not(.ontology-tree) > li::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0.65em;
            width: 6px;
            height: 6px;
            background: var(--color-primary);
            border-radius: 50%;
        }

        /* Ordered list numbers (counter) */
        .content ol > li, .article-content ol > li {
            counter-increment: list-counter;
        }
        .content ol > li::before, .article-content ol > li::before {
            content: counter(list-counter) ".";
            position: absolute;
            left: 0;
            top: 0;
            font-weight: 600;
            color: var(--color-primary);
        }

        /* Ensure ontology-tree nested lists have no bullets */
        .ontology-tree li::before,
        .ontology-tree ul li::before {
            display: none !important;
            content: none !important;
        }

        /* === ENHANCED HORIZONTAL RULE === */
        .content hr, .article-content hr {
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--color-border), var(--color-primary), var(--color-border), transparent);
            margin: var(--spacing-2xl) 0;
            opacity: 0.6;
        }

        /* === PREMIUM CODE BLOCKS === */
        pre {
            position: relative;
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-radius: var(--radius-xl);
            padding: var(--spacing-xl);
            overflow-x: auto;
            box-shadow:
                0 4px 6px rgba(0, 0, 0, 0.1),
                0 10px 20px rgba(0, 0, 0, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }

        pre::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light), var(--color-accent));
            border-radius: var(--radius-xl) var(--radius-xl) 0 0;
        }

        /* Code block window dots */
        pre::after {
            content: '● ● ●';
            position: absolute;
            top: 12px;
            left: 16px;
            font-size: 10px;
            letter-spacing: 4px;
            color: rgba(255, 255, 255, 0.2);
        }

        pre code {
            display: block;
            padding-top: var(--spacing-md);
            color: #e2e8f0;
            font-size: 0.9rem;
            line-height: 1.7;
            tab-size: 2;
        }

        body:not(.theme-dark) pre {
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
            border-color: #e2e8f0;
        }

        body:not(.theme-dark) pre code {
            color: #334155;
        }

        body:not(.theme-dark) pre::after {
            color: rgba(0, 0, 0, 0.15);
        }

        /* === INLINE CODE ENHANCEMENT === */
        code:not(pre code) {
            padding: 3px 8px;
            font-size: 0.875em;
            font-weight: 500;
            background: linear-gradient(135deg, rgba(0, 160, 227, 0.08) 0%, rgba(0, 160, 227, 0.04) 100%);
            border: 1px solid rgba(0, 160, 227, 0.15);
            border-radius: 6px;
            color: var(--color-primary-dark);
            transition: all 0.2s ease;
        }

        code:not(pre code):hover {
            background: linear-gradient(135deg, rgba(0, 160, 227, 0.12) 0%, rgba(0, 160, 227, 0.08) 100%);
            border-color: rgba(0, 160, 227, 0.25);
        }

        body.theme-dark code:not(pre code) {
            color: var(--color-primary-light);
        }

        /* === STAGGERED FADE-IN ANIMATION === */
        @keyframes staggerFadeIn {
            from {
                opacity: 0;
                transform: translateY(12px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .content h2, .content h3,
        .article-content h2, .article-content h3 {
            animation: staggerFadeIn 0.5s ease-out backwards;
        }

        .content h2:nth-of-type(1), .article-content h2:nth-of-type(1) { animation-delay: 0.1s; }
        .content h2:nth-of-type(2), .article-content h2:nth-of-type(2) { animation-delay: 0.15s; }
        .content h2:nth-of-type(3), .article-content h2:nth-of-type(3) { animation-delay: 0.2s; }
        .content h2:nth-of-type(4), .article-content h2:nth-of-type(4) { animation-delay: 0.25s; }
        .content h2:nth-of-type(5), .article-content h2:nth-of-type(5) { animation-delay: 0.3s; }

        /* === PREMIUM CARD HOVER === */
        .content, .article-content {
            transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1),
                        box-shadow 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* === ENHANCED SEARCH INPUT === */
        .search-input {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.95) 100%);
            border: 2px solid transparent;
            box-shadow:
                0 2px 4px rgba(0, 0, 0, 0.02),
                0 4px 8px rgba(0, 0, 0, 0.02),
                inset 0 1px 0 rgba(255, 255, 255, 0.8);
        }

        body.theme-dark .search-input {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(30, 41, 59, 0.95) 100%);
            box-shadow:
                0 2px 4px rgba(0, 0, 0, 0.1),
                0 4px 8px rgba(0, 0, 0, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }

        .search-input:focus {
            border-color: var(--color-primary);
            box-shadow:
                0 0 0 4px rgba(0, 160, 227, 0.1),
                0 4px 12px rgba(0, 160, 227, 0.15);
        }

        /* === PREMIUM NAV LINKS === */
        .nav-link {
            border-radius: var(--radius-lg);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .nav-link:hover {
            transform: translateX(4px);
            background: linear-gradient(135deg, rgba(0, 160, 227, 0.08) 0%, rgba(0, 160, 227, 0.04) 100%);
        }

        .nav-link.active {
            background: linear-gradient(135deg, rgba(0, 160, 227, 0.15) 0%, rgba(0, 160, 227, 0.08) 100%);
            box-shadow: 0 2px 8px rgba(0, 160, 227, 0.15);
        }

        /* === PREMIUM PAGE NAV CARDS === */
        .page-nav-link {
            background: linear-gradient(135deg, var(--color-bg-card) 0%, var(--color-bg-secondary) 100%);
            border: 1px solid var(--color-border);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .page-nav-link:hover {
            transform: translateY(-4px);
            border-color: var(--color-primary);
            box-shadow:
                0 8px 24px rgba(0, 160, 227, 0.15),
                0 4px 12px rgba(0, 160, 227, 0.1);
        }

        .page-nav-link.prev:hover {
            transform: translateY(-4px) translateX(-4px);
        }

        .page-nav-link.next:hover {
            transform: translateY(-4px) translateX(4px);
        }

        /* === PREMIUM THEME TOGGLE === */
        .theme-toggle {
            background: linear-gradient(135deg, var(--color-bg-secondary) 0%, var(--color-bg-tertiary) 100%);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-full);
            padding: 10px 16px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .theme-toggle:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .theme-toggle:active {
            transform: scale(0.98);
        }

        /* === ENHANCED BACK TO TOP === */
        .back-to-top {
            background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
            border: 2px solid rgba(255, 255, 255, 0.2);
            box-shadow:
                0 4px 12px rgba(0, 160, 227, 0.3),
                0 8px 24px rgba(0, 160, 227, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
        }

        .back-to-top:hover {
            transform: translateY(-6px) scale(1.1);
            box-shadow:
                0 8px 20px rgba(0, 160, 227, 0.4),
                0 16px 40px rgba(0, 160, 227, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }

        /* === PREMIUM SCROLL PROGRESS === */
        .scroll-progress {
            height: 4px;
            background: linear-gradient(90deg,
                var(--color-primary-dark) 0%,
                var(--color-primary) 40%,
                var(--color-primary-light) 70%,
                var(--color-accent) 100%);
            box-shadow:
                0 0 10px rgba(0, 160, 227, 0.5),
                0 0 20px rgba(0, 160, 227, 0.3),
                0 0 30px rgba(0, 160, 227, 0.1);
        }

        /* === ENHANCED SEARCH MODAL === */
        .search-modal {
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
        }

        .search-modal-content {
            background: var(--color-bg-secondary);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow:
                0 24px 48px rgba(0, 0, 0, 0.2),
                0 12px 24px rgba(0, 0, 0, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
            border-radius: 20px;
        }

        .search-result-item {
            border-radius: var(--radius-lg);
            margin: 4px 8px;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .search-result-item:hover,
        .search-result-item.selected {
            background: linear-gradient(135deg, rgba(0, 160, 227, 0.1) 0%, rgba(0, 160, 227, 0.05) 100%);
            transform: translateX(4px);
        }

        /* === ENHANCED IMAGES === */
        .content img, .article-content img {
            border-radius: var(--radius-xl);
            box-shadow:
                0 4px 8px rgba(0, 0, 0, 0.04),
                0 8px 16px rgba(0, 0, 0, 0.04),
                0 16px 32px rgba(0, 0, 0, 0.04);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .content img:hover, .article-content img:hover {
            transform: scale(1.02) translateY(-4px);
            box-shadow:
                0 8px 16px rgba(0, 0, 0, 0.08),
                0 16px 32px rgba(0, 0, 0, 0.08),
                0 24px 48px rgba(0, 0, 0, 0.06);
        }

        /* === PREMIUM SECTION DIVIDERS === */
        .nav-section:not(:first-child) {
            margin-top: var(--spacing-sm);
            padding-top: var(--spacing-sm);
            border-top: 1px solid var(--color-border);
        }

        /* === MODERN TOC STYLING === */
        .toc {
            border-radius: var(--radius-xl);
            box-shadow:
                0 4px 12px rgba(0, 0, 0, 0.04),
                0 8px 24px rgba(0, 0, 0, 0.04);
        }

        .toc-list a {
            border-radius: var(--radius-md);
            margin: 2px 0;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .toc-list a:hover {
            background: linear-gradient(135deg, rgba(0, 160, 227, 0.08) 0%, rgba(0, 160, 227, 0.04) 100%);
            transform: translateX(4px);
        }

        .toc-list a.active {
            background: linear-gradient(135deg, rgba(0, 160, 227, 0.12) 0%, rgba(0, 160, 227, 0.06) 100%);
            color: var(--color-primary);
            font-weight: 600;
            border-left-width: 3px;
        }

        /* === SMOOTH CONTENT ENTRANCE === */
        @keyframes contentReveal {
            0% {
                opacity: 0;
                transform: translateY(30px);
                filter: blur(4px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
                filter: blur(0);
            }
        }

        .content-wrapper {
            animation: contentReveal 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }

        /* === GRADIENT TEXT FOR BRANDING === */
        .header-logo span:first-child {
            background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 50%, var(--color-accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        /* === SUBTLE NOISE TEXTURE === */
        body::after {
            content: '';
            position: fixed;
            inset: 0;
            pointer-events: none;
            opacity: 0.015;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
            z-index: 9998;
        }

        body.theme-dark::after {
            opacity: 0.03;
        }

        /* === PREMIUM FOOTER === */
        .footer {
            background: linear-gradient(180deg, transparent 0%, rgba(0, 160, 227, 0.02) 100%);
            border-top: 1px solid var(--color-border);
            padding: var(--spacing-2xl) 0;
        }

        .footer-links a {
            position: relative;
            padding: var(--spacing-xs) var(--spacing-sm);
            border-radius: var(--radius-md);
            transition: all 0.2s ease;
        }

        .footer-links a:hover {
            background: rgba(0, 160, 227, 0.08);
            color: var(--color-primary);
        }

        /* === PRINT STYLES === */
        @media print {
            .header, .sidebar, .toc, .back-to-top, .scroll-progress, .page-nav {
                display: none !important;
            }

            .main-content {
                margin: 0 !important;
                padding: 0 !important;
            }

            .content, .article-content {
                box-shadow: none !important;
                border: none !important;
            }
        }

        /* === HIGH CONTRAST MODE SUPPORT === */
        @media (prefers-contrast: high) {
            :root {
                --color-border: rgba(0, 0, 0, 0.3);
            }

            body.theme-dark {
                --color-border: rgba(255, 255, 255, 0.3);
            }
        }

        /* === REDUCED MOTION SUPPORT === */
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }

            html {
                scroll-behavior: auto;
            }
        }

</style>
</head>

<body>
    <!-- Scroll Progress Indicator -->
    <div class="scroll-progress" id="scrollProgress"></div>

    <!-- Back to Top Button -->
    <button class="back-to-top" id="backToTop" aria-label="Back to top">
        <svg fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <path d="M12 19V5M5 12l7-7 7 7" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </button>

    <header class="header">
        <button aria-label="Toggle menu" class="mobile-menu-btn">
            <svg fill="none" height="24" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" width="24">
                <line x1="3" x2="21" y1="12" y2="12"></line>
                <line x1="3" x2="21" y1="6" y2="6"></line>
                <line x1="3" x2="21" y1="18" y2="18"></line>
            </svg>
        </button>
        <a class="header-logo" href="./intro.html">
            <img src="./Logo.svg" alt="MaterialDigital Logo" style="height: 36px; width: auto;">
            <span style="display: flex; align-items: baseline; gap: 0.25rem;">
                <span style="font-weight: 700; background: linear-gradient(135deg, #00a0e3 0%, #0077b3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">PMD</span><span style="font-weight: 600; color: var(--color-text-primary);">Core</span>
                <span style="font-size: 0.8em; font-weight: 500; color: var(--color-text-muted); margin-left: 0.15rem;">Documentation</span>
            </span>
        </a>
        <nav class="header-nav" style="display: flex; gap: 0.5rem; align-items: center;">
            <a href="https://materialdigital.de/" target="_blank" style="display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.5rem 1rem; border-radius: 2rem; background: linear-gradient(135deg, rgba(0, 160, 227, 0.1) 0%, rgba(0, 119, 179, 0.08) 100%); color: var(--color-text-primary); font-weight: 500; font-size: 0.875rem; text-decoration: none; transition: all 0.2s ease; border: 1px solid rgba(0, 160, 227, 0.2);">
                <svg fill="none" height="14" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" width="14"><path d="M12 2a10 10 0 1 0 0 20a10 10 0 0 0 0-20 M12 16v-4 M12 8h.01"></path></svg>
                About
            </a>
            <a href="https://github.com/materialdigital/core-ontology" target="_blank" style="display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.5rem 1rem; border-radius: 2rem; background: linear-gradient(135deg, rgba(45, 55, 72, 0.1) 0%, rgba(26, 32, 44, 0.08) 100%); color: var(--color-text-primary); font-weight: 500; font-size: 0.875rem; text-decoration: none; transition: all 0.2s ease; border: 1px solid rgba(45, 55, 72, 0.2);">
                <svg fill="none" height="14" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" width="14"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
                GitHub
            </a>
            <a href="https://materialdigital.github.io/core-ontology" target="_blank" style="display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.5rem 1rem; border-radius: 2rem; background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.08) 100%); color: var(--color-text-primary); font-weight: 500; font-size: 0.875rem; text-decoration: none; transition: all 0.2s ease; border: 1px solid rgba(16, 185, 129, 0.2);">
                <svg fill="none" height="14" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" width="14"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20 M4 4.5A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"></path></svg>
                Widoco
            </a>
        </nav>
        <button aria-label="Toggle theme" class="theme-toggle">
            <span class="theme-icon">
                <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z"></path>
                </svg>
            </span>
            <span class="theme-label">Dark</span>
        </button>
    </header>

    <div class="sidebar-overlay"></div>
    <aside class="sidebar">
        <div class="search-container">
            <svg class="search-icon" fill="none" height="18" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"
                width="18">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" x2="16.65" y1="21" y2="16.65"></line>
            </svg>
            <input class="search-input" id="sidebar-search" name="sidebar-search" placeholder="Search docs..." readonly="" type="text" aria-label="Search documentation" />
            <span class="search-shortcut">Ctrl+K</span>
        </div>
        __SIDEBAR_HTML__
    </aside>

    <main class="main-content">
        <div class="content-wrapper">
            <nav class="breadcrumbs">
                <a href="./">Home</a><span>/</span><span class="current">Usage Patterns</span>
            </nav>

            <article class="content">
                __ARTICLE_CONTENT__

            </article>

            __PAGE_NAV__

            <footer class="footer">
                <div class="footer-links">
                    <a href="https://github.com/materialdigital/core-ontology" target="_blank">GitHub</a>
                    <a href="https://materialdigital.de/" target="_blank">MaterialDigital</a>
                    <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank">CC BY 4.0</a>
                </div>
                <p class="footer-copyright">© 2026 Platform MaterialDigital. All rights reserved.</p>
            </footer>
        </div>
    </main>

    <aside class="toc">
        <h4 class="toc-title">On this page</h4>
        <ul class="toc-list">
            __TOC_LIST_ITEMS__
        </ul>
    </aside>

    <!-- Global popover and toast elements -->
    <div class="graph-popover" id="global-popover"></div>
    <div class="graph-toast" id="global-toast"></div>

    <!-- Fullscreen overlay -->
    <div class="fullscreen-overlay" id="fullscreen-overlay" role="dialog" aria-modal="true" aria-label="Fullscreen graph viewer">
        <div class="fullscreen-header">
            <div class="fullscreen-title" id="fullscreen-title">Graph</div>
            <button class="fullscreen-close" id="fullscreen-close" aria-label="Close fullscreen">
                <span aria-hidden="true">✕</span> Close
            </button>
        </div>
        <div class="fullscreen-viewport" id="fullscreen-viewport">
            <div class="fullscreen-wrapper" id="fullscreen-wrapper"></div>
            <div class="fullscreen-zoom-controls">
                <button class="fullscreen-zoom-btn" id="fs-zoom-in" aria-label="Zoom in">+</button>
                <div class="fullscreen-zoom-level" id="fs-zoom-level" aria-live="polite">100%</div>
                <button class="fullscreen-zoom-btn" id="fs-zoom-out" aria-label="Zoom out">−</button>
            </div>
        </div>
    </div>


    <!-- Viz.js (Graphviz) -->
    <script src="https://cdn.jsdelivr.net/npm/viz.js@2.1.2/viz.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/viz.js@2.1.2/full.render.js"></script>

    <!-- Mermaid.js for diagram rendering -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>

<script type="module">
// ========== GRAPHVIZ (VIZ.JS) DIAGRAMS ==========
        const dotDiagrams = __DIAGRAMS_OBJECT__;

const nodeData = __NODEDATA_OBJECT__;

// ========== MERMAID DIAGRAMS ==========
const mermaidDiagrams = __MERMAID_DIAGRAMS_OBJECT__;

        // ========== GRAPH VIEWER CLASS ==========


        // ========== VIZ.JS RENDERING ==========
        // Viz.js v2.1.2 (Graphviz compiled to JS/WASM). We load viz.js + full.render.js as classic scripts.
        // This module relies on global Viz / Module / render injected by those scripts.
        const createViz = () => {
            try {
                if (typeof Module !== 'undefined' && typeof render !== 'undefined') {
                    return new Viz({ Module, render });
                }
            } catch (_) { /* ignore */ }
            return new Viz();
        };

        let viz = createViz();

                const CSS_DPI = 96; // browser/CSS pixel density baseline
        const DEFAULT_EXPORT_DPI = 1200; // requested production export setting
        const MAX_EXPORT_PIXELS = 80_000_000; // safety cap (~320MB RGBA)

                function normalizeDot(dot) {
            if (!dot) return dot;

            // Fix a common JS-escaping pitfall: DOT snippets that include `\"` in source
            // may end up as double-quoted attribute values at runtime (e.g., label=""sh:or"").
            // Graphviz treats this as a broken string and typically errors near the first ':'.
            //
            // Normalize: label=""..."" -> label="..."
            // Apply to a small allowlist of attributes that commonly carry human text.
            dot = dot.replace(/\b(label|tooltip|xlabel)\s*=\s*""([^"\n]*?)""/g, '$1="$2"');

            // Defensive normalization for DOT emitted by diverse toolchains.
            // Primary fix: attribute values containing ':' (e.g., sh:targetClass) MUST be quoted in DOT when unquoted.
            // Secondary: some generators emit unquoted attribute values with spaces; DOT requires quoting.
            // Strategy: quote attribute values up to the next ',', ']' or ';' when they contain ':' or whitespace.
            return dot.replace(/(=)\s*([^"\[\]<>][^,\]\n;]*)/g, (m, eq, rawVal) => {
                const v = String(rawVal).trim();
                if (!v) return m;

                // leave numerics/booleans as-is
                if (/^[+-]?\d+(\.\d+)?$/.test(v)) return `${eq}${v}`;
                if (/^(true|false)$/i.test(v)) return `${eq}${v}`;

                // HTML-like values are valid without quotes: label=<...>
                if (v.startsWith('<') && v.endsWith('>')) return `${eq}${v}`;

                const needsQuotes = v.includes(':') || /\s/.test(v) || v.includes('//');
                if (!needsQuotes) return `${eq}${v}`;

                const escaped = v.replace(/"/g, '\\"');
                return `${eq}"${escaped}"`;
            });
        }

        async function renderDotToSvg(dot) {
            const normalized = normalizeDot(dot);
            try {
                return await viz.renderSVGElement(normalized);
            } catch (err) {
                // Viz instances can become unusable after a render error; recreate and retry once.
                viz = createViz();
                return await viz.renderSVGElement(normalized);
            }
        }

        function sanitizeGraphSvg(svg) {
            // Prevent navigation: remove all hyperlink targets/hrefs injected by DOT URL/href attributes.
            svg.querySelectorAll('a').forEach(a => {
                a.removeAttribute('href');
                a.removeAttribute('xlink:href');
                a.removeAttribute('target');
                a.style.cursor = 'pointer';
            });

            // Make sure SVG is well-formed for downloads.
            svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
            svg.style.maxWidth = 'none';
            svg.style.overflow = 'visible';

            // Improve text rendering consistency.
            svg.querySelectorAll('text').forEach(t => {
                t.style.userSelect = 'none';
            });

            // Rotate edge labels to follow the edge direction
            rotateEdgeLabels(svg);
        }

        function rotateEdgeLabels(svg) {
            // Find all edge groups in the SVG
            svg.querySelectorAll('g.edge').forEach(edgeGroup => {
                // Get the path element (the edge line)
                const path = edgeGroup.querySelector('path');
                // Get the text element (the label)
                const text = edgeGroup.querySelector('text');
                
                if (!path || !text) return;
                
                // Get the path's d attribute
                const d = path.getAttribute('d');
                if (!d) return;
                
                // Parse the path to get start and end points
                // Graphviz paths typically use M (moveto) and C (curveto) or L (lineto)
                const points = parsePathPoints(d);
                if (points.length < 2) return;
                
                // Get the text position
                const textX = parseFloat(text.getAttribute('x')) || 0;
                const textY = parseFloat(text.getAttribute('y')) || 0;
                
                // Find the closest segment to the text label
                const angle = calculateAngleAtPoint(points, textX, textY);
                
                // Apply rotation transform to the text
                // Rotate around the text's anchor point
                if (Math.abs(angle) > 0.1) { // Only rotate if angle is significant
                    // Adjust angle to keep text readable (not upside down)
                    let displayAngle = angle;
                    if (displayAngle > 90) displayAngle -= 180;
                    if (displayAngle < -90) displayAngle += 180;
                    
                    text.setAttribute('transform', `rotate(${displayAngle}, ${textX}, ${textY})`);
                }
            });
        }

        function parsePathPoints(d) {
            const points = [];
            // Match path commands: M, L, C, Q, etc. followed by coordinates
            const regex = /([MLCQSTZ])([^MLCQSTZ]*)/gi;
            let match;
            let currentX = 0, currentY = 0;
            
            while ((match = regex.exec(d)) !== null) {
                const cmd = match[1].toUpperCase();
                const coords = match[2].trim().split(/[\\s,]+/).map(parseFloat).filter(n => !isNaN(n));
                
                switch (cmd) {
                    case 'M':
                    case 'L':
                        if (coords.length >= 2) {
                            currentX = coords[0];
                            currentY = coords[1];
                            points.push({ x: currentX, y: currentY });
                        }
                        break;
                    case 'C': // Cubic bezier: x1,y1 x2,y2 x,y
                        if (coords.length >= 6) {
                            // Add control points and end point
                            points.push({ x: coords[0], y: coords[1] });
                            points.push({ x: coords[2], y: coords[3] });
                            currentX = coords[4];
                            currentY = coords[5];
                            points.push({ x: currentX, y: currentY });
                        }
                        break;
                    case 'Q': // Quadratic bezier: x1,y1 x,y
                        if (coords.length >= 4) {
                            points.push({ x: coords[0], y: coords[1] });
                            currentX = coords[2];
                            currentY = coords[3];
                            points.push({ x: currentX, y: currentY });
                        }
                        break;
                }
            }
            return points;
        }

        function calculateAngleAtPoint(points, textX, textY) {
            if (points.length < 2) return 0;
            
            // Find the two closest points to the text position
            let minDist = Infinity;
            let closestIdx = 0;
            
            for (let i = 0; i < points.length; i++) {
                const dist = Math.sqrt(Math.pow(points[i].x - textX, 2) + Math.pow(points[i].y - textY, 2));
                if (dist < minDist) {
                    minDist = dist;
                    closestIdx = i;
                }
            }
            
            // Get the segment containing or near the closest point
            let p1, p2;
            if (closestIdx === 0) {
                p1 = points[0];
                p2 = points[1];
            } else if (closestIdx === points.length - 1) {
                p1 = points[points.length - 2];
                p2 = points[points.length - 1];
            } else {
                // Use the surrounding points
                p1 = points[closestIdx - 1];
                p2 = points[closestIdx + 1];
            }
            
            // Calculate angle in degrees
            const dx = p2.x - p1.x;
            const dy = p2.y - p1.y;
            const angle = Math.atan2(dy, dx) * (180 / Math.PI);
            
            return angle;
        }

        

        // ---------- High-resolution PNG export (1200 DPI default) ----------
        function parseSvgLengthToPx(lenStr) {
            if (!lenStr) return null;
            const s = String(lenStr).trim();
            const m = s.match(/^([+-]?\d*\.?\d+)([a-z%]*)$/i);
            if (!m) return null;
            const value = parseFloat(m[1]);
            const unit = (m[2] || '').toLowerCase();
            if (!isFinite(value)) return null;

            // CSS px baseline is 96 DPI.
            switch (unit) {
                case '':
                case 'px': return value;
                case 'pt': return value * (CSS_DPI / 72);
                case 'pc': return value * (CSS_DPI / 6);
                case 'in': return value * CSS_DPI;
                case 'cm': return value * (CSS_DPI / 2.54);
                case 'mm': return value * (CSS_DPI / 25.4);
                default: return value; // fallback
            }
        }

        function getSvgSizePx(svg) {
            const wAttr = svg.getAttribute('width');
            const hAttr = svg.getAttribute('height');
            const w = parseSvgLengthToPx(wAttr);
            const h = parseSvgLengthToPx(hAttr);
            if (w && h) return { width: w, height: h };

            const vb = svg.getAttribute('viewBox');
            if (vb) {
                const parts = vb.trim().split(/\s+/).map(Number);
                if (parts.length === 4 && parts.every(n => isFinite(n))) {
                    return { width: Math.abs(parts[2]), height: Math.abs(parts[3]) };
                }
            }

            const rect = svg.getBoundingClientRect?.();
            if (rect && rect.width && rect.height) return { width: rect.width, height: rect.height };
            return { width: 1200, height: 800 };
        }

        function crc32(buf) {
            let crc = 0xFFFFFFFF;
            for (let i = 0; i < buf.length; i++) {
                crc ^= buf[i];
                for (let k = 0; k < 8; k++) {
                    const mask = -(crc & 1);
                    crc = (crc >>> 1) ^ (0xEDB88320 & mask);
                }
            }
            return (crc ^ 0xFFFFFFFF) >>> 0;
        }

        function makePngChunk(type, data) {
            const t = new TextEncoder().encode(type);
            const len = data.length;
            const chunk = new Uint8Array(8 + len + 4);
            chunk[0] = (len >>> 24) & 255;
            chunk[1] = (len >>> 16) & 255;
            chunk[2] = (len >>> 8) & 255;
            chunk[3] = (len) & 255;
            chunk.set(t, 4);
            chunk.set(data, 8);

            const crcBuf = new Uint8Array(t.length + data.length);
            crcBuf.set(t, 0);
            crcBuf.set(data, t.length);
            const crc = crc32(crcBuf);

            const o = 8 + len;
            chunk[o + 0] = (crc >>> 24) & 255;
            chunk[o + 1] = (crc >>> 16) & 255;
            chunk[o + 2] = (crc >>> 8) & 255;
            chunk[o + 3] = (crc) & 255;
            return chunk;
        }

        async function setPngDpi(blob, dpi) {
            try {
                const ab = await blob.arrayBuffer();
                const bytes = new Uint8Array(ab);
                const sig = [137, 80, 78, 71, 13, 10, 26, 10];
                for (let i = 0; i < sig.length; i++) if (bytes[i] !== sig[i]) return blob;

                const ppm = Math.max(1, Math.round(dpi / 0.0254));
                const data = new Uint8Array(9);
                data[0] = (ppm >>> 24) & 255;
                data[1] = (ppm >>> 16) & 255;
                data[2] = (ppm >>> 8) & 255;
                data[3] = (ppm) & 255;
                data[4] = data[0];
                data[5] = data[1];
                data[6] = data[2];
                data[7] = data[3];
                data[8] = 1;

                const pHYs = makePngChunk('pHYs', data);

                const out = [];
                out.push(bytes.slice(0, 8));

                let offset = 8;
                let inserted = false;

                while (offset + 8 <= bytes.length) {
                    const len = (bytes[offset] << 24) | (bytes[offset + 1] << 16) | (bytes[offset + 2] << 8) | bytes[offset + 3];
                    const type = String.fromCharCode(bytes[offset + 4], bytes[offset + 5], bytes[offset + 6], bytes[offset + 7]);
                    const chunkTotal = 8 + len + 4;
                    const chunkBytes = bytes.slice(offset, offset + chunkTotal);

                    out.push(chunkBytes);

                    if (!inserted && type === 'IHDR') {
                        out.push(pHYs);
                        inserted = true;
                    }
                    offset += chunkTotal;
                    if (type === 'IEND') break;
                }

                const mergedLen = out.reduce((a, b) => a + b.length, 0);
                const merged = new Uint8Array(mergedLen);
                let p = 0;
                for (const part of out) { merged.set(part, p); p += part.length; }

                return new Blob([merged], { type: 'image/png' });
            } catch (_) {
                return blob;
            }
        }

        function loadImageFromUrl(url) {
            return new Promise((resolve, reject) => {
                const img = new Image();
                img.decoding = 'async';
                img.onload = () => resolve(img);
                img.onerror = reject;
                img.src = url;
            });
        }

        async function exportSvgToPng(svg, { dpi = DEFAULT_EXPORT_DPI, background = null } = {}) {
            const size = getSvgSizePx(svg);
            const baseW = Math.max(1, size.width);
            const baseH = Math.max(1, size.height);

            let scale = dpi / CSS_DPI;
            let outW = Math.round(baseW * scale);
            let outH = Math.round(baseH * scale);

            const basePixels = baseW * baseH;
            const desiredPixels = outW * outH;

            let actualDpi = dpi;
            if (desiredPixels > MAX_EXPORT_PIXELS) {
                const safeScale = Math.sqrt(MAX_EXPORT_PIXELS / basePixels);
                scale = Math.max(1, safeScale);
                outW = Math.round(baseW * scale);
                outH = Math.round(baseH * scale);
                actualDpi = Math.round(scale * CSS_DPI);
            }

            const svgText = new XMLSerializer().serializeToString(svg);
            const svgBlob = new Blob([svgText], { type: 'image/svg+xml;charset=utf-8' });
            const url = URL.createObjectURL(svgBlob);

            try {
                const img = await loadImageFromUrl(url);
                const canvas = document.createElement('canvas');
                canvas.width = outW;
                canvas.height = outH;
                const ctx = canvas.getContext('2d', { alpha: true });
                if (!ctx) throw new Error('Canvas not available');

                if (background) {
                    ctx.fillStyle = background;
                    ctx.fillRect(0, 0, outW, outH);
                } else {
                    ctx.clearRect(0, 0, outW, outH);
                }

                ctx.imageSmoothingEnabled = true;
                ctx.setTransform(scale, 0, 0, scale, 0, 0);
                ctx.drawImage(img, 0, 0);

                const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));
                if (!blob) throw new Error('PNG generation failed');

                const dpiBlob = await setPngDpi(blob, actualDpi);
                return { blob: dpiBlob, dpi: actualDpi, width: outW, height: outH };
            } finally {
                URL.revokeObjectURL(url);
            }
        }

function parseEdgeTitle(title) {
            const raw = (title || '').trim();
            const m1 = raw.match(/^(.+?)->(.+?)$/);
            if (m1) return { src: m1[1].trim(), dst: m1[2].trim(), directed: true };
            const m2 = raw.match(/^(.+?)--(.+?)$/);
            if (m2) return { src: m2[1].trim(), dst: m2[2].trim(), directed: false };
            return null;
        }

        function getNodeIdFromG(g) {
            const t = g.querySelector('title')?.textContent?.trim();
            return t || null;
        }

        function getNodeLabelFromG(g) {
            const texts = Array.from(g.querySelectorAll('text')).map(t => (t.textContent || '').trim()).filter(Boolean);
            return texts.join(' ');
        }

        function getNodeMetaFromG(g) {
            const id = getNodeIdFromG(g) || g.getAttribute('id') || '';
            const label = getNodeLabelFromG(g) || id;
            const a = g.closest('a');
            const tooltip = a?.getAttribute('xlink:title') || a?.getAttribute('title') || null;
            return { id, label, tooltip };
        }

        // ========== FULLSCREEN MANAGER (ROBUST CLOSE) ==========
        const FullscreenManager = (() => {
            const overlay = document.getElementById('fullscreen-overlay');
            const wrapper = document.getElementById('fullscreen-wrapper');
            const titleEl = document.getElementById('fullscreen-title');
            const viewport = document.getElementById('fullscreen-viewport');
            const zoomLevel = document.getElementById('fs-zoom-level');
            const closeBtn = document.getElementById('fullscreen-close');
            const zoomInBtn = document.getElementById('fs-zoom-in');
            const zoomOutBtn = document.getElementById('fs-zoom-out');

            let fsScale = 1, fsTx = 0, fsTy = 0, fsDrag = false, fsSx = 0, fsSy = 0;
            let currentSvg = null;
            let onNodeClick = null;

            const update = () => {
                wrapper.style.transform = `translate(${fsTx}px, ${fsTy}px) scale(${fsScale})`;
                zoomLevel.textContent = `${Math.round(fsScale * 100)}%`;
            };

            const fit = () => {
                if (!currentSvg) return;
                const sr = currentSvg.getBoundingClientRect();
                const vr = viewport.getBoundingClientRect();
                if (!sr.width || !sr.height) return;
                fsScale = Math.min(vr.width / sr.width, vr.height / sr.height, 2) * 0.92;
                fsTx = (vr.width - sr.width * fsScale) / 2;
                fsTy = (vr.height - sr.height * fsScale) / 2;
                update();
            };

            const close = () => {
                overlay.classList.remove('active');
                document.body.style.overflow = '';
                wrapper.innerHTML = '';
                currentSvg = null;
                onNodeClick = null;
            };

            // Bind once (fixes "close button not working" across repeated opens).
            closeBtn.addEventListener('click', (e) => { e.preventDefault(); e.stopPropagation(); close(); });
            overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });

            zoomInBtn.addEventListener('click', () => { fsScale = Math.min(5, fsScale * 1.2); update(); });
            zoomOutBtn.addEventListener('click', () => { fsScale = Math.max(0.1, fsScale / 1.2); update(); });

            viewport.addEventListener('wheel', (e) => {
                if (!overlay.classList.contains('active')) return;
                e.preventDefault();
                const ns = Math.max(0.1, Math.min(5, fsScale * (e.deltaY > 0 ? 0.9 : 1.1)));
                const r = viewport.getBoundingClientRect();
                const mx = e.clientX - r.left;
                const my = e.clientY - r.top;
                const sd = ns - fsScale;
                fsTx -= (mx - fsTx) * (sd / fsScale);
                fsTy -= (my - fsTy) * (sd / fsScale);
                fsScale = ns;
                update();
            }, { passive: false });

            viewport.addEventListener('mousedown', (e) => {
                if (!overlay.classList.contains('active')) return;
                if (e.target.closest('g.node')) return;
                fsDrag = true;
                fsSx = e.clientX - fsTx;
                fsSy = e.clientY - fsTy;
            });

            window.addEventListener('mousemove', (e) => {
                if (!overlay.classList.contains('active')) return;
                if (!fsDrag) return;
                fsTx = e.clientX - fsSx;
                fsTy = e.clientY - fsSy;
                update();
            });

            window.addEventListener('mouseup', () => { fsDrag = false; });

            window.addEventListener('keydown', (e) => {
                if (!overlay.classList.contains('active')) return;
                if (e.key === 'Escape') close();
            });

            wrapper.addEventListener('click', (e) => {
                if (!overlay.classList.contains('active')) return;
                const node = e.target.closest('g.node');
                if (!node) return;
                if (e.target.closest('a')) e.preventDefault();
                e.stopPropagation();
                onNodeClick?.(node, e.clientX, e.clientY);
            }, true);

            return {
                open({ svg, title, onNodeClick: handler }) {
                    if (!svg) return;
                    overlay.classList.add('active');
                    document.body.style.overflow = 'hidden';
                    titleEl.textContent = title || 'Graph View';

                    wrapper.innerHTML = '';
                    const clone = svg.cloneNode(true);
                    wrapper.appendChild(clone);
                    currentSvg = clone;
                    onNodeClick = handler || null;

                    sanitizeGraphSvg(clone);

                    fsScale = 1; fsTx = 0; fsTy = 0; fsDrag = false; fsSx = 0; fsSy = 0;
                    update();
                    setTimeout(fit, 50);
                },
                close
            };
        })();

        // ========== GRAPH VIEWER (DOT -> SVG) ==========
        class GraphvizGraphViewer {
            constructor(containerId, diagramId, dotCode, data) {
                this.container = document.getElementById(containerId);
                this.diagramId = diagramId;
                this.dotCode = dotCode;
                this.nodeData = data || {};
                this.scale = 1;
                this.tx = 0;
                this.ty = 0;
                this.drag = false;
                this.sx = 0;
                this.sy = 0;

                this.wrapper = this.container.querySelector('.graph-wrapper');
                this.viewport = this.container.querySelector('.graph-viewport');
                this.diagramEl = this.container.querySelector('.mermaid-diagram'); // keep existing markup class
                this.zoomLevel = this.container.querySelector('.zoom-level');
                this.popover = document.getElementById('global-popover');
                this.toast = document.getElementById('global-toast');

                this.nodeIndex = new Map();
                this.edges = [];
                this.neighbors = new Map();

                this.searchState = { query: '', matches: [], idx: 0 };
                this.injectSearchUI();

                this.init();
            }

            injectSearchUI() {
                const header = this.container.querySelector('.graph-header .graph-controls');
                if (!header) return;
                if (header.querySelector('.graph-search')) return;

                const searchId = `graph-search-${this.containerId || Date.now()}`;
                const input = document.createElement('input');
                input.className = 'graph-search';
                input.type = 'search';
                input.id = searchId;
                input.name = searchId;
                input.placeholder = 'Search nodes…';
                input.autocomplete = 'off';
                input.spellcheck = false;
                input.setAttribute('aria-label', 'Search graph nodes');

                const clear = document.createElement('button');
                clear.className = 'graph-btn graph-search-clear';
                clear.type = 'button';
                clear.title = 'Clear search';
                clear.textContent = '✕';
                clear.setAttribute('aria-label', 'Clear search');

                header.prepend(clear);
                header.prepend(input);

                input.addEventListener('input', () => this.applySearch(input.value));
                input.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') { e.preventDefault(); this.jumpToNextMatch(); }
                    if (e.key === 'Escape') { input.value = ''; this.applySearch(''); input.blur(); }
                });

                clear.addEventListener('click', () => { input.value = ''; this.applySearch(''); input.focus(); });
            }

            async init() {
                try {
                    const svg = await renderDotToSvg(this.dotCode);
                    this.diagramEl.innerHTML = '';
                    this.diagramEl.appendChild(svg);
                    sanitizeGraphSvg(svg);

                    this.indexSvg(svg);
                    this.updateLegend(svg);
                    this.bindEvents();
                    setTimeout(() => this.fitView(), 80);
                } catch (e) {
                    console.error('Viz.js render error:', e);
                    this.diagramEl.innerHTML = `<div style="color: var(--color-error); padding: 20px;">Error rendering diagram: ${e?.message || e}</div>`;
                }
            }

            updateLegend(svg) {
                // Detect which node types and ontologies are present in the graph
                const legend = this.container.querySelector('.graph-legend');
                if (!legend) return;

                // Color to legend type mapping based on fill colors from GRAPHVIZ_NODE_STYLES
                const colorToLegend = {
                    '#F556CB': 'bfo',
                    '#f556cb': 'bfo',
                    '#F6A252': 'iao',
                    '#f6a252': 'iao',
                    '#F5D5B1': 'obi',
                    '#f5d5b1': 'obi',
                    '#93AFF3': 'cob',
                    '#93aff3': 'cob',
                    '#46CAD3': 'pmd',
                    '#46cad3': 'pmd',
                    '#F43F5E': 'ro',
                    '#f43f5e': 'ro',
                    '#C9DBFE': 'qudt',
                    '#c9dbfe': 'qudt',
                    '#FDFDC8': 'cls',
                    '#fdfdc8': 'cls',
                    '#E6E6E6': 'ind',
                    '#e6e6e6': 'ind',
                    '#93D053': 'lit',
                    '#93d053': 'lit',
                    '#99F6E4': 'cat',
                    '#99f6e4': 'cat',
                    '#A5F3FC': 'shacl',
                    '#a5f3fc': 'shacl',
                    '#FED7AA': 'constraint',
                    '#fed7aa': 'constraint',
                };

                const foundTypes = new Set();

                // Check all nodes for their fill colors
                svg.querySelectorAll('g.node').forEach(node => {
                    // Check ellipse, polygon, rect for fill color
                    const shapes = node.querySelectorAll('ellipse, polygon, rect, path');
                    shapes.forEach(shape => {
                        const fill = shape.getAttribute('fill');
                        if (fill && colorToLegend[fill]) {
                            foundTypes.add(colorToLegend[fill]);
                        }
                        // Also check for ellipse shape which indicates individual
                        if (shape.tagName === 'ellipse') {
                            foundTypes.add('ind');
                        }
                    });
                });

                // Check for edges (always show property legend if there are edges)
                const edges = svg.querySelectorAll('g.edge');
                if (edges.length > 0) {
                    foundTypes.add('property');
                    // Check for dashed edges (rdf:type)
                    edges.forEach(edge => {
                        const path = edge.querySelector('path');
                        if (path) {
                            const style = path.getAttribute('style') || '';
                            const strokeDasharray = path.getAttribute('stroke-dasharray');
                            if (style.includes('dashed') || strokeDasharray) {
                                foundTypes.add('type');
                            }
                        }
                    });
                }

                // Check for literals (note shape)
                svg.querySelectorAll('g.node polygon').forEach(poly => {
                    const fill = poly.getAttribute('fill');
                    if (fill && (fill.toLowerCase() === '#93d053')) {
                        foundTypes.add('lit');
                    }
                });

                // Show/hide legend items based on what's found
                legend.querySelectorAll('.legend-item[data-legend]').forEach(item => {
                    const legendType = item.getAttribute('data-legend');
                    if (foundTypes.has(legendType)) {
                        item.style.display = 'inline-flex';
                    } else {
                        item.style.display = 'none';
                    }
                });
            }

            indexSvg(svg) {
                this.nodeIndex.clear();
                this.edges = [];
                this.neighbors.clear();

                svg.querySelectorAll('g.node').forEach(g => {
                    const id = getNodeIdFromG(g);
                    if (!id) return;
                    const label = getNodeLabelFromG(g) || id;
                    this.nodeIndex.set(id, { g, label });
                });

                svg.querySelectorAll('g.edge').forEach(g => {
                    const title = g.querySelector('title')?.textContent || '';
                    const parsed = parseEdgeTitle(title);
                    if (!parsed) return;
                    this.edges.push({ g, src: parsed.src, dst: parsed.dst, directed: parsed.directed });

                    if (!this.neighbors.has(parsed.src)) this.neighbors.set(parsed.src, new Set());
                    if (!this.neighbors.has(parsed.dst)) this.neighbors.set(parsed.dst, new Set());
                    this.neighbors.get(parsed.src).add(parsed.dst);
                    this.neighbors.get(parsed.dst).add(parsed.src);
                });
            }

            update() {
                this.wrapper.style.transform = `translate(${this.tx}px, ${this.ty}px) scale(${this.scale})`;
                this.zoomLevel.textContent = `${Math.round(this.scale * 100)}%`;
            }

            zoomIn() { this.scale = Math.min(3, this.scale * 1.2); this.hidePop(); this.update(); }
            zoomOut() { this.scale = Math.max(0.2, this.scale / 1.2); this.hidePop(); this.update(); }

            resetView() { this.clearFocus(); this.hidePop(); this.fitView(); }

            fitView() {
                const svg = this.diagramEl.querySelector('svg');
                if (!svg) return;
                const sr = svg.getBoundingClientRect();
                const wr = this.viewport.getBoundingClientRect();
                if (!sr.width || !sr.height) return;
                this.scale = Math.min(wr.width / sr.width, wr.height / sr.height, 1) * 0.88;
                this.tx = (wr.width - sr.width * this.scale) / 2;
                this.ty = (wr.height - sr.height * this.scale) / 2;
                this.clearFocus();
                this.hidePop();
                this.update();
            }

            showToast(msg) {
                this.toast.textContent = msg;
                this.toast.style.display = 'block';
                clearTimeout(this._toastTimeout);
                this._toastTimeout = setTimeout(() => this.toast.style.display = 'none', 1800);
            }

            async copyText(text) {
                try { await navigator.clipboard.writeText(text); this.showToast('Copied to clipboard'); }
                catch { this.showToast('Copy failed'); }
            }

            showPopForNode(nodeG, x, y) {
                const meta = getNodeMetaFromG(nodeG);
                const nodeId = meta.id;

                const data = this.nodeData[nodeId];
                const label = data?.label || meta.label || nodeId;
                const uri = data?.uri || meta.tooltip || null;

                let cat;
                switch (data?.type) {
                    case 'Class': cat = 'Class (TBox)'; break;
                    case 'Literal': cat = 'Literal'; break;
                    case 'Categorical': cat = 'Categorical Value'; break;
                    case 'SHACL Shape': cat = 'SHACL Shape'; break;
                    case 'Constraint': cat = 'SHACL Constraint'; break;
                    case undefined: cat = 'Node'; break;
                    default: cat = 'Individual (ABox)';
                }

                this.popover.innerHTML = `<div class="pop-head">
                    <button class="close-btn" type="button">×</button>
                    <div class="pop-title">${label}<span class="badge">${cat}</span></div>
                    <div class="pop-uri">${uri || 'No URI available'}</div>
                    <div class="pop-actions">
                        <button class="chip" type="button" data-copy="label">📋 Copy Label</button>
                        ${uri ? '<button class="chip" type="button" data-copy="uri">🔗 Copy URI</button>' : ''}
                        <button class="chip" type="button" data-copy="id">🆔 Copy ID</button>
                    </div>
                </div>`;

                this.popover.querySelector('.close-btn')?.addEventListener('click', () => this.popover.classList.remove('visible'));
                this.popover.querySelector('[data-copy="label"]')?.addEventListener('click', () => this.copyText(label));
                this.popover.querySelector('[data-copy="uri"]')?.addEventListener('click', () => uri && this.copyText(uri));
                this.popover.querySelector('[data-copy="id"]')?.addEventListener('click', () => this.copyText(nodeId));

                this.popover.classList.add('visible');
                const pr = this.popover.getBoundingClientRect();
                this.popover.style.left = Math.max(10, Math.min(x + 10, window.innerWidth - pr.width - 10)) + 'px';
                this.popover.style.top = Math.max(10, Math.min(y + 10, window.innerHeight - pr.height - 10)) + 'px';
            }

            hidePop() {
                this.popover.classList.remove('visible');
                this.diagramEl.querySelectorAll('g.node.selected').forEach(n => n.classList.remove('selected'));
            }

            downloadSVG() {
                const svg = this.diagramEl.querySelector('svg');
                if (!svg) return this.showToast('SVG not ready');
                const clone = svg.cloneNode(true);
                sanitizeGraphSvg(clone);
                const svgText = new XMLSerializer().serializeToString(clone);
                const blob = new Blob([svgText], { type: 'image/svg+xml;charset=utf-8' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${this.diagramId}.svg`;
                a.click();
                URL.revokeObjectURL(url);
                this.showToast('Downloading SVG…');
            }

            async downloadPNG() {
                const svg = this.diagramEl.querySelector('svg');
                if (!svg) return this.showToast('PNG not ready');

                const clone = svg.cloneNode(true);
                sanitizeGraphSvg(clone);

                // Always use transparent background for PNG export
                const background = null;

                try {
                    const { blob, dpi } = await exportSvgToPng(clone, { dpi: DEFAULT_EXPORT_DPI, background });
                    const pngUrl = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = pngUrl;
                    a.download = `${this.diagramId}-${dpi}dpi.png`;
                    a.click();
                    setTimeout(() => URL.revokeObjectURL(pngUrl), 2000);

                    if (dpi === DEFAULT_EXPORT_DPI) this.showToast(`Downloading PNG (${dpi} DPI)…`);
                    else this.showToast(`Downloading PNG (~${dpi} DPI)…`);
                } catch (e) {
                    console.error('PNG export failed', e);
                    this.showToast('PNG export failed');
                }
            }openFullscreen() {
                const svg = this.diagramEl.querySelector('svg');
                if (!svg) return this.showToast('Graph not ready');
                const graphTitle = this.container.querySelector('.graph-title');
                const title = graphTitle ? graphTitle.textContent : 'Graph View';

                FullscreenManager.open({
                    svg,
                    title,
                    onNodeClick: (nodeG, x, y) => this.showPopForNode(nodeG, x, y)
                });
            }

            applySearch(query) {
                this.searchState.query = (query || '').trim().toLowerCase();
                this.searchState.matches = [];
                this.searchState.idx = 0;

                const q = this.searchState.query;
                this.diagramEl.querySelectorAll('g.node.search-match').forEach(n => n.classList.remove('search-match'));
                if (!q) return;

                for (const [id, info] of this.nodeIndex.entries()) {
                    if (info.label.toLowerCase().includes(q) || id.toLowerCase().includes(q)) {
                        info.g.classList.add('search-match');
                        this.searchState.matches.push(id);
                    }
                }
            }

            jumpToNextMatch() {
                const matches = this.searchState.matches;
                if (!matches.length) return this.showToast('No matches');
                const id = matches[this.searchState.idx % matches.length];
                this.searchState.idx = (this.searchState.idx + 1) % matches.length;
                const info = this.nodeIndex.get(id);
                if (!info) return;
                this.selectNode(info.g);
                this.panToNode(info.g);
            }

            panToNode(nodeG) {
                const vr = this.viewport.getBoundingClientRect();
                const nr = nodeG.getBoundingClientRect();
                const cx = (nr.left + nr.right) / 2;
                const cy = (nr.top + nr.bottom) / 2;
                const tx = vr.left + vr.width / 2;
                const ty = vr.top + vr.height / 2;
                this.tx += (tx - cx);
                this.ty += (ty - cy);
                this.update();
            }

            selectNode(nodeG) {
                this.diagramEl.querySelectorAll('g.node.selected').forEach(n => n.classList.remove('selected'));
                nodeG.classList.add('selected');
            }

            setFocus(nodeId) {
                const keep = new Set([nodeId]);
                const neigh = this.neighbors.get(nodeId);
                if (neigh) neigh.forEach(x => keep.add(x));

                this.diagramEl.querySelectorAll('g.node').forEach(g => {
                    const id = getNodeIdFromG(g);
                    if (!id) return;
                    g.classList.toggle('dimmed', !keep.has(id));
                });

                this.diagramEl.querySelectorAll('g.edge').forEach(g => g.classList.add('dimmed'));
                this.edges.forEach(e => {
                    const hit = e.src === nodeId || e.dst === nodeId;
                    e.g.classList.toggle('highlight-edge', hit);
                    e.g.classList.toggle('dimmed', !hit);
                });
            }

            clearFocus() {
                this.diagramEl.querySelectorAll('g.node.dimmed').forEach(g => g.classList.remove('dimmed'));
                this.diagramEl.querySelectorAll('g.edge.dimmed').forEach(g => g.classList.remove('dimmed'));
                this.diagramEl.querySelectorAll('g.edge.highlight-edge').forEach(g => g.classList.remove('highlight-edge'));
            }

            bindEvents() {
                this.container.querySelectorAll('.zoom-btn').forEach(btn => {
                    btn.addEventListener('click', () => {
                        const action = btn.dataset.action;
                        if (action === 'zoom-in') this.zoomIn();
                        if (action === 'zoom-out') this.zoomOut();
                    });
                });

                this.container.querySelectorAll('.graph-btn').forEach(btn => {
                    btn.addEventListener('click', () => {
                        const action = btn.dataset.action;
                        if (action === 'fit') this.fitView();
                        if (action === 'reset') this.resetView();
                        if (action === 'svg') this.downloadSVG();
                        if (action === 'png') this.downloadPNG();
                        if (action === 'fullscreen') this.openFullscreen();
                    });
                });

                this.viewport.addEventListener('wheel', (e) => {
                    e.preventDefault();
                    const ns = Math.max(0.2, Math.min(3, this.scale * (e.deltaY > 0 ? 0.9 : 1.1)));
                    const r = this.viewport.getBoundingClientRect();
                    const mx = e.clientX - r.left;
                    const my = e.clientY - r.top;
                    const sd = ns - this.scale;
                    this.tx -= (mx - this.tx) * (sd / this.scale);
                    this.ty -= (my - this.ty) * (sd / this.scale);
                    this.scale = ns;
                    this.hidePop();
                    this.update();
                }, { passive: false });

                this.viewport.addEventListener('mousedown', (e) => {
                    if (e.target.closest('g.node')) return;
                    this.drag = true;
                    this.sx = e.clientX - this.tx;
                    this.sy = e.clientY - this.ty;
                    this.hidePop();
                });

                window.addEventListener('mousemove', (e) => {
                    if (!this.drag) return;
                    this.tx = e.clientX - this.sx;
                    this.ty = e.clientY - this.sy;
                    this.update();
                });

                window.addEventListener('mouseup', () => { this.drag = false; });

                this.diagramEl.addEventListener('click', (e) => {
                    if (e.target.closest('a')) e.preventDefault();
                    const node = e.target.closest('g.node');
                    if (node) {
                        const id = getNodeIdFromG(node);
                        if (id) {
                            this.selectNode(node);
                            this.setFocus(id);
                            this.showPopForNode(node, e.clientX, e.clientY);
                        }
                        e.stopPropagation();
                    } else {
                        this.clearFocus();
                        this.hidePop();
                    }
                }, true);

                this.diagramEl.addEventListener('mouseover', (e) => {
                    const node = e.target.closest('g.node');
                    if (node) node.classList.add('hovered');
                });

                this.diagramEl.addEventListener('mouseout', (e) => {
                    const node = e.target.closest('g.node');
                    if (node) node.classList.remove('hovered');
                });

                this.diagramEl.addEventListener('dblclick', (e) => { e.preventDefault(); this.fitView(); });

                this.container.addEventListener('mouseenter', () => this._active = true);
                this.container.addEventListener('mouseleave', () => this._active = false);
                window.addEventListener('keydown', (e) => {
                    if (!this._active) return;
                    if (e.key === 'f') this.fitView();
                    if (e.key === 'r') this.resetView();
                    if (e.key === 'Escape') { this.clearFocus(); this.hidePop(); }
                });
            }
        }

        // Create viewers sequentially to avoid Viz render conflicts
        async function initAllDiagrams() {
            // Initialize Graphviz (DOT) diagrams
            const entries = Object.entries(dotDiagrams);
            for (const [id, dot] of entries) {
                const containerId = `graph-${id}`;
                const diagramId = `diagram-${id}`;
                const data = nodeData[id] || {};
                new GraphvizGraphViewer(containerId, diagramId, dot, data);
                await new Promise(resolve => setTimeout(resolve, 30));
            }

            // Initialize Mermaid diagrams
            await initMermaidDiagrams();
        }

        // ========== MERMAID DIAGRAM RENDERING ==========
        async function initMermaidDiagrams() {
            const mermaidEntries = Object.entries(mermaidDiagrams);
            if (mermaidEntries.length === 0) return;

            // Initialize Mermaid with theme-aware configuration
            const isDark = document.body.classList.contains('theme-dark');
            mermaid.initialize({
                startOnLoad: false,
                theme: isDark ? 'dark' : 'default',
                securityLevel: 'loose',
                flowchart: {
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis'
                }
            });

            for (const [id, code] of mermaidEntries) {
                const diagramEl = document.getElementById(`diagram-${id}`);
                if (!diagramEl) {
                    console.warn(`Mermaid diagram element not found: diagram-${id}`);
                    continue;
                }

                try {
                    const { svg } = await mermaid.render(`mermaid-svg-${id}`, code);
                    diagramEl.innerHTML = svg;

                    // Set up the viewer for the rendered Mermaid SVG
                    const container = document.getElementById(`graph-${id}`);
                    if (container) {
                        new MermaidGraphViewer(container, diagramEl, id);
                    }
                } catch (err) {
                    console.error(`Failed to render Mermaid diagram ${id}:`, err);
                    diagramEl.innerHTML = `<div class="diagram-error">Failed to render diagram: ${err.message}</div>`;
                }
            }
        }

        // ========== MERMAID GRAPH VIEWER CLASS ==========
        class MermaidGraphViewer {
            constructor(container, diagramEl, diagramId) {
                this.container = container;
                this.diagramEl = diagramEl;
                this.diagramId = diagramId;
                this.viewport = container.querySelector('.graph-viewport');
                this.wrapper = container.querySelector('.graph-wrapper');

                this.scale = 1;
                this.tx = 0;
                this.ty = 0;
                this.drag = false;
                this.sx = 0;
                this.sy = 0;

                this.bindEvents();
                setTimeout(() => this.fitView(), 100);
            }

            update() {
                this.wrapper.style.transform = `translate(${this.tx}px, ${this.ty}px) scale(${this.scale})`;
                const zoomLevel = this.container.querySelector('.zoom-level');
                if (zoomLevel) zoomLevel.textContent = `${Math.round(this.scale * 100)}%`;
            }

            fitView() {
                const svg = this.diagramEl.querySelector('svg');
                if (!svg) return;

                const vr = this.viewport.getBoundingClientRect();
                const sr = svg.getBoundingClientRect();
                const scaleX = (vr.width - 40) / sr.width;
                const scaleY = (vr.height - 40) / sr.height;
                this.scale = Math.min(scaleX, scaleY, 1.5);
                this.tx = (vr.width - sr.width * this.scale) / 2;
                this.ty = (vr.height - sr.height * this.scale) / 2;
                this.update();
            }

            resetView() {
                this.scale = 1;
                this.tx = 0;
                this.ty = 0;
                this.update();
            }

            zoomIn() { this.scale = Math.min(3, this.scale * 1.2); this.update(); }
            zoomOut() { this.scale = Math.max(0.2, this.scale / 1.2); this.update(); }

            downloadSVG() {
                const svg = this.diagramEl.querySelector('svg');
                if (!svg) return;
                const clone = svg.cloneNode(true);
                clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
                const svgText = new XMLSerializer().serializeToString(clone);
                const blob = new Blob([svgText], { type: 'image/svg+xml;charset=utf-8' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${this.diagramId}.svg`;
                a.click();
                URL.revokeObjectURL(url);
            }

            async downloadPNG() {
                const svg = this.diagramEl.querySelector('svg');
                if (!svg) return;
                const clone = svg.cloneNode(true);
                clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
                try {
                    const { blob, dpi } = await exportSvgToPng(clone, { dpi: 300, background: null });
                    const pngUrl = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = pngUrl;
                    a.download = `${this.diagramId}.png`;
                    a.click();
                    setTimeout(() => URL.revokeObjectURL(pngUrl), 2000);
                } catch (e) {
                    console.error('PNG export failed', e);
                }
            }

            openFullscreen() {
                const svg = this.diagramEl.querySelector('svg');
                if (!svg) return;
                const graphTitle = this.container.querySelector('.graph-title');
                const title = graphTitle ? graphTitle.textContent : 'Mermaid Diagram';
                FullscreenManager.open({ svg, title, onNodeClick: () => {} });
            }

            bindEvents() {
                this.container.querySelectorAll('.zoom-btn').forEach(btn => {
                    btn.addEventListener('click', () => {
                        const action = btn.dataset.action;
                        if (action === 'zoom-in') this.zoomIn();
                        if (action === 'zoom-out') this.zoomOut();
                    });
                });

                this.container.querySelectorAll('.graph-btn').forEach(btn => {
                    btn.addEventListener('click', () => {
                        const action = btn.dataset.action;
                        if (action === 'fit') this.fitView();
                        if (action === 'reset') this.resetView();
                        if (action === 'svg') this.downloadSVG();
                        if (action === 'png') this.downloadPNG();
                        if (action === 'fullscreen') this.openFullscreen();
                    });
                });

                this.viewport.addEventListener('wheel', (e) => {
                    e.preventDefault();
                    const ns = Math.max(0.2, Math.min(3, this.scale * (e.deltaY > 0 ? 0.9 : 1.1)));
                    const r = this.viewport.getBoundingClientRect();
                    const mx = e.clientX - r.left;
                    const my = e.clientY - r.top;
                    const sd = ns - this.scale;
                    this.tx -= (mx - this.tx) * (sd / this.scale);
                    this.ty -= (my - this.ty) * (sd / this.scale);
                    this.scale = ns;
                    this.update();
                }, { passive: false });

                this.viewport.addEventListener('mousedown', (e) => {
                    if (e.target.closest('g.node')) return;
                    this.drag = true;
                    this.sx = e.clientX - this.tx;
                    this.sy = e.clientY - this.ty;
                });

                window.addEventListener('mousemove', (e) => {
                    if (!this.drag) return;
                    this.tx = e.clientX - this.sx;
                    this.ty = e.clientY - this.sy;
                    this.update();
                });

                window.addEventListener('mouseup', () => { this.drag = false; });

                this.diagramEl.addEventListener('dblclick', (e) => { e.preventDefault(); this.fitView(); });
            }
        }

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initAllDiagrams);
        } else {
            initAllDiagrams();
        }

        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') document.getElementById('global-popover')?.classList.remove('visible');
        });

    </script>

    <script>
        // ========== SITE UX (SIDEBAR, THEME, TOC) ==========
        (() => {
            const $ = (s, e = document) => e.querySelector(s);
            const $$ = (s, e = document) => Array.from(e.querySelectorAll(s));

            // Mobile sidebar
            const menuBtn = $('.mobile-menu-btn');
            const sidebar = $('.sidebar');
            const overlay = $('.sidebar-overlay');

            const closeSidebar = () => {
                sidebar?.classList.remove('open');
                overlay?.classList.remove('active');
                document.body?.classList.remove('no-scroll');
            };

            const openSidebar = () => {
                sidebar?.classList.add('open');
                overlay?.classList.add('active');
                document.body?.classList.add('no-scroll');
            };

            if (menuBtn && sidebar && overlay) {
                menuBtn.addEventListener('click', () => {
                    sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
                });
                overlay.addEventListener('click', closeSidebar);
                window.addEventListener('keydown', (e) => {
                    if (e.key === 'Escape') closeSidebar();
                });
            }

            // Theme toggle
            const themeBtn = $('.theme-toggle');
            const themeLabel = $('.theme-label');
            const THEME_KEY = 'pmd_theme';

            const applyTheme = (t) => {
                if (t === 'dark') {
                    document.body.classList.add('theme-dark');
                    if (themeLabel) themeLabel.textContent = 'Dark';
                } else {
                    document.body.classList.remove('theme-dark');
                    if (themeLabel) themeLabel.textContent = 'Light';
                }
            };

            try {
                const saved = localStorage.getItem(THEME_KEY);
                if (saved) applyTheme(saved);
            } catch (_) { }

            if (themeBtn) {
                themeBtn.addEventListener('click', () => {
                    const isDark = document.body.classList.contains('theme-dark');
                    const next = isDark ? 'light' : 'dark';
                    applyTheme(next);
                    try { localStorage.setItem(THEME_KEY, next); } catch (_) { }
                });
            }

            // TOC active section highlight
            const tocEl = $('.toc');
            const content = $('.content');

            if (tocEl && content) {
                const links = $$('a[href^="#"]', tocEl);
                const byId = new Map();

                for (const a of links) {
                    const id = (a.getAttribute('href') || '').slice(1);
                    if (id) byId.set(id, a);
                }

                const headings = $$('h2[id], h3[id]', content).filter(h => byId.has(h.id));

                const clear = () => links.forEach(a => a.classList.remove('active'));
                const setActive = (id) => {
                    clear();
                    const a = byId.get(id);
                    if (a) a.classList.add('active');
                };

                if ('IntersectionObserver' in window && headings.length) {
                    let currentActive = null;

                    const updateActiveOnScroll = () => {
                        const scrollY = window.scrollY + 120;
                        let found = null;

                        for (let i = headings.length - 1; i >= 0; i--) {
                            const h = headings[i];
                            if (h.offsetTop <= scrollY) {
                                found = h.id;
                                break;
                            }
                        }

                        if (!found && headings.length > 0) {
                            found = headings[0].id;
                        }

                        if (found !== currentActive) {
                            currentActive = found;
                            setActive(found);
                        }
                    };

                    window.addEventListener('scroll', updateActiveOnScroll, { passive: true });
                    updateActiveOnScroll();
                }
            }

            // ========== SCROLL PROGRESS & BACK TO TOP ==========
            const scrollProgress = document.getElementById('scrollProgress');
            const backToTop = document.getElementById('backToTop');
            const header = document.querySelector('.header');

            let ticking = false;

            const updateScrollUI = () => {
                const scrollTop = window.scrollY;
                const docHeight = document.documentElement.scrollHeight - window.innerHeight;
                const scrollPercent = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;

                // Update scroll progress bar
                if (scrollProgress) {
                    scrollProgress.style.width = `${Math.min(100, scrollPercent)}%`;
                }

                // Show/hide back to top button
                if (backToTop) {
                    if (scrollTop > 400) {
                        backToTop.classList.add('visible');
                    } else {
                        backToTop.classList.remove('visible');
                    }
                }

                // Add shadow to header on scroll
                if (header) {
                    if (scrollTop > 10) {
                        header.classList.add('scrolled');
                    } else {
                        header.classList.remove('scrolled');
                    }
                }

                ticking = false;
            };

            window.addEventListener('scroll', () => {
                if (!ticking) {
                    requestAnimationFrame(updateScrollUI);
                    ticking = true;
                }
            }, { passive: true });

            // Back to top click handler
            if (backToTop) {
                backToTop.addEventListener('click', () => {
                    window.scrollTo({
                        top: 0,
                        behavior: 'smooth'
                    });
                });
            }

            // Initial call
            updateScrollUI();

            // ========== KEYBOARD NAVIGATION HINTS ==========
            document.addEventListener('keydown', (e) => {
                // Ctrl/Cmd + Home -> scroll to top
                if ((e.ctrlKey || e.metaKey) && e.key === 'Home') {
                    e.preventDefault();
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
                // Ctrl/Cmd + End -> scroll to bottom
                if ((e.ctrlKey || e.metaKey) && e.key === 'End') {
                    e.preventDefault();
                    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                }
            });

        })();

                /* Search */
        class DocSearchEngine {
            constructor(docs) {
                this.docs = docs;
                this.docById = new Map(docs.map(d => [d.id, d]));
                this.index = new Map(); // token -> Map(docId -> tf)
                this.df = new Map();    // token -> document frequency
                this.idf = new Map();   // token -> inverse document frequency
                this.docLen = new Map();// docId -> length (tokens)
                this.vocab = [];
                this.trigram = new Map(); // trigram -> Set(token)
                this.avgLen = 1;
                this._build();
            }

            _normalizeText(t) {
                return (t || '')
                    .toLowerCase()
                    .normalize('NFKD')
                    .replace(/[\u0300-\u036f]/g, '')
                    .replace(/['’`]/g, '')
                    .replace(/[^a-z0-9]+/g, ' ')
                    .trim();
            }

            _tokenize(t) {
                const n = this._normalizeText(t);
                if (!n) return [];
                const tokens = n.split(/\s+/).filter(w => w.length >= 2);
                return tokens;
            }

            _addToken(token, docId) {
                let posting = this.index.get(token);
                if (!posting) { posting = new Map(); this.index.set(token, posting); }
                posting.set(docId, (posting.get(docId) || 0) + 1);
            }

            _buildTrigramsForToken(token) {
                const padded = `  ${token}  `;
                for (let i = 0; i < padded.length - 2; i++) {
                    const tri = padded.slice(i, i + 3);
                    let set = this.trigram.get(tri);
                    if (!set) { set = new Set(); this.trigram.set(tri, set); }
                    set.add(token);
                }
            }

            _build() {
                let totalLen = 0;

                for (const d of this.docs) {
                    const id = d.id;
                    const all = `${d.title || ''}\n${d.section || ''}\n${d.content || ''}`;
                    const tokens = this._tokenize(all);

                    this.docLen.set(id, tokens.length);
                    totalLen += tokens.length;

                    const seen = new Set();
                    for (const tok of tokens) {
                        this._addToken(tok, id);
                        if (!seen.has(tok)) {
                            seen.add(tok);
                            this.df.set(tok, (this.df.get(tok) || 0) + 1);
                        }
                    }
                }

                this.avgLen = Math.max(1, totalLen / Math.max(1, this.docs.length));

                // Build vocab + trigram index for fuzzy expansion
                this.vocab = Array.from(this.index.keys());
                for (const tok of this.vocab) this._buildTrigramsForToken(tok);

                // Precompute IDF (BM25-like)
                const N = Math.max(1, this.docs.length);
                for (const [tok, df] of this.df.entries()) {
                    const idf = Math.log(1 + (N - df + 0.5) / (df + 0.5));
                    this.idf.set(tok, idf);
                }
            }

            _levenshteinMax2(a, b) {
                // Early-exit Levenshtein (max 2); tuned for short query tokens
                if (a === b) return 0;
                const la = a.length, lb = b.length;
                const diff = Math.abs(la - lb);
                if (diff > 2) return 3;

                // DP rows
                let prev = new Array(lb + 1);
                let curr = new Array(lb + 1);
                for (let j = 0; j <= lb; j++) prev[j] = j;

                for (let i = 1; i <= la; i++) {
                    curr[0] = i;
                    let rowMin = curr[0];
                    const ca = a.charCodeAt(i - 1);
                    for (let j = 1; j <= lb; j++) {
                        const cost = ca === b.charCodeAt(j - 1) ? 0 : 1;
                        const v = Math.min(
                            prev[j] + 1,
                            curr[j - 1] + 1,
                            prev[j - 1] + cost
                        );
                        curr[j] = v;
                        if (v < rowMin) rowMin = v;
                    }
                    if (rowMin > 2) return 3;
                    [prev, curr] = [curr, prev];
                }
                return prev[lb];
            }

            _expandToken(q) {
                const token = this._normalizeText(q);
                if (!token) return [];

                // Exact
                if (this.index.has(token)) return [token];

                // Prefix candidates
                const pref = [];
                const maxPref = 40;
                for (const v of this.vocab) {
                    if (v.startsWith(token)) {
                        pref.push(v);
                        if (pref.length >= maxPref) break;
                    }
                }
                if (pref.length) return pref;

                // Fuzzy (trigram intersection + Levenshtein <=2)
                if (token.length < 4) return [];
                const padded = `  ${token}  `;
                const candidates = new Map(); // token -> overlap
                for (let i = 0; i < padded.length - 2; i++) {
                    const tri = padded.slice(i, i + 3);
                    const set = this.trigram.get(tri);
                    if (!set) continue;
                    for (const t of set) candidates.set(t, (candidates.get(t) || 0) + 1);
                }

                // Take top overlaps then filter by edit distance
                const ranked = Array.from(candidates.entries())
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 80)
                    .map(([t]) => t);

                const fuzzy = [];
                for (const t of ranked) {
                    if (Math.abs(t.length - token.length) > 2) continue;
                    const dist = this._levenshteinMax2(token, t);
                    if (dist <= 2) fuzzy.push(t);
                    if (fuzzy.length >= 20) break;
                }
                return fuzzy;
            }

            search(query, { limit = 30 } = {}) {
                const raw = (query || '').trim();
                if (!raw) return [];

                const parts = [];
                const re = /"([^"]+)"|(\S+)/g;
                let m;
                while ((m = re.exec(raw)) !== null) parts.push(m[1] || m[2]);

                const phrases = parts.filter(p => p.includes(' ') && !p.startsWith('type:') && !p.startsWith('section:'));
                const tokens = parts.filter(p => !p.includes(' ') && !p.startsWith('type:') && !p.startsWith('section:'));

                // Optional filters: type:graph / type:section / type:page, section:<text>
                const typeFilter = (parts.find(p => p.startsWith('type:')) || '').slice(5).toLowerCase();
                const sectionFilter = (parts.find(p => p.startsWith('section:')) || '').slice(8).toLowerCase();

                const scores = new Map();
                const matchedTokens = new Map(); // docId -> Set(tokens)

                for (const qt of tokens) {
                    const expanded = this._expandToken(qt);
                    for (const tok of expanded) {
                        const posting = this.index.get(tok);
                        if (!posting) continue;

                        const idf = this.idf.get(tok) || 0.1;
                        for (const [docId, tf] of posting.entries()) {
                            const d = this.docById.get(docId);
                            if (!d) continue;

                            if (typeFilter && String(d.type || '').toLowerCase() !== typeFilter) continue;
                            if (sectionFilter && !String(d.section || '').toLowerCase().includes(sectionFilter)) continue;

                            const len = this.docLen.get(docId) || 1;
                            const tfNorm = tf / (0.5 + 0.5 * (len / this.avgLen));
                            const base = (scores.get(docId) || 0) + (tfNorm * idf);
                            scores.set(docId, base);

                            let s = matchedTokens.get(docId);
                            if (!s) { s = new Set(); matchedTokens.set(docId, s); }
                            s.add(qt);
                        }
                    }
                }

                // Phrase filtering + boost
                const qLower = this._normalizeText(raw);
                const results = [];
                for (const [docId, score0] of scores.entries()) {
                    const d = this.docById.get(docId);
                    if (!d) continue;

                    const normTitle = this._normalizeText(d.title || '');
                    const normContent = this._normalizeText(d.content || '');

                    let score = score0;

                    // Title boost
                    if (qLower && normTitle.includes(qLower)) score *= 2.0;
                    else {
                        // partial boost
                        for (const qt of tokens) {
                            const nt = this._normalizeText(qt);
                            if (nt && normTitle.includes(nt)) score *= 1.25;
                        }
                    }

                    // Phrase requirement: every phrase must appear in title or content
                    let ok = true;
                    for (const ph of phrases) {
                        const np = this._normalizeText(ph);
                        if (!np) continue;
                        if (!normTitle.includes(np) && !normContent.includes(np)) { ok = false; break; }
                        score *= 1.15;
                    }
                    if (!ok) continue;

                    results.push({ doc: d, score, matched: Array.from(matchedTokens.get(docId) || []) });
                }

                results.sort((a, b) => b.score - a.score);
                return results.slice(0, limit);
            }
        }

        function slugify(text) {
            return (text || '')
                .toLowerCase()
                .trim()
                .replace(/[\s]+/g, '-')
                .replace(/[^a-z0-9\-]/g, '')
                .replace(/\-+/g, '-')
                .replace(/^\-+|\-+$/g, '');
        }

        function extractDotIndexText(dot) {
            if (!dot) return '';
            const out = new Set();

            // Node/edge labels
            const re = /label\s*=\s*"((?:\\.|[^"\\])*)"/g;
            let m;
            while ((m = re.exec(dot)) !== null) {
                const s = m[1].replace(/\\n/g, ' ').replace(/\\\"/g, '"').trim();
                if (s) out.add(s);
            }

            // Node IDs in quotes
            const reId = /"([^"]+)"\s*\[/g;
            while ((m = reId.exec(dot)) !== null) {
                const s = m[1].trim();
                if (s) out.add(s);
            }

            return Array.from(out).join(' · ');
        }

        function buildSearchDocuments() {
            const docs = [];
            const article = document.querySelector('article.content') || document.querySelector('.content') || document.body;

            const pageTitle = document.querySelector('h1')?.textContent?.trim() || document.title || 'Documentation';
            const pagePath = location.pathname.split('/').pop() || 'index.html';

            // Whole-page entry
            docs.push({
                id: `page:${pagePath}`,
                type: 'page',
                title: pageTitle,
                section: 'This page',
                path: `./${pagePath}`,
                content: (article?.innerText || '').trim()
            });

            // Section entries (h2/h3)
            const headings = Array.from(article.querySelectorAll('h2, h3'));
            headings.forEach((h, idx) => {
                const level = Number(h.tagName.substring(1)) || 2;
                const title = h.textContent.trim();
                if (!title) return;

                if (!h.id) h.id = `${slugify(title) || 'section'}-${idx + 1}`;
                const id = `sec:${pagePath}#${h.id}`;

                const parts = [];
                let el = h.nextElementSibling;
                while (el) {
                    const isHeading = /H[1-6]/.test(el.tagName);
                    if (isHeading) {
                        const nextLevel = Number(el.tagName.substring(1)) || 6;
                        if (nextLevel <= level) break;
                    }
                    // exclude scripts/styles
                    if (el.tagName !== 'SCRIPT' && el.tagName !== 'STYLE') parts.push(el.innerText || el.textContent || '');
                    el = el.nextElementSibling;
                }

                const content = parts.join('\n').trim();
                docs.push({
                    id,
                    type: 'section',
                    title,
                    section: pageTitle,
                    path: `./${pagePath}#${h.id}`,
                    content
                });
            });

            // Graph entries (node labels + edge labels + ids)
            document.querySelectorAll('.mermaid-graph-container').forEach((container) => {
                const title = container.querySelector('.graph-title')?.textContent?.trim() || 'Graph';
                const graphId = container.id || '';
                const key = graphId.startsWith('graph-') ? graphId.slice(6) : graphId;
                const dot = (typeof dotDiagrams !== 'undefined' && dotDiagrams[key]) ? dotDiagrams[key] : '';

                const graphText = extractDotIndexText(dot);
                if (!graphText.trim()) return;

                docs.push({
                    id: `graph:${pagePath}#${graphId || key}`,
                    type: 'graph',
                    title,
                    section: pageTitle,
                    path: graphId ? `./${pagePath}#${graphId}` : `./${pagePath}`,
                    content: graphText
                });
            });

            // Navigation pages from sidebar links
            document.querySelectorAll('.nav-link[href]').forEach((a) => {
                const t = (a.textContent || '').trim();
                const href = a.getAttribute('href');
                if (!t || !href) return;
                docs.push({
                    id: `nav:${href}`,
                    type: 'page',
                    title: t,
                    section: 'Pages',
                    path: href,
                    content: `Navigate to ${t}`
                });
            });

            return docs;
        }

        // ---- Cross-page search helpers (site-wide indexing) ----
        async function mapLimit(items, limit, fn) {
            const results = new Array(items.length);
            let idx = 0;

            const workers = new Array(Math.min(limit, items.length)).fill(0).map(async () => {
                while (true) {
                    const i = idx++;
                    if (i >= items.length) break;
                    results[i] = await fn(items[i], i, items.length);
                }
            });

            await Promise.all(workers);
            return results;
        }

        function extractDocsFromHtml(htmlText, href) {
            const docs = [];
            try {
                const parser = new DOMParser();
                const doc = parser.parseFromString(htmlText, 'text/html');

                const pageTitle = doc.querySelector('h1')?.textContent?.trim() || doc.title || (href || 'Page');
                const pagePath = (href || '').split('#')[0].split('/').pop() || href || 'page';

                const article = doc.querySelector('article.content') || doc.querySelector('.content') || doc.body;
                const pageText = (article?.innerText || '').trim();

                docs.push({
                    id: `page:${pagePath}`,
                    type: 'page',
                    title: pageTitle,
                    section: 'Pages',
                    path: href,
                    content: pageText
                });

                // Sections (h2/h3 with IDs)
                const headings = Array.from(doc.querySelectorAll('h2[id], h3[id]'));
                headings.forEach((h) => {
                    const title = (h.textContent || '').trim();
                    if (!title) return;

                    const level = Number(h.tagName.substring(1)) || 6;
                    const parts = [];
                    let el = h.nextElementSibling;
                    while (el) {
                        if (/^H[1-6]$/.test(el.tagName)) {
                            const nextLevel = Number(el.tagName.substring(1)) || 6;
                            if (nextLevel <= level) break;
                        }
                        if (el.tagName !== 'SCRIPT' && el.tagName !== 'STYLE') {
                            parts.push(el.innerText || el.textContent || '');
                        }
                        el = el.nextElementSibling;
                    }

                    const content = parts.join('\n').trim();
                    const id = `section:${pagePath}#${h.id}`;

                    docs.push({
                        id,
                        type: 'section',
                        title,
                        section: pageTitle,
                        path: `${href}#${h.id}`,
                        content
                    });
                });

                // Best-effort DOT indexing if the page embeds dotDiagrams (Graphviz).
                try {
                    const m = htmlText.match(/const\s+dotDiagrams\s*=\s*\{([\s\S]*?)\n\s*\};/);
                    if (m && m[1]) {
                        const body = m[1];
                        const re = /"([^"]+)"\s*:\s*`([\s\S]*?)`\s*,?/g;
                        let mm;
                        while ((mm = re.exec(body)) !== null) {
                            const key = mm[1];
                            const dot = mm[2] || '';
                            const graphText = extractDotIndexText(dot);
                            if (!graphText.trim()) continue;
                            docs.push({
                                id: `graph:${pagePath}:${key}`,
                                type: 'graph',
                                title: `Graph: ${key}`,
                                section: pageTitle,
                                path: href,
                                content: graphText
                            });
                        }
                    }
                } catch (e) { /* ignore */ }

            } catch (e) {
                return [];
            }
            return docs;
        }


        function makeSnippet(text, query, maxLen = 180) {
            if (!text) return '';
            const t = String(text).replace(/\s+/g, ' ').trim();
            if (!t) return '';

            const q = (query || '').trim();
            if (!q) return t.slice(0, maxLen);

            const nText = t.toLowerCase();
            const nQuery = q.toLowerCase().replace(/['’`]/g, '');

            let idx = nText.indexOf(nQuery);
            if (idx < 0) {
                // try token-based
                const tokens = nQuery.split(/\s+/).filter(Boolean);
                for (const tok of tokens) {
                    const j = nText.indexOf(tok);
                    if (j >= 0) { idx = j; break; }
                }
            }
            if (idx < 0) idx = 0;

            const start = Math.max(0, idx - Math.floor(maxLen / 3));
            const end = Math.min(t.length, start + maxLen);
            const prefix = start > 0 ? '…' : '';
            const suffix = end < t.length ? '…' : '';
            return prefix + t.slice(start, end) + suffix;
        }

        function highlightHtml(text, query) {
            const div = document.createElement('div');
            div.textContent = text || '';
            let safe = div.innerHTML;

            const q = (query || '').trim();
            if (!q) return safe;

            // Highlight up to first 8 distinct tokens
            const tokens = Array.from(new Set(q.split(/\s+/).filter(w => w.length >= 2))).slice(0, 8);
            for (const tok of tokens) {
                const re = new RegExp(`(${tok.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&')})`, 'ig');
                safe = safe.replace(re, '<mark>$1</mark>');
            }
            return safe;
        }

        class Search {
            constructor() {
                this.selectedIndex = -1;
                this.docs = buildSearchDocuments();
                this.engine = new DocSearchEngine(this.docs);
                this.createModal();
                this.bindEvents();
                this.bootstrapCrossPageIndex();
            }

            createModal() {
                const html = `<div class="search-modal" id="search-modal" aria-hidden="true">
            <div class="search-modal-content" role="dialog" aria-modal="true" aria-label="Search">
                <div class="search-modal-header">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                    <input type="text" class="search-modal-input" id="search-input" name="search-query" placeholder="Search documentation... (use quotes for exact phrase)" autocomplete="off" spellcheck="false" aria-label="Search query">
                    <kbd class="search-shortcut">ESC</kbd>
                </div>
                <div class="search-results" id="search-results"><div class="search-no-results">Type to search…</div></div>
                <div class="search-footer">
                    <span><kbd>↑</kbd><kbd>↓</kbd> Navigate</span>
                    <span><kbd>↵</kbd> Open</span>
                    <span><kbd>ESC</kbd> Close</span>
                </div>
            </div>
        </div>`;
                document.body.insertAdjacentHTML('beforeend', html);
                this.modal = document.getElementById('search-modal');
                this.input = document.getElementById('search-input');
                this.resultsContainer = document.getElementById('search-results');

                // Sidebar search input (kept for layout, opens modal)
                document.getElementById('sidebar-search')?.addEventListener('click', (e) => { e.preventDefault(); this.open(); });
            }

            bindEvents() {
                document.addEventListener('keydown', (e) => {
                    // Open: Ctrl/Cmd + K
                    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
                        e.preventDefault();
                        this.open();
                        return;
                    }

                    if (!this.modal.classList.contains('active')) return;

                    if (e.key === 'Escape') { e.preventDefault(); this.close(); return; }
                    if (e.key === 'ArrowDown') { e.preventDefault(); this.navigate(1); return; }
                    if (e.key === 'ArrowUp') { e.preventDefault(); this.navigate(-1); return; }
                    if (e.key === 'Enter') { e.preventDefault(); this.selectCurrent(); return; }
                });

                this.modal.addEventListener('click', (e) => { if (e.target === this.modal) this.close(); });

                this.input.addEventListener('input', () => {
                    this.selectedIndex = -1;
                    this.search(this.input.value);
                });
            }

            navigate(dir) {
                const items = Array.from(this.resultsContainer.querySelectorAll('.search-result-item'));
                if (!items.length) return;
                this.selectedIndex = Math.max(0, Math.min(items.length - 1, this.selectedIndex + dir));
                items.forEach((el, i) => el.classList.toggle('selected', i === this.selectedIndex));
                items[this.selectedIndex]?.scrollIntoView({ block: 'nearest' });
            }

            selectCurrent() {
                const items = Array.from(this.resultsContainer.querySelectorAll('.search-result-item'));
                if (!items.length) return;
                const idx = this.selectedIndex >= 0 ? this.selectedIndex : 0;
                const item = items[idx];
                const path = item?.dataset?.path;
                if (!path) return;

                this.close();

                // In-page navigation: preserve smooth scroll and flash target
                if (path.includes('#') && path.split('#')[0].endsWith(location.pathname.split('/').pop() || '')) {
                    const id = path.split('#')[1];
                    const el = document.getElementById(id);
                    if (el) {
                        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        el.classList.add('search-target-flash');
                        setTimeout(() => el.classList.remove('search-target-flash'), 900);
                        return;
                    }
                }

                window.location.href = path;
            }

            render(results, query) {
                if (!query.trim()) {
                    this.resultsContainer.innerHTML = `<div class="search-no-results">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                        </svg>
                        <div>Type to search across all documentation...</div>
                        <div style="margin-top: 8px; font-size: 12px;">
                            Try: <kbd style="padding: 2px 6px; background: var(--color-bg-tertiary); border-radius: 4px;">"exact phrase"</kbd>
                            <kbd style="padding: 2px 6px; background: var(--color-bg-tertiary); border-radius: 4px;">type:graph</kbd>
                            <kbd style="padding: 2px 6px; background: var(--color-bg-tertiary); border-radius: 4px;">section:patterns</kbd>
                        </div>
                    </div>`;
                    return;
                }

                if (!results.length) {
                    this.resultsContainer.innerHTML = `<div class="search-no-results">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
                        </svg>
                        <div>No results for "<strong>${this.escapeHtml(query)}</strong>"</div>
                        <div style="margin-top: 8px; font-size: 12px;">Try different keywords or check spelling</div>
                    </div>`;
                    return;
                }

                const html = results.map((r, i) => {
                    const d = r.doc;
                    const type = String(d.type || 'result').toLowerCase();
                    const badge = type.toUpperCase();
                    const badgeClass = type === 'page' ? 'page' : (type === 'graph' ? 'graph' : 'section');

                    // Generate a relevant snippet with context around matched terms
                    const snippet = makeSnippet(d.content || '', query, 180);

                    // Show path info for cross-page results
                    const isExternalPage = !d.path.includes(location.pathname.split('/').pop() || '');
                    const pathInfo = isExternalPage && d.section ? d.section : '';

                    return `<div class="search-result-item ${i === 0 ? 'selected' : ''}" data-index="${i}" data-path="${this.escapeHtml(d.path)}">
                        <div class="search-result-header">
                            <div class="search-result-title">${highlightHtml(d.title || '', query)}</div>
                            <span class="search-result-badge ${badgeClass}">${badge}</span>
                        </div>
                        ${pathInfo ? `<div class="search-result-section">in ${this.escapeHtml(pathInfo)}</div>` : ''}
                        ${snippet ? `<div class="search-result-snippet">${highlightHtml(snippet, query)}</div>` : ''}
                    </div>`;
                }).join('');

                this.resultsContainer.innerHTML = html;
                this.selectedIndex = 0;

                this.resultsContainer.querySelectorAll('.search-result-item').forEach(item => {
                    item.addEventListener('click', () => {
                        this.selectedIndex = Number(item.dataset.index || 0);
                        this.selectCurrent();
                    });
                });
            }

            search(query) {
                const results = this.engine.search(query, { limit: 30 });
                this.render(results, query);
            }

            escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text || '';
                return div.innerHTML;
            }

            open() {
                this.modal.classList.add('active');
                this.modal.setAttribute('aria-hidden', 'false');
                this.input.focus();
                this.input.select();
                this.search(this.input.value || '');
            }

            close() {
                this.modal.classList.remove('active');
                this.modal.setAttribute('aria-hidden', 'true');
                this.input.blur();
            }

            async bootstrapCrossPageIndex() {
                // Load COMPREHENSIVE pre-built search index for full-text cross-page search
                // This index contains ALL content from ALL pages - no truncation
                try {
                    const protocol = (location && location.protocol) ? location.protocol : '';
                    if (protocol === 'file:') {
                        return;
                    }

                    // Load the comprehensive search index
                    const indexUrl = new URL('./search-index.json', location.href);
                    const res = await fetch(indexUrl.toString(), { credentials: 'same-origin', cache: 'default' });

                    if (!res.ok) {
                        return;
                    }

                    const searchIndex = await res.json();

                    if (!Array.isArray(searchIndex) || !searchIndex.length) {
                        return;
                    }

                    // Convert FULL search index to docs format
                    // This creates a comprehensive searchable document collection
                    const extraDocs = [];
                    let totalContentChars = 0;
                    let totalWords = 0;

                    for (const entry of searchIndex) {
                        // Combine ALL content sources for comprehensive page-level search
                        const pageContent = [
                            entry.content || '',           // Full page content (untruncated)
                            entry.keywords || '',          // Extracted technical keywords
                            entry.terms || '',             // All unique terms for exact match
                            // All heading texts and their full content
                            (entry.headings || []).map(h =>
                                `${h.text} ${h.content || ''} ${h.keywords || ''}`
                            ).join(' ')
                        ].join(' ');

                        totalContentChars += pageContent.length;
                        totalWords += entry.wordCount || 0;

                        // Add page entry with COMPLETE content
                        extraDocs.push({
                            id: `page-${entry.href}`,
                            title: entry.title,
                            section: entry.section,
                            path: entry.href,
                            content: pageContent,
                            type: 'page',
                            headingCount: entry.headingCount || 0,
                            wordCount: entry.wordCount || 0
                        });

                        // Add EACH section as a separately searchable document
                        // Allows users to find and navigate to specific sections
                        if (entry.headings && Array.isArray(entry.headings)) {
                            for (const h of entry.headings) {
                                // Combine section's full content with its keywords
                                const sectionContent = [
                                    h.content || '',       // Full section content
                                    h.keywords || '',      // Section-specific keywords
                                    h.text || ''           // Heading text
                                ].join(' ');

                                extraDocs.push({
                                    id: `section-${entry.href}-${h.slug}`,
                                    title: h.text,
                                    section: entry.title,  // Parent page title
                                    path: `${entry.href}#${h.slug}`,
                                    content: sectionContent,
                                    level: h.level || 2,
                                    type: 'section',
                                    parentPage: entry.href
                                });
                            }
                        }
                    }

                    if (extraDocs.length) {
                        // Replace current docs with comprehensive cross-page index
                        // but keep current page's detailed docs for best local search
                        const byId = new Map(this.docs.map(d => [d.id, d]));
                        for (const d of extraDocs) byId.set(d.id, d);
                        this.docs = Array.from(byId.values());

                        // Rebuild the search engine with full content
                        this.engine = new DocSearchEngine(this.docs);

                        // Re-run current search if modal is open
                        if (this.modal && this.modal.classList.contains('active')) {
                            const q = (this.input?.value || '').trim();
                            if (q) this.search(q);
                        }
                    }

                    // Log comprehensive index stats
                    const pagesIndexed = searchIndex.length;
                    const sectionsIndexed = extraDocs.length - pagesIndexed;
                    const sizeKB = (totalContentChars / 1024).toFixed(0);
                    console.log(`[Search] Loaded comprehensive index: ${extraDocs.length} docs, ${totalWords.toLocaleString()} words, ${sizeKB} KB`);
                } catch (e) {
                    console.error('[Search] Failed to load index:', e);
                }
            }

        }

        /* Image Viewer */
        class ImageViewer {
            constructor() {
                this.scale = 1;
                this.translateX = 0;
                this.translateY = 0;
                this.isDragging = false;
                this.startX = 0;
                this.startY = 0;
                this.currentElement = null;
                this.createOverlay();
                this.bindEvents();
            }

            createOverlay() {
                const html = `
            <div class="image-viewer-overlay" id="image-viewer" role="dialog" aria-modal="true" aria-label="Image viewer">
                <button class="image-viewer-close" aria-label="Close image viewer">&times;</button>
                <div class="image-viewer-container" id="image-viewer-container"></div>
                <div class="image-viewer-controls">
                    <button class="image-viewer-btn" id="zoom-in" aria-label="Zoom in">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
                        Zoom In
                    </button>
                    <button class="image-viewer-btn" id="zoom-out" aria-label="Zoom out">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
                        Zoom Out
                    </button>
                    <button class="image-viewer-btn" id="zoom-reset" aria-label="Reset zoom">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
                        Reset
                    </button>
                    <button class="image-viewer-btn" id="download-png" aria-label="Download as PNG">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                        Download PNG
                    </button>
                </div>
            </div>`;
                document.body.insertAdjacentHTML('beforeend', html);
                this.overlay = document.getElementById('image-viewer');
                this.container = document.getElementById('image-viewer-container');
            }

            bindEvents() {
                document.querySelectorAll('.content img, .content svg, .viewable-image').forEach(el => {
                    el.style.cursor = 'zoom-in';
                    el.addEventListener('click', e => {
                        e.preventDefault();
                        this.open(el);
                    });
                });

                this.overlay.querySelector('.image-viewer-close').addEventListener('click', () => this.close());
                this.overlay.addEventListener('click', e => { if (e.target === this.overlay) this.close(); });
                document.getElementById('zoom-in').addEventListener('click', () => this.zoom(0.25));
                document.getElementById('zoom-out').addEventListener('click', () => this.zoom(-0.25));
                document.getElementById('zoom-reset').addEventListener('click', () => this.reset());
                document.getElementById('download-png').addEventListener('click', () => this.downloadPNG());

                this.container.addEventListener('wheel', e => {
                    e.preventDefault();
                    this.zoom(e.deltaY > 0 ? -0.1 : 0.1);
                });

                this.container.addEventListener('mousedown', e => {
                    this.isDragging = true;
                    this.startX = e.clientX - this.translateX;
                    this.startY = e.clientY - this.translateY;
                    this.container.style.cursor = 'grabbing';
                });

                document.addEventListener('mousemove', e => {
                    if (!this.isDragging) return;
                    this.translateX = e.clientX - this.startX;
                    this.translateY = e.clientY - this.startY;
                    this.updateTransform();
                });

                document.addEventListener('mouseup', () => {
                    this.isDragging = false;
                    this.container.style.cursor = 'grab';
                });

                document.addEventListener('keydown', e => {
                    if (!this.overlay.classList.contains('active')) return;
                    if (e.key === 'Escape') this.close();
                    if (e.key === '+' || e.key === '=') this.zoom(0.25);
                    if (e.key === '-') this.zoom(-0.25);
                    if (e.key === '0') this.reset();
                });
            }

            open(element) {
                this.currentElement = element;
                this.reset();

                if (element.tagName === 'IMG') {
                    const img = document.createElement('img');
                    img.src = element.src;
                    img.alt = element.alt || 'Image';
                    // Let CSS handle sizing - don't override with inline styles
                    this.container.innerHTML = '';
                    this.container.appendChild(img);
                } else if (element.tagName === 'svg' || element.tagName === 'SVG') {
                    const clone = element.cloneNode(true);
                    // Reset any inline dimensions from the original
                    clone.removeAttribute('width');
                    clone.removeAttribute('height');
                    clone.style.width = '';
                    clone.style.height = '';
                    this.container.innerHTML = '';
                    this.container.appendChild(clone);
                }

                this.overlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            }

            close() {
                this.overlay.classList.remove('active');
                document.body.style.overflow = '';
            }

            zoom(delta) {
                // Allow much wider zoom range for detailed images (0.1x to 20x)
                this.scale = Math.max(0.1, Math.min(20, this.scale + delta));
                this.updateTransform();
            }

            reset() {
                this.scale = 1;
                this.translateX = 0;
                this.translateY = 0;
                this.updateTransform();
            }

            updateTransform() {
                const el = this.container.querySelector('img, svg');
                if (el) el.style.transform = `translate(${this.translateX}px, ${this.translateY}px) scale(${this.scale})`;
            }

            async downloadPNG() {
                const el = this.container.querySelector('img, svg');
                if (!el) return;

                if (el.tagName === 'IMG') {
                    // For regular images, download the original file directly
                    // This avoids canvas tainting issues with local files
                    try {
                        const response = await fetch(el.src);
                        const blob = await response.blob();
                        const url = URL.createObjectURL(blob);
                        const link = document.createElement('a');
                        link.href = url;
                        // Extract filename from src or use default
                        const srcParts = el.src.split('/');
                        const originalName = srcParts[srcParts.length - 1].split('?')[0] || 'image';
                        link.download = originalName.includes('.') ? originalName : originalName + '.png';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        URL.revokeObjectURL(url);
                    } catch (err) {
                        // Fallback for file:// protocol or CORS issues - open image source
                        console.warn('Image download failed, opening source:', err);
                        const link = document.createElement('a');
                        link.href = el.src;
                        link.download = 'image.png';
                        link.target = '_blank';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    }
                } else {
                    // For SVG - render to PNG with TRANSPARENT background
                    try {
                        const svgData = new XMLSerializer().serializeToString(el);
                        const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
                        const url = URL.createObjectURL(svgBlob);

                        const img = new Image();
                        img.src = url;
                        await new Promise((resolve, reject) => {
                            img.onload = resolve;
                            img.onerror = reject;
                        });

                        const width = el.viewBox?.baseVal?.width || el.getBoundingClientRect().width || 800;
                        const height = el.viewBox?.baseVal?.height || el.getBoundingClientRect().height || 600;

                        const canvas = document.createElement('canvas');
                        canvas.width = width * 2;  // 2x for better quality
                        canvas.height = height * 2;
                        const ctx = canvas.getContext('2d');
                        // TRANSPARENT background - don't fill with white
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                        ctx.scale(2, 2);
                        ctx.drawImage(img, 0, 0, width, height);
                        URL.revokeObjectURL(url);

                        const link = document.createElement('a');
                        link.download = 'pmdco-diagram.png';
                        link.href = canvas.toDataURL('image/png');
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    } catch (err) {
                        // Fallback: download as SVG
                        console.warn('PNG conversion failed, downloading as SVG:', err);
                        const svgData = new XMLSerializer().serializeToString(el);
                        const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
                        const url = URL.createObjectURL(svgBlob);
                        const link = document.createElement('a');
                        link.href = url;
                        link.download = 'pmdco-diagram.svg';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        URL.revokeObjectURL(url);
                    }
                }
            }
        }

        // Initialize Search and ImageViewer
        new Search();
        new ImageViewer();

        // ========== EXTERNAL LINKS HANDLER ==========
        // Make all external links open in new tabs for better UX
        (function() {
            const currentHost = window.location.hostname;
            document.querySelectorAll('a[href]').forEach(link => {
                const href = link.getAttribute('href');
                if (!href) return;

                // Check if link is external (starts with http/https and different domain)
                if (href.startsWith('http://') || href.startsWith('https://')) {
                    try {
                        const url = new URL(href);
                        if (url.hostname !== currentHost) {
                            link.setAttribute('target', '_blank');
                            link.setAttribute('rel', 'noopener noreferrer');
                        }
                    } catch (e) {
                        // Invalid URL, skip
                    }
                }
            });
        })();

        // ========== ONTOLOGY TREE MANAGER ==========
        class OntologyTreeManager {
            constructor() {
                this.tooltip = null;
                this.init();
            }

            init() {
                if (!document.querySelector('.ontology-tree-container')) return;
                this.createTooltip();
                this.bindEvents();
            }

            createTooltip() {
                this.tooltip = document.createElement('div');
                this.tooltip.className = 'tree-tooltip';
                document.body.appendChild(this.tooltip);
            }

            bindEvents() {
                document.querySelectorAll('.tree-toggle').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        this.toggleNode(btn);
                    });
                });

                document.querySelectorAll('.tree-expand-all').forEach(btn => {
                    btn.addEventListener('click', () => {
                        const container = btn.closest('.ontology-tree-container');
                        this.expandAll(container);
                    });
                });

                document.querySelectorAll('.tree-collapse-all').forEach(btn => {
                    btn.addEventListener('click', () => {
                        const container = btn.closest('.ontology-tree-container');
                        this.collapseAll(container);
                    });
                });

                document.querySelectorAll('.tree-search').forEach(input => {
                    input.addEventListener('input', (e) => {
                        const container = input.closest('.ontology-tree-container');
                        this.filterTree(container, e.target.value);
                    });
                });

                document.querySelectorAll('.tree-node.has-definition').forEach(node => {
                    node.addEventListener('mouseenter', (e) => this.showTooltip(e, node));
                    node.addEventListener('mouseleave', () => this.hideTooltip());
                    node.addEventListener('mousemove', (e) => this.moveTooltip(e));
                });
            }

            toggleNode(btn) {
                const li = btn.closest('li');
                const children = li.querySelector(':scope > .tree-children');
                if (!children) return;

                const isCollapsed = btn.classList.contains('collapsed');
                if (isCollapsed) {
                    btn.classList.remove('collapsed');
                    btn.classList.add('expanded');
                    children.classList.remove('collapsed');
                    children.style.maxHeight = children.scrollHeight + 'px';
                } else {
                    btn.classList.remove('expanded');
                    btn.classList.add('collapsed');
                    children.classList.add('collapsed');
                }
            }

            expandAll(container) {
                container.querySelectorAll('.tree-toggle.collapsed').forEach(btn => {
                    btn.classList.remove('collapsed');
                    btn.classList.add('expanded');
                });
                container.querySelectorAll('.tree-children').forEach(children => {
                    children.classList.remove('collapsed');
                    children.style.maxHeight = 'none';
                });
            }

            collapseAll(container) {
                container.querySelectorAll('.tree-toggle.expanded').forEach(btn => {
                    btn.classList.remove('expanded');
                    btn.classList.add('collapsed');
                });
                container.querySelectorAll('.tree-children').forEach(children => {
                    children.classList.add('collapsed');
                });
            }

            filterTree(container, query) {
                const tree = container.querySelector('.ontology-tree');
                const nodes = tree.querySelectorAll('.tree-node');
                const q = query.toLowerCase().trim();

                if (!q) {
                    nodes.forEach(node => {
                        node.classList.remove('search-match');
                        node.closest('li').style.display = '';
                    });
                    return;
                }

                const matchedLis = new Set();
                nodes.forEach(node => {
                    const label = node.querySelector('.tree-label')?.textContent.toLowerCase() || '';
                    const prefix = node.querySelector('.tree-prefix')?.textContent.toLowerCase() || '';
                    const isMatch = label.includes(q) || prefix.includes(q);
                    node.classList.toggle('search-match', isMatch);
                    if (isMatch) {
                        let li = node.closest('li');
                        while (li) {
                            matchedLis.add(li);
                            li = li.parentElement?.closest('li');
                        }
                    }
                });

                tree.querySelectorAll('li').forEach(li => {
                    if (matchedLis.has(li)) {
                        li.style.display = '';
                        const toggle = li.querySelector(':scope > .tree-node .tree-toggle');
                        if (toggle && toggle.classList.contains('collapsed')) {
                            this.toggleNode(toggle);
                        }
                    } else {
                        li.style.display = 'none';
                    }
                });
            }

            showTooltip(e, node) {
                const definition = node.dataset.definition;
                const uri = node.dataset.uri;
                const label = node.querySelector('.tree-label')?.textContent || '';

                let tooltipHtml = '<div class="tree-tooltip-title">' + this.escapeHtml(label) + '</div>';
                if (definition) tooltipHtml += '<div>' + this.escapeHtml(definition) + '</div>';
                if (uri) tooltipHtml += '<div class="tree-tooltip-uri">' + this.escapeHtml(uri) + '</div>';

                this.tooltip.innerHTML = tooltipHtml;
                this.tooltip.classList.add('visible');
                this.moveTooltip(e);
            }

            hideTooltip() { this.tooltip.classList.remove('visible'); }

            moveTooltip(e) {
                const x = e.clientX + 15;
                const y = e.clientY + 15;
                const rect = this.tooltip.getBoundingClientRect();
                const maxX = window.innerWidth - rect.width - 20;
                const maxY = window.innerHeight - rect.height - 20;
                this.tooltip.style.left = Math.min(x, maxX) + 'px';
                this.tooltip.style.top = Math.min(y, maxY) + 'px';
            }

            escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
        }

        // Initialize OntologyTreeManager
        new OntologyTreeManager();
    </script>
</body>

</html>'''


# =============================================================================
# SECTION 3: REGEX PATTERNS AND MARKDOWN PROCESSING HELPERS
# =============================================================================
# Regular expressions for detecting special tags in markdown content and
# utility functions for markdown-to-HTML conversion.
# =============================================================================

# Graphviz renderer tag pattern - matches all variants:
#   <!--@Graphviz_renderer:URL-->              → default (full hierarchy)
#   <!--@Graphviz_renderer_full:URL-->         → explicit full hierarchy
#   <!--@Graphviz_renderer_only_upper:URL-->   → one superclass level above
#   <!--@Graphviz_renderer_only_file:URL-->    → file content only, no hierarchy
GRAPHVIZ_TAG_RE = re.compile(
    r"<!--\s*@Graphviz_renderer(?:_(full|only_upper|upper|only_file|file))?\s*:\s*([^\s>]+)\s*-->",
    re.IGNORECASE,
)

# D2 diagram block pattern - matches ```d2 ... ``` fenced code blocks
# These are stripped as D2 diagrams are not supported by this builder
D2_BLOCK_RE = re.compile(r"```d2[\s\S]*?```", re.IGNORECASE)

# =============================================================================
# MANUAL DIAGRAM RENDERER PATTERNS
# =============================================================================
# These patterns match manually embedded diagram code in markdown files.
# Format: <!--@Graphviz_renderer_manual: Title --> followed by ```dot code block
# Format: <!--@Mermaid_renderer_manual: Title --> followed by ```mermaid code block

# Manual Graphviz renderer - user provides DOT code directly in markdown
# Usage: <!--@Graphviz_renderer_manual: My Diagram Title -->
#        ```dot
#        digraph G { A -> B }
#        ```
GRAPHVIZ_MANUAL_TAG_RE = re.compile(
    r"<!--\s*@Graphviz_renderer_manual\s*:\s*([^>]+?)\s*-->\s*\n\s*```(?:dot|graphviz)\s*\n([\s\S]*?)```",
    re.IGNORECASE | re.MULTILINE,
)

# Manual Mermaid renderer - user provides Mermaid code directly in markdown
# Usage: <!--@Mermaid_renderer_manual: My Diagram Title -->
#        ```mermaid
#        graph TD
#            A --> B
#        ```
MERMAID_MANUAL_TAG_RE = re.compile(
    r"<!--\s*@Mermaid_renderer_manual\s*:\s*([^>]+?)\s*-->\s*\n\s*```mermaid\s*\n([\s\S]*?)```",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass(frozen=True)
class ManualDiagramRef:
    """Reference to a manually embedded diagram in markdown."""
    diagram_id: str
    title: str
    code: str
    diagram_type: str  # 'graphviz' or 'mermaid'


def parse_manual_diagram_refs(md_text: str, slugify_fn: Callable[[str], str]) -> List[ManualDiagramRef]:
    """Extract all manually embedded diagram references from markdown.

    Finds <!--@Graphviz_renderer_manual: Title --> and <!--@Mermaid_renderer_manual: Title -->
    tags followed by their respective fenced code blocks.

    Args:
        md_text: The markdown text to parse.
        slugify_fn: Function to convert titles to URL-safe IDs.

    Returns:
        List of ManualDiagramRef objects in document order.
    """
    refs: List[ManualDiagramRef] = []

    # Track used IDs to avoid duplicates
    used_ids: Dict[str, int] = {}

    # Find all Graphviz manual diagrams
    for m in GRAPHVIZ_MANUAL_TAG_RE.finditer(md_text):
        title = m.group(1).strip()
        code = m.group(2).strip()
        base_id = slugify_fn(title) or "graphviz-diagram"

        # Ensure unique ID
        if base_id in used_ids:
            used_ids[base_id] += 1
            diagram_id = f"{base_id}-{used_ids[base_id]}"
        else:
            used_ids[base_id] = 0
            diagram_id = base_id

        refs.append(ManualDiagramRef(
            diagram_id=diagram_id,
            title=title,
            code=code,
            diagram_type='graphviz'
        ))

    # Find all Mermaid manual diagrams
    for m in MERMAID_MANUAL_TAG_RE.finditer(md_text):
        title = m.group(1).strip()
        code = m.group(2).strip()
        base_id = slugify_fn(title) or "mermaid-diagram"

        # Ensure unique ID
        if base_id in used_ids:
            used_ids[base_id] += 1
            diagram_id = f"{base_id}-{used_ids[base_id]}"
        else:
            used_ids[base_id] = 0
            diagram_id = base_id

        refs.append(ManualDiagramRef(
            diagram_id=diagram_id,
            title=title,
            code=code,
            diagram_type='mermaid'
        ))

    # Sort by position in document
    positions = []
    for ref in refs:
        if ref.diagram_type == 'graphviz':
            for m in GRAPHVIZ_MANUAL_TAG_RE.finditer(md_text):
                if m.group(1).strip() == ref.title:
                    positions.append((m.start(), ref))
                    break
        else:
            for m in MERMAID_MANUAL_TAG_RE.finditer(md_text):
                if m.group(1).strip() == ref.title:
                    positions.append((m.start(), ref))
                    break

    positions.sort(key=lambda x: x[0])
    return [ref for _, ref in positions]


def make_mermaid_container(diagram_id: str, title: str) -> str:
    """Generate an interactive container HTML for a Mermaid diagram.

    Args:
        diagram_id: Unique identifier for the diagram.
        title: Display title for the diagram.

    Returns:
        HTML string for the Mermaid diagram container.
    """
    title = title.strip()
    return f'''
<div class="mermaid-graph-container" id="graph-{diagram_id}" role="figure" aria-label="{title}">
  <div class="graph-header">
    <div class="graph-title">{title}</div>
    <div class="graph-controls" role="toolbar" aria-label="Graph controls">
      <button class="graph-btn" data-action="fit" aria-label="Fit to view">⊡ Fit</button>
      <button class="graph-btn" data-action="reset" aria-label="Reset view">⊙ Reset</button>
      <button class="graph-btn" data-action="fullscreen" aria-label="View fullscreen">⛶ Fullscreen</button>
      <button class="graph-btn" data-action="svg" aria-label="Download as SVG">⬇ SVG</button>
      <button class="graph-btn" data-action="png" aria-label="Download as PNG">⬇ PNG</button>
    </div>
  </div>
  <div class="graph-viewport">
    <div class="graph-wrapper" id="wrapper-{diagram_id}">
      <div class="mermaid-diagram mermaid-source" id="diagram-{diagram_id}"></div>
    </div>
    <div class="zoom-controls" role="toolbar" aria-label="Zoom controls">
      <button class="zoom-btn" data-action="zoom-in" aria-label="Zoom in">+</button>
      <div class="zoom-level" aria-live="polite">100%</div>
      <button class="zoom-btn" data-action="zoom-out" aria-label="Zoom out">−</button>
    </div>
  </div>
</div>
'''.strip()


def inject_manual_graph_containers(md_text: str, refs: List[ManualDiagramRef]) -> str:
    """Replace manual diagram tags with interactive container HTML.

    Args:
        md_text: The markdown text with manual diagram tags.
        refs: List of parsed ManualDiagramRef objects.

    Returns:
        Markdown text with diagram tags replaced by container HTML.
    """
    result = md_text

    for ref in refs:
        if ref.diagram_type == 'graphviz':
            # Replace the Graphviz manual tag and code block with container
            pattern = re.compile(
                r"<!--\s*@Graphviz_renderer_manual\s*:\s*" + re.escape(ref.title) + r"\s*-->\s*\n\s*```(?:dot|graphviz)\s*\n[\s\S]*?```",
                re.IGNORECASE | re.MULTILINE,
            )
            container = make_graph_container(ref.diagram_id, ref.title)
            result = pattern.sub(container, result, count=1)
        else:
            # Replace the Mermaid manual tag and code block with container
            pattern = re.compile(
                r"<!--\s*@Mermaid_renderer_manual\s*:\s*" + re.escape(ref.title) + r"\s*-->\s*\n\s*```mermaid\s*\n[\s\S]*?```",
                re.IGNORECASE | re.MULTILINE,
            )
            container = make_mermaid_container(ref.diagram_id, ref.title)
            result = pattern.sub(container, result, count=1)

    return result


def strip_d2_blocks(md_text: str) -> str:
    """Remove D2 diagram code blocks from markdown text.

    D2 is a diagram scripting language. This function strips any fenced code
    blocks marked with 'd2' language identifier, as they are not processed
    by this builder.

    Args:
        md_text: The raw markdown text potentially containing D2 blocks.

    Returns:
        The markdown text with all ```d2 ... ``` blocks removed.
    """
    return D2_BLOCK_RE.sub("", md_text)


def render_markdown(md_text: str) -> str:
    """Convert markdown text to HTML using markdown2.

    Uses the following markdown2 extras for enhanced formatting:
    - fenced-code-blocks: Support for ```language code blocks
    - tables: GitHub-flavored markdown tables
    - header-ids: Auto-generate IDs for headers (used by TOC)
    - cuddled-lists: Allow lists without blank line before them
    - strike: Support for ~~strikethrough~~ text
    - code-friendly: Don't convert underscores in code

    Args:
        md_text: The markdown text to convert.

    Returns:
        The rendered HTML string.
    """
    return markdown2.markdown(
        md_text,
        extras=[
            "fenced-code-blocks",
            "tables",
            "header-ids",
            "cuddled-lists",
            "strike",
            "code-friendly",
        ],
    )


def wrap_code_in_details(html: str) -> str:
    """
    Wrap <pre><code>...</code></pre> blocks in collapsible <details> elements.
    """
    # Match pre blocks (may or may not have code inside)
    pre_pattern = re.compile(r'(<pre[^>]*>)(.*?)(</pre>)', re.DOTALL)
    
    def replacer(m):
        pre_open = m.group(1)
        content = m.group(2)
        pre_close = m.group(3)
        
        # Detect language from class if present
        lang_match = re.search(r'class="[^"]*language-(\w+)', content)
        lang = lang_match.group(1) if lang_match else 'code'
        
        return f'''<details class="code-block">
<summary>📄 View pattern code</summary>
{pre_open}{content}{pre_close}
</details>'''
    
    return pre_pattern.sub(replacer, html)


def _strip_html_tags(s: str) -> str:
    """Remove all HTML tags from a string and normalize whitespace.

    Args:
        s: The input string potentially containing HTML tags.

    Returns:
        The input string with all HTML tags removed and consecutive whitespace
        collapsed to single spaces.
    """
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()


def build_toc_list_items(article_html: str) -> str:
    """
    Build a flat TOC list matching the template's CSS:

      <li><a ...>H2</a></li>
      <li class="toc-h3"><a ...>H3</a></li>
    """
    headings: List[Tuple[int, str, str]] = []
    for m in re.finditer(
        r"<h([23])\s+id=\"([^\"]+)\"[^>]*>([\s\S]*?)</h\1>",
        article_html,
        flags=re.IGNORECASE,
    ):
        level = int(m.group(1))
        hid = m.group(2)
        title = _strip_html_tags(m.group(3))
        headings.append((level, hid, title))

    items: List[str] = []
    for level, hid, title in headings:
        cls = ' class="toc-h3"' if level == 3 else ""
        items.append(f'            <li{cls}><a href="#{hid}">{title}</a></li>')

    return "\n".join(items)


def _fallback_slugify(stem: str) -> str:
    """Convert a string to a URL-safe slug identifier.

    Used as a fallback when the ttl_to_graphviz module's slugify function
    is not available. Converts the input to lowercase, replaces non-word
    characters with hyphens, and collapses multiple hyphens.

    Args:
        stem: The string to convert to a slug.

    Returns:
        A URL-safe slug string, or "diagram" if the result would be empty.
    """
    s = stem.strip().lower()
    s = re.sub(r"[^\w\-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "diagram"


def make_graph_container(diagram_id: str, title: str) -> str:
    title = title.strip()
    return (
        """
<div class="mermaid-graph-container" id="graph-{diagram_id}" role="figure" aria-label="{title}">
  <div class="graph-header">
    <div class="graph-title">{title}</div>
    <div class="graph-controls" role="toolbar" aria-label="Graph controls">
      <button class="graph-btn" data-action="fit" aria-label="Fit to view">⊡ Fit</button>
      <button class="graph-btn" data-action="reset" aria-label="Reset view">⊙ Reset</button>
      <button class="graph-btn" data-action="fullscreen" aria-label="View fullscreen">⛶ Fullscreen</button>
      <button class="graph-btn" data-action="svg" aria-label="Download as SVG">⬇ SVG</button>
      <button class="graph-btn" data-action="png" aria-label="Download as PNG">⬇ PNG</button>
    </div>
  </div>
  <div class="graph-viewport">
    <div class="graph-wrapper" id="wrapper-{diagram_id}">
      <div class="mermaid-diagram" id="diagram-{diagram_id}"></div>
    </div>
    <div class="zoom-controls" role="toolbar" aria-label="Zoom controls">
      <button class="zoom-btn" data-action="zoom-in" aria-label="Zoom in">+</button>
      <div class="zoom-level" aria-live="polite">100%</div>
      <button class="zoom-btn" data-action="zoom-out" aria-label="Zoom out">−</button>
    </div>
  </div>
  <div class="graph-legend" id="legend-{diagram_id}">
    <!-- Legend items are dynamically shown based on graph content -->
    <span class="legend-item" data-legend="bfo" style="display:none;"><span class="legend-swatch shape-square swatch-bfo"></span>BFO</span>
    <span class="legend-item" data-legend="iao" style="display:none;"><span class="legend-swatch shape-square swatch-iao"></span>IAO</span>
    <span class="legend-item" data-legend="obi" style="display:none;"><span class="legend-swatch shape-square swatch-obi"></span>OBI</span>
    <span class="legend-item" data-legend="cob" style="display:none;"><span class="legend-swatch shape-square swatch-cob"></span>COB</span>
    <span class="legend-item" data-legend="pmd" style="display:none;"><span class="legend-swatch shape-square swatch-pmd"></span>PMD</span>
    <span class="legend-item" data-legend="ro" style="display:none;"><span class="legend-swatch shape-square swatch-ro"></span>RO</span>
    <span class="legend-item" data-legend="qudt" style="display:none;"><span class="legend-swatch shape-square swatch-qudt"></span>QUDT</span>
    <span class="legend-item" data-legend="cls" style="display:none;"><span class="legend-swatch shape-square swatch-class"></span>NamedIndividual(TBox)</span>
    <span class="legend-item" data-legend="ind" style="display:none;"><span class="legend-swatch shape-oval swatch-individual"></span>Individual(ABox)</span>
    <span class="legend-item" data-legend="cat" style="display:none;"><span class="legend-swatch shape-oval swatch-categorical"></span>Categorical</span>
    <span class="legend-item" data-legend="shacl" style="display:none;"><span class="legend-swatch shape-square swatch-shacl"></span>SHACL Shape</span>
    <span class="legend-item" data-legend="constraint" style="display:none;"><span class="legend-swatch shape-square swatch-constraint"></span>Constraint</span>
    <span class="legend-item" data-legend="lit" style="display:none;"><span class="legend-swatch shape-note swatch-literal"></span>Literal</span>
    <span class="legend-item" data-legend="property" style="display:none;"><span class="legend-swatch swatch-property"></span>Object Property</span>
    <span class="legend-item" data-legend="type" style="display:none;"><span class="legend-swatch swatch-type"></span>rdf:type (dashed)</span>
  </div>
</div>
"""
    ).format(diagram_id=diagram_id, title=title).strip()


# Hierarchy modes for @Graphviz_renderer tag variants
HIERARCHY_FULL = "full"              # Walk full PMD core hierarchy upward
HIERARCHY_ONLY_UPPER = "only_upper"  # Only one subclass level above each class
HIERARCHY_ONLY_FILE = "only_file"    # No hierarchy expansion — render file content only


@dataclass(frozen=True)
class DiagramRef:
    diagram_id: str
    rel_path: str
    title: str
    hierarchy_mode: str = HIERARCHY_FULL


def parse_diagram_refs(md_text: str, slugify_fn: Callable[[str], str]) -> List[DiagramRef]:
    """
    Extract all ``<!--@Graphviz_renderer*:...-->`` placeholders from Markdown.

    Supported tag variants (case-insensitive)::

        <!--@Graphviz_renderer:URL-->              full hierarchy (default)
        <!--@Graphviz_renderer_full:URL-->          explicit full hierarchy
        <!--@Graphviz_renderer_only_upper:URL-->    one superclass level above
        <!--@Graphviz_renderer_only_file:URL-->     file content only, no hierarchy

    Returns a list of :class:`DiagramRef` in document order.
    """
    _MODE_MAP = {
        None: HIERARCHY_FULL,
        "full": HIERARCHY_FULL,
        "only_upper": HIERARCHY_ONLY_UPPER,
        "upper": HIERARCHY_ONLY_UPPER,
        "only_file": HIERARCHY_ONLY_FILE,
        "file": HIERARCHY_ONLY_FILE,
    }

    refs: List[DiagramRef] = []
    current_title = ""
    for line in md_text.splitlines():
        if line.lstrip().startswith("## "):
            current_title = line.lstrip()[3:].strip()

        m = GRAPHVIZ_TAG_RE.search(line)
        if not m:
            continue

        mode_suffix = m.group(1)  # None | "full" | "only_upper" | "only_file"
        raw = m.group(2).strip()

        hierarchy_mode = _MODE_MAP.get(
            mode_suffix.lower() if mode_suffix else None,
            HIERARCHY_FULL,
        )

        # For URLs pointing to TTL files, extract the parent folder name as diagram_id
        # Keep the original URL (with encoding) for HTTP requests
        if raw.startswith("http://") or raw.startswith("https://"):
            parsed_path = urllib.parse.urlparse(raw).path
            decoded_path = urllib.parse.unquote(parsed_path)
            path_parts = [p for p in decoded_path.split('/') if p]
            if len(path_parts) >= 2 and path_parts[-1].endswith('.ttl'):
                folder_name = path_parts[-2]
            else:
                folder_name = path_parts[-1] if path_parts else "diagram"
            rel = raw
        else:
            rel = urllib.parse.unquote(raw).strip()
            rel = rel.lstrip("./")
            folder_name = Path(rel).name

        diagram_id = slugify_fn(folder_name)
        title = current_title or folder_name
        refs.append(DiagramRef(
            diagram_id=diagram_id,
            rel_path=rel,
            title=title,
            hierarchy_mode=hierarchy_mode,
        ))
    return refs


def inject_graph_containers(md_text: str, refs: List[DiagramRef]) -> str:
    """
    Replace each Graphviz placeholder tag line with an interactive Graphviz container.
    """
    out_lines: List[str] = []
    it = iter(refs)
    for line in md_text.splitlines():
        m = GRAPHVIZ_TAG_RE.search(line)
        if not m:
            out_lines.append(line)
            continue
        ref = next(it)
        out_lines.append(make_graph_container(ref.diagram_id, ref.title))
    return "\n".join(out_lines)


# -----------------------------------------------------------------------------
# TTL to Graphviz Converter Integration
# -----------------------------------------------------------------------------
# Functions for dynamically loading the ttl_to_graphviz.py converter module
# and using it to transform TTL/SHACL files into Graphviz DOT diagrams.
# -----------------------------------------------------------------------------

def _dynamic_import_from_path(py_path: Path, module_name: str) -> Any:
    """Dynamically import a Python module from a file path.

    Uses importlib to load a module at runtime, allowing the build script
    to work with the ttl_to_graphviz converter without a package install.

    Args:
        py_path: Path to the Python file to import.
        module_name: Name to assign to the imported module in sys.modules.

    Returns:
        The imported module object.

    Raises:
        ImportError: If the module cannot be loaded from the path.
    """
    spec = importlib.util.spec_from_file_location(module_name, str(py_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {py_path}")
    mod = importlib.util.module_from_spec(spec)
    # Register in sys.modules before exec so decorators like @dataclass work
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)  # type: ignore[call-arg]
    return mod


def _find_converter_class(mod: Any) -> Any:
    """Find the diagram converter class in the loaded module.

    Searches the module for a class with a render_graph() method, preferring
    classes with 'Renderer' or 'Diagram' in their name.

    Args:
        mod: The imported converter module.

    Returns:
        The converter class (not an instance).

    Raises:
        RuntimeError: If no suitable converter class is found.
    """
    candidates = []
    for _, obj in vars(mod).items():
        if isinstance(obj, type) and hasattr(obj, "render_graph"):
            candidates.append(obj)
    if not candidates:
        raise RuntimeError(
            "Converter module must expose a class with a render_graph() method "
            "(e.g., DiagramRenderer in ttl_to_graphviz.py)."
        )

    for c in candidates:
        if "Renderer" in c.__name__ or "Diagram" in c.__name__:
            return c
    return candidates[0]


def _get_attr(obj: Any, *names: str) -> Any:
    """Get the first available attribute from an object by trying multiple names.

    Useful for handling different converter API versions that may use
    different attribute names for the same data.

    Args:
        obj: The object to get an attribute from.
        *names: Attribute names to try in order.

    Returns:
        The value of the first attribute that exists.

    Raises:
        AttributeError: If none of the specified attributes exist.
    """
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    raise AttributeError(f"Object did not expose any of: {', '.join(names)}")


def _find_shape_ttl(pattern_dir: Path) -> Optional[Path]:
    """Find the SHACL shape data TTL file in a pattern directory.

    Searches for common shape file naming conventions and falls back to
    glob matching if no exact match is found.

    Args:
        pattern_dir: Directory containing the pattern files.

    Returns:
        Path to the shape TTL file, or None if not found.
    """
    candidates = [
        pattern_dir / "shape_data.ttl",
        pattern_dir / "shape-data.ttl",
        pattern_dir / "shape data.ttl",
        pattern_dir / "shape_data.TTL",
        pattern_dir / "shape-data.TTL",
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            return p
    globs = sorted([p for p in pattern_dir.glob("shape*data*.ttl") if p.is_file() and not p.name.endswith("_full.ttl")])
    return globs[0] if globs else None


def _find_dot_file(pattern_dir: Path) -> Optional[Path]:
    """Find a pre-rendered DOT file in a pattern directory.

    Used as a fallback when no TTL source is available but a pre-generated
    Graphviz DOT file exists.

    Args:
        pattern_dir: Directory containing the pattern files.

    Returns:
        Path to the DOT file, or None if not found.
    """
    candidates = [
        pattern_dir / "shape_data.dot",
        pattern_dir / "shape-data.dot",
        pattern_dir / "graph.dot",
        pattern_dir / "diagram.dot",
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            return p
    dots = sorted([p for p in pattern_dir.glob("*.dot") if p.is_file()])
    return dots[0] if dots else None


def _find_per_pattern_js(pattern_dir: Path) -> Optional[Path]:
    """Find a cached per-pattern JavaScript file in a pattern directory.

    These files contain pre-rendered DOT code and node metadata, generated
    by a previous build with --write-per-pattern-js.

    Args:
        pattern_dir: Directory containing the pattern files.

    Returns:
        Path to the JS file, or None if not found.
    """
    js_files = sorted([p for p in pattern_dir.glob("*shape*data*.js") if p.is_file()])
    return js_files[0] if js_files else None


def _extract_from_per_pattern_js(js_text: str) -> Tuple[Optional[str], Optional[dict]]:
    """
    Extract diagram DOT (template literal) and nodeData from a *_shape_data.js file.

    Supports both legacy 'const diagrams' and patched 'const dotDiagrams' naming.
    """
    diag = None
    m = re.search(
        r'const\s+(?:diagrams|dotDiagrams)\s*=\s*\{[\s\S]*?`([\s\S]*?)`[\s\S]*?\}\s*;',
        js_text,
    )
    if m:
        diag = m.group(1)

    nd = None
    m2 = re.search(r'const\s+nodeData\s*=\s*(\{[\s\S]*?\})\s*;', js_text)
    if m2:
        try:
            nd = json.loads(m2.group(1))
        except Exception:
            nd = None
    return diag, nd


# Cache for the PMD core full-ontology index (built once per process)
_PMDCO_FULL_ONTOLOGY_INDEX = None


def _load_pmdco_full_ontology_index(converter_module):
    """Load the PMD core full ontology as a FullOntologyIndex.

    The ontology path is read from navigator.yaml's ``full_ontology_path``.
    Supports both remote URLs and local file paths.  The result is cached so
    that repeated calls (e.g. across multiple diagrams) are essentially free.
    """
    global _PMDCO_FULL_ONTOLOGY_INDEX
    if _PMDCO_FULL_ONTOLOGY_INDEX is not None:
        return _PMDCO_FULL_ONTOLOGY_INDEX

    load_fn = getattr(converter_module, "load_full_ontology_index", None)
    if not callable(load_fn):
        print("  Warning: converter module has no load_full_ontology_index; hierarchy disabled")
        return None

    script_dir = Path(__file__).parent
    config = load_NAVIGATOR_CONFIG(script_dir)
    full_ontology_path = config.get("full_ontology_path", "")

    ttl_path = None

    if not full_ontology_path:
        # Fallback: look for pmdco_full.ttl next to docs
        candidate = script_dir.parent / "patterns" / "pmdco_full.ttl"
        if candidate.exists():
            ttl_path = candidate

    elif full_ontology_path.startswith("http://") or full_ontology_path.startswith("https://"):
        # Download to a temp file so load_full_ontology_index can parse it
        try:
            print(f"  Fetching PMD core ontology for hierarchy: {full_ontology_path}")
            req = urllib.request.Request(full_ontology_path, headers={"User-Agent": "PMDco-Doc-Builder/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                ttl_content = resp.read().decode("utf-8")
            tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".ttl", delete=False, encoding="utf-8")
            tmp.write(ttl_content)
            tmp.close()
            ttl_path = Path(tmp.name)
            print(f"  Downloaded {len(ttl_content)} bytes for hierarchy index")
        except Exception as exc:
            print(f"  Warning: Failed to fetch full ontology from URL: {exc}")

    else:
        # Local path (absolute or relative to docs dir)
        p = Path(full_ontology_path)
        if not p.is_absolute():
            p = script_dir.parent / full_ontology_path
        if p.exists():
            ttl_path = p

    if ttl_path is None:
        print("  Warning: PMD core full ontology not found; hierarchy expansion disabled")
        return None

    print(f"  Building full-ontology hierarchy index from: {ttl_path.name}")
    index = load_fn([ttl_path])
    if index is not None:
        print(f"  Indexed {len(index.labels)} labels, {len(index.parents)} parent relations")
    _PMDCO_FULL_ONTOLOGY_INDEX = index
    return index


def _resolve_diagram_sources(
    refs: List[DiagramRef],
    diagrams_root: Path,
    converter_path: Path,
    strict: bool = True,
    write_per_pattern_js: bool = False,
) -> Tuple[Dict[str, str], Dict[str, Dict[str, Dict[str, str]]], Callable[[str], str]]:
    mod = _dynamic_import_from_path(converter_path, "ttl_to_graphviz_dyn")
    Converter = _find_converter_class(mod)

    js_escape = getattr(mod, "js_escape_template_literal", None)
    if not callable(js_escape):
        def js_escape(s: str) -> str:
            s = s.replace("\\", "\\\\")
            s = s.replace("`", "\\`")
            s = s.replace("${", "\\${")
            return s

    # Load PMD core full ontology for hierarchy expansion and label resolution.
    # This is the ONLY source of truth for class hierarchy — external ontologies
    # (BFO, OBI, IAO etc.) are NOT used for hierarchy because their view may
    # differ from PMD core's curated structure.
    full_ontology_index = _load_pmdco_full_ontology_index(mod)

    # Instantiate converter:
    #   enrich=True        → enables remote label lookups for node names
    #   superclass_depth=0 → disables remote hierarchy expansion (we use full_ontology instead)
    #   full_ontology       → PMD core ontology drives all hierarchy edges
    converter_options = {
        "output_format": "dot",
        "include_bnodes": False,
        "enrich": True,
        "superclass_depth": 0,
        "full_ontology": full_ontology_index,
        "use_full_hierarchy": True,
        "full_hierarchy_max_depth": 20,
        "max_nodes": 500,
        "max_edges": 1500,
    }
    try:
        converter = Converter(**converter_options)
    except TypeError:
        # Fallback for simpler converter signatures
        try:
            converter = Converter(output_format="dot")
        except TypeError:
            converter = Converter()
        # Set attributes directly if possible
        for attr, val in converter_options.items():
            if hasattr(converter, attr):
                setattr(converter, attr, val)

    def _hierarchy_kwargs(mode: str) -> Dict[str, Any]:
        """Map a hierarchy_mode string to render_graph() keyword arguments."""
        if mode == HIERARCHY_ONLY_FILE:
            return {"use_full_hierarchy": False}
        if mode == HIERARCHY_ONLY_UPPER:
            return {"use_full_hierarchy": True, "full_hierarchy_max_depth": 1}
        # HIERARCHY_FULL (default)
        return {}

    diagrams: Dict[str, str] = {}
    node_data_all: Dict[str, Dict[str, Dict[str, str]]] = {}

    for ref in refs:
        # Check if rel_path is a remote URL
        is_remote_url = ref.rel_path.startswith("http://") or ref.rel_path.startswith("https://")
        
        if is_remote_url:
            # Download TTL content from remote URL
            try:
                print(f"  Fetching remote TTL: {ref.rel_path}")
                req = urllib.request.Request(ref.rel_path, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=30) as response:
                    ttl_content = response.read().decode('utf-8')
                    print(f"    Downloaded {len(ttl_content)} bytes")
                
                # Write to temporary file for processing
                with tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False, encoding='utf-8') as tmp_file:
                    tmp_file.write(ttl_content)
                    tmp_path = Path(tmp_file.name)
                
                try:
                    hkw = _hierarchy_kwargs(ref.hierarchy_mode)
                    print(f"    Hierarchy mode: {ref.hierarchy_mode}")
                    res = converter.render_graph(tmp_path, diagram_id=ref.diagram_id, **hkw)
                    dot = _get_attr(res, "source", "dot", "graphviz", "code", "mermaid")
                    nd = _get_attr(res, "node_data", "nodeData")
                    diagrams[ref.diagram_id] = str(dot)
                    node_data_all[ref.diagram_id] = dict(nd)
                    print(f"    Generated diagram: {ref.diagram_id}")
                finally:
                    # Clean up temp file
                    try:
                        tmp_path.unlink()
                    except:
                        pass
                continue
                
            except Exception as e:
                if strict:
                    raise RuntimeError(f"Failed to fetch remote TTL for '{ref.diagram_id}' from {ref.rel_path}: {e}")
                print(f"    Warning: Failed to fetch {ref.rel_path}: {e}")
                continue
        
        # Local file handling (original behavior)
        pattern_dir = (diagrams_root / ref.rel_path).resolve()
        if not pattern_dir.exists():
            if strict:
                raise FileNotFoundError(f"Pattern directory not found: {pattern_dir} (from {ref.rel_path})")
            continue

        ttl = _find_shape_ttl(pattern_dir)
        if ttl and ttl.exists():
            hkw = _hierarchy_kwargs(ref.hierarchy_mode)
            res = converter.render_graph(ttl, diagram_id=ref.diagram_id, **hkw)  # type: ignore[attr-defined]
            dot = _get_attr(res, "source", "dot", "graphviz", "code", "mermaid")
            nd = _get_attr(res, "node_data", "nodeData")
            diagrams[ref.diagram_id] = str(dot)
            node_data_all[ref.diagram_id] = dict(nd)

            if write_per_pattern_js:
                out_js = pattern_dir / f"{ref.diagram_id}_shape_data.js"
                out_js.write_text(
                    "// Auto-generated by build_patterns_graphviz_advanced.py. Do not edit.\n"
                    "const dotDiagrams = {\n"
                    f'  "{ref.diagram_id}": `{js_escape(str(dot))}`\n'
                    "};\n\n"
                    "const nodeData = " + json.dumps({ref.diagram_id: nd}, ensure_ascii=False, indent=2) + ";\n",
                    encoding="utf-8",
                )
            continue

        dot_file = _find_dot_file(pattern_dir)
        if dot_file and dot_file.exists():
            diagrams[ref.diagram_id] = dot_file.read_text(encoding="utf-8")
            node_data_all.setdefault(ref.diagram_id, {})
            continue

        js_file = _find_per_pattern_js(pattern_dir)
        if js_file and js_file.exists():
            diag, nd = _extract_from_per_pattern_js(js_file.read_text(encoding="utf-8"))
            if diag:
                diagrams[ref.diagram_id] = diag
            if isinstance(nd, dict) and ref.diagram_id in nd:
                node_data_all[ref.diagram_id] = nd[ref.diagram_id]
            else:
                node_data_all.setdefault(ref.diagram_id, {})
            if ref.diagram_id in diagrams:
                continue

        if strict:
            raise FileNotFoundError(
                f"Could not resolve diagram source for '{ref.diagram_id}' in {pattern_dir}. "
                "Expected shape_data.ttl, a .dot file, or a *_shape_data.js file."
            )

    return diagrams, node_data_all, js_escape


def build_dot_diagrams_object(diagrams: Dict[str, str], js_escape_fn: Callable[[str], str]) -> str:
    lines: List[str] = []
    lines.append("{")
    for k in sorted(diagrams.keys()):
        code = js_escape_fn(diagrams[k])
        lines.append(f'            "{k}": `{code}`,')
        lines.append("")
    if lines and lines[-1] == "":
        lines.pop()
    lines.append("        }")
    return "\n".join(lines)


def build_node_data_object(node_data: Dict[str, Dict[str, Dict[str, str]]]) -> str:
    return json.dumps(node_data, ensure_ascii=False, indent=12)


def build_mermaid_diagrams_object(diagrams: Dict[str, str], js_escape_fn: Callable[[str], str]) -> str:
    """Build a JavaScript object literal containing Mermaid diagram code.

    Args:
        diagrams: Dict mapping diagram IDs to Mermaid source code.
        js_escape_fn: Function to escape code for JavaScript template literals.

    Returns:
        JavaScript object literal as a string.
    """
    if not diagrams:
        return "{}"
    lines: List[str] = []
    lines.append("{")
    for k in sorted(diagrams.keys()):
        code = js_escape_fn(diagrams[k])
        lines.append(f'            "{k}": `{code}`,')
        lines.append("")
    if lines and lines[-1] == "":
        lines.pop()
    lines.append("        }")
    return "\n".join(lines)


def build_html(
    markdown_path: Path,
    diagrams_root: Path,
    out_html: Path,
    converter_path: Path,
    strict: bool = True,
    write_per_pattern_js: bool = False,
) -> None:
    """Build an HTML documentation page with Graphviz diagrams (patterns mode).

    This is the main build function for pattern documentation pages that contain
    @Graphviz_renderer tags. It processes the markdown, resolves diagram sources,
    renders them using the ttl_to_graphviz converter, and generates an interactive
    HTML page.

    Args:
        markdown_path: Path to the source markdown file.
        diagrams_root: Base directory for resolving @Graphviz_renderer paths.
        out_html: Path where the output HTML file will be written.
        converter_path: Path to the ttl_to_graphviz.py converter module.
        strict: If True, raise errors when diagrams cannot be resolved.
            If False, skip missing diagrams with warnings.
        write_per_pattern_js: If True, write per-pattern *_shape_data.js files
            alongside the TTL sources for caching.

    Raises:
        FileNotFoundError: If strict=True and a diagram source cannot be found.
        RuntimeError: If required template placeholders are missing.
    """
    md_text_raw = markdown_path.read_text(encoding="utf-8")

    # Process @md_file_renderer / @source_code_renderer before anything else
    if MD_FILE_RENDERER_RE.search(md_text_raw):
        print("  Processing @md_file_renderer tags...")
        md_text_raw = process_md_file_renderers(md_text_raw)
    if SOURCE_CODE_RENDERER_RE.search(md_text_raw):
        print("  Processing @source_code_renderer tags...")
        md_text_raw = process_source_code_renderers(md_text_raw)

    mod = _dynamic_import_from_path(converter_path, "ttl_to_graphviz_slug")
    slugify_fn = getattr(mod, "slugify", None)
    if not callable(slugify_fn):
        slugify_fn = _fallback_slugify
    refs = parse_diagram_refs(md_text_raw, slugify_fn)

    # Parse manual diagram references (embedded DOT/Mermaid code)
    manual_refs = parse_manual_diagram_refs(md_text_raw, slugify_fn)
    if manual_refs:
        print(f"  Found {len(manual_refs)} manual diagram(s)")

    md_text = strip_d2_blocks(md_text_raw)
    md_with_graphs = inject_graph_containers(md_text, refs)

    # Inject containers for manual diagrams
    if manual_refs:
        md_with_graphs = inject_manual_graph_containers(md_with_graphs, manual_refs)

    article_html = wrap_code_in_details(render_markdown(md_with_graphs).strip())
    toc_items = build_toc_list_items(article_html).strip()

    diagrams, node_data_all, js_escape = _resolve_diagram_sources(
        refs=refs,
        diagrams_root=diagrams_root,
        converter_path=converter_path,
        strict=strict,
        write_per_pattern_js=write_per_pattern_js,
    )

    # Add manual diagrams to the diagrams object
    mermaid_diagrams: Dict[str, str] = {}
    for ref in manual_refs:
        if ref.diagram_type == 'graphviz':
            diagrams[ref.diagram_id] = ref.code
            node_data_all[ref.diagram_id] = {}
            print(f"    Added manual Graphviz diagram: {ref.diagram_id}")
        else:
            mermaid_diagrams[ref.diagram_id] = ref.code
            print(f"    Added manual Mermaid diagram: {ref.diagram_id}")

    dot_obj = build_dot_diagrams_object(diagrams, js_escape)
    node_obj = build_node_data_object(node_data_all)
    mermaid_obj = build_mermaid_diagrams_object(mermaid_diagrams, js_escape)

    html_out = TEMPLATE_HTML
    for ph in ("__ARTICLE_CONTENT__", "__TOC_LIST_ITEMS__", "__DIAGRAMS_OBJECT__", "__NODEDATA_OBJECT__", "__MERMAID_DIAGRAMS_OBJECT__"):
        if ph not in html_out:
            raise RuntimeError(f"Template placeholder missing: {ph}")

    html_out = html_out.replace("__ARTICLE_CONTENT__", article_html)
    html_out = html_out.replace("__TOC_LIST_ITEMS__", toc_items)
    html_out = html_out.replace("__DIAGRAMS_OBJECT__", dot_obj)
    html_out = html_out.replace("__NODEDATA_OBJECT__", node_obj)
    html_out = html_out.replace("__MERMAID_DIAGRAMS_OBJECT__", mermaid_obj)

    # Generate dynamic sidebar from navigator.yaml
    active_page = out_html.name  # Use output filename to determine active page
    sidebar_html = generate_sidebar_html(active_page=active_page, script_dir=Path(__file__).parent)
    html_out = html_out.replace("__SIDEBAR_HTML__", sidebar_html)

    # Generate dynamic page navigation from navigator.yaml
    page_nav_html = generate_page_nav_html(active_page=active_page, script_dir=Path(__file__).parent)
    html_out = html_out.replace("__PAGE_NAV__", page_nav_html)

    out_html.write_text(html_out, encoding="utf-8")


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the PMDco documentation builder.

    Parses command-line arguments, detects or uses the specified build mode,
    and delegates to the appropriate build function (build_html for patterns,
    build_doc_html for docs).

    Args:
        argv: Command-line arguments. If None, uses sys.argv.

    Returns:
        Exit code: 0 for success, 1 for errors.

    Command-Line Arguments:
        --mode, -M: Build mode (docs, patterns, auto)
        --markdown, -m: Source markdown file path (required)
        --out, -o: Output HTML file path (required)
        --title, -t: Page title override (docs mode)
        --diagrams-root, -d: Base directory for diagrams (patterns mode, required)
        --converter, -c: Path to ttl_to_graphviz.py converter
        --no-strict: Continue on diagram resolution failures
        --prev, --next: Page navigation links (docs mode)
        --active-nav: Active navigation item identifier
        --write-per-pattern-js: Cache rendered diagrams as JS files
    """
    p = argparse.ArgumentParser(description="Unified PMDco documentation builder (supports docs and patterns modes).")
    p.add_argument("--mode", "-M", type=str, choices=["docs", "patterns", "auto"], default="auto",
                   help="Build mode: 'docs' for simple markdown, 'patterns' for diagrams, 'auto' to detect (default: auto).")
    p.add_argument("--markdown", "-m", type=Path, required=True, help="Path to source Markdown file.")
    p.add_argument("--out", "-o", type=Path, required=True, help="Output HTML path.")
    p.add_argument("--title", "-t", type=str, default=None, help="Page title (defaults to H1, docs mode only).")
    p.add_argument("--diagrams-root", "-d", type=Path, default=None, help="Base directory for Graphviz_renderer paths (patterns mode).")
    p.add_argument(
        "--converter",
        "-c",
        type=Path,
        default=Path(__file__).with_name("ttl_to_graphviz.py"),
        help="Path to ttl_to_graphviz.py (patterns mode only).",
    )
    p.add_argument("--no-strict", action="store_true", help="Do not fail build if a diagram cannot be resolved.")
    p.add_argument("--prev", type=str, default=None, help="Previous page: 'href|title' (docs mode only).")
    p.add_argument("--next", type=str, default=None, help="Next page: 'href|title' (docs mode only).")
    p.add_argument("--active-nav", type=str, default=None, help="Active nav item (docs mode only).")
    p.add_argument(
        "--write-per-pattern-js",
        action="store_true",
        help="Write per-pattern *_shape_data.js files (patterns mode only).",
    )
    args = p.parse_args(argv)

    # Read markdown to detect mode if auto
    md_text = args.markdown.read_text(encoding="utf-8")
    mode = args.mode
    
    if mode == "auto":
        # Auto-detect based on content
        if GRAPHVIZ_TAG_RE.search(md_text):
            mode = "patterns"
            print("Auto-detected mode: patterns (found @Graphviz_renderer tags)")
        else:
            mode = "docs"
            print("Auto-detected mode: docs")

    if mode == "patterns":
        # Patterns mode - require diagrams-root
        if args.diagrams_root is None:
            print("Error: --diagrams-root is required for patterns mode")
            return 1
        
        build_html(
            markdown_path=args.markdown.resolve(),
            diagrams_root=args.diagrams_root.resolve(),
            out_html=args.out.resolve(),
            converter_path=args.converter.resolve(),
            strict=not args.no_strict,
            write_per_pattern_js=args.write_per_pattern_js,
        )
    else:
        # Docs mode
        prev_page = tuple(args.prev.split("|", 1)) if args.prev else None
        next_page = tuple(args.next.split("|", 1)) if args.next else None
        
        build_doc_html(
            markdown_path=args.markdown.resolve(),
            out_html=args.out.resolve(),
            page_title=args.title,
            prev_page=prev_page,
            next_page=next_page,
            active_nav=args.active_nav,
        )
    
    return 0


# =============================================================================
# SECTION 4: DOCS MODE - ONTOLOGY TREE GENERATION
# =============================================================================
# Functions for processing @module_indicator and @property_indicator tags,
# parsing OWL ontologies, and generating interactive class/property trees.
# Originally from build_docs.py, now unified into this single builder.
# =============================================================================

# Regex patterns for document indicator tags
# @Document_indicator - Marker tag (stripped, not rendered)
DOCUMENT_INDICATOR_RE = re.compile(r"<!--\s*@Document_indicator\s*:\s*([^>]+)\s*-->", re.IGNORECASE)

# @module_indicator:URL - Generates class hierarchy tree from OWL file at URL
MODULE_INDICATOR_RE = re.compile(r"<!--\s*@module_indicator\s*:\s*(https?://[^\s>]+)\s*-->", re.IGNORECASE)

# @property_indicator:TYPE - Generates property tree (TYPE = object|data|annotation)
PROPERTY_INDICATOR_RE = re.compile(r"<!--\s*@property_indicator\s*:\s*(object|data|annotation)\s*-->", re.IGNORECASE)

# @md_file_renderer:URL - Injects markdown content from remote URL
MD_FILE_RENDERER_RE = re.compile(r"<!--\s*@md_file_renderer\s*:\s*(https?://[^\s>]+)\s*-->", re.IGNORECASE)

# @source_code_renderer:URL - Injects source code from remote URL in fenced block
SOURCE_CODE_RENDERER_RE = re.compile(r"<!--\s*@source_code_renderer\s*:\s*(https?://[^\s>]+)\s*-->", re.IGNORECASE)


@dataclass
class OntologyClass:
    """Represents an ontology class with its metadata."""
    uri: str
    label: str = ""
    definition: str = ""
    children: List['OntologyClass'] = field(default_factory=list)
    
    @property
    def prefix(self) -> str:
        uri = self.uri
        if 'pmd/co/' in uri or '/PMD_' in uri: return 'pmd'
        elif 'BFO_' in uri: return 'bfo'
        elif 'RO_' in uri: return 'ro'
        elif 'IAO_' in uri: return 'iao'
        elif 'OBI_' in uri: return 'obi'
        elif 'CHEBI_' in uri: return 'chebi'
        return 'owl'
    
    @property
    def display_name(self) -> str:
        if self.label: return self.label
        local = self.uri.split('#')[-1] if '#' in self.uri else self.uri.split('/')[-1]
        return local.replace('_', ' ')


@dataclass
class OntologyProperty:
    """Represents an ontology property with its metadata."""
    uri: str
    label: str = ""
    definition: str = ""
    property_type: str = "object"
    children: List['OntologyProperty'] = field(default_factory=list)
    
    @property
    def prefix(self) -> str:
        if 'pmd/co/' in self.uri or 'PMD_' in self.uri: return 'pmd'
        elif 'BFO_' in self.uri: return 'bfo'
        elif 'RO_' in self.uri: return 'ro'
        elif 'IAO_' in self.uri: return 'iao'
        elif 'OBI_' in self.uri: return 'obi'
        return 'owl'
    
    @property
    def display_name(self) -> str:
        if self.label: return self.label
        local = self.uri.split('#')[-1] if '#' in self.uri else self.uri.split('/')[-1]
        return local.replace('_', ' ')


def fetch_owl_file(url: str) -> Optional[str]:
    """Fetch OWL ontology file content from a remote URL.

    Downloads the content of an OWL file (in any format: RDF/XML, Turtle,
    Functional Syntax) from the specified URL with a 30-second timeout.

    Args:
        url: The URL of the OWL file to fetch.

    Returns:
        The file content as a UTF-8 decoded string, or None if the fetch fails.
    """
    try:
        print(f"  Fetching OWL file from: {url}")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8')
            print(f"  Fetched {len(content)} bytes")
            return content
    except Exception as e:
        print(f"  Warning: Failed to fetch {url}: {e}")
        return None


def parse_owl_functional_syntax(owl_content: str) -> Optional[dict]:
    """Parse OWL Functional Syntax format and extract class hierarchy.

    Extracts class declarations, subclass relationships, and rdfs:label
    annotations from OWL content in Functional Syntax format (starts with
    'Prefix(...)').

    Args:
        owl_content: The OWL content string in Functional Syntax format.

    Returns:
        A dictionary containing:
        - 'classes': Dict[str, OntologyClass] mapping URIs to class objects
        - 'child_map': Dict[str, set] mapping parent URIs to child URI sets
        - 'parent_map': Dict[str, set] mapping child URIs to parent URI sets
        Returns None if parsing fails.
    """
    classes: Dict[str, OntologyClass] = {}
    child_map: Dict[str, set] = defaultdict(set)
    parent_map: Dict[str, set] = defaultdict(set)
    
    # Extract prefixes
    prefixes = {}
    for m in re.finditer(r'Prefix\(\s*(\w*)\s*[:=]\s*\<([^>]+)\>\s*\)', owl_content):
        prefix = m.group(1)
        iri = m.group(2)
        prefixes[prefix] = iri
    
    def resolve_iri(ref: str) -> str:
        ref = ref.strip()
        if ref.startswith('<') and ref.endswith('>'):
            return ref[1:-1]
        if ':' in ref:
            prefix, local = ref.split(':', 1)
            if prefix in prefixes:
                return prefixes[prefix] + local
        return ref
    
    # Parse Declaration(Class(...))
    for m in re.finditer(r'Declaration\s*\(\s*Class\s*\(\s*([^)]+)\s*\)\s*\)', owl_content):
        uri = resolve_iri(m.group(1))
        if uri and uri not in classes:
            classes[uri] = OntologyClass(uri=uri)
    
    # Parse SubClassOf
    for m in re.finditer(r'SubClassOf\s*\(\s*([^)\s]+)\s+([^)\s]+)\s*\)', owl_content):
        child_iri = resolve_iri(m.group(1))
        parent_iri = resolve_iri(m.group(2))
        if child_iri and parent_iri:
            child_map[parent_iri].add(child_iri)
            parent_map[child_iri].add(parent_iri)
            if child_iri not in classes:
                classes[child_iri] = OntologyClass(uri=child_iri)
            if parent_iri not in classes:
                classes[parent_iri] = OntologyClass(uri=parent_iri)
    
    # Parse annotations (labels)
    for m in re.finditer(r'AnnotationAssertion\s*\(\s*rdfs:label\s+([^)\s]+)\s+"([^"]+)"', owl_content):
        uri = resolve_iri(m.group(1))
        label = m.group(2)
        if uri in classes:
            classes[uri].label = label
    
    print(f"  Parsed {len(classes)} classes from OWL Functional Syntax")
    return {'classes': classes, 'child_map': child_map, 'parent_map': parent_map}


def parse_owl_content(owl_content: str) -> Optional[dict]:
    """Parse OWL content in any supported format and extract class hierarchy.

    Auto-detects the OWL format (Functional Syntax, RDF/XML, or Turtle) and
    delegates to the appropriate parser. Extracts owl:Class declarations,
    rdfs:subClassOf relationships, and rdfs:label annotations.

    Args:
        owl_content: The OWL ontology content as a string.

    Returns:
        A dictionary containing 'classes', 'child_map', and 'parent_map',
        or None if parsing fails. See parse_owl_functional_syntax for details.

    Note:
        RDF/XML and Turtle parsing requires rdflib to be installed.
    """
    if owl_content.strip().startswith('Prefix('):
        return parse_owl_functional_syntax(owl_content)
    
    if not RDFLIB_AVAILABLE:
        print("  Warning: rdflib not available, cannot parse RDF/XML or Turtle")
        return None
    
    try:
        graph = Graph()
        graph.parse(data=owl_content, format="xml")
    except:
        try:
            graph = Graph()
            graph.parse(data=owl_content, format="turtle")
        except Exception as e:
            print(f"  Warning: Failed to parse OWL content: {e}")
            return None
    
    classes: Dict[str, OntologyClass] = {}
    child_map: Dict[str, set] = defaultdict(set)
    parent_map: Dict[str, set] = defaultdict(set)
    
    # Get all classes
    for s, p, o in graph.triples((None, RDF.type, OWL.Class)):
        uri = str(s)
        classes[uri] = OntologyClass(uri=uri)
    
    # Get labels
    for s, p, o in graph.triples((None, RDFS.label, None)):
        uri = str(s)
        if uri in classes and isinstance(o, Literal):
            lang = o.language
            if lang == 'en' or lang is None:
                classes[uri].label = str(o)
    
    # Get subclass relationships
    for s, p, o in graph.triples((None, RDFS.subClassOf, None)):
        child_uri = str(s)
        parent_uri = str(o)
        if isinstance(o, URIRef):
            child_map[parent_uri].add(child_uri)
            parent_map[child_uri].add(parent_uri)
    
    print(f"  Parsed {len(classes)} classes")
    return {'classes': classes, 'child_map': child_map, 'parent_map': parent_map}


def build_tree(classes: dict, child_map: dict, parent_map: dict) -> List[OntologyClass]:
    """Build a hierarchical tree structure from parsed ontology classes.

    Creates a tree of OntologyClass nodes from flat dictionaries of classes
    and their relationships. Classes without parents become root nodes.

    Args:
        classes: Dict mapping URIs to OntologyClass instances.
        child_map: Dict mapping parent URIs to sets of child URIs.
        parent_map: Dict mapping child URIs to sets of parent URIs.

    Returns:
        List of root OntologyClass nodes with children populated recursively.
    """
    roots = []
    for uri in classes:
        if uri not in parent_map or not parent_map[uri]:
            roots.append(uri)
    
    def build_node(uri: str, visited: set) -> Optional[OntologyClass]:
        if uri in visited or uri not in classes:
            return None
        visited.add(uri)
        source = classes[uri]
        node = OntologyClass(uri=source.uri, label=source.label, definition=source.definition)
        children = sorted(child_map.get(uri, set()), 
                          key=lambda u: classes.get(u, OntologyClass(uri=u)).display_name.lower())
        for child_uri in children:
            child_node = build_node(child_uri, visited.copy())
            if child_node:
                node.children.append(child_node)
        return node
    
    tree_roots = []
    for root_uri in sorted(roots, key=lambda u: classes.get(u, OntologyClass(uri=u)).display_name.lower()):
        node = build_node(root_uri, set())
        if node:
            tree_roots.append(node)
    
    return tree_roots


def count_tree_nodes(roots: List[OntologyClass]) -> int:
    """Count total number of nodes in a tree structure.

    Recursively traverses the tree starting from all root nodes and counts
    every node encountered. Works with any object that has a 'children' attribute.

    Args:
        roots: List of root nodes (OntologyClass or OntologyProperty instances).

    Returns:
        The total number of nodes in the tree including all roots and descendants.
    """
    count = 0

    def count_rec(node):
        nonlocal count
        count += 1
        for child in node.children:
            count_rec(child)

    for root in roots:
        count_rec(root)
    return count


def generate_tree_html(roots: List[OntologyClass], tree_id: str) -> str:
    """Generate interactive HTML for an ontology class tree.

    Creates a collapsible tree view with:
    - Expand/collapse all buttons
    - Search functionality
    - Class count display
    - Tooltip support for definitions
    - Prefix-based styling (pmd, bfo, ro, etc.)

    Args:
        roots: List of root OntologyClass nodes with populated children.
        tree_id: Unique HTML ID for the tree container element.

    Returns:
        Complete HTML string for the interactive tree component.
    """
    class_count = count_tree_nodes(roots)
    
    def generate_node_html(node: OntologyClass, depth: int) -> str:
        has_children = len(node.children) > 0
        has_definition = bool(node.definition)
        
        label = html_module.escape(node.display_name)
        prefix = html_module.escape(node.prefix)
        definition = html_module.escape(node.definition or '')
        uri = html_module.escape(node.uri)
        
        node_classes = ['tree-node']
        if has_definition:
            node_classes.append('has-definition')
        
        data_attrs = f'data-uri="{uri}"'
        if has_definition:
            data_attrs += f' data-definition="{definition}"'
        
        initially_collapsed = depth >= 1 and has_children
        toggle_class = 'collapsed' if initially_collapsed else 'expanded'
        children_class = 'collapsed' if initially_collapsed else ''
        
        html_parts = ['<li>']
        html_parts.append(f'<span class="{" ".join(node_classes)}" {data_attrs}>')
        
        if has_children:
            html_parts.append(f'<button class="tree-toggle {toggle_class}" aria-label="Toggle"></button>')
        else:
            html_parts.append('<span class="tree-toggle-placeholder"></span>')
        
        html_parts.append(f'<span class="tree-prefix">{prefix}:</span>')
        html_parts.append(f'<span class="tree-label">{label}</span>')
        html_parts.append('</span>')
        
        if has_children:
            html_parts.append(f'<ul class="tree-children {children_class}">')
            for child in node.children:
                html_parts.append(generate_node_html(child, depth + 1))
            html_parts.append('</ul>')
        
        html_parts.append('</li>')
        return ''.join(html_parts)
    
    html_parts = [f'''
    <div class="ontology-tree-container" id="{tree_id}" role="tree" aria-label="Class hierarchy">
        <div class="tree-toolbar" role="toolbar" aria-label="Tree controls">
            <button class="tree-toolbar-btn tree-expand-all" aria-label="Expand all nodes">Expand All</button>
            <button class="tree-toolbar-btn tree-collapse-all" aria-label="Collapse all nodes">Collapse All</button>
            <input type="text" class="tree-search" id="{tree_id}-search" name="{tree_id}-search" placeholder="Search classes..." aria-label="Search classes">
            <span class="tree-stats" aria-live="polite">{class_count} classes</span>
        </div>
        <ul class="ontology-tree" role="group">
    ''']
    
    for root in roots:
        html_parts.append(generate_node_html(root, 0))
    
    html_parts.append('</ul></div>')
    return ''.join(html_parts)


def process_module_indicators(html_content: str) -> str:
    """Process @module_indicator tags and replace with generated class trees.

    Finds all HTML comments matching <!--@module_indicator:URL--> and replaces
    them with interactive ontology class trees generated from the OWL file
    at the specified URL.

    Args:
        html_content: The HTML content containing @module_indicator tags.

    Returns:
        The HTML with all @module_indicator tags replaced by tree widgets,
        or warning messages if loading/parsing fails.
    """
    tree_counter = [0]
    
    def replace_indicator(match):
        url = match.group(1).strip()
        tree_counter[0] += 1
        tree_id = f"module-tree-{tree_counter[0]}"
        
        owl_content = fetch_owl_file(url)
        if not owl_content:
            return f'<p class="warning">Failed to load ontology from {html_module.escape(url)}</p>'
        
        parsed = parse_owl_content(owl_content)
        if not parsed:
            return f'<p class="warning">Failed to parse ontology from {html_module.escape(url)}</p>'
        
        # Enrich classes with labels from full ontology
        enrich_classes_from_full_ontology(parsed['classes'])
        
        roots = build_tree(parsed['classes'], parsed['child_map'], parsed['parent_map'])
        if not roots:
            return f'<p class="warning">No classes found in {html_module.escape(url)}</p>'
        
        tree_html = generate_tree_html(roots, tree_id)
        print(f"  Generated tree with {count_tree_nodes(roots)} classes")
        return tree_html
    
    return MODULE_INDICATOR_RE.sub(replace_indicator, html_content)


# Global cache for full ontology labels
_FULL_ONTOLOGY_LABELS = None
_FULL_ONTOLOGY_URL_CACHE = None


def load_full_ontology_from_url(url: str) -> dict:
    """Load all labels from the full ontology via URL.
    
    Fetches TTL from URL, parses it, and extracts labels/definitions.
    Results are cached for subsequent calls.
    """
    global _FULL_ONTOLOGY_URL_CACHE
    
    if _FULL_ONTOLOGY_URL_CACHE is not None:
        return _FULL_ONTOLOGY_URL_CACHE
    
    if not RDFLIB_AVAILABLE:
        print("  Warning: rdflib not available for full ontology parsing")
        return {}
    
    print(f"  Fetching full ontology from URL: {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PMDco-Doc-Builder/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            ttl_content = resp.read().decode('utf-8')
        print(f"  Fetched {len(ttl_content)} bytes")
        
        graph = Graph()
        graph.parse(data=ttl_content, format="turtle")
        
        labels = {}
        definitions = {}
        
        # Extract all labels
        for subj, _, obj in graph.triples((None, RDFS.label, None)):
            if isinstance(subj, URIRef) and isinstance(obj, Literal):
                uri = str(subj)
                lang = obj.language
                if lang == 'en' or lang is None:
                    labels[uri] = str(obj)
        
        # Extract definitions
        for subj, _, obj in graph.triples((None, SKOS.definition, None)):
            if isinstance(subj, URIRef) and isinstance(obj, Literal):
                uri = str(subj)
                lang = obj.language
                if lang == 'en' or lang is None:
                    definitions[uri] = str(obj)
        
        print(f"  Loaded {len(labels)} labels, {len(definitions)} definitions from URL")
        _FULL_ONTOLOGY_URL_CACHE = {'labels': labels, 'definitions': definitions}
        return _FULL_ONTOLOGY_URL_CACHE
    except Exception as e:
        print(f"  Warning: Failed to load full ontology from URL: {e}")
        return {}


def load_full_ontology_labels(ttl_path: Path) -> dict:
    """Load all labels from the full ontology TTL file."""
    global _FULL_ONTOLOGY_LABELS
    
    if _FULL_ONTOLOGY_LABELS is not None:
        return _FULL_ONTOLOGY_LABELS
    
    if not ttl_path.exists():
        print(f"  Warning: Full ontology file not found: {ttl_path}")
        return {}
    
    if not RDFLIB_AVAILABLE:
        print("  Warning: rdflib not available for full ontology parsing")
        return {}
    
    print(f"  Loading labels from full ontology: {ttl_path.name}")
    try:
        graph = Graph()
        graph.parse(str(ttl_path), format="turtle")
        
        labels = {}
        definitions = {}
        
        # Extract all labels
        for subj, _, obj in graph.triples((None, RDFS.label, None)):
            if isinstance(subj, URIRef) and isinstance(obj, Literal):
                uri = str(subj)
                lang = obj.language
                if lang == 'en' or lang is None:
                    labels[uri] = str(obj)
        
        # Extract definitions
        for subj, _, obj in graph.triples((None, SKOS.definition, None)):
            if isinstance(subj, URIRef) and isinstance(obj, Literal):
                uri = str(subj)
                lang = obj.language
                if lang == 'en' or lang is None:
                    definitions[uri] = str(obj)
        
        print(f"  Loaded {len(labels)} labels, {len(definitions)} definitions")
        _FULL_ONTOLOGY_LABELS = {'labels': labels, 'definitions': definitions}
        return _FULL_ONTOLOGY_LABELS
    except Exception as e:
        print(f"  Warning: Failed to load full ontology: {e}")
        return {}


def enrich_classes_from_full_ontology(classes: dict) -> None:
    """Enrich classes with labels/definitions from full ontology file.
    
    Uses full_ontology_path from navigator.yaml which can be a URL or local path.
    """
    script_dir = Path(__file__).parent
    config = load_NAVIGATOR_CONFIG(script_dir)
    
    # Get full_ontology_path from navigator.yaml
    full_ontology_path = config.get('full_ontology_path', '')
    
    if not full_ontology_path:
        # Fallback to local file
        ttl_path = script_dir.parent / "patterns" / "pmdco_full.ttl"
        full_data = load_full_ontology_labels(ttl_path)
    elif full_ontology_path.startswith('http://') or full_ontology_path.startswith('https://'):
        # Fetch from URL
        full_data = load_full_ontology_from_url(full_ontology_path)
    else:
        # Local path
        ttl_path = Path(full_ontology_path)
        if not ttl_path.is_absolute():
            ttl_path = script_dir.parent / full_ontology_path
        full_data = load_full_ontology_labels(ttl_path)
    
    if not full_data:
        return
    
    labels = full_data.get('labels', {})
    definitions = full_data.get('definitions', {})
    
    enriched_count = 0
    for uri, cls in classes.items():
        if not cls.label and uri in labels:
            cls.label = labels[uri]
            enriched_count += 1
        if not cls.definition and uri in definitions:
            cls.definition = definitions[uri]
    
    if enriched_count > 0:
        print(f"  Enriched {enriched_count} classes with labels from full ontology")


# Global cache for properties
_PROPERTY_CACHE = None

def load_property_data(script_dir: Path) -> Optional[dict]:
    """Load all properties (object, data, annotation) from the full ontology.

    Parses the PMD core ontology to extract all OWL property types along with
    their labels, definitions, and subproperty relationships. Results are
    cached globally to avoid repeated parsing.

    The ontology location is determined from navigator.yaml's full_ontology_path
    setting, which can be a URL or local file path.

    Args:
        script_dir: Path to the scripts directory for locating navigator.yaml.

    Returns:
        A dictionary containing:
        - 'object': Dict of object properties
        - 'data': Dict of data properties
        - 'annotation': Dict of annotation properties
        - 'relations': List of (child_uri, parent_uri) subproperty tuples
        Returns None if loading fails.

    Note:
        Requires rdflib to be installed for parsing.
    """
    global _PROPERTY_CACHE
    
    if _PROPERTY_CACHE is not None:
        return _PROPERTY_CACHE
    
    if not RDFLIB_AVAILABLE:
        print("  Warning: rdflib not available for property loading")
        return None
    
    config = load_NAVIGATOR_CONFIG(script_dir)
    full_ontology_path = config.get('full_ontology_path', '')
    
    try:
        graph = Graph()
        
        if not full_ontology_path:
            # Fallback to local file
            ttl_path = script_dir.parent / "patterns" / "pmdco_full.ttl"
            if not ttl_path.exists():
                print(f"  Warning: pmdco_full.ttl not found at {ttl_path}")
                return None
            print(f"  Loading properties from: {ttl_path.name}")
            graph.parse(str(ttl_path), format="turtle")
        elif full_ontology_path.startswith('http://') or full_ontology_path.startswith('https://'):
            # Fetch from URL
            print(f"  Loading properties from URL: {full_ontology_path}")
            req = urllib.request.Request(full_ontology_path, headers={"User-Agent": "PMDco-Doc-Builder/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                ttl_content = resp.read().decode('utf-8')
            graph.parse(data=ttl_content, format="turtle")
        else:
            # Local path from navigator.yaml
            ttl_path = Path(full_ontology_path)
            if not ttl_path.is_absolute():
                ttl_path = script_dir.parent / full_ontology_path
            if not ttl_path.exists():
                print(f"  Warning: Ontology file not found at {ttl_path}")
                return None
            print(f"  Loading properties from: {ttl_path.name}")
            graph.parse(str(ttl_path), format="turtle")
        
        object_props = {}
        data_props = {}
        annotation_props = {}
        subprop_relations = []
        
        # Extract object properties
        for s, _, _ in graph.triples((None, RDF.type, OWL.ObjectProperty)):
            uri = str(s)
            object_props[uri] = OntologyProperty(uri=uri, property_type="object")
        
        # Extract data properties
        for s, _, _ in graph.triples((None, RDF.type, OWL.DatatypeProperty)):
            uri = str(s)
            data_props[uri] = OntologyProperty(uri=uri, property_type="data")
        
        # Extract annotation properties
        for s, _, _ in graph.triples((None, RDF.type, OWL.AnnotationProperty)):
            uri = str(s)
            annotation_props[uri] = OntologyProperty(uri=uri, property_type="annotation")
        
        # Extract subproperty relations
        for s, _, o in graph.triples((None, RDFS.subPropertyOf, None)):
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                subprop_relations.append((str(s), str(o)))
        
        # Extract labels and definitions for all properties
        all_props = {**object_props, **data_props, **annotation_props}
        for uri, prop in all_props.items():
            uri_ref = URIRef(uri)
            for label in graph.objects(uri_ref, RDFS.label):
                if isinstance(label, Literal):
                    lang = label.language
                    if lang == 'en' or lang is None:
                        prop.label = str(label)
                        break
            for defn in graph.objects(uri_ref, SKOS.definition):
                if isinstance(defn, Literal):
                    lang = defn.language
                    if lang == 'en' or lang is None:
                        prop.definition = str(defn)
                        break
        
        print(f"  Found {len(object_props)} object, {len(data_props)} data, {len(annotation_props)} annotation properties")
        
        _PROPERTY_CACHE = {
            'object': object_props,
            'data': data_props,
            'annotation': annotation_props,
            'relations': subprop_relations
        }
        return _PROPERTY_CACHE
    except Exception as e:
        print(f"  Warning: Failed to load properties: {e}")
        return None


def build_property_tree(properties: dict, relations: list) -> List[OntologyProperty]:
    """Build a hierarchical tree structure from ontology properties.

    Creates a tree of OntologyProperty nodes from a flat dictionary of properties
    and their subproperty relationships. Properties without parents become roots.

    Args:
        properties: Dict mapping URIs to OntologyProperty instances.
        relations: List of (child_uri, parent_uri) tuples representing
            rdfs:subPropertyOf relationships.

    Returns:
        List of root OntologyProperty nodes with children populated recursively,
        sorted alphabetically by display name.
    """
    children_map = defaultdict(set)
    has_parent = set()
    
    for child_uri, parent_uri in relations:
        if child_uri in properties and parent_uri in properties:
            children_map[parent_uri].add(child_uri)
            has_parent.add(child_uri)
    
    def build_node(uri: str, visited: set) -> Optional[OntologyProperty]:
        if uri in visited or uri not in properties:
            return None
        visited.add(uri)
        source = properties[uri]
        node = OntologyProperty(uri=source.uri, label=source.label, 
                               definition=source.definition, property_type=source.property_type)
        for child_uri in sorted(children_map.get(uri, set())):
            child = build_node(child_uri, visited.copy())
            if child:
                node.children.append(child)
        node.children.sort(key=lambda x: x.display_name.lower())
        return node
    
    roots = []
    for uri in properties:
        if uri not in has_parent:
            node = build_node(uri, set())
            if node:
                roots.append(node)
    roots.sort(key=lambda x: x.display_name.lower())
    return roots


def count_property_nodes(roots: List[OntologyProperty]) -> int:
    """Count total number of nodes in a property tree.

    This is an alias for count_tree_nodes that accepts OntologyProperty roots.
    Both OntologyClass and OntologyProperty have compatible 'children' attributes.

    Args:
        roots: List of root OntologyProperty nodes.

    Returns:
        The total number of property nodes in the tree.
    """
    return count_tree_nodes(roots)  # Reuse generic tree counting


def generate_property_tree_html(roots: List[OntologyProperty], tree_id: str, title: str) -> str:
    """Generate interactive HTML for an ontology property tree.

    Creates a collapsible tree view similar to generate_tree_html but
    customized for property display with property-specific search placeholder.

    Args:
        roots: List of root OntologyProperty nodes with populated children.
        tree_id: Unique HTML ID for the tree container element.
        title: Display title for the property type (e.g., "Object Properties").

    Returns:
        Complete HTML string for the interactive property tree component.
    """
    prop_count = count_property_nodes(roots)
    
    def generate_node_html(node: OntologyProperty, depth: int) -> str:
        has_children = len(node.children) > 0
        has_definition = bool(node.definition)
        
        label = html_module.escape(node.display_name)
        prefix = html_module.escape(node.prefix)
        definition = html_module.escape(node.definition or '')
        uri = html_module.escape(node.uri)
        
        node_classes = ['tree-node']
        if has_definition:
            node_classes.append('has-definition')
        
        data_attrs = f'data-uri="{uri}"'
        if has_definition:
            data_attrs += f' data-definition="{definition}"'
        
        initially_collapsed = depth >= 1 and has_children
        toggle_class = 'collapsed' if initially_collapsed else 'expanded'
        children_class = 'collapsed' if initially_collapsed else ''
        
        parts = ['<li>']
        parts.append(f'<span class="{" ".join(node_classes)}" {data_attrs}>')
        
        if has_children:
            parts.append(f'<button class="tree-toggle {toggle_class}" aria-label="Toggle"></button>')
        else:
            parts.append('<span class="tree-toggle-placeholder"></span>')
        
        parts.append(f'<span class="tree-prefix">{prefix}:</span>')
        parts.append(f'<span class="tree-label">{label}</span>')
        parts.append('</span>')
        
        if has_children:
            parts.append(f'<ul class="tree-children {children_class}">')
            for child in node.children:
                parts.append(generate_node_html(child, depth + 1))
            parts.append('</ul>')
        
        parts.append('</li>')
        return ''.join(parts)
    
    html_parts = [f'''
    <div class="ontology-tree-container" id="{tree_id}" role="tree" aria-label="{title} hierarchy">
        <div class="tree-toolbar" role="toolbar" aria-label="Tree controls">
            <button class="tree-toolbar-btn tree-expand-all" aria-label="Expand all nodes">Expand All</button>
            <button class="tree-toolbar-btn tree-collapse-all" aria-label="Collapse all nodes">Collapse All</button>
            <input type="text" class="tree-search" id="{tree_id}-search" name="{tree_id}-search" placeholder="Search {title.lower()}..." aria-label="Search {title.lower()}">
            <span class="tree-stats" aria-live="polite">{prop_count} properties</span>
        </div>
        <ul class="ontology-tree" role="group">
    ''']
    
    for root in roots:
        html_parts.append(generate_node_html(root, 0))
    
    html_parts.append('</ul></div>')
    return ''.join(html_parts)


def process_property_indicators(html_content: str) -> str:
    """Process @property_indicator tags and replace with property trees.

    Finds all HTML comments matching <!--@property_indicator:TYPE--> where TYPE
    is 'object', 'data', or 'annotation', and replaces them with interactive
    property hierarchy trees loaded from the full ontology.

    Args:
        html_content: The HTML content containing @property_indicator tags.

    Returns:
        The HTML with all @property_indicator tags replaced by tree widgets,
        or warning messages if loading fails.
    """
    prop_counter = [0]
    
    def replace_indicator(match):
        prop_type = match.group(1).strip().lower()
        prop_counter[0] += 1
        tree_id = f"property-tree-{prop_type}-{prop_counter[0]}"
        
        script_dir = Path(__file__).parent
        prop_data = load_property_data(script_dir)
        
        if not prop_data:
            return f'<p class="warning">Failed to load properties from pmdco_full.ttl</p>'
        
        if prop_type not in prop_data:
            return f'<p class="warning">Unknown property type: {prop_type}</p>'
        
        properties = prop_data[prop_type]
        relations = prop_data['relations']
        
        roots = build_property_tree(properties, relations)
        if not roots:
            return f'<p class="warning">No {prop_type} properties found</p>'
        
        title_map = {'object': 'Object Properties', 'data': 'Data Properties', 'annotation': 'Annotation Properties'}
        tree_html = generate_property_tree_html(roots, tree_id, title_map.get(prop_type, 'Properties'))
        node_count = count_property_nodes(roots)
        print(f"  Generated {prop_type} property tree with {node_count} properties")
        return tree_html
    
    return PROPERTY_INDICATOR_RE.sub(replace_indicator, html_content)


def strip_document_indicator(md_text: str) -> str:
    """Remove @Document_indicator placeholder comments from markdown.

    The @Document_indicator tag is used as a marker in markdown files but
    should not appear in the final rendered output.

    Args:
        md_text: The markdown text potentially containing Document_indicator tags.

    Returns:
        The markdown text with all Document_indicator comments removed.
    """
    return DOCUMENT_INDICATOR_RE.sub("", md_text)


# ---- URL content cache (shared across all renderers within a build) --------
_URL_CONTENT_CACHE: Dict[str, Optional[str]] = {}


def fetch_remote_content(url: str) -> Optional[str]:
    """Fetch text content from a remote URL with caching and error handling.

    Returns the decoded text on success, or *None* on any failure.
    Results (including failures) are cached for the duration of the build so
    that the same URL is never fetched twice.
    """
    if url in _URL_CONTENT_CACHE:
        return _URL_CONTENT_CACHE[url]

    try:
        print(f"    Fetching remote content: {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "PMDco-Doc-Builder/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8")
        print(f"    Fetched {len(content)} bytes")
        _URL_CONTENT_CACHE[url] = content
        return content
    except Exception as exc:
        print(f"    Warning: Failed to fetch {url}: {exc}")
        _URL_CONTENT_CACHE[url] = None
        return None


def _detect_language_from_url(url: str) -> str:
    """Infer a code-block language hint from the file extension in *url*."""
    path = urllib.parse.urlparse(url).path.lower()
    ext_map = {
        ".ttl": "turtle",
        ".rdf": "xml",
        ".owl": "xml",
        ".xml": "xml",
        ".json": "json",
        ".jsonld": "json",
        ".py": "python",
        ".sparql": "sparql",
        ".rq": "sparql",
        ".md": "markdown",
    }
    for ext, lang in ext_map.items():
        if path.endswith(ext):
            return lang
    return ""


def process_md_file_renderers(md_text: str) -> str:
    """Process ``@md_file_renderer`` tags **before** markdown-to-HTML conversion.

    Each tag is replaced with the raw markdown content fetched from the
    specified URL so that it becomes part of the surrounding document and is
    rendered together with the rest of the page.
    """
    def _replace(match: re.Match) -> str:
        url = match.group(1).strip()
        content = fetch_remote_content(url)
        if content is None:
            return (
                f'\n\n> **Warning:** Could not load markdown file from '
                f'[{url}]({url})\n\n'
            )
        print(f"    Injected markdown from {url} ({len(content)} chars)")
        # Return fetched markdown as-is; it will be rendered with the rest
        return f"\n\n{content}\n\n"

    return MD_FILE_RENDERER_RE.sub(_replace, md_text)


def process_source_code_renderers(md_text: str) -> str:
    """Process ``@source_code_renderer`` tags **before** markdown-to-HTML conversion.

    Each tag is replaced with the remote file content wrapped inside a fenced
    code block so that the build's normal markdown pipeline renders it as a
    styled ``<pre><code>`` element.
    """
    def _replace(match: re.Match) -> str:
        url = match.group(1).strip()
        content = fetch_remote_content(url)
        if content is None:
            return (
                f'\n\n> **Warning:** Could not load source file from '
                f'[{url}]({url})\n\n'
            )
        lang = _detect_language_from_url(url)
        # Derive a short filename for the summary label
        filename = urllib.parse.unquote(url.rsplit("/", 1)[-1]) if "/" in url else url
        print(f"    Injected source code from {url} ({len(content)} chars)")
        return f"\n\n```{lang}\n{content}\n```\n\n"

    return SOURCE_CODE_RENDERER_RE.sub(_replace, md_text)


def extract_title_from_html(article_html: str) -> str:
    """Extract the first H1 title from rendered HTML content.

    Searches for the first <h1> tag in the HTML and extracts its text content,
    stripping any nested HTML tags.

    Args:
        article_html: The rendered HTML content to search.

    Returns:
        The text content of the first H1 heading, or "Documentation" if no
        H1 heading is found.
    """
    m = re.search(r"<h1[^>]*>([\s\S]*?)</h1>", article_html, re.IGNORECASE)
    if m:
        return _strip_html_tags(m.group(1))
    return "Documentation"


def build_page_nav(prev_page: Optional[Tuple[str, str]] = None, 
                   next_page: Optional[Tuple[str, str]] = None) -> str:
    """Build page navigation HTML."""
    if not prev_page and not next_page:
        return ""
    
    nav_html = '<nav class="page-nav">\n'
    
    if prev_page:
        nav_html += f'''                <a class="page-nav-link prev" href="{prev_page[0]}">
                    <span class="page-nav-label">&larr; Previous</span>
                    <span class="page-nav-title">{prev_page[1]}</span>
                </a>\n'''
    else:
        nav_html += '                <div></div>\n'
    
    if next_page:
        nav_html += f'''                <a class="page-nav-link next" href="{next_page[0]}">
                    <span class="page-nav-label">Next &rarr;</span>
                    <span class="page-nav-title">{next_page[1]}</span>
                </a>\n'''
    else:
        nav_html += '                <div></div>\n'
    
    nav_html += '            </nav>'
    return nav_html


# Docs mode template - same as patterns but without diagram placeholders
# Docs mode template - same as patterns but without diagram placeholders by default
# Manual diagrams can still be embedded and will be processed
DOCS_TEMPLATE_HTML = (
    TEMPLATE_HTML
    .replace("__DIAGRAMS_OBJECT__", "{}")
    .replace("__NODEDATA_OBJECT__", "{}")
    .replace("__MERMAID_DIAGRAMS_OBJECT__", "{}")
)


def build_doc_html(
    markdown_path: Path,
    out_html: Path,
    page_title: Optional[str] = None,
    prev_page: Optional[Tuple[str, str]] = None,
    next_page: Optional[Tuple[str, str]] = None,
    active_nav: Optional[str] = None,
) -> None:
    """Build an HTML documentation page from markdown (docs mode).

    This is the main build function for standard documentation pages that do not
    contain @Graphviz_renderer tags. It processes special indicators like
    @module_indicator and @property_indicator to generate interactive trees.

    Supported markdown extensions:
    - @module_indicator:URL - Generates class hierarchy tree from OWL file
    - @property_indicator:TYPE - Generates property tree (object/data/annotation)
    - @md_file_renderer:URL - Injects remote markdown content
    - @source_code_renderer:URL - Injects remote source code in code block
    - @Graphviz_renderer_manual:TITLE - Render embedded DOT code
    - @Mermaid_renderer_manual:TITLE - Render embedded Mermaid code

    Args:
        markdown_path: Path to the source markdown file.
        out_html: Path where the output HTML file will be written.
        page_title: Optional page title. If not provided, extracted from first H1.
        prev_page: Optional (href, title) tuple for previous page navigation.
        next_page: Optional (href, title) tuple for next page navigation.
        active_nav: Optional identifier for the active navigation item.
    """
    md_text_raw = markdown_path.read_text(encoding="utf-8")

    # Strip document indicator
    md_text = strip_document_indicator(md_text_raw)

    # Process @md_file_renderer / @source_code_renderer before markdown conversion
    if MD_FILE_RENDERER_RE.search(md_text):
        print("  Processing @md_file_renderer tags...")
        md_text = process_md_file_renderers(md_text)
    if SOURCE_CODE_RENDERER_RE.search(md_text):
        print("  Processing @source_code_renderer tags...")
        md_text = process_source_code_renderers(md_text)

    # Parse manual diagram references (embedded DOT/Mermaid code)
    manual_refs = parse_manual_diagram_refs(md_text, _fallback_slugify)
    if manual_refs:
        print(f"  Found {len(manual_refs)} manual diagram(s)")
        md_text = inject_manual_graph_containers(md_text, manual_refs)

    # Render markdown to HTML
    article_html = render_markdown(md_text).strip()

    # Process @module_indicator tags and generate ontology trees
    if MODULE_INDICATOR_RE.search(article_html):
        print("  Processing @module_indicator tags...")
        article_html = process_module_indicators(article_html)

    # Process @property_indicator tags and generate property trees
    if PROPERTY_INDICATOR_RE.search(article_html):
        print("  Processing @property_indicator tags...")
        article_html = process_property_indicators(article_html)

    # Extract title if not provided
    if not page_title:
        page_title = extract_title_from_html(article_html)

    # Build TOC
    toc_items = build_toc_list_items(article_html)

    # Build page navigation
    page_nav = build_page_nav(prev_page, next_page)

    # Build diagram objects for manual diagrams
    def _simple_js_escape(s: str) -> str:
        s = s.replace("\\", "\\\\")
        s = s.replace("`", "\\`")
        s = s.replace("${", "\\${")
        return s

    dot_diagrams: Dict[str, str] = {}
    mermaid_diagrams: Dict[str, str] = {}
    for ref in manual_refs:
        if ref.diagram_type == 'graphviz':
            dot_diagrams[ref.diagram_id] = ref.code
            print(f"    Added manual Graphviz diagram: {ref.diagram_id}")
        else:
            mermaid_diagrams[ref.diagram_id] = ref.code
            print(f"    Added manual Mermaid diagram: {ref.diagram_id}")

    # Build JS objects for diagrams
    dot_obj = build_dot_diagrams_object(dot_diagrams, _simple_js_escape) if dot_diagrams else "{}"
    mermaid_obj = build_mermaid_diagrams_object(mermaid_diagrams, _simple_js_escape) if mermaid_diagrams else "{}"
    node_obj = "{}"  # No node data for manual diagrams

    # Use full template if we have manual diagrams, otherwise use docs template
    if manual_refs:
        html_out = TEMPLATE_HTML
        html_out = html_out.replace("__DIAGRAMS_OBJECT__", dot_obj)
        html_out = html_out.replace("__NODEDATA_OBJECT__", node_obj)
        html_out = html_out.replace("__MERMAID_DIAGRAMS_OBJECT__", mermaid_obj)
    else:
        html_out = DOCS_TEMPLATE_HTML

    html_out = html_out.replace("__ARTICLE_CONTENT__", article_html)
    html_out = html_out.replace("__TOC_LIST_ITEMS__", toc_items)

    # Generate dynamic sidebar from navigator.yaml
    active_page = out_html.name  # Use output filename to determine active page
    sidebar_html = generate_sidebar_html(active_page=active_page, script_dir=Path(__file__).parent)
    html_out = html_out.replace("__SIDEBAR_HTML__", sidebar_html)

    # Generate dynamic page navigation from navigator.yaml
    page_nav_html = generate_page_nav_html(active_page=active_page, script_dir=Path(__file__).parent)
    html_out = html_out.replace("__PAGE_NAV__", page_nav_html)

    # Write output
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html_out, encoding="utf-8")
    print(f"Generated: {out_html} ({out_html.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    raise SystemExit(main())

