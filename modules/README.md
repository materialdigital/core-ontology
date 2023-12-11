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
  - **Language**: Specify languages (e.g.,`en` for English, `de` for German).

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
  - **Language**: `en` for English
- **iao:IAO_0000114 (has curation status)**: Choose according to editing status.
- **iao:IAO_0000117 (term editor)**: 
  - **Format**: "PERSON: Firstname Lastname" (as responsible person)

### Additional Annotations
- **skos:altLabel**: 
  - Use for synonyms.
  - Ensure skos:prefLabel is also set.
  - **Format**: Capitalized
- **skos:example**: Include examples if possible.
- **iao:IAO_0000119 (definition source)**: 
  - Use when definition is adopted from a resource.
- Additional translations are welcome.


## PMDco-Qualities features

- subclass hierarchy to [bfo:Quality](http://purl.obolibrary.org/obo/BFO_0000019) categorizing to biological, chemical, pyhsical and performance qualities 
- a lot of mechanical qualities as subclasses of morphological quality
- reuse of pato size, shape, texture, structure, color, odor and spatial pattern as morphological qualities (curate_qualities.ipynb)
- reuse of organismal qualities and cellular qualities as subclass of biological quality  (curate_qualities.ipynb)
- translations to german for 856 trough text-davinci-003 model (curate_qualities.ipynb), and personally revised

curently 991, terms 857 [pato](https://obofoundry.org/ontology/pato.html) terms referenced with [Imported From](http://purl.obolibrary.org/obo/IAO_0000412)