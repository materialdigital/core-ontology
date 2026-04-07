#!/usr/bin/env python3
"""Check a pyshacl report for blocking sh:Violation results on PMDco terms.

Usage: python3 check_shacl_violations.py <shacl_report.ttl>
Exits 0 if no PMDco violations found, 1 otherwise.
"""
import sys
import rdflib

PMDCO_PREFIX = "https://w3id.org/pmd/co/"

QUERY = """
PREFIX sh: <http://www.w3.org/ns/shacl#>
SELECT ?focusNode ?resultMessage WHERE {
    ?vr a sh:ValidationResult ;
        sh:focusNode ?focusNode ;
        sh:resultMessage ?resultMessage ;
        sh:resultSeverity sh:Violation .
    FILTER(STRSTARTS(STR(?focusNode), "%s"))
}
""" % PMDCO_PREFIX


def main():
    if len(sys.argv) < 2:
        print("Usage: check_shacl_violations.py <shacl_report.ttl>", file=sys.stderr)
        sys.exit(2)

    g = rdflib.Graph()
    g.parse(sys.argv[1])

    rows = list(g.query(QUERY))
    if rows:
        print(f"FAIL: {len(rows)} blocking violation(s):")
        for r in rows:
            print(f"  {r.focusNode}  --  {r.resultMessage}")
        sys.exit(1)

    print("No blocking violations found.")


if __name__ == "__main__":
    main()
