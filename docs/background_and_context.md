# 2. Background and Context

Todo

> - **Domain Overview**: Provide an introduction to the domain being modeled.
> - **Motivation**: Explain why the ontology was created and the problems it addresses.
> - **Existing Ontologies**: Mention related ontologies and how this ontology complements or extends them.

> --> Please check for comprehensibility (Markus)

## Domain Overview

The Platform MaterialDigital Core Ontology (PMDco) addresses challenges in the domain of Materials Science and Engineering (MSE), which is undergoing a significant digital transformation. MSE is an interdisciplinary field that focuses on understanding and adaption of the properties of materials to develop new products and improve existing ones. It combines principles from physics, chemistry, and engineering to explore the relationships between the structure, properties, processing, and performance of materials.

Hence, the key components of MSE may be considered to be:

- ***Materials Classes***, such as metals, ceramics, polymer, composites, etc.,
- ***Materials Related Paradigms***, which are summarized by processing, structure, properties, and performance (PSPP), and
- ***Applications and Research Areas***, which include, e.g., nanotechnology, metallurgy, materials testing, etc.

> **Materials Paradigms**
>
> ***Processing (P)***: The methods used to shape and treat materials to achieve desired properties. This includes techniques like casting, forging, and additive manufacturing.
>
> ***Structure (S)***: The arrangement of atoms and molecules within a material, which can be observed at >  different scales (atomic, microscopic, and macroscopic).
>
> ***Properties (P)***: The characteristics of materials that determine their behavior under various > conditions. These include mechanical, electrical, thermal, optical, and magnetic properties.
>
> ***Performance (P)***: How well a material performs in a specific application, considering factors like > durability, efficiency, and cost-effectiveness.

MSE is crucial for technological advancement and innovation. It drives the development of new materials that can lead to breakthroughs in various industries, including aerospace, automotive, electronics, healthcare, and energy. By understanding and controlling the properties of materials, scientists and engineers can create solutions that improve performance, efficiency, and sustainability. Especially with regard to the latter, MSE encompasses the entire materials lifecycle, from raw material procurement to the development of components, production, and end-of-life recycling.

As a matter of fact, efficient data management in MSE is vital for enhancing productivity, enabling innovations, and ensuring sustainability. This requires harmonized data structures that are accessible, reusable, and interoperable. Semantic interoperability, enabled by ontologies, bridges the gap between high-level conceptual frameworks and specific domain applications, making it easier to capture, share, and reuse data across disciplines and throughout material lifecycles.

---

## Motivation

The creation of the PMDco is driven by the need to overcome critical data integration and management challenges in MSE, such as:

1. **Heterogeneity of Terminology**: MSE involves diverse perspectives from its subdomains, leading to inconsistencies in terminology that hinder data sharing and understanding.
2. **Lack of Standardized Data Formats**: Data from experiments, simulations, and industrial processes often lack uniform structures, impeding the seamless exchange of information.
3. **Sparse and Incomplete Data**: Contextual information, including metadata and provenance, is frequently missing, limiting reproducibility and reuse.
4. **Semantic Gaps Between Domains**: The absence of alignment between high-level ontologies and domain-specific vocabularies creates integration challenges for cross-disciplinary research.

The PMDco serves as a mid-level ontology designed to address these challenges by standardizing MSE terminologies and processes, enabling automated data integration, and facilitating adherence to the FAIR (Findable, Accessible, Interoperable, Reusable) principles.

---

## Existing Ontologies

The PMDco complements and extends several existing ontologies by providing a mid-level framework tailored for the MSE domain:

- **Top-Level Ontologies (TLOs)**:

  - The *[Basic Formal Ontology (BFO)](https://basic-formal-ontology.org/)* provides abstract, cross-domain semantic structures. However, its high-level nature complicates direct application to MSE-specific contexts.
  - PMDco bridges the gap by integrating MSE-specific concepts into this (and such) general frameworks.
- **Domain-Specific Ontologies**:

  - Chemical Entities of Biological Interest ([ChEBI](https://www.ebi.ac.uk/chebi/)) facilitates representation of chemical entities.
  - Quantities, Units, Dimensions, and Types ([QUDT](https://qudt.org/)) ontology supports the standardization and conversion of measurement units.
  - PROV Ontology ([PROV-O](https://www.w3.org/TR/prov-o/)), developed by [W3C](https://www.w3.org/), focuses on representing provenance and process data, which PMDco leverages to ensure traceability in MSE processes.

Despite their utility, many existing ontologies are niche-focused, inaccessible, or poorly maintained, limiting their broader applicability. The PMDco incorporates reusable components from these ontologies while addressing their limitations through a community-driven development and curation process.

---
