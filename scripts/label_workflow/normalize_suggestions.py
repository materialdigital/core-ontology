#!/usr/bin/env python3
"""Normalize *_suggested columns in a reviewed CSV to ISO 704 noun-phrase form.

Strips leading articles and trailing periods from agent-generated suggestions
that were written as full sentences (e.g. "A yield strength is a mechanical
property that…" → "mechanical property that…").

Rules applied:
  English definitions/labels:
    - Remove leading "A/An [words] is a/an " (full Aristotelian subject)
    - Remove remaining leading article "A " or "An "
    - Lowercase first character
    - Strip trailing period

  German definitions/labels:
    - Remove leading "Ein/Eine [words] ist ein/eine " (full Aristotelian subject)
    - Remove remaining leading article "Ein/Eine/Der/Die/Das "
    - Keep case (German nouns are capitalised — correct orthography)
    - Strip trailing period

  DEPRECATED prefix is preserved unchanged around the above transforms.

Usage:
    python3 normalize_suggestions.py [--input PATH]

Run from the repository root.
"""

import re
import csv
import sys
import shutil
import argparse
from pathlib import Path


def _norm_en(s: str) -> str:
    s = s.strip()
    if not s:
        return s
    dep = ""
    if s.startswith("DEPRECATED "):
        dep = "DEPRECATED "
        s = s[11:]
    # Strip full Aristotelian subject: "A/An [term words] is a/an "
    s = re.sub(r'^[Aa]n?\s+[\w][\w\s\-\/]*?\s+is\s+(?:a|an)\s+', '', s)
    # Strip remaining leading article
    s = re.sub(r'^[Aa]n?\s+', '', s)
    # Lowercase first character
    if s:
        s = s[0].lower() + s[1:]
    # Strip trailing period
    s = s.rstrip('.')
    return dep + s


def _norm_de(s: str) -> str:
    s = s.strip()
    if not s:
        return s
    dep = ""
    if s.startswith("DEPRECATED "):
        dep = "DEPRECATED "
        s = s[11:]
    # Strip full Aristotelian subject: "Ein/Eine [term] ist ein/eine "
    s = re.sub(
        r'^(?:Ein(?:e[ns]?)?|Der|Die|Das)\s+[\w][\w\s\-\/]*?\s+ist\s+'
        r'(?:ein(?:e[ns]?)?|der|die|das)\s+',
        '', s,
    )
    # Strip remaining leading article
    s = re.sub(r'^(?:Ein(?:e[ns]?)?|Der|Die|Das)\s+', '', s)
    # German: keep case (nouns stay capitalised)
    # Strip trailing period
    s = s.rstrip('.')
    return dep + s


def _norm_label(s: str) -> str:
    s = s.strip().rstrip('.')
    if not s:
        return s
    if s.startswith("DEPRECATED "):
        return s
    # Lowercase first character unless it is an acronym (all-caps first word)
    first_word = s.split()[0]
    if not first_word.isupper():
        s = s[0].lower() + s[1:]
    return s


TRANSFORMS = {
    "definition_en_suggested": _norm_en,
    "definition_de_suggested": _norm_de,
    "label_en_suggested":      _norm_label,
    "label_de_suggested":      _norm_label,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        default="scripts/label_workflow/pmdco_labels_reviewed.csv",
        metavar="PATH",
        help="CSV to normalize in-place (default: scripts/label_workflow/pmdco_labels_reviewed.csv)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip writing a .bak backup before modifying",
    )
    args = parser.parse_args()

    path = Path(args.input)
    if not path.exists():
        sys.exit(f"ERROR: {path} not found")

    if not args.no_backup:
        shutil.copy2(path, str(path) + ".bak")
        print(f"Backup written: {path}.bak")

    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    if not rows:
        print("No rows found.")
        return

    changed = 0
    for row in rows:
        row_changed = False
        for col, fn in TRANSFORMS.items():
            if col not in row:
                continue
            before = row[col]
            after = fn(before)
            if after != before:
                row[col] = after
                row_changed = True
        if row_changed:
            changed += 1

    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Normalized {changed} rows → {path}")


if __name__ == "__main__":
    main()
