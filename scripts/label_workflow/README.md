# Label / Definition Review Workflow

Round-trip pipeline for reviewing and correcting `rdfs:label` and `skos:definition`
annotations across all PMDco component OWL files.

## Prerequisites

```bash
pip install rdflib anthropic python-dotenv
```

Set your API key (or put it in a `.env` file at the repo root):

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Workflow

Run all commands from the **repository root**.

### Step 1 — Extract current annotations to CSV

```bash
python3 scripts/label_workflow/extract_labels.py
```

Reads `src/ontology/pmdco-edit.owl` to discover component files, then produces
`scripts/label_workflow/pmdco_labels.csv` with one row per term containing:

- `iri`, `source_file`, `parent_iris`
- `label_en`, `label_de`, `label_none`
- `definition_en`, `definition_de`, `definition_none`
- empty `*_suggested` columns for corrections
- `notes`

Options:

```
--edit-owl PATH   Path to pmdco-edit.owl  (default: src/ontology/pmdco-edit.owl)
--output PATH     Output CSV path         (default: scripts/label_workflow/pmdco_labels.csv)
```

### Step 2 — Agent review (AI suggestions)

```bash
python3 scripts/label_workflow/agent_review.py \
  --input  scripts/label_workflow/pmdco_labels.csv \
  --output scripts/label_workflow/pmdco_labels_reviewed.csv
```

Sends terms in batches to Claude and fills the `*_suggested` columns with proposed
improvements. Already-filled rows are skipped (safe to re-run / resume).

Options:

```
--input PATH      Input CSV             (default: scripts/label_workflow/pmdco_labels.csv)
--output PATH     Output CSV            (default: scripts/label_workflow/pmdco_labels_reviewed.csv)
--batch-size N    Terms per API call    (default: 20)
--model ID        Anthropic model       (default: claude-sonnet-4-6)
--rows N          Process only first N rows (useful for testing)
--dry-run         Print first batch prompt and exit without API calls
```

### Step 3 — Human review

Open `pmdco_labels_reviewed.csv` in a spreadsheet editor.

- Edit or clear `*_suggested` cells as needed.
- Leave a cell **empty** to keep the current value unchanged.
- Use the `notes` column for free-text comments.

### Step 4 — Preview changes (dry run)

```bash
python3 scripts/label_workflow/replace_labels.py \
  --input scripts/label_workflow/pmdco_labels_reviewed.csv \
  --dry-run
```

Prints a diff of every planned replacement without touching any file.

### Step 5 — Apply corrections

```bash
python3 scripts/label_workflow/replace_labels.py \
  --input   scripts/label_workflow/pmdco_labels_reviewed.csv \
  --backup
```

Patches only the targeted `AnnotationAssertion` lines in the OWL component files.
`--backup` writes `<file>.bak` before each edit.

Options:

```
--input PATH   Reviewed CSV   (default: scripts/label_workflow/pmdco_labels_reviewed.csv)
--dry-run      Show diff, no writes
--backup       Write <file>.bak before patching
```

### Step 6 — Validate

```bash
git diff src/ontology/components/
```

Check that only `rdfs:label` and `skos:definition` lines changed.  
SHACL validation runs automatically on the PR via CI (`pr-shacl.yaml`).

## Label and definition style rules

These rules govern what the agent suggests and what is valid in the
`*_suggested` columns.  They follow **ISO 704** (Terminology work — Principles
and methods) and standard IEC/ISO/ASTM materials-engineering terminology.

### Labels (`rdfs:label`)

| Rule | Correct | Wrong |
|------|---------|-------|
| Plain noun phrase | `tensile strength` | `Tensile Strength`, `measures tensile` |
| Lowercase first letter (EN) | `yield strength` | `Yield strength` |
| German: DIN/VDI/DGM term | `Streckgrenze` | `Fließgrenze` (when DIN uses `Streckgrenze`) |
| No trailing period | `cooling rate` | `cooling rate.` |
| No leading article | `process attribute` | `A process attribute` |

### Definitions (`skos:definition`)

Definitions must be **ISO 704 noun-phrase** form — not a full sentence.

| Rule | Correct | Wrong |
|------|---------|-------|
| Noun-phrase, no sentence | `mechanical property that quantifies…` | `A yield strength is a mechanical property…` |
| No leading article (EN) | `process attribute that describes…` | `A process attribute that describes…` |
| No trailing period | `…per unit time` | `…per unit time.` |
| German: no leading article | `Prozessattribut, das die Änderung…` | `Ein Prozessattribut, das die Änderung….` |
| Genus = most specific parent | `material property that…` (not `quality that…`) | |
| One differentia clause | single relative clause | two independent clauses |
| No circular reference | genus ≠ term itself | `yield strength: the yield strength of…` |
| No hedging | definitive statement | `typically`, `often`, `generally` |

**Structure:** `[genus] [differentia]`

Example:
```
✓  mechanical property that quantifies the stress at which a material begins
   to deform plastically
✗  A yield strength is a mechanical property that quantifies the stress at
   which a material begins to deform plastically.
```

### Post-processing existing suggestions

If suggestions were generated with sentence form (leading article + period),
run the normalizer:

```bash
python3 scripts/label_workflow/normalize_suggestions.py \
  --input scripts/label_workflow/pmdco_labels_reviewed.csv
```

This strips leading articles (`A`/`An`/`Ein`/`Eine`) and trailing periods from
all `*_suggested` columns in-place (writes a `.bak` backup first).

## CSV column reference

| Column | Description |
|--------|-------------|
| `iri` | Full term IRI |
| `source_file` | Repo-relative path to the component OWL file |
| `parent_iris` | Named parent class IRIs, `\|`-separated; `[complex]` = has OWL expression parent |
| `label_en` / `label_de` / `label_none` | Current `rdfs:label` per language tag |
| `definition_en` / `definition_de` / `definition_none` | Current `skos:definition` per language tag |
| `label_en_suggested` … | Suggested replacement — empty = keep current |
| `notes` | Free-text comments |

## ROBOT template files (materials-listing.owl)

`materials-listing.owl` is **generated by ROBOT from a TSV template** — it is not
manually maintained:

```
src/templates/materials-listing.tsv  →  make  →  src/ontology/components/materials-listing.owl
```

This file is **intentionally excluded** from the workflow.  `extract_labels.py` only
picks up `pmdco-*.owl` files from the Import list; `materials-listing.owl` does not
match that prefix and is never processed.

If you need to review or correct labels/definitions for terms that live in
`materials-listing.owl` (IRI range `PMD_0010000`–`PMD_0011000`), edit the TSV
directly:

```text
src/templates/materials-listing.tsv   ← edit here
```

Column mapping in the TSV:
- Column `Label` (`AL rdfs:label@en`) → `rdfs:label @en`
- Column `Definition` (`AL skos:definition@en`) → `skos:definition @en`

After saving the TSV, regenerate the OWL file:

```bash
# inside the ODK docker environment
cd src/ontology && make components/materials-listing.owl
```

Do **not** run `replace_labels.py` on `materials-listing.owl` — any direct OWL edits
would be overwritten the next time `make` runs.

Note: terms in the `PMD_001xxxx` IRI range also appear in `pmdco-manufacturing.owl`
(those are manually maintained). The workflow handles them normally.

## Safety notes

- `replace_labels.py` exits non-zero **without writing any file** if a replacement
  pattern matches more than one line in a file (ambiguous hit).
- Only `rdfs:label` and `skos:definition` are ever touched; `SubClassOf`,
  `EquivalentClasses`, and all other axioms are untouched.
- The agent script **never writes to OWL files** — only to the CSV.
