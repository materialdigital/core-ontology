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
