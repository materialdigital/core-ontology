# The PMD Core Ontology (PMDco) 

This is version v2.0.5 of the PMD Core Ontology (PMDco). 

Files: 
 - ```pmd_core.ttl```    core version of the PMD ontology
 - ```pmd_bfo_adapter.ttl```     mappings to information artifact ontolgy (IAO) and basic formal ontology (BFO). 

If you like to contribute, please feel free to add any issues or participate in discussions here on Github.

* Namespace: [https://w3id.org/pmd/co](https://w3id.org/pmd/co)
* Prefix: pmdco
* [OWL Documentation in HTML](https://w3id.org/pmd/co) 
* [Miro Board Documentation](https://miro.com/app/board/uXjVPn5wGiA=)

# Application Ontologies 

* PMDco related [modules and application ontologies](https://github.com/materialdigital/application-ontologies)

## Introduction
The Platform MaterialDigital core ontology (PMDco) is a lightweight mid-level ontology for materials science and engineering (MSE). The PMDco provides bridging mid-level concepts for detailed description of processes, experiments, and computational workflows enabling the reproducibility of process and materials data. These general MSE concepts are designed to be extendable for specific applications within application ontologies. The PMDco is designed in a collaborative effort within the MaterialDigital initiative and intended to be easily used by MSE domain experts.

### Starting example: Boiling an egg
Lets start with an easy example of represent the process of boiling an raw egg using an egg boilingmachine.

In the schematic the EggBoilingProcess is introduced as a subclass of the pmd:Process. The RawEgg as a subclass of pmd:Object is input to this process. The BoiledEgg, also a subclass of pmd:Object is the output of this process.

![](https://matdig.uni-leipzig.de/hedgedoc/uploads/upload_d406a929cd83400c7b576251b1e49990.png)

The EggBoilingProcess is exectuded by an EggBoilingMachine that is introduced as a subclass of pmd:ProcessingNode.

![](https://matdig.uni-leipzig.de/hedgedoc/uploads/upload_9d01144b9fcde0645cfbf0a4a2a88bbc.png)

In order to represent the duration of the process, pmd:Duration is reused from the PMDco has an input for the EggBoilingProcess.

![](https://matdig.uni-leipzig.de/hedgedoc/uploads/upload_d5871057e22ba8ec280f572c78233a9a.png)
