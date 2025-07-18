# Versions

## Stable release versions

The latest version of the ontology can always be found at:


[pmdco.owl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/pmdco.owl) and [pmdco.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/pmdco.ttl)


## Variants

The ontology is shipped in three varaints, each as OWL (\*.owl) and Turtle serializations (\*.ttl):

* **full:** [pmdco-full.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/pmdco-full.ttl), [pmdco.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/pmdco.ttl) (default)
* **base:** [pmdco-base.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/pmdco-base.ttl)
* **simple:** [pmdco-simple.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/pmdco-simple.ttl)
* **minimal:** [pmdco-minimal.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/pmdco-minimal.ttl)

The **"full release"** artefact contains all logical axioms, including inferred subsumptions. All imports and components are merged into the full release artefact to ensure easy version management. The full release represents most closely the actual ontology as it was intended at the time of release, including all its logical implications. 

The **"base file"** is a specific release flavour. It reflects the intention of the ontology author for the official (publicly released) representation of the ontologies "base entities". "Base entities" are entities that are defined ("owned") by the ontology. The representation includes the intended public metadata (annotations), and classification (subClassOf hierarchy), including any statements where a base entity is the subject.

The **"simple"** artefact only contains a simple existential graph of the terms defined in the ontology. This corresponds to the state before logical definitions and imports. For example, the only logical axioms are of the form *CL1 subClassOf CL2* or *CL1 subClassOf R some CL3* where *R* is any objectProperty and *CLn* is a class. The simple variant only contains the essential classes and no imports.

The **"minimal"** artefact only contains a preselected minimal of the terms defined in the ontology. This set is extracted form the full variant and represents a lightweight subset of the ontology that covers the most essential concepts for basic interoperability and implementation. We recommend beginners to start with this artifact when learning about the ontology (See issue [#121](https://github.com/materialdigital/core-ontology/issues/121)).


The ontology **"main"** file [pmdco.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/pmdco.ttl) contains the full version.


## Editors' version

Editors of this ontology should use the edit versions of the differenet modules. You can find them in the components folder.

Editors component files: [src/ontology/components](https://github.com/materialdigital/core-ontology/blob/main/src/ontology/components)


From the editing main file all release variants are derived by the build workflows.

Editors main file: [src/ontology/pmdco-edit.owl](https://github.com/materialdigital/core-ontology/blob/main/src/ontology/pmdco-edit.owl)


