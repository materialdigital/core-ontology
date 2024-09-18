![shacl validation](https://github.com/materialdigital/core-ontology/actions/workflows/shacl.yaml/badge.svg?branch=develop-3.0.0)
![pmd-core reasoning](https://github.com/materialdigital/core-ontology/actions/workflows/reasoning.yaml/badge.svg?branch=develop-3.0.0)
![pmd-core reasoning](https://github.com/materialdigital/core-ontology/actions/workflows/qc.yaml/badge.svg?branch=develop-3.0.0)

# The PMD Core Ontology (PMDco) 

This is version v3.0.0alpha of the PMD Core Ontology (PMDco). 

## Introduction

The Platform MaterialDigital core ontology (PMDco) is a mid-level ontology for materials science and engineering (MSE). The PMDco provides bridging mid-level concepts for detailed description of processes, experiments, and computational workflows enabling the reproducibility of process and materials data. These general MSE concepts are designed to be extendable for specific applications within application ontologies. The PMDco is designed in a collaborative effort within the MaterialDigital initiative and intended to be easily used by MSE domain experts.

## Contribute
If you like to contribute, please feel free to add any issues or participate in discussions here on Github.

- Namespace: [https://w3id.org/pmd/co](https://w3id.org/pmd/co)
- Prefix: pmdco
<!---
- [OWL Documentation in HTML](https://w3id.org/pmd/co)
--->
- [Miro Board Documentation](https://miro.com/app/board/uXjVNOTPrFo=/)

Folders: 
 - ```modules```    modules of the PMD ontology
 - ```patterns```    patterns describing the use of the modules and show examples
 - ```shapes```    shapes to describe the sets of conditions and constraints of use formally

The modules depend on the following ontologies:
- Basic formal ontology, http://purl.obolibrary.org/obo/bfo.owl in version http://purl.obolibrary.org/obo/bfo/2020/bfo.owl 
- Relations Ontology RO Core,  http://purl.obolibrary.org/obo/ro/core.owl in version http://purl.obolibrary.org/obo/ro/releases/2023-08-18/core.owl 
- Information artifact ontology, http://purl.obolibrary.org/obo/iao.owl in version http://purl.obolibrary.org/obo/2022-11-07/iao.owl 
- Ontology for Biomedical Investigations, http://purl.obolibrary.org/obo/obi.owl in version http://purl.obolibrary.org/obo/2023-09-20/obi.owl
