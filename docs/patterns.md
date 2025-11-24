# Usage Patterns

In ontology development and usage, **usage patterns** play a critical role in addressing recurring modeling requirements. These patterns provide standardized, reusable semantic snippets that facilitate consistent representation of relationships between instances and entities. Furthermore, such patterns may be used to create SHACL shapes to include constraints in a knowledge representation. By following usage patterns, ontology users and developers can ensure uniformity, clarity, and reusability in their models.

The sections below illustrate how to read and apply these patterns. Each pattern includes its purpose, description, relevant properties, visualization, and example.

## Pattern 1 - Temporal Region


- **Purpose**: Specifying the boundaries of a process on the time axis. 
- **Core Properties**: 
  - `bfo:occupies temporal region` ([BFO_0000199](http://purl.obolibrary.org/obo/BFO_0000199))
  - `bfo:proper temporal part of ` ([BFO_0000136](http://purl.obolibrary.org/obo/BFO_0000136))
  - `bfo:has first instant ` ([BFO_0000222](http://purl.obolibrary.org/obo/BFO_0000222))
  - `bfo:has last instant ` ([BFO_0000224](http://purl.obolibrary.org/obo/BFO_0000224))

- **Example Use Case**: the pattern defines a temporal ontology where processes unfold within bounded durations, those durations may be nested, and continuant entities exist at specific times. It provides a temporal structure linking processes, periods, instants, and enduring entities.
- **Description**: This graph describes a set of temporal relationships among processes, temporal regions, and continuant entities. The graph models how different kinds of entities relate to time and duration through their association with temporal regions and instants.
Within this model, there are two processes — (ex:process_1) and (ex:process_2) — each representing an occurrence or event that unfolds over time. Both processes are linked to distinct one-dimensional temporal regions (ex:period_1, ex:period_2), via the occupies_temporal_region property. This expresses that each process extends through a particular temporal duration.
The temporal structure is further refined through hierarchical and boundary definitions. The region (ex:period_1) is described as a proper_temporal_part_of (ex:period_2), indicating that the first period is entirely contained within the second, but not identical to it. The larger region (ex:period_2) has defined temporal boundaries: it has_first_instant (ex:start) and has_last_instant (ex:end), both of which are represented as zero-dimensional temporal regions, signifying discrete points in time marking the beginning and end of that duration.
In addition to the processes and periods, the model includes a continuant entity, (ex:object_1), which exists_at a particular temporal region, (ex:some_time). This denotes that the continuant maintains existence at or during a specific time interval, emphasizing persistence or presence within the temporal framework. 

```d2
direction: up

classes: {
  bfoclazz: {
    style: {
      fill: "#dd42f5"
      shadow: true
      border-radius: 5
      font-color: white
    }
  }
  individual: {
    style: {
      fill: "lightgrey"
    }
  }
}
tbox.bfo*.class: bfoclazz
tbox.label: ""
tbox: {
  "bfo:occurrent" -> "bfo:entity": "rdfs:subClassOf"
  "bfo:continuant" -> "bfo:entity": "rdfs:subClassOf"
  "bfo:process" -> "bfo:occurrent": "rdfs:subClassOf"
  "bfo:temporal region" -> "bfo:occurrent": "rdfs:subClassOf"
  "bfo:one dimensional t.r." -> "bfo:temporal region": "rdfs:subClassOf"
  "bfo:zero dimensional t.r." -> "bfo:temporal region": "rdfs:subClassOf"
}

tbox.style.stroke: transparent
tbox.style.fill: transparent

abox.ex*.class: individual
abox.label: "___________________________________________________________________________"
abox: {
  "ex:process 1" -> "ex:period 1": "bfo:occupies_temporal_region"
  "ex:process 2" -> "ex:period 2": "bfo:occupies_remporal_region"
  "ex:period 2" -> "ex:start": "bfo:has_first_instant"
  "ex:period 2" -> "ex:end": "bfo:has_last_instant"
  "ex:period 1" -> "ex:period 2": "bfo:proper_temporal_part_of"
  "ex:object 1" -> "ex:some time": "bfo:existsAt"
}
abox.style.stroke: transparent
abox.style.fill: transparent

abox."ex:process 1" -> tbox."bfo:process": "rdf:type"
abox."ex:process 2" -> tbox."bfo:process": "rdf:type"
abox."ex:period 1" -> tbox."bfo:one dimensional t.r.": "rdf:type"
abox."ex:period 2" -> tbox."bfo:one dimensional t.r.": "rdf:type"
abox."ex:some time" -> tbox."bfo:temporal region": "rdf:type"
abox."ex:object 1" -> tbox."bfo:continuant": "rdf:type"
abox."ex:start" -> tbox."bfo:zero dimensional t.r.": "rdf:type"
abox."ex:end" -> tbox."bfo:zero dimensional t.r.": "rdf:type"

```
```
@prefix : <https://w3id.org/pmd/co/test#> .
@prefix ex: <https://www.example.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <https://w3id.org/pmd/co/test#> .

@prefix process: <http://purl.obolibrary.org/obo/BFO_0000015>  . #Class
@prefix continuant: <http://purl.obolibrary.org/obo/BFO_0000002> .  #Class
@prefix temporal_region: <http://purl.obolibrary.org/obo/BFO_0000008> . #Class
@prefix one-dimensional_temporal_region: <http://purl.obolibrary.org/obo/BFO_0000038> . #Class
@prefix zero-dimensional_temporal_region: <http://purl.obolibrary.org/obo/BFO_0000148> . #Class

@prefix occupies_temporal_region: <http://purl.obolibrary.org/obo/BFO_0000199> . #ObjectProperty
@prefix proper_temporal_part_of: <http://purl.obolibrary.org/obo/BFO_0000136> . #ObjectProperty
@prefix has_first_instant: <http://purl.obolibrary.org/obo/BFO_0000222> . #ObjectProperty
@prefix has_last_instant: <http://purl.obolibrary.org/obo/BFO_0000224> . #ObjectProperty
@prefix exists_at: <http://purl.obolibrary.org/obo/BFO_0000108> . #ObjectProperty

<https://w3id.org/pmd/co/test/shape/temporal_region> rdf:type owl:Ontology .

ex:process_1 a process: .
ex:process_2 a process: .
ex:period_1 a one-dimensional_temporal_region: .
ex:period_2 a one-dimensional_temporal_region: . 
ex:some_time a temporal_region: .
ex:object_1 a continuant: .
ex:start a zero-dimensional_temporal_region: .
ex:end a zero-dimensional_temporal_region: .

ex:process_1 occupies_temporal_region: ex:period_1 . 
ex:process_2 occupies_temporal_region: ex:period_2 .
ex:period_2 has_first_instant: ex:start . 
ex:period_2 has_last_instant: ex:end .
ex:period_1 proper_temporal_part_of: ex:period_2 .
ex:object_1 exists_at: ex:some_time .

```
(see folder [patterns/temporal region](https://github.com/materialdigital/core-ontology/tree/main/patterns/temporal%20region))

---

## Pattern 2 - Process Chain

- **Purpose**: Represent processes, consisting of simultaneous and serial subprocesses. 
- **Core Properties**: 
  - `bfo:precedes` ([BFO_0000063](http://purl.obolibrary.org/obo/BFO_0000063))
  - `ro:has part` ([BFO_0000051](http://purl.obolibrary.org/obo/BFO_0000051))
  - `ro:starts with` ([RO_0002224](http://purl.obolibrary.org/obo/RO_0002224))
  - `ro:ends with ` ([RO_0002230](http://purl.obolibrary.org/obo/RO_0002230))
  - `ro:simultaneous with` ([RO_0002082](http://purl.obolibrary.org/obo/RO_0002082))
- **Example Use Case**: the pattern defines a hierarchical and temporal relationship among processes: a parent process composed of multiple interconnected stages, where the first step leads into two concurrent middle steps, both of which precede the final one. This structure models a workflow with clear order, parallel execution, and a defined start and end.
- **Description**: This graph describes a structured process chain that organizes several interrelated process steps within a defined sequence. The graph defines relationships among processes using temporal and structural object properties.
At the highest level, there is a parent process (ex:process_parent), which serves as the overarching workflow. This process begins with (ex:process_step1) and concludes with (ex:process_step3), as indicated by the starts_with and ends_with relationships. The parent process is composed of several parts — specifically (ex:process_step1), (ex:process_step2a), (ex:process_step2b), and (ex:process_step3) — through the has_part property, defining the hierarchical structure of the process.
The sequence begins with (ex:process_step1), which acts as the initial phase. This step precedes (ex:process_step2a), (ex:process_step2b), and (ex:process_step3), establishing it as the starting point from which subsequent processes emerge. Among the intermediate steps, (ex:process_step2a) and (ex:process_step2b) are connected not only sequentially but also through simultaneity: (ex:process_step2a) is defined as simultaneous_with (ex:process_step2b), indicating that they occur at the same time within the overall process.
Finally, both (ex:process_step2a) and (ex:process_step2b) lead to (ex:process_step3), the final step of the chain. This closing process represents the conclusion of the overall workflow, marking the endpoint of the structured and partially parallel sequence defined in the RDF model.


```d2
direction: up

classes: {
  bfoclazz: {
    style: {
      fill: "#dd42f5"
      shadow: true
      border-radius: 5
      font-color: white
    }
  }
  individual: {
    style: {
      fill: "lightgrey"
    }
  }
}
tbox.bfo*.class: bfoclazz
tbox.label: ""
tbox: {
  "bfo:process" -> "bfo:occurrent": "rdfs:subClassOf"
}

tbox.style.stroke: transparent
tbox.style.fill: transparent

abox.ex*.class: individual
abox.label: "___________________________________________________________________________"
abox: {
  "ex:process parent" -> "ex:process step1": "ro:starts_with"
  "ex:process parent" -> "ex:process step3": "ro:ends_with"

  "ex:process parent" -> "ex:process step1": "ro:has part"
  "ex:process parent" -> "ex:process step2a": "ro:has part"
  "ex:process parent" -> "ex:process step2b": "ro:has part"
  "ex:process parent" -> "ex:process step3": "ro:has part"

  "ex:process step1" -> "ex:process step2a": "bfo:precedes"
  "ex:process step1" -> "ex:process step2b": "bfo:precedes"
  "ex:process step1" -> "ex:process step3": "bfo:precedes"

  "ex:process step2a" -> "ex:process step3": "bfo:precedes"
  "ex:process step2a" -> "ex:process step2b": "ro:simultaneous_with"
}

abox.style.stroke: transparent
abox.style.fill: transparent

abox."ex:process parent" -> tbox."bfo:process": "rdf:type"
abox."ex:process step1" -> tbox."bfo:process": "rdf:type"
abox."ex:process step2a" -> tbox."bfo:process": "rdf:type"
abox."ex:process step2b" -> tbox."bfo:process": "rdf:type"
abox."ex:process step3" -> tbox."bfo:process": "rdf:type"
```

```
@prefix : <https://w3id.org/pmd/co/test#> .
@prefix ex: <https://www.example.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <https://w3id.org/pmd/co/test#> .

@prefix process: <http://purl.obolibrary.org/obo/BFO_0000015>  . #Class

@prefix has_part: <http://purl.obolibrary.org/obo/BFO_0000051> . #ObjectProperty 
@prefix precedes: <http://purl.obolibrary.org/obo/BFO_0000063> . #ObjectProperty
@prefix starts_with: <http://purl.obolibrary.org/obo/RO_0002224> . #ObjectProperty
@prefix ends_with: <http://purl.obolibrary.org/obo/RO_0002230> . #ObjectProperty
@prefix simultaneous_with: <http://purl.obolibrary.org/obo/RO_0002082> . #ObjectProperty

<https://w3id.org/pmd/co/test/shape/process_chain> rdf:type owl:Ontology .

ex:process_parent a process: .
ex:process_step1 a process: .
ex:process_step2a a process: .
ex:process_step2b a process: .
ex:process_step3 a process: .


ex:process_parent starts_with: ex:process_step1 .
ex:process_parent ends_with: ex:process_step3 .
ex:process_parent has_part: ex:process_step1, ex:process_step2a, ex:process_step2b, ex:process_step3 .

ex:process_step1 precedes: ex:process_step2a, ex:process_step2b, ex:process_step3 .

ex:process_step2a precedes: ex:process_step3 .
ex:process_step2a simultaneous_with: ex:process_step2b .
```

(see folder [patterns/process chain](https://github.com/materialdigital/core-ontology/tree/main/patterns/process%20chain))


---

## Pattern 3 - Process Inputs and Outputs

- **Purpose**: Describes how to represent inputs and outputs for planned processes typically involving material entities or information-bearing entities.
- **Core Properties**: 
  - `obi:has_specified_input` [OBI_0000293](http://purl.obolibrary.org/obo/OBI_0000293)
  - `obi:has_specified_output` [OBI_0000299](http://purl.obolibrary.org/obo/OBI_0000299)
- **Example Use Case**: A planned process with possibility of multiple inputs and outputs, e.g., testing properties of a metallic sample, or transforming a piece of material into another product.
- **Further notes**: There are also the properties [has input](http://purl.obolibrary.org/obo/RO_0002233) and [has output](http://purl.obolibrary.org/obo/RO_0002234) from RO. It is intended to use the OBI [has specified input](http://purl.obolibrary.org/obo/OBI_0000293) and [has specified output](http://purl.obolibrary.org/obo/OBI_0000299) on [planned processes](http://purl.obolibrary.org/obo/OBI_0000011) (as also indicated by the domain of those) and the RO variant on other kinds of processes.  

```d2
direction: up

classes: {
  bfoclazz: {
    style: {
      fill: "#dd42f5"
      shadow: true
      border-radius: 5
      font-color: white
    }
  }
  pmdclazz: {
    style: {
      fill: "#7777BB"
      shadow: true
      border-radius: 5
      font-color: white
    }
  }
  obiclazz: {
    style: {
      fill: "#BB7777"
      shadow: true
      border-radius: 5
      font-color: white
    }
  }
  individual: {
    style: {
      fill: "lightgrey"
    }
  }
}
bfo*.class: bfoclazz
pmd*.class: pmdclazz
obi*.class: obiclazz
ex*.class: individual

"ex:process 1" -> "ex:object1": "obi:has_specified_input"
"ex:process 1" -> "ex:object2": "obi:has_specified_output"
"ex:process 2" -> "ex:object2": "obi:has_specified_input"
"ex:process 2" -> "ex:object3": "obi:has_specified_output"

"ex:process 1" -> "pmd:manufacturing process": "rdf:type"
"ex:process 2" -> "pmd:coating process": "rdf:type"
"obi:planned process" -> "bfo:process": "owl:subClassOf"
"pmd:coating process" -> "pmd:manufacturing process": "owl:subClassOf"

"pmd:manufacturing process" -> "obi:planned process": "owl:subClassOf"

"ex:object1" -> "bfo:object": "rdf:type"
"ex:object2" -> "bfo:object": "rdf:type"
"ex:object3" -> "bfo:object": "rdf:type"

```

```
@prefix : <https://w3id.org/pmd/co/test#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex: <http://example.com/> .
@base <https://w3id.org/pmd/co/test> .


@prefix planned_process: <http://purl.obolibrary.org/obo/OBI_0000011> .
@prefix manufacturing_process: <https://w3id.org/pmd/co/PMD_0000833> .
@prefix coating: <https://w3id.org/pmd/co/PMD_0000563> .
@prefix has_specified_input: <http://purl.obolibrary.org/obo/OBI_0000293> .
@prefix has_specified_output: <http://purl.obolibrary.org/obo/OBI_0000299> .
@prefix object: <http://purl.obolibrary.org/obo/BFO_0000030> .

<https://w3id.org/pmd/co/test> rdf:type owl:Ontology  .

manufacturing_process: owl:subClassOf planned_process: .

ex:process1 a manufacturing_process: ;   
        has_specified_input: ex:object1 ;
        has_specified_output: ex:object2 . 

ex:process2 a coating:;  
        has_specified_input: ex:object2  ; 
        has_specified_output: ex:object3 . 

ex:object1 a object:
ex:object2 a object:
ex:object3 a object:
```
(see folder [patterns/input and output of processes](https://github.com/materialdigital/core-ontology/tree/main/patterns/input%20and%20output%20of%20processes))


---

## Pattern 4 - Realizable Entities (Role)

- **Purpose**: Represent characteristics of the objects, brought to existence by a specific situation. E.g. a role, which is relalized in a process.
- **Core Properties**: 
  - `ro:has role` [RO_0000087](http://purl.obolibrary.org/obo/RO_0000087)
  - `bfo:has realization` [BFO_0000054](http://purl.obolibrary.org/obo/BFO_0000054)
  - `obi:has specified input` [OBI_0000293](http://purl.obolibrary.org/obo/OBI_0000293)

- **Example Use Case**: Specifying the role of a specimen of a material object that participates a process as input. 
  
```d2
direction: up

classes: {
  bfoclazz: {
    style: {
      fill: "#dd42f5"
      shadow: true
      border-radius: 5
      font-color: white
    }
  }
  pmdclazz: {
    style: {
      fill: "#7777BB"
      shadow: true
      border-radius: 5
      font-color: white
    }
  }
  obiclazz: {
    style: {
      fill: "#BB7777"
      shadow: true
      border-radius: 5
      font-color: white
    }
  }
  individual: {
    style: {
      fill: "lightgrey"
    }
  }
}
bfo*.class: bfoclazz
pmd*.class: pmdclazz
obi*.class: obiclazz
ex*.class: individual

"ex:process 1" -> "ex:object 1": "obi:has_specified_input"
"ex:process 1" -> "ex:result 1": "obi:has_specified_output"
"ex:process 1" -> "ex:objective 1": "achieves_planned_objective"

"ex:objective 1" -> "ex:object 1": "iao:is about"
"ex:result 1" -> "ex:object 1": "iao:is about"
"ex:process 1" -> "pmd:fatigue testing process": "rdf:type"
"pmd:fatigue testing process:" -> "obi:planned process": "owl:subClassOf"
"obi:planned process" -> "bfo:process": "owl:subClassOf"

"ex:object 1" -> "bfo:object": "rdf:type"
"ex:object 1" -> "ex:role 1": "ro:has role"
"ex:role 1" -> "obi:evaluant role": "rdf:type"
"ex:role 1" -> "ex:process 1": "bfo:has realization"

# "bfo:object": {
#  near: center-left
# }


```
```


@prefix : <https://w3id.org/pmd/co/test#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex: <http://example.com/> .
@base <https://w3id.org/pmd/co/test> .

@prefix object: <http://purl.obolibrary.org/obo/BFO_0000030> .
@prefix evaluant_role: <http://purl.obolibrary.org/obo/OBI_0000067> .
@prefix has_role: <http://purl.obolibrary.org/obo/RO_0000087> .
@prefix has_realization: <http://purl.obolibrary.org/obo/BFO_0000054> .
@prefix planned_process: <http://purl.obolibrary.org/obo/OBI_0000011> .
@prefix fatigue_testing_process: <https://w3id.org/pmd/co/PMD_0000638> .
@prefix has_specified_input: <http://purl.obolibrary.org/obo/OBI_0000293> .
@prefix has_specified_output: <http://purl.obolibrary.org/obo/OBI_0000299> .
@prefix achieves_planned_objective: <http://purl.obolibrary.org/obo/OBI_0000417> .
@prefix is_about: <http://purl.obolibrary.org/obo/IAO_0000136>  .

<https://w3id.org/pmd/co/test/role> rdf:type owl:Ontology  .

ex:process_1 a fatigue_testing_process: .
ex:process_1 has_specified_input: ex:object_1 .
ex:process_1 achieves_planned_objective: ex:objective_1 .
ex:process_1 has_specified_output: ex:result_1 .

ex:objective_1 is_about: ex:object_1 .
ex:result_1  is_about: ex:object_1 .

ex:object_1 a object: .
ex:object_1 has_role: ex:role_1 .

ex:role_1 a evaluant_role: .
ex:role_1 has_realization: ex:process_1  .


```

---

## Pattern 5 - Material Properties (Qualities)

- **Purpose**: Represent materials, their qualities, and their behaviors at different moments/periods of time.
- **Example Use Case**: 
This example defines a set of example individuals illustrating how materials, their qualities, and their behaviors can be semantically represented. 
The example models three main themes:

	1. Intrinsic material qualities: Examples include mass, and density.
		
		- A metal sheet is modeled as a material object that has a mass quality with a given numeric value (3.3 g).
		- A steel material has an associated density quality (7.5 g/cm³).

	2. Behavioral material properties and processes: These represent how a material behaves under certain conditions.
		- A steel material has a melting point (1500 °C), which is realized through a melting process.
		- The melting process is triggered by an application of heat flux and involves a change of temperature as the material responds.

	3. Relational material qualities: These capture qualities that depend on relations between materials and objects.
		- A mass proportion is expressed between some portion of iron and the metal sheet, with a value of 97.7 %.



```

@prefix : <https://w3id.org/pmd/co/test#> .
@prefix ex: <https://www.example.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <https://w3id.org/pmd/co/test#> .


<https://w3id.org/pmd/co/test/shape/qualities_and_properties> rdf:type owl:Ontology .

### Define prefixes ###

# Classes
@prefix entity: <http://purl.obolibrary.org/obo/BFO_0000001> . 
@prefix independent_continuant: <http://purl.obolibrary.org/obo/BFO_0000004> .
@prefix material_entity: <http://purl.obolibrary.org/obo/BFO_0000040> .
@prefix object: <http://purl.obolibrary.org/obo/BFO_0000030> .
@prefix temporally_qualified_continuant:  <https://w3id.org/pmd/co/PMD_0000068> .
@prefix portion_of_iron: <https://w3id.org/pmd/co/PMD_0020026> . 
@prefix material: <https://w3id.org/pmd/co/PMD_0000000> .
@prefix temporal_region: <http://purl.obolibrary.org/obo/BFO_0000008> . 
@prefix quality: <http://purl.obolibrary.org/obo/BFO_0000019> .
@prefix mass: <https://w3id.org/pmd/co/PMD_0020133> .
@prefix density: <https://w3id.org/pmd/co/PMD_0000597> .
@prefix behavioral_material_property: <https://w3id.org/pmd/co/PMD_0000005> .
@prefix specifically_dependent_continuant: <http://purl.obolibrary.org/obo/BFO_0000020> .
@prefix melting_point: <https://w3id.org/pmd/co/PMD_0000851> .
@prefix relational_quality: <http://purl.obolibrary.org/obo/BFO_0000145> .
@prefix mass_proportion: <https://w3id.org/pmd/co/PMD_0020102> .
@prefix scalar_value_specification: <http://purl.obolibrary.org/obo/OBI_0001931> .
@prefix fraction_value_specification: <https://w3id.org/pmd/co/PMD_0025997> .
@prefix gram: <http://purl.obolibrary.org/obo/UO_0000021> . 
@prefix gram_per_cubic_centimetre: <http://purl.obolibrary.org/obo/UO_0000084> .
@prefix degree_celsius: <http://purl.obolibrary.org/obo/UO_0000027> .
@prefix mass_percentage: <http://purl.obolibrary.org/obo/UO_0000163> .
@prefix melting_process: <https://w3id.org/pmd/co/PMD_0000053> .
@prefix application_of_heat_flux: <https://w3id.org/pmd/co/PMD_0000520> . 
@prefix stimulating_process: <https://w3id.org/pmd/co/PMD_0000950> .
@prefix process: <http://purl.obolibrary.org/obo/BFO_0000015> .
@prefix change_of_temperature: <https://w3id.org/pmd/co/PMD_0000549> .

# Subclass relations 
object: rdfs:subClassOf material_entity: .
material_entity: rdfs:subClassOf independent_continuant: .
material: rdfs:subClassOf material_entity: .
portion_of_iron: rdfs:subClassOf material_entity: .
quality: rdfs:subClassOf specifically_dependent_continuant: .
mass: rdfs:subClassOf quality: .
density: rdfs:subClassOf quality: .
relational_quality: rdfs:subClassOf quality: .
mass_proportion: rdfs:subClassOf relational_quality: .
behavioral_material_property: rdfs:subClassOf specifically_dependent_continuant: .
melting_point: rdfs:subClassOf behavioral_material_property: .
specifically_dependent_continuant: rdfs:subClassOf entity: .
melting_process: rdfs:subClassOf process: .
stimulating_process: rdfs:subClassOf process: .
application_of_heat_flux: rdfs:subClassOf stimulating_process: .
change_of_temperature: rdfs:subClassOf process: .

# Object properties
@prefix exists_at: <http://purl.obolibrary.org/obo/BFO_0000108> . 
@prefix is_state_of: <https://w3id.org/pmd/co/PMD_0000070> .
@prefix quality_of: <http://purl.obolibrary.org/obo/RO_0000080> .
@prefix characteristic_of: <http://purl.obolibrary.org/obo/RO_0000052> .
@prefix relational_quality_of: <https://w3id.org/pmd/co/PMD_0025999> .
@prefix concretizes: <http://purl.obolibrary.org/obo/RO_0000059> .
@prefix has_specified_numeric_value: <http://purl.obolibrary.org/obo/OBI_0001937> . 
@prefix has_measurement_unit_label: <http://purl.obolibrary.org/obo/IAO_0000039> .
@prefix specifies_value_of: <http://purl.obolibrary.org/obo/OBI_0001927> .
@prefix has_realization: <http://purl.obolibrary.org/obo/BFO_0000054> .
@prefix participates_in: <http://purl.obolibrary.org/obo/RO_0000056> .
@prefix has_participant: <http://purl.obolibrary.org/obo/RO_0000057> .
@prefix stimulated_by: <https://w3id.org/pmd/co/PMD_0001030> .
@prefix responds_with: <https://w3id.org/pmd/co/PMD_0001029> .
@prefix has_specified_input: <http://purl.obolibrary.org/obo/OBI_0000293> .
@prefix has_specified_output: <http://purl.obolibrary.org/obo/OBI_0000299> .

### Instances ###

# Quality example
ex:metal_sheet a owl:NamedIndividual , object: .

ex:mass_metal_sheet a owl:NamedIndividual , mass: ;
            quality_of: ex:metal_sheet . 

ex:svs_15_g a owl:NamedIndividual , scalar_value_specification: ;
            has_specified_numeric_value: "3.3"^^xsd:float ;
            has_measurement_unit_label: gram: ; 
            specifies_value_of: ex:mass_metal_sheet .

ex:tcq_temporal_region a owl:NamedIndividual , temporal_region: .
        
ex:tqc_steel_material a owl:NamedIndividual , material: , temporally_qualified_continuant: ; 
            exists_at: ex:tcq_temporal_region ; 
            is_state_of: ex:steel_material .

ex:density_steel a owl:NamedIndividual , density: ;
            quality_of: ex:tqc_steel_material . 


ex:svs_7_5_g_per_cm a owl:NamedIndividual , scalar_value_specification: ;
            has_specified_numeric_value: "7.5"^^xsd:float ;
            has_measurement_unit_label: gram_per_cubic_centimetre: ; 
            specifies_value_of: ex:density_steel .


# Behavioral material property
ex:steel_material a owl:NamedIndividual , material: ; 
            participates_in: ex:melting_process .

ex:svs_1500_deg_c a owl:NamedIndividual , scalar_value_specification: ;
            has_specified_numeric_value: "1500"^^xsd:float ;
            has_measurement_unit_label: degree_celsius: ; 
            specifies_value_of: ex:melting_temperature_steel .

ex:melting_temperature_steel a owl:NamedIndividual , melting_point: ; 
            characteristic_of: ex:steel_material ;
            has_realization: ex:melting_process ; 
            stimulated_by: ex:application_of_heat_flux ; 
            responds_with: ex:change_of_temperature_during_melting .

ex:melting_process a owl:NamedIndividual , melting_process: ;
            has_specified_output: ex:steel_material ; 
            has_specified_input: ex:steel_material .

ex:application_of_heat_flux a owl:NamedIndividual , application_of_heat_flux: .

ex:change_of_temperature_during_melting a owl:NamedIndividual , change_of_temperature: .

# Relational quality
ex:some_iron a owl:NamedIndividual , portion_of_iron: . 

ex:mass_proportion_iron a owl:NamedIndividual , mass_proportion: ;
            relational_quality_of:  ex:some_iron , ex:metal_sheet .

ex:fraction_iron a owl:NamedIndividual , fraction_value_specification: ;
            has_specified_numeric_value: "97.7"^^xsd:float ;
            has_measurement_unit_label: mass_percentage: ; 
            specifies_value_of: ex:mass_proportion_iron .


```

---

## Pattern 6 - Scalar Measurement

- **Purpose**: Represent measured value of some material characteristic. 
- **Core Properties**: 
  - `iao:isQualityMeasuredAs` 
  - `bfo:realizes`
  - `iao:isAbout`
  - `pmd:hasInput`
  - `pmd:hasOutput`
  - `pmd:hasValueSpecification`
  - `pmd:specifiesValueOf`
- **Example Use Case**: Specifying the measured heat capacity value of a specimen.

![Visualization of Pattern 6](https://github.com/user-attachments/assets/770530aa-8ac1-49ff-98ec-7aa8c060d6ec)

---

## Pattern 7 - Scalar Value Specification

- **Purpose**: Represents scalar physical quantities, combining a numerical value and a unit.
- **Core Properties**: 
  - `obi:hasSpecifiedNumericValue`
  - `iao:hasMeasurementUnitLabel`
  - `iao:MeasurementUnitLabel`

- **Example Use Case**: The example describes a scalar value specification, ex:scalar_value_specification_X, which is assigned a numeric value of 135.0 and linked to a measurement unit represented by the individual ex:unit_X. The numeric value is provided via the OBI property has_specified_numeric_value, while the unit is associated through the IAO property has_measurement_unit_label. The unit individual ex:unit_X is typed as a measurement unit label, but in practice this placeholder unit could be replaced by a formally defined unit from established ontologies such as UO (Units of Measurement Ontology) or QUDT (Quantities, Units, Dimensions, and Types). Together, the triples express that a value of 135.0 is specified in some unit, whether a custom one like ex:unit_X or a standard unit drawn from UO or QUDT.

```
@prefix : <https://w3id.org/pmd/co/test#> .
@prefix ex: <https://www.example.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <https://w3id.org/pmd/co/test#> .

<https://w3id.org/pmd/co/test/shape2> rdf:type owl:Ontology .

@prefix has_measurement_unit_label: <http://purl.obolibrary.org/obo/IAO_0000039> .
@prefix has_specified_numeric_value: <http://purl.obolibrary.org/obo/OBI_0001937> .
@prefix measurement_unit_label: <http://purl.obolibrary.org/obo/IAO_0000003> .


ex:scalar_value_specification_X rdf:type owl:NamedIndividual ;
                                has_measurement_unit_label: ex:unit_X ;
                                has_specified_numeric_value: 135.0 .

ex:unit_X rdf:type owl:NamedIndividual ,
                   measurement_unit_label: .

```

---

## Pattern 8 - Categorical Value Specification

- **Purpose**: Represents object characteristics, described by belonging to some category.
- **Core Properties**: 
  - `obi:hasSpecifiedValue`
  - `iao:isQualityMeasuredAs`
  - `pmd:hasValueSpecification`
  - `pmd:specifiesValueOf`
- **Example Use Case**: Specifying that material belongs to a certain category, e.g., is a polymer.
  
![Visualization of Pattern 8](https://github.com/user-attachments/assets/38d70bbd-29d1-47c3-b73b-6e4ebc12feef)

---
## Pattern 9 - Material and Device Specification

- **Purpose**: Specify the material, from which the object is made, by stating that it complies with the certain material specification. Or, specifying the device in the same manner.
- **Core Properties**: 
  - `iao:isQualityMeasuredAs`
  - `iao:isAbout`
  - `pmd:hasValueSpecification`
  - `pmd:specifiesValueOf`
- **Core Idea**: provide a class pmd:MaterialSpecification/pmd:DeviceSpecification as a subclass of iao:InformationContentEntity, to which the material/device object can adhere.
- **Example Use Case**: Specifying the material of a steel sheet to be the steel S355J2.

![Visualization of Pattern 9](https://github.com/user-attachments/assets/3414e021-477f-4eab-8174-2e8b2f29560b)


---
