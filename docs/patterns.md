# Usage Patterns

In ontology development and usage, **usage patterns** play a critical role in addressing recurring modeling requirements. These patterns provide standardized, reusable semantic snippets that facilitate consistent representation of relationships between instances and entities. Furthermore, such patterns may be used to create SHACL shapes to include constraints in a knowledge representation. By following usage patterns, ontology users and developers can ensure uniformity, clarity, and reusability in their models.

The sections below illustrate how to read and apply these patterns. Each pattern includes its purpose, description, relevant properties, visualization, and example.

## Pattern 1 - Temporal Region


- **Purpose**: Specifying the boundaries of a process on the time axis. 
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

```turtle
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
- **Description**: A planned process with possibility of multiple inputs and outputs, e.g., testing properties of a metallic sample, or transforming a piece of material into another product.
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

- **Purpose**: Represent characteristics of the objects, brought to existence by a specific situation. E.g. a role, which is realized in a process.
- **Description**: This example describes how an object participates in a planned experimental process by bearing a specific evaluant role. An object, here ex:object_1, is involved in a fatigue testing process, and this process takes the object as its specified input. The process is linked to an objective, and both the objective and the resulting output are explicitly stated to be about the same object, making clear that the purpose and outcome of the process concern that object. The object is assigned an evaluant role, ex:role_1, and this role is realized in the execution of the fatigue testing process. In this way, the pattern connects object, role, process, objective, and result into a coherent structure showing that the object is the thing being evaluated in the process, and that the process executes and realizes the evaluant role associated with that object.
  
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
"pmd:fatigue testing process" -> "obi:planned process": "owl:subClassOf"
"obi:planned process" -> "bfo:process": "owl:subClassOf"

"ex:object 1" -> "bfo:object": "rdf:type"
"ex:object 1" -> "ex:role 1": "ro:has role"
"ex:role 1" -> "obi:evaluant role": "rdf:type"
"ex:role 1" -> "ex:process 1": "bfo:has realization"

# "bfo:object": {
#  near: center-left
# }
```


```turtle
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

(see folder: [patterns/realizable entity (role)](https://github.com/materialdigital/core-ontology/tree/main/patterns/realizable%20entity%20(role))
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

## Pattern 5 Qualities (structure and state properties)

- **Purpose**:  
The pattern describes a quality (mass) that inheres in some independent continuant at all times that the object exists and a second quality (density) that inheres in a TQC of the same independent continuant during a specific period. To this end, the independent continuant is seen as an bfo:object throughout its whole existance and bears its mass during the existance. As for the quality that that is specific to some period, the independent continuant is seen as a material (and as a temporally qualified continuant TQC) that will cease to exist with its current qualities (density) once it is sintered.
  
  Note that relational qualities are excluded.  

- **Core Properties**:  
  - `pmd:is state of`  
  - `bfo:exists at`
  - `ro:quality of`
- **Example Use Case**: Specifying that the mass of an object persists over time while the material it is made of (including the density quality) changes.

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
  roclazz: {
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
  uoclazz: {
    style: {
      fill: "#777799"
      shadow: true
      stroke-dash: 3
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
tbox.ro*.class: roclazz
tbox.pmd*.class: pmdclazz
tbox.obi*.class: obiclazz
tbox.uo*.class: uoclazz

abox.ex*.class: individual

tbox.style.stroke: transparent
tbox.style.fill: transparent

abox.style.stroke: transparent
abox.style.fill: transparent

tbox.label: ""
abox.label: "___________________________________________________________________________________________________________"

tbox."bfo:object": {
  near: tbox."pmd:TQC"
}

abox: {
  "ex:svs 7 g" -> "7": "obi:has_specified_numeric_value"
  "ex:mass of sintering component" -> "ex:my dental crown": "ro:quality of"
  "ex:green part material" -> "ex:my dental crown": "pmd:is state of"
  "ex:green part material" -> "ex:sometime before sintering": "bfo:exists at"
  "ex:svs 7 g" -> "ex:mass of sintering component": "obi:specifies value of"
  "ex:density of green part material" -> "ex:green part material": "ro:quality of"
  "ex:svs 3.5 g per cm3" -> "3.5": "obi:has_specified_numeric_value"
  "ex:svs 3.5 g per cm3" -> "ex:density of green part material": "obi:specifies value of"
}

abox."ex:green part material" -> tbox."pmd:TQC": "rdf:type"
abox."ex:green part material" -> tbox."pmd:material": "rdf:type"
abox."ex:my dental crown" -> tbox."bfo:object": "rdf:type"
abox."ex:svs 3.5 g per cm3" -> tbox."obi:scalar value specification": "rdf:type"
abox."ex:mass of sintering component" -> tbox."pmd:mass": "rdf:type"
abox."ex:density of green part material" -> tbox."pmd:density": "rdf:type"
abox."ex:svs 7 g" -> tbox."obi:scalar value specification": "rdf:type"
abox."ex:svs 7 g" -> tbox."uo:g": "iao:has measurement unit label"
abox."ex:svs 3.5 g per cm3" -> tbox."uo:g/cm3": "iao:has measurement unit label"
abox."ex:sometime before sintering" -> tbox."bfo:temporal region": "rdf:type"

```

```turtle
@prefix mo: <http://purl.org/ontology/mo/> .
@prefix si: <https://si-digital-framework.org/SI#> .
@prefix : <https://w3id.org/pmd/co/test#> .
@prefix ex: <https://www.example.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <https://w3id.org/pmd/co/test#> .

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


# Quality example
ex:my_dental_crown a owl:NamedIndividual ,
                  object: .

ex:mass_of_my_dental_crown a owl:NamedIndividual , 
                      mass: ;
                    quality_of: ex:my_dental_crown . 

ex:svs_7_g a owl:NamedIndividual ,
              scalar_value_specification: ;
            has_specified_numeric_value: "7"^^xsd:float ;
            has_measurement_unit_label: gram: ; 
            specifies_value_of: ex:mass_of_my_dental_crown .

ex:sometime_before_sintering a owl:NamedIndividual ,
                        temporal_region: .
        
ex:green_part_material a owl:NamedIndividual ,
                          material: ,
                          temporally_qualified_continuant: ; 
                      exists_at: ex:sometime_before_sintering ; 
                      is_state_of: ex:my_dental_crown .

ex:density_of_green_part_material a owl:NamedIndividual , 
                      density: ;
                  quality_of: ex:green_part_material . 


ex:svs_3_5_g_per_cm3 a owl:NamedIndividual ,
              scalar_value_specification: ;
            has_specified_numeric_value: "3.5"^^xsd:float ;
            has_measurement_unit_label: gram_per_cubic_centimetre: ; 
            specifies_value_of: ex:density_of_green_part_material .

```

---

## Pattern 5 - Realizable Entities (Qualities)

- **Purpose**: Represent inherent characteristics of the objects, having certain scalar values at moments/periods of time.
- **Core Properties**:  
  - `bfo:bearerOf`  
  - `bfo:existAt`
  - `iao:isAbout`
  - `pmd:derivesFrom`
- **Example Use Case**: Specifying that value of hardness of a specimen at certain point of time.

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

(see folder:  [patterns/material property (quality)](https://github.com/materialdigital/core-ontology/tree/main/patterns/material%20property%20(quality)))

```turtle


```


---

## Pattern 6 - Measurement

- **Purpose**: Represent measured value of some material characteristic. 
- **Example Use Case**: This example represents a measurement workflow:

	- An assay with an objective assesses a material entity.
	- The entity has a quality that the assay evaluates, there is also another quality which is not evaluates.
	- The assay produces a measurement datum representing the measurement result of that quality.
	- The datum includes a value specification providing numeric value and units. 
	- The value specification also relates to the quality.


```
@prefix : <https://w3id.org/pmd/co/test/shape3/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <https://w3id.org/pmd/co/test/shape3#> .

@prefix assay: <http://purl.obolibrary.org/obo/OBI_0000070> .
@prefix realizes: <http://purl.obolibrary.org/obo/BFO_0000055> .
@prefix has_specified_input: <http://purl.obolibrary.org/obo/OBI_0000293> .
@prefix has_specified_output: <http://purl.obolibrary.org/obo/OBI_0000299> .
@prefix evaluant_role: <http://purl.obolibrary.org/obo/OBI_0000067> .
@prefix realized_in: <http://purl.obolibrary.org/obo/BFO_0000054> .
@prefix quality: <http://purl.obolibrary.org/obo/BFO_0000019> . 
@prefix quality_is_specified_as: <http://purl.obolibrary.org/obo/IAO_0000419> . 
@prefix material_entity: <http://purl.obolibrary.org/obo/BFO_0000040> . 
@prefix has_quality: <http://purl.obolibrary.org/obo/RO_0000086> . 
@prefix has_role: <http://purl.obolibrary.org/obo/RO_0000087> . 
@prefix has_measurement_unit_label: <http://purl.obolibrary.org/obo/IAO_0000039>  .
@prefix centimeter: <http://purl.obolibrary.org/obo/UO_0000015> .
@prefix is_about: <http://purl.obolibrary.org/obo/IAO_0000136> .
@prefix specifies_value_of: <http://purl.obolibrary.org/obo/OBI_0001927> .
@prefix has_specified_numeric_value: <http://purl.obolibrary.org/obo/OBI_0001937> .
@prefix scalar_measurement_datum: <http://purl.obolibrary.org/obo/IAO_0000032> .
@prefix is_quality_measurement_of: <http://purl.obolibrary.org/obo/IAO_0000221> . 
@prefix has_value_specification: <http://purl.obolibrary.org/obo/OBI_0001938> .
@prefix has_part: <http://purl.obolibrary.org/obo/BFO_0000051> . 
@prefix achieves_planned_objective: <http://purl.obolibrary.org/obo/OBI_0000417> .
@prefix has_measurement_value: <http://purl.obolibrary.org/obo/IAO_0000004> .

<https://w3id.org/pmd/co/test/shape3> rdf:type owl:Ontology  .


:my_assay a owl:NamedIndividual , assay: ;
          realizes: :my_entities_evaluant_role ;
          has_specified_input: :my_evaluated_entity ;
          has_specified_output: :my_qualities_measurement_datum ;
          achieves_planned_objective: :my_objective .

:my_objective is_about: :my_evaluated_entity .

:my_entities_evaluant_role a owl:NamedIndividual , evaluant_role: ;
          realized_in: :my_assay .

:my_entities_preexising_quality a owl:NamedIndividual , quality: .

:my_entities_quality a owl:NamedIndividual , quality: ;
          quality_is_specified_as: :my_qualities_measurement_datum .


:my_evaluated_entity a owl:NamedIndividual , material_entity: ;
          has_quality: :my_entities_preexising_quality ,
          :my_entities_quality ;
          has_role: :my_entities_evaluant_role .


:my_measurment_datums_value_specification a owl:NamedIndividual ;
          has_measurement_unit_label: centimeter: ;
          is_about: :my_evaluated_entity ;
          specifies_value_of: :my_entities_quality ;
          has_specified_numeric_value: 1.0 .


:my_qualities_measurement_datum a owl:NamedIndividual ,
          scalar_measurement_datum: ;
          is_about: :my_evaluated_entity ;
          is_quality_measurement_of: :my_entities_quality ;
          has_value_specification: :my_measurment_datums_value_specification ;
          has_measurement_value: "1234.0"^^xsd:double .
```

(see folder: [patterns/measurement](https://github.com/materialdigital/core-ontology/tree/main/patterns/measurement))

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
(see folder:     [patterns/scalar value specification/](https://github.com/materialdigital/core-ontology/tree/main/patterns/scalar%20value%20specification) )


---

## Pattern 8 - Categorical Value Specification

- **Purpose**: Represents how categorical values such as ferrite, face-centered cubic, and liquid are used to specify the values of material characteristics.
- **Example Use Case**: The example describes materials and the categorical qualities they might possess. In the first example, `ex:fcc_material` is a material that has both a crystal structure and a grain structure. Its crystal structure quality is assigned the categorical value “face-centered cubic”, and its grain structure quality is assigned the categorical value “ferrite”, which is also explicitly stated to be about this same material. In other words, the material is characterized as having an FCC crystal structure and a ferritic grain structure.

In the second example, ex:steel_melt is described as a melt that has an aggregate state quality. This quality is given the categorical value “liquid”, indicating that the melt is in the liquid state.


```
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix sh:    <http://www.w3.org/ns/shacl#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex:    <http://www.example.org/#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix obo:    <http://purl.obolibrary.org/obo/> .
@prefix pmd:   <https://w3id.org/pmd/co/> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix shape:   <https://w3id.org/pmd/co/shapes> .
@base <https://w3id.org/pmd/co/test/shape_categorical_value_specification#> .

<https://w3id.org/pmd/co/test/shape_categorical_value_specification> 
    rdf:type owl:Ontology .

### Define prefixes ###

# Classes
@prefix categorical_value_specification: <http://purl.obolibrary.org/obo/OBI_0001930> . 
@prefix material: <https://w3id.org/pmd/co/PMD_0000000> .
@prefix melt: <https://w3id.org/pmd/co/PMD_0020139> .
@prefix entity: <http://purl.obolibrary.org/obo/BFO_0000001> .
@prefix quality: <http://purl.obolibrary.org/obo/BFO_0000019> . 

@prefix metallic_grain_structure: <https://w3id.org/pmd/co/PMD_0025003> .           # SDC
@prefix ferrite: <https://w3id.org/pmd/co/PMD_0020100> .                            # Individual
@prefix metallic_grain_structures: <https://w3id.org/pmd/co/PMD_0020023> .          # Categorical value

@prefix aggregate_state_value: <https://w3id.org/pmd/co/PMD_0020116> .              # Categorical value
@prefix aggregate_state_liquid: <https://w3id.org/pmd/co/PMD_0020118> .             # Individual
@prefix aggregate_state: <https://w3id.org/pmd/co/PMD_0000512> .                    # SDC

@prefix crystal_structure: <https://w3id.org/pmd/co/PMD_0000591> .                   # SDC
@prefix bravais_lattice: <https://w3id.org/pmd/co/PMD_0020099> .                     # Categorical value
@prefix bravais_lattice_cubic_face_centered: <https://w3id.org/pmd/co/PMD_0020019> . # Individual
@prefix in_minimal: <https://w3id.org/pmd/co/PMD_0000060> . 


# Object properties

@prefix has_quality: <http://purl.obolibrary.org/obo/RO_0000086> .
@prefix specifies_value_of: <http://purl.obolibrary.org/obo/OBI_0001927> .
@prefix is_about: <http://purl.obolibrary.org/obo/IAO_0000136> .

### Define entities ###

# Example 1

ex:fcc_material a owl:NamedIndividual ,
                    material: ; 
                has_quality: ex:crystal_structure_quality ,
                             ex:grain_structure_quality .

ex:crystal_structure_quality a owl:NamedIndividual ,
                                crystal_structure: .
bravais_lattice_cubic_face_centered: specifies_value_of: ex:crystal_structure_quality .

ex:grain_structure_quality a owl:NamedIndividual ,
                                metallic_grain_structure: .
ferrite:  specifies_value_of: ex:grain_structure_quality .
ferrite: is_about: ex:fcc_material .

# Example 2
ex:steel_melt: a owl:NamedIndividual ,
                 melt: ; 
               has_quality: ex:aggregate_state_quality .

ex:aggregate_state_quality a owl:NamedIndividual ,
                            aggregate_state: .
aggregate_state_liquid: specifies_value_of: ex:aggregate_state_quality .

```
(see folder [patterns/categorical value specification](https://github.com/materialdigital/core-ontology/tree/main/patterns/categorical%20value%20specification))


---
## Pattern 9: Simulation input/output 

- **Purpose**: Information content entities as input and output of (simulation-)processes.
- **Example Use Case**: 
A challenge arises when working with digital data about material entities, as is the case in simulations. Due to our ontological commitment to BFO, roles (like described in the patterns above) can only inhere in independent continuants, because a role is something that is physically realized when its bearer participates in a process. Information Content Entities (ICEs), such as datasets, specifications, or parameter files used in a simulation are generically dependent continuants. They are abstract contents that rely on some physical carrier (e.g., a hard drive) but do not themselves participate physically in a process. Assigning roles directly to ICEs would require the role to inhere in the ICE rather than in a material entity, which violates BFO’s ontological constraints.
To preserve the functionality of roles for informational inputs and outputs, we introduce process boundaries as “input/output assignments”. In this pattern, an ICE participates in an input (or output) assignment, which is a dependent entity representing the assignment of that ICE to the process. The assignment itself is then part of the main process. This allows us to capture the role-like semantics of inputs and outputs without violating BFO’s constraint that roles must inhere in material entities. Each assignment can be typed  to specify its intended function in the process, while maintaining ontological consistency. 
For example, in a division calculation process, two numbers considered as ICE serve as inputs through role-like assignments: one as the numerator, and the other as the denominator. Each number participates in an input assignment that is part of the division process, while the resulting quotient participates in an output assignment. This pattern captures the functional roles of inputs and outputs without requiring the numbers themselves to bear roles directly, maintaining ontological consistency.


```
@prefix : <http://example.org/division#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

@prefix hasParticipant: <http://purl.obolibrary.org/obo/RO_0000057> .
@prefix partOf: <http://purl.obolibrary.org/obo/BFO_0000050> .
@prefix InformationContentEntity: <http://purl.obolibrary.org/obo/IAO_0000030> .
@prefix SimulationProcess: <https://w3id.org/pmd/co/PMD_0000933> .
@prefix InputAssignment: <https://w3id.org/pmd/co/PMD_0000066> .
@prefix OutputAssignment: <https://w3id.org/pmd/co/PMD_0000067> .
@prefix hasSpecifiedValue: <http://purl.obolibrary.org/obo/OBI_0001937> .
@prefix isSpecifiedInputOf: <http://purl.obolibrary.org/obo/OBI_0000295> .
@prefix isSpecifiedOutputOf: <http://purl.obolibrary.org/obo/OBI_0000312> .

############################
#   CLASS AXIOMS
############################

:Number rdf:type owl:Class ;
        rdfs:subClassOf InformationContentEntity: .

:DivisionProcess rdf:type owl:Class ;
        rdfs:subClassOf SimulationProcess: .

:NumeratorAssignment rdf:type owl:Class ;
    rdfs:subClassOf 
        InputAssignment: ,
        [ rdf:type owl:Restriction ;
          owl:onProperty hasParticipant: ;
          owl:someValuesFrom :Number ],
        [ rdf:type owl:Restriction ;
          owl:onProperty partOf: ;
          owl:someValuesFrom :DivisionProcess ] .

:DenominatorAssignment rdf:type owl:Class ;
    rdfs:subClassOf 
        InputAssignment: ,
        [ rdf:type owl:Restriction ;
          owl:onProperty hasParticipant: ;
          owl:someValuesFrom :Number ],
        [ rdf:type owl:Restriction ;
          owl:onProperty partOf: ;
          owl:someValuesFrom :DivisionProcess ] .

:QuotientAssignment rdf:type owl:Class ;
    rdfs:subClassOf 
        OutputAssignment: ,
        [ rdf:type owl:Restriction ;
          owl:onProperty hasParticipant: ;
          owl:someValuesFrom :Number ],
        [ rdf:type owl:Restriction ;
          owl:onProperty partOf: ;
          owl:someValuesFrom :DivisionProcess ] .

############################
#   INDIVIDUALS
############################

:num1 rdf:type :Number ;
      hasSpecifiedValue: "10"^^xsd:integer ;
      isSpecifiedInputOf: :div1 .

:num2 rdf:type :Number ;
      hasSpecifiedValue: "2"^^xsd:integer ;
      isSpecifiedInputOf: :div1 .

:quotient1 rdf:type :Number ;
      hasSpecifiedValue: "5"^^xsd:integer ;
      isSpecifiedOutputOf: :div1 .

:div1 rdf:type :DivisionProcess .

:numerator_assign rdf:type :NumeratorAssignment ;
    hasParticipant: :num1 ;
    partOf: :div1 .

:denominator_assign rdf:type :DenominatorAssignment ;
    hasParticipant: :num2 ;
    partOf: :div1 .

:quotient_assign rdf:type :QuotientAssignment ;
    hasParticipant: :quotient1 ;
    partOf: :div1 .
```


## More patterns at GitHub

More patterns can be found in the patterns folder :

[https://github.com/materialdigital/core-ontology/tree/main/patterns](https://github.com/materialdigital/core-ontology/tree/main/patterns)
