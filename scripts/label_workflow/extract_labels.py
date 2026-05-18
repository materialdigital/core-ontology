#!/usr/bin/env python3
"""Extract rdfs:label and skos:definition annotations from PMDco component OWL files.

Reads src/ontology/pmdco-edit.owl to discover the authoritative component file list,
parses each OWL Functional Syntax file with regex, and produces a CSV with:
  - Current annotation values per language tag (en, de, none)
  - Empty *_suggested columns for human/agent review
  - Parent class URIs and source file path per term

Usage:
    python3 extract_labels.py [--edit-owl PATH] [--output PATH]

Run from the repository root:
    python3 scripts/label_workflow/extract_labels.py
"""

import re
import csv
import sys
import argparse
from collections import defaultdict
from pathlib import Path

PMDCO_BASE = "https://w3id.org/pmd/co/"
COMPONENTS_IRI_BASE = "https://w3id.org/pmd/co/components/"

CSV_FIELDS = [
    "iri", "source_file", "parent_iris",
    "label_en", "label_de", "label_none",
    "definition_en", "definition_de", "definition_none",
    "label_en_suggested", "label_de_suggested",
    "definition_en_suggested", "definition_de_suggested",
    "notes",
]

# AnnotationAssertion with a string literal; re.DOTALL lets value span lines
ANN_RE = re.compile(
    r'AnnotationAssertion\s*\(\s*'
    r'(?P<prop>\S+)\s+'                   # property
    r'(?P<subj>\S+)\s+'                   # subject IRI / prefixed name
    r'"(?P<value>(?:[^"\\]|\\.)*)"'       # literal value (handles \" and \\)
    r'(?:@(?P<lang>[a-zA-Z][a-zA-Z0-9-]*))?\s*'  # optional @lang
    r'\)',
    re.DOTALL,
)

# SubClassOf with two plain named classes (no nested expressions)
SIMPLE_SC_RE = re.compile(
    r'SubClassOf\s*\(\s*([^\s()]+)\s+([^\s()]+)\s*\)'
)

# SubClassOf where the parent is a class expression (ObjectXxx|DataXxx keyword)
COMPLEX_SC_RE = re.compile(
    r'SubClassOf\s*\(\s*([^\s()]+)\s+(?:Object|Data)\w+\s*\('
)

PROP_RDFS_LABEL = frozenset({
    "rdfs:label",
    "<http://www.w3.org/2000/01/rdf-schema#label>",
})
PROP_SKOS_DEF = frozenset({
    "skos:definition",
    "<http://www.w3.org/2004/02/skos/core#definition>",
})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ofn_unescape(s: str) -> str:
    """Resolve OFN string escapes (\\\" → \", \\\\ → \\) for human-readable CSV output."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            nc = s[i + 1]
            if nc == '"':
                result.append('"')
            elif nc == '\\':
                result.append('\\')
            else:
                result.append('\\')
                result.append(nc)
            i += 2
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


def extract_prefixes(text: str) -> dict[str, str]:
    """Parse Prefix declarations → {prefix_alias: namespace_iri}."""
    prefixes: dict[str, str] = {}
    for m in re.finditer(r'Prefix\s*\(\s*(\S*:)\s*=\s*<([^>]+)>\s*\)', text):
        prefixes[m.group(1)] = m.group(2)
    return prefixes


def expand_iri(curie: str, prefixes: dict[str, str]) -> str:
    """Expand a prefixed name or full IRI ref (<...>) to a plain IRI string."""
    if curie.startswith('<') and curie.endswith('>'):
        return curie[1:-1]
    for pfx, ns in prefixes.items():
        if curie.startswith(pfx):
            return ns + curie[len(pfx):]
    return curie


def discover_component_files(edit_owl_path: Path) -> list[Path]:
    """Return pmdco-*.owl component paths discovered from Import() lines."""
    text = edit_owl_path.read_text(encoding="utf-8")
    components_dir = edit_owl_path.parent / "components"
    paths: list[Path] = []
    for m in re.finditer(r'Import\s*\(<([^>]+)>\)', text):
        iri = m.group(1)
        if not iri.startswith(COMPONENTS_IRI_BASE):
            continue
        fname = iri[len(COMPONENTS_IRI_BASE):]
        if not fname.startswith("pmdco-"):
            continue
        local = components_dir / fname
        if local.exists():
            paths.append(local)
        else:
            print(f"WARNING: imported component not found: {local}", file=sys.stderr)
    return paths


# ---------------------------------------------------------------------------
# Per-file extraction
# ---------------------------------------------------------------------------

def parse_component(owl_path: Path, repo_root: Path) -> list[dict]:
    """Extract label/definition/parent data from one OFN component file."""
    text = owl_path.read_text(encoding="utf-8")
    prefixes = extract_prefixes(text)
    rel_path = str(owl_path.relative_to(repo_root))

    # annotations[full_iri][(prop_type, lang)] = display_value
    annotations: dict[str, dict[tuple[str, str], str]] = defaultdict(dict)

    for m in ANN_RE.finditer(text):
        prop = m.group("prop")
        subj = expand_iri(m.group("subj"), prefixes)

        if not subj.startswith(PMDCO_BASE + "PMD_"):
            continue

        if prop in PROP_RDFS_LABEL:
            prop_key = "label"
        elif prop in PROP_SKOS_DEF:
            prop_key = "definition"
        else:
            continue

        raw_value = m.group("value")
        lang_raw = m.group("lang") or ""
        # Normalise en-US → en (established project convention)
        lang = lang_raw.lower()
        if lang in ("en-us",):
            lang = "en"
        lang = lang or "none"

        display_value = ofn_unescape(raw_value)
        key = (prop_key, lang)

        if key in annotations[subj]:
            print(
                f"WARNING: duplicate {prop_key}@{lang} on <{subj}> — joining with ' | '",
                file=sys.stderr,
            )
            annotations[subj][key] += " | " + display_value
        else:
            annotations[subj][key] = display_value

    # Simple named parents
    simple_parents: dict[str, list[str]] = defaultdict(list)
    for m in SIMPLE_SC_RE.finditer(text):
        child = expand_iri(m.group(1), prefixes)
        parent = expand_iri(m.group(2), prefixes)
        if child.startswith(PMDCO_BASE + "PMD_"):
            simple_parents[child].append(parent)

    # Terms with at least one complex expression parent
    complex_terms: set[str] = set()
    for m in COMPLEX_SC_RE.finditer(text):
        child = expand_iri(m.group(1), prefixes)
        if child.startswith(PMDCO_BASE + "PMD_"):
            complex_terms.add(child)

    # Build rows — only terms that have at least one label or definition
    rows: list[dict] = []
    for iri, ann in annotations.items():
        parent_list = sorted(set(simple_parents.get(iri, [])))
        if iri in complex_terms:
            parent_list.append("[complex]")

        rows.append({
            "iri": iri,
            "source_file": rel_path,
            "parent_iris": " | ".join(parent_list),
            "label_en": ann.get(("label", "en"), ""),
            "label_de": ann.get(("label", "de"), ""),
            "label_none": ann.get(("label", "none"), ""),
            "definition_en": ann.get(("definition", "en"), ""),
            "definition_de": ann.get(("definition", "de"), ""),
            "definition_none": ann.get(("definition", "none"), ""),
            "label_en_suggested": "",
            "label_de_suggested": "",
            "definition_en_suggested": "",
            "definition_de_suggested": "",
            "notes": "",
        })

    rows.sort(key=lambda r: int(re.search(r"PMD_0*(\d+)$", r["iri"]).group(1)))
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--edit-owl",
        default="src/ontology/pmdco-edit.owl",
        metavar="PATH",
        help="Path to pmdco-edit.owl (default: src/ontology/pmdco-edit.owl)",
    )
    parser.add_argument(
        "--output",
        default="scripts/label_workflow/pmdco_labels.csv",
        metavar="PATH",
        help="Output CSV path (default: scripts/label_workflow/pmdco_labels.csv)",
    )
    args = parser.parse_args()

    edit_owl = Path(args.edit_owl)
    if not edit_owl.exists():
        sys.exit(f"ERROR: {edit_owl} not found — run from the repository root")

    # Repo root: pmdco-edit.owl is at src/ontology/pmdco-edit.owl
    repo_root = edit_owl.parent.parent.parent

    component_files = discover_component_files(edit_owl)
    if not component_files:
        sys.exit("ERROR: no pmdco-*.owl component files found in Import() list")

    print(f"Discovered {len(component_files)} component files:")
    for f in component_files:
        print(f"  {f.name}")
    print()

    all_rows: list[dict] = []
    for f in component_files:
        print(f"Parsing {f.name} ...", end=" ", flush=True)
        rows = parse_component(f, repo_root)
        print(f"{len(rows)} terms with labels/definitions")
        all_rows.extend(rows)

    # Final sort: by source_file then by numeric IRI
    all_rows.sort(key=lambda r: (
        r["source_file"],
        int(re.search(r"PMD_0*(\d+)$", r["iri"]).group(1)),
    ))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nWrote {len(all_rows)} rows → {output}")


if __name__ == "__main__":
    main()
