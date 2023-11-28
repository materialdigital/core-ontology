# The PMD Core Ontology (PMDco) 

Modules:

 - ```pmdco-materials.ttl``` Materials (material types, classes)
 	- describes materials itself using the qualities and characteristics from ```pmdco-qualities.ttl```. 
 - ```pmdco-qualities.ttl``` Material Qualities (qualities, dispositions and functions)
 	- "lists of" qualities and characteristics materials, devices, processes, etc. can have.
 - ```pmdco-manufacturing.ttl``` Material Manufacturing (transformation)
 	- describes processes related to the transformation of materials
 - ```pmdco-characterization.ttl``` Material Characterization (measuring, analysing)
 	- describes processes related to the analysis of materials (e.g. measuring of qualities)	
 - ```pmdco-datatransformation.ttl``` Data Transformation (workflows, simulations)
 	- describes processes related to data transformation and data analysis
 - ```pmdco-devices.ttl``` Devices
   - "list of" devices related to materials science and engineering	
 - ```pmdco-logistics.ttl``` Logistics and general organization
   - describes "logistics" of materials, datasets, and general organization of the domain
 

* Namespace: [https://w3id.org/pmd/co](https://w3id.org/pmd/co)
* Prefix: pmdco


## Mandatory Annotations for Ontology Terms
### IRIs (Internationalized Resource Identifiers)
- Ensure unique and persistent IRIs for each term

### Classes
- **Naming Convention**: Use UpperCamelCase (e.g., `YourSuperNewTerm`).
- **rdfs:label**: 
  - **Format**: Capitalized
  - **Example**: "Your Super New Term"
  - **Language**: Specify languages (e.g., `en`, `de`).

### Properties
- **Naming Convention**: Use lowerCamelCase (e.g., `yourNewProperty`).
- **rdfs:label**: 
  - **Format**: Natural language
  - **Example**: "your new property"
  - **Language**: Specify languages (e.g.,`en` for English, `de` for German).

### Annotation Properties
- **rdfs:label**: 
  - **For Classes**: Capitalized
  - **Language**: Specify languages (e.g.,`en` for English, `de` for German).
- **skos:definition**: 
  - **Content**: Aristotelian principle definition of the term
  - **Language**: `en` (English)
- **iao:IAO_0000114 (has curation status)**: Choose according to editing status.
- **iao:IAO_0000117 (term editor)**: 
  - **Format**: "PERSON: Firstname Lastname" (as responsible person)

### Additional Annotations
- **skos:altLabel**: 
  - Use for synonyms.
  - Ensure skos:prefLabel is also set.
  - **Format**: Capitalized
- **skos:example**: Include examples if possible.
- **iao:definitionSource**: 
  - Use when definition is adopted from a resource.
- Additional translations are welcome.
