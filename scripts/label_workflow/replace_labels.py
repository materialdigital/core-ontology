#!/usr/bin/env python3
"""Apply label/definition corrections from a reviewed CSV back into OWL component files.

Reads the CSV produced by extract_labels.py (and reviewed by agent_review.py or
manually), compares *_suggested columns against current values, and patches only the
targeted AnnotationAssertion lines in the relevant OWL Functional Syntax files.

Safety guarantees:
  - Only rdfs:label and skos:definition AnnotationAssertion lines are touched.
  - Exits non-zero if a replacement pattern matches more than one line in a file
    (ambiguous hit — no files are written in that case).
  - --dry-run shows the planned changes as a diff without writing any files.
  - --backup writes <file>.bak before patching.

Usage:
    python3 replace_labels.py --input pmdco_labels_reviewed.csv [--dry-run] [--backup]

Run from the repository root.
"""

import re
import csv
import sys
import shutil
import argparse
from collections import defaultdict
from pathlib import Path

PMDCO_BASE = "https://w3id.org/pmd/co/"

# Columns that map to (property_key, lang)
ANNOTATION_COLUMNS = {
    "label_en_suggested":       ("label",      "en"),
    "label_de_suggested":       ("label",      "de"),
    "label_none_suggested":     ("label",      "none"),   # not in CSV but handled if present
    "definition_en_suggested":  ("definition", "en"),
    "definition_de_suggested":  ("definition", "de"),
    "definition_none_suggested": ("definition", "none"),  # not in CSV but handled if present
}

# Current-value columns corresponding to each suggested column
CURRENT_COLUMNS = {
    "label_en_suggested":       "label_en",
    "label_de_suggested":       "label_de",
    "definition_en_suggested":  "definition_en",
    "definition_de_suggested":  "definition_de",
}

# OFN property expressions (primary prefixed form; also accept full IRI)
PROP_PATTERNS = {
    "label": r'(?:rdfs:label|<http://www\.w3\.org/2000/01/rdf-schema#label>)',
    "definition": r'(?:skos:definition|<http://www\.w3\.org/2004/02/skos/core#definition>)',
}


# ---------------------------------------------------------------------------
# String helpers
# ---------------------------------------------------------------------------

def ofn_escape(s: str) -> str:
    """Escape a display string for embedding in an OFN string literal."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def pmdco_prefix_alias(text: str) -> str:
    """Return the prefix alias (e.g. ':' or 'pmdco:') that maps to PMDCO_BASE."""
    for m in re.finditer(
        r'Prefix\s*\(\s*(\w*:)\s*=\s*<' + re.escape(PMDCO_BASE) + r'>\s*\)', text
    ):
        return m.group(1)
    return ":"  # fallback


def iri_to_local_id(iri: str) -> str | None:
    """Extract the zero-padded PMD ID from a full IRI, e.g. 'PMD_0000005'."""
    m = re.search(r"(PMD_\d+)$", iri)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Core patch logic
# ---------------------------------------------------------------------------

def build_annotation_pattern(prop_re: str, subject: str, old_value_raw: str, lang: str) -> str:
    """
    Return a regex pattern that matches exactly the AnnotationAssertion line to replace.

    prop_re   — already-built regex alternation for the property
    subject   — prefixed IRI string as it appears in the file (e.g. 'pmdco:PMD_0000005')
    old_value_raw — OFN-escaped value as it appears in the file between the quotes
    lang      — language tag string, or 'none' for untagged literals
    """
    lang_part = rf"@{re.escape(lang)}" if lang != "none" else ""
    return (
        r"(AnnotationAssertion\s*\(\s*"
        + prop_re
        + r"\s+"
        + re.escape(subject)
        + r'\s+")'
        + re.escape(old_value_raw)
        + r'("'
        + lang_part
        + r"\s*\))"
    )


def patch_file(
    owl_path: Path,
    changes: list[tuple],  # list of (prop_key, lang, old_display, new_display)
    dry_run: bool,
    backup: bool,
) -> tuple[int, int]:
    """
    Patch one OWL file in-place.

    changes items: (prop_key, lang, old_display_value, new_display_value, iri_str)

    Returns (replacements_made, appended_annotations).
    """
    text = owl_path.read_text(encoding="utf-8")
    alias = pmdco_prefix_alias(text)

    n_replaced = 0
    n_appended = 0
    pending_appends: list[str] = []  # annotation lines to append at end of Ontology

    for prop_key, lang, old_display, new_display, iri_str in changes:
        local_id = iri_to_local_id(iri_str)
        if not local_id:
            print(f"  WARNING: cannot derive local ID from <{iri_str}> — skipping", file=sys.stderr)
            continue

        subject = f"{alias}{local_id}"
        prop_re = PROP_PATTERNS[prop_key]

        new_raw = ofn_escape(new_display)
        lang_suffix = f"@{lang}" if lang != "none" else ""

        if old_display:
            # Replace existing annotation
            old_raw = ofn_escape(old_display)

            # Warn and skip multiline old values
            if "\n" in old_raw:
                print(
                    f"  WARNING: multiline value for {prop_key}@{lang} on {local_id} — skipping",
                    file=sys.stderr,
                )
                continue

            pattern = build_annotation_pattern(prop_re, subject, old_raw, lang)

            matches = re.findall(pattern, text, re.DOTALL)
            if len(matches) > 1:
                # Ambiguous: abort the entire file write
                print(
                    f"  ERROR: pattern for {prop_key}@{lang} on {local_id} matches "
                    f"{len(matches)} lines in {owl_path.name} — aborting all writes",
                    file=sys.stderr,
                )
                return -1, -1  # signal abort

            if len(matches) == 0:
                print(
                    f"  WARNING: no match for {prop_key}@{lang} on {local_id} "
                    f"in {owl_path.name} — file may have changed; skipping",
                    file=sys.stderr,
                )
                continue

            replacement_line = (
                f'AnnotationAssertion({PROP_PATTERNS_CANONICAL[prop_key]} '
                f'{subject} "{new_raw}"{lang_suffix})'
            )

            if dry_run:
                old_line = (
                    f'AnnotationAssertion({PROP_PATTERNS_CANONICAL[prop_key]} '
                    f'{subject} "{old_raw}"{lang_suffix})'
                )
                print(f"  - {old_line}")
                print(f"  + {replacement_line}")
            else:
                text = re.sub(
                    pattern,
                    lambda m, nr=new_raw: m.group(1) + nr + m.group(2),
                    text,
                    flags=re.DOTALL,
                )
            n_replaced += 1

        else:
            # Annotation absent — append new one
            new_line = (
                f'AnnotationAssertion({PROP_PATTERNS_CANONICAL[prop_key]} '
                f'{subject} "{new_raw}"{lang_suffix})'
            )
            if dry_run:
                print(f"  + (append) {new_line}")
            else:
                pending_appends.append(new_line)
            n_appended += 1

    # Apply appends (insert before final closing ')' of Ontology block)
    if pending_appends and not dry_run:
        last_paren = text.rfind("\n)")
        if last_paren == -1:
            print(
                f"  WARNING: cannot locate closing ')' in {owl_path.name} — "
                "appended annotations skipped",
                file=sys.stderr,
            )
        else:
            insertion = "\n" + "\n".join(pending_appends) + "\n"
            text = text[:last_paren] + insertion + text[last_paren:]

    if not dry_run and (n_replaced > 0 or n_appended > 0):
        if backup:
            shutil.copy2(owl_path, str(owl_path) + ".bak")
        owl_path.write_text(text, encoding="utf-8")

    return n_replaced, n_appended


# Canonical property string for emitting in replacement lines
PROP_PATTERNS_CANONICAL = {
    "label": "rdfs:label",
    "definition": "skos:definition",
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        default="scripts/label_workflow/pmdco_labels_reviewed.csv",
        metavar="PATH",
        help="Reviewed CSV (default: scripts/label_workflow/pmdco_labels_reviewed.csv)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned changes as diff without writing any files",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Write <file>.bak before patching each component file",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        sys.exit(f"ERROR: input CSV not found: {input_path}")

    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    if args.dry_run:
        print("DRY RUN — no files will be modified.\n")

    # Collect changes grouped by source_file
    # file_changes[source_file] = [(prop_key, lang, old_display, new_display, iri)]
    file_changes: dict[str, list] = defaultdict(list)
    total_changes = 0

    for row in rows:
        iri = row.get("iri", "").strip()
        source_file = row.get("source_file", "").strip()
        if not iri or not source_file:
            continue

        for sug_col, (prop_key, lang) in ANNOTATION_COLUMNS.items():
            if sug_col not in row:
                continue
            new_val = row.get(sug_col, "").strip()
            if not new_val:
                continue  # no suggestion → skip

            # Derive the corresponding current-value column
            cur_col = CURRENT_COLUMNS.get(sug_col)
            old_val = row.get(cur_col, "").strip() if cur_col else ""

            if old_val == new_val:
                continue  # identical → nothing to do

            file_changes[source_file].append((prop_key, lang, old_val, new_val, iri))
            total_changes += 1

    if total_changes == 0:
        print("No differences between current values and suggested values — nothing to do.")
        return

    print(f"Found {total_changes} annotation change(s) across {len(file_changes)} file(s).\n")

    abort = False
    total_replaced = 0
    total_appended = 0

    for source_file, changes in sorted(file_changes.items()):
        owl_path = Path(source_file)
        if not owl_path.exists():
            print(f"WARNING: {source_file} not found — skipping", file=sys.stderr)
            continue

        print(f"{owl_path.name}: {len(changes)} change(s)")
        n_rep, n_app = patch_file(owl_path, changes, args.dry_run, args.backup)

        if n_rep == -1:  # abort signal
            abort = True
            break

        total_replaced += n_rep
        total_appended += n_app

    if abort:
        print(
            "\nABORTED: ambiguous match detected — no files were written.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.dry_run:
        print(f"\nDry run: {total_replaced} replacement(s) + {total_appended} append(s) planned.")
    else:
        print(f"\nDone: {total_replaced} replacement(s) + {total_appended} append(s) applied.")


if __name__ == "__main__":
    main()
