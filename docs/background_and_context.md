# Background and Context

## Domain Overview

The Platform MaterialDigital Core Ontology (PMDco) addresses challenges in the domain of Materials Science and Engineering (MSE), which is subject to significant digital transformation. The MSE domain is an interdisciplinary field that focuses on understanding and adaption of material properties to develop new and improve existing products. The MSE domain combines principles from physics, chemistry, and engineering to explore the relationships between the structure, properties, processing, and performance of materials.

In summary, key components of the MSE domain can be categorized in:

- ***Materials Classes***, such as metals, ceramics, polymer, composites, etc.,
- ***Applications and Research Areas***, which include, e.g., nanotechnology, metallurgy, or materials testing, and
- ***Materials Related Paradigms***, which are summarized by processing, structure, properties, and performance (PSPP).
  
> **Materials Paradigms**
>
> ***Processing***: The methods used to shape and treat materials to achieve desired properties. This includes techniques like casting, forging, and additive manufacturing.
>
> ***Structure***: The arrangement of atoms and molecules within a material, which can be observed at  different scales (atomic, microscopic, and macroscopic).
>
> ***Properties***: The characteristics of materials that determine their behavior under various conditions. These include mechanical, electrical, thermal, optical, and magnetic properties.
>
> ***Performance***: How well a material performs in a specific application, considering factors like durability, efficiency, and cost-effectiveness.

MSE is crucial for technological advancement and innovation. It drives the development of new materials that can lead to breakthroughs in various industries, including aerospace, automotive, electronics, healthcare, and energy. By understanding and controlling the properties of materials, scientists and engineers can create solutions that improve performance, efficiency, and sustainability. Especially with regard to the latter, MSE encompasses the entire materials lifecycle, from raw material procurement to the development of components, production, and end-of-life recycling.

As a matter of fact, efficient data management in MSE is vital for enhancing productivity, enabling innovations, and ensuring sustainability. This requires harmonized data structures that are accessible, reusable, and interoperable. Semantic interoperability, enabled by ontologies, bridges the gap between high-level conceptual frameworks and specific domain applications, making it easier to capture, share, and reuse data across disciplines and throughout material lifecycles.

---

## Motivation

The creation of the PMDco is driven by the need to overcome critical data integration and management challenges in MSE, such as:

1. **Heterogeneity of Terminology**: MSE involves diverse perspectives from its subdomains, leading to inconsistencies in terminology that hinder data sharing and understanding.
2. **Lack of Standardized Data Formats**: Data from experiments, simulations, and industrial processes often lack uniform structure, impeding the seamless exchange of information.
3. **Sparse and Incomplete Data**: Contextual information, including metadata and provenance, is frequently missing, limiting reproducibility and reuse.
4. **Semantic Gaps Between Domains**: The absence of alignment between high-level and domain-specific vocabularies poses integration challenges for cross-disciplinary research.

The PMDco serves as a mid-level ontology designed to address these challenges by standardizing the MSE terminologies and processes, enabling automated data integration, and facilitating adherence to the FAIR (Findable, Accessible, Interoperable, Reusable) principles.

---

## Existing Ontologies

The PMDco complements and extends several existing ontologies by providing a mid-level framework tailored for the MSE domain:

- **Top-Level Ontologies (TLOs)**:

  - The [Basic Formal Ontology](https://basic-formal-ontology.org/bfo-2020.html) which is an ISO standard [BFO2020](https://www.iso.org/standard/74572.html) provides abstract, cross-domain semantic structures. However, its highly abstract nature complicates direct application to MSE-specific contexts.
  - PMDco bridges the gap by integrating MSE-specific concepts into this general framework.
    
- **Domain-Specific Ontologies**:
  
  - Chemical Entities of Biological Interest ([ChEBI](https://www.ebi.ac.uk/chebi/)) facilitates representation of chemical entities.
  - Information Artifact Ontology ([IAO](https://obofoundry.org/ontology/iao.html)) represents types of information content entities such as documents, databases, and digital images.
  - Ontology for Biomedical Investigations ([OBI](https://obi-ontology.org/)) helps to communicate about scientific investigations by defining terms for assays, devices, objectives, and more.
    
 Please note that while IAO and OBI ontologies are not the domain-level ontologies in the usual meaning, we put them into this list to point out that they cover only certain "aspects of reality", in contrast to the BFO ontology, aiming to provide a comprehensive abstract framework for all the concepts.
  

Despite their utility, many existing ontologies are niche-focused, inaccessible, or poorly maintained, limiting their broader applicability. The PMDco incorporates reusable components from these ontologies while addressing their limitations through a community-driven development and curation process.

---
