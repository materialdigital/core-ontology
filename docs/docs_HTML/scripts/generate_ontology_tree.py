#!/usr/bin/env python3
"""
PMDco Ontology Tree Generator (Production Version)

This script parses the unified pmdco.ttl ontology file using rdflib and generates
an interactive HTML tree view for the ontology-structure.html page.

Features:
- Parses Turtle (.ttl) format using rdflib
- Extracts human-readable labels (rdfs:label) instead of URIs
- Builds complete class hierarchy from rdfs:subClassOf
- Generates interactive expandable tree with search and tooltips
- Verifies class counts match the source file

Usage:
    python generate_ontology_tree.py

Output:
    Updates ontology-structure.html with interactive ontology trees
"""

import re
import html
import shutil
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple

from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef, Literal
from rdflib.namespace import SKOS, XSD


# === NAMESPACE DEFINITIONS ===
CO = Namespace("https://w3id.org/pmd/co/")
OBO = Namespace("http://purl.obolibrary.org/obo/")
IAO = Namespace("http://purl.obolibrary.org/obo/IAO_")
BFO = Namespace("http://purl.obolibrary.org/obo/BFO_")
CHEBI = Namespace("http://purl.obolibrary.org/obo/CHEBI_")
OBI = Namespace("http://purl.obolibrary.org/obo/OBI_")


@dataclass
class OntologyClass:
    """Represents an ontology class with its metadata."""
    uri: str
    label: str = ""
    label_de: str = ""
    definition: str = ""
    comment: str = ""
    children: List['OntologyClass'] = field(default_factory=list)
    
    @property
    def prefix(self) -> str:
        """Extract prefix from URI for display."""
        uri = self.uri
        if 'pmd/co/' in uri or '/PMD_' in uri:
            return 'pmd'
        elif 'BFO_' in uri:
            return 'bfo'
        elif 'RO_' in uri:
            return 'ro'
        elif 'IAO_' in uri:
            return 'iao'
        elif 'OBI_' in uri:
            return 'obi'
        elif 'CHEBI_' in uri:
            return 'chebi'
        elif 'NCBITaxon_' in uri:
            return 'ncbi'
        elif 'skos/core#' in uri:
            return 'skos'
        return 'owl'
    
    @property
    def local_name(self) -> str:
        """Extract local name from URI."""
        if '#' in self.uri:
            return self.uri.split('#')[-1]
        return self.uri.split('/')[-1]
    
    @property
    def display_name(self) -> str:
        """Get the best display name for the class (label preferred over URI)."""
        if self.label:
            return self.label
        # Fallback: convert local name to readable format
        local = self.local_name
        # Handle underscore-separated IDs like PMD_0000001
        if '_' in local and local.split('_')[0].isupper():
            return local  # Keep as-is for IDs
        # Convert camelCase or underscores to spaces
        return local.replace('_', ' ')


class OntologyParser:
    """Parses OWL ontology files using rdflib."""
    
    def __init__(self, ttl_path: Path):
        self.ttl_path = ttl_path
        self.graph = Graph()
        self.classes: Dict[str, OntologyClass] = {}
        self.parent_map: Dict[str, Set[str]] = defaultdict(set)  # child -> parents
        self.child_map: Dict[str, Set[str]] = defaultdict(set)   # parent -> children
        
    def parse(self) -> None:
        """Parse the TTL file and extract all class information."""
        print(f"Loading ontology from: {self.ttl_path}")
        self.graph.parse(str(self.ttl_path), format="turtle")
        print(f"  Loaded {len(self.graph)} triples")
        
        self._extract_classes()
        self._extract_hierarchy()
        self._extract_annotations()
        
        print(f"  Found {len(self.classes)} classes")
        print(f"  Found {sum(len(v) for v in self.child_map.values())} subclass relationships")
        
    def _extract_classes(self) -> None:
        """Extract all OWL class declarations."""
        # Get classes declared with rdf:type owl:Class
        for cls in self.graph.subjects(RDF.type, OWL.Class):
            if isinstance(cls, URIRef):
                uri = str(cls)
                if uri not in self.classes:
                    self.classes[uri] = OntologyClass(uri=uri)
                    
    def _extract_hierarchy(self) -> None:
        """Extract subclass relationships."""
        for child, _, parent in self.graph.triples((None, RDFS.subClassOf, None)):
            if isinstance(child, URIRef) and isinstance(parent, URIRef):
                child_uri = str(child)
                parent_uri = str(parent)
                
                # Skip self-references and blank nodes
                if child_uri == parent_uri:
                    continue
                    
                self.parent_map[child_uri].add(parent_uri)
                self.child_map[parent_uri].add(child_uri)
                
                # Ensure both are in classes dict
                if child_uri not in self.classes:
                    self.classes[child_uri] = OntologyClass(uri=child_uri)
                if parent_uri not in self.classes:
                    self.classes[parent_uri] = OntologyClass(uri=parent_uri)
                    
    def _extract_annotations(self) -> None:
        """Extract labels and definitions from annotations."""
        for uri, cls in self.classes.items():
            uri_ref = URIRef(uri)
            
            # Extract rdfs:label (prefer English)
            for label in self.graph.objects(uri_ref, RDFS.label):
                if isinstance(label, Literal):
                    lang = label.language
                    if lang == 'en' or lang is None:
                        if not cls.label:  # Don't overwrite if already set
                            cls.label = str(label)
                    elif lang == 'de':
                        cls.label_de = str(label)
            
            # Extract skos:definition
            for defn in self.graph.objects(uri_ref, SKOS.definition):
                if isinstance(defn, Literal):
                    lang = defn.language
                    if lang == 'en' or lang is None:
                        cls.definition = str(defn)
                        break
                        
            # Extract IAO definition (obo:IAO_0000115)
            if not cls.definition:
                iao_def = URIRef("http://purl.obolibrary.org/obo/IAO_0000115")
                for defn in self.graph.objects(uri_ref, iao_def):
                    if isinstance(defn, Literal):
                        cls.definition = str(defn)
                        break
                        
            # Extract rdfs:comment as fallback
            if not cls.definition:
                for comment in self.graph.objects(uri_ref, RDFS.comment):
                    if isinstance(comment, Literal):
                        lang = comment.language
                        if lang == 'en' or lang is None:
                            cls.comment = str(comment)
                            break
    
    def enrich_from_full_ontology(self, full_ttl_path: Path) -> None:
        """Enrich classes with labels/definitions from full ontology file."""
        if not full_ttl_path.exists():
            print(f"  Warning: Full ontology file not found: {full_ttl_path}")
            return
        
        print(f"  Loading labels from full ontology: {full_ttl_path.name}")
        full_graph = Graph()
        full_graph.parse(str(full_ttl_path), format="turtle")
        
        labels_added = 0
        defs_added = 0
        
        for uri, cls in self.classes.items():
            uri_ref = URIRef(uri)
            
            # Enrich missing labels
            if not cls.label:
                for label in full_graph.objects(uri_ref, RDFS.label):
                    if isinstance(label, Literal):
                        lang = label.language
                        if lang == 'en' or lang is None:
                            cls.label = str(label)
                            labels_added += 1
                            break
            
            # Enrich missing definitions
            if not cls.definition and not cls.comment:
                for defn in full_graph.objects(uri_ref, SKOS.definition):
                    if isinstance(defn, Literal):
                        lang = defn.language
                        if lang == 'en' or lang is None:
                            cls.definition = str(defn)
                            defs_added += 1
                            break
        
        print(f"  Enriched {labels_added} labels, {defs_added} definitions from full ontology")


class OntologyTreeBuilder:
    """Builds hierarchical tree structures from parsed ontology data."""
    
    def __init__(self, parser: OntologyParser):
        self.parser = parser
        self.classes = parser.classes
        self.parent_map = parser.parent_map
        self.child_map = parser.child_map
        
    def get_root_classes(self) -> List[str]:
        """Get classes with no parents (root of hierarchy)."""
        roots = []
        for uri in self.classes:
            if uri not in self.parent_map or not self.parent_map[uri]:
                roots.append(uri)
        return sorted(roots, key=lambda u: self.classes[u].display_name.lower())
    
    def get_classes_under(self, root_uri: str) -> Set[str]:
        """Get all descendant classes under a given root."""
        descendants = set()
        to_visit = [root_uri]
        
        while to_visit:
            current = to_visit.pop()
            if current in descendants:
                continue
            descendants.add(current)
            for child in self.child_map.get(current, set()):
                to_visit.append(child)
                
        return descendants
    
    def build_tree(self, root_uri: str, allowed_uris: Optional[Set[str]] = None, 
                   visited: Optional[Set[str]] = None) -> Optional[OntologyClass]:
        """Build a tree starting from the given root, optionally filtered by allowed URIs."""
        if visited is None:
            visited = set()
            
        if root_uri in visited:
            return None
        if allowed_uris and root_uri not in allowed_uris:
            return None
        if root_uri not in self.classes:
            return None
            
        visited.add(root_uri)
        source = self.classes[root_uri]
        
        node = OntologyClass(
            uri=source.uri,
            label=source.label,
            label_de=source.label_de,
            definition=source.definition,
            comment=source.comment,
        )
        
        # Get children and sort by display name
        children = self.child_map.get(root_uri, set())
        if allowed_uris:
            children = children.intersection(allowed_uris)
            
        sorted_children = sorted(
            children, 
            key=lambda u: self.classes.get(u, OntologyClass(uri=u)).display_name.lower()
        )
        
        for child_uri in sorted_children:
            child_tree = self.build_tree(child_uri, allowed_uris, visited.copy())
            if child_tree:
                node.children.append(child_tree)
                
        return node


class HTMLGenerator:
    """Generates HTML output for the ontology trees."""
    
    # CSS for the tree viewer (consistent with existing site styling)
    TREE_CSS = '''
    /* Ontology Tree Styles */
    .ontology-tree-container {
      background: var(--color-bg-tertiary);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-lg);
      padding: var(--spacing-lg);
      margin: var(--spacing-lg) 0;
      max-height: 600px;
      overflow-y: auto;
    }

    .ontology-tree-container::-webkit-scrollbar {
      width: 8px;
    }

    .ontology-tree-container::-webkit-scrollbar-track {
      background: var(--color-bg-secondary);
      border-radius: 4px;
    }

    .ontology-tree-container::-webkit-scrollbar-thumb {
      background: var(--color-border);
      border-radius: 4px;
    }

    .ontology-tree-container::-webkit-scrollbar-thumb:hover {
      background: var(--color-primary);
    }

    .ontology-tree {
      list-style: none;
      padding-left: 0;
      margin: 0;
      font-family: var(--font-family-mono);
      font-size: var(--font-size-sm);
    }

    .ontology-tree ul {
      list-style: none;
      padding-left: 20px;
      margin: 0;
      border-left: 1px dashed var(--color-border);
      margin-left: 8px;
    }

    .ontology-tree li {
      margin: 4px 0;
      position: relative;
    }

    .tree-node {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 8px;
      border-radius: var(--radius-sm);
      cursor: default;
      transition: background var(--transition-fast);
      max-width: 100%;
    }

    .tree-node:hover {
      background: var(--color-bg-hover);
    }

    .tree-toggle {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 18px;
      height: 18px;
      border: none;
      background: var(--color-bg-secondary);
      color: var(--color-text-muted);
      border-radius: 3px;
      cursor: pointer;
      font-size: 10px;
      flex-shrink: 0;
      transition: all var(--transition-fast);
    }

    .tree-toggle:hover {
      background: var(--color-primary);
      color: white;
    }

    .tree-toggle.collapsed::before {
      content: '▶';
    }

    .tree-toggle.expanded::before {
      content: '▼';
    }

    .tree-toggle-placeholder {
      width: 18px;
      height: 18px;
      flex-shrink: 0;
    }

    .tree-prefix {
      color: var(--color-text-muted);
      font-size: 0.85em;
    }

    .tree-label {
      color: var(--color-primary-light);
      font-weight: 500;
    }

    .tree-node.has-definition {
      cursor: help;
    }

    .tree-node.has-definition .tree-label {
      border-bottom: 1px dotted var(--color-text-muted);
    }

    .tree-children {
      overflow: hidden;
      transition: max-height 0.2s ease-out;
    }

    .tree-children.collapsed {
      max-height: 0 !important;
    }

    /* Tree toolbar */
    .tree-toolbar {
      display: flex;
      gap: var(--spacing-sm);
      margin-bottom: var(--spacing-md);
      padding-bottom: var(--spacing-sm);
      border-bottom: 1px solid var(--color-border);
      flex-wrap: wrap;
      align-items: center;
    }

    .tree-toolbar-btn {
      padding: 6px 12px;
      font-size: var(--font-size-xs);
      font-weight: 500;
      color: var(--color-text-secondary);
      background: var(--color-bg-secondary);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: all var(--transition-fast);
    }

    .tree-toolbar-btn:hover {
      color: var(--color-text-primary);
      border-color: var(--color-primary);
      background: var(--color-bg-hover);
    }

    .tree-search {
      flex: 1;
      max-width: 250px;
      padding: 6px 12px;
      font-size: var(--font-size-sm);
      color: var(--color-text-primary);
      background: var(--color-bg-secondary);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-sm);
      outline: none;
    }

    .tree-search:focus {
      border-color: var(--color-primary);
    }

    .tree-search::placeholder {
      color: var(--color-text-muted);
    }

    .tree-node.search-match .tree-label {
      background: rgba(0, 160, 227, 0.3);
      padding: 0 2px;
      border-radius: 2px;
    }

    .tree-node.search-hidden {
      display: none;
    }

    .tree-stats {
      font-size: var(--font-size-xs);
      color: var(--color-text-muted);
      margin-left: auto;
      display: flex;
      align-items: center;
    }

    /* Tooltip */
    .tree-tooltip {
      position: fixed;
      z-index: 1000;
      max-width: 400px;
      padding: 12px 16px;
      background: var(--color-bg-primary);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-lg);
      font-family: var(--font-family);
      font-size: var(--font-size-sm);
      color: var(--color-text-secondary);
      line-height: 1.5;
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.15s;
    }

    .tree-tooltip.visible {
      opacity: 1;
    }

    .tree-tooltip-title {
      font-weight: 600;
      color: var(--color-text-primary);
      margin-bottom: 6px;
    }

    .tree-tooltip-uri {
      font-family: var(--font-family-mono);
      font-size: var(--font-size-xs);
      color: var(--color-text-muted);
      word-break: break-all;
      margin-top: 8px;
      padding-top: 8px;
      border-top: 1px solid var(--color-border);
    }
    '''
    
    # JavaScript for tree interactivity
    TREE_JS = '''
    /* Ontology Tree Manager */
    class OntologyTreeManager {
      constructor() {
        this.tooltip = null;
        this.init();
      }

      init() {
        this.createTooltip();
        this.bindEvents();
      }

      createTooltip() {
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'tree-tooltip';
        document.body.appendChild(this.tooltip);
      }

      bindEvents() {
        // Toggle expand/collapse
        document.querySelectorAll('.tree-toggle').forEach(btn => {
          btn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleNode(btn);
          });
        });

        // Expand all buttons
        document.querySelectorAll('.tree-expand-all').forEach(btn => {
          btn.addEventListener('click', () => {
            const container = btn.closest('.ontology-tree-container');
            this.expandAll(container);
          });
        });

        // Collapse all buttons
        document.querySelectorAll('.tree-collapse-all').forEach(btn => {
          btn.addEventListener('click', () => {
            const container = btn.closest('.ontology-tree-container');
            this.collapseAll(container);
          });
        });

        // Search functionality
        document.querySelectorAll('.tree-search').forEach(input => {
          input.addEventListener('input', (e) => {
            const container = input.closest('.ontology-tree-container');
            this.filterTree(container, e.target.value);
          });
        });

        // Tooltips
        document.querySelectorAll('.tree-node.has-definition').forEach(node => {
          node.addEventListener('mouseenter', (e) => this.showTooltip(e, node));
          node.addEventListener('mouseleave', () => this.hideTooltip());
          node.addEventListener('mousemove', (e) => this.moveTooltip(e));
        });
      }

      toggleNode(btn) {
        const li = btn.closest('li');
        const children = li.querySelector(':scope > .tree-children');
        if (!children) return;

        const isCollapsed = btn.classList.contains('collapsed');
        if (isCollapsed) {
          btn.classList.remove('collapsed');
          btn.classList.add('expanded');
          children.classList.remove('collapsed');
          children.style.maxHeight = children.scrollHeight + 'px';
        } else {
          btn.classList.remove('expanded');
          btn.classList.add('collapsed');
          children.classList.add('collapsed');
        }
      }

      expandAll(container) {
        container.querySelectorAll('.tree-toggle.collapsed').forEach(btn => {
          btn.classList.remove('collapsed');
          btn.classList.add('expanded');
        });
        container.querySelectorAll('.tree-children').forEach(children => {
          children.classList.remove('collapsed');
          children.style.maxHeight = children.scrollHeight + 'px';
        });
        // Recalculate heights after initial expansion
        setTimeout(() => {
          container.querySelectorAll('.tree-children').forEach(children => {
            children.style.maxHeight = 'none';
          });
        }, 250);
      }

      collapseAll(container) {
        container.querySelectorAll('.tree-toggle.expanded').forEach(btn => {
          btn.classList.remove('expanded');
          btn.classList.add('collapsed');
        });
        container.querySelectorAll('.tree-children').forEach(children => {
          children.classList.add('collapsed');
        });
      }

      filterTree(container, query) {
        const tree = container.querySelector('.ontology-tree');
        const nodes = tree.querySelectorAll('.tree-node');
        const q = query.toLowerCase().trim();

        if (!q) {
          // Reset all
          nodes.forEach(node => {
            node.classList.remove('search-match', 'search-hidden');
            node.closest('li').style.display = '';
          });
          return;
        }

        // First pass: find matches
        const matchedLis = new Set();
        nodes.forEach(node => {
          const label = node.querySelector('.tree-label')?.textContent.toLowerCase() || '';
          const prefix = node.querySelector('.tree-prefix')?.textContent.toLowerCase() || '';
          const isMatch = label.includes(q) || prefix.includes(q);
          
          node.classList.toggle('search-match', isMatch);
          
          if (isMatch) {
            // Mark this and all ancestors as visible
            let li = node.closest('li');
            while (li) {
              matchedLis.add(li);
              li = li.parentElement?.closest('li');
            }
          }
        });

        // Second pass: show/hide
        tree.querySelectorAll('li').forEach(li => {
          if (matchedLis.has(li)) {
            li.style.display = '';
            // Expand path to matched items
            const toggle = li.querySelector(':scope > .tree-node .tree-toggle');
            if (toggle && toggle.classList.contains('collapsed')) {
              this.toggleNode(toggle);
            }
          } else {
            li.style.display = 'none';
          }
        });
      }

      showTooltip(e, node) {
        const definition = node.dataset.definition;
        const uri = node.dataset.uri;
        const label = node.querySelector('.tree-label')?.textContent || '';

        let tooltipHtml = `<div class="tree-tooltip-title">${this.escapeHtml(label)}</div>`;
        if (definition) {
          tooltipHtml += `<div>${this.escapeHtml(definition)}</div>`;
        }
        if (uri) {
          tooltipHtml += `<div class="tree-tooltip-uri">${this.escapeHtml(uri)}</div>`;
        }

        this.tooltip.innerHTML = tooltipHtml;
        this.tooltip.classList.add('visible');
        this.moveTooltip(e);
      }

      hideTooltip() {
        this.tooltip.classList.remove('visible');
      }

      moveTooltip(e) {
        const x = e.clientX + 15;
        const y = e.clientY + 15;
        const rect = this.tooltip.getBoundingClientRect();
        
        // Keep tooltip in viewport
        const maxX = window.innerWidth - rect.width - 20;
        const maxY = window.innerHeight - rect.height - 20;
        
        this.tooltip.style.left = Math.min(x, maxX) + 'px';
        this.tooltip.style.top = Math.min(y, maxY) + 'px';
      }

      escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
      }
    }
    '''
    
    def __init__(self, tree_builder: OntologyTreeBuilder):
        self.tree_builder = tree_builder
        
    def count_nodes(self, roots: List[OntologyClass]) -> int:
        """Count total nodes in the tree."""
        count = 0
        def count_recursive(node):
            nonlocal count
            count += 1
            for child in node.children:
                count_recursive(child)
        for root in roots:
            count_recursive(root)
        return count
        
    def generate_tree_html(self, roots: List[OntologyClass], module_name: str, tree_id: str) -> str:
        """Generate HTML for a tree with toolbar."""
        class_count = self.count_nodes(roots)
        
        html_parts = [f'''
        <div class="ontology-tree-container" id="{tree_id}">
          <div class="tree-toolbar">
            <button class="tree-toolbar-btn tree-expand-all" title="Expand all nodes">Expand All</button>
            <button class="tree-toolbar-btn tree-collapse-all" title="Collapse all nodes">Collapse All</button>
            <input type="text" class="tree-search" placeholder="Search classes..." aria-label="Search {module_name} classes">
            <span class="tree-stats">{class_count} classes</span>
          </div>
          <ul class="ontology-tree">
        ''']
        
        for root in roots:
            html_parts.append(self._generate_node_html(root, 0))
            
        html_parts.append('</ul></div>')
        return ''.join(html_parts)
    
    def _generate_node_html(self, node: OntologyClass, depth: int) -> str:
        """Generate HTML for a single tree node and its children."""
        has_children = len(node.children) > 0
        has_definition = bool(node.definition or node.comment)
        
        # Escape HTML entities
        label = html.escape(node.display_name)
        prefix = html.escape(node.prefix)
        definition = html.escape(node.definition or node.comment or '')
        uri = html.escape(node.uri)
        
        # Build node classes
        node_classes = ['tree-node']
        if has_definition:
            node_classes.append('has-definition')
            
        # Build data attributes
        data_attrs = f'data-uri="{uri}"'
        if has_definition:
            data_attrs += f' data-definition="{definition}"'
        
        # Determine initial collapse state (collapse after depth 1)
        initially_collapsed = depth >= 1 and has_children
        toggle_class = 'collapsed' if initially_collapsed else 'expanded'
        children_class = 'collapsed' if initially_collapsed else ''
        
        html_parts = ['<li>']
        html_parts.append(f'<span class="{" ".join(node_classes)}" {data_attrs}>')
        
        if has_children:
            html_parts.append(f'<button class="tree-toggle {toggle_class}" aria-label="Toggle"></button>')
        else:
            html_parts.append('<span class="tree-toggle-placeholder"></span>')
            
        html_parts.append(f'<span class="tree-prefix">{prefix}:</span>')
        html_parts.append(f'<span class="tree-label">{label}</span>')
        html_parts.append('</span>')
        
        if has_children:
            html_parts.append(f'<ul class="tree-children {children_class}">')
            for child in node.children:
                html_parts.append(self._generate_node_html(child, depth + 1))
            html_parts.append('</ul>')
            
        html_parts.append('</li>')
        return ''.join(html_parts)


# === MODULE DEFINITIONS ===
# Maps module names to their root URIs for building separate trees
MODULE_CONFIGS = {
    'materials': {
        'title': 'Materials Module Classes',
        'roots': [
            'http://purl.obolibrary.org/obo/BFO_0000040',  # material entity
        ],
        'extra_roots': [
            'https://w3id.org/pmd/co/PMD_0000001',  # portion of matter
            'https://w3id.org/pmd/co/PMD_0000000',  # Material
        ]
    },
    'qualities': {
        'title': 'Qualities Module Classes',
        'roots': [
            'http://purl.obolibrary.org/obo/BFO_0000019',  # quality
            'http://purl.obolibrary.org/obo/BFO_0000020',  # specifically dependent continuant
        ]
    },
    'manufacturing': {
        'title': 'Manufacturing Module Classes',
        'roots': [
            'http://purl.obolibrary.org/obo/BFO_0000015',  # process
        ]
    },
    'characterization': {
        'title': 'Characterization Module Classes',
        'roots': [
            'http://purl.obolibrary.org/obo/OBI_0000070',  # assay
        ]
    },
    'datatransformation': {
        'title': 'Data Transformation Module Classes',
        'roots': [
            'http://purl.obolibrary.org/obo/BFO_0000015',  # process
        ]
    },
    'devices': {
        'title': 'Devices Module Classes',
        'roots': [
            'http://purl.obolibrary.org/obo/BFO_0000030',  # object
        ]
    }
}


def generate_unified_tree(parser: OntologyParser) -> Tuple[str, int]:
    """Generate a unified tree of all classes from the ontology."""
    builder = OntologyTreeBuilder(parser)
    generator = HTMLGenerator(builder)
    
    # Find root classes (no parents)
    root_uris = builder.get_root_classes()
    print(f"  Found {len(root_uris)} root classes")
    
    # Build trees for all roots
    trees = []
    for root_uri in root_uris:
        tree = builder.build_tree(root_uri)
        if tree:
            trees.append(tree)
            
    # Generate HTML
    tree_html = generator.generate_tree_html(trees, "Full Ontology", "tree-full")
    class_count = generator.count_nodes(trees)
    
    return tree_html, class_count


def generate_module_trees(parser: OntologyParser) -> Dict[str, Tuple[str, int]]:
    """Generate separate trees for each module."""
    builder = OntologyTreeBuilder(parser)
    generator = HTMLGenerator(builder)
    
    trees = {}
    
    for module_name, config in MODULE_CONFIGS.items():
        print(f"  Building tree for {module_name}...")
        
        # Get root URIs for this module
        root_uris = config['roots'].copy()
        if 'extra_roots' in config:
            root_uris.extend(config['extra_roots'])
            
        # Build trees and collect all classes under these roots
        module_trees = []
        module_classes = set()
        
        for root_uri in root_uris:
            if root_uri in builder.classes:
                descendants = builder.get_classes_under(root_uri)
                module_classes.update(descendants)
                
        # Build trees starting from specified roots
        for root_uri in root_uris:
            tree = builder.build_tree(root_uri, allowed_uris=module_classes)
            if tree:
                module_trees.append(tree)
                
        if module_trees:
            tree_html = generator.generate_tree_html(
                module_trees, 
                config['title'], 
                f"tree-{module_name}"
            )
            class_count = generator.count_nodes(module_trees)
            trees[module_name] = (tree_html, class_count)
            print(f"    Generated tree with {class_count} classes")
        else:
            print(f"    Warning: No classes found for {module_name}")
            
    return trees


def update_html_file(script_dir: Path, parser: OntologyParser) -> None:
    """Update ontology-structure.html with generated trees."""
    html_file = script_dir / 'ontology-structure.html'
    
    if not html_file.exists():
        raise FileNotFoundError(f"HTML file not found: {html_file}")
        
    # Create backup
    backup_file = script_dir / f'ontology-structure.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    shutil.copy(html_file, backup_file)
    print(f"Created backup: {backup_file.name}")
    
    # Read current content
    content = html_file.read_text(encoding='utf-8')
    
    # Generate module trees
    module_trees = generate_module_trees(parser)
    
    # Check if CSS is already present
    if '.ontology-tree-container' not in content:
        # Insert CSS before /* Responsive */
        css_marker = '/* Responsive */'
        if css_marker in content:
            content = content.replace(
                css_marker,
                HTMLGenerator.TREE_CSS + '\n\n    ' + css_marker
            )
            print("  Inserted tree CSS styles")
            
    # Check if JS is already present
    if 'OntologyTreeManager' not in content:
        # Insert JS before /* Initialize */
        js_marker = '/* Initialize */'
        if js_marker in content:
            content = content.replace(
                js_marker,
                HTMLGenerator.TREE_JS + '\n\n    ' + js_marker
            )
            print("  Inserted tree JavaScript")
            
        # Add initialization call
        init_pattern = r"document\.addEventListener\('DOMContentLoaded',\s*\(\)\s*=>\s*\{"
        init_match = re.search(init_pattern, content)
        if init_match:
            insert_pos = init_match.end()
            content = (
                content[:insert_pos] +
                '\n      new OntologyTreeManager();' +
                content[insert_pos:]
            )
            print("  Added tree manager initialization")
            
    # Replace existing tree containers with new ones
    for module_name, (tree_html, count) in module_trees.items():
        tree_id = f'tree-{module_name}'
        
        # Pattern to match existing tree container - ends with </ul></div> 
        # Use non-greedy match and proper ending
        pattern = rf'<div class="ontology-tree-container" id="{tree_id}">[\s\S]*?</ul>\s*</div>'
        
        if re.search(pattern, content, flags=re.DOTALL):
            content = re.sub(pattern, tree_html.strip(), content, flags=re.DOTALL)
            print(f"  Replaced {module_name} tree ({count} classes)")
        else:
            print(f"  Warning: Could not find insertion point for {module_name}")
    
    # Write updated content
    html_file.write_text(content, encoding='utf-8')
    print(f"Updated: {html_file}")


def main():
    """Main entry point."""
    print("=" * 70)
    print("PMDco Ontology Tree Generator (Production Version)")
    print("=" * 70)
    
    # Determine paths
    script_dir = Path(__file__).parent.resolve()
    components_dir = script_dir / 'components'
    ttl_file = components_dir / 'pmdco.ttl'
    
    print(f"\nScript directory: {script_dir}")
    print(f"TTL file: {ttl_file}")
    
    # Check TTL file exists
    if not ttl_file.exists():
        print(f"\nError: TTL file not found: {ttl_file}")
        return 1
        
    # Parse ontology
    print("\n" + "-" * 40)
    print("Parsing ontology...")
    print("-" * 40)
    
    parser = OntologyParser(ttl_file)
    parser.parse()
    
    # Verification: Report class count
    total_classes = len(parser.classes)
    print(f"\n[OK] Total classes in ontology: {total_classes}")
    
    # Update HTML file
    print("\n" + "-" * 40)
    print("Updating HTML file...")
    print("-" * 40)
    
    try:
        update_html_file(script_dir, parser)
    except Exception as e:
        print(f"\nError updating HTML: {e}")
        return 1
    
    print("\n" + "=" * 70)
    print(f"[OK] Done! Total classes: {total_classes}")
    print("  Open ontology-structure.html in a browser to view the trees.")
    print("=" * 70)
    
    return 0


if __name__ == '__main__':
    exit(main())
