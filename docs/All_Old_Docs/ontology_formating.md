# Ontology Entity Creation and Formatting Rules

This document establishes a set of rules for creating and formatting ontology entities within the Material Digital Core Ontology project, guided by the ISO 704 standard (Key Findings) and structured analogously to the existing `ontology_structure.md`.

---

## 1. Purpose

Define clear, consistent, and reusable ontology entities (classes, properties, datatypes) that conform to ISO 704 principles and the project’s structural conventions.

## 2. Scope

Applies to all contributions to the Core Ontology (`pmdco-full.owl`) across all modules, ensuring uniform naming, modeling, and documentation.

---

## 3. Terminology and Conformance

1. **Term**: A linguistic label used in the ontology for a concept or relationship.
2. **Concept (Class)**: An abstract idea or category defined by a set of characteristics.
3. **Relationship (Property)**: A typed, directed association between ontology entities.
4. **Definition**: A text description capturing the essential characteristics of a term.

> All terms, concepts, and relationships shall conform to ISO 704 guidelines for terminological work.

---

## 4. Entity Creation Rules

### 4.1 Identifying Domain Concepts

* **Conceptual Analysis**: Derive terms from domain literature and stakeholder interviews.
* **Scope Note**: Provide a usage context when ambiguity is possible.

### 4.2 Naming Conventions

* **Classes**:

  * Use singular, PascalCase (e.g., `BuildingComponent`).
  * Avoid abbreviations unless widely recognized.
* **Object Properties**:

  * Use verb phrases in camelCase, prefixed by the domain (e.g., `hasPart`, `isLocatedIn`).
* **Datatype Properties**:

  * Use noun phrases in camelCase with `has` prefix (e.g., `hasName`, `hasArea`).
* **Annotations**:

  * Use standard annotation properties (`rdfs:label`, `rdfs:comment`, `skos:definition`).

### 4.3 Definitions and Documentation

* **rdfs\:label**: Human-readable preferred term.
* **skos\:definition**: Formal definition in clear, unambiguous language (adapted from ISO 704).
* **skos\:scopeNote**: Elaboration or usage example.
* **dc\:source**: Citation of source document or standard.

### 4.4 Identifiers and URIs

* **Base IRI**: `https://material.digital/ontology/core/3.0.0/`
* **Entity IRI pattern**: `{baseIRI}{entityType}/{localName}` (e.g., `.../Class/BuildingComponent`).
* **Versioning**: Append version tag in ontology header, not in each entity.

### 4.5 Hierarchy and Modularization

* **Taxonomy**: Single-inheritance for explicit class hierarchies; use multiple inheritance sparingly with clear justification.
* **Modules**: Group related entities into OWL imports (e.g., `core`, `spatial`, `process`).
* **Namespaces**: Use one namespace per module; avoid cross-cutting definitions.

### 4.6 Relationships and Constraints

* **Domain and Range**: Explicitly state domain and range for every object property.
* **Cardinality**: Use `owl:cardinality`, `owl:minCardinality`, or `owl:maxCardinality` where required.
* **Inverse Properties**: Provide inverses for key relations (e.g., `hasPart` ↔ `isPartOf`).
* **Property Chains**: Define only when necessary for inference; document thoroughly.

---

## 5. Formatting and Style

* **Turtle Serialization**: Follow the prefix declarations in `ontology_structure.md`.
* **Line Length**: Maximum 120 characters.
* **Comments**: Inline comments start with `# `; block comments use multiple `#` lines.
* **Ordering**:

  1. Prefix declarations
  2. Ontology header (metadata)
  3. Class definitions
  4. Property definitions
  5. Axioms (equivalence, disjointness)
  6. Annotations

---

## 6. Improvements Needed on Current Ontology (`pmdco-full.owl`)

1. **Missing Definitions**: Several classes lack `skos:definition` annotations.
2. **Ambiguous Naming**: Some properties use past-tense or unclear verbs (e.g., `isLoadedBy`).
3. **Unassigned Domains/Ranges**: At least 12 object properties missing explicit domain or range.
4. **Lack of Inverse Properties**: Common relations (e.g., `connectsTo`) missing inverses.
5. **Modular Overlaps**: Spatial and core modules define overlapping classes (e.g., `Site`).
6. **Insufficient Metadata**: Missing `dc:creator`, `dc:created` dates on imported modules.
7. **Cardinality Gaps**: Key relationships (e.g., `hasUnit`) lack cardinality restrictions.
8. **External References**: No mappings to established vocabularies (e.g., QUDT, GeoNames).

---

*End of document.*
