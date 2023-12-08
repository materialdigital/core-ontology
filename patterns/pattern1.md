# Pattern 1: input and output of processes
## Purpose
Description on how to represent inputs and outputs of processes.

## Description
Typically, in PMD processes are subclasses of the 'planned process' (OBI:0000011), meaning 
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
[../shapes/shape1-data.ttl)](../shapes/shape1-data.ttl)

[../shapes/shape1.ttl](../shapes/shape1.ttl)

