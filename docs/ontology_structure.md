# Ontology Structure
<!--@Document_indicator: Text,links -->
## BFO as top level ontology

The Basic Formal Ontology (BFO) is a **top-level ontology** that provides a structured framework for organizing entities based on their fundamental nature. It does not include domain-specific content but instead defines **high-level categories** that support the development of specialized ontologies like NFDIcore.  

BFO distinguishes entities based on whether they persist through time or unfold over time, dividing them into **continuants** and **occurrents**.  

### **Continuants (Endurants)**  
Continuants are entities that **exist at any given moment in time** and maintain their identity over time. There are tree kinds of continuants: *independent* continuants, *generically dependent* continuants and *specifically dependent* continuants.

#### **Independent Continuants (IC)**  
These are entities that **exist independently** and do not require another entity to exist.  

- **Material Entities** – Physical objects with spatial extension.  
  - *Examples*: Organisms, buildings, tools.  
- **Immaterial Entities** – Boundaries or parts of objects defined by human convention.  
  - *Examples*: The equator, the upper half of a sphere.  

#### **Generically Dependent Continuants (GDC)**  
These entities **depend on independent continuants** for their existence.  
Generically dependent continuants can exist in multiple instances or be replicated across different locations. 

- *Examples*:
	- A book’s content (as opposed to a single physical copy of the book)  
	- A software program (which can be installed on multiple computers)  
	- A musical composition (which can be played on different instruments)   
	- A dataset and data items
	- Entities with information content

#### **Specifically Dependent Continuants (SDC)**  
Specifically dependent continuants are **qualities, roles, or dispositions** that **exist only in relation to a particular independent continuant**. They cannot exist independently and must always be **inherent in something else**.  

  
- **Qualities**  - Intrinsic properties of an independent continuant. They describe **how an entity is** at any moment in time.  

	- *Examples*: The color of a leaf, the weight of a person, the temperature of a liquid.

- **Roles** - Situational properties that an entity has **based on context or social convention**.  

	- *Examples*: The role of a teacher, he status of a patient in a hospital, the role of a machine undergoing maintenance.

- **Dispositions and functions** - Potential behaviors or tendencies that an entity has, even if they are not currently being realized. Functions are dispositions that represent the particular purpose of something.

	- *Examples*: The fragility of glass (it might break if dropped), the solubility of salt (it dissolves in water), a person’s ability to speak multiple languages, the function of an oven to heat something up, the function of a screwdriver to turn screws in and out.


### **Occurrents (Perdurants)**  
An occurrents is an **entity that unfolds itself in time** or it is the start or end of such an entity.

#### **Processes**  
Processes are dynamic activities with temporal duration.  

- *Examples*: A running event, a chemical reaction, cell division.  

#### **Temporal Regions**  
These represent divisions of time.  

- *Examples*: A second, an hour, a historical period.  

#### **Spatiotemporal Regions**  
These combine space and time into a single entity.  

- *Examples*: The path of a moving object, the trajectory of a planet.  



### **Relations in BFO**  
BFO defines formal **relationships** between entities to maintain consistency. Some key relations include:  


- **continunat part of** – Indicates compositional relationships. (*Example: A wheel is part of a car.*) 
- **occurent part of** - Some process has another process as part. (*Example: A conference event has multiple workshop events.*)
- **located in** – Specifies spatial containment. (*Example: A book is located_in a library.*)  
- **bearer of** – Assigns specifically dependent continuants to independent continuants. (*Example: A teacher is the bearer of the educator role.*)  
- **has participant** - Assigns continuants to processes. (*Example: A student participates a lecture event.*)


More information about BFO can be found at the [GitHub repo](https://github.com/bfo-ontology/BFO-2020) and the [documentation page](https://basic-formal-ontology.org/bfo-2020.html). 
 




## Key Components of PMDco

PMDco follows a classical ontology development approach, incorporating classes, object properties, data properties, individuals, and annotations to define and structure domain knowledge. All elements are categorized in the BFO hierarchy. 


### Classes

PMDco defines several primary categories central to materials science and engineering (MSE). These categories provide a structured ontology for representing materials, their properties, processes, and associated devices. The ontology is made of modules, representing categories of the MSE concepts:

![image (1)](https://github.com/user-attachments/assets/578d42b1-27dd-4f4c-83cc-513d827f1192)

We provide a few examples from each category below:

**1. Materials module**: This category includes fundamental entities that represent physical materials, independent of their shape, and their compositional relationships.

Examples:

``bfo:material entity`` – the main superclass for materials and objects from BFO.

``chebi:chemical entity`` - contains all the periodic elements imported from CHEBI ontology.

``pmd:Connected Material Entity Aggregate`` – A mereological sum of separate material entities, which adhere to one another through chemical bonds or physical junctions that go beyond gravity. <br/>
Examples: the atoms of a molecule, the molecules forming the membrane of a cell, the epidermis in a human body.

``pmd:Disonnected Material Entity Aggregate``  – A mereological sum of scattered (i.e. spatially separated) material entities, which do not adhere to one another through chemical bonds or physical junctions but, instead, relate to one another merely on grounds of metric proximity. The material entities are separated from one another through space or through other material entities that do not belong to the group. <br/> Examples: a heap of stones, a colony of honeybees, a group of synapses.

``pmd:Material`` – A Portion Of Matter that may participate in some Manifacturing Process and whose shape is not relevant for its participation in the Manifacuring Process.

Some concrete materials definitions:

pmd:Metal - A metal is an engineered material representing a class of materials characterized by high electrical and thermal conductivity, ductility, and metallic bonding.

pmd:Ceramics - Ceramics are engineered materials described as non-metallic, inorganic materials characterized by high hardness, brittleness, and heat resistance, commonly used in engineering applications.

**2. Qualities module**: Material qualities define the intrinsic and extrinsic properties of materials that determine their behavior and usability in various applications.

Main BFO superclasses:

``bfo:quality`` – A quality is a specifically dependent continuant that, in contrast to roles and dispositions, does not require any further process in order to be realized

``bfo:realizable entity`` - A specifically dependent continuant  that inheres in continuant  entities and are not exhibited in full at every time in which it inheres in an entity or group of entities. The exhibition 
or actualization of a realizable entity is a particular manifestation, functioning or process that occurs under certain circumstances.

Examples from PMD:

``pmd:Morphologic Quality`` - A morphological quality is a material entity that represents the characteristics related to the shape, size, and structure of a material's features.

``pmd:Material Property`` - A property is a material trait in terms of the kind and magnitude of response to a specific imposed stimulus. Generally, definitions of properties are made independent of material shape 
and size.

Some concrete properties:

``pmd:Hardness`` – A measure of a material’s resistance to deformation or indentation.

``pmd:Yield Strength`` – The stress at which a material transitions from elastic to plastic deformation.

**3. Manufacturing module**: This category encompasses various processes and devices involved in the transformation of raw materials into finished products or components.

The superclass for industrial processes:

``pmd:Manufacturing Process`` - A planned process that is driven by the primary intent to transform objectsA manufacturing process is always a transformative process.

More specific examples:

``pmd:Coating`` – A manufacturing process that aims to deposit a permanently adhering layer of a material without a form onto a workpiece, whereby the immediate state of the coating material directly before 
application is essential.

``pmd:Forming`` - A manufacturing process that changes the shape of a solid body through plastic deformation while retaining both mass and structural integrity.

``pmd:Joining`` - A manufacturing process that enables the continuous bonding or joining of two or more workpieces with a specific, fixed shape or of such workpieces with a shapeless material, whereby the cohesion 
is created at specific points and reinforced overall.

** 4. Material Characterization**: Material characterization involves methods and devices used to analyze the physical, mechanical, and chemical properties of materials.

Main BFO superclass:

``bfo:process`` - p is a process means p is an occurrent that has some temporal proper part and for some time t, p has some material entity as participant

The superclass for characterization processes:

``pmd:Assay`` - A planned process that has the objective to produce information about a material entity (the evaluant) by examining it. (Imported from OBI ontology)

More specific examples:

``pmd:Acoustical Property Analyzing Process`` - An assay that measures the acoustic properties of materials by analyzing how sound waves interact with the material. This process involves generating sound waves and observing their reflection, transmission, absorption, or scattering to determine properties such as acoustic impedance, absorption coefficient, and sound speed.

``pmd:Mechanical Property Analyzing Process`` - An assay that evaluates the mechanical characteristics of materials, such as strength, hardness, elasticity, and tensile properties, often through tests that measure response to forces and loads.

``pmd:Tensile Testing Process`` – A Mechanical Property Analyzing Process that determines a material's response to tensile forces, measuring its tensile strength, elongation, and Young's modulus.

**5. Data Transformation module**: This category includes processes that involve computational simulations and digital transformations related to material properties and behaviors.

Main BFO superclass:

``bfo:process`` - p is a process means p is an occurrent that has some temporal proper part and for some time t, p has some material entity as participant

Examples:

``pmd:Computing Process`` - A planned process that involves the systematic use of computational methods and tools to perform simulations, analyses, or data transformations to achieve specific scientific or 
engineering goals.

``pmd:Simulation Process`` - A Computing Process that models the behavior of a system over time using mathematical or computational techniques.

``pmd:Monte Carlo Simulation`` - A Simulation Process that uses random sampling to solve physical and mathematical problems.

**6. Devices module**: This category includes devices performing certain functions in industrial processes.

Main BFO superclass:

``bfo:object`` - An object is a material entity which manifests causal unity & is of a type instances of which are maximal relative to the sort of causal unity manifested.

Examples:

``pmd:Device`` - A physical or virtual entity used to perform a specific function or task, often involving measurement, manipulation, or analysis of materials.

``pmd:Furnace`` - An enclosed structure in which heat is produced (as for heating a house or for reducing ore).

``pmd:Creep Testing Device`` - A device used to test the creep behavior of materials under constant stress at high temperatures.


### Properties
PMDco includes properties that define relationships and attributes:

- **Object Properties**:
  - **stimulates**: A relation between a stimulating process and material property, where there is some material entity that is bearer of the material property and participates in the stimulating process, and the material property comes to be realized in the course of the stimulating process.
  - **interacts with**: A relation between participants of a process indicating that some of the participants SDCs are affected during the process due to the interaction of the participants.
  - **consists of**: A continuant part property that relates Material Entity Aggregates in the direction of smaller length-scale.

- **Data Properties**:
  - **has specified value**: Assigns a specific value to a property, such as a numerical measurement.
  - **has unit**: Specifies the unit of measurement for a given value.

### Individuals
While PMDco serves as a mid-level ontology and may not define specific instances, it provides a framework for users to instantiate individuals pertinent to their domain. Therefore, it mostly does not contain individuals in its pure form. <br/>
The only individuals present in the PMDco are the ones belonging to the subclasses of a ``pmd:Nature Constant`` class, defined in the Qualities module: <br/>
``pmd:Aggregate State Value`` - solid, liquid, etc. <br/>
``pmd:Bravias Lattice (3D)`` - cubic body-centered, monoclinic primitive, etc. <br/>
``pmd:Metallic Grain Structures`` - austenite, ferrite, etc.

## Hierarchy
PMDco presents a structured taxonomy with parent-child relationships among classes (class/subclass-relations). This hierarchical structure facilitates organized data representation and promotes interoperability across MSE domains.

Some Examples visualized in Protege provided below.

**Characterization processes taxonomy:**

![tax_char](https://github.com/user-attachments/assets/aece6cdc-5639-43d0-b25f-19aba9400bca)

**Materials taxonomy:**

![tax_mater](https://github.com/user-attachments/assets/fc9530d7-db9a-4a87-b8b1-0681569c6b89)

**Taxonomy of material properties:**

![tax_qualities](https://github.com/user-attachments/assets/b2cfc656-47b0-4a6b-93cc-a18835513379)

**Taxonomy of physical processes:**

![tax_qualproc](https://github.com/user-attachments/assets/f45a1669-4018-4fdd-ba0a-651704714389)



## Annotations
PMDco employs annotations to enrich classes and properties with metadata and human readable information, enhancing clarity and usability. This information may be provided in different natural languages (e.g., English and German).

- **Labels** | ***rdfs:label***: Provide human-readable names for ontology elements.
- **Comments** | ***rdfs:comment***: Offer detailed descriptions, usage notes, clarifications of definitions, or additional relevant information. They may enhance the understanding of the terms regarded.
- **Definitions** | ***skos:definition***: Delivers formal, human readable explanations and descriptions of classes and properties. Preferably, [Aristotelian definitions](#aristotelian-definition) are used that support in finding subclass relationships.
- **Definition Source** | ***obo:IAO_0000119***: If the definition was obtained from a specific source (e.g., a well-known work from the field of MSE, a dictionary, or a URI/URL), this is specified as definition source, also citing the original document.

**Example Annotations**:

The class **Material** has the following annotations:

``rdfs:label:`` "Material"@en <br/>
``rdfs:label:`` "Material"@de <br/>
``rdfs:comment:`` "Instances of Portions Of Matter whose shape is relevant for their dispostion to participate in a Manufacturing Process may be SemiFinishedProdcuts." <br/>
``skos:definition:`` "A Material is a Portion Of Matter that has the disposition to participate in some Manifacturing Process and whose shape is not relevant for its disposition to participate in the Manifacuring Process." <br/>
``obo:IAO_0000119:`` "Defined in accordance with standard materials science literature." <br/>
``rdfs:isDefinedBy:`` https://w3id.org/pmd/co/ <br/>

Protege look:

![p0](https://github.com/user-attachments/assets/3c3ec208-40fc-407b-a7fc-f6a33a10bd2d)

Similarly, the object property **exists at** has the following annotations:

``rdfs:label:`` "exists at" <br/>
``rdfs:comment:`` "Indicates the spatial or temporal existence of an entity." <br/>
``skos:definition:`` "(Elucidation) exists at is a relation between a particular and some temporal region at which the particular exists" <br/>
``dc:identifier:`` "118-BFO” <br/>
``rdfs:isDefinedBy:`` https://w3id.org/pmd/co/ <br/>
``skos:example:`` "First World War exists at 1914-1916; Mexico exists at January 1, 2000" <br/>

Protege look:

![p1](https://github.com/user-attachments/assets/cec64d9e-5b7b-48f3-8a2b-0e710ff63ccb)


#### Aristotelian definition:
For providing the class definitions in PMDcore ontology we follow the Aristotelian principle:
> An **Aristotelian definition** typically refers to defining something by its genus (general category) and differentia (specific characteristics that distinguish it from other members of the same genus), that should be expressed in the concepts defined in the ontology. This method is rooted in Aristotle's philosophy and is often used in ontology development to define classes in relation to their superclasses. For more information, please see [Aristotelian](https://www.merriam-webster.com/dictionary/Aristotelian) and [Aristotelianism](https://en.wikipedia.org/wiki/Aristotelianism).

For instance, the class **Material** may have the following annotations:
- **Label**: "Material"@en, "Material"@de
- **Definition**: "A Material is a Portion Of Matter that has the disposition to participate in some Manifacturing Process and whose shape is not relevant for its disposition to participate in the Manifacuring Process."@en
- **Comment**: "The sum of portions of matter of the same type form a portion of matter of that type."@en

## Constraints and Rules
PMDco defines specific constraints to ensure data consistency:

- **Cardinality Constraints**: Specify the number of times a property can be associated with a class.
  - For example, a **Manufacturing Process** may be constrained to have some **material entity** as input using the **has_specified_input** property.

- **Domain and Range Specifications**: Define the applicable classes for properties.
  - The **stimulates** property (subproperty of **realizes**) has a domain of **Stimulating Process** and a range of **Material Property**.

These constraints ensure logical consistency and facilitate accurate data representation within the ontology.