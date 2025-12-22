# PMDco Documentation Builder

A comprehensive static site builder for generating production-ready HTML documentation from Markdown files. This system powers the **Platform MaterialDigital Core Ontology (PMDco)** documentation website.

---

## 📁 Project Structure

```
docs/
├── navigator.yaml                    # Navigation configuration (REQUIRED)
├── patterns.md                       # Usage patterns with Graphviz diagrams
├── ontology_structure.md             # Ontology structure with class trees
├── index.md                          # Home page
├── intro.md                          # Introduction
├── ...
│
├── docs_HTML/
│   ├── scripts/
│   │   ├── build_all.py              # Main unified builder script
│   │   ├── run_all.py                # Batch builder for all pages
│   │   └── ttl_to_graphviz.py        # TTL to Graphviz converter
│   │
│   ├── HTML_Docs/                    # Generated HTML files
│   │   ├── patterns.html
│   │   ├── index.html
│   │   ├── Logo.svg                  # Copied logo asset
│   │   └── ...
│   │
│   └── README.md                     # This documentation
└── ...
```

---

## 🚀 Getting Started

### Prerequisites

Install required Python packages:

```bash
pip install markdown2 rdflib pyyaml
```

### Build All Documentation Pages

Navigate to the project root or scripts directory:

```bash
# From docs/docs_HTML/scripts/
cd docs/docs_HTML/scripts
python run_all.py
```

This reads `navigator.yaml` from the `docs/` directory and builds HTML for every page defined in it.

**New Default Output:** The generated HTML files will be placed in `docs/docs_HTML/HTML_Docs` by default.

### Build a Single Page

```bash
python build_all.py --markdown "../../patterns.md" --out "../HTML_Docs/patterns.html"
```

For pages with diagrams, specify the diagrams root:

```bash
python build_all.py --markdown "../../patterns.md" --out "../HTML_Docs/patterns.html" --diagrams-root "../../"
```

---

## 📋 Navigator Configuration (`navigator.yaml`)

The `docs/navigator.yaml` file is the **single source of truth** for the entire website structure. The build system reads this file to:

1. **Generate the sidebar navigation** with icons and section groupings
2. **Calculate previous/next page links** based on page order
3. **Map markdown files to HTML outputs** for batch building
4. **Define the full ontology path** for class/property enrichment
5. **Provide icon definitions** for the UI

### Complete Schema Reference

```yaml
# Version identifier for compatibility
schema: "pmdco-nav/v1"

# Default icons that rotate automatically for pages without explicit icons
defaults:
  icons:
    - file-text
    - document
    - compass
    - star
    - zap
    - globe

# Path to the full ontology TTL file for enriching class labels and definitions
full_ontology_path: "https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/src/ontology/pmdco.ttl"

# Navigation sections
sections:
  - id: getting-started
    title: "Getting Started"
    icon: home
    pages:
      - title: Home
        href: index.html
        md: index.md
        icon: home

  - id: ontology-guide
    title: "Ontology Guide"
    icon: layers
    pages:
      - title: Usage Patterns
        href: patterns.html
        md: patterns.md
        icon: zap

# Icon catalog
icons:
  home:
    path: "..."
```

---

## 📝 Markdown Tags Reference

The build system recognizes special HTML comment tags in your Markdown files. These tags tell the builder to generate dynamic content.

### 1. `@Graphviz_renderer` — Interactive Ontology Diagrams

**Purpose:** Renders TTL (Turtle) or SHACL shape files as interactive Graphviz diagrams with zoom, pan, tooltips, and export capabilities.

**Syntax:**
```markdown
<!--@Graphviz_renderer:PATH_OR_URL_TO_TTL_FILE-->
```

**Real Example from `patterns.md`:**

```markdown
## Pattern 1 - Temporal Region
<!--@Graphviz_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/temporal%20region/shape-data.ttl-->
```

### 2. `@module_indicator` — Ontology Class Hierarchy Trees

**Purpose:** Fetches an OWL ontology file and generates an interactive, expandable class hierarchy tree.

**Syntax:**
```markdown
<!--@module_indicator:URL_TO_OWL_FILE-->
```

**Real Example from `ontology_structure.md`:**

```markdown
## BFO Module Classes
<!--@module_indicator:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/src/ontology/modules/bfo_module.owl-->
```

### 3. `@property_indicator` — Property Hierarchy Trees

**Purpose:** Generates interactive property trees showing object, data, or annotation properties.

**Syntax:**
```markdown
<!--@property_indicator:PROPERTY_TYPE-->
```

**Property Types:** `object`, `data`, `annotation`

**Real Example from `ontology_structure.md`:**

```markdown
## Object Properties
<!--@property_indicator:object-->
```

---

## 🎨 Branding & Assets

### Logo
The build system expects a logo file named `Logo.svg` in the source documentation directory (`docs/Logo.svg`).
During the build process, this file is automatically copied to the output directory (`HTML_Docs/Logo.svg`) and linked in the website header.

---

## 📌 Command Line Reference

### `build_all.py`

Main builder script for single pages.

```
Usage: python build_all.py [OPTIONS]

Required Arguments:
  --markdown, -m PATH      Source Markdown file path
  --out, -o PATH           Output HTML file path

Optional Arguments:
  --mode, -M MODE          Build mode: docs, patterns, auto (default: auto)
  --diagrams-root, -d PATH Base directory for Graphviz_renderer paths
  --title, -t TEXT         Override page title
  --no-strict              Don't fail if diagrams can't be resolved
```

### `run_all.py`

Batch builder that builds all pages defined in `navigator.yaml`.

```
Usage: python run_all.py [OPTIONS]

Optional Arguments:
  --md-dir PATH            Markdown source directory (default: ../../)
  --out-dir PATH           HTML output directory (default: ../HTML_Docs)
  --diagrams-root PATH     Base directory for diagrams (default: ../../)
  --quiet, -q              Suppress detailed progress output
```

**Examples:**

```bash
# Build all documentation pages to default HTML_Docs/
python run_all.py

# Build to custom output directory
python run_all.py --out-dir "../custom_output"
```

---

## 📄 License

Part of the **Platform MaterialDigital (PMD)** project.

Funded by the German Federal Ministry of Education and Research (BMBF).

See [materialdigital.de](https://materialdigital.de/) for more information.
