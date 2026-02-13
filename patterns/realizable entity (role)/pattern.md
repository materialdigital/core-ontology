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
