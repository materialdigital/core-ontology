# PMDco User Guide 

## How to Develop Your Application Ontologies using PMDco and OBO+ODK Best Practices

Although several guidelines and tutorials for ontology development are available (see Ontology Learning Materials for Beginners), we provide here a dedicated list of recommendations for creating application ontologies based on PMDco, making use of PMD guidance, ontology design patterns, OBO principles, and ODK features.


### 1-	Define the scope and domain of the ontology
-	Clearly define the domain (e.g., materials testing, patient data, food production)
-	Collaborating with the domain experts, specify he use cases or competency questions the ontology should address
-	Determine the target audience (e.g., researchers, software agents, data engineers)
- Formulate a narrow and specific ontology scope according to [OBO principles](https://obofoundry.org/principles/fp-005-delineated-content.html).


### 2-	Decide on the level of detail and sources for terminology collection
-	Determine whether the ontology will cover a broad area at a general level or focus on a specific topic in more detail,
-	Identify reliable sources for terminology and concepts, such as books, scientific publications, domain experts, and relevant standards,
-	Through such resources, identify the essential concepts within your domain,
-	Provide accurate labels and clear definitions for each class (e.g., documented in a spreadsheet).


### 3-	Create an ODK-based ontology repository
-	If you already know ODK, create a GitHub repository for ontology with a reasonable x.yaml file configuration and importing the latest PMDco version,
-	If you don’t know ODK or don’t want to install it, we made a template for you. Simply create your repository following the instructions mentioned in [“application-ontology-template”](https://github.com/materialdigital/application-ontology-template). This template applies the same framework used for PMDco and mirrors PMDco with all its modules.


### 4-	Collaborative ontology development workflow
-	Any person who wants to contribute to the collaborative development of ontology should clone the ODK repository to the local machine,
-	In Protégé, open the editable file: src/ontology/*-edit.owl (Any editor can manage an assigned ID range),
-	Edit the ontology, like add classes/properties, update definitions, and organize axioms,
-	Save and validate locally,
-	Commit your edits and push them to your branch,
-	Create a Pull Request, submit a PR with a short summary and justification of your changes,
-	Team members review; after approval, the PR is merged.


### 5-	Add your desired taxonomy 
-	Edit ontology in protégé, 
-	Create new classes, properties, and individuals according to your terminology lists,
-	Structure them hierarchically in alignment with reused top- and mid-level ontologies, where subclasses inherit properties from their superclasses,
-	Evaluate other OBO Foundry ontologies (e.g., using [Ontobee](https://ontobee.org/)) to check for existing classes and to guide your classification. In the case you want to import entities from other ontologies, please follow the instructions [here](https://oboacademy.github.io/obook/howto/update-import/),
-	Following [OBO principles](https://obofoundry.org/principles/fp-007-relations.html), build the ontology primarily by extending the class hierarchy and minimizing the introduction of new object properties.
-	Add rich annotations for new entities (such as definitions, references, examples, and editorial notes).
-	Include comprehensive ontology annotation metadata (e.g., title, label, description, creators, contributors, version info, previous versions, license, and citation). 


### 6-	Define a richer semantic model with multiple relationship types, rules, and constraints
-	Define logical axioms and property constraints (e.g., domain and range), 
-	Use graphical tools (e.g., Ontopanel or Miro) to visually discuss the modeling issues,
-	Use our [Ontology Design Patterns](https://github.com/materialdigital/core-ontology/tree/main/patterns) as a guideline for the semantic representation of your concepts,
-	Look at [Beginners Guide Miro Board](https://miro.com/app/board/uXjVLY9FwGU=/) and [PMDco3 Miro Board](https://miro.com/app/board/uXjVNOTPrFo=/), where we created lots of use case modeling examples,
-	See other PMDco-based application ontologies (listed below this page) for similar modeling concepts.
-	If you still need support for specific modelling issues, please feel free to mention it in our GitHub [issues](https://github.com/ISE-FIZKarlsruhe/mwo/issues) or [discussion forum](https://github.com/materialdigital/core-ontology/discussions).


### 7-	Ontology evaluation and testing workflow
-	Plan regular meetings with both ontology and MSE domain experts in your project to assess the ontology’s structure, resolve modeling issues, and ensure its logical correctness, 
-	Use ODK evaluation and testing workflows through GitHub Actions Continuous Integration to validate the ontology’s structure, syntax, annotation completeness, and logical consistency,
-	Use reasoning tools (e.g., reasoners HermiT and Pellet) to ensure logical and technical consistency and identify potential redundancies,
-	Analyzes the ontology for common modeling pitfalls, structural issues, and best-practice violations using tools like OOPS! (Ontology Pitfall Scanner!),
-	We will be pleased to invite you to present your ontology in one of our “Ontology Playground meetings” (See Section Who We Are & How to Join)


### 8-	Ontology release, updating, and versioning workflow
-	Use ODK automated workflow for the release process, which follows these steps: running the release with ODK, reviewing the output, merging changes into the main branch, and creating a GitHub release. 
-	Track actively the GitHub issue to gather community feedback, recognize bugs, and identify necessary additions and refinements.
-	Implement a curation process to assess and prioritize updates based on community needs.
-	Employ the robust versioning system hosted on GitHub to ensure clear tracking of changes over time, management of previous versions, and clear tracking of the ontology’s evolution over time.


### 9-	Ontology documentation and publishing
-	Create detailed documentation, including best practices, examples, and guidelines in your ontology GitHub repository.
-	Use [Widoco template](https://github.com/dgarijo/Widoco), a documentation generator for ontologies that automatically produces human-readable HTML documentation including metadata, hierarchies of classes, properties, and annotations,
-	If interested, create [MkDocs](https://www.mkdocs.org/) documentation (like this repository). 
-	If you are using [“application-ontology-template”](https://github.com/materialdigital/application-ontology-template), your ontology is automatically documented in [obofoundary.org](https://obofoundry.org/), 
-	To enhance your ontology accessibility, please also publish your ontology in [MatPortal](https://matportal.org/) and [PMD DataPortal](https://dataportal.material-digital.de/).


## List of Ontologies Developed Based on PMDco V3.x.x:
-	**[Logistic Application Ontology (LOG)](https://github.com/materialdigital/logistics-application-ontology)**
-	**[Vickers Testing Ontology (VTO)](https://github.com/HosseinBeygiNasrabadi/Vickers-testing-application-ontology)**
-	**[Heat Treatment Ontology (HTO)](https://github.com/materialdigital/heat-treatment-application-ontology)**
-	**[Tensile testing Ontology (TTO)](https://github.com/materialdigital/tensile-test-ontology)**
-	**[NFDI MatWerk Ontology (MWO)](https://github.com/ISE-FIZKarlsruhe/mwo)**
-	**[Bio-inspired Meta Materials Ontology (BiMMO)](https://github.com/HosseinBeygiNasrabadi/Bio-inspired-meta-materials-ontology-bimmo)**
-	**[Reference Dataset Ontology for Creep (RDOC)](https://github.com/HosseinBeygiNasrabadi/Reference-dataset-ontology-rdo)**

A [collection of application ontologies](https://github.com/materialdigital/materialdigital1_ontology_collection) was also developed by PMD projects, planned to be integrated with PMDco V3.x.x soon! 
