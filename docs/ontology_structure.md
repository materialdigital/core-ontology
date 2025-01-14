# Ontology Structure
TODO:
> - **Key Components**:
>   - **Classes**: Define the primary categories or entities.
>   - **Properties**: Describe relationships (object properties) and attributes (data properties).
>   - **Individuals**: Provide examples of specific instances.
> - **Hierarchy**:
>   - Present the taxonomy or class hierarchy (e.g., parent-child relationships).
>   - Use diagrams for clarity.
> - **Annotations**: Document metadata for classes, properties, and individuals (e.g., labels, comments, descriptions).
> - **Constraints and Rules**: Define any restrictions (e.g., cardinality constraints, domain/range specifications).

## Key Components

The key components within PMDco are based on classic ontology development, so that classes, object properties, data properties, individuals, and annotations are defined and specified in PMDco. 

### Classes
PMDco defines several primary categories central to materials science and engineering (MSE) as classes. Notable classes include:

- **Material**: A Material is a portion of matter that has the disposition to participate in some manufacturing process and whose shape is not relevant for its disposition to participate in the manufacuring process.
- **Manufacturing Process**: Denotes a planned process that is driven by the primary intent to transform objects. A manufacturing process is always a transformative process.
- **Mechanical Property Analyzing Process**: Refers to an assay that evaluates the mechanical characteristics of materials, such as strength, hardness, elasticity, and tensile properties, often through tests that measure response to forces and loads.
- **Material Property**: A material property is a material trait in terms of the kind and magnitude of response to a specific imposed stimulus. Generally, definitions of properties are made independent of material shape and size.

### Properties
PMDco includes properties that define relationships and attributes:

- **Object Properties**:
  - **stimulates**: Links a stimulating process to a material property involved.
  - **composed of**: The property specifies of which kind of general portion of material something is built of.

- **Data Properties**:
  - **hasValue**: Assigns a specific value to a property, such as a numerical measurement.
  - **hasUnit**: Specifies the unit of measurement for a given value.

### Individuals
While PMDco serves as a mid-level ontology and may not define specific instances, it provides a framework for users to instantiate individuals pertinent to their domain. Therefore, however, it does not contain individuals in its pure form.

## Hierarchy
PMDco presents a structured taxonomy with parent-child relationships among classes (class/subclass-relations). For example:

- **Entity**
  - **Continuant**
    - **Independent Continuant**
      - **Material Entity**
        - **Material Entity Aggregate**
          - **Portion of Matter**
            - **Material**
  - **Occurrent**
    - **Process**
      - **Planned Process**
        - **Manufacturing Process**

Block depiction:
```
Entity
  ├── Continuant
  │   ├── Independent Continuant
  │   │   ├── Material Entity
  │   │   │   ├── Material Entity Aggregate
  │   │   │   │   ├── Portion of Matter
  │   │   │   │   │   └── Material
  ├── Occurrent
  │   ├── Process
  │   │   ├── Planned Process
  │   │   │   └── Manufacturing Process
  ```

This hierarchical structure facilitates organized data representation and promotes interoperability across MSE domains.

## Annotations
PMDco employs annotations to enrich classes and properties with metadata and human readable information, enhancing clarity and usability. This information may be provided in different natural languages (e.g., English and German).

- **Labels** | ***rdfs:label***: Provide human-readable names for ontology elements.
- **Comments** | ***rdfs:comment***: Offer detailed descriptions, usage notes, clarifications of definitions, or additional relevant information. They may enhance the understanding of the terms regarded.
- **Definitions** | ***skos:definition***: Delivers formal, human readable explanations and descriptions of classes and properties. Preferably, [Aristotelian definitions](#aristotelian-definition) are used that support in finding subclass relationships.
- **Definition Source** | ***obo:IAO_0000119***: If the definition was obtained from a specific source (e.g., a well-known work from the field of MSE, a dictionary, or a URI/URL), this is specified as definition source, also citing the original document.

> #### Aristotelian definition: 
> An **Aristotelian definition** typically refers to defining something by its genus (general category) and differentia (specific characteristics that distinguish it from other members of the same genus). This method is rooted in Aristotle's philosophy and is often used in ontology development to define classes in relation to their superclasses. For more information, please see [Aristotelian](https://www.merriam-webster.com/dictionary/Aristotelian) and [Aristotelianism](https://en.wikipedia.org/wiki/Aristotelianism).

For instance, the class **Material** may have the following annotations:
- **Label**: "Material"@en, "Material"@de
- **Definition**: "A Material is a Portion Of Matter that has the disposition to participate in some Manifacturing Process and whose shape is not relevant for its disposition to participate in the Manifacuring Process."@en
- **Comment**: "The sum of portions of matter of the same type form a portion of matter of that type."@en

## Constraints and Rules
PMDco defines specific constraints to ensure data consistency:

- **Cardinality Constraints**: Specify the number of times a property can be associated with a class.
  - For example, a **Manufacturing Process** may be constrained to have some **material entity** as input using the **has_specified_input** property.

- **Domain and Range Specifications**: Define the applicable classes for properties.
  - The **stimulates** property (subproperty of **realizes**) has a domain of **Stimulating Process** and a range of **Material Property**.

These constraints ensure logical consistency and facilitate accurate data representation within the ontology.