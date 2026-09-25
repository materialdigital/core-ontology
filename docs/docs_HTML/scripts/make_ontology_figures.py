#!/usr/bin/env python3
"""
make_ontology_figures.py - Protege-style figures for ontology-structure.html
===========================================================================

Replaces the old Protege screenshots with crisp SVGs generated from the
ontology, so the figures stay sharp at any zoom and always match the ontology.

run_all.py calls generate() on every docs build (and so does the deploy
workflow on every push to main), using navigator.yaml's full_ontology_path -
the same source as the interactive class trees. It can also be run alone:

    python make_ontology_figures.py                  # full_ontology_path from navigator.yaml
    python make_ontology_figures.py path/or/url.ttl  # any other copy of pmdco-full.ttl

Writes into docs/ (run_all.py copies docs/*.svg next to the pages):
    hierarchy-<module>.svg         class hierarchy per module
    hierarchy-object-properties.svg
    annotations-<name>.svg         annotation panel of one entity

Hierarchy figures are described by {label: None | [child labels]}:
    None      -> show every child
    [labels]  -> show only these children, summarise the rest as "+N more"
Anything not listed is drawn collapsed. Class hierarchy = asserted rdfs:subClassOf
plus named operands of intersections (Protege's told superclasses); property
hierarchy = rdfs:subPropertyOf. Deprecated terms are left out. If a figure names
a term that no longer exists, that figure is skipped with a warning and the
previous SVG is kept, so an ontology change never breaks the docs build.
"""
import collections
import html
import sys
import textwrap
from pathlib import Path

from rdflib import Graph, Literal, OWL, RDF, RDFS, URIRef
from rdflib.collection import Collection

DOCS = Path(__file__).resolve().parents[2]
TOP_OBJECT_PROPERTY = "owl:topObjectProperty"

CLASS_FIGURES = {
    "materials": {
        "entity": ["continuant"],
        "continuant": ["independent continuant"],
        "independent continuant": ["material entity"],
        "material entity": None,
        "object aggregate": ["connected material entity aggregate", "disconnected material entity aggregate"],
        "connected material entity aggregate": None,
        "disconnected material entity aggregate": None,
        "portion of matter": None,
        "material": None,
        "engineered material": None,
    },
    "qualities": {
        "entity": ["continuant"],
        "continuant": ["specifically dependent continuant"],
        "specifically dependent continuant": None,
        "property": None,
        "characteristic material property": ["composition", "grain size", "hardness", "porosity",
                                             "strength", "toughness"],
        "composition": None,
        "facetted property": None,
        "quality": ["fundamental quality of system"],
        "fundamental quality of system": None,
    },
    "manufacturing": {
        "entity": ["occurrent"],
        "occurrent": ["process"],
        "process": ["planned process"],
        "planned process": ["completely executed planned process"],
        "completely executed planned process": ["manufacturing process"],
        "manufacturing process": None,
        "coating": None,
        "joining": None,
        "primary shaping": None,
    },
    "characterization": {
        "entity": ["occurrent"],
        "occurrent": ["process"],
        "process": ["planned process"],
        "planned process": ["completely executed planned process"],
        "completely executed planned process": ["assay"],
        "assay": None,
        "mechanical property analyzing process": None,
        "structural property analyzing process": None,
    },
    "datatransformation": {
        "entity": None,
        "continuant": ["generically dependent continuant"],
        "generically dependent continuant": ["information content entity"],
        "information content entity": None,
        "directive information entity": None,
        "plan specification": None,
        "simulation method specification": None,
        "occurrent": ["process", "process boundary"],
        "process": ["planned process"],
        "planned process": ["completely executed planned process"],
        "completely executed planned process": ["computing process"],
        "computing process": None,
        "simulation process": None,
        "process boundary": None,
    },
    "devices": {
        "entity": ["continuant"],
        "continuant": ["independent continuant"],
        "independent continuant": ["material entity"],
        "material entity": ["object"],
        "object": ["device"],
        "device": None,
    },
}

OBJECT_PROPERTY_FIGURE = {
    TOP_OBJECT_PROPERTY.lower(): None,
    "characteristic of": None,
    "has characteristic": None,
    "has participant": None,
    "part of": None,
    "has part": None,
}

# (output name, entity label, entity kind) - the page's annotation examples
ANNOTATION_PANELS = [("material", "material", "class"), ("has-quality", "has quality", "property")]

# Drawing constants (px)
ROW, INDENT, PAD, FONT = 24, 22, 16, 14
GOLD, BLUE, LINE, TEXT, MUTED = "#d4ac0d", "#2f79c3", "#c7ccd4", "#1f2937", "#6b7280"
GUIDE, EXPANDER = "#8b9099", "#7b8088"  # dotted tree lines and expander triangles
FONT_CSS = 'font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif'
QNAMES = {
    "http://www.w3.org/2004/02/skos/core#": "skos:",
    "http://www.w3.org/2000/01/rdf-schema#": "rdfs:",
    "http://purl.org/dc/terms/": "dcterms:",
    "http://purl.obolibrary.org/obo/": "obo:",
    "http://www.geneontology.org/formats/oboInOwl#": "oboInOwl:",
}


class Ontology:
    def __init__(self, source):
        self.g = g = Graph()
        g.parse(str(source), format="turtle")
        self.deprecated = {s for s, o in g.subject_objects(OWL.deprecated) if str(o).lower() == "true"}
        self.class_kids, self.defined = collections.defaultdict(set), set()
        for pred in (RDFS.subClassOf, OWL.equivalentClass):
            for s, o in g.subject_objects(pred):
                if not isinstance(s, URIRef) or s in self.deprecated:
                    continue
                if pred == OWL.equivalentClass:
                    self.defined.add(s)
                if isinstance(o, URIRef):
                    if pred == RDFS.subClassOf and o not in self.deprecated and o != s:
                        self.class_kids[o].add(s)
                    continue
                for lst in g.objects(o, OWL.intersectionOf):
                    for m in Collection(g, lst):
                        if isinstance(m, URIRef) and m != s and m not in self.deprecated:
                            self.class_kids[m].add(s)
        # object properties; the ones without a (live) superproperty hang under topObjectProperty
        self.prop_kids = collections.defaultdict(set)
        ops = {s for s in g.subjects(RDF.type, OWL.ObjectProperty) if isinstance(s, URIRef)} - self.deprecated
        for p in ops:
            sups = {o for o in g.objects(p, RDFS.subPropertyOf) if o in ops and o != p}  # 'has part' is its own subproperty
            for sup in sups or {TOP_OBJECT_PROPERTY}:
                self.prop_kids[sup].add(p)
        self.by_label = {}
        for s in {s for s in g.subjects(RDFS.label, None) if isinstance(s, URIRef)} - self.deprecated:
            self.by_label.setdefault(self.label(s).lower(), s)
        self.by_label[TOP_OBJECT_PROPERTY.lower()] = TOP_OBJECT_PROPERTY

    def label(self, u):
        if u == TOP_OBJECT_PROPERTY:
            return u
        vals = {o.language: str(o) for o in self.g.objects(u, RDFS.label) if isinstance(o, Literal)}
        return vals.get("en", vals.get(None, qname(u)))


def qname(u):
    u = str(u)
    for ns, pfx in QNAMES.items():
        if u.startswith(ns):
            return pfx + u[len(ns):]
    return u.rsplit("/", 1)[-1].rsplit("#", 1)[-1]


# ---------------------------------------------------------------- hierarchies

def layout(onto, spec, kids, root):
    """Flatten the expanded tree into rows: (depth, kind, uri_or_text, expanded, has_children)."""
    unknown = [n for n in spec if n not in onto.by_label]
    if unknown:
        raise ValueError(f"unknown or deprecated term(s): {unknown}")
    rows = []

    def walk(u, depth):
        name = onto.label(u).lower()
        expanded = name in spec
        rows.append((depth, "node", u, expanded, bool(kids[u])))
        if not expanded:
            return
        children = sorted(kids[u], key=lambda c: onto.label(c).lower())
        only = [n.lower() for n in spec[name]] if spec[name] is not None else None
        hidden = 0
        if only is not None:
            wanted = {onto.by_label[n] for n in only if n in onto.by_label}
            stray = [n for n in only if onto.by_label.get(n) not in children]
            if stray:
                raise ValueError(f"'{name}' has no child(ren) {stray}")
            hidden = len(children) - len(wanted)
            children = [c for c in children if c in wanted]
        for c in children:
            walk(c, depth + 1)
        if hidden:
            rows.append((depth + 1, "more", f"+{hidden} more", False, False))

    walk(onto.by_label[root], 0)
    return rows


def render_tree(onto, rows, title, icon):
    def x_of(depth):
        return PAD + 14 + depth * INDENT  # icon centre

    def text_of(row):
        return onto.label(row[2]) if row[1] == "node" else row[2]

    width = max(x_of(r[0]) + 12 + len(text_of(r)) * FONT * 0.58 for r in rows) + PAD
    height = PAD * 2 + len(rows) * ROW
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height}" '
           f'width="{width:.0f}" height="{height}" role="img" aria-labelledby="t">',
           f'  <title id="t">{html.escape(title)}</title>',
           f'  <style>text{{{FONT_CSS};font-size:{FONT}px;dominant-baseline:central;fill:{TEXT}}}'
           f'.pmd{{font-weight:700}}.more{{fill:{MUTED};font-style:italic}}</style>',
           f'  <rect width="{width:.0f}" height="{height}" rx="8" fill="#fff"/>']

    y = lambda i: PAD + i * ROW + ROW / 2
    dotted = f'stroke="{GUIDE}" stroke-width="1" stroke-dasharray="1 2"'
    # Protege/Swing tree lines: a dotted leg drops from under each expanded node's icon;
    # every child gets a dotted connector from that leg to its icon
    for i, (d, _, _, exp, _) in enumerate(rows):
        if not exp:
            continue
        last = i
        for j in range(i + 1, len(rows)):
            if rows[j][0] <= d:
                break
            if rows[j][0] == d + 1:
                last = j
                out.append(f'  <path d="M{x_of(d)} {y(j)}H{x_of(d + 1) - 9}" {dotted}/>')
        if last > i:
            out.append(f'  <path d="M{x_of(d)} {y(i) + 8}V{y(last)}" {dotted}/>')

    for i, (d, kind, u, exp, has_kids) in enumerate(rows):
        cx, cy = x_of(d), y(i)
        if kind == "more":
            out.append(f'  <text class="more" x="{cx - 6}" y="{cy}">{html.escape(u)}</text>')
            continue
        if has_kids:  # solid expander triangle sitting on the parent's leg (right = collapsed, down = expanded)
            tx = cx - INDENT
            pts = (f"{tx - 4.5},{cy - 2.5} {tx + 4.5},{cy - 2.5} {tx},{cy + 3.5}" if exp
                   else f"{tx - 2.5},{cy - 4.5} {tx + 3.5},{cy} {tx - 2.5},{cy + 4.5}")
            out.append(f'  <polygon points="{pts}" fill="{EXPANDER}"/>')
        if icon == "class":
            out.append(f'  <circle cx="{cx}" cy="{cy}" r="7" fill="{GOLD}"/>')
            if u in onto.defined:  # Protege marks defined (equivalent) classes with "="
                out.append(f'  <path d="M{cx - 3.5} {cy - 1.5}h7M{cx - 3.5} {cy + 1.5}h7" stroke="#fff" stroke-width="1.4"/>')
        else:  # object property: Protege's blue bar
            out.append(f'  <rect x="{cx - 8}" y="{cy - 4.5}" width="16" height="9" rx="1.5" fill="{BLUE}"/>')
        cls = ' class="pmd"' if "/pmd/co/" in str(u) else ""
        out.append(f'  <text{cls} x="{cx + 12}" y="{cy}">{html.escape(onto.label(u))}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------- annotation panels

ANNOTATION_ORDER = ["label", "definition", "skos:definition", "comment", "altLabel", "skos:altLabel"]


def render_annotations(onto, name, kind):
    """Protege-like 'Annotations: X' panel listing every annotation of the entity, in every language.

    Text values show their language/datatype; term values (e.g. has curation status) show the term's label.
    """
    u = onto.by_label.get(name.lower())
    if u is None:
        raise ValueError(f"unknown or deprecated term: '{name}'")
    items = []
    for p, o in onto.g.predicate_objects(u):
        if isinstance(o, Literal):
            meta = (f"[language: {o.language}]" if o.language
                    else f"[type: {qname(o.datatype).replace('XMLSchema#', 'xsd:')}]" if o.datatype else "")
            value = str(o).strip()
        elif isinstance(o, URIRef) and (p, RDF.type, OWL.AnnotationProperty) in onto.g:
            meta, value = "", onto.label(o)
        else:
            continue
        pname = onto.label(p) if (p, RDFS.label, None) in onto.g else qname(p)
        items.append((pname, meta, value))
    rank = lambda it: (ANNOTATION_ORDER.index(it[0]) if it[0] in ANNOTATION_ORDER else len(ANNOTATION_ORDER),
                       it[0].lower(), it[1] != "[language: en]", it[1], it[2])
    items.sort(key=rank)

    width, wrap = 720, 98
    head_h, top = 36, 36 + 12
    body = []
    y = top
    for pname, meta, value in items:
        lines = []
        for para in value.splitlines() or [""]:
            lines += textwrap.wrap(para, wrap) or [""]
        body.append((y, pname, meta, lines))
        y += 26 + len(lines) * 20 + 12
    height = y + 8
    colour = GOLD if kind == "class" else BLUE
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" '
           f'height="{height}" role="img" aria-labelledby="t">',
           f'  <title id="t">Annotations of {html.escape(name)}</title>',
           f'  <style>text{{{FONT_CSS};font-size:{FONT}px;fill:{TEXT}}}.k{{font-weight:700}}'
           f'.m{{fill:{MUTED};font-size:12.5px}}.h{{fill:#fff;font-size:16px;font-weight:600}}</style>',
           f'  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" fill="#fff" stroke="{LINE}"/>',
           f'  <path d="M0.5 {head_h}V8.5a8 8 0 0 1 8-8H{width - 8.5}a8 8 0 0 1 8 8V{head_h}z" fill="{colour}"/>',
           f'  <text class="h" x="{PAD}" y="{head_h / 2 + 6}">Annotations: {html.escape(name)}</text>']
    for i, (y0, pname, meta, lines) in enumerate(body):
        if i:
            out.append(f'  <path d="M{PAD} {y0 - 8}H{width - PAD}" stroke="#e5e7eb"/>')
        key_w = len(pname) * FONT * 0.56
        out.append(f'  <text class="k" x="{PAD + 8}" y="{y0 + 12}">{html.escape(pname)}</text>')
        if meta:
            out.append(f'  <text class="m" x="{PAD + 8 + key_w + 10:.0f}" y="{y0 + 12}">{html.escape(meta)}</text>')
        for k, line in enumerate(lines):
            out.append(f'  <text x="{PAD + 8}" y="{y0 + 34 + k * 20}">{html.escape(line)}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------- driver

def _write(name, make):
    """Write docs/<name>; on a stale spec keep the previous file and warn instead of failing."""
    try:
        svg = make()
    except ValueError as e:
        print(f"  Warning: figure {name} not regenerated ({e}); keeping the existing file")
        return
    (DOCS / name).write_text(svg, encoding="utf-8")
    print(f"  Generated figure: {name}")


def generate(source) -> None:
    onto = Ontology(source)
    for module, spec in CLASS_FIGURES.items():
        spec = {k.lower(): v for k, v in spec.items()}
        _write(f"hierarchy-{module}.svg", lambda s=spec, m=module: render_tree(
            onto, layout(onto, s, onto.class_kids, "entity"), f"PMDco {m} module: class hierarchy", "class"))
    _write("hierarchy-object-properties.svg", lambda: render_tree(
        onto, layout(onto, OBJECT_PROPERTY_FIGURE, onto.prop_kids, TOP_OBJECT_PROPERTY.lower()),
        "PMDco object property hierarchy", "property"))
    for out_name, label, kind in ANNOTATION_PANELS:
        _write(f"annotations-{out_name}.svg", lambda l=label, k=kind: render_annotations(onto, l, k))


def default_source():
    import yaml
    path = yaml.safe_load((DOCS / "navigator.yaml").read_text(encoding="utf-8")).get("full_ontology_path", "")
    # resolved exactly like build_all.py does (relative to docs/docs_HTML)
    if not path:
        return DOCS / "docs_HTML" / "patterns" / "pmdco_full.ttl"
    if path.startswith(("http://", "https://")):
        return path
    p = Path(path)
    return p if p.is_absolute() else DOCS / "docs_HTML" / p


if __name__ == "__main__":
    generate(sys.argv[1] if len(sys.argv) > 1 else default_source())
