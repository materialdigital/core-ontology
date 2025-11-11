# owl2shacl
OWL 2 SHACL conversion rules, adapted from TopQuadrant's original post at https://www.topquadrant.com/from-owl-to-shacl-in-an-automated-way/

These rules can be used by SHACL Play at **https://shacl-play.sparna.fr/play/convert** to convert an OWL file to SHACL.


This comes in 3 flavors :
1. **open** flavor does not close the Shapes and does not verify the domain of properties
2. **semi-closed** flavor does verify the domains of the properties in the ontology, but does not close the shapes, leaving open the possibility to have properties of other ontologies in the data.
3. **closed** closes all shapes, so does not allow the use of properties outside of the ones declared in the ontology, and closing the shapes verifies that each property is asserted on a valid entity according to its domain declaration
