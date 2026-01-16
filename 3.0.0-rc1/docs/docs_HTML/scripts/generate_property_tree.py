#!/usr/bin/env python3
"""
Generate interactive property trees for PMDco ontology.
Parses pmdco.ttl using rdflib and generates HTML trees for:
- Object Properties
- Annotation Properties

Usage: python generate_property_tree.py
"""

import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    from rdflib import Graph, Namespace, URIRef, Literal
    from rdflib.namespace import RDF, RDFS, OWL, SKOS
except ImportError:
    print("Error: rdflib is required. Install with: pip install rdflib")
    exit(1)


# Define namespaces
OBO = Namespace("http://purl.obolibrary.org/obo/")
CO = Namespace("https://w3id.org/pmd/co/")
DC = Namespace("http://purl.org/dc/elements/1.1/")
DCTERMS = Namespace("http://purl.org/dc/terms/")


@dataclass
class OntologyProperty:
    """Represents an ontology property with its metadata."""
    uri: str
    label: str = ""
    label_de: str = ""
    definition: str = ""
    comment: str = ""
    property_type: str = "object"  # "object" or "annotation"
    children: List['OntologyProperty'] = field(default_factory=list)
    
    @property
    def prefix(self) -> str:
        """Extract prefix from URI."""
        if 'pmd/co/' in self.uri or 'PMD_' in self.uri:
            return 'pmd'
        elif 'obolibrary.org/obo/BFO_' in self.uri:
            return 'bfo'
        elif 'obolibrary.org/obo/RO_' in self.uri:
            return 'ro'
        elif 'obolibrary.org/obo/IAO_' in self.uri:
            return 'iao'
        elif 'obolibrary.org/obo/OBI_' in self.uri:
            return 'obi'
        elif 'obolibrary.org/obo/CHEBI_' in self.uri:
            return 'chebi'
        elif 'skos/core#' in self.uri:
            return 'skos'
        elif 'purl.org/dc/' in self.uri:
            return 'dc'
        return 'owl'
    
    @property
    def local_name(self) -> str:
        """Extract local name from URI."""
        if '#' in self.uri:
            return self.uri.split('#')[-1]
        return self.uri.split('/')[-1]
    
    @property
    def display_name(self) -> str:
        """Get the best display name for the property."""
        if self.label:
            return self.label
        # Format local name for readability
        name = self.local_name
        # Handle underscored names like portion_of_matter
        if '_' in name:
            # Check if it's an ID like PMD_0000001
            if re.match(r'^[A-Z]+_\d+$', name):
                return name  # Keep as-is for IDs
            return name.replace('_', ' ')
        # Handle camelCase
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return name.lower()


class PropertyParser:
    """Parser for ontology properties using rdflib."""
    
    def __init__(self, ttl_path: Path):
        self.ttl_path = ttl_path
        self.graph = Graph()
        self.object_properties: Dict[str, OntologyProperty] = {}
        self.annotation_properties: Dict[str, OntologyProperty] = {}
        self.subproperty_relations: List[Tuple[str, str]] = []  # (child, parent)
        
    def parse(self) -> None:
        """Parse the TTL file and extract properties."""
        print(f"Loading ontology from: {self.ttl_path}")
        self.graph.parse(str(self.ttl_path), format='turtle')
        print(f"  Loaded {len(self.graph)} triples")
        
        self._extract_object_properties()
        self._extract_annotation_properties()
        self._extract_subproperty_relations()
        self._extract_annotations()
        
        print(f"  Found {len(self.object_properties)} object properties")
        print(f"  Found {len(self.annotation_properties)} annotation properties")
        print(f"  Found {len(self.subproperty_relations)} subproperty relationships")
        
    def _extract_object_properties(self) -> None:
        """Extract all object property declarations."""
        for s, p, o in self.graph.triples((None, RDF.type, OWL.ObjectProperty)):
            uri = str(s)
            if uri not in self.object_properties:
                self.object_properties[uri] = OntologyProperty(uri=uri, property_type="object")
                
    def _extract_annotation_properties(self) -> None:
        """Extract all annotation property declarations."""
        for s, p, o in self.graph.triples((None, RDF.type, OWL.AnnotationProperty)):
            uri = str(s)
            if uri not in self.annotation_properties:
                self.annotation_properties[uri] = OntologyProperty(uri=uri, property_type="annotation")
                
    def _extract_subproperty_relations(self) -> None:
        """Extract all subPropertyOf relations."""
        for s, p, o in self.graph.triples((None, RDFS.subPropertyOf, None)):
            child_uri = str(s)
            parent_uri = str(o)
            self.subproperty_relations.append((child_uri, parent_uri))
    
    def _get_preferred_literal(self, literals, preferred_lang: str = 'en') -> str:
        """Get the preferred language literal or first available."""
        if not literals:
            return ""
        
        # Try to find preferred language
        for lit in literals:
            if isinstance(lit, Literal) and lit.language == preferred_lang:
                return str(lit)
        
        # Fall back to any literal without language tag
        for lit in literals:
            if isinstance(lit, Literal) and lit.language is None:
                return str(lit)
                
        # Fall back to first available
        return str(literals[0]) if literals else ""
    
    def _extract_annotations(self) -> None:
        """Extract labels and definitions for all properties."""
        all_properties = {**self.object_properties, **self.annotation_properties}
        
        for uri, prop in all_properties.items():
            uri_ref = URIRef(uri)
            
            # Get labels
            labels = list(self.graph.objects(uri_ref, RDFS.label))
            prop.label = self._get_preferred_literal(labels, 'en')
            
            # Get definition from skos:definition or IAO_0000115
            definitions = list(self.graph.objects(uri_ref, SKOS.definition))
            if not definitions:
                definitions = list(self.graph.objects(uri_ref, OBO.IAO_0000115))
            prop.definition = self._get_preferred_literal(definitions, 'en')
            
            # Get comment
            comments = list(self.graph.objects(uri_ref, RDFS.comment))
            prop.comment = self._get_preferred_literal(comments, 'en')


class PropertyTreeBuilder:
    """Builds hierarchical tree structure from parsed properties."""
    
    def __init__(self, parser: PropertyParser):
        self.parser = parser
        
    def build_tree(self, property_type: str = "object") -> List[OntologyProperty]:
        """Build the property hierarchy tree."""
        if property_type == "object":
            properties = self.parser.object_properties
        else:
            properties = self.parser.annotation_properties
            
        # Find parent-child relationships
        children_map: Dict[str, Set[str]] = {}
        has_parent: Set[str] = set()
        
        for child_uri, parent_uri in self.parser.subproperty_relations:
            if child_uri in properties and parent_uri in properties:
                if parent_uri not in children_map:
                    children_map[parent_uri] = set()
                children_map[parent_uri].add(child_uri)
                has_parent.add(child_uri)
        
        # Build tree structure
        def build_node(uri: str, visited: Set[str]) -> Optional[OntologyProperty]:
            if uri in visited or uri not in properties:
                return None
            visited.add(uri)
            
            prop = properties[uri]
            prop.children = []
            
            if uri in children_map:
                for child_uri in sorted(children_map[uri]):
                    child = build_node(child_uri, visited.copy())
                    if child:
                        prop.children.append(child)
                        
            # Sort children by display name
            prop.children.sort(key=lambda x: x.display_name.lower())
            return prop
        
        # Find root properties (those with no parent in our set)
        roots = []
        for uri in properties:
            if uri not in has_parent:
                node = build_node(uri, set())
                if node:
                    roots.append(node)
        
        # Sort roots by display name
        roots.sort(key=lambda x: x.display_name.lower())
        return roots
    
    def get_all_descendants(self, roots: List[OntologyProperty]) -> List[OntologyProperty]:
        """Get all properties including descendants."""
        result = []
        
        def collect(prop: OntologyProperty):
            result.append(prop)
            for child in prop.children:
                collect(child)
                
        for root in roots:
            collect(root)
        return result


class HTMLGenerator:
    """Generates HTML for property trees."""
    
    @staticmethod
    def escape_html(text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))
    
    def generate_tree_html(self, roots: List[OntologyProperty], 
                          title: str, tree_id: str) -> str:
        """Generate complete tree HTML with toolbar."""
        total_count = self._count_properties(roots)
        
        html_parts = [
            f'<div class="ontology-tree-container" id="{tree_id}">',
            '  <div class="tree-toolbar">',
            '    <button class="tree-toolbar-btn tree-expand-all" title="Expand all nodes">Expand All</button>',
            '    <button class="tree-toolbar-btn tree-collapse-all" title="Collapse all nodes">Collapse All</button>',
            f'    <input type="text" class="tree-search" placeholder="Search properties..." aria-label="Search {title} properties">',
            f'    <span class="tree-stats">{total_count} properties</span>',
            '  </div>',
            '  <ul class="ontology-tree">',
        ]
        
        for root in roots:
            html_parts.append(self._generate_node_html(root, expanded=True))
            
        html_parts.append('  </ul>')
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    def _count_properties(self, roots: List[OntologyProperty]) -> int:
        """Count total properties in tree."""
        count = 0
        
        def count_node(prop: OntologyProperty):
            nonlocal count
            count += 1
            for child in prop.children:
                count_node(child)
                
        for root in roots:
            count_node(root)
        return count
    
    def _generate_node_html(self, prop: OntologyProperty, 
                           expanded: bool = False, depth: int = 0) -> str:
        """Generate HTML for a single property node."""
        has_children = len(prop.children) > 0
        
        # Build node classes
        node_class = "tree-node"
        if prop.definition:
            node_class += " has-definition"
            
        # Build data attributes
        data_attrs = f'data-uri="{self.escape_html(prop.uri)}"'
        if prop.definition:
            data_attrs += f' data-definition="{self.escape_html(prop.definition)}"'
            
        # Build toggle button
        if has_children:
            toggle_class = "expanded" if expanded else "collapsed"
            toggle = f'<button class="tree-toggle {toggle_class}" aria-label="Toggle"></button>'
        else:
            toggle = '<span class="tree-toggle-placeholder"></span>'
            
        # Build label
        label = f'<span class="tree-prefix">{prop.prefix}:</span><span class="tree-label">{self.escape_html(prop.display_name)}</span>'
        
        # Build node
        html = f'<li><span class="{node_class}" {data_attrs}>{toggle}{label}</span>'
        
        # Add children
        if has_children:
            children_class = "" if expanded else "collapsed"
            html += f'<ul class="tree-children {children_class}">'
            for child in prop.children:
                html += self._generate_node_html(child, expanded=False, depth=depth+1)
            html += '</ul>'
            
        html += '</li>'
        return html


def generate_property_trees(parser: PropertyParser) -> Dict[str, Tuple[str, int]]:
    """Generate HTML trees for object and annotation properties."""
    builder = PropertyTreeBuilder(parser)
    generator = HTMLGenerator()
    
    result = {}
    
    # Object Properties
    print("  Building tree for object properties...")
    obj_roots = builder.build_tree("object")
    obj_html = generator.generate_tree_html(obj_roots, "Object Properties", "tree-object-properties")
    obj_count = generator._count_properties(obj_roots)
    result['object-properties'] = (obj_html, obj_count)
    print(f"    Generated tree with {obj_count} properties")
    
    # Annotation Properties  
    print("  Building tree for annotation properties...")
    ann_roots = builder.build_tree("annotation")
    ann_html = generator.generate_tree_html(ann_roots, "Annotation Properties", "tree-annotation-properties")
    ann_count = generator._count_properties(ann_roots)
    result['annotation-properties'] = (ann_html, ann_count)
    print(f"    Generated tree with {ann_count} properties")
    
    return result


def update_html_file(script_dir: Path, parser: PropertyParser) -> None:
    """Update ontology-structure.html with property trees."""
    html_file = script_dir / 'ontology-structure.html'
    
    if not html_file.exists():
        raise FileNotFoundError(f"HTML file not found: {html_file}")
        
    # Create backup
    backup_file = script_dir / f'ontology-structure.backup.properties.{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    shutil.copy(html_file, backup_file)
    print(f"Created backup: {backup_file.name}")
    
    # Read current content
    content = html_file.read_text(encoding='utf-8')
    
    # Generate property trees
    property_trees = generate_property_trees(parser)
    
    obj_html, obj_count = property_trees['object-properties']
    ann_html, ann_count = property_trees['annotation-properties']
    
    # 1. Replace Object Properties image with interactive tree
    # The image has asset ID: 0c384fca-4c65-44ad-9601-7511ed79156a
    obj_prop_pattern = r'<div class="figure-container">\s*<img[^>]*src="[^"]*0c384fca-4c65-44ad-9601-7511ed79156a[^"]*"[^>]*>\s*</div>'
    
    if re.search(obj_prop_pattern, content, flags=re.DOTALL):
        content = re.sub(obj_prop_pattern, obj_html.strip(), content, flags=re.DOTALL)
        print(f"  [OK] Replaced Object Properties image with interactive tree ({obj_count} properties)")
    elif 'id="tree-object-properties"' in content:
        # Tree already exists, replace it
        pattern = r'<div class="ontology-tree-container" id="tree-object-properties">[\s\S]*?</ul>\s*</div>'
        if re.search(pattern, content, flags=re.DOTALL):
            content = re.sub(pattern, obj_html.strip(), content, flags=re.DOTALL)
            print(f"  [OK] Replaced existing object properties tree ({obj_count} properties)")
        else:
            print("  Warning: Could not replace object properties tree")
    else:
        print("  Warning: Could not find Object Properties image placeholder")
    
    # 2. Add Annotation Properties tree
    if 'id="tree-annotation-properties"' in content:
        # Already exists, replace it
        pattern = r'<div class="ontology-tree-container" id="tree-annotation-properties">[\s\S]*?</ul>\s*</div>'
        if re.search(pattern, content, flags=re.DOTALL):
            content = re.sub(pattern, ann_html.strip(), content, flags=re.DOTALL)
            print(f"  [OK] Replaced existing annotation properties tree ({ann_count} properties)")
        else:
            print("  Warning: Could not replace annotation properties tree")
    else:
        # Insert after the annotation properties intro list (after "Definition Source" list item and closing </ul>)
        ann_insert_pattern = r'(<li><strong>Definition Source</strong>[^<]*<em>obo:IAO_0000119</em>[^<]*</li>\s*</ul>)'
        match = re.search(ann_insert_pattern, content, flags=re.DOTALL)
        if match:
            insert_pos = match.end()
            tree_section = f'''

        <p><strong>Full Annotation Properties Hierarchy:</strong></p>
        {ann_html}
'''
            content = content[:insert_pos] + tree_section + content[insert_pos:]
            print(f"  [OK] Added annotation properties tree ({ann_count} properties)")
        else:
            print("  Warning: Could not find insertion point for annotation properties tree")
    
    # Write updated content
    html_file.write_text(content, encoding='utf-8')
    print(f"Updated: {html_file}")


def main():
    """Main entry point."""
    print("=" * 70)
    print("PMDco Property Tree Generator")
    print("=" * 70)
    print()
    
    # Get script directory
    script_dir = Path(__file__).parent.resolve()
    print(f"Script directory: {script_dir}")
    
    # Find TTL file
    ttl_file = script_dir / 'components' / 'pmdco.ttl'
    if not ttl_file.exists():
        print(f"Error: TTL file not found: {ttl_file}")
        return
    print(f"TTL file: {ttl_file}")
    print()
    
    # Parse ontology
    print("-" * 40)
    print("Parsing ontology...")
    print("-" * 40)
    
    parser = PropertyParser(ttl_file)
    parser.parse()
    
    print()
    print(f"[OK] Object properties: {len(parser.object_properties)}")
    print(f"[OK] Annotation properties: {len(parser.annotation_properties)}")
    print()
    
    # Update HTML file
    print("-" * 40)
    print("Updating HTML file...")
    print("-" * 40)
    
    update_html_file(script_dir, parser)
    
    print()
    print("=" * 70)
    print(f"[OK] Done! Object: {len(parser.object_properties)}, Annotation: {len(parser.annotation_properties)}")
    print("  Open ontology-structure.html in a browser to view the trees.")
    print("=" * 70)


if __name__ == "__main__":
    main()
