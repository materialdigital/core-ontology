# build_all.py - Complete Technical Documentation

**Version:** 1.0  
**Date:** January 11, 2026  
**File:** `build_all.py`  
**Location:** `c:\Users\potu\Desktop\PMD\PMD_Docs_Presentation\docs\docs_HTML\scripts\build_all.py`

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Dependencies & Requirements](#dependencies--requirements)
4. [File Structure & Organization](#file-structure--organization)
5. [Configuration Files](#configuration-files)
6. [Core Components](#core-components)
7. [Build Modes](#build-modes)
8. [HTML Generation Process](#html-generation-process)
9. [Function Reference](#function-reference)
10. [Data Flow Diagrams](#data-flow-diagrams)
11. [Troubleshooting](#troubleshooting)

---

## 1. Overview

### Purpose
`build_all.py` is a **unified static site builder** for PMDco (Platform MaterialDigital Core Ontology) documentation. It combines the functionality of two separate builders (`build_docs.py` and `build_html.py`) into a single, comprehensive tool.

### What It Does
- Converts Markdown files to HTML with rich interactivity
- Generates interactive ontology class hierarchies from OWL files
- Creates property trees (object, data, annotation properties)
- Renders Graphviz diagrams from TTL/SHACL files
- Provides a dynamic sidebar, table of contents, search functionality, and theme toggle
- Supports both local and remote resource loading

### Key Features
1. **Two Build Modes:**
   - `docs`: Simple markdown documents with ontology trees
   - `patterns`: Pattern pages with Graphviz diagrams

2. **Smart Tag Processing:**
   - `@module_indicator`: Fetches OWL files and generates ontology class trees
   - `@property_indicator`: Generates property hierarchies
   - `@Graphviz_renderer`: Converts TTL files to interactive diagrams

3. **Auto-Detection:** Can automatically detect the appropriate mode based on content

---

## 2. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        build_all.py                              │
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Input Layer │───▶│ Processing   │───▶│ Output Layer │      │
│  │              │    │    Layer     │    │              │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                    │                   │              │
│    Markdown Files      Tag Processing       HTML Files         │
│    OWL/TTL Files       Tree Generation      CSS/JS Embedded    │
│    navigator.yaml      Diagram Rendering    Interactive UI     │
└─────────────────────────────────────────────────────────────────┘
```

### Component Relationships

```
build_all.py
├── Configuration Module
│   ├── load_NAVIGATOR_CONFIG()
│   ├── get_feather_icon_svg()
│   └── navigator.yaml (external)
│
├── Docs Mode Pipeline
│   ├── Markdown Parser (markdown2)
│   ├── @module_indicator processor
│   ├── @property_indicator processor
│   ├── OWL/RDF Parser (rdflib)
│   └── Tree Generators
│
├── Patterns Mode Pipeline
│   ├── Markdown Parser (markdown2)
│   ├── @Graphviz_renderer processor
│   ├── TTL Converter (ttl_to_graphviz.py)
│   └── Diagram Generators
│
├── HTML Template Engine
│   ├── TEMPLATE_HTML (embedded)
│   ├── Sidebar Generator
│   ├── TOC Generator
│   └── Navigation Generator
│
└── Utility Functions
    ├── File I/O
    ├── URL Fetching
    └── String Processing
```

---

## 3. Dependencies & Requirements

### Required Python Libraries

#### Standard Library (Built-in)
```python
import argparse          # Command-line argument parsing
import json              # JSON encoding/decoding
import re                # Regular expressions for pattern matching
import urllib.parse      # URL parsing and manipulation
import urllib.request    # URL fetching (HTTP requests)
import importlib.util    # Dynamic module importing
import sys               # System-specific parameters
import tempfile          # Temporary file creation
import html              # HTML escaping (imported as html_module)
from dataclasses import dataclass, field  # Data classes
from pathlib import Path                   # Object-oriented filesystem paths
from typing import Dict, List, Optional, Tuple, Any, Callable  # Type hints
from collections import defaultdict        # Default dictionaries
```

#### Third-Party Libraries (Must Install)

1. **markdown2** (REQUIRED)
   - Purpose: Convert Markdown to HTML
   - Install: `pip install markdown2`
   - Usage: Renders markdown with extensions (tables, code blocks, etc.)

2. **rdflib** (OPTIONAL but highly recommended)
   - Purpose: Parse RDF/OWL ontology files
   - Install: `pip install rdflib`
   - Usage: Extract class hierarchies, properties, labels from OWL/TTL files
   - Components used:
     - `Graph`: RDF graph operations
     - `Namespace`: URI namespace management
     - `RDF, RDFS, OWL, URIRef, Literal`: RDF vocabulary
     - `SKOS`: SKOS vocabulary (for definitions)

3. **pyyaml** (OPTIONAL but highly recommended)
   - Purpose: Parse YAML configuration files
   - Install: `pip install pyyaml`
   - Usage: Load `navigator.yaml` for sidebar/navigation structure

### External Dependencies

1. **ttl_to_graphviz.py**
   - Location: Same directory as `build_all.py`
   - Purpose: Convert TTL/SHACL files to Graphviz DOT format
   - Must have a class with `render_graph()` method
   - Expected to provide `slugify()` function

2. **navigator.yaml**
   - Location: `../../navigator.yaml` (relative to script)
   - Purpose: Define site structure, navigation, page mappings
   - Schema: Custom YAML format (see Configuration Files section)

3. **Full Ontology File** (optional)
   - Location: Configurable via `navigator.yaml`
   - Default: `https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/src/ontology/pmdco.ttl`
   - Purpose: Enrich classes with labels and definitions
   - Can be local file or remote URL

---

## 4. File Structure & Organization

### Directory Layout

```
c:\Users\potu\Desktop\PMD\PMD_Docs_Presentation\docs\
│
├── navigator.yaml                    # Site structure configuration
├── index.md                          # Homepage markdown
├── patterns.md                       # Patterns page (uses @Graphviz_renderer)
├── intro.md                          # Various content pages
├── *.md                              # Other markdown files
│
├── docs_HTML/
│   ├── scripts/
│   │   ├── build_all.py              # THIS FILE - Main builder
│   │   ├── run_all.py                # Batch runner (calls build_all.py)
│   │   ├── ttl_to_graphviz.py        # TTL→DOT converter
│   │   ├── generate_ontology_tree.py # (may exist separately)
│   │   └── generate_property_tree.py # (may exist separately)
│   │
│   └── HTML_Docs/                    # OUTPUT DIRECTORY
│       ├── index.html                # Generated HTML files
│       ├── patterns.html
│       ├── intro.html
│       ├── *.html
│       ├── Logo.svg                  # Copied assets
│       └── search-index.json         # Search index
│
└── patterns/                         # Pattern TTL files (for local diagrams)
    ├── temporal region/
    │   └── shape-data.ttl
    └── [other patterns]/
```

### File Naming Conventions

- **Markdown files:** `*.md` (can have spaces, e.g., `Introduction to Ontologies.md`)
- **HTML output:** `*.html` (lowercase with hyphens, e.g., `introduction-to-ontologies.html`)
- **TTL files:** `shape-data.ttl`, `shape_data.ttl`, or similar patterns
- **DOT files:** `*.dot` (alternative to TTL for pre-rendered diagrams)

---

## 5. Configuration Files

### navigator.yaml

**Purpose:** Single source of truth for website structure, navigation, and page mappings

**Location:** `c:\Users\potu\Desktop\PMD\PMD_Docs_Presentation\docs\navigator.yaml`

**Schema:**
```yaml
schema: "pmdco-nav/v1"

defaults:
  icons:
    - file-text
    - document
    - compass
    # ... rotating icons for pages without specific icons

full_ontology_path: "https://raw.githubusercontent.com/.../pmdco.ttl"
# Can be URL or local path (relative to navigator.yaml)

icons:
  # Feather icon definitions (SVG path data)
  home:
    path: "M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z M9 22V12h6v10"
  # ... more icon definitions

sections:
  - id: getting-started
    title: "Getting Started"
    icon: home
    pages:
      - title: Home
        href: index.html          # OUTPUT filename
        md: index.md              # INPUT markdown file
        icon: home
      
      - title: Introduction
        href: intro.html
        md: intro.md
        icon: info
  
  # ... more sections
```

**Key Fields:**
- `sections[].pages[].href`: Output HTML filename (what user sees in browser)
- `sections[].pages[].md`: Input markdown filename (source file)
- `full_ontology_path`: URL or path to full ontology for label enrichment

---

## 6. Core Components

### 6.1 Configuration & Navigation System

#### Global Variables
```python
_NAVIGATOR_CONFIG = None         # Cached navigator.yaml content
_FULL_ONTOLOGY_LABELS = None     # Cached ontology labels (local file)
_FULL_ONTOLOGY_URL_CACHE = None  # Cached ontology labels (from URL)
_PROPERTY_CACHE = None           # Cached property data
```

#### load_NAVIGATOR_CONFIG()
**Purpose:** Load and cache the navigator.yaml configuration

**Process:**
1. Check if already cached → return cached version
2. Locate navigator.yaml (2 levels up from script directory)
3. Parse YAML content
4. Cache result
5. Return dictionary

**Used By:**
- `generate_sidebar_html()`
- `generate_page_nav_html()`
- `generate_search_index_json()`
- Property/class enrichment functions

---

### 6.2 Sidebar Generation

#### generate_sidebar_html(active_page, script_dir)
**Purpose:** Generate dynamic sidebar navigation HTML

**Input:**
- `active_page`: Current page filename (e.g., "patterns.html")
- `script_dir`: Path to script directory

**Process:**
1. Load navigator.yaml configuration
2. Iterate through sections and pages
3. Generate HTML structure:
   - Section headers with icons
   - Page links with active state
   - Collapsible sections
4. Return complete sidebar HTML string

**Output Example:**
```html
<nav class="nav-sections">
  <div class="nav-section">
    <h3 class="nav-section-title">
      <svg>...</svg> Getting Started
    </h3>
    <ul>
      <li><a class="nav-link active" href="./index.html">
        <svg>...</svg> Home
      </a></li>
      <!-- more pages -->
    </ul>
  </div>
  <!-- more sections -->
</nav>
```

---

### 6.3 Page Navigation (Prev/Next)

#### generate_page_nav_html(active_page, script_dir)
**Purpose:** Generate previous/next page navigation

**Process:**
1. Load navigator.yaml
2. Flatten all pages into ordered list
3. Find current page index
4. Get previous and next pages
5. Build navigation HTML with arrows

**Output Example:**
```html
<nav class="page-nav">
  <a class="page-nav-link prev" href="./intro.html">
    <span class="page-nav-label">← Previous</span>
    <span class="page-nav-title">Introduction</span>
  </a>
  <a class="page-nav-link next" href="./patterns.html">
    <span class="page-nav-label">Next →</span>
    <span class="page-nav-title">Usage Patterns</span>
  </a>
</nav>
```

---

### 6.4 Search Index Generation

#### generate_search_index_json(script_dir)
**Purpose:** Create a search index for all pages

**Process:**
1. Load navigator.yaml
2. Extract all page entries
3. For each page:
   - Extract title, href
   - Parse content headings
4. Build JSON structure:
   ```json
   [
     {
       "title": "Introduction",
       "href": "./intro.html",
       "section": "Getting Started",
       "headings": ["Overview", "Key Concepts"]
     }
   ]
   ```

---

## 7. Build Modes

### 7.1 DOCS MODE

**When Used:**
- Default for most pages
- Pages with `@module_indicator` or `@property_indicator` tags
- No `@Graphviz_renderer` tags present

**Processing Pipeline:**

```
Input: Markdown File
  ↓
Strip @Document_indicator tags
  ↓
Convert Markdown → HTML (markdown2)
  ↓
Process @module_indicator tags
  ├─→ Fetch OWL file from URL
  ├─→ Parse OWL content (rdflib or functional syntax parser)
  ├─→ Extract class hierarchy
  ├─→ Enrich with labels from full ontology
  ├─→ Build tree structure
  └─→ Generate interactive HTML tree
  ↓
Process @property_indicator tags
  ├─→ Load full ontology (pmdco.ttl)
  ├─→ Extract properties (object/data/annotation)
  ├─→ Extract subproperty relations
  ├─→ Build property hierarchy
  └─→ Generate interactive HTML tree
  ↓
Extract title from first H1
  ↓
Build Table of Contents from H2/H3
  ↓
Generate sidebar (from navigator.yaml)
  ↓
Generate page navigation (prev/next)
  ↓
Insert into HTML template
  ↓
Output: Complete HTML file
```

**Entry Point:**
```python
build_doc_html(
    markdown_path=Path,      # Input .md file
    out_html=Path,           # Output .html file
    page_title=str,          # Optional title override
    prev_page=tuple,         # ("href", "title")
    next_page=tuple,         # ("href", "title")
    active_nav=str           # Active nav item
)
```

---

### 7.2 PATTERNS MODE

**When Used:**
- Pages with `@Graphviz_renderer` tags
- Specifically for `patterns.html`

**Processing Pipeline:**

```
Input: Markdown File
  ↓
Parse @Graphviz_renderer tags
  ├─→ Extract URLs/paths to TTL files
  ├─→ Extract diagram titles (from preceding H2)
  └─→ Generate diagram IDs (slugified folder names)
  ↓
Strip D2 code blocks (if any)
  ↓
Inject graph container placeholders
  ↓
Convert Markdown → HTML (markdown2)
  ↓
Wrap code blocks in collapsible <details>
  ↓
Resolve diagram sources
  ├─→ For each TTL file:
  │   ├─→ If remote URL: Download content
  │   ├─→ If local: Find shape-data.ttl file
  │   ├─→ Call ttl_to_graphviz.py converter
  │   ├─→ Get DOT source and node metadata
  │   └─→ Store in diagrams dictionary
  ↓
Build JavaScript objects
  ├─→ dotDiagrams: {diagram_id: "DOT source"}
  └─→ nodeData: {diagram_id: {node_id: metadata}}
  ↓
Build Table of Contents
  ↓
Generate sidebar
  ↓
Generate page navigation
  ↓
Insert into HTML template
  ├─→ Replace __ARTICLE_CONTENT__
  ├─→ Replace __DIAGRAMS_OBJECT__
  ├─→ Replace __NODEDATA_OBJECT__
  ├─→ Replace __SIDEBAR_HTML__
  └─→ Replace __PAGE_NAV__
  ↓
Output: Complete HTML with embedded diagrams
```

**Entry Point:**
```python
build_html(
    markdown_path=Path,           # Input .md file
    diagrams_root=Path,           # Root dir for TTL files
    out_html=Path,                # Output .html file
    converter_path=Path,          # Path to ttl_to_graphviz.py
    strict=bool,                  # Fail on missing diagrams?
    write_per_pattern_js=bool     # Write individual .js files?
)
```

---

## 8. HTML Generation Process

### 8.1 Template Structure

The HTML template (`TEMPLATE_HTML`) is a ~3,500 line string containing:

1. **Document Head:**
   - Meta tags (charset, viewport, description)
   - Title
   - Google Fonts links
   - Embedded CSS (~2,000 lines)

2. **Document Body:**
   - Header with logo, search, theme toggle
   - Sidebar (placeholder: `__SIDEBAR_HTML__`)
   - Main content area (placeholder: `__ARTICLE_CONTENT__`)
   - Table of contents (placeholder: `__TOC_LIST_ITEMS__`)
   - Page navigation (placeholder: `__PAGE_NAV__`)
   - Embedded JavaScript (~1,500 lines)

3. **CSS Sections:**
   - CSS variables (colors, spacing, fonts)
   - Theme switching (light/dark mode)
   - Layout (grid, flexbox)
   - Component styles (sidebar, TOC, trees, diagrams)
   - Responsive design (mobile, tablet, desktop)
   - Print styles

4. **JavaScript Sections:**
   - Sidebar toggle (mobile)
   - Theme persistence (localStorage)
   - TOC active section highlighting
   - Search functionality
   - Ontology tree interactions
   - Graphviz diagram rendering (Viz.js)
   - Pan/zoom controls
   - Export functions (SVG, PNG)

### 8.2 Placeholder Replacement

The template uses these placeholders:

| Placeholder             | Replaced With                          | Mode    |
|-------------------------|----------------------------------------|---------|
| `__ARTICLE_CONTENT__`   | Processed markdown HTML                | Both    |
| `__TOC_LIST_ITEMS__`    | Table of contents `<li>` elements      | Both    |
| `__SIDEBAR_HTML__`      | Generated sidebar navigation           | Both    |
| `__PAGE_NAV__`          | Previous/next page links               | Both    |
| `__DIAGRAMS_OBJECT__`   | JavaScript object with DOT sources     | Patterns|
| `__NODEDATA_OBJECT__`   | JavaScript object with node metadata   | Patterns|

**Replacement Process:**
```python
html_out = TEMPLATE_HTML
html_out = html_out.replace("__ARTICLE_CONTENT__", article_html)
html_out = html_out.replace("__TOC_LIST_ITEMS__", toc_items)
html_out = html_out.replace("__SIDEBAR_HTML__", sidebar_html)
html_out = html_out.replace("__PAGE_NAV__", page_nav_html)
# Patterns mode only:
html_out = html_out.replace("__DIAGRAMS_OBJECT__", dot_obj)
html_out = html_out.replace("__NODEDATA_OBJECT__", node_obj)
```

### 8.3 CSS Architecture

**Design System:**
- CSS Custom Properties (variables) for theming
- BEM-like naming conventions
- Mobile-first responsive design
- Print-optimized styles

**Key CSS Variables:**
```css
:root {
  --color-primary: #00a0e3;
  --color-bg-primary: #f7f9fc;
  --color-text-primary: #0f172a;
  /* ~50 more variables */
}

body.theme-dark {
  /* Dark mode overrides */
  --color-bg-primary: #0f172a;
  --color-text-primary: #f1f5f9;
  /* ... */
}
```

**Component Hierarchy:**
```
body
├── .header
│   ├── .logo
│   ├── .search-container
│   └── .theme-toggle
├── .sidebar
│   └── .nav-sections
│       └── .nav-section
│           ├── .nav-section-title
│           └── ul → .nav-link
├── .main-wrapper
│   ├── .content
│   │   └── article (markdown content)
│   └── .toc
└── .page-nav (prev/next links)
```

---

## 9. Function Reference

### 9.1 Navigation Functions

#### `get_feather_icon_svg(icon_name, navigator_config)`
- **Purpose:** Generate SVG markup for Feather icons
- **Input:** Icon name (str), navigator config (dict)
- **Output:** SVG string
- **Example:**
  ```python
  svg = get_feather_icon_svg("home", config)
  # Returns: '<svg fill="none" ...><path d="..."></path></svg>'
  ```

#### `load_NAVIGATOR_CONFIG(script_dir)`
- **Purpose:** Load and cache navigator.yaml
- **Input:** Script directory path (optional)
- **Output:** Dictionary with sections, pages, icons
- **Caching:** Results cached in `_NAVIGATOR_CONFIG` global

#### `generate_sidebar_html(active_page, script_dir)`
- **Purpose:** Generate sidebar navigation
- **Input:** Active page filename, script directory
- **Output:** HTML string for sidebar
- **Features:**
  - Hierarchical sections
  - Active page highlighting
  - Icon support
  - Fallback to hardcoded structure

#### `generate_page_nav_html(active_page, script_dir)`
- **Purpose:** Generate prev/next navigation
- **Input:** Active page filename, script directory
- **Output:** HTML string for page navigation
- **Logic:**
  - Flattens all pages from navigator.yaml
  - Finds current page index
  - Gets adjacent pages
  - Builds navigation links

#### `generate_search_index_json(script_dir)`
- **Purpose:** Create JSON search index
- **Input:** Script directory
- **Output:** JSON string
- **Structure:**
  ```json
  [
    {
      "title": "Page Title",
      "href": "./page.html",
      "section": "Section Name",
      "headings": ["H2", "H3"]
    }
  ]
  ```

---

### 9.2 Docs Mode Functions

#### `fetch_owl_file(url)`
- **Purpose:** Download OWL file from URL
- **Input:** URL string
- **Output:** OWL content (string) or None
- **Features:**
  - Custom User-Agent
  - 30-second timeout
  - Error handling

#### `parse_owl_functional_syntax(owl_content)`
- **Purpose:** Parse OWL Functional Syntax
- **Input:** OWL content string
- **Output:** Dictionary with classes, child_map, parent_map
- **Process:**
  1. Extract prefix declarations
  2. Parse Declaration(Class(...))
  3. Parse SubClassOf relations
  4. Parse AnnotationAssertion (labels)
  5. Build class hierarchy maps

#### `parse_owl_content(owl_content)`
- **Purpose:** Parse OWL (auto-detect format)
- **Input:** OWL content string
- **Output:** Dictionary with classes, child_map, parent_map
- **Formats Supported:**
  - Functional Syntax (if starts with "Prefix(")
  - RDF/XML (via rdflib)
  - Turtle (via rdflib)

#### `build_tree(classes, child_map, parent_map)`
- **Purpose:** Build tree structure from flat class data
- **Input:** Classes dict, child map, parent map
- **Output:** List of root OntologyClass nodes
- **Algorithm:**
  1. Identify root classes (no parents)
  2. Recursively build child nodes
  3. Sort alphabetically at each level
  4. Avoid circular references (visited set)

#### `generate_tree_html(roots, tree_id)`
- **Purpose:** Generate HTML for ontology tree
- **Input:** Root nodes, tree ID
- **Output:** HTML string
- **Features:**
  - Collapsible nodes
  - Tooltips with definitions
  - Search functionality
  - Expand/collapse all buttons
  - Depth-based initial state

#### `process_module_indicators(html_content)`
- **Purpose:** Replace @module_indicator tags with trees
- **Input:** HTML content
- **Output:** HTML with embedded ontology trees
- **Process:**
  1. Find all `<!--@module_indicator:URL-->` tags
  2. For each tag:
     - Fetch OWL file
     - Parse content
     - Enrich with labels
     - Build tree
     - Generate HTML
     - Replace tag with tree HTML

#### `load_full_ontology_labels(ttl_path)`
- **Purpose:** Load labels from full ontology file
- **Input:** Path to pmdco.ttl
- **Output:** Dictionary with labels and definitions
- **Caching:** Results cached in `_FULL_ONTOLOGY_LABELS`
- **Uses:** rdflib to parse TTL and extract RDFS labels, SKOS definitions

#### `load_full_ontology_from_url(url)`
- **Purpose:** Load labels from remote ontology URL
- **Input:** URL to TTL file
- **Output:** Dictionary with labels and definitions
- **Caching:** Results cached in `_FULL_ONTOLOGY_URL_CACHE`
- **Timeout:** 60 seconds

#### `enrich_classes_from_full_ontology(classes)`
- **Purpose:** Add labels/definitions to classes
- **Input:** Classes dictionary (modified in-place)
- **Output:** None (modifies input)
- **Process:**
  1. Load full ontology (from URL or file)
  2. Match class URIs
  3. Add missing labels and definitions

#### `load_property_data(script_dir)`
- **Purpose:** Load all properties from ontology
- **Input:** Script directory
- **Output:** Dictionary with object, data, annotation properties
- **Caching:** Results cached in `_PROPERTY_CACHE`
- **Process:**
  1. Load full ontology
  2. Extract properties by type (rdf:type)
  3. Extract subPropertyOf relations
  4. Extract labels and definitions

#### `build_property_tree(properties, relations)`
- **Purpose:** Build property hierarchy
- **Input:** Properties dict, relations list
- **Output:** List of root OntologyProperty nodes
- **Similar to:** `build_tree()` but for properties

#### `generate_property_tree_html(roots, tree_id, title)`
- **Purpose:** Generate HTML for property tree
- **Input:** Root nodes, tree ID, title
- **Output:** HTML string
- **Similar to:** `generate_tree_html()` but customized for properties

#### `process_property_indicators(html_content)`
- **Purpose:** Replace @property_indicator tags with trees
- **Input:** HTML content
- **Output:** HTML with embedded property trees
- **Process:**
  1. Find all `<!--@property_indicator:TYPE-->` tags
  2. For each tag:
     - Load property data
     - Filter by type (object/data/annotation)
     - Build tree
     - Generate HTML
     - Replace tag with tree HTML

#### `build_doc_html(...)`
- **Purpose:** Main entry point for docs mode
- **Input:**
  - `markdown_path`: Input .md file
  - `out_html`: Output .html file
  - `page_title`: Optional title override
  - `prev_page`: (href, title) tuple
  - `next_page`: (href, title) tuple
  - `active_nav`: Active nav item
- **Output:** Writes HTML file
- **Process:**
  1. Read markdown
  2. Strip document indicators
  3. Render markdown to HTML
  4. Process @module_indicator tags
  5. Process @property_indicator tags
  6. Extract title
  7. Build TOC
  8. Generate sidebar
  9. Generate page navigation
  10. Replace template placeholders
  11. Write output file

---

### 9.3 Patterns Mode Functions

#### `strip_d2_blocks(md_text)`
- **Purpose:** Remove D2 diagram code blocks
- **Input:** Markdown text
- **Output:** Markdown without D2 blocks
- **Pattern:** ````d2...```

#### `render_markdown(md_text)`
- **Purpose:** Convert markdown to HTML
- **Input:** Markdown text
- **Output:** HTML string
- **Extras:**
  - fenced-code-blocks
  - tables
  - header-ids
  - cuddled-lists
  - strike
  - code-friendly

#### `wrap_code_in_details(html)`
- **Purpose:** Wrap code blocks in collapsible sections
- **Input:** HTML string
- **Output:** HTML with `<details>` wrapped code
- **Pattern:**
  ```html
  <details class="code-block">
    <summary>📄 View pattern code</summary>
    <pre><code>...</code></pre>
  </details>
  ```

#### `build_toc_list_items(article_html)`
- **Purpose:** Extract H2/H3 headings for TOC
- **Input:** Article HTML
- **Output:** `<li>` elements string
- **Format:**
  ```html
  <li><a href="#heading-id">H2 Title</a></li>
  <li class="toc-h3"><a href="#sub-heading">H3 Title</a></li>
  ```

#### `parse_diagram_refs(md_text, slugify_fn)`
- **Purpose:** Extract @Graphviz_renderer tags
- **Input:** Markdown text, slugify function
- **Output:** List of DiagramRef objects
- **Process:**
  1. Track current H2 heading (for diagram title)
  2. Find all `<!--@Graphviz_renderer:PATH-->` tags
  3. For each tag:
     - Extract path/URL
     - Decode URL-encoded paths
     - Extract folder name for diagram ID
     - Use slugify function for ID
     - Create DiagramRef with (id, path, title)

#### `inject_graph_containers(md_text, refs)`
- **Purpose:** Replace @Graphviz_renderer tags with containers
- **Input:** Markdown text, diagram references
- **Output:** Markdown with embedded containers
- **Container Structure:**
  ```html
  <div class="mermaid-graph-container" id="graph-{id}">
    <div class="graph-header">
      <div class="graph-title">{title}</div>
      <div class="graph-controls">...</div>
    </div>
    <div class="graph-viewport">
      <div class="graph-wrapper" id="wrapper-{id}">
        <div class="mermaid-diagram" id="diagram-{id}"></div>
      </div>
    </div>
    <div class="graph-legend">...</div>
  </div>
  ```

#### `_dynamic_import_from_path(py_path, module_name)`
- **Purpose:** Dynamically import Python module
- **Input:** Path to .py file, module name
- **Output:** Imported module object
- **Use Case:** Load ttl_to_graphviz.py at runtime

#### `_find_converter_class(mod)`
- **Purpose:** Find converter class in module
- **Input:** Module object
- **Output:** Converter class
- **Logic:**
  - Look for classes with `render_graph()` method
  - Prefer classes with "Renderer" or "Diagram" in name

#### `_find_shape_ttl(pattern_dir)`
- **Purpose:** Locate TTL file in pattern directory
- **Input:** Pattern directory path
- **Output:** Path to TTL file or None
- **Search Pattern:**
  1. shape_data.ttl
  2. shape-data.ttl
  3. shape data.ttl
  4. Glob for shape*data*.ttl

#### `_resolve_diagram_sources(...)`
- **Purpose:** Convert TTL files to DOT diagrams
- **Input:**
  - `refs`: List of diagram references
  - `diagrams_root`: Root directory for local files
  - `converter_path`: Path to ttl_to_graphviz.py
  - `strict`: Fail on errors?
  - `write_per_pattern_js`: Write individual JS files?
- **Output:** Tuple of (diagrams dict, node_data dict, js_escape function)
- **Process:**
  1. Load and instantiate converter
  2. For each diagram reference:
     - If remote URL: Download TTL content
     - If local: Find shape-data.ttl file
     - Call converter.render_graph()
     - Extract DOT source and node metadata
     - Store in dictionaries
     - Optionally write per-pattern JS file
  3. Return diagrams and metadata

#### `build_dot_diagrams_object(diagrams, js_escape)`
- **Purpose:** Build JavaScript object with DOT sources
- **Input:** Diagrams dict, JS escape function
- **Output:** JavaScript object literal string
- **Format:**
  ```javascript
  {
    "diagram-id-1": `digraph G { ... }`,
    "diagram-id-2": `digraph G { ... }`
  }
  ```

#### `build_node_data_object(node_data_all)`
- **Purpose:** Build JavaScript object with node metadata
- **Input:** Node data dict
- **Output:** JavaScript object literal string
- **Format:**
  ```javascript
  {
    "diagram-id-1": {
      "node-1": {"label": "...", "type": "..."},
      "node-2": {...}
    }
  }
  ```

#### `build_html(...)`
- **Purpose:** Main entry point for patterns mode
- **Input:**
  - `markdown_path`: Input .md file
  - `diagrams_root`: Root for TTL files
  - `out_html`: Output .html file
  - `converter_path`: Path to ttl_to_graphviz.py
  - `strict`: Fail on missing diagrams?
  - `write_per_pattern_js`: Write .js files?
- **Output:** Writes HTML file
- **Process:**
  1. Read markdown
  2. Parse diagram references
  3. Strip D2 blocks
  4. Inject graph containers
  5. Render markdown to HTML
  6. Wrap code in details
  7. Build TOC
  8. Resolve diagram sources
  9. Build JavaScript objects
  10. Generate sidebar
  11. Generate page navigation
  12. Replace template placeholders
  13. Write output file

---

### 9.4 Main Entry Point

#### `main(argv)`
- **Purpose:** Command-line interface
- **Input:** Command-line arguments (optional)
- **Output:** Exit code (0=success, 1=error)
- **Arguments:**
  - `--mode`: Build mode (docs/patterns/auto)
  - `--markdown`: Input markdown file (required)
  - `--out`: Output HTML file (required)
  - `--title`: Page title (docs mode)
  - `--diagrams-root`: Root for TTL files (patterns mode, required)
  - `--converter`: Path to ttl_to_graphviz.py
  - `--no-strict`: Don't fail on missing diagrams
  - `--prev`: Previous page (href|title)
  - `--next`: Next page (href|title)
  - `--active-nav`: Active nav item
  - `--write-per-pattern-js`: Write individual JS files
- **Auto-Detection:**
  - If `--mode auto`: Searches for @Graphviz_renderer tags
  - If found: Use patterns mode
  - If not found: Use docs mode
- **Error Handling:**
  - Validates required arguments
  - Checks file existence
  - Provides error messages

---

## 10. Data Flow Diagrams

### 10.1 Docs Mode Data Flow

```
┌─────────────────────┐
│  Input: index.md    │
│  Contains:          │
│  - Markdown text    │
│  - @module_indicator│
│  - @property_ind... │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│  Read Markdown File         │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Strip Document Indicators  │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  markdown2.markdown()       │
│  Converts MD → HTML         │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│  Process @module_indicator Tags                 │
│  ┌───────────────────────────────────────────┐  │
│  │  For each tag:                            │  │
│  │  1. Extract URL                           │  │
│  │  2. fetch_owl_file(url)                   │  │
│  │     ├─→ HTTP GET request                  │  │
│  │     └─→ Returns OWL content               │  │
│  │  3. parse_owl_content(content)            │  │
│  │     ├─→ Detect format                     │  │
│  │     ├─→ Parse with rdflib or regex        │  │
│  │     └─→ Returns {classes, maps}           │  │
│  │  4. enrich_classes_from_full_ontology()   │  │
│  │     ├─→ Load pmdco.ttl                    │  │
│  │     ├─→ Match URIs                        │  │
│  │     └─→ Add labels/definitions            │  │
│  │  5. build_tree()                          │  │
│  │     ├─→ Identify roots                    │  │
│  │     ├─→ Recursively build children        │  │
│  │     └─→ Returns tree structure            │  │
│  │  6. generate_tree_html()                  │  │
│  │     ├─→ Create collapsible nodes          │  │
│  │     ├─→ Add tooltips                      │  │
│  │     └─→ Returns HTML string               │  │
│  │  7. Replace tag with generated HTML       │  │
│  └───────────────────────────────────────────┘  │
└──────────┬──────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│  Process @property_indicator Tags               │
│  ┌───────────────────────────────────────────┐  │
│  │  For each tag:                            │  │
│  │  1. Extract type (object/data/annotation) │  │
│  │  2. load_property_data()                  │  │
│  │     ├─→ Load pmdco.ttl                    │  │
│  │     ├─→ Extract properties by type        │  │
│  │     ├─→ Extract subPropertyOf relations   │  │
│  │     └─→ Returns property data             │  │
│  │  3. build_property_tree()                 │  │
│  │     ├─→ Similar to build_tree()           │  │
│  │     └─→ Returns property tree             │  │
│  │  4. generate_property_tree_html()         │  │
│  │     └─→ Returns HTML string               │  │
│  │  5. Replace tag with generated HTML       │  │
│  └───────────────────────────────────────────┘  │
└──────────┬──────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Extract Title from H1      │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Build TOC from H2/H3       │
│  build_toc_list_items()     │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Generate Sidebar           │
│  generate_sidebar_html()    │
│  ├─→ Load navigator.yaml    │
│  └─→ Build HTML structure   │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Generate Page Navigation   │
│  generate_page_nav_html()   │
│  ├─→ Find prev/next pages   │
│  └─→ Build nav links        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Replace Template Placeholders      │
│  html = TEMPLATE_HTML               │
│  .replace("__ARTICLE_CONTENT__", …) │
│  .replace("__TOC_LIST_ITEMS__", …)  │
│  .replace("__SIDEBAR_HTML__", …)    │
│  .replace("__PAGE_NAV__", …)        │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Write Output HTML File     │
│  out_html.write_text(html)  │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Output: index.html         │
│  - Complete static page     │
│  - Embedded CSS/JS          │
│  - Interactive trees        │
│  - Navigation               │
└─────────────────────────────┘
```

---

### 10.2 Patterns Mode Data Flow

```
┌─────────────────────┐
│  Input: patterns.md │
│  Contains:          │
│  - Markdown text    │
│  - @Graphviz_rend...│
│  - D2 diagrams      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│  Read Markdown File         │
└──────────┬──────────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│  Parse Diagram References                    │
│  parse_diagram_refs()                        │
│  ┌────────────────────────────────────────┐  │
│  │  Scan for <!--@Graphviz_renderer:...-->│  │
│  │  Extract:                              │  │
│  │  - URL/path to TTL file                │  │
│  │  - Diagram title (from H2)             │  │
│  │  - Folder name → diagram_id            │  │
│  │  Create DiagramRef objects             │  │
│  └────────────────────────────────────────┘  │
└──────────┬───────────────────────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Strip D2 Code Blocks       │
│  strip_d2_blocks()          │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│  Inject Graph Containers                    │
│  inject_graph_containers()                  │
│  Replace each @Graphviz tag with:           │
│  <div class="mermaid-graph-container">...</> │
└──────────┬──────────────────────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Render Markdown to HTML    │
│  markdown2.markdown()       │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Wrap Code in <details>     │
│  wrap_code_in_details()     │
└──────────┬──────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────┐
│  Resolve Diagram Sources                                 │
│  _resolve_diagram_sources()                              │
│  ┌────────────────────────────────────────────────────┐  │
│  │  1. Load ttl_to_graphviz.py module                 │  │
│  │     _dynamic_import_from_path()                    │  │
│  │                                                     │  │
│  │  2. Find converter class                           │  │
│  │     _find_converter_class()                        │  │
│  │     └─→ Look for render_graph() method             │  │
│  │                                                     │  │
│  │  3. Instantiate converter with options             │  │
│  │     converter = Converter(                         │  │
│  │       output_format="dot",                         │  │
│  │       include_bnodes=False,                        │  │
│  │       enrich=True,                                 │  │
│  │       max_nodes=500                                │  │
│  │     )                                              │  │
│  │                                                     │  │
│  │  4. For each DiagramRef:                           │  │
│  │     ┌─────────────────────────────────────────┐    │  │
│  │     │ If remote URL:                          │    │  │
│  │     │   ├─→ urllib.request.urlopen()          │    │  │
│  │     │   ├─→ Download TTL content              │    │  │
│  │     │   ├─→ Write to temp file                │    │  │
│  │     │   ├─→ converter.render_graph(tmp_path)  │    │  │
│  │     │   └─→ Delete temp file                  │    │  │
│  │     │                                          │    │  │
│  │     │ If local path:                          │    │  │
│  │     │   ├─→ Find pattern directory            │    │  │
│  │     │   ├─→ _find_shape_ttl()                 │    │  │
│  │     │   │   └─→ Search for shape-data.ttl     │    │  │
│  │     │   └─→ converter.render_graph(ttl_path)  │    │  │
│  │     │                                          │    │  │
│  │     │ Extract from result:                    │    │  │
│  │     │   ├─→ DOT source (Graphviz diagram)     │    │  │
│  │     │   └─→ Node metadata (labels, types)     │    │  │
│  │     │                                          │    │  │
│  │     │ Store in dictionaries:                  │    │  │
│  │     │   ├─→ diagrams[diagram_id] = dot        │    │  │
│  │     │   └─→ node_data[diagram_id] = metadata  │    │  │
│  │     └─────────────────────────────────────────┘    │  │
│  │                                                     │  │
│  │  5. Return (diagrams, node_data, js_escape)        │  │
│  └────────────────────────────────────────────────────┘  │
└──────────┬───────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Build JavaScript Objects               │
│  ┌───────────────────────────────────┐  │
│  │ build_dot_diagrams_object()       │  │
│  │   diagrams = {                    │  │
│  │     "temporal-region": `digraph { │  │
│  │       node1 [label="..."];        │  │
│  │       ...                         │  │
│  │     }`                            │  │
│  │   }                               │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │ build_node_data_object()          │  │
│  │   nodeData = {                    │  │
│  │     "temporal-region": {          │  │
│  │       "node1": {                  │  │
│  │         "label": "Process",       │  │
│  │         "type": "class"           │  │
│  │       }                           │  │
│  │     }                             │  │
│  │   }                               │  │
│  └───────────────────────────────────┘  │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Build TOC                  │
│  build_toc_list_items()     │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Generate Sidebar           │
│  generate_sidebar_html()    │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Generate Page Navigation   │
│  generate_page_nav_html()   │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Replace Template Placeholders          │
│  html = TEMPLATE_HTML                   │
│  .replace("__ARTICLE_CONTENT__", …)     │
│  .replace("__TOC_LIST_ITEMS__", …)      │
│  .replace("__SIDEBAR_HTML__", …)        │
│  .replace("__PAGE_NAV__", …)            │
│  .replace("__DIAGRAMS_OBJECT__", …)     │
│  .replace("__NODEDATA_OBJECT__", …)     │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Write Output HTML File     │
│  out_html.write_text(html)  │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Output: patterns.html      │
│  - Complete static page     │
│  - Embedded diagrams (DOT)  │
│  - Client-side Viz.js       │
│  - Interactive controls     │
│  - Pan/zoom/export          │
└─────────────────────────────┘
```

---

## 11. Troubleshooting

### 11.1 Common Issues

#### Issue: "markdown2 is required"
**Cause:** markdown2 not installed  
**Solution:**
```bash
pip install markdown2
```

#### Issue: "rdflib not available, cannot parse RDF/XML"
**Cause:** rdflib not installed  
**Solution:**
```bash
pip install rdflib
```

#### Issue: "navigator.yaml not found"
**Cause:** Script cannot locate navigator.yaml  
**Expected Location:** `../../navigator.yaml` (relative to script)  
**Solution:**
- Check file exists at: `c:\Users\potu\Desktop\PMD\PMD_Docs_Presentation\docs\navigator.yaml`
- Verify script location matches expected structure

#### Issue: "Failed to load ontology from URL"
**Cause:** Network error, timeout, or invalid URL  
**Solution:**
1. Check internet connection
2. Verify URL is accessible in browser
3. Check firewall/proxy settings
4. Increase timeout in `fetch_owl_file()` or `load_full_ontology_from_url()`

#### Issue: "Pattern directory not found"
**Cause:** Incorrect `--diagrams-root` path  
**Solution:**
- Verify diagrams_root points to correct directory
- Check that pattern subdirectories exist
- For patterns.md: Should be parent directory containing `patterns/` folder

#### Issue: "ttl_to_graphviz.py not found"
**Cause:** Converter script missing or in wrong location  
**Expected Location:** Same directory as build_all.py  
**Solution:**
- Verify file exists: `c:\Users\potu\Desktop\PMD\PMD_Docs_Presentation\docs\docs_HTML\scripts\ttl_to_graphviz.py`
- Use `--converter` argument to specify custom path

#### Issue: "Failed to fetch remote TTL"
**Cause:** URL inaccessible, timeout, or encoding issues  
**Solution:**
1. Test URL in browser
2. Check for URL encoding (spaces → %20)
3. Verify User-Agent not blocked
4. Use `--no-strict` to continue on errors

#### Issue: "No classes found in ontology"
**Cause:** OWL file has no class declarations, or parsing failed  
**Solution:**
1. Verify OWL file is valid
2. Check format (Functional Syntax, RDF/XML, Turtle)
3. Inspect raw OWL content for expected patterns
4. Enable debug logging in parse functions

### 11.2 Debugging Tips

#### Enable Verbose Output
Add print statements in key functions:
```python
# In fetch_owl_file():
print(f"  Fetching OWL file from: {url}")
print(f"  Fetched {len(content)} bytes")

# In parse_owl_content():
print(f"  Parsed {len(classes)} classes")

# In build_tree():
print(f"  Building tree with {len(roots)} roots")
```

#### Check Intermediate Results
Insert debug prints:
```python
# After parsing OWL:
print(f"Classes: {list(classes.keys())[:5]}")  # First 5
print(f"Child map: {dict(list(child_map.items())[:3])}")

# After enrichment:
print(f"Enriched {enriched_count} classes")
```

#### Validate File Paths
```python
# Check file existence:
print(f"Navigator path exists: {navigator_path.exists()}")
print(f"TTL file exists: {ttl_path.exists()}")
print(f"Output dir exists: {out_html.parent.exists()}")
```

#### Test Regex Patterns
```python
# Test tag matching:
test_md = "<!--@module_indicator:https://example.com/owl-->"
matches = MODULE_INDICATOR_RE.findall(test_md)
print(f"Found {len(matches)} module indicators")
```

#### Inspect Navigator Config
```python
# After loading:
config = load_NAVIGATOR_CONFIG()
print(json.dumps(config, indent=2))
```

### 11.3 Performance Optimization

#### Cache Management
- Navigator config cached in `_NAVIGATOR_CONFIG`
- Ontology labels cached in `_FULL_ONTOLOGY_LABELS`
- Property data cached in `_PROPERTY_CACHE`
- **To clear cache:** Restart script or set globals to `None`

#### Large Ontologies
If processing very large ontologies (>10,000 classes):
1. Adjust `max_nodes` in converter options
2. Increase `max_edges` for complex diagrams
3. Consider pagination or filtering

#### Network Optimization
- Use local files instead of remote URLs when possible
- Cache downloaded ontologies locally
- Increase timeouts for slow connections

---

## 12. Appendix

### 12.1 Tag Reference

#### @module_indicator
**Format:**
```html
<!--@module_indicator:URL-->
```

**Example:**
```html
<!--@module_indicator:https://w3id.org/pmd/co/modules/PMD_subset.owl-->
```

**Effect:**
- Fetches OWL file from URL
- Parses class hierarchy
- Generates interactive tree
- Replaces tag with HTML tree

**Supported Formats:**
- OWL Functional Syntax
- RDF/XML
- Turtle (TTL)

---

#### @property_indicator
**Format:**
```html
<!--@property_indicator:TYPE-->
```

**Types:**
- `object`: Object properties
- `data`: Data properties
- `annotation`: Annotation properties

**Example:**
```html
<!--@property_indicator:object-->
```

**Effect:**
- Loads full ontology
- Extracts properties of specified type
- Builds property hierarchy
- Generates interactive tree
- Replaces tag with HTML tree

---

#### @Graphviz_renderer
**Format:**
```html
<!--@Graphviz_renderer:PATH_OR_URL-->
```

**Example (Remote URL):**
```html
<!--@Graphviz_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/temporal%20region/shape-data.ttl-->
```

**Example (Local Path):**
```html
<!--@Graphviz_renderer:./patterns/temporal region-->
```

**Effect:**
- Downloads TTL file (if URL) or finds local file
- Converts to Graphviz DOT format
- Generates interactive diagram container
- Replaces tag with container HTML
- Embeds DOT source in JavaScript

**Notes:**
- Title taken from nearest preceding `## Heading`
- Diagram ID generated from folder name
- URL encoding preserved for HTTP requests
- Local paths searched for `shape-data.ttl` variants

---

### 12.2 OntologyClass Dataclass

```python
@dataclass
class OntologyClass:
    uri: str                                    # Full URI
    label: str = ""                             # Human-readable label
    definition: str = ""                        # SKOS definition
    children: List['OntologyClass'] = []        # Child classes
    
    @property
    def prefix(self) -> str:
        """Determine prefix based on URI"""
        # Returns: 'pmd', 'bfo', 'ro', 'iao', 'obi', 'chebi', 'owl'
    
    @property
    def display_name(self) -> str:
        """Get display name (label or local part)"""
        # Returns label if available, else local name from URI
```

---

### 12.3 OntologyProperty Dataclass

```python
@dataclass
class OntologyProperty:
    uri: str                                    # Full URI
    label: str = ""                             # Human-readable label
    definition: str = ""                        # SKOS definition
    property_type: str = "object"               # object/data/annotation
    children: List['OntologyProperty'] = []     # Sub-properties
    
    @property
    def prefix(self) -> str:
        """Determine prefix based on URI"""
        # Returns: 'pmd', 'bfo', 'ro', 'iao', 'obi', 'owl'
    
    @property
    def display_name(self) -> str:
        """Get display name (label or local part)"""
        # Returns label if available, else local name from URI
```

---

### 12.4 DiagramRef Dataclass

```python
@dataclass(frozen=True)
class DiagramRef:
    diagram_id: str        # Slugified folder name
    rel_path: str          # Relative path or URL to TTL file
    title: str             # Diagram title (from H2 or folder name)
```

---

### 12.5 Command-Line Examples

#### Build Single Doc
```bash
python build_all.py \
  --mode docs \
  --markdown ../index.md \
  --out ../docs_HTML/HTML_Docs/index.html
```

#### Build Patterns Page
```bash
python build_all.py \
  --mode patterns \
  --markdown ../patterns.md \
  --diagrams-root ../ \
  --out ../docs_HTML/HTML_Docs/patterns.html
```

#### Auto-Detect Mode
```bash
python build_all.py \
  --markdown ../intro.md \
  --out ../docs_HTML/HTML_Docs/intro.html
```

#### With Custom Title and Navigation
```bash
python build_all.py \
  --mode docs \
  --markdown ../intro.md \
  --out ../docs_HTML/HTML_Docs/intro.html \
  --title "Introduction to PMDco" \
  --prev "index.html|Home" \
  --next "patterns.html|Usage Patterns"
```

---

## End of Documentation

This documentation covers all aspects of `build_all.py`. For questions or issues, refer to the source code or contact the development team.

**Last Updated:** January 11, 2026  
**Author:** AI Documentation Generator  
**Version:** 1.0
