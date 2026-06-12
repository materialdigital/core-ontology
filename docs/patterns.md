<!--@Document_indicator: Text,links, Patterns -->

<!--
LOCAL PREVIEW HELP
Each pattern below renders from the remote GitHub (main) sources by default.
To preview a pattern from your local working copy before pushing, change that
pattern's three remote tag values to local relative paths (see the example below),
then rebuild, for example (run from the repo root):
    python docs/docs_HTML/scripts/build_all.py -M patterns -m docs/patterns.md -o docs/patterns.html
The local form uses the https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/NAME/... style with plain spaces; paths are
resolved relative to this file, so no diagrams-root argument is needed.
Example - Pattern 1's three tag values in local form (each value goes inside its own
HTML comment tag, e.g. @Graphviz_renderer:VALUE):
    @Graphviz_renderer  ->  https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/duality object material/shape-data.ttl
    @md_file_renderer   ->  https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/duality object material/pattern.md
    @source_code_renderer  ->  https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/duality object material/shape-data.ttl
-->

<!--
DIAGRAM RENDERING NOTES
-----------------------
Pattern diagrams are rendered interactively with Cytoscape.js + ELK
(clean layered, top-to-bottom layout). Each @Graphviz_renderer tag below
produces three switchable views: "Full Hierarchy" / "Direct Parents" /
"Pattern Only". Object-property edge labels are shown by default; hover any
edge to reveal its label (incl. rdfs:subClassOf / rdf:type). Nodes can be
dragged to rearrange the graph.

Available renderer tag variants:
    @Graphviz_renderer:URL              default (all three hierarchy views)
    @Graphviz_renderer_only_upper:URL   default view = "Direct Parents"
    @Graphviz_renderer_only_file:URL    default view = "Pattern Only"
    @Graphviz_renderer_with_BNode:URL   additionally draws blank/anonymous
                                        nodes as small empty circles. Use this
                                        only for patterns that actually define
                                        blank nodes (e.g. an inline [ ... ]).
-->

<!--Please provide the link to the pattern (raw data ttl file) in the repository-->

# Usage patterns in ontology development and formal knowledge representation

In ontology development and usage, usage patterns address recurring modeling requirements by providing standardized, reusable semantic snippets. These patterns ensure consistent representation of relationships between instances and entities across knowledge graphs. In OWL ontologies, modeling choices are expressed through axioms, which define the structure and constraints of the domain. However, the open world assumption makes it difficult to enforce completeness checks on knowledge graphs using ontology reasoners alone. This is where SHACL shapes become essential: they enable validation of knowledge graphs by checking data against defined structural and completeness requirements.

By adopting usage patterns and supporting them with SHACL validation, ontology developers and users can ensure:

-    Uniformity and consistency across models
-    Clarity in semantic representation
-    Reusability of proven solutions
-    Verifiable completeness and data quality of knowledge graphs


Each pattern section below includes its purpose, description, relevant properties, visualization, and examples. Together with corresponding SHACL shapes, these patterns provide both semantic guidance and validation mechanisms for reliable knowledge representation.

# Section 1:  The steel ingot story
To illustrate how usage patterns apply in practice, we follow a single ingot of steel through a part of its life: from casting through rolling to a measurement on a product (a slab) that has been produced from the ingot. We start with the philosophical duality statue/clay problem, demonstrates how the material entities persists or vanish through transformations of form, composition, and properties. By observing the entites at each stage, we see how patterns address recurring modeling challenges: object identity, temporal change, process chains, and measurement contexts. 


## Pattern 1 - Duality of object and material
<!--@md_file_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/duality%20object%20material/pattern.md-->
<!--@Graphviz_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/duality%20object%20material/shape-data.ttl-->
<!--@source_code_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/duality%20object%20material/shape-data.ttl-->
(see folder:     [patterns/duality object material/](https://github.com/materialdigital/core-ontology/tree/main/patterns/duality%20object%20material) )
---

## Pattern 2a - Temporal dimensions of a process ...
<!--@md_file_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/temporal%20region/pattern.md-->
<!--@Graphviz_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/temporal%20region/shape-data.ttl-->
<!--@source_code_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/temporal%20region/shape-data.ttl-->
(see folder:     [patterns/temporal region/](https://github.com/materialdigital/core-ontology/tree/main/patterns/temporal%20region) )
---
## Pattern 2b - ... and the participant objects states

<!--@md_file_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/TQC%20microstructure%20of%20ingot/pattern.md-->
<!--@Graphviz_renderer_with_BNode:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/TQC%20microstructure%20of%20ingot/shape-data.ttl-->
<!--@source_code_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/TQC%20microstructure%20of%20ingot/shape-data.ttl-->
(see folder:     [patterns/TQC microstructure of ingot/](https://github.com/materialdigital/core-ontology/tree/main/patterns/TQC%20microstructure%20of%20ingot) )
---


## Pattern 3 - A process with a chain of subprocesses
<!--@md_file_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/process%20chain/pattern.md-->
<!--@Graphviz_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/process%20chain/shape-data.ttl-->
<!--@source_code_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/process%20chain/shape-data.ttl-->
(see folder:     [patterns/process chain/](https://github.com/materialdigital/core-ontology/tree/main/patterns/process%20chain) )
---

## Pattern 4 - A manufacturing process with its input and outputs
<!--@md_file_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/input%20and%20output%20of%20processes/pattern.md-->
<!--@Graphviz_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/input%20and%20output%20of%20processes/shape-data.ttl-->
<!--@source_code_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/input%20and%20output%20of%20processes/shape-data.ttl-->
(see folder:     [patterns/input and output of processes/](https://github.com/materialdigital/core-ontology/tree/main/patterns/input%20and%20output%20of%20processes) )
---

## Pattern 5 - Realization of a role
<!--@md_file_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/realizable%20entity%20(role)/pattern.md-->
<!--@Graphviz_renderer_with_BNode:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/realizable%20entity%20(role)/shape-data.ttl-->
<!--@source_code_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/realizable%20entity%20(role)/shape-data.ttl-->
(see folder:     [patterns/realizable entity (role)/](https://github.com/materialdigital/core-ontology/tree/main/patterns/realizable%20entity%20(role)) )
---

# Section 2:  FAP (frequently applied patterns)
Some facts are frequently expressed in the domain of MSE. The propably most frequent statement type is one about the properties of a material. From the ontological point of view there are different types of propreties, which are presented in pattern 6. Another frequent situation is to talk about values that result from a measurements and to talk about values that we consider as specifications, like setpoints. This is addressed in pattern 7. If the values a scalar physical quanitities with magnitude and physical unit, we can express the using pattern 8.


## Pattern 6 - Different types of material properties
<!--@md_file_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/material%20property%20(quality)/pattern.md-->
### fundamental property
<!--@Graphviz_renderer_with_BNode:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/material%20property%20(quality)/shape-data_fundamental.ttl-->
### behavoiral property
<!--@Graphviz_renderer_with_BNode:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/material%20property%20(quality)/shape-data_behavioral.ttl-->
### relational property
<!--@Graphviz_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/material%20property%20(quality)/shape-data_relational.ttl-->
<!--@source_code_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/material%20property%20(quality)/shape-data.ttl-->
(see folder:     [patterns/material property (quality)/](https://github.com/materialdigital/core-ontology/tree/main/patterns/material%20property%20(quality)) )
---


## Pattern 7 - Measurement and setpoint.
<!--@md_file_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/measurement/pattern.md-->
<!--@Graphviz_renderer_with_BNode:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/measurement/shape-data.ttl-->
<!--@source_code_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/measurement/shape-data.ttl-->
<!--@Graphviz_renderer_with_BNode:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/measurement/shape-data_setpoint.ttl-->
<!--@source_code_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/measurement/shape-data_setpoint.ttl-->


(see folder:     [patterns/measurement/](https://github.com/materialdigital/core-ontology/tree/main/patterns/measurement) )


---

## Pattern 8a - Expressing a (scalar) value with "Scalar Value Specification" ...
<!--@md_file_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/scalar%20value%20specification/pattern.md-->
<!--@Graphviz_renderer_with_BNode:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/scalar%20value%20specification/shape-data.ttl-->
<!--@source_code_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/scalar%20value%20specification/shape-data.ttl-->


(see folder:     [patterns/scalar value specification/](https://github.com/materialdigital/core-ontology/tree/main/patterns/scalar%20value%20specification) )


---

## Pattern 8b - ... and expressing a categorical value 
<!--@md_file_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/categorical%20value%20specification/pattern.md-->
<!--@Graphviz_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/categorical%20value%20specification/shape-data.ttl-->
<!--@source_code_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/categorical%20value%20specification/shape-data.ttl-->


(see folder:     [patterns/categorical value specification/](https://github.com/materialdigital/core-ontology/tree/main/patterns/categorical%20value%20specification) )


---
# Section 3:  the world of computation and simulation
Many scientific questions in MSE are addressed using computational materials science. This section introduces the representation of simulations and their in- and outputs.  

## Pattern 9 - Simulation with in- and output
<!--@md_file_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/simulation%20inout%20simple/pattern.md-->
<!--@Graphviz_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/simulation%20inout%20simple/shape-data.ttl-->
<!--@source_code_renderer:https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/patterns/simulation%20inout%20simple/shape-data.ttl-->

(see folder:     [patterns/simulation inout simple/](https://github.com/materialdigital/core-ontology/tree/main/patterns/simulation%20inout%20simple) )


---

# More patterns at GitHub

More patterns can be found in the patterns folder :

[https://github.com/materialdigital/core-ontology/tree/main/patterns](https://github.com/materialdigital/core-ontology/tree/main/patterns)
