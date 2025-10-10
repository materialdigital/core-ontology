# Usage Patterns

In ontology development and usage, **usage patterns** play a critical role in addressing recurring modeling requirements. These patterns provide standardized, reusable semantic snippets that facilitate consistent representation of relationships between instances and entities. Furthermore, such patterns may be used to create SHACL shapes to include constraints in a knowledge representation. By following usage patterns, ontology users and developers can ensure uniformity, clarity, and reusability in their models.
![TableOfContents](https://github.com/user-attachments/assets/3510fa58-9774-4d04-a466-6a6bf7f2ddcd)

The sections below illustrate how to read and apply these patterns. Each pattern includes its purpose, description, relevant properties, visualization, and example.

---

## Table of Contents
Hereby we provide an overview of the patterns used in PMDco 3.0.0:

- [Pattern 1](#Pattern-1---Temporal-Region): Temporal Region
- [Pattern 2](#Pattern-2---Process-Chain): Process Chain
- [Pattern 3](#Pattern-3---Process-Inputs-and-Outputs): Process Inputs and Outputs
- [Pattern 4](#Pattern-4---Realizable-Entities): Realizable Entities
- [Pattern 5](#Pattern-5---Qualities): Qualities
- [Pattern 6](#Pattern-6---Scalar-Measurement): Scalar Measurement
- [Pattern 7](#Pattern-7---Scalar-Value-Specification): Scalar Value Specification
- [Pattern 8](#Pattern-8---Categorical-Value-Specification): Categorical Value Specification
- [Pattern 9](#Pattern-9---Material-and-Device-Specification): Material and Device Specification

---

## Example Patterns

### Pattern 1 - Temporal Region


- **Purpose**: Specifying the boundaries of a process on the time axis. 
- **Core Properties**: 
  - `bfo:occupies temporal region` ([BFO_0000199](http://purl.obolibrary.org/obo/BFO_0000199))
  - `bfo:proper temporal part of ` ([BFO_0000136](http://purl.obolibrary.org/obo/BFO_0000136))
  - `bfo:has first instant ` ([BFO_0000222](http://purl.obolibrary.org/obo/BFO_0000222))
  - `bfo:has last instant ` ([BFO_0000224](http://purl.obolibrary.org/obo/BFO_0000224))
  - `pmd:ends with ` ([PMD_0060003](https://w3id.org/pmd/co/PMD_0060003))
- **Example Use Case**: Specifying certain moments of time when some industrial process started or ended. 

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

### Pattern 2 - Process Chain

- **Purpose**: Represent complex processes, consisting of simultaneous and serial subprocesses. 
- **Core Properties**: 
  - `bfo:precedes` ([BFO_0000063](http://purl.obolibrary.org/obo/BFO_0000063))
  - `ro:has part` ([BFO_0000051](http://purl.obolibrary.org/obo/BFO_0000051))
  - `pmd:starts with` ([PMD_0060002](https://w3id.org/pmd/co/PMD_0060002))
  - `pmd:ends with ` ([PMD_0060003](https://w3id.org/pmd/co/PMD_0060003))
  - `pmd:simultaneous with` ([PMD_0060004](https://w3id.org/pmd/co/PMD_0060004))
- **Example Use Case**: Specifying the structure of commplex manufacturing processes consisting of several stages.

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
  "ex:process parent" -> "ex:process step1": "pmd:starts_with"
  "ex:process parent" -> "ex:process step3": "pmd:ends_with"

  "ex:process parent" -> "ex:process step1": "ro:has part"
  "ex:process parent" -> "ex:process step2a": "ro:has part"
  "ex:process parent" -> "ex:process step2b": "ro:has part"
  "ex:process parent" -> "ex:process step3": "ro:has part"

  "ex:process step1" -> "ex:process step2a": "bfo:precedes"
  "ex:process step1" -> "ex:process step2b": "bfo:precedes"
  "ex:process step1" -> "ex:process step3": "bfo:precedes"

  "ex:process step2a" -> "ex:process step3": "bfo:precedes"
  "ex:process step2a" -> "ex:process step2b": "pmd:simultaneous_with"
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
@prefix starts_with: <https://w3id.org/pmd/co/PMD_0060002> . #ObjectProperty
@prefix ends_with: <https://w3id.org/pmd/co/PMD_0060003> . #ObjectProperty
@prefix simultaneous_with: <https://w3id.org/pmd/co/PMD_0060004> . #ObjectProperty

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

### Pattern 3 - Process Inputs and Outputs

- **Purpose**: Describes how to represent inputs and outputs for planned processes typically involving material entities or information-bearing entities.
- **Core Properties**: 
  - `obi:has_specified_input` [OBI_0000293](http://purl.obolibrary.org/obo/OBI_0000293)
  - `obi:has_specified_output` [OBI_0000299](http://purl.obolibrary.org/obo/OBI_0000299)
- **Example Use Case**: A planned process with possibility of multiple inputs and outputs, e.g., testing properties of a metallic sample, or transforming a piece of material into another product.

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
  individual: {
    style: {
      fill: "lightgrey"
    }
  }
}
bfo*.class: bfoclazz
pmd*.class: pmdclazz
ex*.class: individual

"ex:process 1" -> "ex:object1": "obi:has_specified_input"
"ex:process 1" -> "ex:object2": "obi:has_specified_output"
"ex:process 2" -> "ex:object2": "obi:has_specified_input"
"ex:process 2" -> "ex:object3": "obi:has_specified_output"

"ex:process 1" -> "pmd:manufacturing process": "rdf:type"
"ex:process 2" -> "pmd:coating process": "rdf:type"
"pmd:manufacturing process" -> "bfo:process": "owl:subClassOf"
"pmd:coating process" -> "pmd:manufacturing process": "owl:subClassOf"

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

@prefix manufacturing_process: <https://w3id.org/pmd/co/PMD_0000833> .
@prefix coating: <https://w3id.org/pmd/co/PMD_0000563> .
@prefix has_specified_input: <http://purl.obolibrary.org/obo/OBI_0000293> .
@prefix has_specified_output: <http://purl.obolibrary.org/obo/OBI_0000299> .
@prefix object: <http://purl.obolibrary.org/obo/BFO_0000030> .

<https://w3id.org/pmd/co/test> rdf:type owl:Ontology  .

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

### Pattern 4 - Realizable Entities

- **Purpose**: Represent characteristics of the objects, brought to existence by specific situation.
- **Core Properties**: 
  - `bfo:bearerOf` 
  - `bfo:concretizes`
  - `bfo:realizes`
  - `bfo:hasParticipant`
- **Example Use Case**: Specifying the role of specimen, which material object undertakes during a process. 
  
![Visualization of Pattern 4](https://github.com/user-attachments/assets/38b57e8a-c7d4-43e4-ad65-7b9204d2101e)

---

### Pattern 5 - Qualities

- **Purpose**: Represent inherent characteristics of the objects, having certain scalar values at moments/periods of time.
- **Core Properties**: 
  - `bfo:bearerOf` 
  - `bfo:existAt`
  - `iao:isAbout`
  - `pmd:derivesFrom`
- **Example Use Case**: Specifying that value of hardness of a specimen at certain point of time.

![Visualization of Pattern 5](https://github.com/user-attachments/assets/a707b8ba-9835-491c-bd5c-48180e1e7cbd)

---

### Pattern 6 - Scalar Measurement

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

### Pattern 7 - Scalar Value Specification

- **Purpose**: Represents scalar physical quantities, combining a numerical value and a unit.
- **Core Properties**: 
  - `obi:hasSpecifiedNumericValue`
  - `iao:hasMeasurementUnitLabel`
  - `pmd:hasValueSpecification`
  - `pmd:specifiesValueOf`
- **Example Use Case**: Specifying measurements like length, mass, or time with standard units.

![Visualization of Pattern 7](https://github.com/user-attachments/assets/91e5d524-141f-4e49-b110-c98994cb38be)

---

### Pattern 8 - Categorical Value Specification

- **Purpose**: Represents object characteristics, described by belonging to some category.
- **Core Properties**: 
  - `obi:hasSpecifiedValue`
  - `iao:isQualityMeasuredAs`
  - `pmd:hasValueSpecification`
  - `pmd:specifiesValueOf`
- **Example Use Case**: Specifying that material belongs to a certain category, e.g., is a polymer.
  
![Visualization of Pattern 8](https://github.com/user-attachments/assets/38d70bbd-29d1-47c3-b73b-6e4ebc12feef)

---
### Pattern 9 - Material and Device Specification

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
