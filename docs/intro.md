# Introduction to the PMD Ontology (PMDco v3.0.x)  

The **Platform MaterialDigital Core Ontology (PMDco)** is a mid-level ontology specifically developed to support the digital transformation of the Materials Science and Engineering (MSE) domain. With its latest version (v3.0.x), PMDco integrates a modular approach, aligning with the Basic Formal Ontology (BFO) standard to provide a comprehensive and interoperable framework for modeling materials, processes, and data.

## Scope
The **Platform MaterialDigital Core Ontology (PMDco)** is a mid-level semantic framework for **Materials Science and Engineering (MSE)**. Aligning with the ISO/IEC 21838-2:2021 standard, PMDco constructed on basis of *Basic Formal Ontology (BFO)* and reuses several BFO-aligned ontologies like RO, IAO, and OBI. The scope of PMDco follows the fundamental paradigm of MSE (processing, structure, and properties) and encompasses the following domains:

* **Processes:** Representation of MSE-related process chains, including materials manufacturing, characterization, and simulation processes.
* **Structure/state:** Description of substances, engineered materials, and specification of materials, their composition, and multiscale structural features.
* **Properties:** Specification of material properties and qualities, representing processing-structure-properties dependences.

PMDco also provides general entities required for representing the fundamental MSE topics (e.g., thermodynamics), as well as general semantics for entities commonly required across MSE disciplines (such as devices, roles, functions, and plans).


## Objectives  
- **Semantic Interoperability**: Facilitates consistent representation and exchange of materials data across domains and applications by bridging gaps between high-level and domain-specific ontologies.  
- **FAIR Data Principles**: Supports the Findable, Accessible, Interoperable, and Reusable (FAIR) principles, promoting structured data management and reusability.  
- **Workflow Modeling**: Provides tools to describe complex MSE workflows, including manufacturing, characterization, and data transformation processes.  

## Key Features  
1. **Community-Driven Development**: Refined collaboratively in the Ontology Playground sessions with input from MSE experts and practitioners.  
2. **Modular Design**: Organized into distinct modules, such as Materials, Manufacturing, Characterization, Data Transformation, Devices, and Logistics, to cover the entire MSE lifecycle.  
3. **Alignment with Standards**: Built on ISO-compliant BFO and integrates with related ontologies like OBI (Ontology for Biomedical Investigations) and IAO (Information Artifact Ontology).  
4. **Advanced Process Modeling**: Enables detailed representation of processes and their substeps, capturing input/output relationships, device roles, and data transformations.  
5. **Reusability and Extensibility**: Incorporates elements from established ontologies such as QUDT (for units and dimensions) and ChEBI (for chemical entities), ensuring broad applicability and cross-domain connectivity.

## Applications  
- **Material Specifications**: Models material properties and specifications, ensuring compliance with established standards (e.g., European Steel Grades).  
- **Process Chains**: Captures the sequence of interconnected processes, such as transforming a steel sheet into test pieces, performing tensile tests, and analyzing resulting data.  
- **Data Integration and Analysis**: Supports the transformation of raw data (e.g., time series) into derived material properties like elastic modulus, fostering reproducibility and transparency.  
- **Device and Function Modeling**: Links devices (e.g., forming machines) to their specifications and roles within processes, ensuring traceability and compliance.


## Competency questions
To ensure the ontology captures the knowledge we need and supports the right queries, we defined a set of competency questions. These are practical, user-focused questions that the ontology should be able to answer once complete. They guide the development process and later serve as a benchmark to check whether the ontology meets its goals. Examples of these competency questions include:

- **Materials state/structure**:
	- What is the identifier X of material Y?
	- What is the chemical composition of material X?
	- What are the constituent substances of composite material X?
	- Which engineered materials are specified for property X?
	- Which specifications describe material X (e.g., standard references, certifications)?
	- What microstructural features (e.g., grain size, phase) are observed in material X?
	- How does the microstructure of material X change after processing step Y?
	- Which phases are present in alloy X under condition Y?
	- What is the relationship between microstructural feature X and property Y?
- **Process**:
	- Which processing steps were applied to material X during manufacturing?
	- What is the sequence of processes in workflow X?
	- Which characterization processes were performed on sample X?
	- What simulation processes have been conducted to predict property X of material Y?
- **Properties**:
	- What are the mechanical properties of material X (e.g., tensile strength, hardness)?
	- How does property X of material Y vary with parameter Z (e.g., temperature, pressure)?
	 Which instruments or devices were used in process X?
