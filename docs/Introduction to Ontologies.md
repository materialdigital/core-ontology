# Introduction to Ontologies (Beginners' Guide)

## What is an Ontology?

An ontology is a formally defined logical structure that represents concepts, categories, properties, and relationships within a specific scientific domain using standardized definitions and naming conventions. Ontologies provide a common language to describe data consistently, making raw information easier to organize, interpret, and share across different experiments, databases, and research disciplines. 

Read more:
- Guarino, Nicola, Daniel Oberle, and Steffen Staab. "What is an ontology?." Handbook on ontologies. Berlin, Heidelberg: Springer Berlin Heidelberg, 2009. 1-17.

## Why do we Need Ontologies?

Ontologies are crucial for modern data management and digitalization because they provide a shared conceptual framework that defines relationships between data entities, ensuring interoperability and consistency across diverse systems. By organizing data using a formal structure, ontologies make information easier to integrate, search, and analyze, helping organizations transform raw, heterogeneous datasets into coherent digital knowledge assets. They support effective data governance by enabling clear definitions, data lineage tracking, and quality control throughout digital infrastructures.
In the context of digital transformation, ontologies act as a universal language that connects data, systems, and processes across business domains, reducing silos and enabling automation, advanced analytics, and AI-driven decision-making. They are also integral to realizing the FAIR data principles (Findable, Accessible, Interoperable, and Reusable) by embedding semantic meaning directly into data models, which promotes transparency, reproducibility, and long-term data sustainability. Without ontologies, organizations face fragmented data landscapes where digital information cannot be effectively reused or shared, hindering collaboration and innovation.

## Motivation for Developing Ontologies in Materials Science and Engineering (MSE)
The motivation for developing MSE ontologies arises from the increasing demand to organize, integrate, and exploit the rapidly growing volume of heterogeneous data produced across the field. MSE is undergoing a major digital transformation, driven by the need for data-driven innovation, sustainability, and accelerated materials discovery. As an interdisciplinary domain, MSE combines physics, chemistry, and engineering to understand and optimize the relationships between material processing, structure, properties, and performance (PSPP). It spans the full materials lifecycle (from raw material extraction to product design, manufacturing, and end-of-life recycling) and supports key technological sectors including energy, aerospace, electronics, automotive, and healthcare.
 

<img width="468" height="276" alt="image" src="https://github.com/user-attachments/assets/2700f632-dafb-46d4-84de-00e14885e176" />

Motivation for the Semantic Representation of Materials Life Cycle via PMDco

This complexity leads to diverse experimental methods, simulation techniques, and industrial processes, all generating data with different formats, terminologies, and metadata requirements. Without a shared semantic foundation, such diversity makes it difficult to connect, compare, or reuse data across laboratories, instruments, and software tools. As a result, valuable knowledge remains siloed, limiting reproducibility and slowing down scientific progress.

Ontologies address these challenges by providing standardized vocabularies and formal semantic relationships that ensure consistent description of materials and their behaviors. By harmonizing data models and bridging conceptual and domain-specific knowledge, ontologies enable semantic interoperability, allowing data to be seamlessly exchanged, integrated, and interpreted across scales, methods, and organizations. This is essential for applying the FAIR principles, ensuring that MSE data becomes both human-understandable and machine-actionable for advanced analytics, automation, and AI-driven research.

In addition, ontology-based data representation improves data quality by capturing dependencies (e.g., process–structure relationships), enforcing consistency, and reducing ambiguity in interpretation. Enhanced provenance and metadata standards further support reproducibility, traceability, and credibility in research outcomes. These capabilities are crucial for emerging digital concepts such as materials informatics, workflow automation, and digital twins, which rely on robust links between experimental and computational knowledge.

The development of PMDco specifically targets several critical challenges within the MSE landscape:
-	Heterogeneous terminology, stemming from diverse subdomains and industrial practices
-	Lack of standardized data structures, especially across experimental, simulation, and manufacturing environments
-	Sparse or missing metadata, which restricts data reuse and reproducibility
-	Semantic misalignment between generic models and specialized domain knowledge, limiting cross-disciplinary collaboration

By functioning as a mid-level ontology for MSE, PMDco provides a common semantic backbone for the Platform MaterialDigital ecosystem. It supports automated data integration, harmonizes terminology and processes, and enables coherent knowledge representation throughout the materials lifecycle.

Ultimately, the development of MSE ontologies represents a strategic step toward a more efficient, connected, and intelligent research ecosystem — accelerating innovation while promoting sustainable and FAIR data practices.

## Ontology Levels and Example MSE-Related Ontologies

Based on the degree of abstraction and formal expressiveness, the ontologies are classified into the following four levels: 

**1) Top-level ontologies (TLOs)** describe common general concepts across various domains at the highest possible level of abstraction. TLOs establish semantic standards and incorporate universal and fundamental concepts to ensure the connection and interoperability of a wide range of conceivable domain ontologies. [Basic Formal Ontology (BFO)](https://github.com/bfo-ontology/BFO-2020), [Eelementary Multiperspective mMaterial Ontology (EMMO)](https://emmo-repo.github.io/), [descriptive ontology for linguistic and cognitive engineering (DOLCE)](https://www.loa.istc.cnr.it/index.php/dolce/), [suggested upper merged ontology (SUMO)](https://github.com/ontologyportal/sumo), and [semanticscience integrated ontology (SIO)](https://github.com/MaastrichtU-IDS/semanticscience) are TLOs that were mostly reused for developing the ontologies in the MSE domain. 

**2) Mid-level ontologies (MLOs)** add finer granular entities to the TLOs and make them more modular to enable interconnecting of the complex and expressive domain-level ontologies (DLOs). For example, [ontology of biomedical investigations (OBI)](https://obi-ontology.org/), [NFDIcore ontology](https://github.com/ISE-FIZKarlsruhe/nfdicore), and [industrial ontologies foundry (IOF) core](https://github.com/iofoundry/ontology) are the MLOs that are established based on the BFO TPO. 

**3) Domain-level ontologies (DLOs)** contain highly expressive and explicit expert knowledge and represent concepts, definitions, facts, statements, axioms, rules, and relations that belong to specific domains. Until now, a variety of DLOs were introduced in the domain of materials science, which were designed based on different types of TLOs and MLOs. For instance, [MSEO](https://github.com/Mat-O-Lab/MSEO) is a DLO that reuses BFO and IOF core and represents extensive semantics in the domain of materials science and engineering. 

**4) Application-level ontologies (ALOs)** provide highly detailed semantics for specific use cases and support the development of knowledge graphs. For example, tensile test ontology (TTO), fatigue testing ontology (FTO), and Vickers testing ontology (VTO) in the domain of materials mechanical testing. 

More examples for MSE ontologies can be found in [MatPortal](https://matportal.org/), the ontology repository for materials science.

Read more:
-	Beygi Nasrabadi, Hossein, et al. "Performance Evaluation of Upper‐Level Ontologies in Developing Materials Science Ontologies and Knowledge Graphs." Advanced Engineering Materials 27.8 (2025): 2401534.
-	De Baas, Anne, et al. "Review and alignment of domain-level ontologies for materials science." IEEE Access 11 (2023): 120372-120401.
-	Norouzi, Ebrahim, Jörg Waitelonis, and Harald Sack. "The landscape of ontologies in materials science and engineering: A survey and evaluation." arXiv preprint arXiv:2408.06034 (2024).

## Ontology Language

The ontology is implemented in the [Web Ontology Language (OWL)](https://www.w3.org/OWL/), a powerful and widely used language for creating complex and interoperable ontologies. OWL supports logical reasoning and facilitates the integration of machine-readable data with semantic web technologies. Furthermore, different notations and formats may be used. Typically, PMDco is also provided in [Turtle (TTL)](https://www.w3.org/TR/turtle/) syntax.

## Key Components of an Ontology

-	**Class**: A class provides an abstraction mechanism for grouping resources with similar characteristics. Every class is associated with a set of individuals, called the class extension. The individuals in the class extension are called the instances of the class. A class has an intentional meaning i.e., the underlying concept.
-	**Object Property**:  The relationship of an individual to another individual. An object property is defined as an instance of the built-in OWL class owl:ObjectProperty.
-	**Datatype Property**: Datatype properties link individuals to data values. A datatype property is defined as an instance of the built-in OWL class owl:DatatypeProperty.
-	**Instance**: Individual realization of a concept. For example, the concept tensile test may be instantiated with a particular tensile test that occurred at a particular time at a particular location and with particular parameters. All instantiations together represent the ontology A-Box, where statements are made about instances using the terminology defined in the T-Box.
Read more: MaterialDigital Initiative Glossary (a comprehensive glossary for the ontology-related terms).

## Ontology Development Tools and Resources
* [Protégé](https://protege.stanford.edu/software.php) - A versatile ontology editor that supports OWL 2. It enables visualization, editing, and reasoning over ontology structures.
* [ODK](https://github.com/INCATools/ontology-development-kit) - The Ontology development kit (ODK) is an incredibly great tool to manage your ontology's life cycle. The ODK is: i) a toolbox of various ontology related tools such as ROBOT, owltools, dosdp-tools and many more, bundled as a docker image, and ii) a set of executable workflows for managing your ontology's continuous integration, quality control, releases and dynamic imports.
* [Draw.io](https://www.drawio.com/) - Online tool for visual diagrams construction.
* [OntoPanel](https://yuechenbam.github.io/src/main/webapp/index.html) - A graphical plug-in for diagrams.net that simplifies ontology development and visualization for domain experts.
* [Chowlk Converter](https://chowlk.linkeddata.es/) - Chowlk Converter is a web application that takes as input an ontology conceptualization made with diagrams.net and generates its implementation in OWL.
* [OTTR](https://ottr.xyz/) - language with supporting tools for representing and instantiating RDF graph and OWL ontology modelling patterns. Provides an abstraction level on top of basic RDF functionality.
* [OOPS!](https://oops.linkeddata.es/) - OOPS! is a web-based tool, independent of any ontology development environment, for detecting potential pitfalls that could lead to modelling errors.
* [RDF Grapher](https://www.ldf.fi/service/rdf-grapher) - RDF grapher is a web service for parsing RDF data and visualizing it as a graph.
* [OnToology](http://ontoology.linkeddata.es/) - A system to automate part of the collaborative ontology development process. Given a repository with an owl file, OnToology will survey it and produce diagrams, a complete documentation and validation based on common pitfalls. 
* [ROBOT](http://robot.obolibrary.org/) - ROBOT is a tool for working with Open Biomedical Ontologies. It can be used as a command-line tool or as a library for any language on the Java Virtual Machine.
*	**Python Libraries** - Libraries such as ``rdflib`` and ``Owlready2`` are mostly employed for semantic data processing, integration, and validation.
*	**Version Control and Collaboration** - GitHub is useing for version control, issue tracking, and collaborative development, ensuring transparency and structured updates.

## Ontology Learning Materials for Beginners

*	[A Practical Ontology Development Guide](https://github.com/scientific-ontology-network/ontology-development-guide/releases/download/v0.1.0/ontology-guide.pdf): In cooperation with participants in the MaterialDigital initiative, a guide for the development of ontologies in general was created, which contains basic aspects and recommended procedures. This guide may be expanded and developed further and is hosted at [The Scientific Ontology Network](https://scientific-ontology-network.github.io/).
*	[Ontology Development 101](https://protege.stanford.edu/publications/ontology_development/ontology101.pdf): Stanford University's guide provides a foundational, step-by-step methodology for creating your first ontology.
*	[Pizza Tutorial](https://drive.google.com/file/d/1A3Y8T6nIfXQ_UQOpCAr_HFSCwpTqELeP/view): A practical guide to building OWL ontologies using Protégé 5.5 and plugins
*	[OBO Academy’s Ontology Design Course](https://oboacademy.github.io/obook/lesson/ontology-design/): An interactive, free curriculum that provides lessons on ontology construction, reasoning, and design principles (based on the OBO Foundry and Semantic Web standards)
*	[ISE FIZ YouTube channel](https://www.youtube.com/channel/UCjkkhNSNuXrJpMYZoeSBw6Q/): [Playlist of Lectures "Knowledge Graphs - Foundations and Applications](https://www.youtube.com/playlist?list=PLNXdQl4kBgzubTOfY5cbtxZCgg9UTe-uF)"
*	[Barry Smith's YouTube channel](https://www.youtube.com/@BarrySmithOntology/playlists)
*	[PMD YouTube channel](https://www.youtube.com/channel/UCAwf5QXQ6Oa4NPaL3bXFvAA)

 

