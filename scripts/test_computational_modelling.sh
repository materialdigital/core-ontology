#!/bin/bash
# In ODK: cd src/ontology && sh run.sh bash /work/scripts/test_computational_modelling.sh
# Or locally: ROBOT=/path/to/robot bash scripts/test_computational_modelling.sh
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
ROBOT="${ROBOT:-robot}"
OUT="$(mktemp -d "${TMPDIR:-/tmp}/pmdco-computational-test.XXXXXX")"
# Set KEEP_ARTIFACTS=1 to retain successful or failed runs for debugging.
cleanup() {
  if [[ "${KEEP_ARTIFACTS:-0}" == 1 ]]; then
    echo "Retained validation artifacts: ${OUT}"
  else
    rm -rf -- "${OUT}"
  fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
echo "Validation artifacts: ${OUT}"
"${ROBOT}" merge --catalog "${REPO}/src/ontology/catalog-v001.xml" \
  --input "${REPO}/src/ontology/pmdco-edit.owl" \
  --output "${OUT}/ontology.owl"
# Locality module retains the axioms relevant to this pattern. Full ontology QC
# remains a separate required check (scripts/test_pr_checks.sh --odk-only).
"${ROBOT}" extract --input "${OUT}/ontology.owl" --method BOT \
  --term-file "${REPO}/src/ontology/tests/computational-modelling-terms.txt" \
  --output-iri https://example.org/pmdco/computational-module \
  --output "${OUT}/module.owl"
"${ROBOT}" merge --input "${OUT}/module.owl" \
  --input "${REPO}/src/ontology/tests/computational-modelling.ttl" \
  --output "${OUT}/merged.owl"
# Check the complement and cardinality restrictions with HermiT.
"${ROBOT}" reason --input "${OUT}/merged.owl" --reasoner HermiT \
  --axiom-generators 'SubClass ClassAssertion' \
  --equivalent-classes-allowed asserted-only --output "${OUT}/reasoned.owl"
"${ROBOT}" verify --input "${OUT}/reasoned.owl" \
  --queries "${REPO}/src/sparql/computational-modelling-violation.sparql" \
  --output-dir "${OUT}"

# Competency answers are explicit named data, not anonymous existential fillers.
"${ROBOT}" query --input "${OUT}/merged.owl" \
  --query "${REPO}/src/sparql/computational-modelling-competency.sparql" \
  "${OUT}/competency-asserted.csv"
"${ROBOT}" verify --input "${OUT}/merged.owl" \
  --queries "${REPO}/src/sparql/computational-modelling-data-violation.sparql" \
  --output-dir "${OUT}"

# The data-violation query only finds missing answers. These answers must not appear:
# a time step is a setting, not a condition, and a setting belongs only to the plan that uses it.
EX="https://example.org/pmdco/computational-test"
unexpected=0
for answer in \
  "condition,${EX}/mdPlan,${EX}/timeStepDatum" \
  "condition,${EX}/mdPlan2,${EX}/timeStepDatum2" \
  "plan setting,${EX}/mdPlan,${EX}/timeStepDatum2" \
  "plan setting,${EX}/mdPlan2,${EX}/timeStepDatum"; do
  if tr -d '\r' < "${OUT}/competency-asserted.csv" | grep -Fqx -- "${answer}"; then
    echo "FAIL unexpected competency answer: ${answer}"
    unexpected=1
  fi
done
if [[ "${unexpected}" == 1 ]]; then
  exit 1
fi
echo "PASS no unexpected competency answers"
