# GitHub Actions Workflows

## On push to `main`

### `automake.yaml` — Import refresh and publish
Runs `make refresh-imports pmdco.ttl` in the ODK container to regenerate import modules and the assembled `pmdco.ttl`, then commits the result back to `main`.

### `quality-checks.yaml` — ROBOT quality checks
Merges all component files and runs ROBOT checks: OWL DL profile validation and SPARQL-based violation queries (missing labels, missing definitions, deprecated `http://` IRIs).

### `abox_conventions_shacl.yaml` — Annotation convention SHACL
Merges and reasons the ontology, then runs pyshacl against `abox_quality_shacl.ttl` to check annotation conventions on all PMDco terms. Produces `ValidationReport.csv` and `ValidationSummary.csv` as downloadable artifacts.

### `shacl.yaml` — Pattern SHACL
Iterates over all usage patterns in `patterns/` and validates each pattern's example data (`shape-data.ttl`) against its SHACL shapes and the auto-generated shapes. Also checks that every IRI used in example data exists in the merged ontology.

### `deploy.yaml` — HTML documentation
Builds versioned HTML documentation for all releases using Widoco and MkDocs, then deploys to GitHub Pages.

---

## On pull requests targeting `main`

### `pr-qc.yaml` — PR Quality Checks
Three jobs run in sequence to gate every PR before it can be merged:

1. **`auto-annotate`** — Runs an initial SHACL pass, then automatically adds any missing `IAO_0000114` (curation status) and `IAO_0000117` (term editor) annotations to component files. Curation status is derived from the SHACL result; the term editor is looked up from `pmdco-idranges.owl`. Changes are committed back to the PR branch. Existing annotations are never overwritten.

2. **`odk-make-test`** — Runs ODK `make` checks (IRI range validation, ELK consistency reasoning, SPARQL violation queries, ROBOT OBO report) on the updated branch.

3. **`annotation-shacl`** — Re-runs SHACL on the updated branch. Fails the PR on any `sh:Violation` for PMDco-namespaced terms. Warnings (missing German labels/definitions, missing `skos:example`, duplicate language tags) are reported in the artifact but do not block the PR.

Artifacts `ValidationReport.csv` and `ValidationSummary.csv` are always uploaded so reviewers can inspect the full annotation status.

---

## Shared resources — `.github/workflow_resources/`

| File | Used by |
|---|---|
| `abox_quality_shacl.ttl` | `abox_conventions_shacl.yaml`, `pr-qc.yaml` |
| `q_listValidationResults.sparql` | `abox_conventions_shacl.yaml`, `pr-qc.yaml` |
| `q_countValidationResults.sparql` | `abox_conventions_shacl.yaml`, `pr-qc.yaml` |
| `q_shacl_errors_only.sparql` | reference query (violations scoped to PMDco IRIs) |
| `qc-queries/` | `quality-checks.yaml` |
