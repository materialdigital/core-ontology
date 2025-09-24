# Pattern: input and output of processes
## Purpose
Description on how to represent inputs and outputs of processes.

## Description
Typically, in PMD, processes are subclasses of the 'planned process' (OBI:0000011), meaning 
a process realizes some plan, which is the concretization of some plan specification. 
In contrary, natural processes are not realizing a particular plan that has been specified somehow.

The input of a process might be of different kinds, e.g. material entities, entities bearing some information content. 

To specify the input and output of a process, it is recommended to use the following properties:

```
has_specified_input (OBI:0000293)
has_specified_output (OBI:0000299)
```

The properties define the domain as 'planned process'. Both are sub property of 'has participant' which is defined in range 'occurent' and domain 'continuant'. 

A typical process can have any number of inputs and outputs or neither.

## Visualization
The following image shows some manufacturing process with multiple inputs and outputs.

<img src="https://github.com/materialdigital/core-ontology/blob/develop-3.0.0/patterns/pattern1.png?raw=true" alt="pattern1 image" width="750"/>

## Shapes and example data
[../shapes/shape1-data.ttl](../shapes/shape1-data.ttl)

[../shapes/shape1.ttl](../shapes/shape1.ttl)

## Interactive Playground
Auto-generated webeditor to create valid instances: [OO-LD Playground](https://oo-ld.github.io/playground-yaml/?data=N4Ig9gDgLglmB2BnEAuUMDGCA2MBGqIAZglAIYDuApomALZUCsIANOHgFZUZQD62ZAJ5gArlELwwAJzplsrEIgwALKrNSgAAlnhQqAD3FpwFeShDKoUCCgD0tio4B0FAMxPpAc1sAmAAx%2BPrZ%2BAOy2YKYAxApSACZEhJbWdg7Obh5S3gCMAJx5wUE%2BPgC0cUTFiIK6ZPrFSNFs%2BnRmFlY29o4ULu5etgAaALIAMra5OQActvBkDIgQZBhUCvqIsYltKZ3dGd7%2Bfln9wwDKKmpkDSBlyOZJ7ald6b17fsEHZRWnshdgeDAaIJoYGsbht7BARFJsB48GBcHgpGQpIIduEYbYAPIAIQAkrwFJoIFIqEQYPpUFApCIqABfNgQOixLDrayITauIEo%2BmxWxYWz4vBkRBLEEstkc3pcnlgWx6RBQPlsKCCCDCgFKlUKIGEQFrNgweDgoxaLXmH4wFABAI%2BHKufHq1U6kC08BiQ3%2FR2m34Wy3WnJ25UOrXU50AEiwdAYukIJ1UsgABCQpHGyHGuVgUAMyPAREQFlAIfrPAAFKRgRaIZCKmBQbCqktlmiVkD2wg%2FLg8GJUACOIhgROBAG1mwHNbqQPq3WxRNYxCAALp00sqqSwGj%2FFvGWA11UAFRHbFiNAwUhg0Dg8EIe5VcbjYCIcagyhgiDj%2BrlWcWCg3igphc7ZFidF4GwQRyUpKgD2JMgRGwIwQDTMAMyzHM8wLeBi1LctkGdE1QC3WtCGxAARL8R3MOUT3QhRD1zGC4MJBsKyyJ09QNWdN2rAjzGxNjxEVMiQERBFQLYRNZDgoVax4HxNT0OhrjwgSKL%2FNgw3oSM4J4uMiTkOMKGkbBYmTCAIFwDAyFgBAX0fMAhVvThuCgPTREMuM8CoOM6DAQ9sFrIzBTjRARBhByeFvJMiCoKBTiMohSzoB9VDjABrSRTCoWJPA8zwEQgZQFCobM6FQIc20c5ip1CqAZMq9soFtOdnTofVsTk64sjYER4BgHsqFatRrgpKlINo2CSvYOqKomxyZMaqdXXYxSNXMIShAUMSLMISSZtkgb1041V0QWpyACUaFEKRy1I5af0ozwCqK8ayp4LI%2FAUZ6oCyKaPqyWampatrUA6kAup6ql%2BvksDhpAGjoLGlBSqq1752DZ1EGUCJeCoKRSyka5x10bG83PL9Y1VGEwCgCiyAgAAWBQyA4GooYgkBkqoKgIF4BAqDvXgADc5Cpa5c2wIVnQ4WgL03ASEKQ7Ncx4NCMMYpsTXgzDGymid2MRyb3qq2b5pnIw9fKt7GupIA%3D%3D%3D) (see also [OO-LD Schema](https://github.com/OO-LD/schema))

[SHACL-Validation](https://shacl-playground.zazuko.com/#shapesGraph=%40prefix+rdf%3A+++%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E+.%0A%40prefix+sh%3A++++%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Fshacl%23%3E+.%0A%40prefix+xsd%3A+++%3Chttp%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema%23%3E+.%0A%40prefix+rdfs%3A++%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E+.%0A%40prefix+ex%3A++++%3Chttp%3A%2F%2Fwww.example.org%2F%23%3E+.%0A%40prefix+owl%3A+++%3Chttp%3A%2F%2Fwww.w3.org%2F2002%2F07%2Fowl%23%3E+.%0A%40prefix+pmd%3A+++%3Chttps%3A%2F%2Fw3id.org%2Fpmd%2Fco%2F%3E+.%0A%0Aex%3APattern1%0A++++a+sh%3ANodeShape+%3B%0A++++sh%3AtargetClass++pmd%3AManufacturingProcess+%3B+%0A++++sh%3Aproperty+%5B++++++++++++%0A++++++++sh%3Apath+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FOBI_0000293%3E+%3B++++++++%0A++++++++sh%3AminCount+1+%3B%0A++++%5D+%3B%0A++++sh%3Aproperty+%5B++++++++++++%0A++++++++sh%3Apath+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FOBI_0000299%3E+%3B+++++++%0A++++++++sh%3AminCount+1+%3B%0A++++%5D+%3B%0A+++%0A+++%23+sh%3Aclosed+true+%3B%0A+++%23+sh%3AignoredProperties+%28+rdf%3Atype+owl%3AtopDataProperty+owl%3AtopObjectProperty+%29+%3B%0A++++.%0A+%23%23%23%23%23%23+add+SHACL+vocabulary+%23%23%23%23%23%23+%0A&dataGraph=%7B%0A++%22%40context%22%3A+%7B%0A++++%22owl%22%3A+%22http%3A%2F%2Fwww.w3.org%2F2002%2F07%2Fowl%23%22%2C%0A++++%22rdf%22%3A+%22http%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%22%2C%0A++++%22xml%22%3A+%22http%3A%2F%2Fwww.w3.org%2FXML%2F1998%2Fnamespace%22%2C%0A++++%22xsd%22%3A+%22http%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema%23%22%2C%0A++++%22rdfs%22%3A+%22http%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%22%2C%0A++++%22obi%22%3A+%7B%0A++++++%22%40id%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FOBI_%22%2C%0A++++++%22%40prefix%22%3A+true%0A++++%7D%2C%0A++++%22pmdco%22%3A+%22https%3A%2F%2Fw3id.org%2Fpmd%2Fco%2F%22%2C%0A++++%22%40base%22%3A+%22https%3A%2F%2Fw3id.org%2Fpmd%2Fco%2Ftest%2F%22%2C%0A++++%22type%22%3A+%22%40type%22%2C%0A++++%22id%22%3A+%22%40id%22%2C%0A++++%22input%22%3A+%7B%0A++++++%22%40id%22%3A+%22obi%3A0000293%22%2C%0A++++++%22%40type%22%3A+%22%40id%22%0A++++%7D%2C%0A++++%22output%22%3A+%7B%0A++++++%22%40id%22%3A+%22obi%3A0000299%22%2C%0A++++++%22%40type%22%3A+%22%40id%22%0A++++%7D%0A++%7D%2C%0A++%22type%22%3A+%22pmdco%3AManufacturingProcess%22%2C%0A++%22id%22%3A+%22process1%22%2C%0A++%22input%22%3A+%5B%0A++++%22object1%22%2C%0A++++%22object2%22%0A++%5D%2C%0A++%22output%22%3A+%5B%0A++++%22object10%22%0A++%5D%0A%7D&shapesGraphFormat=text%2Fturtle&dataGraphFormat=application%2Fld%2Bjson)

