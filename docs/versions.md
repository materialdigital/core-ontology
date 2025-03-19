# Versions

(TODO: update correct links before release)

## Stable release versions

The latest version of the ontology can always be found at:


[pmdco.owl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/develop-3.0.0/pmdco.owl) and [pmdco.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/develop-3.0.0/pmdco.ttl)


## Variants

The ontology is shipped in three varaints, each as OWL (\*.owl) and Turtle serializations (\*.ttl):

* **full:** [pmdco-full.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/develop-3.0.0/pmdco-full.ttl), [pmdco.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/develop-3.0.0/pmdco.ttl) (default)
* **base:** [pmdco-base.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/develop-3.0.0/pmdco-base.ttl)
* **simple:** [pmdco-simple.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/develop-3.0.0/pmdco-simple.ttl)

The **"full release"** artefact contains all logical axioms, including inferred subsumptions. All imports and components are merged into the full release artefact to ensure easy version management. The full release represents most closely the actual ontology as it was intended at the time of release, including all its logical implications. 

The **"base file"** is a specific release flavour. It reflects the intention of the ontology author for the official (publicly released) representation of the ontologies "base entities". "Base entities" are entities that are defined ("owned") by the ontology. The representation includes the intended public metadata (annotations), and classification (subClassOf hierarchy), including any statements where a base entity is the subject.

The **"simple"** artefact only contains a simple existential graph of the terms defined in the ontology. This corresponds to the state before logical definitions and imports. For example, the only logical axioms are of the form *CL1 subClassOf CL2* or *CL1 subClassOf R some CL3* where *R* is any objectProperty and *CLn* is a class. The simple variant only contains the essential classes and no imports.

The ontology **"main"** file [pmdco.ttl](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/develop-3.0.0/pmdco.ttl) contains the full version.


## Editors' version

Editors of this ontology should use the edit version. From this version all release variants are derived by the build workflows.

Editors version: [src/ontology/pmdco-edit.owl](https://github.com/materialdigital/core-ontology/blob/develop-3.0.0/src/ontology/pmdco-edit.owl)
