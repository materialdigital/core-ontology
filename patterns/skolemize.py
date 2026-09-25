#!/usr/bin/env python3

import argparse
import uuid
from rdflib import Graph, BNode, URIRef


def skolemize_graph(graph, base_iri):
    """
    Replace blank nodes with skolem IRIs.
    Keeps a stable mapping during this conversion run.
    """

    bnode_map = {}

    def replace_node(node):
        if isinstance(node, BNode):
            if node not in bnode_map:
                bnode_map[node] = URIRef(
                    f"{base_iri}{uuid.uuid4()}"
                )
            return bnode_map[node]

        return node

    new_graph = Graph()

    # Copy namespace bindings
    for prefix, namespace in graph.namespaces():
        new_graph.bind(prefix, namespace)

    for s, p, o in graph:
        new_graph.add((
            replace_node(s),
            replace_node(p),
            replace_node(o)
        ))

    return new_graph


def main():
    parser = argparse.ArgumentParser(
        description="Skolemize RDF blank nodes using RDFLib"
    )

    parser.add_argument(
        "input",
        help="Input RDF file"
    )

    parser.add_argument(
        "output",
        help="Output RDF file"
    )

    parser.add_argument(
        "--input-format",
        default=None,
        help="RDFLib input format (e.g. turtle, nt, xml, json-ld)"
    )

    parser.add_argument(
        "--output-format",
        default="turtle",
        help="RDFLib output format (default: turtle)"
    )

    parser.add_argument(
        "--base-iri",
        default="http://example.org/skolemized/",
        help="Base IRI for generated skolem IRIs"
    )

    args = parser.parse_args()

    graph = Graph()

    graph.parse(
        args.input,
        format=args.input_format
    )

    skolemized = skolemize_graph(
        graph,
        args.base_iri
    )

    skolemized.serialize(
        destination=args.output,
        format=args.output_format
    )


if __name__ == "__main__":
    main()