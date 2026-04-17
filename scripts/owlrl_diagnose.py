#!/usr/bin/env python3
"""
OWL-RL reasoning diagnostic tool for PMDco.

Tries OWL-RL reasoning with a configurable timeout, then reports:
- Whether reasoning succeeded / timed out / errored
- Triple count growth (detects runaway expansion)
- Detected loop-prone axiom patterns (circular property chains, transitive+inverse combos)

Default input: pmdco-full.ttl (Turtle release artifact in repo root).
Use source OWL files via ODK container ROBOT conversion if needed.
"""

import sys
import time
import signal
import argparse
import textwrap
import subprocess
import tempfile
from pathlib import Path

import rdflib
from rdflib import OWL, RDF, RDFS, URIRef
from rdflib.namespace import Namespace

OBO = Namespace("http://purl.obolibrary.org/obo/")
PMDCO = Namespace("https://w3id.org/pmd/co/")


# ---------------------------------------------------------------------------
# Timeout helper
# ---------------------------------------------------------------------------

class TimeoutError(Exception):
    pass


def _timeout_handler(signum, frame):
    raise TimeoutError()


# ---------------------------------------------------------------------------
# Static analysis: detect loop-prone patterns
# ---------------------------------------------------------------------------

def detect_problematic_patterns(g: rdflib.ConjunctiveGraph) -> list[dict]:
    issues = []

    # 1. Collect transitive properties
    transitive = set(g.subjects(RDF.type, OWL.TransitiveProperty))

    # 2. Collect inverse pairs
    inverse_pairs: dict[URIRef, URIRef] = {}
    for s, _, o in g.triples((None, OWL.inverseOf, None)):
        inverse_pairs[s] = o
        inverse_pairs[o] = s

    # 3. Collect property chains
    chains = []
    for prop in g.subjects(OWL.propertyChainAxiom, None):
        chain_node = g.value(prop, OWL.propertyChainAxiom)
        if chain_node is None:
            continue
        chain_members = list(g.items(chain_node))
        chains.append((prop, chain_members))

    # 4. Check each chain for problematic patterns
    for prop, members in chains:
        prop_short = _short(prop)

        # Pattern A: prop appears in its own chain → direct cycle
        if prop in members:
            issues.append({
                "severity": "CRITICAL",
                "pattern": "Self-referential chain",
                "property": prop_short,
                "detail": f"Chain members include the property itself: {[_short(m) for m in members]}",
                "owl_rl_effect": "Forward chaining fires indefinitely on any instance",
            })
            continue

        # Pattern B: chain uses a transitive property + result is same or inverse
        chain_has_transitive = any(m in transitive for m in members)
        result_inverse = inverse_pairs.get(prop)
        chain_mentions_inverse = result_inverse is not None and result_inverse in members

        if chain_has_transitive and chain_mentions_inverse:
            issues.append({
                "severity": "CRITICAL",
                "pattern": "Transitive+Inverse feedback chain",
                "property": prop_short,
                "detail": (
                    f"Chain {[_short(m) for m in members]} contains transitive property "
                    f"and inverse of result property {_short(result_inverse)}"
                ),
                "owl_rl_effect": "Paired with inverse chain creates mutual rule amplification",
            })

        # Pattern C: chain ends/starts with transitive property whose inverse feeds back
        for m in members:
            inv_m = inverse_pairs.get(m)
            if inv_m is not None and inv_m in members:
                issues.append({
                    "severity": "HIGH",
                    "pattern": "Inverse pair both in chain",
                    "property": prop_short,
                    "detail": f"{_short(m)} and its inverse {_short(inv_m)} both appear in chain",
                    "owl_rl_effect": "May cause symmetric rule firing",
                })

    # 5. Symmetric + transitive on same property
    symmetric = set(g.subjects(RDF.type, OWL.SymmetricProperty))
    for p in transitive & symmetric:
        issues.append({
            "severity": "HIGH",
            "pattern": "Symmetric + Transitive on same property",
            "property": _short(p),
            "detail": "OWL-RL generates equivalence classes — can be expensive or non-terminating with rich ABox",
            "owl_rl_effect": "Rule scm-sco fires repeatedly as closure grows",
        })

    # 6. Detect cross-chain feedback: chain A uses result of chain B and vice versa
    chain_results = {prop: set(members) for prop, members in chains}
    prop_list = list(chain_results.keys())
    for i, pa in enumerate(prop_list):
        for pb in prop_list[i+1:]:
            if pa in chain_results[pb] and pb in chain_results[pa]:
                issues.append({
                    "severity": "CRITICAL",
                    "pattern": "Mutual chain dependency",
                    "property": f"{_short(pa)} ↔ {_short(pb)}",
                    "detail": "Each property's chain includes the other property",
                    "owl_rl_effect": "Creates mutual rule derivation loop",
                })

    return issues


def _short(uri) -> str:
    s = str(uri)
    for prefix, ns in [("BFO:", str(OBO)), ("pmdco:", str(PMDCO))]:
        if s.startswith(ns):
            return prefix + s[len(ns):]
    return s.split("/")[-1].split("#")[-1]


# ---------------------------------------------------------------------------
# DL expressivity loss analysis
# ---------------------------------------------------------------------------

# Axioms OWL-RL handles incompletely vs full DL (HermiT/ELK).
# Axioms are NOT removed — they stay in the graph.
# What is lost: specific inference directions OWL-RL's Datalog rules cannot derive.
DL_LOSS_EXPLANATIONS = {
    "allValuesFrom": (
        "OWL-RL only propagates allValuesFrom along known property assertions. "
        "Cannot infer closed-world filler constraints as DL does."
    ),
    "complementOf": (
        "Datalog has no negation. OWL-RL cannot derive class membership "
        "from complement expressions."
    ),
    "disjointWith": (
        "OWL-RL detects inconsistency from disjointness but cannot derive "
        "negative class membership or use disjointness for classification."
    ),
    "oneOf (nominals)": (
        "OWL-RL cannot reason about named individuals as class extensions "
        "in combination with other constructors."
    ),
    "hasValue": (
        "OWL-RL handles hasValue for instance checking but misses "
        "some inferences when combined with complex class hierarchies."
    ),
    "equivalentClass (complex)": (
        "OWL-RL handles only one direction: right-to-left subsumption. "
        "It cannot decompose a class into existential fillers (needs witness creation) "
        "or disjunctive members (Datalog has no disjunctive rule heads)."
    ),
    "unionOf": (
        "A ⊆ B⊔C: OWL-RL cannot derive 'x is B or x is C' from 'x is A'. "
        "Disjunction in rule conclusions is outside Datalog."
    ),
}


def detect_dl_loss(g: rdflib.ConjunctiveGraph) -> list[dict]:
    items = []

    def add(key, count, explanation):
        items.append({"label": key, "count": count, "explanation": explanation})

    add("allValuesFrom", len(list(g.subjects(OWL.allValuesFrom, None))),
        DL_LOSS_EXPLANATIONS["allValuesFrom"])

    add("complementOf", len(list(g.subjects(OWL.complementOf, None))),
        DL_LOSS_EXPLANATIONS["complementOf"])

    add("disjointWith", len(list(g.triples((None, OWL.disjointWith, None)))),
        DL_LOSS_EXPLANATIONS["disjointWith"])

    add("oneOf (nominals)", len(list(g.subjects(OWL.oneOf, None))),
        DL_LOSS_EXPLANATIONS["oneOf (nominals)"])

    add("hasValue", len(list(g.subjects(OWL.hasValue, None))),
        DL_LOSS_EXPLANATIONS["hasValue"])

    equiv_complex = sum(
        1 for _, _, o in g.triples((None, OWL.equivalentClass, None))
        if (o, RDF.type, OWL.Restriction) in g
        or (o, OWL.intersectionOf, None) in g
        or (o, OWL.unionOf, None) in g
    )
    add("equivalentClass (complex)", equiv_complex,
        DL_LOSS_EXPLANATIONS["equivalentClass (complex)"])

    add("unionOf", len(list(g.subjects(OWL.unionOf, None))),
        DL_LOSS_EXPLANATIONS["unionOf"])

    return items


# ---------------------------------------------------------------------------
# Reasoning attempt with growth monitoring
# ---------------------------------------------------------------------------

def attempt_reasoning(g: rdflib.ConjunctiveGraph, timeout_sec: int, sample_interval: float = 2.0):
    import owlrl

    result = {
        "status": None,
        "elapsed_sec": None,
        "triples_before": len(g),
        "triples_after": None,
        "growth_samples": [],
        "error": None,
    }

    # Use SIGALRM for timeout (Unix only)
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(timeout_sec)

    t0 = time.time()
    try:
        owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
        result["status"] = "SUCCESS"
    except TimeoutError:
        result["status"] = "TIMEOUT"
        result["error"] = f"Did not finish within {timeout_sec}s"
    except Exception as exc:
        result["status"] = "ERROR"
        result["error"] = str(exc)
    finally:
        signal.alarm(0)
        result["elapsed_sec"] = round(time.time() - t0, 2)
        result["triples_after"] = len(g)

    return result


# ---------------------------------------------------------------------------
# ROBOT benchmark (ELK + HermiT via docker ODK)
# ---------------------------------------------------------------------------

ALLOWED_REASONERS = {"ELK", "HermiT"}
ALLOWED_ODK_IMAGE_PREFIX = "obolibrary/odkfull"


def run_robot_reasoner(owl_file: Path, reasoner: str, odk_image: str, merge: bool = False) -> dict:
    if reasoner not in ALLOWED_REASONERS:
        raise ValueError(f"Reasoner must be one of {ALLOWED_REASONERS}")
    if not odk_image.startswith(ALLOWED_ODK_IMAGE_PREFIX):
        raise ValueError(f"ODK image must start with '{ALLOWED_ODK_IMAGE_PREFIX}'")
    with tempfile.NamedTemporaryFile(suffix=".owl", delete=False) as tmp:
        out = tmp.name
    # merge --input resolves imports before reasoning; required for fair timing from edit file
    robot_cmd = ["robot"]
    if merge:
        robot_cmd += ["merge", "--input", owl_file.name]
    else:
        robot_cmd += ["--input", owl_file.name]
    robot_cmd += ["reason", "--reasoner", reasoner, "--output", out]
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{owl_file.parent.resolve()}:/work",
        "-w", "/work",
        "-e", "ROBOT_JAVA_ARGS=-Xmx8G",
        odk_image,
    ] + robot_cmd
    t0 = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        elapsed = round(time.time() - t0, 2)
        label = f"{reasoner} (merge+reason)" if merge else f"{reasoner} (reason only)"
        return {
            "reasoner": label,
            "status": "SUCCESS" if result.returncode == 0 else "ERROR",
            "elapsed_sec": elapsed,
            "error": result.stderr.strip() if result.returncode != 0 else None,
        }
    except subprocess.TimeoutExpired:
        return {"reasoner": reasoner, "status": "TIMEOUT", "elapsed_sec": 600, "error": "timed out"}
    except FileNotFoundError:
        return {"reasoner": reasoner, "status": "ERROR", "elapsed_sec": 0, "error": "docker not found"}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="OWL-RL diagnostic: attempt reasoning + detect loop-prone patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python owlrl_diagnose.py src/ontology/pmdco-edit.owl
              python owlrl_diagnose.py src/ontology/pmdco-edit.owl --timeout 30 --skip-reasoning
              python owlrl_diagnose.py src/ontology/pmdco-edit.owl --format turtle
        """),
    )
    parser.add_argument("ontology", nargs="?", default="pmdco-full.ttl",
                        help="Path to Turtle release artifact (default: pmdco-full.ttl)")
    parser.add_argument("--timeout", type=int, default=60, help="Reasoning timeout in seconds (default: 60)")
    parser.add_argument("--skip-reasoning", action="store_true", help="Only run static analysis, skip OWL-RL attempt")
    parser.add_argument("--format", default="turtle", help="RDFLib parse format: turtle, xml, n3, nt (default: turtle)")
    parser.add_argument("--benchmark", metavar="OWL_FILE",
                        help="Also time ELK+HermiT via ROBOT docker on this OWL file (merge+reason for fair comparison)")
    parser.add_argument("--odk-image", default="obolibrary/odkfull:latest",
                        help="ODK docker image for benchmark (default: obolibrary/odkfull:latest)")
    args = parser.parse_args()

    path = Path(args.ontology)
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"OWL-RL Diagnostic: {path.name}")
    print(f"{'='*60}\n")

    # Load
    print(f"Loading ontology ({args.format})...")
    t0 = time.time()
    g = rdflib.ConjunctiveGraph()
    try:
        g.parse(str(path), format=args.format)
    except Exception as e:
        print(f"PARSE ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"  Loaded {len(g):,} triples in {time.time()-t0:.1f}s\n")

    # DL coverage loss analysis
    print("--- DL Coverage: Inferences OWL-RL Cannot Derive ---")
    print("  (Axioms stay in graph; only specific inference directions are lost)\n")
    dl_loss = detect_dl_loss(g)
    affected = [i for i in dl_loss if i["count"] > 0]
    if not affected:
        print("  No DL-only patterns detected — OWL-RL fully covers this ontology.\n")
    else:
        for item in dl_loss:
            if item["count"] > 0:
                print(f"  [{item['count']:>3}]  {item['label']}")
                # wrap explanation at 70 chars
                words = item["explanation"].split()
                line, lines = [], []
                for w in words:
                    if sum(len(x)+1 for x in line) + len(w) > 70:
                        lines.append(" ".join(line))
                        line = [w]
                    else:
                        line.append(w)
                if line:
                    lines.append(" ".join(line))
                for ln in lines:
                    print(f"         {ln}")
                print()
        print(f"  {len(affected)} of {len(dl_loss)} axiom types have incomplete OWL-RL coverage.\n")

    # Static analysis
    print("--- Static Analysis: Loop-Prone Patterns ---")
    issues = detect_problematic_patterns(g)
    if not issues:
        print("  No problematic patterns detected.\n")
    else:
        for i, iss in enumerate(issues, 1):
            print(f"\n  [{i}] {iss['severity']}: {iss['pattern']}")
            print(f"      Property : {iss['property']}")
            print(f"      Detail   : {iss['detail']}")
            print(f"      OWL-RL   : {iss['owl_rl_effect']}")
        print()

    # Reasoning
    res = None
    if args.skip_reasoning:
        print("(Skipping OWL-RL reasoning as requested)\n")
    else:
        print(f"--- OWL-RL Reasoning Attempt (timeout: {args.timeout}s) ---")
        print("  Running... (Ctrl-C to abort)")
        res = attempt_reasoning(g, args.timeout)

        status_icon = {"SUCCESS": "✓", "TIMEOUT": "✗ TIMEOUT", "ERROR": "✗ ERROR"}.get(res["status"], "?")
        print(f"\n  Status  : {status_icon}")
        print(f"  Elapsed : {res['elapsed_sec']}s")
        print(f"  Triples : {res['triples_before']:,} → {res['triples_after']:,}", end="")
        if res["triples_after"] and res["triples_before"]:
            growth = res["triples_after"] - res["triples_before"]
            print(f"  (+{growth:,} derived)" if growth >= 0 else f"  ({growth:,})", end="")
        print()
        if res["error"]:
            print(f"  Error   : {res['error']}")
        print()

    # Benchmark
    if args.benchmark:
        bpath = Path(args.benchmark)
        if not bpath.exists():
            print(f"  ERROR: benchmark file not found: {bpath}\n", file=sys.stderr)
        else:
            print("--- DL Reasoner Benchmark (via ROBOT docker) ---")
            print(f"  Input : {bpath.name} (merge + reason)\n")
            results = []
            for reasoner in ("ELK", "HermiT"):
                print(f"  Running {reasoner}...", flush=True)
                r = run_robot_reasoner(bpath, reasoner, args.odk_image, merge=True)
                results.append(r)
                icon = "✓" if r["status"] == "SUCCESS" else "✗"
                print(f"  {icon} {r['reasoner']}: {r['elapsed_sec']}s  [{r['status']}]")
                if r["error"]:
                    print(f"    {r['error']}")
            print()
            if not args.skip_reasoning and res is not None:
                print("  Comparison summary:")
                for r in results:
                    print(f"    {r['reasoner']}: {r['elapsed_sec']}s")
                if res["status"] == "SUCCESS":
                    print(f"    OWL-RL on {path.name}: {res['elapsed_sec']}s  (after HermiT pre-materialization)")
                print()

    # Summary
    critical = [i for i in issues if i["severity"] == "CRITICAL"]
    high = [i for i in issues if i["severity"] == "HIGH"]
    print("--- Summary ---")
    print(f"  Critical issues : {len(critical)}")
    print(f"  High issues     : {len(high)}")
    if critical:
        print("\n  Fix these first to enable OWL-RL reasoning:")
        for iss in critical:
            print(f"    • {iss['pattern']} on {iss['property']}")
    print()


if __name__ == "__main__":
    main()
