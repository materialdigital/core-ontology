---
title: "feat: OWL label/definition extract–review–replace workflow"
type: feat
status: active
date: 2026-05-18
---

# feat: OWL label/definition extract–review–replace workflow

## Overview

Three-script pipeline for reviewing and correcting `rdfs:label` and `skos:definition`
annotations across all PMDco component OWL files:

1. **extract** — dump current labels/definitions + parent class into a CSV
2. **agent_review** — Claude-powered script analyses the CSV, writes suggestions into
   a `_suggested` variant of each column
3. **replace** — applies accepted corrections back into the OWL component files

The entry point for discovery is `pmdco-edit.owl`, which is read to obtain the
authoritative component file list from its `Import()` declarations.

## Problem Frame

Labels and definitions in PMDco need periodic review for translation accuracy (EN/DE),
definitional clarity, and consistency across term families.  The volume (~760
`skos:definition` entries across 8 component files, ~2700 `@en` + ~1400 `@de` labels)
makes manual review impractical without tooling.  An AI-assisted CSV round-trip
workflow provides a structured, version-controllable review cycle.

## Requirements Trace

- R1. Extract all `rdfs:label` and `skos:definition` values (all language tags) per
  term, with source file and parent class(es), into a single CSV.
- R2. The CSV schema must include both *current* values and *suggested/corrected*
  columns so a human can diff before committing replacements.
- R3. An agent script reads the CSV and writes language-specific suggestions into the
  `_suggested` columns without modifying OWL files.
- R4. A replacement script reads the CSV's `_suggested` (or manually edited) columns
  and patches exactly those `AnnotationAssertion` lines in the relevant component
  file — leaving all other triples untouched.
- R5. The workflow must handle the `pmdco:` prefix alias in `pmdco-qualities.owl` and
  the `:` alias used by all other component files.
- R6. No OWL structural axioms (SubClassOf, EquivalentClasses, etc.) are ever
  modified or emitted by any script.

## Scope Boundaries

- Only `rdfs:label` and `skos:definition` are targeted.  `rdfs:comment`,
  `IAO_0000115`, and `IAO_0000116` editorial notes are excluded.
- The replacement script performs literal string replacement only — it does not
  re-serialise the OWL graph.
- Parent class extraction covers only named (URI) parents from simple `SubClassOf`
  axioms; complex OWL expressions (restrictions, intersections) are recorded as
  `[complex]` and never modified.
- The agent script only *suggests* — it never writes directly to OWL files.

### Deferred to Separate Tasks

- Batch translation of missing `@de` labels via deep_translator (separate PR).
- SHACL validation run after replacement (existing CI covers this).

## Context & Research

### Relevant Code and Patterns

- `scripts/iof_quality_ingest/iof_to_pmdco.py` — rdflib parse pattern,
  `literal_to_ofn()`, `iri_to_ofn()`, graph-based annotation lookup — **reuse
  directly**.
- `scripts/fix_missing_annotations.py` — OFN text patching with regex,
  `pmdco_prefix_alias()` — **reuse directly** for write-back.
- `src/ontology/pmdco-edit.owl` — authoritative `Import()` list; parse this to
  discover component files rather than hardcoding.
- `src/templates/materials-listing.tsv` — ROBOT template column naming convention
  (informational).
- `src/ontology/components/scripts/curate_qualities.ipynb` — prior art for
  AI-assisted annotation curation using an LLM API; confirms the review pattern.

### Institutional Learnings

- rdflib is the only OWL parsing tool used in this repo; owlready2 has no footprint.
- OFN write-back must be string/regex manipulation — rdflib has no OFN serialiser.
- Prefix alias varies per file (`pmdco:` vs `:`); `pmdco_prefix_alias()` already
  solves this.
- ~14 annotations have no language tag (`PMD_0000111`, `PMD_0010013`, etc.); CSV
  must accommodate a `lang=none` bucket.
- Multiline literals exist; rdflib normalises them on parse; `literal_to_ofn()`
  collapses newlines to spaces — established convention.

## Key Technical Decisions

- **Discovery via pmdco-edit.owl Import list, not hardcoded paths**: parse the edit
  file with rdflib (or simple regex on the `Import(...)` lines) to obtain the
  component file list dynamically, so adding a new component is automatically picked
  up.
- **Per-file rdflib graph, not one merged graph**: parsing each component file into
  its own graph preserves the mapping `iri → source_file` without ambiguity.
- **CSV columns**: `iri, source_file, parent_iris, label_en, label_de,
  definition_en, definition_de, label_en_suggested, label_de_suggested,
  definition_en_suggested, definition_de_suggested, notes`.  Blank `_suggested` cell
  = no change needed.  Human edits `_suggested` columns directly before running
  replace.
- **Replacement strategy**: for each non-blank `_suggested` cell, find the exact OFN
  `AnnotationAssertion` line using a regex keyed on `(property, iri, lang_tag)` and
  replace the literal value in-place.  If no existing line matches (annotation is
  missing), append it just before the closing `)` of the `Ontology(...)` block,
  mirroring `fix_missing_annotations.py`.
- **Agent uses Anthropic Claude API** (not Azure OpenAI) via the `anthropic` SDK with
  prompt caching on the system prompt.  Processes rows in batches to reduce API
  calls.  Writes to `_suggested` columns; never touches OWL files.

## High-Level Technical Design

> *Directional guidance for review, not implementation specification.*

```
pmdco-edit.owl
      │  parse Import() lines
      ▼
component file list
      │  rdflib.Graph.parse() per file
      ▼
per-file graphs ──► SPARQL / graph.objects() ──► rows
      │                                            │
      │                                            ▼
      │                               CSV (current values + empty _suggested)
      │                                            │
      │                                    agent_review.py
      │                                    (Anthropic API, batch)
      │                                            │
      │                                    CSV (with _suggested filled)
      │                                            │
      │                              human reviews / edits CSV
      │                                            │
      └────────────────────────────────── replace_labels.py
                                          (regex OFN patch per file)
```

## Output Structure

    scripts/
      label_workflow/
        extract_labels.py        # Unit 1
        agent_review.py          # Unit 2
        replace_labels.py        # Unit 3
        README.md                (optional, out of scope for plan)

## Implementation Units

---

- [ ] **Unit 1: extract_labels.py — CSV extraction from component OWL files**

**Goal:** Produce a well-structured CSV of all `rdfs:label` and `skos:definition`
values from every PMDco component file, one row per term, with parent class URIs and
source file path.

**Requirements:** R1, R2, R5

**Dependencies:** None (standalone script)

**Files:**
- Create: `scripts/label_workflow/extract_labels.py`

**Approach:**
- Read `src/ontology/pmdco-edit.owl` and extract the list of imported component file
  paths from `Import(...)` lines (simple regex or rdflib parse — regex is sufficient
  here since the file is stable and small).
- For each component file, `Graph.parse(path, format="application/owl-functional")`.
- Query each graph for all terms matching the `https://w3id.org/pmd/co/PMD_` IRI
  pattern (use `graph.subjects()` or a SPARQL `SELECT DISTINCT ?s` on the
  graph's triples).
- For each term IRI:
  - `label_en`: `graph.value(term, RDFS.label, any=False)` filtered to `@en`;
    if multiple `@en` labels exist, join with ` | `.
  - `label_de`: same for `@de`.
  - `definition_en`, `definition_de`: same for `skos:definition`.
  - `parent_iris`: `list(graph.objects(term, RDFS.subClassOf))` — filter to
    `URIRef` only, stringify to CURIE or full IRI; join with ` | `.  BNode parents
    recorded as `[complex]`.
  - `source_file`: repo-relative path of the component file.
- Emit one CSV row per term; `_suggested` columns output as empty strings.
- Sort rows by `source_file`, then by IRI numerically.
- Output path: `scripts/label_workflow/pmdco_labels.csv` (or CLI arg `--output`).

**Patterns to follow:**
- `scripts/iof_quality_ingest/iof_to_pmdco.py` — rdflib graph parse and
  `graph.objects()` traversal pattern.
- `scripts/fix_missing_annotations.py` — `pmdco_prefix_alias()` (for reference,
  though rdflib resolves prefixes transparently during extraction).

**Test scenarios:**
- Happy path: run against real component files, assert row count matches known
  `skos:definition` totals (e.g. pmdco-qualities.owl ≈ 762 definitions).
- Happy path: each row for `PMD_0000005` has `label_en="material property"`,
  `label_de="Materialeigenschaft"`, `definition_en` non-empty, `source_file` set.
- Edge case: terms with no `@de` label emit an empty `label_de` cell (not an error).
- Edge case: terms with a language-untagged label/definition appear in a `label_none`
  / `definition_none` column bucket; they are not silently dropped.
- Edge case: `parent_iris` for a term with a complex `ObjectSomeValuesFrom` parent
  contains `[complex]`, not an error.
- Edge case: if a term has two `@en` labels (data inconsistency), the cell contains
  both joined with ` | ` and a warning is printed to stderr.
- Integration: running the script twice on the same files produces identical CSV
  output (deterministic sort).

**Verification:**
- Row count of output CSV matches total declared PMDco term count (check via
  `grep -c "Declaration(Class" components/*.owl`).
- No `AnnotationAssertion` lines in the source files are silently skipped
  (validate against a manual spot-check of 5 terms).
- `_suggested` columns in output are all empty strings.

---

- [ ] **Unit 2: agent_review.py — Claude-powered suggestion writer**

**Goal:** Read the extracted CSV and populate `_suggested` columns with AI-generated
label and definition improvement suggestions, using the Anthropic Claude API with
prompt caching.

**Requirements:** R3

**Dependencies:** Unit 1 output CSV; `anthropic` SDK installed.

**Files:**
- Create: `scripts/label_workflow/agent_review.py`

**Approach:**
- Read the CSV, skip rows where all `_suggested` columns are already filled (allows
  re-run / partial runs).
- Batch rows (e.g. 20 terms per API call) to keep prompt size manageable.
- System prompt (cached with `cache_control: {"type": "ephemeral"}`): explain
  PMDco ontology context, BFO quality hierarchy, target audience (materials
  scientists), desired definition style (concise, genus-differentia, third-person,
  no circular references).
- User message per batch: provide current `label_en`, `label_de`, `definition_en`,
  `definition_de`, and `parent_iris` for each term; ask the model to return a JSON
  array with `iri`, `label_en_suggested`, `label_de_suggested`,
  `definition_en_suggested`, `definition_de_suggested` fields.  Empty string = no
  change.
- Parse JSON response; write `_suggested` values back into the CSV.  Handle API
  errors with retry (exponential backoff, max 3 attempts).
- Write output to `scripts/label_workflow/pmdco_labels_reviewed.csv` (or
  `--output` arg), preserving all existing columns.
- `--dry-run` flag prints first batch prompt and expected response format without
  making API calls.
- API key read from `ANTHROPIC_API_KEY` env var (`.env` file support via
  python-dotenv, already in project).

**Patterns to follow:**
- `src/ontology/components/scripts/curate_qualities.ipynb` — prior AI curation
  pattern (batch loop, prompt structure).
- Anthropic SDK prompt caching pattern: pass `cache_control` on the system prompt
  `content` block.
- Use `claude-sonnet-4-6` as default model (current Sonnet, matches environment);
  expose as `--model` CLI arg.

**Test scenarios:**
- Happy path (`--dry-run`): prints a well-formed batch prompt and exits 0 without
  making API calls.
- Happy path: given a CSV with 3 rows, the output CSV has non-empty `_suggested`
  values for at least the rows where the model suggested a change.
- Edge case: rows where all `_suggested` columns are already non-empty are skipped
  (idempotent re-run).
- Error path: invalid `ANTHROPIC_API_KEY` emits a clear error message and exits
  non-zero.
- Error path: malformed JSON in API response triggers a retry; after max retries,
  the batch is skipped with a warning and remaining rows are processed.
- Edge case: row with no `definition_en` still produces a suggestion prompt that
  asks the model to draft a definition, not just improve one.

**Verification:**
- `--dry-run` exits 0 and prints a readable prompt.
- After a real run on a 10-row sample CSV, `_suggested` columns are non-empty for
  terms the model judged improvable, empty for terms it found acceptable.
- Re-running on an already-reviewed CSV does not overwrite existing suggestions.

---

- [ ] **Unit 3: replace_labels.py — OFN in-place patch**

**Goal:** Apply accepted corrections from the reviewed CSV back into the OWL
component files, replacing only the targeted `AnnotationAssertion` literals without
touching any other content.

**Requirements:** R4, R5, R6

**Dependencies:** Unit 1 (CSV schema), Unit 2 output CSV (or manually edited CSV).

**Files:**
- Create: `scripts/label_workflow/replace_labels.py`

**Approach:**
- Read the reviewed CSV.  For each row, collect the columns that differ between
  current value and `_suggested` value (non-empty `_suggested` cell ≠ current cell).
- Group changed rows by `source_file` to batch file reads/writes.
- For each component file with changes:
  1. Read file text.
  2. Detect prefix alias via `pmdco_prefix_alias()` (from
     `fix_missing_annotations.py`).
  3. For each changed annotation on a term:
     - Build a regex pattern matching
       `AnnotationAssertion(<prop> <prefixed_iri> "<old_value>"@<lang>)`.
       Account for escaped quotes and that the value may span no more than one line
       (multiline literals are edge cases; warn and skip if encountered).
     - Replace with `AnnotationAssertion(<prop> <prefixed_iri> "<new_value>"@<lang>)`.
  4. If no existing line matched (annotation absent), append it before the closing
     `)` of the `Ontology(...)` block — same approach as
     `fix_missing_annotations.py`.
  5. Write the patched text back to the same path.
- `--dry-run` flag: print a diff of each planned replacement without writing files.
- `--backup` flag: write `<file>.bak` before patching.
- Exit non-zero and skip all writes if any regex match is ambiguous (> 1 hit for
  the same pattern in one file).

**Patterns to follow:**
- `scripts/fix_missing_annotations.py` — regex-based OFN patching, prefix alias
  detection, append-before-closing-paren pattern.
- `scripts/iof_quality_ingest/iof_to_pmdco.py` — `literal_to_ofn()` for correctly
  escaping double quotes and emitting the language tag.

**Test scenarios:**
- Happy path (`--dry-run`): given a CSV with 2 changes, prints expected diff lines
  and exits 0 without modifying files.
- Happy path: after a real run, `rdfs:label` value for the target term in the
  component file matches the `_suggested` value from the CSV.
- Happy path: a `@de` label missing from the OWL file is appended correctly when the
  `_suggested` cell is non-empty and the current cell was empty.
- Edge case: `_suggested` cell identical to current value → no change emitted for
  that annotation.
- Edge case: term with `pmdco:` prefix alias (qualities.owl) is patched correctly.
- Edge case: term with `:` prefix alias (other component files) is patched correctly.
- Error path: if the regex finds 0 matches for an existing non-empty current value,
  emit a warning (the file may have been manually edited) and skip that annotation.
- Error path: if the regex finds > 1 matches (ambiguous hit), exit non-zero without
  writing any file.
- Integration: run extract → manually set one `_suggested` cell → run replace →
  run extract again → the new extract's current value matches the previously
  suggested value.

**Verification:**
- `--dry-run` shows exactly the lines that will change, nothing else.
- `git diff` after a real run touches only the targeted `AnnotationAssertion` lines
  in the expected files.
- No `SubClassOf`, `EquivalentClasses`, or any non-annotation line is altered.

---

## System-Wide Impact

- **Interaction graph:** Scripts read/write component OWL files directly. ODK `make`
  and ROBOT downstream assembly are unaffected as long as OFN syntax remains valid.
- **Error propagation:** replace_labels.py is the only script that writes to tracked
  files; `--dry-run` and `--backup` flags protect against accidental data loss.
- **State lifecycle risks:** Partial runs leave the CSV in a partially filled state;
  re-running agent_review.py skips already-suggested rows safely (idempotent).
- **API surface parity:** No changes to OWL term IRIs, SubClassOf axioms, or any
  other annotation property — only `rdfs:label` and `skos:definition` literal values
  are touched.
- **Integration coverage:** After replacement, run `git diff` + SHACL CI to verify
  no structural regressions.
- **Unchanged invariants:** All SubClassOf axioms, EquivalentClasses, property
  declarations, IRI allocations, and import statements are untouched by all three
  scripts.

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| Regex replacement hits wrong line (e.g. two terms share a literal) | Script exits non-zero on > 1 match; `--dry-run` to inspect before committing |
| Multiline literal in a `skos:definition` breaks regex match | Warn and skip; log term IRI for manual review |
| Agent over-corrects / introduces wrong terminology | `_suggested` columns are advisory; human reviews CSV before running replace |
| `pmdco-edit.owl` Import list changes (new component added) | Extract script reads the Import list dynamically — no hardcoded paths |
| rdflib OFN parser version drift | Pin rdflib version in script header comment; tested against rdflib 6.x (current project baseline) |
| Anthropic API rate limits | Batch size tunable via `--batch-size` arg; exponential backoff on 429 |

## Sources & References

- Related code: `scripts/iof_quality_ingest/iof_to_pmdco.py`
- Related code: `scripts/fix_missing_annotations.py`
- Related code: `src/ontology/components/scripts/curate_qualities.ipynb`
- Related template: `src/templates/materials-listing.tsv`
