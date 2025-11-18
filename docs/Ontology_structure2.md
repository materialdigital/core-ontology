# Ontology Structure


## Modularization
Modules in ontology are formally defined, self-contained, and reusable fragments of an ontology that represent specific conceptual subdomains. They are engineered to support logic-based reasoning, interoperability, and tractable querying, allowing large or complex ontologies to be efficiently developed, understood, and maintained by dividing them into coherent, manageable parts. These modules make it possible to approach ontology engineering in a divide-and-conquer manner, facilitating reuse and integration across different domains and applications. PMDco defines six primary modules central to MSE, naming material, material qualities, material manufacturing, material characterization, data transformation, and devices. 

Furthermore, in ODK-based ontology modularization, modules such as import-edit, shared, and axioms-shared play distinct roles. The import-edit module contains external ontology terms and their logical extensions, supporting controlled editing and updates without manual changes to the imported content. The shared module aggregates terms or patterns that must be reused across different ontology parts, promoting interoperability between collections. The axioms-shared module collects logical axioms that are common and essential for reasoning across modules, ensuring consistency and coordination within the ontology system. As seen in below figure, PMDco is eventually created by unifying all mentioned ontology modules.

<img width="1407" height="384" alt="Screenshot 2025-11-17 at 11 37 59" src="https://github.com/user-attachments/assets/d647e9b7-b0dc-44ea-ba87-7964ae9f7e53" />
 
PMDco V3.x.x modularization

In a modularized ontology, key concepts such as classes and object properties are organized into distinct modules that capture specific domains or subdomains. Each module contains related classes, which denote the core concepts of the domain, along with their corresponding object properties, which describe relationships between these concepts and other entities. This structure allows for targeted development and maintenance, where groups of interrelated classes and properties can be managed, reused, and evolved independently while supporting interoperability through well-defined module boundaries. 

The complete list of PMDco classes, object properties, data properties, annotation properties and individuals can be found in the [Widoco](https://materialdigital.github.io/core-ontology/) documentation page. 

The following section provide example concepts related to different ontology modules.


## Classes

**1. Materials module**

This category includes fundamental entities that represent physical materials, independent of their shape, and their compositional relationships.

<img width="321" height="527" alt="image" src="https://github.com/user-attachments/assets/4757e92c-9b9b-4509-ad59-a04aa595d008" />


Examples:

``bfo:material entity`` – the main superclass for materials and objects from BFO.

``chebi:chemical entity`` - contains all the periodic elements imported from CHEBI ontology.

``pmd:Connected Material Entity Aggregate`` – A mereological sum of separate material entities, which adhere to one another through chemical bonds or physical junctions that go beyond gravity. <br/>
Examples: the atoms of a molecule, the molecules forming the membrane of a cell, the epidermis in a human body.

``pmd:Disonnected Material Entity Aggregate``  – A mereological sum of scattered (i.e. spatially separated) material entities, which do not adhere to one another through chemical bonds or physical junctions but, instead, relate to one another merely on grounds of metric proximity. The material entities are separated from one another through space or through other material entities that do not belong to the group. <br/> Examples: a heap of stones, a colony of honeybees, a group of synapses.

``pmd:Material`` – A Portion Of Matter that may participate in some Manifacturing Process and whose shape is not relevant for its participation in the Manifacuring Process.

Some concrete materials definitions:

``pmd:Metal`` - A metal is an engineered material representing a class of materials characterized by high electrical and thermal conductivity, ductility, and metallic bonding.

``pmd:Ceramics`` - Ceramics are engineered materials described as non-metallic, inorganic materials characterized by high hardness, brittleness, and heat resistance, commonly used in engineering applications.


**2. Qualities module**

Material qualities define the intrinsic and extrinsic properties of materials that determine their behavior and usability in various applications.

<img width="257" height="421" alt="image" src="https://github.com/user-attachments/assets/a6419778-a2dc-46e6-973f-50806c017c95" />


Main BFO superclasses:

``bfo:quality`` – A quality is a specifically dependent continuant that, in contrast to roles and dispositions, does not require any further process in order to be realized

``bfo:realizable entity`` - A specifically dependent continuant  that inheres in continuant  entities and are not exhibited in full at every time in which it inheres in an entity or group of entities. The exhibition 
or actualization of a realizable entity is a particular manifestation, functioning or process that occurs under certain circumstances.

Examples from PMD:

``pmd:Extensive Quality`` - A quality that inheres in only object or object aggregate or fiat object part or chemical entity and is dependent on the bearers (system-) size.

  - Examples: 

  - ``Pmd:Mass`` - A quality that inheres in an object, object aggregate or fiat object part and affects those in processes where gravitation, acceleration, thermal mass etc are relevant.

  - ``Pmd:Energy`` - A quality of material entities which manifests as a capacity to perform work (such as causing motion or the interaction of molecules)

``pmd:Intensive Quality`` - A qualty that inheres in only portion of matter and thus is independent of the bearers (system-) size.

  - Examples: 

  - ``pmd:Chemical Composition`` - A morphological quality describing the types and proportions of elements or compounds present in a material.

  - ``pmd:Defect Density`` - A morphological quality describing the number of defects per unit volume or area in a material, which can affect its mechanical and electronic properties.

``pmd:Behavioral Material Property`` - A material trait in terms of the kind and magnitude of response to a specific imposed stimulus. Generally, definitions of properties are made independent of material shape and size.

  - Examples: 

  - ``pmd:Hardness`` – A measure of a material’s resistance to deformation or indentation.

  - ``pmd:Morphological property`` – A material property representing the characteristics of a material's structure, such as shape, size, and distribution of its features.


**3. Manufacturing module** 

This category encompasses various processes and devices involved in the transformation of raw materials into finished products or components.

<img width="296" height="474" alt="image" src="https://github.com/user-attachments/assets/75559de5-2d35-48e6-bb4b-0488f17ef8b2" />


The superclass for industrial processes:

``pmd:Manufacturing Process`` - A planned process that is driven by the primary intent to transform objectsA manufacturing process is always a transformative process.

More specific examples:

``pmd:Coating`` – A manufacturing process that aims to deposit a permanently adhering layer of a material without a form onto a workpiece, whereby the immediate state of the coating material directly before 
application is essential.

``pmd:Forming`` - A manufacturing process that changes the shape of a solid body through plastic deformation while retaining both mass and structural integrity.

``pmd:Joining`` - A manufacturing process that enables the continuous bonding or joining of two or more workpieces with a specific, fixed shape or of such workpieces with a shapeless material, whereby the cohesion 
is created at specific points and reinforced overall.

**4. Material characterization module** 

Material characterization involves methods and devices used to analyze the physical, mechanical, and chemical properties of materials.

<img width="276" height="443" alt="image" src="https://github.com/user-attachments/assets/f7b3aa6c-ab41-41af-83e1-c83a76dec822" />


Main BFO superclass:

``bfo:process`` - p is a process means p is an occurrent that has some temporal proper part and for some time t, p has some material entity as participant

The superclass for characterization processes:

``obi:Assay`` - A planned process that has the objective to produce information about a material entity (the evaluant) by examining it. 

More specific examples:

``pmd:Acoustical Property Analyzing Process`` - An assay that measures the acoustic properties of materials by analyzing how sound waves interact with the material. This process involves generating sound waves and observing their reflection, transmission, absorption, or scattering to determine properties such as acoustic impedance, absorption coefficient, and sound speed.

``pmd:Mechanical Property Analyzing Process`` - An assay that evaluates the mechanical characteristics of materials, such as strength, hardness, elasticity, and tensile properties, often through tests that measure response to forces and loads.

``pmd:Tensile Testing Process`` – A Mechanical Property Analyzing Process that determines a material's response to tensile forces, measuring its tensile strength, elongation, and Young's modulus.

**5. Data transformation module** 

This category includes processes that involve computational simulations and digital transformations related to material properties and behaviors.

<img width="287" height="460" alt="image" src="https://github.com/user-attachments/assets/4662af0a-cde3-465c-a63a-b573ea20605e" />


``pmd:Computing Process`` - A planned process that involves the systematic use of computational methods and tools to perform simulations, analyses, or data transformations to achieve specific scientific or 
engineering goals.

``pmd:Simulation Process`` - A Computing Process that models the behavior of a system over time using mathematical or computational techniques.

``pmd:Monte Carlo Simulation`` - A Simulation Process that uses random sampling to solve physical and mathematical problems.

**6. Devices module**

This category includes devices performing certain functions in industrial processes.

<img width="351" height="564" alt="image" src="https://github.com/user-attachments/assets/f5063956-e3b6-47f6-ab4e-cff8556d1acc" />


Main BFO superclass:

``bfo:object`` - An object is a material entity which manifests causal unity & is of a type instances of which are maximal relative to the sort of causal unity manifested.

Examples:

``pmd:Device`` - A physical or virtual entity used to perform a specific function or task, often involving measurement, manipulation, or analysis of materials.

``pmd:Furnace`` - An enclosed structure in which heat is produced (as for heating a house or for reducing ore).

``pmd:Creep Testing Device`` - A device used to test the creep behavior of materials under constant stress at high temperatures.


## Object Properties
While most of PMDco object properties are driven from ro, bfo, iao and obi, many object properties also defined to represents more specific MSE relations. A portion of PMDco object properties hierarchy is shown here. As examples, we also introduced some object properties below:
 
<img width="329" height="528" alt="image" src="https://github.com/user-attachments/assets/0c384fca-4c65-44ad-9601-7511ed79156a" />


``bfo:realizes`` – A relation between a process b and realizable entity c such that c inheres in some d & for all t, if b has participant d then c exists & the type instantiated by b is correlated with the type instantiated by c.

``ro:concretizes`` – A relationship between a specifically dependent continuant or process and a generically dependent continuant, in which the generically dependent continuant depends on some independent continuant in virtue of the fact that the specifically dependent continuant or process also depends on that same independent continuant. Multiple specifically dependent continuants or processes can concretize the same generically dependent continuant.

``iao:denotes`` – A primitive, instance-level, relation obtaining between an information content entity and some portion of reality. Denotation is what happens when someone creates an information content entity E in order to specifically refer to something. The only relation between E and the thing is that E can be used to 'pick out' the thing. This relation connects those two together. Freedictionary.com sense 3: To signify directly; refer to specifically.

``obi:has value specification`` – A relation between an information content entity and a value specification that specifies its value.

``pmd:consist of`` – A continuant part property that relates Material Entity Aggregates in the direction of smaller length-scale.

``pmd:intracts with`` – A relation between participants of a process indicating that some of the participants SDCs are affected during the process due to the interaction of the participants.

``pmd:stimulates`` – A relation between a stimulating process and material property, where there is some material entity that is bearer of the material property and participates in the stimulating process, and the material property comes to be realized in the course of the stimulating process.

Note that PMDco uses specific constraints and rules to ensure logical consistency and facilitate accurate data representation within the ontology:
-	**Property characteristics**: Ontology properties have several key characteristics that define their behavior and impact reasoning. Properties can be functional, meaning each individual has at most one value for a property. They may be inverse functional, so each value points to at most one individual. Properties can also be transitive, allowing chains of relationships to infer new ones, or symmetric, meaning relationships go both ways between individuals. Other characteristics include asymmetric (relationships do not reverse), reflexive (every individual relates to itself), and irreflexive (no individual relates to itself). These characteristics are essential for accurately modeling domain relationships and constraints in ontologies.
-	**Cardinality Constraints**: the number of times a property can be associated with a class. For example, a Manufacturing Process may be constrained to have some material entity as input using the has_specified_input property.
-	**Domain and Range Specifications**: Define the applicable classes for properties. For example, the stimulates property (subproperty of realizes) has a domain of Stimulating Process and a range of Material Property.


## Data Properties

``iao:has measurement value`` –

``obi:has specified value`` – A relation between a value specification and a literal.

``pmd:has value`` – Data property that relates an information content entity to a literal


## Annotation properties
PMDco employs annotations to enrich classes and properties with metadata and human readable information, enhancing clarity and usability. This information may be provided in different natural languages (e.g., English and German).

- **Labels** | ***rdfs:label***: Provide human-readable names for ontology elements.
- **Comments** | ***rdfs:comment***: Offer detailed descriptions, usage notes, clarifications of definitions, or additional relevant information. They may enhance the understanding of the terms regarded.
- **Definitions** | ***skos:definition***: Delivers formal, human readable explanations and descriptions of classes and properties. Preferably, [Aristotelian definitions](#aristotelian-definition) are used that support in finding subclass relationships.
- **Definition Source** | ***obo:IAO_0000119***: If the definition was obtained from a specific source (e.g., a well-known work from the field of MSE, a dictionary, or a URI/URL), this is specified as definition source, also citing the original document.

As examples, the annotation for ``pmd:Material`` class and ``ro:has quality`` object property are shown in below figures:

<img width="467" height="279" alt="image" src="https://github.com/user-attachments/assets/3a4c1d14-1282-4944-b36b-d9838830984c" />

<img width="464" height="201" alt="image" src="https://github.com/user-attachments/assets/33e1629b-7a65-4c44-a360-9d018a542918" />

-	Note that, for providing the definitions in PMDcore ontology we follow the [Aristotelian](https://www.merriam-webster.com/dictionary/Aristotelian) principle. An aristotelian definition typically refers to defining something by its genus (general category) and differentia (specific characteristics that distinguish it from other members of the same genus), that should be expressed in the concepts defined in the ontology. 

## Individuals
While PMDco serves as a mid-level ontology and may not define specific instances, it provides a framework for users to instantiate individuals pertinent to their domain. Therefore, it mostly does not contain individuals in its pure form. <br/>
The only individuals present in the PMDco are the ones belonging to the subclasses of a ``pmd:Nature Constant`` class, defined in the Qualities module: <br/>
``pmd:Aggregate State Value`` - solid, liquid, etc. <br/>
``pmd:Bravias Lattice (3D)`` - cubic body-centered, monoclinic primitive, etc. <br/>
``pmd:Metallic Grain Structures`` - austenite, ferrite, etc.
