#!/bin/bash
# Run the PR quality checks locally using the same ODK Docker container as CI.
# Usage: bash scripts/test_pr_checks.sh [--annotate-only | --shacl-only | --odk-only]
#
# Output files are written to /tmp/pmdco-pr-check/

set -e

REPO="$(cd "$(dirname "$0")/.." && pwd)"
OUT=/tmp/pmdco-pr-check
ODK_IMAGE=obolibrary/odkfull:v1.6
SKIP_ANNOTATE=0
SKIP_ODK=0
SKIP_SHACL=0

ANNOTATE_DRY_RUN=0

for arg in "$@"; do
  case ${arg} in
    --annotate-only)     SKIP_ODK=1;      SKIP_SHACL=1 ;;
    --annotate-dry-run)  SKIP_ODK=1;      SKIP_SHACL=1; ANNOTATE_DRY_RUN=1 ;;
    --shacl-only)        SKIP_ANNOTATE=1; SKIP_ODK=1 ;;
    --odk-only)          SKIP_ANNOTATE=1; SKIP_SHACL=1 ;;
    *) echo "Unknown argument: ${arg}"; exit 1 ;;
  esac
done

mkdir -p "${OUT}"

# ---------------------------------------------------------------------------
# Job 0: Auto-fill missing IAO_0000114 / IAO_0000117 annotations
# ---------------------------------------------------------------------------
if [[ "${SKIP_ANNOTATE}" -eq 0 ]]; then
  echo ""
  echo "============================================================"
  echo " Job 0: Auto-fill missing IAO annotations"
  echo "============================================================"

  DRY_RUN_FLAG=""
  if [[ "${ANNOTATE_DRY_RUN}" -eq 1 ]]; then
    DRY_RUN_FLAG="--dry-run"
  fi

  docker run --rm \
    -v "${REPO}:/work" \
    -v "${OUT}:/out" \
    -w /work \
    -e "DRY_RUN_FLAG=${DRY_RUN_FLAG}" \
    "${ODK_IMAGE}" \
    bash -c '
      set -e

      echo "--- Installing Python dependencies ---"
      pip install pyshacl rdflib -q --break-system-packages

      echo "--- Merging ontology ---"
      robot merge \
        --catalog src/ontology/catalog-v001.xml \
        --input src/ontology/pmdco-edit.owl \
        --output /out/merged.ttl

      echo "--- Reasoning (ELK) ---"
      robot reason \
        --reasoner elk \
        --input /out/merged.ttl \
        --output /out/reasoned.ttl

      echo "--- Running initial SHACL pass ---"
      python3 -m pyshacl \
        -f turtle \
        --advanced \
        -s .github/workflow_resources/abox_quality_shacl.ttl \
        /out/reasoned.ttl > /out/shacl_initial.ttl || true

      echo "--- Adding missing IAO_0000114 / IAO_0000117 ---"
      python3 /work/scripts/fix_missing_annotations.py \
        src/ontology/components \
        --shacl-report /out/shacl_initial.ttl \
        ${DRY_RUN_FLAG}
    '
  echo ""
  echo "Job 0 PASSED — component files patched (if any annotations were missing)"
  echo "Review changes with: git diff src/ontology/components/"
fi

# ---------------------------------------------------------------------------
# Job 1: ODK make sub-targets (reason, SPARQL violations, ROBOT report)
# ---------------------------------------------------------------------------
if [[ "${SKIP_ODK}" -eq 0 ]]; then
  echo ""
  echo "============================================================"
  echo " Job 1: ODK make (reason_test, sparql_test, robot_reports)"
  echo "============================================================"
  # test_fast includes validate_profile which needs pre-built mirror/*.owl files
  # (generated artifacts not in git). Run the sub-targets that work on a clean checkout.
  docker run --rm \
    -v "${REPO}:/work" \
    -w /work/src/ontology \
    "${ODK_IMAGE}" \
    make IMP=false PAT=false COMP=false MIR=false validate_idranges reason_test sparql_test robot_reports
  echo ""
  echo "Job 1 PASSED"
fi

# ---------------------------------------------------------------------------
# Job 2: Annotation SHACL
# ---------------------------------------------------------------------------
if [[ "${SKIP_SHACL}" -eq 0 ]]; then
  echo ""
  echo "============================================================"
  echo " Job 2: Annotation standard SHACL"
  echo "============================================================"
  docker run --rm \
    -v "${REPO}:/work" \
    -v "${OUT}:/out" \
    -w /work \
    "${ODK_IMAGE}" \
    bash -c '
      set -e

      echo "--- Installing pyshacl ---"
      pip install pyshacl -q --break-system-packages

      echo "--- Merging ontology ---"
      robot merge \
        --catalog src/ontology/catalog-v001.xml \
        --input src/ontology/pmdco-edit.owl \
        --output /out/merged.ttl

      echo "--- Reasoning (ELK) ---"
      robot reason \
        --reasoner elk \
        --input /out/merged.ttl \
        --output /out/reasoned.ttl

      echo "--- Running SHACL validation ---"
      python3 -m pyshacl \
        -f turtle \
        --advanced \
        -s .github/workflow_resources/abox_quality_shacl.ttl \
        /out/reasoned.ttl > /out/shacl_report.ttl || true

      echo "--- Checking for blocking violations (PMDco terms, sh:Violation only) ---"
      # Use rdflib (pyshacl dependency) — robot query chokes on the OWL blank-node
      # structures pyshacl includes alongside the validation results in its output.
      python3 /work/scripts/check_shacl_violations.py /out/shacl_report.ttl

      echo "--- Generating full validation reports ---"
      robot query \
        --input /out/shacl_report.ttl \
        --query .github/workflow_resources/q_listValidationResults.sparql \
        /out/ValidationReport.csv
      robot query \
        --input /out/shacl_report.ttl \
        --query .github/workflow_resources/q_countValidationResults.sparql \
        /out/ValidationSummary.csv

      echo ""
      echo "=== Violation summary (PMDco terms only) ==="
      cat /out/ValidationSummary.csv
      echo ""
      echo "=== Full report ==="
      cat /out/ValidationReport.csv
    '
  echo ""
  echo "Job 2 PASSED (warnings may appear in the report above)"
  echo "Full reports written to: ${OUT}/"
fi
