#!/usr/bin/env python3
"""AI-assisted review of PMDco labels and definitions using the Anthropic Claude API.

Reads the CSV produced by extract_labels.py, sends batches of terms to Claude for
review, and writes suggestions into the *_suggested columns of a new output CSV.

The agent suggests improvements to:
  - English and German rdfs:labels (clarity, translation accuracy, naming consistency)
  - English and German skos:definitions (genus-differentia structure, no circular
    references, appropriate for materials scientists)

Rows where all four *_suggested columns are already non-empty are skipped (idempotent
re-runs / partial runs are safe).

Usage:
    python3 agent_review.py --input pmdco_labels.csv [--output pmdco_labels_reviewed.csv]
                            [--batch-size 20] [--model claude-sonnet-4-6]
                            [--dry-run] [--rows N]

Environment:
    ANTHROPIC_API_KEY   Required. Set in .env or shell environment.

Run from the repository root.
"""

import csv
import json
import os
import sys
import time
import argparse
from pathlib import Path

import re

try:
    import anthropic
except ImportError:
    sys.exit("ERROR: anthropic SDK not found — pip install anthropic")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv optional

SYSTEM_PROMPT = """\
You are an expert ontology editor for the PMDco (Platform MaterialDigital Core Ontology).

PMDco is a materials science ontology built on BFO 2020 (Basic Formal Ontology).
Key hierarchy used here:
  - BFO_0000019 (quality) — intrinsic qualities of material entities
  - BFO_0000145 (relational quality) — qualities relating two entities
  - BFO_0000016 (disposition) — capacities/capabilities of entities
  - PMD_0000005 (material property) — material-specific qualities

Target audience: materials scientists and ontology engineers.

Definition style guidelines:
  - Use genus-differentia structure: "[term] is a [parent class] that [differentiating condition]."
  - Third-person, declarative, present tense.
  - No circular definitions (do not use the term being defined in the definition).
  - Avoid vague language ("some", "various", "certain").
  - Definitions must be concise (1-3 sentences maximum).
  - German labels and definitions must be accurate scientific German, not machine-translated.
  - English labels: use standard materials science terminology.
  - German labels: use established German materials science terms where they exist.

Your task: review each term and suggest improvements. Return empty string "" for any
field you consider already acceptable — only fill fields that genuinely need improvement.
Do NOT invent new terms or change the ontological meaning/classification of a term.
"""

CSV_FIELDS = [
    "iri", "source_file", "parent_iris",
    "label_en", "label_de", "label_none",
    "definition_en", "definition_de", "definition_none",
    "label_en_suggested", "label_de_suggested",
    "definition_en_suggested", "definition_de_suggested",
    "notes",
]

SUGGESTED_FIELDS = [
    "label_en_suggested",
    "label_de_suggested",
    "definition_en_suggested",
    "definition_de_suggested",
]


def row_is_reviewed(row: dict) -> bool:
    """Return True if all four suggested columns are already non-empty."""
    return all(row.get(f, "").strip() for f in SUGGESTED_FIELDS)


def build_batch_prompt(batch: list[dict]) -> str:
    """Build the user message for a batch of terms."""
    lines = [
        "Review the following PMDco terms. For each term, suggest improvements to the"
        " label and definition fields. Return a JSON array — one object per term —"
        " with these exact keys:",
        '  "iri", "label_en_suggested", "label_de_suggested",'
        ' "definition_en_suggested", "definition_de_suggested"',
        "",
        'Use "" (empty string) for any field you consider already acceptable.',
        "Do not change the ontological classification or introduce new concepts.",
        "",
        "Terms:",
        "",
    ]
    for row in batch:
        iri_short = row["iri"].split("/")[-1]
        lines.append(f"IRI: {row['iri']}  ({iri_short})")
        lines.append(f"  Parent(s):       {row.get('parent_iris', '') or '(none recorded)'}")
        lines.append(f"  label_en:        {row.get('label_en', '') or '(missing)'}")
        lines.append(f"  label_de:        {row.get('label_de', '') or '(missing)'}")
        lines.append(f"  definition_en:   {row.get('definition_en', '') or '(missing)'}")
        lines.append(f"  definition_de:   {row.get('definition_de', '') or '(missing)'}")
        lines.append("")
    lines.append(
        "Return ONLY valid JSON — a top-level array, no markdown fences, no prose."
    )
    return "\n".join(lines)


def call_api_with_retry(
    client: anthropic.Anthropic,
    model: str,
    system_content: list,
    user_message: str,
    max_retries: int = 3,
) -> str | None:
    """Call the Anthropic API with exponential backoff. Returns response text or None."""
    delay = 2.0
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                system=system_content,
                messages=[{"role": "user", "content": user_message}],
            )
            return response.content[0].text
        except anthropic.RateLimitError:
            if attempt < max_retries - 1:
                print(f"  Rate limited — retrying in {delay:.0f}s …", file=sys.stderr)
                time.sleep(delay)
                delay *= 2
            else:
                print("  Rate limit exceeded — skipping batch after max retries", file=sys.stderr)
                return None
        except anthropic.APIError as exc:
            if attempt < max_retries - 1:
                print(f"  API error ({exc}) — retrying in {delay:.0f}s …", file=sys.stderr)
                time.sleep(delay)
                delay *= 2
            else:
                print(f"  API error after max retries: {exc}", file=sys.stderr)
                return None
    return None


def parse_suggestions(response_text: str, batch: list[dict]) -> dict[str, dict]:
    """Parse JSON array response → {iri: {field: suggested_value}}."""
    # Strip any accidental markdown fences
    text = response_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)

    try:
        items = json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"  JSON parse error: {exc}", file=sys.stderr)
        return {}

    if not isinstance(items, list):
        print("  Response is not a JSON array", file=sys.stderr)
        return {}

    result: dict[str, dict] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        iri = item.get("iri", "")
        if not iri:
            continue
        result[iri] = {
            "label_en_suggested": str(item.get("label_en_suggested", "")),
            "label_de_suggested": str(item.get("label_de_suggested", "")),
            "definition_en_suggested": str(item.get("definition_en_suggested", "")),
            "definition_de_suggested": str(item.get("definition_de_suggested", "")),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        default="scripts/label_workflow/pmdco_labels.csv",
        metavar="PATH",
        help="Input CSV from extract_labels.py",
    )
    parser.add_argument(
        "--output",
        default="scripts/label_workflow/pmdco_labels_reviewed.csv",
        metavar="PATH",
        help="Output CSV with suggested values filled in",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        metavar="N",
        help="Number of terms per API call (default: 20)",
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-6",
        help="Anthropic model ID (default: claude-sonnet-4-6)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the first batch prompt and exit without API calls",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=None,
        metavar="N",
        help="Process only the first N rows (useful for testing)",
    )
    args = parser.parse_args()

    # Load input CSV
    input_path = Path(args.input)
    if not input_path.exists():
        sys.exit(f"ERROR: input CSV not found: {input_path}")

    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    if args.rows:
        rows = rows[: args.rows]

    pending = [r for r in rows if not row_is_reviewed(r)]
    already_done = len(rows) - len(pending)

    if already_done:
        print(f"Skipping {already_done} already-reviewed rows (idempotent).")
    print(f"{len(pending)} rows to review in batches of {args.batch_size}.")

    if args.dry_run:
        first_batch = pending[: args.batch_size]
        print("\n--- DRY RUN: first batch prompt ---\n")
        print(build_batch_prompt(first_batch))
        print("\n--- Expected JSON response shape ---")
        example = [
            {
                "iri": r["iri"],
                "label_en_suggested": "",
                "label_de_suggested": "",
                "definition_en_suggested": "<suggested definition>",
                "definition_de_suggested": "",
            }
            for r in first_batch[:2]
        ]
        print(json.dumps(example, indent=2))
        sys.exit(0)

    # Check API key
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        sys.exit("ERROR: ANTHROPIC_API_KEY not set in environment or .env file")

    client = anthropic.Anthropic(api_key=api_key)

    # System prompt with cache_control for repeated batches
    system_content = [
        {
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }
    ]

    # Build an index of rows by IRI for fast updates
    row_index: dict[str, dict] = {r["iri"]: r for r in rows}

    # Process in batches
    batches = [pending[i: i + args.batch_size] for i in range(0, len(pending), args.batch_size)]
    total_suggested = 0

    for batch_num, batch in enumerate(batches, 1):
        print(f"Batch {batch_num}/{len(batches)} ({len(batch)} terms) …", end=" ", flush=True)
        prompt = build_batch_prompt(batch)
        response_text = call_api_with_retry(client, args.model, system_content, prompt)

        if response_text is None:
            print("SKIPPED (API error)")
            continue

        suggestions = parse_suggestions(response_text, batch)
        if not suggestions:
            print("SKIPPED (parse error)")
            continue

        updated = 0
        for row in batch:
            if row["iri"] in suggestions:
                for field, value in suggestions[row["iri"]].items():
                    row_index[row["iri"]][field] = value
                updated += 1
        total_suggested += updated
        print(f"OK ({updated}/{len(batch)} updated)")

    # Write output CSV (preserves all columns, all rows)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Use input fieldnames to preserve any extra columns in order
    out_fields = CSV_FIELDS

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows → {output_path}")
    print(f"Suggestions added: {total_suggested} terms updated.")


if __name__ == "__main__":
    main()
