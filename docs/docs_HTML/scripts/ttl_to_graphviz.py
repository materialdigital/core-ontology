#!/usr/bin/env python3
"""
ttl_to_mermaid.py

Generate diagram sources from RDF Turtle (.ttl) files in either:
  - Mermaid flowchart format ("mermaid")
  - Graphviz DOT format ("dot")

Primary outputs:
- Diagram source suitable for embedding in HTML (as a string).
- (Optional) a JS file that defines:
    const diagrams = { "<id>": `...source...`, ... };
    const nodeData = { "<id>": { "<nodeId>": {label,type,uri}, ... }, ... };

Integration:
- Can patch a patterns.html-style file by replacing its `const diagrams = {...}` and
  `const nodeData = {...}` blocks.

Dependency:
  pip install rdflib

Examples:
  # Print Mermaid for a single TTL file
  python ttl_to_mermaid.py --ttl ./patterns/temporal-region.ttl --format mermaid

  # Print DOT for a single TTL file
  python ttl_to_mermaid.py --ttl ./patterns/temporal-region.ttl --format dot

  # Generate a JS file for all TTLs in a directory (DOT)
  python ttl_to_mermaid.py --ttl-dir ./patterns --format dot --out-js ./generated_diagrams.js

  # Patch patterns.html in-place (only generates diagrams for IDs present in the HTML)
  python ttl_to_mermaid.py --ttl-dir ./patterns --format mermaid --html ./patterns.html --patch-html

Optional enrichment:
  --enrich enables best-effort downloading/caching of selected ontologies (BFO/OBI/IAO/RO/UO)
  to resolve rdfs:label and superclass chains. If downloads fail, the script falls back to
  QName-based labels.

Local ontology enrichment (recommended for completeness):
  Place one or more *_full.ttl files alongside patterns. These are auto-discovered and used to:
    - resolve rdfs:label for IRIs
    - expand rdfs:subClassOf chains up to a root (default BFO entity)

Notes on Turtle prefix style:
Some pattern TTLs define prefixes that point to a *single term IRI*:
    @prefix process: <.../BFO_0000015> .
and then use the empty-local QName `process:`. rdflib does not normalize these into QNames.
This script detects such "exact-prefix" definitions and uses the prefix token (e.g., "process")
for labels and stable node IDs.
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

# SHACL namespace (used if present)
SH = Namespace("http://www.w3.org/ns/shacl#")

LOG = logging.getLogger("ttl_to_mermaid")

# -----------------------------
# Styling (Mermaid classDefs)
# -----------------------------
CLASSDEF_STYLES: Dict[str, str] = {
    # Generic
    "cls": "fill:#b34dff,stroke:#4a148c,stroke-width:2px,color:#fff",
    "ind": "fill:#e8f0ff,stroke:#1e40af,stroke-width:2px,color:#0b1220",
    "lit": "fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#78350f",
    "cat": "fill:#d1fae5,stroke:#059669,stroke-width:2px,color:#064e3b",
    "shacl": "fill:#22d3ee,stroke:#0891b2,stroke-width:2px,color:#042f2e",
    "constraint": "fill:#fb923c,stroke:#ea580c,stroke-width:2px,color:#431407",
    # Ontology buckets (commonly used in patterns)
    "bfo": "fill:#b34dff,stroke:#7c3aed,stroke-width:2px,color:#fff",
    "obi": "fill:#a78bbc,stroke:#7c5c8f,stroke-width:2px,color:#fff",
    "pmd": "fill:#6b7fa3,stroke:#4a5568,stroke-width:2px,color:#fff",
}

# -----------------------------
# Styling (Graphviz nodes)
# -----------------------------
GRAPHVIZ_NODE_STYLES: Dict[str, Dict[str, str]] = {
    "cls": {"fillcolor": "#b34dff", "color": "#4a148c", "penwidth": "2", "fontcolor": "#ffffff"},
    "ind": {"fillcolor": "#e8f0ff", "color": "#1e40af", "penwidth": "2", "fontcolor": "#0b1220"},
    "lit": {"fillcolor": "#fef3c7", "color": "#d97706", "penwidth": "2", "fontcolor": "#78350f"},
    "cat": {"fillcolor": "#d1fae5", "color": "#059669", "penwidth": "2", "fontcolor": "#064e3b"},
    "shacl": {"fillcolor": "#22d3ee", "color": "#0891b2", "penwidth": "2", "fontcolor": "#042f2e"},
    "constraint": {"fillcolor": "#fb923c", "color": "#ea580c", "penwidth": "2", "fontcolor": "#431407"},
    "bfo": {"fillcolor": "#b34dff", "color": "#7c3aed", "penwidth": "2", "fontcolor": "#ffffff"},
    "obi": {"fillcolor": "#a78bbc", "color": "#7c5c8f", "penwidth": "2", "fontcolor": "#ffffff"},
    "pmd": {"fillcolor": "#6b7fa3", "color": "#4a5568", "penwidth": "2", "fontcolor": "#ffffff"},
}

# Ontology download targets (best-effort; only used with --enrich)
DEFAULT_ONTOLOGY_URLS: Dict[str, str] = {
    "bfo": "http://purl.obolibrary.org/obo/bfo.owl",
    "obi": "http://purl.obolibrary.org/obo/obi.owl",
    "iao": "http://purl.obolibrary.org/obo/iao.owl",
    "ro": "http://purl.obolibrary.org/obo/ro.owl",
    "uo": "http://purl.obolibrary.org/obo/uo.owl",
}

# Root class for BFO (entity)
BFO_ENTITY_IRI = "http://purl.obolibrary.org/obo/BFO_0000001"

# -----------------------------
# Parsing hardening
# -----------------------------
def parse_turtle_safely(g: Graph, path: Path) -> None:
    """
    Parse Turtle content with light hardening.
    Normalizes non-breaking spaces (U+00A0) to spaces to avoid rdflib parser issues.
    """
    data = path.read_text(encoding="utf-8", errors="replace").replace("\u00a0", " ")
    g.parse(data=data, format="turtle", publicID=str(path.resolve().as_uri()))


# -----------------------------
# Helpers
# -----------------------------
def slugify(stem: str) -> str:
    s = stem.strip().lower()
    s = re.sub(r"[^\w\-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "diagram"


def escape_mermaid_label(label: str) -> str:
    """
    Escape label for Mermaid node/edge text.
    """
    label = label.replace("&", "&amp;")
    label = label.replace('"', "&quot;")
    label = label.replace("[", "&#91;").replace("]", "&#93;")
    label = label.replace("\n", "<br/>")
    return label


def escape_dot_label(label: str) -> str:
    """
    Escape label for Graphviz DOT quoted strings.
    """
    label = label.replace("\\", "\\\\")
    label = label.replace('"', '\\"')
    label = label.replace("\r\n", "\n").replace("\r", "\n")
    label = label.replace("\n", "\\n")
    return label


def dot_attrs(attrs: Dict[str, str]) -> str:
    """
    Build DOT attribute list: [k="v",...]
    """
    if not attrs:
        return ""
    parts = []
    for k in sorted(attrs.keys()):
        parts.append(f'{k}="{escape_dot_label(str(attrs[k]))}"')
    return " [" + ",".join(parts) + "]"


def chunked(items: List[str], n: int = 10) -> Iterable[List[str]]:
    for i in range(0, len(items), n):
        yield items[i : i + n]


def uri_local_name(uri: str) -> str:
    if "#" in uri:
        return uri.rsplit("#", 1)[1]
    return uri.rstrip("/").rsplit("/", 1)[-1]


def obo_prefix_for_iri(iri: str) -> Optional[str]:
    """
    Detect common ontology bucket based on IRI patterns.
    Returns token (bfo, obi, iao, ro, uo, pmd) or None.
    """
    if "purl.obolibrary.org/obo/" in iri:
        local = iri.split("/obo/", 1)[1]
        m = re.match(r"^([A-Za-z]+)_\d+$", local)
        if m:
            return m.group(1).lower()
    if "w3id.org/pmd/" in iri:
        return "pmd"
    return None


def safe_mermaid_id(raw: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_]", "_", raw)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        s = "n"
    if s[0].isdigit():
        s = "n_" + s
    return s


# -----------------------------
# Ontology cache (optional enrichment)
# -----------------------------
class OntologyCache:
    def __init__(self, cache_dir: Path, ontology_urls: Dict[str, str]) -> None:
        self.cache_dir = cache_dir
        self.ontology_urls = ontology_urls
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._graphs: Dict[str, Graph] = {}

    def _cached_path(self, key: str, url: str) -> Path:
        h = re.sub(r"[^a-zA-Z0-9]+", "_", url)[:40]
        return self.cache_dir / f"{key}-{h}.rdf"

    def ensure_loaded(self, key: str) -> Optional[Graph]:
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
                if isinstance(parent, URIRef):
                    edges.add((cur, parent))
                    if parent not in seen:
                        seen.add(parent)
                        frontier.append((parent, depth + 1))
        return edges


# -----------------------------
# Full-ontology index (local *_full.ttl)
# -----------------------------
@dataclass
class FullOntologyIndex:
    """
    Lightweight index over one or more '*_full.ttl' ontology files.

    Indexes:
      - rdfs:label for IRIs (language-pref)
      - rdfs:subClassOf edges between named classes
    """

    labels: Dict[str, str]
    parents: Dict[str, Set[str]]

    def label_for(self, uri: URIRef) -> Optional[str]:
        return self.labels.get(str(uri))

    def parents_of(self, uri: URIRef) -> Set[URIRef]:
        return {URIRef(p) for p in self.parents.get(str(uri), set())}


def discover_full_ontology_files(base_dir: Path) -> List[Path]:
    return sorted([p for p in base_dir.glob("*_full.ttl") if p.is_file()])


def best_label(literals: List[Literal]) -> Optional[str]:
    if not literals:
        return None

    def score(l: Literal) -> Tuple[int, int]:
        lang = (l.language or "").lower()
        lang_rank = 0 if (lang in ("", "en")) else 1
        return (lang_rank, len(str(l)))

    return str(sorted(literals, key=score)[0])


def load_full_ontology_index(paths: List[Path]) -> Optional[FullOntologyIndex]:
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

    return FullOntologyIndex(labels=labels, parents=parents)


def resolve_hierarchy_root(root: str) -> URIRef:
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


# -----------------------------
# Core generation
# -----------------------------
Node = Union[URIRef, BNode, Literal]


@dataclass(frozen=True)
class NodeInfo:
    node_id: str
    label: str
    kind: str  # Class | Individual | Literal | Categorical | SHACL Shape | Constraint
    uri: str   # "" for literals/bnodes


@dataclass
class DiagramResult:
    diagram_id: str
    source: str           # Mermaid or DOT source
    format: str           # "mermaid" | "dot"
    node_data: Dict[str, Dict[str, str]]  # node_id -> {label,type,uri}

    @property
    def mermaid(self) -> str:
        # Backward-compatible alias: existing callers expecting .mermaid still work.
        return self.source


class RdfToDiagram:
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

    # -------- labels / IDs --------
    def _exact_prefix_token(self, g: Graph, uri: URIRef) -> Optional[str]:
        u = str(uri)
        for prefix, ns in g.namespace_manager.namespaces():
            if str(ns) == u:
                return str(prefix)
        return None

    @staticmethod
    def _normalize_label(lbl: str) -> str:
        lbl = re.sub(r"\s+", "_", lbl.strip())
        lbl = re.sub(r"[^\w\-]+", "_", lbl).strip("_")
        return lbl or "node"

    def _node_label(self, g: Graph, node: Node) -> str:
        if isinstance(node, Literal):
            return str(node)

        if isinstance(node, BNode):
            return f"_:{str(node)}"

        assert isinstance(node, URIRef)

        token = self._exact_prefix_token(g, node)
        if token:
            return token

        local_lits: List[Literal] = [l for l in g.objects(node, RDFS.label) if isinstance(l, Literal)]
        lbl0 = best_label(local_lits)
        if lbl0:
            return self._normalize_label(lbl0)

        if self.full_ontology is not None:
            lbl1 = self.full_ontology.label_for(node)
            if lbl1:
                pref = obo_prefix_for_iri(str(node))
                core = self._normalize_label(lbl1)
                return f"{pref}:{core}" if pref else core

        if self.ont is not None:
            lbl2 = self.ont.label_for(node)
            if lbl2:
                pref = obo_prefix_for_iri(str(node))
                core = self._normalize_label(lbl2)
                return f"{pref}:{core}" if pref else core

        try:
            qname = g.namespace_manager.normalizeUri(node)
        except Exception:
            qname = f"<{node}>"

        if qname.startswith("<") and qname.endswith(">"):
            return uri_local_name(str(node))
        if qname.endswith(":"):
            return qname[:-1]
        return qname

    def _predicate_label(self, g: Graph, pred: URIRef) -> str:
        if pred == RDF.type:
            return "rdf:type"
        if pred == RDFS.subClassOf:
            return "rdfs:subClassOf"

        local_lits: List[Literal] = [l for l in g.objects(pred, RDFS.label) if isinstance(l, Literal)]
        lbl0 = best_label(local_lits)
        if lbl0:
            return self._normalize_label(lbl0)

        if self.full_ontology is not None:
            lbl1 = self.full_ontology.label_for(pred)
            if lbl1:
                return self._normalize_label(lbl1)

        if self.ont is not None:
            lbl2 = self.ont.label_for(pred)
            if lbl2:
                return self._normalize_label(lbl2)

        token = self._exact_prefix_token(g, pred)
        if token:
            return token

        try:
            qname = g.namespace_manager.normalizeUri(pred)
        except Exception:
            qname = f"<{pred}>"

        if qname.startswith("<") and qname.endswith(">"):
            return uri_local_name(str(pred))

        if qname.endswith(":"):
            return qname[:-1]

        # for edges, prefer the local part if qname-like
        if ":" in qname:
            return qname.split(":", 1)[1]
        return qname

    def _kind_for_uri(self, uri: URIRef, classes: Set[URIRef], shapes: Set[URIRef], categorical: Set[URIRef]) -> str:
        if uri in shapes:
            return "SHACL Shape"
        if uri in classes:
            return "Class"
        if uri in categorical:
            return "Categorical"
        return "Individual"

    def _style_bucket_for_node(self, uri: Optional[URIRef], kind: str) -> str:
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
            if bucket in ("bfo", "obi", "pmd"):
                return bucket
        return "cls"

    def _extract_list_items(self, g: Graph, head: BNode) -> Optional[List[Node]]:
        try:
            col = Collection(g, head)
            return list(col)
        except Exception:
            return None

    # -------- hierarchy enrichment --------
    def _add_full_hierarchy(
        self,
        classes: Set[URIRef],
        nodes: Set[Node],
        edges: List[Tuple[Node, URIRef, Node]],
    ) -> None:
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
                    if not isinstance(parent, URIRef):
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

    # -------- collect graph content --------
    def _collect_schema_and_instances(
        self, g: Graph
    ) -> Tuple[Set[URIRef], Set[URIRef], Set[URIRef], Set[Node], List[Tuple[Node, URIRef, Node]]]:
        classes: Set[URIRef] = set()
        shapes: Set[URIRef] = set()
        categorical: Set[URIRef] = set()
        nodes: Set[Node] = set()
        edges: List[Tuple[Node, URIRef, Node]] = []

        # Identify classes/shapes
        for s, _, o in g.triples((None, RDF.type, None)):
            if isinstance(o, URIRef):
                if o in (SH.NodeShape, SH.PropertyShape, SH.Shape):
                    if isinstance(s, URIRef):
                        shapes.add(s)
                if o in (OWL.Class, RDFS.Class):
                    if isinstance(s, URIRef):
                        classes.add(s)
                # also treat "type objects" as classes for TBOX visibility
                classes.add(o)

        for s, _, o in g.triples((None, RDFS.subClassOf, None)):
            if isinstance(s, URIRef):
                classes.add(s)
            if isinstance(o, URIRef):
                classes.add(o)

        # sh:in items are categorical values
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

            # Skip list structure
            if p in (RDF.first, RDF.rest):
                continue

            # Skip ontology declaration
            if p == RDF.type and o == OWL.Ontology:
                continue

            # Expand selected SHACL list predicates
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

        # Size caps
        if len(nodes) > self.max_nodes:
            LOG.warning("Node count %d exceeds max_nodes=%d; truncating.", len(nodes), self.max_nodes)
            ordered = sorted(nodes, key=lambda n: (0 if isinstance(n, URIRef) else 1 if isinstance(n, BNode) else 2, str(n)))
            nodes = set(ordered[: self.max_nodes])

        if len(edges) > self.max_edges:
            LOG.warning("Edge count %d exceeds max_edges=%d; truncating.", len(edges), self.max_edges)
            edges = edges[: self.max_edges]

        # Remote enrichment: superclass edges
        if self.enrich and self.superclass_depth > 0 and self.ont is not None:
            extra: Set[Tuple[URIRef, URIRef]] = set()
            for c in list(classes):
                extra |= self.ont.superclasses(c, self.superclass_depth)
            for child, parent in extra:
                edges.append((child, RDFS.subClassOf, parent))
                nodes.add(child)
                nodes.add(parent)
                classes.add(child)
                classes.add(parent)

        # Local full ontology hierarchy expansion
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
        self._pred_label_cache = {}
        for _, p, _ in edges:
            if isinstance(p, URIRef):
                self._pred_label_cache[str(p)] = self._predicate_label(g, p)

    # -------- Mermaid rendering --------
    def _build_mermaid(
        self,
        node_infos: Dict[Node, NodeInfo],
        edges: List[Tuple[Node, URIRef, Node]],
    ) -> str:
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

    # -------- Graphviz rendering --------
    def _build_graphviz(
        self,
        node_infos: Dict[Node, NodeInfo],
        edges: List[Tuple[Node, URIRef, Node]],
    ) -> str:
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
                    "label": info.label,
                    "shape": kind_shape(info.kind),
                    "style": "filled",
                    **style,
                }
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

        # Literals outside clusters
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

    def render_graph(self, ttl_path: Path, diagram_id: Optional[str] = None) -> DiagramResult:
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


# -----------------------------
# JS and HTML integration
# -----------------------------
def js_escape_template_literal(s: str) -> str:
    s = s.replace("\\", "\\\\")
    s = s.replace("`", "\\`")
    s = s.replace("${", "\\${")
    return s


def write_js(diagrams: Dict[str, str], node_data: Dict[str, Dict[str, Dict[str, str]]], out_js: Path) -> None:
    lines: List[str] = []
    lines.append("// Auto-generated by ttl_to_mermaid.py. Do not edit manually.")
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


# -----------------------------
# CLI
# -----------------------------
def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Convert Turtle (.ttl) patterns into Mermaid diagrams or Graphviz DOT and embeddable JS/HTML."
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--ttl", type=Path, help="Single TTL file to convert.")
    src.add_argument("--ttl-dir", type=Path, help="Directory of TTL files to convert.")

    p.add_argument("--format", default="mermaid", choices=["mermaid", "dot"], help="Diagram output format.")
    p.add_argument("--direction", default="BT", choices=["BT", "TD", "LR", "RL"], help="Diagram flow direction.")
    p.add_argument("--no-bnodes", action="store_true", help="Exclude blank nodes (BNodes) from diagrams.")

    p.add_argument("--enrich", action="store_true", help="Best-effort enrichment using cached ontologies (labels and superclasses).")
    p.add_argument("--superclass-depth", type=int, default=0, help="When --enrich, include up to N rdfs:subClassOf superclasses.")
    p.add_argument("--ontology-cache", type=Path, default=Path(".ontology_cache"), help="Cache directory for downloaded ontologies.")

    p.add_argument(
        "--full-ontology",
        type=Path,
        action="append",
        help="Path to local '*_full.ttl' ontology file(s) for labels and rdfs:subClassOf hierarchy. "
             "May be provided multiple times. If omitted, '*_full.ttl' files are auto-discovered in the input folder.",
    )
    p.add_argument("--no-full-hierarchy", action="store_true", help="Disable adding superclass chains from local full ontology files.")
    p.add_argument("--hierarchy-root", default="bfo:entity", help="Root IRI/CURIE to stop superclass expansion (default: bfo:entity).")
    p.add_argument("--hierarchy-max-depth", type=int, default=50, help="Maximum rdfs:subClassOf hops when adding local full hierarchy.")

    p.add_argument("--out-js", type=Path, help="Write a JS file with const diagrams/nodeData for embedding.")
    p.add_argument("--html", type=Path, help="HTML file to patch (patterns.html style).")
    p.add_argument("--patch-html", action="store_true", help="Patch --html in-place with generated diagrams/nodeData blocks.")
    p.add_argument("--out-html", type=Path, help="Write patched HTML to this path instead of in-place.")

    p.add_argument("--max-nodes", type=int, default=500, help="Safety cap on nodes per diagram.")
    p.add_argument("--max-edges", type=int, default=1500, help="Safety cap on edges per diagram.")
    p.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Log verbosity.")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s: %(message)s")

    # Local full ontology discovery/loading
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

        # If no embedding outputs were requested, print diagram source and exit.
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
                LOG.warning("No graph container IDs found in %s. Falling back to all TTL files.", args.html)
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
