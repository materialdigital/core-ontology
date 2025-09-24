# Pattern: chemical composition of a material
## Purpose
Description on how to represent the chemical composition of a (typical metallic) material

## Description
The shape illustrates how to describe the chemical composition of a (metallic) object. To this end it first uses the "consists of" relation to point to a material, which is an uncounted portion of matter. This matter has a morphologic quality, the chemical composition. The chemical composition quality is quantified by a generically dependent "chemical composition specification", a complex information content entity that has several scalar value specifications as parts. Those scalar value specifications (expressing mass fraction, mol fraction, volume fraction, ...) in turn quantify the relational property between a portion of (pure) substance and the material which is the sum of such portions. 

## Visualization
The following image shows some manufacturing process with multiple inputs and outputs.

<img src="pattern.png?raw=true" alt="pattern7 image" width="750"/>

## SHACL shape and example data
[shape-data.ttl](shape-data.ttl)

[shape.ttl](shape.ttl)

