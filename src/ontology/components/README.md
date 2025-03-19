# The PMD Core Ontology (PMDco) 

Modules:

 - ```pmdco-materials.owl``` Materials (material types, classes)
 	- describes materials itself using the qualities and characteristics from ```pmdco-qualities.ttl```. 
 - ```pmdco-qualities.owl``` Material Qualities (qualities, dispositions and functions)
 	- "lists of" qualities and characteristics materials, devices, processes, etc. can have.
 - ```pmdco-manufacturing.owl``` Material Manufacturing (transformation)
 	- describes processes related to the transformation of materials
 - ```pmdco-characterization.owl``` Material Characterization (measuring, analysing)
 	- describes processes related to the analysis of materials (e.g. measuring of qualities)	
 - ```pmdco-datatransformation.owl``` Data Transformation (workflows, simulations)
 	- describes processes related to data transformation and data analysis
 - ```pmdco-devices.owl``` Devices
   - "list of" devices related to materials science and engineering	
 - ```pmdco-logistics.owl``` Logistics and general organization
   - describes "logistics" of materials, datasets, and general organization of the domain
 

* Namespace: [https://w3id.org/pmd/co](https://w3id.org/pmd/co)
* Prefix: pmdco


## Mandatory Annotations for Ontology Terms
### IRIs (Internationalized Resource Identifiers)
- IRIs are created folloing the general format: `https://w3id.org/pmd/co/PMD_<local ID>`
- Local ID is a 7 digit number with leading zeros.
- Example: https://w3id.org/pmd/co/PMD_0020098  (Natural Constant)
- When adding a new concept with a new ID, please make sure, to use a new _global_ ID. (In relation to the entire ontology, not only within one module.)



### Classes
- **rdfs:label**: 
  - **Format**: Entitled, singular
  - **Example**: "Your Super New Term"
  - **Language**: Specify languages (e.g.,`en` for English, `de` for German).
- **Processes**: Use Gerund (e.g., `Cutting`)

### Properties
- **rdfs:label**: 
  - **Format**: Natural language lower case
  - **Example**: "your new property"
  - **Language**: Specify languages (e.g.,`en` for English, `de` for German).

### Annotation Properties
- **skos:definition**: 
  - **Content**: Aristotelian principle definition of the term; If B is subclass of A, the definition should have the form "B is an A that ...". 
  - **Language**: `en` for English
- **iao:IAO_0000114 (has curation status)**: Choose according to editing status. 
- **iao:IAO_0000117 (term editor)**: 
  - **Format**: "PERSON: Firstname Lastname" (as responsible person)

## Additional Annotations
- **skos:altLabel**: 
  - Use for synonyms.
  - Ensure skos:prefLabel is also set.
  - **Format**: Capitalized
- **skos:example**: Include examples if possible.
- **iao:IAO_0000119 (definition source)**: 
  - Use when definition is adopted from a resource.
- **iao:IAO_0000412 (imported from)**: 
  - Use when definition is imported from existing ontology concept.
- Additional translations are welcome.

