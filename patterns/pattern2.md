# Pattern 2: scalar value specification with value and unit
## Purpose
Description on how to represent scalar physical quanities with value and unit.

## Description
Typically, scalar physical quantitites will be represented by a resource with associated 
value (aka magnitude) and a unit. Units will typically be resources from external ontologies. 
A scalar physical quantity has exactly one value and exactly one unit. 
You should consider modelling the resource as a BNode.


## Visualization
The following image shows an instance of a scalar value specification with value and unit. 

<img src="https://raw.githubusercontent.com/materialdigital/core-ontology/develop-3.0.0/patterns/pattern2.png" alt="pattern2 image" width="750"/>
          
## Shapes and example data
[../shapes/shape2-data1.ttl](../shapes/shape2-data1.ttl)

[../shapes/shape2.ttl](../shapes/shape2.ttl)

## Interactive Playground
Auto-generated webeditor to create valid instances: [OO-LD Playground](https://oo-ld.github.io/playground-yaml/?data=N4Ig9gDgLglmB2BnEAuUMDGCA2MBGqIAZglAIYDuApomALZUCsIANOHgFZUZQD62ZAJ5gArlELwwAJzplsrEIgwALKrNSgAAlnhQqAD3FpwFeShDKoUCCgD0tio4B0FAMxPpAc1sAmAAx%2BPrZ%2BAOy2YKYAxApSACZEhJbWdg7Obh5S3gCMAJx5wUE%2BPgC0cUTFiIK6ZPrFSNFs%2BnRmFlY29o4ULu5etgAaALIAMra5OQActvBkDIgQZBhUCvqIsYltKZ3dGd7%2Bfln9wwDKKmpkDSBlyOZJ7ald6b17fsEHZRWnshdgeDAaIJoYGsbht7BARFJsB48GBcHgpGQpIIduEYbYAPIAIQAkrwFJoIFIqEQYPpUFApCIqABfNgwMhgf6A4GtZJgiFQn6w%2FAIpEorm2bEAQXReLYBKJJLJKApVNpIAgdFiWHW1kQm1cQJRititiwtnxeDIiCWILVGq1vR1erAtj0iCgBrYUEEEFNAJdboUQMIzIUIgAjiJYkZWRB1fYgyGUQA3MAYMh4WwieAwR0KGNyKmEH4wFABfY5Vwhf2poxaH3mHVYFAptP4z3uv3U%2BUAEiwdAYukIJ1UsgABCQpP2yP3q2AUAMyPAREQFlAITB4J4AApSeM0ZDOtPYd0nOSI%2FsANSzVH7RzdGBgJITsAQCkbOc43HEbCJQZgROBAG0QI%2B6WsbCZtg2ZsHW4gALpsGQsSxGmcDTNga6QFQUiwDQqBztgJpsISKFoTAGHGI%2BxE7u6AAqrpLM6VGEA6UhLp4MRUDB6LwNggjkpSVBsFQM50Kgv65vmAS5K4WQgFBICxMSZAiNgobCQWYkSWwkB3kg%2FwAOUdl2obkcoMCIP2RmDtI%2FY4IIZnDlAqj9gAqtiCh8SIdC8LAUC7tcQm%2FCg%2B4CFIJ4gVQF7cNemBkBpkktgB%2FwebuhDYgAIg%2BtHmPRjEKDJc7yaGQbTh5ghBVSEnysB2akZ57rFdRf5pSA%2FF4KhWWyblqBZE4WTyuBcX1Rly4KEOsihouzn8YJICBsGUCTv6UYzQA0jA2BgAA4gMc3TSgSUAKKrbwADCklsNlckKYQU0hrNanQAh1ygDp9B6YQBmmaZQ4WexVkfbZZ6OWNrnuWR3kgAJbAANZMWwAANR0QS2MWKMoES8Kh65SNcIBLnoCI8AhD59u6MJgFA9FkBAAAsChkBwNRcVSENUFQEC8AgVBgEQvDlURWEmvKHC0PAvVeuYSmiUWqlYyy%2BW6GmRWnpL3PtZ1YFlhd82zS2QA) (see also [OO-LD Schema](https://github.com/OO-LD/schema))

[SHACL-Validation](https://shacl-playground.zazuko.com/#shapesGraph=%40prefix+rdf%3A+++%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E+.%0A%40prefix+sh%3A++++%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Fshacl%23%3E+.%0A%40prefix+xsd%3A+++%3Chttp%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema%23%3E+.%0A%40prefix+rdfs%3A++%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E+.%0A%40prefix+ex%3A++++%3Chttp%3A%2F%2Fwww.example.org%2F%23%3E+.%0A%40prefix+owl%3A+++%3Chttp%3A%2F%2Fwww.w3.org%2F2002%2F07%2Fowl%23%3E+.%0A%40prefix+pmd%3A+++%3Chttps%3A%2F%2Fw3id.org%2Fpmd%2Fco%2F%3E+.%0A%40prefix+obi%3A+++%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F%3E+.%0A%40prefix+pmdco%3A+%3Chttps%3A%2F%2Fw3id.org%2Fpmd%2Fco%2F%3E+.%0A%0Aex%3AShape2+rdf%3Atype+sh%3ANodeShape+%3B%0A++++++++++sh%3AtargetClass++%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FOBI_0001931%3E+%3B+%23+obi%3Ascalar+value+specification%0A++++%0A%09%23+Exactly+one+property+pointing+to+the+scalar+value%0A++++sh%3Aproperty+%5B%0A++++++++++++sh%3Apath+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FOBI_0001937%3E+%3B+%23obi%3Ahas+specified+numeric+value%0A++++++++++++sh%3AminCount+1+%3B%0A++++++++++++sh%3AmaxCount+1+%0A++++++++%5D%3B%0A++++%0A++++%23+Exactly+one+property+pointing+to+the+physical+unit%0A++++sh%3Aproperty+%5B++++++++++++%0A++++++++++++sh%3Apath+pmd%3Aunit+%3B%0A++++++++++++sh%3AminCount+1+%3B%0A++++++++++++sh%3AmaxCount+1+%0A++++++++%5D%3B%0A+++%0A+++sh%3Aclosed+true+%3B%0A+++sh%3AignoredProperties+%28+rdf%3Atype+owl%3AtopDataProperty+owl%3AtopObjectProperty+%29+.%0A&dataGraph=%7B%0A++%22%40context%22%3A+%7B%0A++++%22owl%22%3A+%22http%3A%2F%2Fwww.w3.org%2F2002%2F07%2Fowl%23%22%2C%0A++++%22rdf%22%3A+%22http%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%22%2C%0A++++%22xml%22%3A+%22http%3A%2F%2Fwww.w3.org%2FXML%2F1998%2Fnamespace%22%2C%0A++++%22xsd%22%3A+%22http%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema%23%22%2C%0A++++%22rdfs%22%3A+%22http%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%22%2C%0A++++%22obi%22%3A+%7B%0A++++++%22%40id%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FOBI_%22%2C%0A++++++%22%40prefix%22%3A+true%0A++++%7D%2C%0A++++%22iao%22%3A+%7B%0A++++++%22%40id%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FIAO_%22%2C%0A++++++%22%40prefix%22%3A+true%0A++++%7D%2C%0A++++%22pmdco%22%3A+%22https%3A%2F%2Fw3id.org%2Fpmd%2Fco%2F%22%2C%0A++++%22%40base%22%3A+%22https%3A%2F%2Fw3id.org%2Fpmd%2Fco%2Ftest%2F%22%2C%0A++++%22type%22%3A+%22%40type%22%2C%0A++++%22id%22%3A+%22%40id%22%2C%0A++++%22uqudt%22%3A+%22https%3A%2F%2Fqudt.org%2Fvocab%2Funit%2F%22%2C%0A++++%22value%22%3A+%22obi%3A0001937%22%2C%0A++++%22unit%22%3A+%7B%0A++++++%22%40id%22%3A+%22pmdco%3Aunit%22%2C%0A++++++%22%40type%22%3A+%22%40id%22%0A++++%7D%0A++%7D%2C%0A++%22type%22%3A+%22obi%3A0001931%22%2C%0A++%22id%22%3A+%22quantityValue1%22%2C%0A++%22value%22%3A+1.1%2C%0A++%22unit%22%3A+%22uqudt%3AM%22%0A%7D&shapesGraphFormat=text%2Fturtle&dataGraphFormat=application%2Fld%2Bjson)


