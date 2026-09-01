# Ontology comparison

## Left (old)
- Ontology IRI: `https://w3id.org/pmd/co/imports/obi_import.owl`
- Version IRI: `https://w3id.org/pmd/co/releases/2026-07-30/imports/obi_import.owl`
- Loaded from: `file:/Users/joerg/Development/pmd/core-ontology/src/ontology/imports/obi_import-2025-12-18.owl`

## Right (new)
- Ontology IRI: `https://w3id.org/pmd/co/imports/obi_import.owl`
- Version IRI: `https://w3id.org/pmd/co/releases/2026-09-01/imports/obi_import.owl`
- Loaded from: `file:/Users/joerg/Development/pmd/core-ontology/src/ontology/imports/obi_import.owl`


### Ontology annotations 
#### Removed
- [Source](http://purl.org/dc/elements/1.1/source) [obi.owl](http://purl.obolibrary.org/obo/obi/2025-12-18/obi.owl) 

- [versionInfo](http://www.w3.org/2002/07/owl#versionInfo) "2026-07-30" 

#### Added
- [Source](http://purl.org/dc/elements/1.1/source) [obi.owl](http://purl.obolibrary.org/obo/obi/2026-07-27/obi.owl) 

- [versionInfo](http://www.w3.org/2002/07/owl#versionInfo) "2026-09-01" 


### data item `http://purl.obolibrary.org/obo/IAO_0000027`

#### Added
- [data item](http://purl.obolibrary.org/obo/IAO_0000027) [definition](http://purl.obolibrary.org/obo/IAO_0000115) "An information content entity that is intended to be one or more truthful statement(s) about something (modulo, e.g., measurement precision or other systematic errors) and is constructed/acquired by a method which reliably tends to produce (approximately) truthful statements."@en 

- [data item](http://purl.obolibrary.org/obo/IAO_0000027) [label](http://www.w3.org/2000/01/rdf-schema#label) "data entity"@en 


### data set `http://purl.obolibrary.org/obo/IAO_0000100`
#### Removed
- [data set](http://purl.obolibrary.org/obo/IAO_0000100) [label](http://www.w3.org/2000/01/rdf-schema#label) "data set"@en 

#### Added
- [data set](http://purl.obolibrary.org/obo/IAO_0000100) [label](http://www.w3.org/2000/01/rdf-schema#label) "homogenous data collection"@en 


### definition `http://purl.obolibrary.org/obo/IAO_0000115`

#### Added
- [definition](http://purl.obolibrary.org/obo/IAO_0000115) [definition](http://purl.obolibrary.org/obo/IAO_0000115) "A property representing the English language definitions of what NCI means by the concept. They may also include information about the definition's source and attribution in a form that can easily be interpreted by software." 

- [definition](http://purl.obolibrary.org/obo/IAO_0000115) [definition](http://purl.obolibrary.org/obo/IAO_0000115) "English language definitions of what NCI means by the concept. These are limited to 1024 characters. They may also include information about the definition's source and attribution in a form that can easily be interpreted by software." 

- [definition](http://purl.obolibrary.org/obo/IAO_0000115) [definition](http://purl.obolibrary.org/obo/IAO_0000115) "The official definition." 


### denoted by `http://purl.obolibrary.org/obo/IAO_0000235`

#### Added
- [denoted by](http://purl.obolibrary.org/obo/IAO_0000235) Range [information content entity](http://purl.obolibrary.org/obo/IAO_0000030) 


### denotes `http://purl.obolibrary.org/obo/IAO_0000219`

#### Added
- [denotes](http://purl.obolibrary.org/obo/IAO_0000219) InverseOf [denoted by](http://purl.obolibrary.org/obo/IAO_0000235) 

- [denotes](http://purl.obolibrary.org/obo/IAO_0000219) Domain [information content entity](http://purl.obolibrary.org/obo/IAO_0000030) 


### has measurement unit label `http://purl.obolibrary.org/obo/IAO_0000039`
#### Removed
- [has measurement unit label](http://purl.obolibrary.org/obo/IAO_0000039) SubPropertyOf: [has part](http://purl.obolibrary.org/obo/BFO_0000051) 

#### Added
- [has measurement unit label](http://purl.obolibrary.org/obo/IAO_0000039) Range [measurement unit label](http://purl.obolibrary.org/obo/IAO_0000003) 


### is quality measurement of `http://purl.obolibrary.org/obo/IAO_0000221`

#### Added
- [is quality measurement of](http://purl.obolibrary.org/obo/IAO_0000221) Domain [measurement datum](http://purl.obolibrary.org/obo/IAO_0000109) 


### label `http://www.w3.org/2000/01/rdf-schema#label`

#### Added
- [label](http://www.w3.org/2000/01/rdf-schema#label) [definition](http://purl.obolibrary.org/obo/IAO_0000115) "A human readable name for this class." 

- [label](http://www.w3.org/2000/01/rdf-schema#label) [label](http://www.w3.org/2000/01/rdf-schema#label) "label"@en 


### part of `http://purl.obolibrary.org/obo/BFO_0000050`

#### Added
- [part of](http://purl.obolibrary.org/obo/BFO_0000050) [label](http://www.w3.org/2000/01/rdf-schema#label) "part of" 

- [part of](http://purl.obolibrary.org/obo/BFO_0000050) InverseOf [has part](http://purl.obolibrary.org/obo/BFO_0000051) 

-  Transitive: [part of](http://purl.obolibrary.org/obo/BFO_0000050) 


### term tracker item `http://purl.obolibrary.org/obo/IAO_0000233`
#### Removed
- [term tracker item](http://purl.obolibrary.org/obo/IAO_0000233) [example of usage](http://purl.obolibrary.org/obo/IAO_0000112) "the URI for an OBI Terms ticket at sourceforge, such as https://sourceforge.net/p/obi/obi-terms/772/"@en 

- [term tracker item](http://purl.obolibrary.org/obo/IAO_0000233) [definition](http://purl.obolibrary.org/obo/IAO_0000115) "An IRI or similar locator for a request or discussion of an ontology term."@en 

#### Added
- [term tracker item](http://purl.obolibrary.org/obo/IAO_0000233) [example of usage](http://purl.obolibrary.org/obo/IAO_0000112) "the URL for an ontology term tracker issue, such as https://github.com/monarch-initiative/mondo/issues/7588"@en 

- [term tracker item](http://purl.obolibrary.org/obo/IAO_0000233) [definition](http://purl.obolibrary.org/obo/IAO_0000115) "A URL for a request or discussion of an ontology term."@en 

- [term tracker item](http://purl.obolibrary.org/obo/IAO_0000233) Range [anyURI](http://www.w3.org/2001/XMLSchema#anyURI) 

