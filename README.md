![shacl validation](https://github.com/materialdigital/core-ontology/actions/workflows/shacl.yaml/badge.svg)
![basic checks](https://github.com/materialdigital/core-ontology/actions/workflows/quality-checks.yaml/badge.svg)
![Build Status](https://github.com/materialdigital/core-ontology/actions/workflows/qc.yml/badge.svg)


# PMD Core Ontology

## Introduction

The Platform MaterialDigital core ontology (PMDco) is a mid-level ontology for materials science and engineering (MSE). The PMDco provides bridging mid-level concepts for detailed description of processes, experiments, and computational workflows enabling the reproducibility of process and materials data. These general MSE concepts are designed to be extendable for specific applications within application ontologies. The PMDco is designed in a collaborative effort within the MaterialDigital initiative and intended to be easily used by MSE domain experts.


## Versions
### Stable release versions

The latest version of the ontology can always be found at:


[pmdco.owl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/pmdco.owl) and [pmdco.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/pmdco.ttl)


### Variants

The ontology is shipped in different variants, each as OWL (\*.owl) and Turtle serializations (\*.ttl):

* **full:** [pmdco-full.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/pmdco-full.ttl), [pmdco.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/pmdco.ttl) (default)
* **base:** [pmdco-base.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/pmdco-base.ttl)
* **simple:** [pmdco-simple.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/pmdco-simple.ttl)
* **minimal:** [pmdco-minimal.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/pmdco-minimal.ttl) (for beginners)

The **"full release"** artefact contains all logical axioms, including inferred subsumptions. All imports and components are merged into the full release artefact to ensure easy version management. The full release represents most closely the actual ontology as it was intended at the time of release, including all its logical implications. 

The **"base file"** is a specific release flavour. It reflects the intention of the ontology author for the official (publicly released) representation of the ontologies "base entities". "Base entities" are entities that are defined ("owned") by the ontology. The representation includes the intended public metadata (annotations), and classification (subClassOf hierarchy), including any statements where a base entity is the subject.

The **"simple"** artefact only contains a simple existential graph of the terms defined in the ontology. This corresponds to the state before logical definitions and imports. For example, the only logical axioms are of the form *CL1 subClassOf CL2* or *CL1 subClassOf R some CL3* where *R* is any objectProperty and *CLn* is a class. The simple variant only contains the essential classes and no imports.

The **"minimal"** artefact only contains a preselected minimal of the terms defined in the ontology. This set is extracted form the full variant and represents a lightweight subset of the ontology that covers the most essential concepts for basic interoperability and implementation. We recommend beginners to start with this artifact when learning about the ontolgoy (See issue [#121](https://github.com/materialdigital/core-ontology/issues/121)).


The ontology **"main"** file [pmdco.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/pmdco.ttl) contains the full version.


### Editors' version

Editors of this ontology should use the edit versions of the differenet modules. You can find them in the components folder.

Editors component files: [src/ontology/components](https://github.com/materialdigital/core-ontology/blob/main/src/ontology/components)

From the editing main file all release variants are derived by the build workflows.
Editors main file: [src/ontology/pmdco-edit.owl](https://github.com/materialdigital/core-ontology/blob/main/src/ontology/pmdco-edit.owl)

### Important Folders: 

 - ```src/ontology/components```    modules of the PMD ontology
 - ```patterns```    patterns describing the use of the modules and show examples
 - ```shapes```    shapes to describe the sets of conditions and constraints of use formally

## Documentation

- [Documentation](https://materialdigital.github.io/core-ontology/docs)
- [Beginers Guide Miro Board ](https://miro.com/app/board/uXjVLY9FwGU=/)
- [Widoco List of Classes and Properties](https://materialdigital.github.io/core-ontology/)
- [Patterns and Active Development Miro Board (Playground)](https://miro.com/app/board/uXjVNOTPrFo=/)

 
## Contact

Please use this GitHub repository's [Issue tracker](https://github.com/materialdigital/core-ontology/issues) to request new terms/classes or report errors or specific concerns related to the ontology.

Our **Ontology Playground**, organised online **every second Friday from 1-2 pm (CET)**, is a great opportunity to connect with developers and our proactive community to shape the PMDco. Please register via our [mailing list](https://www.lists.kit.edu/sympa/subscribe/ontology-playground?previous_action=info).

## Acknowledgements

This ontology repository was created using the [Ontology Development Kit (ODK)](https://github.com/INCATools/ontology-development-kit).
