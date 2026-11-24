#!/bin/bash
# In ODK: cd src/ontology && sh run.sh bash /work/scripts/test_computational_modelling.sh
# Or locally: ROBOT=/path/to/robot bash scripts/test_computational_modelling.sh
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
ROBOT="${ROBOT:-robot}"
OUT="$(mktemp -d "${TMPDIR:-/tmp}/pmdco-computational-test.XXXXXX")"
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
