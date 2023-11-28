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
### IRIs
- Classes: UpperCamelCase like rdfs:label [en], example: YourSuperNewTerm; label: Your Super New Term
- Properties: lowerCamelCase like rdfs:label [en], example: yourNewProperty; label: your new property

### Annotation Properties
- rdfs:label: Capitalized for classes, language: en, de
- skos:definition: aristotelian principle definition of the term, language: [en]
- iao:IAO_0000114 (hasCurationStatus) choose according to editing status
- iao:IAO_0000117 (term Editor) your name as responsible person,  format: "PERSON: Firstname Lastname" 

## Additional Annotations
- skos:altLabel for synonyms then also skos:prefLabel has to be set, formating capitalized
- skos:example if possible
- iao:definitionSource when definition is adopted form a resource
- addional translations are welcome
