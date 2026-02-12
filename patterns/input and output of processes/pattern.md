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
