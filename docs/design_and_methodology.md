# Design and Methodology

TODO

> - **Design Principles**: Outline principles (e.g., modularity, reuse of existing standards).
> - **Ontology Language and Tools**: Specify the ontology language (e.g., OWL, RDF) and tools (e.g., Protégé, OntoPanel).
> - **Development Process**: Describe steps followed during ontology creation (e.g., requirements gathering, modeling, validation).
> - **Versioning and Updates**: Discuss how the ontology will be maintained and updated.

> --> Please check for comprehensibility (Markus)

## Design Principles

The design of the ontology adheres to several fundamental principles to ensure usability, scalability, and alignment with the broader materials science community:

1. **Modularity**:
   The ontology is constructed in a modular fashion to enable different components to be developed, maintained, and reused independently. This approach supports scalability and customization for diverse use cases within the field of MSE while maintaining a cohesive structure.

2. **Reuse of Existing Standards**:
   Existing ontologies and standards such as [QUDT](https://qudt.org/) and [ChEBI](https://www.ebi.ac.uk/chebi/) have been integrated into the ontology to enhance semantic consistency and avoid duplication of effort. Aligning with these well-established resources ensures interoperability with other knowledge systems. Furthermore, established standards within the MSE realm are used to create, label, and define relevant concepts. One of the advantages is their broad distribution among stakeholders and a terminology and denomination a group of experts in the field has already agreed upon which enhances its acceptability.

3. **Community-Driven Development**:
   The ontology is curated and refined through ongoing engagement with domain experts and stakeholders. Workshops, feedback sessions, and collaborative modeling exercises are integral to ensuring the ontology addresses real-world requirements effectively.

4. **Adherence to FAIR Principles**:
   The design facilitates the creation of Findable, Accessible, Interoperable, and Reusable (FAIR) datasets by providing well-defined semantics and structured frameworks for data representation.

---

## Ontology Language and Tools

### Ontology Language

The ontology is implemented in the **[Web Ontology Language (OWL)](https://www.w3.org/OWL/)**, a powerful and widely used language for creating complex and interoperable ontologies. OWL supports logical reasoning and facilitates the integration of machine-readable data with semantic web technologies. Furthermore, different notations and formats may be used. Typically, PMDco is also provided in **[Turtle (TTL)](https://www.w3.org/TR/turtle/)** syntax.

### Tools Used

1. **Protégé**:
   A versatile ontology editor that supports OWL 2. It enables visualization, editing, and reasoning over ontology structures. Protégé was used for creating and managing the ontology.

2. **OntoPanel**:
   A graphical plug-in for diagrams.net that simplifies ontology development and visualization for domain experts.

3. **Python Libraries**:
   Libraries such as `rdflib` and `Owlready2` were employed for semantic data processing, integration, and validation.
   
4. **Version Control and Collaboration**:
   GitHub was used for version control, issue tracking, and collaborative development, ensuring transparency and structured updates.

---

## Development Process

The ontology development followed a structured and iterative process:

1. **Requirements Gathering**:

   - Conduct surveys and consultations with domain experts to identify key concepts, relationships, and use cases.
   - In particular, consideration and involvement of standards relevant in the field of MSE.
   - Analyze existing data and workflows in MSE to understand integration points and challenges.
2. **Conceptual Modeling**:

   - Develop visual representations of key processes and entities using tools like ConceptBoard or Miro.
   - Structure concepts hierarchically, linking mid-level ontology elements to top-level frameworks (e.g., BFO).
3. **Implementation**:

   - Define classes, properties, and axioms in OWL using the well-known ontology creation and manipulation tool ***[Protégé](https://protege.stanford.edu/)***.
   - Leverage existing ontologies where possible, mapping relevant terms and extending them with domain-specific semantics.
4. **Validation and Iteration**:

   - Use reasoning tools (e.g., resoners HermiT and Pellet) to ensure logical and technical consistency and identify potential redundancies.
   - Validate the ontology against real-world datasets and application scenarios through collaborative workshops.
5. **Documentation and Training**:

   - Create detailed documentation, including best practices, examples, and guidelines for using the ontology.
   - Conduct training sessions for stakeholders to facilitate adoption and feedback collection.

---

## Versioning and Updates

### Version Control

The ontology employs a robust versioning system hosted on GitHub, aiming to ensure:

- Clear tracking of changes over time.
- Transparent contributions from the community.
- Accessibility of historical versions for comparison and reference.

### Update Mechanism

1. **Community Feedback Loop**:

   - Regular workshops and feedback sessions with MSE experts to identify necessary additions and refinements.
   - Implementation of a curation process to assess and prioritize updates based on community needs.
2. **Release Cycle**:

   - Major updates may be rolled out to a certain extent, incorporating substantial changes and new features.
   - Minor updates addressing bug fixes or minor refinements are released on a need basis.
3. **Documentation of Changes**:

   - A comprehensive changelog is maintained for every release, detailing added, modified, or deprecated elements.
