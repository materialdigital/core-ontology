#!/usr/bin/env python3
"""Check axiom sensitivity using retained test_computational_modelling.sh artifacts.

Requires rdflib and ROBOT. Usage:
  KEEP_ARTIFACTS=1 ROBOT=/path/to/robot bash scripts/test_computational_modelling.sh
  ROBOT=/path/to/robot python3 scripts/test_computational_modelling_mutations.py ARTIFACT_DIR

Mutates only temporary copies of the locality module; production files are untouched.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from rdflib import Graph, Namespace, OWL, RDFS


def main():
    module = Path(sys.argv[1]) / 'module.owl'
    repo = Path(__file__).resolve().parents[1]
    robot = os.environ.get('ROBOT', 'robot')
    pmd = Namespace('https://w3id.org/pmd/co/')
    obo = Namespace('http://purl.obolibrary.org/obo/')
    original = Graph().parse(module)
    mutations = []
    for name, subject, prop in [
        ('execution', pmd.PMD_0000933, obo.STATO_0000102),
        ('model', pmd.PMD_0200011, pmd.PMD_0200013),
        ('method', pmd.PMD_0200011, obo.BFO_0000051),
        ('granularity', pmd.PMD_0200012, obo.OBI_0001927),
    ]:
        targets = [r for r in original.objects(subject, RDFS.subClassOf)
                   if (r, OWL.onProperty, prop) in original
                   and (r, OWL.someValuesFrom, None) in original]
        assert len(targets) == 1, (name, targets)
        mutations.append((name, (subject, RDFS.subClassOf, targets[0])))
    mutations.extend([
        ('domain', (pmd.PMD_0200013, RDFS.domain, obo.IAO_0000104)),
        ('range', (pmd.PMD_0200013, RDFS.range, pmd.PMD_0200009)),
        ('aboutness', (pmd.PMD_0200013, RDFS.subPropertyOf, obo.IAO_0000136)),
    ])
    with tempfile.TemporaryDirectory(prefix='pmdco-mutations-') as directory:
        out = Path(directory)
        for name, triple in mutations:
            assert triple in original, (name, triple)
            graph = Graph()
            graph += original
            graph.remove(triple)
            mutant = out / (name + '.ttl')
            graph.serialize(mutant, format='turtle')
            reasoned = out / (name + '-reasoned.owl')
            # Reasoning must succeed: a crash/inconsistency is not a killed mutant.
            subprocess.run([
                robot, 'merge', '--input', str(mutant), '--input',
                str(repo / 'src/ontology/tests/computational-modelling.ttl'),
                'reason', '--reasoner', 'HermiT', '--axiom-generators',
                'SubClass ClassAssertion', '--equivalent-classes-allowed',
                'asserted-only', '--output', str(reasoned),
            ], check=True)
            result = subprocess.run([
                robot, 'verify', '--input', str(reasoned), '--queries',
                str(repo / 'src/sparql/computational-modelling-violation.sparql'),
                '--output-dir', str(out),
            ], capture_output=True, text=True)
            if result.returncode == 0 or 'FAIL Rule' not in result.stdout + result.stderr:
                raise RuntimeError(f'{name}: expected query violation, got {result.stdout}{result.stderr}')
            print(f'{name}: removal detected by regression query', flush=True)


if __name__ == '__main__':
    main()
