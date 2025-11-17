![shacl validation](https://github.com/materialdigital/core-ontology/actions/workflows/shacl.yaml/badge.svg)
![basic checks](https://github.com/materialdigital/core-ontology/actions/workflows/quality-checks.yaml/badge.svg)


# PMD Core Ontology

## Introduction

The **Platform MaterialDigital Core Ontology (PMDco)** is a mid-level semantic framework for **Materials Science and Engineering (MSE)**. Aligning with the ISO/IEC 21838-2:2021 standard, PMDco constructed on basis of *Basic Formal Ontology (BFO)* and reuses several BFO-aligned ontologies like RO, IAO, and OBI. The scope of PMDco follows the fundamental paradigm of MSE (processing, structure, and properties) and encompasses the following domains:

* **Processes:** Representation of MSE-related process chains, including materials manufacturing, characterization, and simulation processes.
* **Structure/state:** Description of substances, engineered materials, and specification of materials, their composition, and multiscale structural features.
* **Properties:** Specification of material properties and qualities, representing processing-structure-properties dependences.

PMDco also provides general entities required for representing the fundamental MSE topics (e.g., thermodynamics), as well as general semantics for entities commonly required across MSE disciplines (such as devices, roles, functions, and plans).


## Repository Structure

This repository provides the modular implementation of PMDco, developed and maintained using the [Ontology Development Kit (ODK)](https://github.com/INCATools/ontology-development-kit).
### Top-level directories
* **.github/:** GitHub configuration files, including CI workflows and templates.
* **docs/:** Documentation sources for the ontology website and user guides.
* **patterns/:** Logical patterns and SHACL shapes used to maintain consistent ontology design.
* **src/:** Main development folder generated and managed through ODK.
  * **ontology/components/:** – Modular ontology components (classes, properties, axioms).
  * **ontology/pmdco-edit.owl:** – Primary editable ontology file used during development (ontology editors' version).

### Ontology versions
* **pmdco-full.owl/ttl:** Complete ontology with all imports and full axiomatization.
* **pmdco-base.owl/ttl:** Core entities without extended imports.
* **pmdco-simple.owl/ttl:** Simplified version with basic subclass and existential axioms.
* **pmdco-minimal.owl/ttl:** Lightweight minimal version for quick onboarding (recommended for beginners, see issue [#121](https://github.com/materialdigital/core-ontology/issues/121)).
* **pmdco.owl/ttl:** Main ontology file contains the full version.

### Other files
* README.md, LICENSE.txt, CONTRIBUTING.md – Project overview, license, and contribution guidelines.
* mkdocs.yaml – Configuration for building the documentation site.


## Documentation
**[PMDco documentation page]( https://materialdigital.github.io/core-ontology/docs/)** is designed to provide a clear overview of the core concepts, modules, and design principles of the Platform Material Digital Core Ontology. It offers guidance for users and developers on how the ontology is structured, how it should be applied in real-world MSE data workflows, and how the components relate to each other. The site includes detailed explanations, examples, patterns, and release information, helping new users get started quickly while supporting advanced users in integrating PMDco into their data and knowledge graph environments.

### Further documentation sources:
* **[Widoco List of Classes and Properties](https://materialdigital.github.io/core-ontology/)**
* **[PMDCo in MatPortal](https://matportal.org/ontologies/PMDCO)**
* **[Publications related to PMDco]( https://materialdigital.github.io/core-ontology/docs/publications/)**


## Contribution

We welcome contributions to the Platform MaterialDigital core ontology (PMDco)!

To get involved:

- Please use this GitHub repository's **[Issue tracker](https://github.com/materialdigital/core-ontology/issues)** to request new terms/classes or report errors or specific concerns related to the ontology.
- For creation of application ontologies using PMD core ontologies, we advise using the **[application-ontology-template](https://github.com/materialdigital/application-ontology-template/)**. It applies the same framework used here and mirrors the pmdco with all its modules.
- Write about your specific modeling concerns or any other discussable topics in the **[discussion forum](https://github.com/materialdigital/core-ontology/discussions)**.
- Participate in our **PMD Playground Meetings**: Our Ontology Playground, organized online every second Friday from 1-2 pm (CET), is a great opportunity to connect with developers and our proactive community to shape the PMDco. Please register via our [mailing list](https://www.lists.kit.edu/sympa/subscribe/ontology-playground?previous_action=info).
- If you need further information, please feel free to contact us via **[info@material-digital.de](info@material-digital.de)**

