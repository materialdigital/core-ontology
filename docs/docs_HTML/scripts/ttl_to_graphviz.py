#!/usr/bin/env python3
"""
ttl_to_graphviz.py - RDF/TTL to Diagram Converter for PMDco
============================================================

This module converts RDF Turtle (.ttl) ontology pattern files into visual
diagrams in either Graphviz DOT or Mermaid flowchart format. It is the core
diagram generation engine used by the PMDco documentation build system.

Architecture Overview
---------------------
The converter operates in three main phases:

1. **RDF Parsing**: Load TTL files using rdflib, handling various encoding
   issues and prefix conventions common in ontology files.

2. **Graph Analysis**: Extract classes, individuals, properties, SHACL shapes,
   and relationships. Optionally enrich with labels and hierarchy from:
   - Local *_full.ttl ontology files (preferred)
   - Remote OBO Foundry ontologies (BFO, OBI, IAO, RO, etc.)

3. **Diagram Rendering**: Generate visual representation as either:
   - Graphviz DOT: For high-quality static SVG rendering
   - Mermaid: For interactive web-based rendering

Visual Style Guide
------------------
Nodes are color-coded by ontology source for easy identification:

    BFO (Basic Formal Ontology):  #F556CB (pink)
    OBI (Ontology for Biomedical Investigations):  #F5D5B1 (peach)
    IAO (Information Artifact Ontology):  #F6A252 (orange)
    RO (Relation Ontology):  #F43F5E (rose)
    COB (Core Ontology for Biology):  #93AFF3 (periwinkle)
    PMD/PMDco (Materials Data Ontology):  #46CAD3 (cyan)
    QUDT (Quantities, Units, Dimensions):  #C9DBFE (light blue)
    Generic Class:  #FDFDC8 (light yellow)
    Individual (ABox):  #E6E6E6 (light gray)
    Literal:  #93D053 (green)
    SHACL Shape:  #A5F3FC (cyan)
    Constraint:  #FED7AA (orange)

Node shapes indicate semantic role:
    - Box/Square: TBox (Classes, Named Individuals)
    - Ellipse/Oval: ABox (Instance data)
    - Hexagon: SHACL Shapes
    - Diamond: Constraints
    - Note: Literals

Usage Examples
--------------
Command-line usage for a single TTL file::

    # Output DOT format to stdout
    python ttl_to_graphviz.py --ttl pattern.ttl --format dot

    # Output Mermaid format to stdout
    python ttl_to_graphviz.py --ttl pattern.ttl --format mermaid

Batch processing with JS output::

    # Generate JS file with all diagrams from a directory
    python ttl_to_graphviz.py --ttl-dir ./patterns --format dot --out-js diagrams.js

Integration with build_all.py::

    # The build system imports and uses this module programmatically
    from ttl_to_graphviz import RdfToDiagram, load_full_ontology_index

    # Load the full PMDco ontology for hierarchy resolution
    index = load_full_ontology_index([Path("pmdco_full.ttl")])

    # Create converter with hierarchy expansion enabled
    converter = RdfToDiagram(
        output_format="dot",
        full_ontology=index,
        use_full_hierarchy=True,
    )

    # Render a pattern file
    result = converter.render_graph(Path("pattern.ttl"))
    print(result.source)  # DOT code

Prefix Handling
---------------
Ontology TTL files often use special prefix conventions that require
careful handling:

1. **Exact-prefix tokens**: Some patterns define prefixes pointing to a
   single term IRI::

       @prefix process: <http://purl.obolibrary.org/obo/BFO_0000015> .

   The empty local QName `process:` is then used to reference this term.
   rdflib doesn't normalize these into QNames, so we detect and handle
   them specially.

2. **OBO Foundry prefixes**: Standard OBO URIs like
   `http://purl.obolibrary.org/obo/BFO_0000001` are parsed to extract
   the prefix (BFO) for styling and labeling.

Dependencies
------------
Required:
    - rdflib: RDF parsing and graph operations

Optional (for enhanced label resolution):
    - Network access for downloading OBO ontologies when --enrich is used

Module Exports
--------------
Main classes and functions for programmatic use:

    RdfToDiagram: Main converter class
    DiagramResult: Container for rendered diagram output
    FullOntologyIndex: Index over local *_full.ttl files
    load_full_ontology_index: Load and index local ontology files
    slugify: Convert strings to URL-safe identifiers
    js_escape_template_literal: Escape strings for JS template literals

Author: PMDco Documentation Team
License: CC BY 4.0
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

from rdflib import BNode, Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL

# =============================================================================
# NAMESPACE DEFINITIONS
# =============================================================================

# SHACL namespace for constraint validation shapes
SH = Namespace("http://www.w3.org/ns/shacl#")

# Module logger - use logging.basicConfig() to configure output
LOG = logging.getLogger("ttl_to_graphviz")


# =============================================================================
# STYLING CONFIGURATION
# =============================================================================
# Color schemes and visual styles for diagram nodes and edges.
# Each ontology source gets a distinct color for easy visual identification.
# =============================================================================

# Mermaid classDef styles - CSS-like styling for Mermaid flowcharts
# Format: "fill:COLOR,stroke:BORDER,stroke-width:WIDTH,color:TEXT"
CLASSDEF_STYLES: Dict[str, str] = {
    # Generic node types
    "cls": "fill:#FDFDC8,stroke:#D4D48A,stroke-width:2px,color:#333333",       # Default class (light yellow)
    "ind": "fill:#E6E6E6,stroke:#AAAAAA,stroke-width:2px,color:#333333",       # ABox individual (light gray)
    "lit": "fill:#93D053,stroke:#6BA33A,stroke-width:2px,color:#333333",       # Literal value (green)
    "cat": "fill:#99F6E4,stroke:#0D9488,stroke-width:2px,color:#134E4A",       # Categorical value (teal)
    "shacl": "fill:#A5F3FC,stroke:#0891B2,stroke-width:2px,color:#164E63",     # SHACL Shape (cyan)
    "constraint": "fill:#FED7AA,stroke:#EA580C,stroke-width:2px,color:#7C2D12",# Constraint (orange)
    # Ontology-specific styles for TBox classes
    "bfo": "fill:#F556CB,stroke:#C93DA0,stroke-width:2px,color:#333333",       # BFO (pink)
    "obi": "fill:#F5D5B1,stroke:#D4B08A,stroke-width:2px,color:#333333",       # OBI (warm peach)
    "cob": "fill:#93AFF3,stroke:#6B8AD6,stroke-width:2px,color:#333333",       # COB (periwinkle blue)
    "pmd": "fill:#46CAD3,stroke:#2EA0A8,stroke-width:2px,color:#333333",       # PMD (cyan)
    "pmdco": "fill:#46CAD3,stroke:#2EA0A8,stroke-width:2px,color:#333333",     # PMDco (same as PMD)
    "iao": "fill:#F6A252,stroke:#D4803A,stroke-width:2px,color:#333333",       # IAO (orange)
    "ro": "fill:#F43F5E,stroke:#C4283F,stroke-width:2px,color:#FFFFFF",        # RO (rose)
    "qudt": "fill:#C9DBFE,stroke:#8AAAD6,stroke-width:2px,color:#333333",      # QUDT (light blue)
}

# Graphviz DOT node styles - attribute dictionaries for node styling
# Keys match CLASSDEF_STYLES for consistency between formats
GRAPHVIZ_NODE_STYLES: Dict[str, Dict[str, str]] = {
    # Generic node types
    "cls": {"fillcolor": "#FDFDC8", "color": "#D4D48A", "penwidth": "2", "fontcolor": "#333333"},
    "ind": {"fillcolor": "#E6E6E6", "color": "#AAAAAA", "penwidth": "2", "fontcolor": "#333333"},
    "lit": {"fillcolor": "#93D053", "color": "#6BA33A", "penwidth": "2", "fontcolor": "#333333"},
    "cat": {"fillcolor": "#99F6E4", "color": "#0D9488", "penwidth": "2", "fontcolor": "#134E4A"},
    "shacl": {"fillcolor": "#A5F3FC", "color": "#0891B2", "penwidth": "2", "fontcolor": "#164E63"},
    "constraint": {"fillcolor": "#FED7AA", "color": "#EA580C", "penwidth": "2", "fontcolor": "#7C2D12"},
    # Ontology-specific styles
    "bfo": {"fillcolor": "#F556CB", "color": "#C93DA0", "penwidth": "2", "fontcolor": "#333333"},
    "obi": {"fillcolor": "#F5D5B1", "color": "#D4B08A", "penwidth": "2", "fontcolor": "#333333"},
    "cob": {"fillcolor": "#93AFF3", "color": "#6B8AD6", "penwidth": "2", "fontcolor": "#333333"},
    "pmd": {"fillcolor": "#46CAD3", "color": "#2EA0A8", "penwidth": "2", "fontcolor": "#333333"},
    "pmdco": {"fillcolor": "#46CAD3", "color": "#2EA0A8", "penwidth": "2", "fontcolor": "#333333"},
    "iao": {"fillcolor": "#F6A252", "color": "#D4803A", "penwidth": "2", "fontcolor": "#333333"},
    "ro": {"fillcolor": "#F43F5E", "color": "#C4283F", "penwidth": "2", "fontcolor": "#FFFFFF"},
    "qudt": {"fillcolor": "#C9DBFE", "color": "#8AAAD6", "penwidth": "2", "fontcolor": "#333333"},
}

# Remote ontology download URLs for enrichment (--enrich flag)
# These are fetched on-demand and cached locally
DEFAULT_ONTOLOGY_URLS: Dict[str, str] = {
    "bfo": "http://purl.obolibrary.org/obo/bfo.owl",
    "obi": "http://purl.obolibrary.org/obo/obi.owl",
    "iao": "http://purl.obolibrary.org/obo/iao.owl",
    "ro": "http://purl.obolibrary.org/obo/ro.owl",
    "uo": "http://purl.obolibrary.org/obo/uo.owl",
    "cob": "http://purl.obolibrary.org/obo/cob.owl",
}

# BFO Entity - the root class for ontology hierarchies
BFO_ENTITY_IRI = "http://purl.obolibrary.org/obo/BFO_0000001"

# Implicit top-level classes that should be excluded from diagrams
# Every class is implicitly a subclass of these, so showing them adds noise
_IMPLICIT_TOP_CLASSES: set = {
    URIRef("http://www.w3.org/2002/07/owl#Thing"),
    URIRef("http://www.w3.org/2000/01/rdf-schema#Resource"),
}


# =============================================================================
# TURTLE PARSING UTILITIES
# =============================================================================

def parse_turtle_safely(g: Graph, path: Path) -> None:
    """Parse a Turtle file with encoding normalization.

    Handles common encoding issues in ontology files:
    - Non-breaking spaces (U+00A0) that cause rdflib parser errors
    - UTF-8 encoding with error replacement for invalid sequences

    Args:
        g: RDFLib Graph to parse into (will be modified in-place).
        path: Path to the Turtle (.ttl) file to parse.

    Raises:
        Exception: If the file cannot be parsed as valid Turtle syntax.

    Note:
        The file's URI is used as the publicID for relative IRI resolution.
    """
    data = path.read_text(encoding="utf-8", errors="replace").replace("\u00a0", " ")
    g.parse(data=data, format="turtle", publicID=str(path.resolve().as_uri()))


# =============================================================================
# STRING UTILITIES
# =============================================================================

def slugify(stem: str) -> str:
    """Convert a string to a URL-safe slug identifier.

    Transforms the input string by:
    1. Converting to lowercase
    2. Replacing non-word characters with hyphens
    3. Collapsing multiple consecutive hyphens
    4. Stripping leading/trailing hyphens

    Args:
        stem: The string to convert (e.g., a filename or title).

    Returns:
        A URL-safe slug string, or "diagram" if the result would be empty.

    Examples:
        >>> slugify("Temporal Region Pattern")
        'temporal-region-pattern'
        >>> slugify("BFO_0000015")
        'bfo-0000015'
    """
    s = stem.strip().lower()
    s = re.sub(r"[^\w\-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "diagram"


def escape_mermaid_label(label: str) -> str:
    """Escape a string for use in Mermaid node/edge labels.

    Escapes special characters that have meaning in Mermaid syntax:
    - Ampersand (&) for HTML entities
    - Quotes (") for attribute values
    - Brackets ([]) for node definitions
    - Newlines for multi-line labels

    Args:
        label: The raw label text to escape.

    Returns:
        The escaped label safe for Mermaid syntax.
    """
    label = label.replace("&", "&amp;")
    label = label.replace('"', "&quot;")
    label = label.replace("[", "&#91;").replace("]", "&#93;")
    label = label.replace("\n", "<br/>")
    return label


def escape_dot_label(label: str) -> str:
    """Escape a string for use in Graphviz DOT quoted strings.

    Escapes special characters that have meaning in DOT syntax:
    - Backslash (\\) as escape character
    - Quotes (") for string delimiters
    - Newlines for multi-line labels

    Args:
        label: The raw label text to escape.

    Returns:
        The escaped label safe for DOT quoted strings.
    """
    label = label.replace("\\", "\\\\")
    label = label.replace('"', '\\"')
    label = label.replace("\r\n", "\n").replace("\r", "\n")
    label = label.replace("\n", "\\n")
    return label


def dot_attrs(attrs: Dict[str, str]) -> str:
    """Build a DOT attribute list from a dictionary.

    Formats the attributes as: [key1="value1",key2="value2",...]

    Special handling:
    - HTML-like labels (starting with < and ending with >) are not quoted
    - All other values are escaped and double-quoted

    Args:
        attrs: Dictionary of attribute name-value pairs.

    Returns:
        DOT attribute list string, or empty string if attrs is empty.

    Example:
        >>> dot_attrs({"shape": "box", "label": "Node"})
        ' [label="Node",shape="box"]'
    """
    if not attrs:
        return ""
    parts = []
    for k in sorted(attrs.keys()):
        val = str(attrs[k])
        # HTML-like labels should not be quoted
        if k == "label" and val.startswith("<") and val.endswith(">"):
            parts.append(f'{k}={val}')
        else:
            parts.append(f'{k}="{escape_dot_label(val)}"')
    return " [" + ",".join(parts) + "]"


def chunked(items: List[str], n: int = 10) -> Iterable[List[str]]:
    """Split a list into chunks of size n.

    Args:
        items: List to split into chunks.
        n: Maximum size of each chunk (default: 10).

    Yields:
        Lists of up to n items each.
    """
    for i in range(0, len(items), n):
        yield items[i : i + n]


def uri_local_name(uri: str) -> str:
    """Extract the local name from a URI.

    Extracts the fragment identifier after # if present, otherwise
    the last path segment after /.

    Args:
        uri: Full URI string.

    Returns:
        The local name portion of the URI.

    Examples:
        >>> uri_local_name("http://example.org/ns#LocalName")
        'LocalName'
        >>> uri_local_name("http://example.org/ns/LocalName")
        'LocalName'
    """
    if "#" in uri:
        return uri.rsplit("#", 1)[1]
    return uri.rstrip("/").rsplit("/", 1)[-1]


def obo_prefix_for_iri(iri: str) -> Optional[str]:
    """Detect the ontology source from an IRI and return its prefix.

    Recognizes IRIs from various ontology sources and returns a lowercase
    prefix token that can be used for styling and labeling.

    Supported sources:
    - OBO Foundry: BFO, OBI, IAO, RO, UO, CHEBI, GO, PATO, etc.
    - PMD: pmd, pmdco
    - QUDT: units, quantities
    - W3C vocabularies: dcterms, dc, foaf, skos, prov, schema

    Args:
        iri: The IRI to analyze.

    Returns:
        Lowercase prefix string (e.g., 'bfo', 'obi', 'pmd') or None if
        the ontology source cannot be determined.

    Examples:
        >>> obo_prefix_for_iri("http://purl.obolibrary.org/obo/BFO_0000001")
        'bfo'
        >>> obo_prefix_for_iri("https://w3id.org/pmd/co/Process")
        'pmdco'
    """
    # OBO Foundry pattern: http://purl.obolibrary.org/obo/PREFIX_nnnnnnn
    if "purl.obolibrary.org/obo/" in iri:
        local = iri.split("/obo/", 1)[1]
        # Match patterns like BFO_0000001, OBI_0000245, RO_0000056
        m = re.match(r"^([A-Za-z]+)_\d+$", local)
        if m:
            return m.group(1).lower()
        # Handle hash-based OBO IRIs
        m2 = re.match(r"^([A-Za-z]+)_", local)
        if m2:
            return m2.group(1).lower()

    # PMD ontologies
    if "w3id.org/pmd/" in iri:
        if "/pmdco/" in iri or "/pmdco#" in iri:
            return "pmdco"
        return "pmd"

    # QUDT (Quantities, Units, Dimensions)
    if "qudt.org/" in iri:
        return "qudt"

    # Dublin Core
    if "purl.org/dc/terms/" in iri:
        return "dcterms"
    if "purl.org/dc/elements/" in iri:
        return "dc"

    # Schema.org
    if "schema.org/" in iri:
        return "schema"

    # FOAF
    if "xmlns.com/foaf/" in iri:
        return "foaf"

    # SKOS
    if "w3.org/2004/02/skos/" in iri:
        return "skos"

    # PROV-O
    if "w3.org/ns/prov" in iri:
        return "prov"

    return None


def safe_mermaid_id(raw: str) -> str:
    """Convert a string to a valid Mermaid node identifier.

    Mermaid node IDs must:
    - Contain only alphanumeric characters and underscores
    - Not start with a digit
    - Not be empty

    Args:
        raw: The raw string to convert.

    Returns:
        A valid Mermaid node ID.
    """
    s = re.sub(r"[^A-Za-z0-9_]", "_", raw)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        s = "n"
    if s[0].isdigit():
        s = "n_" + s
    return s


# =============================================================================
# ONTOLOGY CACHE - REMOTE ENRICHMENT
# =============================================================================

class OntologyCache:
    """Cache manager for remote ontology files used in enrichment.

    Downloads and caches OWL ontology files from OBO Foundry and other
    sources. Used when the --enrich flag is enabled to resolve labels
    and superclass chains for external ontology terms.

    Attributes:
        cache_dir: Local directory for storing cached ontology files.
        ontology_urls: Mapping of prefix keys to download URLs.

    Note:
        Prefer using local *_full.ttl files for enrichment as they provide
        curated labels and hierarchy specific to the PMDco context.
    """

    def __init__(self, cache_dir: Path, ontology_urls: Dict[str, str]) -> None:
        """Initialize the ontology cache.

        Args:
            cache_dir: Directory for storing downloaded ontology files.
                Created if it doesn't exist.
            ontology_urls: Dictionary mapping prefix keys (e.g., 'bfo')
                to their download URLs.
        """
        self.cache_dir = cache_dir
        self.ontology_urls = ontology_urls
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._graphs: Dict[str, Graph] = {}

    def _cached_path(self, key: str, url: str) -> Path:
        """Generate the cache file path for an ontology."""
        h = re.sub(r"[^a-zA-Z0-9]+", "_", url)[:40]
        return self.cache_dir / f"{key}-{h}.rdf"

    def ensure_loaded(self, key: str) -> Optional[Graph]:
        """Ensure an ontology is loaded into memory, downloading if needed."""
        if key in self._graphs:
            return self._graphs[key]

        url = self.ontology_urls.get(key)
        if not url:
            return None

        target = self._cached_path(key, url)
        if not target.exists():
            try:
                LOG.info("Downloading ontology %s from %s", key, url)
                with urllib.request.urlopen(url, timeout=60) as r:
                    target.write_bytes(r.read())
            except Exception as e:
                LOG.warning("Failed to download ontology '%s' (%s): %s", key, url, e)
                return None

        g = Graph()
        try:
            g.parse(target.as_posix())
        except Exception as e:
            LOG.warning("Failed to parse cached ontology '%s' (%s): %s", key, target, e)
            return None

        self._graphs[key] = g
        return g

    def label_for(self, uri: URIRef) -> Optional[str]:
        """Get the rdfs:label for a URI from cached ontologies."""
        iri = str(uri)
        key = obo_prefix_for_iri(iri)
        if not key:
            return None
        g = self.ensure_loaded(key)
        if not g:
            return None
        for lbl in g.objects(uri, RDFS.label):
            if isinstance(lbl, Literal):
                return str(lbl)
        return None

    def superclasses(self, cls: URIRef, max_depth: int) -> Set[Tuple[URIRef, URIRef]]:
        """Get superclass edges for a class up to a maximum depth."""
        iri = str(cls)
        key = obo_prefix_for_iri(iri)
        if not key:
            return set()
        g = self.ensure_loaded(key)
        if not g:
            return set()

        edges: Set[Tuple[URIRef, URIRef]] = set()
        frontier: List[Tuple[URIRef, int]] = [(cls, 0)]
        seen: Set[URIRef] = {cls}
        while frontier:
            cur, depth = frontier.pop(0)
            if depth >= max_depth:
                continue
            for parent in g.objects(cur, RDFS.subClassOf):
                if isinstance(parent, URIRef) and parent not in _IMPLICIT_TOP_CLASSES:
                    edges.add((cur, parent))
                    if parent not in seen:
                        seen.add(parent)
                        frontier.append((parent, depth + 1))
        return edges


# =============================================================================
# FULL ONTOLOGY INDEX - LOCAL ENRICHMENT
# =============================================================================

@dataclass
class FullOntologyIndex:
    """Lightweight index over local '*_full.ttl' ontology files.

    Provides efficient lookup for rdfs:label annotations and
    rdfs:subClassOf relationships for hierarchy expansion.

    Attributes:
        labels: Mapping of URI strings to their label strings.
        parents: Mapping of URI strings to sets of parent URI strings.
    """

    labels: Dict[str, str]
    parents: Dict[str, Set[str]]

    def label_for(self, uri: URIRef) -> Optional[str]:
        """Get the label for a URI."""
        return self.labels.get(str(uri))

    def parents_of(self, uri: URIRef) -> Set[URIRef]:
        """Get the direct parent classes of a URI."""
        return {URIRef(p) for p in self.parents.get(str(uri), set())}


def discover_full_ontology_files(base_dir: Path) -> List[Path]:
    """Discover all '*_full.ttl' ontology files in a directory."""
    return sorted([p for p in base_dir.glob("*_full.ttl") if p.is_file()])


def best_label(literals: List[Literal]) -> Optional[str]:
    """Select the best label from a list of literal values.

    Prefers English labels or labels without language tags,
    and shorter labels for concise display.
    """
    if not literals:
        return None

    def score(l: Literal) -> Tuple[int, int]:
        lang = (l.language or "").lower()
        lang_rank = 0 if (lang in ("", "en")) else 1
        return (lang_rank, len(str(l)))

    return str(sorted(literals, key=score)[0])


def _extract_named_parents_from_bnode(
    g: Graph,
    child: URIRef,
    bnode: BNode,
    parents: Dict[str, Set[str]],
) -> None:
    """Extract named parent classes from OWL class expression blank nodes.

    When a class has ``rdfs:subClassOf`` pointing to a blank node (e.g. an
    ``owl:intersectionOf`` or ``owl:unionOf`` list), the simple URI-to-URI
    parent extraction misses the intended parent.  This helper digs into the
    class expression and adds any named classes it finds as parents, so that
    hierarchy walks can traverse through these constructs.

    Handles:
    - ``owl:intersectionOf (NamedClass Restriction ...)``
    - ``owl:unionOf (NamedClass ...)``
    - Direct ``rdf:type`` / other patterns pointing at named classes
    """
    for list_pred in (OWL.intersectionOf, OWL.unionOf):
        for _, _, rdf_list in g.triples((bnode, list_pred, None)):
            if isinstance(rdf_list, BNode):
                try:
                    col = Collection(g, rdf_list)
                    for item in col:
                        if isinstance(item, URIRef):
                            parents.setdefault(str(child), set()).add(str(item))
                except Exception:
                    pass


def load_full_ontology_index(paths: List[Path]) -> Optional[FullOntologyIndex]:
    """Load and index one or more '*_full.ttl' ontology files.

    Args:
        paths: List of paths to ontology files to load.

    Returns:
        FullOntologyIndex containing merged data, or None if no paths.
    """
    if not paths:
        return None

    g = Graph()
    for p in paths:
        try:
            parse_turtle_safely(g, p)
        except Exception as e:
            LOG.warning("Failed to parse full ontology file '%s': %s", p, e)

    tmp: Dict[str, List[Literal]] = {}
    for s, _, o in g.triples((None, RDFS.label, None)):
        if isinstance(s, URIRef) and isinstance(o, Literal):
            tmp.setdefault(str(s), []).append(o)

    labels: Dict[str, str] = {}
    for iri, lits in tmp.items():
        lbl = best_label(lits)
        if lbl:
            labels[iri] = lbl

    parents: Dict[str, Set[str]] = {}
    for child, _, parent in g.triples((None, RDFS.subClassOf, None)):
        if isinstance(child, URIRef) and isinstance(parent, URIRef):
            parents.setdefault(str(child), set()).add(str(parent))
        elif isinstance(child, URIRef) and isinstance(parent, BNode):
            # Handle OWL class expressions: extract named classes from
            # owl:intersectionOf, owl:unionOf, and owl:equivalentClass
            # constructs so the hierarchy walk doesn't stop at blank nodes.
            _extract_named_parents_from_bnode(g, child, parent, parents)

    # Also extract parents from owl:equivalentClass blank nodes
    for child, _, equiv in g.triples((None, OWL.equivalentClass, None)):
        if isinstance(child, URIRef) and isinstance(equiv, BNode):
            _extract_named_parents_from_bnode(g, child, equiv, parents)

    return FullOntologyIndex(labels=labels, parents=parents)


def resolve_hierarchy_root(root: str) -> URIRef:
    """Resolve a hierarchy root specification to a URI."""
    r = root.strip()
    if not r:
        return URIRef(BFO_ENTITY_IRI)

    if r.lower() == "bfo:entity":
        return URIRef(BFO_ENTITY_IRI)

    if r.startswith("http://") or r.startswith("https://"):
        return URIRef(r)

    if r.upper() == "BFO_0000001":
        return URIRef(BFO_ENTITY_IRI)

    if r.lower().startswith("obo:") and r.upper().endswith("BFO_0000001"):
        return URIRef(BFO_ENTITY_IRI)

    return URIRef(r)


# =============================================================================
# CORE DATA STRUCTURES
# =============================================================================

Node = Union[URIRef, BNode, Literal]


@dataclass(frozen=True)
class NodeInfo:
    """Metadata about a node in the diagram."""
    node_id: str
    label: str
    kind: str  # Class | Individual | Literal | Categorical | SHACL Shape | Constraint
    uri: str


@dataclass
class DiagramResult:
    """Container for the output of diagram rendering."""
    diagram_id: str
    source: str
    format: str
    node_data: Dict[str, Dict[str, str]]

    @property
    def mermaid(self) -> str:
        """Backward-compatible alias for source."""
        return self.source


# =============================================================================
# MAIN CONVERTER CLASS
# =============================================================================

class RdfToDiagram:
    """Converter for transforming RDF/TTL files into visual diagrams.

    This is the main class for diagram generation. See module docstring
    for comprehensive usage examples.
    """

    def __init__(
        self,
        direction: str = "BT",
        output_format: str = "mermaid",
        include_bnodes: bool = True,
        enrich: bool = False,
        superclass_depth: int = 0,
        ontology_cache_dir: Optional[Path] = None,
        ontology_urls: Optional[Dict[str, str]] = None,
        full_ontology: Optional[FullOntologyIndex] = None,
        use_full_hierarchy: bool = True,
        full_hierarchy_root: str = BFO_ENTITY_IRI,
        full_hierarchy_max_depth: int = 50,
        max_nodes: int = 500,
        max_edges: int = 1500,
    ) -> None:
        """Initialize the RDF to diagram converter.

        Args:
            direction: Graph layout direction ('BT', 'TD', 'LR', 'RL').
            output_format: Diagram format ('dot' or 'mermaid').
            include_bnodes: Include blank nodes in output.
            enrich: Enable remote ontology enrichment.
            superclass_depth: Levels of remote superclasses to fetch.
            ontology_cache_dir: Cache directory for downloaded ontologies.
            ontology_urls: Custom prefix-to-URL mapping.
            full_ontology: Pre-loaded FullOntologyIndex for local enrichment.
            use_full_hierarchy: Expand hierarchy from local index.
            full_hierarchy_root: Root class for hierarchy expansion.
            full_hierarchy_max_depth: Maximum hierarchy depth.
            max_nodes: Safety cap on nodes per diagram.
            max_edges: Safety cap on edges per diagram.
        """
        self.direction = direction
        self.output_format = output_format.lower().strip()
        if self.output_format not in ("mermaid", "dot"):
            raise ValueError("output_format must be 'mermaid' or 'dot'")

        self.include_bnodes = include_bnodes
        self.enrich = enrich
        self.superclass_depth = max(0, int(superclass_depth))
        self.max_nodes = max(1, int(max_nodes))
        self.max_edges = max(1, int(max_edges))
        self._pred_label_cache: Dict[str, str] = {}

        self.full_ontology = full_ontology
        self.use_full_hierarchy = bool(use_full_hierarchy and self.full_ontology is not None)
        self.full_hierarchy_root = resolve_hierarchy_root(full_hierarchy_root)
        self.full_hierarchy_max_depth = max(1, int(full_hierarchy_max_depth))

        if self.enrich:
            cache_dir = ontology_cache_dir or Path(".ontology_cache")
            urls = ontology_urls or DEFAULT_ONTOLOGY_URLS
            self.ont = OntologyCache(cache_dir=cache_dir, ontology_urls=urls)
        else:
            self.ont = None

    def _exact_prefix_token(self, g: Graph, uri: URIRef) -> Optional[str]:
        """Get prefix token if URI exactly matches a namespace."""
        u = str(uri)
        for prefix, ns in g.namespace_manager.namespaces():
            if str(ns) == u:
                return str(prefix)
        return None

    @staticmethod
    def _normalize_label(lbl: str) -> str:
        """Normalize a label for use in node IDs."""
        lbl = re.sub(r"\s+", "_", lbl.strip())
        lbl = re.sub(r"[^\w\-]+", "_", lbl).strip("_")
        return lbl or "node"

    def _node_label(self, g: Graph, node: Node) -> str:
        """Generate a human-readable label for a node."""
        if isinstance(node, Literal):
            return str(node)

        if isinstance(node, BNode):
            return f"_:{str(node)}"

        assert isinstance(node, URIRef)

        prefix = obo_prefix_for_iri(str(node))

        token = self._exact_prefix_token(g, node)
        if token:
            if prefix and ":" not in token:
                return f"{prefix}:{token}"
            return token

        local_lits: List[Literal] = [l for l in g.objects(node, RDFS.label) if isinstance(l, Literal)]
        lbl0 = best_label(local_lits)
        if lbl0:
            core = self._normalize_label(lbl0)
            return f"{prefix}:{core}" if prefix else core

        if self.full_ontology is not None:
            lbl1 = self.full_ontology.label_for(node)
            if lbl1:
                core = self._normalize_label(lbl1)
                return f"{prefix}:{core}" if prefix else core

        if self.ont is not None:
            lbl2 = self.ont.label_for(node)
            if lbl2:
                core = self._normalize_label(lbl2)
                return f"{prefix}:{core}" if prefix else core

        try:
            qname = g.namespace_manager.normalizeUri(node)
        except Exception:
            qname = f"<{node}>"

        if qname.startswith("<") and qname.endswith(">"):
            local = uri_local_name(str(node))
            return f"{prefix}:{local}" if prefix else local
        if qname.endswith(":"):
            return qname[:-1]
        return qname

    def _predicate_label(self, g: Graph, pred: URIRef) -> str:
        """Generate a human-readable label for a predicate."""
        if pred == RDF.type:
            return "rdf:type"
        if pred == RDFS.subClassOf:
            return "rdfs:subClassOf"

        prefix = obo_prefix_for_iri(str(pred))

        local_lits: List[Literal] = [l for l in g.objects(pred, RDFS.label) if isinstance(l, Literal)]
        lbl0 = best_label(local_lits)
        if lbl0:
            core = self._normalize_label(lbl0)
            return f"{prefix}:{core}" if prefix else core

        if self.full_ontology is not None:
            lbl1 = self.full_ontology.label_for(pred)
            if lbl1:
                core = self._normalize_label(lbl1)
                return f"{prefix}:{core}" if prefix else core

        if self.ont is not None:
            lbl2 = self.ont.label_for(pred)
            if lbl2:
                core = self._normalize_label(lbl2)
                return f"{prefix}:{core}" if prefix else core

        token = self._exact_prefix_token(g, pred)
        if token:
            if prefix and ":" not in token:
                return f"{prefix}:{token}"
            return token

        try:
            qname = g.namespace_manager.normalizeUri(pred)
        except Exception:
            qname = f"<{pred}>"

        if qname.startswith("<") and qname.endswith(">"):
            local = uri_local_name(str(pred))
            return f"{prefix}:{local}" if prefix else local

        if qname.endswith(":"):
            return qname[:-1]

        return qname

    def _kind_for_uri(self, uri: URIRef, classes: Set[URIRef], shapes: Set[URIRef], categorical: Set[URIRef]) -> str:
        """Determine the semantic kind of a URI node."""
        if uri in shapes:
            return "SHACL Shape"
        if uri in classes:
            return "Class"
        if uri in categorical:
            return "Categorical"
        return "Individual"

    def _style_bucket_for_node(self, uri: Optional[URIRef], kind: str) -> str:
        """Determine the style bucket for a node."""
        if kind == "Literal":
            return "lit"
        if kind == "Constraint":
            return "constraint"
        if kind == "SHACL Shape":
            return "shacl"
        if kind == "Categorical":
            return "cat"
        if kind == "Individual":
            return "ind"

        if uri is not None:
            bucket = obo_prefix_for_iri(str(uri))
            if bucket in CLASSDEF_STYLES:
                return bucket
        return "cls"

    def _extract_list_items(self, g: Graph, head: BNode) -> Optional[List[Node]]:
        """Extract items from an RDF list."""
        try:
            col = Collection(g, head)
            return list(col)
        except Exception:
            return None

    def _add_full_hierarchy(
        self,
        classes: Set[URIRef],
        nodes: Set[Node],
        edges: List[Tuple[Node, URIRef, Node]],
    ) -> None:
        """Expand class hierarchy using the local full ontology index."""
        if not self.use_full_hierarchy or self.full_ontology is None:
            return

        root = self.full_hierarchy_root
        max_depth = self.full_hierarchy_max_depth

        edge_set: Set[Tuple[Node, URIRef, Node]] = set(edges)

        for start in list(classes):
            if not isinstance(start, URIRef):
                continue

            frontier: List[Tuple[URIRef, int]] = [(start, 0)]
            visited: Set[URIRef] = {start}

            while frontier:
                cur, depth = frontier.pop(0)
                if cur == root or depth >= max_depth:
                    continue

                for parent in self.full_ontology.parents_of(cur):
                    if not isinstance(parent, URIRef) or parent in _IMPLICIT_TOP_CLASSES:
                        continue

                    triple = (cur, RDFS.subClassOf, parent)
                    if triple not in edge_set:
                        edges.append(triple)
                        edge_set.add(triple)

                    nodes.add(cur)
                    nodes.add(parent)
                    classes.add(parent)

                    if len(nodes) >= self.max_nodes or len(edges) >= self.max_edges:
                        LOG.warning("Size cap reached while adding full hierarchy; truncating.")
                        return

                    if parent not in visited and parent != root:
                        visited.add(parent)
                        frontier.append((parent, depth + 1))

    def _collect_schema_and_instances(
        self, g: Graph
    ) -> Tuple[Set[URIRef], Set[URIRef], Set[URIRef], Set[Node], List[Tuple[Node, URIRef, Node]]]:
        """Extract all relevant nodes and edges from an RDF graph."""
        classes: Set[URIRef] = set()
        shapes: Set[URIRef] = set()
        categorical: Set[URIRef] = set()
        nodes: Set[Node] = set()
        edges: List[Tuple[Node, URIRef, Node]] = []

        for s, _, o in g.triples((None, RDF.type, None)):
            if isinstance(o, URIRef):
                if o in (SH.NodeShape, SH.PropertyShape, SH.Shape):
                    if isinstance(s, URIRef):
                        shapes.add(s)
                if o in (OWL.Class, RDFS.Class):
                    if isinstance(s, URIRef):
                        classes.add(s)
                if o not in _IMPLICIT_TOP_CLASSES:
                    classes.add(o)

        for s, _, o in g.triples((None, RDFS.subClassOf, None)):
            if isinstance(o, URIRef) and o in _IMPLICIT_TOP_CLASSES:
                continue
            if isinstance(s, URIRef):
                classes.add(s)
            if isinstance(o, URIRef):
                classes.add(o)

        for _, _, o in g.triples((None, SH["in"], None)):
            if isinstance(o, BNode):
                items = self._extract_list_items(g, o)
                if items:
                    for it in items:
                        if isinstance(it, URIRef):
                            categorical.add(it)

        SHACL_LIST_PREDICATES = {SH["in"], SH["or"], SH["and"], SH["xone"], SH["not"]}

        for s, p, o in g:
            if not isinstance(p, URIRef):
                continue

            if p in (RDF.first, RDF.rest):
                continue

            if p == RDF.type and o == OWL.Ontology:
                continue

            if (isinstance(s, URIRef) and s in _IMPLICIT_TOP_CLASSES) or \
               (isinstance(o, URIRef) and o in _IMPLICIT_TOP_CLASSES):
                continue

            if p in SHACL_LIST_PREDICATES and isinstance(o, BNode):
                items = self._extract_list_items(g, o)
                if items:
                    for it in items:
                        edges.append((s, p, it))
                        nodes.add(s)
                        nodes.add(it)
                    continue

            if not self.include_bnodes and (isinstance(s, BNode) or isinstance(o, BNode)):
                continue

            edges.append((s, p, o))
            nodes.add(s)
            nodes.add(o)

        if len(nodes) > self.max_nodes:
            LOG.warning("Node count %d exceeds max_nodes=%d; truncating.", len(nodes), self.max_nodes)
            ordered = sorted(nodes, key=lambda n: (0 if isinstance(n, URIRef) else 1 if isinstance(n, BNode) else 2, str(n)))
            nodes = set(ordered[: self.max_nodes])

        if len(edges) > self.max_edges:
            LOG.warning("Edge count %d exceeds max_edges=%d; truncating.", len(edges), self.max_edges)
            edges = edges[: self.max_edges]

        if self.enrich and self.superclass_depth > 0 and self.ont is not None:
            extra: Set[Tuple[URIRef, URIRef]] = set()
            for c in list(classes):
                extra |= self.ont.superclasses(c, self.superclass_depth)
            for child, parent in extra:
                if parent in _IMPLICIT_TOP_CLASSES:
                    continue
                edges.append((child, RDFS.subClassOf, parent))
                nodes.add(child)
                nodes.add(parent)
                classes.add(child)
                classes.add(parent)

        if self.use_full_hierarchy:
            self._add_full_hierarchy(classes, nodes, edges)

        return classes, shapes, categorical, nodes, edges

    def _assign_ids_and_metadata(
        self,
        g: Graph,
        diagram_id: str,
        classes: Set[URIRef],
        shapes: Set[URIRef],
        categorical: Set[URIRef],
        nodes: Set[Node],
    ) -> Tuple[Dict[Node, NodeInfo], Dict[str, Dict[str, str]]]:
        """Assign unique IDs and collect metadata for all nodes."""
        def node_sort_key(n: Node) -> Tuple[int, str]:
            if isinstance(n, URIRef):
                return (0, str(n))
            if isinstance(n, BNode):
                return (1, str(n))
            return (2, str(n))

        used_ids: Set[str] = set()
        node_infos: Dict[Node, NodeInfo] = {}
        node_data: Dict[str, Dict[str, str]] = {}

        for n in sorted(nodes, key=node_sort_key):
            label = self._node_label(g, n)

            if isinstance(n, Literal):
                kind = "Literal"
                uri = ""
                base = "val_" + safe_mermaid_id(str(n))

            elif isinstance(n, BNode):
                kind = "Constraint"
                uri = ""
                base = "bn_" + safe_mermaid_id(str(n))

            else:
                assert isinstance(n, URIRef)
                kind = self._kind_for_uri(n, classes, shapes, categorical)
                uri = str(n)

                token = self._exact_prefix_token(g, n)
                if token:
                    base = safe_mermaid_id(token)
                else:
                    try:
                        qname = g.namespace_manager.normalizeUri(n)
                    except Exception:
                        qname = uri_local_name(uri)

                    if qname.startswith("<") and qname.endswith(">"):
                        qname = uri_local_name(uri)

                    qname = qname.replace(":", "_")
                    base = safe_mermaid_id(qname)

            node_id = base
            if node_id in used_ids:
                suffix = abs(hash((diagram_id, str(n)))) % 100000
                node_id = f"{base}_{suffix}"
            used_ids.add(node_id)

            info = NodeInfo(node_id=node_id, label=label, kind=kind, uri=uri)
            node_infos[n] = info
            node_data[node_id] = {"label": label, "type": kind, "uri": uri}

        return node_infos, node_data

    def _set_predicate_cache(self, g: Graph, edges: List[Tuple[Node, URIRef, Node]]) -> None:
        """Pre-compute labels for all predicates."""
        self._pred_label_cache = {}
        for _, p, _ in edges:
            if isinstance(p, URIRef):
                self._pred_label_cache[str(p)] = self._predicate_label(g, p)

    def _build_mermaid(
        self,
        node_infos: Dict[Node, NodeInfo],
        edges: List[Tuple[Node, URIRef, Node]],
    ) -> str:
        """Build Mermaid flowchart source from nodes and edges."""
        class_nodes: List[NodeInfo] = []
        shape_nodes: List[NodeInfo] = []
        constraint_nodes: List[NodeInfo] = []
        abox_nodes: List[NodeInfo] = []
        lit_nodes: List[NodeInfo] = []

        style_bucket_by_id: Dict[str, str] = {}

        for n, info in node_infos.items():
            if info.kind == "Literal":
                lit_nodes.append(info)
                style_bucket_by_id[info.node_id] = "lit"
            elif info.kind == "Constraint":
                constraint_nodes.append(info)
                style_bucket_by_id[info.node_id] = "constraint"
            elif info.kind == "SHACL Shape":
                shape_nodes.append(info)
                style_bucket_by_id[info.node_id] = "shacl"
            elif info.kind == "Class":
                class_nodes.append(info)
                style_bucket_by_id[info.node_id] = self._style_bucket_for_node(n if isinstance(n, URIRef) else None, info.kind)
            elif info.kind == "Categorical":
                abox_nodes.append(info)
                style_bucket_by_id[info.node_id] = "cat"
            else:
                abox_nodes.append(info)
                style_bucket_by_id[info.node_id] = "ind"

        for group in (class_nodes, shape_nodes, constraint_nodes, abox_nodes, lit_nodes):
            group.sort(key=lambda ni: ni.node_id)

        lines: List[str] = [f"flowchart {self.direction}"]

        def emit_subgraph(name: str, node_list: List[NodeInfo]) -> None:
            if not node_list:
                return
            lines.append(f'subgraph {name}[" "]')
            lines.append(f"direction {self.direction}")
            for info in node_list:
                lines.append(f'  {info.node_id}["{escape_mermaid_label(info.label)}"]')
            lines.append("end")

        if class_nodes:
            emit_subgraph("TBOX", class_nodes)
        if shape_nodes:
            emit_subgraph("SHAPES", shape_nodes)
        if constraint_nodes:
            emit_subgraph("CONSTRAINTS", constraint_nodes)
        if abox_nodes:
            emit_subgraph("ABOX", abox_nodes)

        for info in lit_nodes:
            lines.append(f'  {info.node_id}["{escape_mermaid_label(info.label)}"]')

        filtered: List[Tuple[str, str, str, bool]] = []
        for s, p, o in edges:
            if s not in node_infos or o not in node_infos or not isinstance(p, URIRef):
                continue
            sid = node_infos[s].node_id
            oid = node_infos[o].node_id
            plabel = self._pred_label_cache.get(str(p), uri_local_name(str(p)))
            is_type = (p == RDF.type)
            filtered.append((sid, plabel, oid, is_type))

        filtered.sort(key=lambda t: (t[0], t[1], t[2]))

        for sid, plabel, oid, is_type in filtered:
            if is_type:
                lines.append(f"  {sid} -.->|rdf:type| {oid}")
            else:
                lines.append(f"  {sid} -->|{escape_mermaid_label(plabel)}| {oid}")

        used_style_classes = sorted(set(style_bucket_by_id.values()))
        for cls_name in used_style_classes:
            style = CLASSDEF_STYLES.get(cls_name)
            if style:
                lines.append(f"classDef {cls_name} {style};")

        for cls_name in used_style_classes:
            node_ids = sorted([nid for nid, b in style_bucket_by_id.items() if b == cls_name])
            for part in chunked(node_ids, n=12):
                lines.append(f"class {','.join(part)} {cls_name};")

        for sg in ("TBOX", "SHAPES", "CONSTRAINTS", "ABOX"):
            if any(l.startswith(f"subgraph {sg}") for l in lines):
                lines.append(f"style {sg} fill:transparent,stroke:transparent;")

        return "\n".join(lines)

    def _build_graphviz(
        self,
        node_infos: Dict[Node, NodeInfo],
        edges: List[Tuple[Node, URIRef, Node]],
    ) -> str:
        """Build Graphviz DOT source from nodes and edges."""
        class_nodes: List[NodeInfo] = []
        shape_nodes: List[NodeInfo] = []
        constraint_nodes: List[NodeInfo] = []
        abox_nodes: List[NodeInfo] = []
        lit_nodes: List[NodeInfo] = []

        style_bucket_by_id: Dict[str, str] = {}

        def kind_shape(kind: str) -> str:
            return {
                "Class": "box",
                "Individual": "ellipse",
                "Categorical": "box",
                "SHACL Shape": "hexagon",
                "Constraint": "diamond",
                "Literal": "note",
            }.get(kind, "box")

        for n, info in node_infos.items():
            if info.kind == "Literal":
                lit_nodes.append(info)
                style_bucket_by_id[info.node_id] = "lit"
            elif info.kind == "Constraint":
                constraint_nodes.append(info)
                style_bucket_by_id[info.node_id] = "constraint"
            elif info.kind == "SHACL Shape":
                shape_nodes.append(info)
                style_bucket_by_id[info.node_id] = "shacl"
            elif info.kind == "Class":
                class_nodes.append(info)
                style_bucket_by_id[info.node_id] = self._style_bucket_for_node(n if isinstance(n, URIRef) else None, info.kind)
            elif info.kind == "Categorical":
                abox_nodes.append(info)
                style_bucket_by_id[info.node_id] = "cat"
            else:
                abox_nodes.append(info)
                style_bucket_by_id[info.node_id] = "ind"

        for group in (class_nodes, shape_nodes, constraint_nodes, abox_nodes, lit_nodes):
            group.sort(key=lambda ni: ni.node_id)

        rankdir = {"TD": "TB", "BT": "BT", "LR": "LR", "RL": "RL"}.get(self.direction, "BT")

        lines: List[str] = []
        lines.append("digraph G {")
        lines.append(f'  rankdir="{rankdir}";')
        lines.append('  graph [bgcolor="transparent",compound="true",splines="true"];')
        lines.append('  node  [fontname="Arial",fontsize="10"];')
        lines.append('  edge  [fontname="Arial",fontsize="9"];')

        def emit_nodes(node_list: List[NodeInfo]) -> None:
            for info in node_list:
                bucket = style_bucket_by_id.get(info.node_id, "cls")
                style = GRAPHVIZ_NODE_STYLES.get(bucket, GRAPHVIZ_NODE_STYLES["cls"])
                attrs: Dict[str, str] = {
                    "shape": kind_shape(info.kind),
                    "style": "filled",
                    "margin": "0.2,0.1",
                    **style,
                }
                if info.kind == "Class":
                    escaped_label = info.label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    font_color = style.get("fontcolor", "#333333")
                    attrs["label"] = f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4"><TR><TD><B><FONT COLOR="{font_color}">{escaped_label}</FONT></B></TD></TR></TABLE>>'
                else:
                    attrs["label"] = info.label
                if info.uri:
                    attrs["tooltip"] = info.uri
                    attrs["URL"] = info.uri
                    attrs["target"] = "_blank"
                lines.append(f'    "{info.node_id}"{dot_attrs(attrs)};')

        def emit_cluster(cluster_name: str, node_list: List[NodeInfo]) -> None:
            if not node_list:
                return
            lines.append(f'  subgraph "cluster_{cluster_name}" {{')
            lines.append('    label="";')
            lines.append('    color="transparent";')
            lines.append('    penwidth="0";')
            lines.append('    style="rounded";')
            emit_nodes(node_list)
            lines.append("  }")

        if class_nodes:
            emit_cluster("TBOX", class_nodes)
        if shape_nodes:
            emit_cluster("SHAPES", shape_nodes)
        if constraint_nodes:
            emit_cluster("CONSTRAINTS", constraint_nodes)
        if abox_nodes:
            emit_cluster("ABOX", abox_nodes)

        emit_nodes(lit_nodes)

        filtered: List[Tuple[str, str, str, bool]] = []
        for s, p, o in edges:
            if s not in node_infos or o not in node_infos or not isinstance(p, URIRef):
                continue
            sid = node_infos[s].node_id
            oid = node_infos[o].node_id
            plabel = self._pred_label_cache.get(str(p), uri_local_name(str(p)))
            is_type = (p == RDF.type)
            filtered.append((sid, plabel, oid, is_type))

        filtered.sort(key=lambda t: (t[0], t[1], t[2]))
        for sid, plabel, oid, is_type in filtered:
            attrs: Dict[str, str] = {"label": plabel}
            if is_type:
                attrs["style"] = "dashed"
            lines.append(f'  "{sid}" -> "{oid}"{dot_attrs(attrs)};')

        lines.append("}")
        return "\n".join(lines)

    def render_graph(
        self,
        ttl_path: Path,
        diagram_id: Optional[str] = None,
        use_full_hierarchy: Optional[bool] = None,
        full_hierarchy_max_depth: Optional[int] = None,
    ) -> DiagramResult:
        """Render a TTL file to a diagram.

        Args:
            ttl_path: Path to the Turtle file to render.
            diagram_id: Custom diagram identifier (default: derived from filename).
            use_full_hierarchy: Override instance setting for this call.
            full_hierarchy_max_depth: Override instance setting for this call.

        Returns:
            DiagramResult containing the rendered source and metadata.
        """
        orig_use = self.use_full_hierarchy
        orig_depth = self.full_hierarchy_max_depth
        try:
            if use_full_hierarchy is not None:
                self.use_full_hierarchy = bool(use_full_hierarchy and self.full_ontology is not None)
            if full_hierarchy_max_depth is not None:
                self.full_hierarchy_max_depth = max(1, int(full_hierarchy_max_depth))

            g = Graph()
            parse_turtle_safely(g, ttl_path)

            did = diagram_id or slugify(ttl_path.stem)

            classes, shapes, categorical, nodes, edges = self._collect_schema_and_instances(g)
            node_infos, node_data = self._assign_ids_and_metadata(g, did, classes, shapes, categorical, nodes)
            self._set_predicate_cache(g, edges)

            if self.output_format == "dot":
                src = self._build_graphviz(node_infos, edges)
            else:
                src = self._build_mermaid(node_infos, edges)

            return DiagramResult(diagram_id=did, source=src, format=self.output_format, node_data=node_data)
        finally:
            self.use_full_hierarchy = orig_use
            self.full_hierarchy_max_depth = orig_depth


# =============================================================================
# JAVASCRIPT AND HTML INTEGRATION
# =============================================================================

def js_escape_template_literal(s: str) -> str:
    """Escape a string for use in JavaScript template literals."""
    s = s.replace("\\", "\\\\")
    s = s.replace("`", "\\`")
    s = s.replace("${", "\\${")
    return s


def write_js(diagrams: Dict[str, str], node_data: Dict[str, Dict[str, Dict[str, str]]], out_js: Path) -> None:
    """Write diagrams and node data to a JavaScript file."""
    lines: List[str] = []
    lines.append("// Auto-generated by ttl_to_graphviz.py. Do not edit manually.")
    lines.append("const diagrams = {")
    for k in sorted(diagrams.keys()):
        code = js_escape_template_literal(diagrams[k])
        lines.append(f'  "{k}": `{code}`,')
        lines.append("")
    if lines and lines[-1] == "":
        lines.pop()
    lines.append("};")
    lines.append("")
    lines.append("const nodeData = " + json.dumps(node_data, ensure_ascii=False, indent=2) + ";")
    lines.append("")
    out_js.write_text("\n".join(lines), encoding="utf-8")
    LOG.info("Wrote JS: %s", out_js)


def patch_html(html_path: Path, diagrams_js_block: str, node_data_js_block: str, out_path: Optional[Path] = None) -> Path:
    """Patch an HTML file with new diagram and node data blocks."""
    text = html_path.read_text(encoding="utf-8")

    m1 = re.search(r"\bconst\s+diagrams\s*=\s*\{", text)
    m2 = re.search(r"\bconst\s+nodeData\s*=\s*\{", text)
    m3 = re.search(r"//\s*=+\s*GRAPH VIEWER CLASS\s*=+", text)

    if not (m1 and m2 and m3) or not (m1.start() < m2.start() < m3.start()):
        raise RuntimeError(
            "Could not locate 'const diagrams', 'const nodeData', and 'GRAPH VIEWER CLASS' markers in HTML."
        )

    diag_line_start = text.rfind("\n", 0, m1.start()) + 1
    indent = re.match(r"[ \t]*", text[diag_line_start:m1.start()]).group(0)

    before = text[:m1.start()].rstrip("\n")
    after = text[m3.start():]

    new_text = "\n".join(
        [
            before,
            "",
            indent + diagrams_js_block.replace("\n", "\n" + indent),
            "",
            indent + node_data_js_block.replace("\n", "\n" + indent),
            "",
            after,
        ]
    )

    out = out_path or html_path
    out.write_text(new_text, encoding="utf-8")
    LOG.info("Patched HTML: %s", out)
    return out


def discover_graph_ids_from_html(html_path: Path) -> List[str]:
    """Extract graph container IDs from an HTML file."""
    text = html_path.read_text(encoding="utf-8")
    ids = re.findall(r'id="graph-([a-zA-Z0-9\-]+)"', text)
    seen: Set[str] = set()
    ordered: List[str] = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            ordered.append(i)
    return ordered


def resolve_ttl_for_id(ttl_dir: Path, diagram_id: str) -> Optional[Path]:
    """Find a TTL file matching a diagram ID."""
    exact = ttl_dir / f"{diagram_id}.ttl"
    if exact.exists():
        return exact

    cands = [p for p in ttl_dir.glob("*.ttl") if not p.name.endswith("_full.ttl")]
    ends = [p for p in cands if p.stem.lower().endswith(diagram_id.lower())]
    if len(ends) == 1:
        return ends[0]
    if len(ends) > 1:
        ends.sort(key=lambda p: len(p.stem))
        return ends[0]
    return None


# =============================================================================
# COMMAND-LINE INTERFACE
# =============================================================================

def build_arg_parser() -> argparse.ArgumentParser:
    """Build the argument parser for command-line usage."""
    p = argparse.ArgumentParser(
        description="Convert Turtle (.ttl) ontology patterns into Mermaid or Graphviz DOT diagrams.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Print DOT for a single TTL file
  python ttl_to_graphviz.py --ttl pattern.ttl --format dot

  # Generate JS file for all TTLs in a directory
  python ttl_to_graphviz.py --ttl-dir ./patterns --format dot --out-js diagrams.js

  # Patch patterns.html with generated diagrams
  python ttl_to_graphviz.py --ttl-dir ./patterns --format dot --html patterns.html --patch-html
        """
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--ttl", type=Path, help="Single TTL file to convert.")
    src.add_argument("--ttl-dir", type=Path, help="Directory of TTL files to convert.")

    p.add_argument("--format", default="mermaid", choices=["mermaid", "dot"], help="Diagram output format.")
    p.add_argument("--direction", default="BT", choices=["BT", "TD", "LR", "RL"], help="Diagram flow direction.")
    p.add_argument("--no-bnodes", action="store_true", help="Exclude blank nodes (BNodes) from diagrams.")

    p.add_argument("--enrich", action="store_true", help="Enable remote ontology enrichment.")
    p.add_argument("--superclass-depth", type=int, default=0, help="With --enrich, include up to N rdfs:subClassOf levels.")
    p.add_argument("--ontology-cache", type=Path, default=Path(".ontology_cache"), help="Cache directory for downloaded ontologies.")

    p.add_argument(
        "--full-ontology",
        type=Path,
        action="append",
        help="Path to local '*_full.ttl' ontology file(s).",
    )
    p.add_argument("--no-full-hierarchy", action="store_true", help="Disable hierarchy expansion from local ontology files.")
    p.add_argument("--hierarchy-root", default="bfo:entity", help="Root IRI/CURIE for hierarchy expansion.")
    p.add_argument("--hierarchy-max-depth", type=int, default=50, help="Maximum rdfs:subClassOf hops.")

    p.add_argument("--out-js", type=Path, help="Write JavaScript file with diagrams/nodeData.")
    p.add_argument("--html", type=Path, help="HTML file to patch.")
    p.add_argument("--patch-html", action="store_true", help="Patch --html in-place.")
    p.add_argument("--out-html", type=Path, help="Write patched HTML to this path.")

    p.add_argument("--max-nodes", type=int, default=500, help="Safety cap on nodes per diagram.")
    p.add_argument("--max-edges", type=int, default=1500, help="Safety cap on edges per diagram.")
    p.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Log verbosity.")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for command-line usage."""
    args = build_arg_parser().parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s: %(message)s")

    base_dir = args.ttl.parent if args.ttl is not None else args.ttl_dir
    if base_dir is None:
        LOG.error("Cannot determine input base directory.")
        return 2

    full_paths = args.full_ontology or discover_full_ontology_files(base_dir)
    full_index = load_full_ontology_index(full_paths) if full_paths else None
    if full_paths:
        LOG.info("Using full ontology file(s): %s", ", ".join(str(p) for p in full_paths))
    if full_index is not None:
        LOG.info(
            "Full ontology index loaded (labels=%d, subclass-edges=%d).",
            len(full_index.labels),
            sum(len(v) for v in full_index.parents.values()),
        )

    gen = RdfToDiagram(
        direction=args.direction,
        output_format=args.format,
        include_bnodes=not args.no_bnodes,
        enrich=args.enrich,
        superclass_depth=args.superclass_depth,
        ontology_cache_dir=args.ontology_cache,
        full_ontology=full_index,
        use_full_hierarchy=not args.no_full_hierarchy,
        full_hierarchy_root=args.hierarchy_root,
        full_hierarchy_max_depth=args.hierarchy_max_depth,
        max_nodes=args.max_nodes,
        max_edges=args.max_edges,
    )

    diagrams: Dict[str, str] = {}
    node_data: Dict[str, Dict[str, Dict[str, str]]] = {}

    if args.ttl is not None:
        res = gen.render_graph(args.ttl)
        diagrams[res.diagram_id] = res.source
        node_data[res.diagram_id] = res.node_data

        if not args.out_js and not (args.html and args.patch_html):
            sys.stdout.write(res.source + "\n")
            return 0
    else:
        ttl_dir: Path = args.ttl_dir
        if not ttl_dir.exists() or not ttl_dir.is_dir():
            LOG.error("--ttl-dir does not exist or is not a directory: %s", ttl_dir)
            return 2

        if args.html and args.patch_html:
            ids = discover_graph_ids_from_html(args.html)
            if not ids:
                LOG.warning("No graph container IDs found in %s. Processing all TTL files.", args.html)
                ttl_files = sorted([p for p in ttl_dir.glob("*.ttl") if not p.name.endswith("_full.ttl")])
                for f in ttl_files:
                    res = gen.render_graph(f)
                    diagrams[res.diagram_id] = res.source
                    node_data[res.diagram_id] = res.node_data
            else:
                for did in ids:
                    ttl = resolve_ttl_for_id(ttl_dir, did)
                    if not ttl:
                        LOG.warning("No TTL file found for id '%s' in %s; skipping.", did, ttl_dir)
                        continue
                    res = gen.render_graph(ttl, diagram_id=did)
                    diagrams[did] = res.source
                    node_data[did] = res.node_data
        else:
            ttl_files = sorted([p for p in ttl_dir.glob("*.ttl") if not p.name.endswith("_full.ttl")])
            if not ttl_files:
                LOG.error("No .ttl files found in %s", ttl_dir)
                return 2
            for f in ttl_files:
                res = gen.render_graph(f)
                diagrams[res.diagram_id] = res.source
                node_data[res.diagram_id] = res.node_data

    if args.out_js:
        write_js(diagrams, node_data, args.out_js)

    if args.html and args.patch_html:
        diagrams_block = "const diagrams = {\n" + "\n".join(
            [f'  "{k}": `{js_escape_template_literal(diagrams[k])}`,' for k in sorted(diagrams.keys())]
        ) + "\n};"
        node_block = "const nodeData = " + json.dumps(node_data, ensure_ascii=False, indent=2) + ";"
        patch_html(args.html, diagrams_block, node_block, out_path=args.out_html)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
