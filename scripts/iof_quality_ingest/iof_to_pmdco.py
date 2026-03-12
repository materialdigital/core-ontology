#!/usr/bin/env python3
"""
IOF Qualities → PMDco migration script
=======================================
Reads the migration_config.csv, traverses the IOF class hierarchy to the
specified depth, converts annotations and object-property IRIs using the
mapping files, assigns fresh PMD IRIs from Thomas Hanke's range (80000-89999),
and writes output as OWL Functional Syntax ready to be reviewed and inserted
into the target PMDco component file.

Usage
-----
    python iof_to_pmdco.py [--output OUTPUT] [--start-id START_ID] [--dry-run]

Files expected alongside this script (same directory)
------------------------------------------------------
    migration_config.csv          — what to migrate and where
    annotation_property_mapping.json
    object_property_mapping.json
    iri_existing_mapping.json     — IOF IRI → already-existing PMDco/BFO IRI

Output
------
    A fragment of OWL Functional Syntax (default: migration_output.ofn) that can
    be appended to or merged into src/ontology/pmdco-edit.owl or a component file.
    A companion iri_new_mapping.json records the newly assigned PMD IRIs.
"""

import json
import csv
import re
import argparse
from pathlib import Path

from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent
PMDCO_BASE = "https://w3id.org/pmd/co/"
PMDCO_NS = Namespace(PMDCO_BASE)

# Thomas Hanke's allocated range (pmdco-idranges.owl idrange:4)
THOMAS_ID_START = 80000
THOMAS_ID_END = 89999

IOF_AV = Namespace("https://spec.industrialontologies.org/ontology/annotation/")

# Annotation properties kept verbatim in PMDco
PMDCO_PROP_IRIREF = {
    "http://www.w3.org/2000/01/rdf-schema#label": "rdfs:label",
    "http://www.w3.org/2004/02/skos/core#altLabel": "skos:altLabel",
    "http://www.w3.org/2004/02/skos/core#example": "skos:example",
    "http://purl.obolibrary.org/obo/IAO_0000115": "obo:IAO_0000115",
    "http://purl.obolibrary.org/obo/IAO_0000116": "obo:IAO_0000116",
    "http://purl.obolibrary.org/obo/IAO_0000119": "obo:IAO_0000119",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    with open(path) as f:
        raw = json.load(f)
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def iri_to_ofn(iri: str, prefixes: dict) -> str:
    """Return a prefixed name if a known prefix matches, else a full IRI ref."""
    for prefix, ns in prefixes.items():
        if iri.startswith(ns):
            return f"{prefix}:{iri[len(ns):]}"
    return f"<{iri}>"


def literal_to_ofn(lit: Literal) -> str:
    """Serialize an rdflib Literal to OWL FS notation."""
    text = str(lit).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    if lit.language:
        return f'"{text}"@{lit.language}'
    if lit.datatype and str(lit.datatype) != str(XSD.string):
        dtype = str(lit.datatype)
        if dtype == str(XSD.boolean):
            return f'"{text}"^^xsd:boolean'
        if dtype == str(XSD.integer):
            return f'"{text}"^^xsd:integer'
        return f'"{text}"^^<{dtype}>'
    return f'"{text}"'


def node_to_ofn(node, graph: Graph, prefixes: dict, op_map: dict,
                existing_map: dict, new_map: dict) -> str:
    """Recursively render an OWL class expression node to OWL FS string."""
    if isinstance(node, URIRef):
        mapped = resolve_iri(str(node), op_map, existing_map, new_map)
        return iri_to_ofn(mapped, prefixes)
    if isinstance(node, Literal):
        return literal_to_ofn(node)
    if isinstance(node, BNode):
        # Determine expression type
        expr_type = graph.value(node, RDF.type)
        if expr_type == OWL.Restriction:
            prop = graph.value(node, OWL.onProperty)
            prop_ofn = iri_to_ofn(
                resolve_iri(str(prop), op_map, existing_map, new_map), prefixes
            ) if prop else "???"
            some = graph.value(node, OWL.someValuesFrom)
            if some is not None:
                filler = node_to_ofn(some, graph, prefixes, op_map, existing_map, new_map)
                return f"ObjectSomeValuesFrom({prop_ofn} {filler})"
            all_vals = graph.value(node, OWL.allValuesFrom)
            if all_vals is not None:
                filler = node_to_ofn(all_vals, graph, prefixes, op_map, existing_map, new_map)
                return f"ObjectAllValuesFrom({prop_ofn} {filler})"
            exact = graph.value(node, OWL.qualifiedCardinality)
            on_class = graph.value(node, OWL.onClass)
            if exact is not None and on_class is not None:
                filler = node_to_ofn(on_class, graph, prefixes, op_map, existing_map, new_map)
                return f"ObjectExactCardinality({exact} {prop_ofn} {filler})"
            min_c = graph.value(node, OWL.minQualifiedCardinality)
            if min_c is not None and on_class is not None:
                filler = node_to_ofn(on_class, graph, prefixes, op_map, existing_map, new_map)
                return f"ObjectMinCardinality({min_c} {prop_ofn} {filler})"
            has_val = graph.value(node, OWL.hasValue)
            if has_val is not None:
                val = node_to_ofn(has_val, graph, prefixes, op_map, existing_map, new_map)
                return f"ObjectHasValue({prop_ofn} {val})"
        # Intersection / Union / Complement
        intersection = graph.value(node, OWL.intersectionOf)
        if intersection is not None:
            members = list_from_rdf_list(intersection, graph)
            parts = " ".join(
                node_to_ofn(m, graph, prefixes, op_map, existing_map, new_map)
                for m in members
            )
            return f"ObjectIntersectionOf({parts})"
        union = graph.value(node, OWL.unionOf)
        if union is not None:
            members = list_from_rdf_list(union, graph)
            parts = " ".join(
                node_to_ofn(m, graph, prefixes, op_map, existing_map, new_map)
                for m in members
            )
            return f"ObjectUnionOf({parts})"
        complement = graph.value(node, OWL.complementOf)
        if complement is not None:
            inner = node_to_ofn(complement, graph, prefixes, op_map, existing_map, new_map)
            return f"ObjectComplementOf({inner})"
    return f"<UNKNOWN:{node}>"


def list_from_rdf_list(node, graph: Graph):
    """Flatten an rdf:List into a Python list."""
    result = []
    current = node
    while current and current != RDF.nil:
        first = graph.value(current, RDF.first)
        if first is not None:
            result.append(first)
        current = graph.value(current, RDF.rest)
    return result


def resolve_iri(iri: str, op_map: dict, existing_map: dict, new_map: dict) -> str:
    """Resolve an IOF IRI to its PMDco equivalent. Precedence: op_map > existing > new."""
    if iri in op_map:
        return op_map[iri]
    if iri in existing_map:
        return existing_map[iri]
    if iri in new_map:
        return new_map[iri]
    return iri  # pass through unknown IRIs unchanged


# ---------------------------------------------------------------------------
# Scan ontology files for already-declared PMD IRIs
# ---------------------------------------------------------------------------

_PMD_IRI_RE = re.compile(r"PMD_(\d{7})")


def scan_declared_pmd_iris(ontology_dir: Path) -> set[str]:
    """
    Return the set of full PMD IRIs already present anywhere in *.owl files
    under ontology_dir.  Uses a fast regex scan (no RDF parsing) so it stays
    quick even for large corpora.
    """
    declared: set[str] = set()
    for owl_file in ontology_dir.rglob("*.owl"):
        try:
            text = owl_file.read_text(errors="replace")
        except OSError:
            continue
        for m in _PMD_IRI_RE.finditer(text):
            declared.add(f"{PMDCO_BASE}PMD_{m.group(1)}")
    return declared


# ---------------------------------------------------------------------------
# IRI allocator
# ---------------------------------------------------------------------------

class IRIAllocator:
    def __init__(self, start_id: int, end_id: int,
                 persisted_map: dict, declared_iris: set[str]):
        """
        Parameters
        ----------
        start_id      : lowest numeric ID in the allocated range
        end_id        : highest numeric ID in the allocated range
        persisted_map : iri_new_mapping.json contents (IOF → PMD IRI strings)
        declared_iris : all PMD IRI strings already present in the ontology
                        files (from scan_declared_pmd_iris)
        """
        # Collect ALL numeric IDs that are already claimed
        used: set[int] = set()
        for iri in declared_iris:
            m = _PMD_IRI_RE.search(iri)
            if m:
                used.add(int(m.group(1)))
        for iri in persisted_map.values():
            m = _PMD_IRI_RE.search(str(iri))
            if m:
                used.add(int(m.group(1)))

        self._next = start_id
        while self._next in used:
            self._next += 1
        self._end = end_id

    def next_iri(self) -> str:
        if self._next > self._end:
            raise RuntimeError(
                f"IRI range exhausted (max {self._end}). "
                "Update pmdco-idranges.owl to allocate more IDs."
            )
        iri = f"{PMDCO_BASE}PMD_{self._next:07d}"
        self._next += 1
        return iri


# ---------------------------------------------------------------------------
# OWL-FS generator for a single class
# ---------------------------------------------------------------------------

PREFIXES = {
    "obo": "http://purl.obolibrary.org/obo/",
    "pmdco": PMDCO_BASE,
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "owl": "http://www.w3.org/2002/07/owl#",
}


def generate_class_block(
    iof_iri: URIRef,
    target_parent_iri: str,
    graph: Graph,
    ann_map: dict,
    op_map: dict,
    existing_map: dict,
    new_map: dict,
    pmd_iri: str,
) -> list[str]:
    """
    Return a list of OWL FS lines for one class:
      Declaration, label comment, AnnotationAssertions, SubClassOf(s).
    """
    lines = []
    pmd_ref = iri_to_ofn(pmd_iri, PREFIXES)
    parent_ref = iri_to_ofn(target_parent_iri, PREFIXES)

    # Label for comment header
    label_en = next(
        (str(o) for o in graph.objects(iof_iri, RDFS.label) if getattr(o, "language", None) in ("en-US", "en", None)),
        str(iof_iri).rsplit("/", 1)[-1],
    )

    lines.append(f"# Class: {pmd_ref} ({label_en})")
    lines.append(f"# Adopted from IOF: <{iof_iri}>")
    lines.append("")

    # AnnotationAssertions -----------------------------------------------
    seen_preds: dict[str, set] = {}

    for pred, obj in graph.predicate_objects(iof_iri):
        pred_str = str(pred)

        # Skip owl/rdf structural predicates and things we handle elsewhere
        if pred in (RDF.type, RDFS.subClassOf, OWL.equivalentClass,
                    OWL.disjointWith, OWL.deprecated):
            continue

        # Map annotation property IRI
        if pred_str in ann_map:
            target_pred = ann_map[pred_str]
            if target_pred is None:
                continue  # explicitly dropped
        elif pred == RDFS.label:
            target_pred = str(RDFS.label)
        elif pred in (SKOS.altLabel, SKOS.prefLabel):
            target_pred = str(SKOS.altLabel)
        elif pred == SKOS.example:
            target_pred = str(SKOS.example)
        else:
            continue  # skip unmapped predicates

        target_ref = PMDCO_PROP_IRIREF.get(target_pred, f"<{target_pred}>")

        if isinstance(obj, Literal):
            val = literal_to_ofn(obj)
            key = (target_pred, str(obj), getattr(obj, "language", None))
            bucket = seen_preds.setdefault(target_pred, set())
            if key in bucket:
                continue
            bucket.add(key)
            lines.append(f"AnnotationAssertion({target_ref} {pmd_ref} {val})")
        elif isinstance(obj, URIRef):
            # adaptedFrom / definition source — keep IRI value
            resolved = resolve_iri(str(obj), op_map, existing_map, new_map)
            val = f"<{resolved}>"
            key = (target_pred, resolved)
            bucket = seen_preds.setdefault(target_pred, set())
            if key in bucket:
                continue
            bucket.add(key)
            lines.append(f"AnnotationAssertion({target_ref} {pmd_ref} {val})")

    # isInMinimalProfile flag (PMDco convention)
    lines.append(f'AnnotationAssertion(pmdco:PMD_0000060 {pmd_ref} "true"^^xsd:boolean)')

    # SubClassOf — primary parent
    lines.append(f"SubClassOf({pmd_ref} {parent_ref})")

    # Additional subClassOf axioms from the IOF source (excluding the IOF parent,
    # which is replaced by target_parent_iri)
    iof_parents = set(graph.objects(iof_iri, RDFS.subClassOf))
    for parent_node in iof_parents:
        if isinstance(parent_node, BNode):
            # Complex restriction — convert and emit
            expr = node_to_ofn(parent_node, graph, PREFIXES, op_map, existing_map, new_map)
            lines.append(f"SubClassOf({pmd_ref} {expr})")
        # Named parent nodes are intentionally skipped: the hierarchy placement
        # is controlled by migration_config.csv (target_parent_iri), not by the
        # original IOF parent.

    # EquivalentClass axioms (only for fully-defined non-primitive classes)
    for eq_node in graph.objects(iof_iri, OWL.equivalentClass):
        if isinstance(eq_node, BNode):
            expr = node_to_ofn(eq_node, graph, PREFIXES, op_map, existing_map, new_map)
            lines.append(f"EquivalentClasses({pmd_ref} {expr})")

    lines.append("")
    return lines


# ---------------------------------------------------------------------------
# Traversal
# ---------------------------------------------------------------------------

def get_children(parent: URIRef, graph: Graph) -> list[URIRef]:
    return [
        s for s in graph.subjects(RDFS.subClassOf, parent)
        if isinstance(s, URIRef)
    ]


def traverse(
    iof_iri: URIRef,
    target_parent_iri: str,
    depth: int,
    max_depth: int,
    stop_iris: set,
    graph: Graph,
    ann_map: dict,
    op_map: dict,
    existing_map: dict,
    new_map: dict,
    declared_iris: set[str],
    allocator: IRIAllocator,
    declarations: list,
    body_lines: list,
    dry_run: bool,
) -> None:
    iof_str = str(iof_iri)

    # ------------------------------------------------------------------ #
    # Determine the PMD IRI for this IOF class                            #
    # ------------------------------------------------------------------ #
    if iof_str in existing_map:
        # Maps to a pre-existing PMDco/BFO IRI — never re-emit, just reference
        pmd_iri = existing_map[iof_str]
        print(f"  [EXISTS]  {iof_str} -> {pmd_iri}")

    elif iof_str in new_map:
        # Previously assigned by an earlier run of this script
        pmd_iri = new_map[iof_str]
        if pmd_iri in declared_iris:
            # Term has been merged into the ontology already — skip emission
            print(f"  [MERGED]  {iof_str} -> {pmd_iri}  (already in ontology)")
        else:
            # Assigned but not yet merged — re-emit so it appears in the output
            print(f"  [PENDING] {iof_str} -> {pmd_iri}  (mapped, not yet merged)")
            declarations.append(f"Declaration(Class(<{pmd_iri}>))")
            block = generate_class_block(
                iof_iri, target_parent_iri, graph,
                ann_map, op_map, existing_map, new_map, pmd_iri
            )
            body_lines.extend(block)

    else:
        # Brand-new IOF term — assign a fresh PMD IRI
        if dry_run:
            pmd_iri = f"{PMDCO_BASE}PMD_DRY_{iof_str.rsplit('/', 1)[-1]}"
        else:
            pmd_iri = allocator.next_iri()
        new_map[iof_str] = pmd_iri
        print(f"  [NEW]     {iof_str} -> {pmd_iri}")

        declarations.append(f"Declaration(Class(<{pmd_iri}>))")
        block = generate_class_block(
            iof_iri, target_parent_iri, graph,
            ann_map, op_map, existing_map, new_map, pmd_iri
        )
        body_lines.extend(block)

    # ------------------------------------------------------------------ #
    # Recurse into children within the depth limit                        #
    # ------------------------------------------------------------------ #
    if max_depth is None or depth < max_depth:
        for child in get_children(iof_iri, graph):
            if str(child) in stop_iris:
                continue
            traverse(
                child, pmd_iri, depth + 1, max_depth, stop_iris,
                graph, ann_map, op_map, existing_map, new_map,
                declared_iris, allocator, declarations, body_lines, dry_run,
            )


# ---------------------------------------------------------------------------
# CSV reader
# ---------------------------------------------------------------------------

def parse_config(csv_path: Path) -> list[dict]:
    entries = []
    with open(csv_path) as f:
        for row in csv.DictReader(row for row in f if not row.strip().startswith("#")):
            if not row.get("source_iri", "").strip():
                continue
            entries.append({
                "source_iri": row["source_iri"].strip(),
                "source_file": row["source_file"].strip(),
                "target_parent_iri": row["target_parent_iri"].strip(),
                "stop_depth": (lambda v: int(v) if v else None)(row.get("stop_depth", "").strip()),
                "stop_at_iris": set(
                    s.strip()
                    for s in row.get("stop_at_iris", "").split(";")
                    if s.strip()
                ),
                "notes": row.get("notes", "").strip(),
            })
    return entries


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Migrate IOF quality classes to PMDco OWL FS.")
    parser.add_argument(
        "--output", default=str(SCRIPT_DIR / "migration_output.ofn"),
        help="Output OWL Functional Syntax file (default: migration_output.ofn)"
    )
    parser.add_argument(
        "--ontology-dir",
        default=str(SCRIPT_DIR.parent / "src" / "ontology"),
        help="Root directory of PMDco *.owl files to scan for existing IRIs "
             "(default: ../src/ontology relative to scripts/)"
    )
    parser.add_argument(
        "--start-id", type=int, default=THOMAS_ID_START,
        help=f"First numeric ID to assign (default: {THOMAS_ID_START}, Thomas Hanke's range)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Do not assign real IRIs; just print what would be migrated."
    )
    args = parser.parse_args()

    # Load mapping files
    ann_map = load_json(SCRIPT_DIR / "annotation_property_mapping.json")
    op_map = load_json(SCRIPT_DIR / "object_property_mapping.json")
    existing_map = load_json(SCRIPT_DIR / "iri_existing_mapping.json")

    # Scan the live ontology for every PMD IRI already declared there.
    # This ensures the allocator never collides with hand-authored terms and
    # that already-merged migration terms are not emitted again on reruns.
    ontology_dir = Path(args.ontology_dir)
    print(f"Scanning ontology files in: {ontology_dir}")
    declared_iris = scan_declared_pmd_iris(ontology_dir)
    print(f"  Found {len(declared_iris)} declared PMD IRIs in ontology files.")

    # Load any previously created IRI mappings to avoid gaps on reruns
    new_map_path = SCRIPT_DIR / "iri_new_mapping.json"
    new_map: dict = {}
    if new_map_path.exists():
        with open(new_map_path) as f:
            new_map = json.load(f)

    allocator = IRIAllocator(args.start_id, THOMAS_ID_END, new_map, declared_iris)

    config = parse_config(SCRIPT_DIR / "migration_config.csv")

    # Cache for loaded graphs (avoid re-parsing the same file multiple times)
    graph_cache: dict[str, Graph] = {}

    def load_graph(source_files_str: str) -> Graph:
        """Load one or more semicolon-separated RDF files into a merged graph."""
        files = [f.strip() for f in source_files_str.split(";") if f.strip()]
        # Check if we have a single-file hit in cache
        cache_key = ";".join(sorted(files))
        if cache_key in graph_cache:
            return graph_cache[cache_key]
        g = Graph()
        for path in files:
            if path not in graph_cache:
                print(f"\nLoading: {path}")
                single = Graph()
                single.parse(path)
                graph_cache[path] = single
            g += graph_cache[path]
        graph_cache[cache_key] = g
        return g

    declarations: list[str] = []
    body_lines: list[str] = []

    for entry in config:
        source_file = entry["source_file"]
        g = load_graph(source_file)

        iof_iri = URIRef(entry["source_iri"])
        print(f"\nTraversing: {entry['source_iri']}")
        print(f"  -> target parent: {entry['target_parent_iri']}")
        depth_label = str(entry['stop_depth']) if entry['stop_depth'] is not None else "unlimited"
        print(f"  -> max depth: {depth_label}")
        if entry["notes"]:
            print(f"  -> note: {entry['notes']}")

        traverse(
            iof_iri=iof_iri,
            target_parent_iri=entry["target_parent_iri"],
            depth=0,
            max_depth=entry["stop_depth"],
            stop_iris=entry["stop_at_iris"],
            graph=g,
            ann_map=ann_map,
            op_map=op_map,
            existing_map=existing_map,
            new_map=new_map,
            declared_iris=declared_iris,
            allocator=allocator,
            declarations=declarations,
            body_lines=body_lines,
            dry_run=args.dry_run,
        )

    # Write output
    output_path = Path(args.output)
    with open(output_path, "w") as f:
        f.write("# ============================================================\n")
        f.write("# IOF → PMDco migration output\n")
        f.write("# Generated by scripts/iof_to_pmdco.py\n")
        f.write("# Review carefully before merging into target component file.\n")
        f.write("# ============================================================\n\n")

        if declarations:
            f.write("# --- Declarations ---\n\n")
            for d in declarations:
                f.write(d + "\n")
            f.write("\n")

        f.write("# --- Class Definitions ---\n\n")
        for line in body_lines:
            f.write(line + "\n")

    print(f"\nOutput written to: {output_path}")

    # ------------------------------------------------------------------ #
    # Migration report — shows before/after hierarchy as a tree           #
    # ------------------------------------------------------------------ #
    report_path = Path(args.output).with_suffix(".report.md")
    _write_report(
        report_path, config, graph_cache, existing_map, new_map,
        declared_iris, args.dry_run
    )
    print(f"Report written to:  {report_path}")

    # Persist new IRI mappings
    if not args.dry_run:
        with open(new_map_path, "w") as f:
            json.dump(new_map, f, indent=2)
        print(f"IRI mapping saved to: {new_map_path}")


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------

def _label(iof_iri: URIRef, graph: Graph) -> str:
    """Best English label for a class, falling back to local name."""
    for lang in ("en-US", "en", None):
        for lit in graph.objects(iof_iri, RDFS.label):
            if lang is None or getattr(lit, "language", None) == lang:
                return str(lit)
    return str(iof_iri).rsplit("/", 1)[-1]


def _tree_lines(
    iof_iri: URIRef,
    target_pmd_iri: str,
    depth: int,
    max_depth: int,
    stop_iris: set,
    graph: Graph,
    existing_map: dict,
    new_map: dict,
    declared_iris: set[str],
    dry_run: bool,
) -> list[str]:
    """Recursively build tree lines for the report."""
    indent = "  " * depth
    lbl = _label(iof_iri, graph)
    iof_str = str(iof_iri)

    if iof_str in existing_map:
        status = "EXISTS"
        pmd = existing_map[iof_str]
    elif iof_str in new_map:
        pmd = new_map[iof_str]
        status = "MERGED" if pmd in declared_iris else "PENDING"
    else:
        status = "DRY" if dry_run else "NEW"
        pmd = new_map.get(iof_str, "?")

    pmd_short = pmd.rsplit("/", 1)[-1] if pmd.startswith("http") else pmd
    lines = [f"{indent}- **{lbl}** `{pmd_short}` [{status}]"]

    if max_depth is None or depth < max_depth:
        for child in sorted(get_children(iof_iri, graph), key=lambda c: str(c)):
            if str(child) in stop_iris:
                continue
            child_pmd = existing_map.get(str(child)) or new_map.get(str(child), pmd)
            lines += _tree_lines(
                child, child_pmd, depth + 1, max_depth, stop_iris,
                graph, existing_map, new_map, declared_iris, dry_run,
            )
    return lines


def _write_report(
    report_path: Path,
    config: list[dict],
    graph_cache: dict,
    existing_map: dict,
    new_map: dict,
    declared_iris: set[str],
    dry_run: bool,
) -> None:
    counts = {"NEW": 0, "PENDING": 0, "MERGED": 0, "EXISTS": 0}

    lines = [
        "# IOF → PMDco Migration Report",
        "",
        "Status legend",
        "- **NEW** — fresh term; PMD IRI just assigned, not yet in ontology",
        "- **PENDING** — PMD IRI assigned in a previous run but not yet merged into ontology",
        "- **MERGED** — term was already merged into the ontology (skipped in output)",
        "- **EXISTS** — mapped to a pre-existing PMDco/BFO IRI (never re-emitted)",
        "",
        "---",
        "",
    ]

    for entry in config:
        source_files = entry["source_file"]
        # Build a merged graph from whatever was already loaded
        cache_key = ";".join(sorted(f.strip() for f in source_files.split(";")))
        g = graph_cache.get(cache_key)
        if g is None:
            # Fall back to a single-file match
            g = next(
                (v for k, v in graph_cache.items() if source_files.split(";")[0].strip() in k),
                Graph()
            )

        iof_iri = URIRef(entry["source_iri"])
        target_pmd = existing_map.get(entry["source_iri"]) or new_map.get(entry["source_iri"], "")
        lbl = _label(iof_iri, g)

        lines.append(f"## {lbl}")
        lines.append(f"- IOF source: `{entry['source_iri']}`")
        lines.append(f"- Target parent in PMDco: `{entry['target_parent_iri']}`")
        if entry["notes"]:
            lines.append(f"- Note: {entry['notes']}")
        lines.append("")
        lines.append("### Hierarchy")
        lines.append("")

        tree = _tree_lines(
            iof_iri, target_pmd,
            depth=0,
            max_depth=entry["stop_depth"],
            stop_iris=entry["stop_at_iris"],
            graph=g,
            existing_map=existing_map,
            new_map=new_map,
            declared_iris=declared_iris,
            dry_run=dry_run,
        )
        lines += tree
        lines.append("")

        # Tally statuses from the tree lines
        for tl in tree:
            for status in counts:
                if f"[{status}]" in tl:
                    counts[status] += 1

    # Summary table
    summary = [
        "---",
        "",
        "## Summary",
        "",
        f"| Status | Count |",
        f"|--------|-------|",
        f"| NEW (output this run) | {counts['NEW']} |",
        f"| PENDING (output, not yet merged) | {counts['PENDING']} |",
        f"| MERGED (skipped, already in ontology) | {counts['MERGED']} |",
        f"| EXISTS (pre-existing PMDco term) | {counts['EXISTS']} |",
        "",
    ]

    # Write in logical order: intro → entries → summary
    report_path.write_text("\n".join(lines + summary))


if __name__ == "__main__":
    main()
