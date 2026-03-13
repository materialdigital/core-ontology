#!/usr/bin/env python3
"""Add missing IAO_0000114 (curation status) and IAO_0000117 (term editor)
annotations to PMDco component OWL files (OFN format).

Curation status is set only when the annotation is completely absent:
  - If --robot-report is given: terms with no WARN/ERROR in the ROBOT OBO report
    get IAO_0000122 (ready for release); others get IAO_0000123 (metadata incomplete).
  - If --shacl-report is given: terms with no non-IAO_0000114 violations
    get IAO_0000122 (ready for release); others get IAO_0000123 (metadata incomplete).
  - Without either flag: all missing statuses default to IAO_0000123.

Term editor is determined from the IRI numeric range (pmdco-idranges.owl).
Only adds annotations that are completely absent for a given term.

Usage:
    python3 fix_missing_annotations.py <components_dir> [--robot-report FILE]
    python3 fix_missing_annotations.py <components_dir> [--shacl-report FILE]
"""

import csv
import re
import sys
import argparse
from pathlib import Path

try:
    import rdflib
    HAS_RDFLIB = True
except ImportError:
    HAS_RDFLIB = False

PMDCO_PREFIX = "https://w3id.org/pmd/co/"
# Paths we are filling ourselves — excluded when deciding curation status
FILLED_PATHS = {
    "http://purl.obolibrary.org/obo/IAO_0000114",
    "http://purl.obolibrary.org/obo/IAO_0000117",
}

# IRI range → full person name (from pmdco-idranges.owl + pmdco-edit.owl labels)
ID_RANGES = [
    (0,      9999,   "Joerg Waitelonis"),
    (10000,  19999,  "Bernd Bayerlein"),
    (20000,  25000,  "Philipp von Hartrott"),
    (25001,  25999,  "Kamilla Zaripova"),
    (30000,  39999,  "Henk Birkholz"),
    (40000,  49999,  "Lars Vogt"),
    (50000,  59999,  "Markus Schilling"),
    (60000,  69999,  "Hossein Beygi Nasrabadi"),
    (70000,  79999,  "ebrahim"),
    (80000,  89999,  "Thomas Hanke"),
    (90000,  94999,  "thnlrd"),
    (200000, 999999, "PMDco Team"),
]

STATUS_READY      = "<http://purl.obolibrary.org/obo/IAO_0000122>"   # ready for release
STATUS_INCOMPLETE = "<http://purl.obolibrary.org/obo/IAO_0000123>"   # metadata incomplete


def editor_for_iri(iri: str) -> str:
    """Return 'PERSON: <name>' for the owner of the IRI's numeric range."""
    m = re.search(r"PMD_0*(\d+)$", iri)
    if not m:
        return "PERSON: PMDco Team"
    n = int(m.group(1))
    for lo, hi, name in ID_RANGES:
        if lo <= n <= hi:
            return f"PERSON: {name}"
    return "PERSON: PMDco Team"


def load_violations(report_path: Path):
    """Parse a pyshacl Turtle report.

    Returns a dict mapping focusNode IRI → set of resultPath IRIs that have
    sh:Violation severity.  The IAO_0000114 path is excluded from each set
    (it is what we are about to fix).  A term appearing in the dict with an
    empty set had only IAO_0000114 violations and is otherwise compliant.
    """
    if not HAS_RDFLIB:
        raise RuntimeError(
            "rdflib is required for --shacl-report processing; pip install rdflib"
        )
    g = rdflib.Graph()
    g.parse(report_path)

    query = f"""
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        SELECT ?focusNode ?resultPath WHERE {{
            ?vr a sh:ValidationResult ;
                sh:focusNode ?focusNode ;
                sh:resultSeverity sh:Violation .
            OPTIONAL {{ ?vr sh:resultPath ?resultPath }}
            FILTER(STRSTARTS(STR(?focusNode), "{PMDCO_PREFIX}"))
        }}
    """
    violations = {}
    for row in g.query(query):
        iri = str(row.focusNode)
        path = str(row.resultPath) if row.resultPath else None
        if iri not in violations:
            violations[iri] = set()
        if path and path not in FILLED_PATHS:
            violations[iri].add(path)
    return violations


def load_robot_violations(report_path: Path):
    """Parse a ROBOT OBO report TSV (columns: Level, Rule Name, Subject, ...).

    Returns a dict mapping term IRI → set of rule names where Level is ERROR.
    Only ERROR-level issues affect curation status; WARNs like multiple_labels
    are expected for multilingual ontologies and are excluded.
    Terms not in the dict have no blocking errors (ready for release).
    """
    violations = {}
    with open(report_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            level = row.get("Level", "").strip()
            subject = row.get("Subject", "").strip()
            rule = row.get("Rule Name", "").strip()
            if not subject.startswith(PMDCO_PREFIX):
                continue
            if level == "ERROR":
                if subject not in violations:
                    violations[subject] = set()
                violations[subject].add(rule)
    return violations


def pmdco_prefix_alias(text: str) -> str:
    """Return the prefix alias (e.g. ':' or 'pmdco:') that maps to PMDCO_PREFIX."""
    for m in re.finditer(
        r'Prefix\s*\(\s*(\w*:)\s*=\s*<' + re.escape(PMDCO_PREFIX) + r'>\s*\)', text
    ):
        return m.group(1)
    return ":"  # fallback


def process_file(owl_file: Path, violations, dry_run: bool = False) -> tuple:
    """Patch one OFN component file in-place.

    Returns (annotations_added, terms_touched).
    """
    text = owl_file.read_text(encoding="utf-8")

    # Detect which prefix alias this file uses for the PMDco namespace
    alias = pmdco_prefix_alias(text)
    alias_re = re.escape(alias)

    # Find all declared PMDco term IDs (stored as zero-padded 7-digit strings)
    declared = set()
    for m in re.finditer(
        r"Declaration\s*\(\s*"
        r"(?:Class|ObjectProperty|AnnotationProperty|DataProperty)\s*"
        r"\(\s*" + alias_re + r"PMD_(\d+)\s*\)\s*\)",
        text,
    ):
        declared.add(m.group(1).zfill(7))

    if not declared:
        return 0, 0

    # Find which terms already carry the annotations we might add
    has_114 = set()
    has_117 = set()
    for m in re.finditer(
        r"AnnotationAssertion\s*\(\s*(?:obo:IAO_0000114|<http://purl\.obolibrary\.org/obo/IAO_0000114>)\s+" + alias_re + r"PMD_(\d+)", text
    ):
        has_114.add(m.group(1).zfill(7))
    for m in re.finditer(
        r"AnnotationAssertion\s*\(\s*(?:obo:IAO_0000117|<http://purl\.obolibrary\.org/obo/IAO_0000117>)\s+" + alias_re + r"PMD_(\d+)", text
    ):
        has_117.add(m.group(1).zfill(7))

    new_lines = []
    touched = set()

    for num in sorted(declared):
        iri = f"{PMDCO_PREFIX}PMD_{num}"
        changed = False

        if num not in has_117:
            editor = editor_for_iri(iri)
            new_lines.append(
                f'AnnotationAssertion(<http://purl.obolibrary.org/obo/IAO_0000117> {alias}PMD_{num} "{editor}")'
            )
            changed = True

        if num not in has_114:
            if violations is not None:
                other_violations = violations.get(iri, set())
                status = STATUS_READY if not other_violations else STATUS_INCOMPLETE
            else:
                status = STATUS_INCOMPLETE  # conservative default without a report
            new_lines.append(
                f"AnnotationAssertion(<http://purl.obolibrary.org/obo/IAO_0000114> {alias}PMD_{num} {status})"
            )
            changed = True

        if changed:
            touched.add(num)

    if not new_lines:
        return 0, 0

    if dry_run:
        print(f"  [dry-run] {owl_file.name}: would add {len(new_lines)} annotation(s) on {len(touched)} term(s):")
        for line in new_lines:
            print(f"    + {line}")
        return len(new_lines), len(touched)

    # Insert the new assertions just before the final closing ')' of Ontology(...)
    last_paren = text.rfind("\n)")
    if last_paren == -1:
        print(
            f"WARNING: cannot locate closing ')' in {owl_file.name} — skipping",
            file=sys.stderr,
        )
        return 0, 0

    insertion = "\n" + "\n".join(new_lines) + "\n"
    owl_file.write_text(
        text[:last_paren] + insertion + text[last_paren:], encoding="utf-8"
    )
    return len(new_lines), len(touched)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "components_dir",
        help="Path to the components/ directory (e.g. src/ontology/components)",
    )
    parser.add_argument(
        "--robot-report",
        metavar="FILE",
        help=(
            "ROBOT OBO report TSV used to determine curation status. "
            "Terms with no WARN/ERROR get IAO_0000122 (ready for release); "
            "others get IAO_0000123 (metadata incomplete)."
        ),
    )
    parser.add_argument(
        "--shacl-report",
        metavar="FILE",
        help=(
            "pyshacl Turtle report used to determine curation status. "
            "Without this flag every missing IAO_0000114 is set to "
            "IAO_0000123 (metadata incomplete)."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be added without writing any files.",
    )
    args = parser.parse_args()

    violations = None
    if args.robot_report:
        print(f"Loading ROBOT report violations from {args.robot_report} ...")
        violations = load_robot_violations(Path(args.robot_report))
        print(f"  {len(violations)} term(s) with WARN/ERROR violations found")
    elif args.shacl_report:
        print(f"Loading SHACL violations from {args.shacl_report} ...")
        violations = load_violations(Path(args.shacl_report))
        print(f"  {len(violations)} term(s) with violations found")
    else:
        print(
            "No --robot-report or --shacl-report given: missing IAO_0000114 will default to "
            "IAO_0000123 (metadata incomplete)"
        )

    components_dir = Path(args.components_dir)
    if args.dry_run:
        print("DRY RUN — no files will be modified.\n")

    components_dir = Path(args.components_dir)
    owl_files = sorted(components_dir.glob("pmdco-*.owl"))

    total_ann = 0
    total_terms = 0
    for f in owl_files:
        n_ann, n_terms = process_file(f, violations, dry_run=args.dry_run)
        if n_ann and not args.dry_run:
            print(f"  {f.name}: +{n_ann} annotation(s) on {n_terms} term(s)")
        total_ann += n_ann
        total_terms += n_terms

    if total_ann == 0:
        print("No missing annotations found — nothing to do.")
    elif args.dry_run:
        print(f"\nDry run total: {total_ann} annotation(s) would be added across {total_terms} term(s).")
    else:
        print(f"\nTotal: +{total_ann} annotation(s) added across {total_terms} term(s).")


if __name__ == "__main__":
    main()
