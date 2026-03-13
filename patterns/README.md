# The PMD Core Ontology Patterns

This folder hosts a set of patterns and shapes that illustrate how the PMDco ontology can be applied in concrete modelling scenarios.

## Purpose & scope

This pattern collection is dedicated to reusable modelling templates: standardized patterns for how to represent processes, experiments, workflows, temporal/structural relationships, data flows, etc. These patterns enable ontology users to follow best-practice modelling schemas rather than starting from scratch.

By providing SHACL shapes, examples and pattern guidance, the folder supports users in shaping their data, aligning semantic models, and ensuring interoperability.

You can also find some examples in the documentation: [https://materialdigital.github.io/core-ontology/docs/patterns/](https://materialdigital.github.io/core-ontology/docs/patterns/)

## Contents & usage

Within this folder you will find modules, example files, perhaps SHACL shapes, RDF/OWL skeletons that demonstrate how to instantiate certain concepts of the ontology in realistic use-cases.

Users of the ontology—developers, data engineers, domain scientists—can pick a pattern from this folder as a starting point, adapt it to their scenario, and thereby ensure that they remain consistent with the ontology’s design, semantics and interoperability goals.

The autoshapes folder contains automatically generated SHACL shapes (or similar shapes/validation artefacts) that are derived from the ontology definitions. These shapes serve to validate that ontology modules and pattern instances conform to expected structure and constraints. In the workflow:

When a pull request or commit happens, the workflow triggers the SHACL validation job (as defined in shacl.yaml).


## Why it’s valuable

Patterns lower the barrier to adoption: instead of designing from first principles, you can use a vetted template aligned with PMDco’s semantics.

They promote consistency: multiple users modelling data in different domains but using PMDco can follow the same patterns, facilitating integration and reuse.

They support documentation & education: having examples and shapes makes the ontology more accessible for domain practitioners who are less familiar with ontology engineering.

They advance FAIR principles: by providing reusable modelling patterns, the repository helps make data more Findable, Accessible, Interoperable and Re-usable in the MSE context and beyond. This aligns with the ontology’s aims. 

## Automated processing of patterns

Whenever a commit or pull request is made, a workflow is triggered (via GitHub Actions) to perform validation of the ontology and its patterns (see: [.github/workflows/shacl.yaml](https://github.com/materialdigital/core-ontology/blob/main/.github/workflows/shacl.yaml) ).

The workflow executes SHACL validation steps: it runs a SHACL validator against the shapes and data files to check that the modelling patterns conform to the constraints.

If the validation passes, the build continues; if it fails, the workflow reports errors and the commit/PR is flagged so the authors can fix modelling issues.

Thus the workflow automates quality control of the patterns-folder: ensuring that changes do not break the defined SHACL shapes and that the ontology remains consistent with the modelling patterns.

The `autoshapes` folder contains automatically generated SHACL shapes that are derived from the ontology definitions. These shapes serve to validate that ontology modules and pattern instances conform to expected structure and constraints. 
The autoshapes are used as part of the validation workflow — they define the constraints that the ontology and pattern artefacts must satisfy.

The `unused` folder holds files (patterns, shapes) that have been deprecated, superseded, or are no longer actively used in the current version of the ontology/patterns. This folder is ignored by the workflow.

To include patterns in the automated workflow the documentation of the patterns have to meet the following requirements.

## How to document patterns?

1. Create a sketch of a pattern in the [miro board](https://miro.com/app/board/uXjVNOTPrFo=/). Discuss and develop the pattern with the community.
2. Create a folder here with a short name describing the pattern. 
3. Create some example A-Box data and store it in a file called `shape-data.ttl`
4. (optional) Create the shacl shape and store it in a file called `shape.ttl`
5. Creater a `pattern.md` Markdown file describing your pattern. 
Follow the template:

````{verbatim}
# Pattern: the pattern title
## Purpose
Short description of the purpose of the pattern.

## Description

Detailed description of the pattern.

## Visualization

<img src="pattern.png" alt="pattern image" width="750"/>
          
## Shapes and example data
[shape-data.ttl](shape-data.ttl)

[shape.ttl](shape.ttl)
````

!! please follow the naming conventions, because the patterns are evaluated through automated scripting.




# Further good practices

Patterns are used to:

* Validate data and ontology structures
* Demonstrate modeling approaches
* Support education and understanding

Because patterns are designed for human consumption, they should be easy to read and understand.

A pattern represents only a small part of a larger model. Therefore, patterns should remain simple and focused.


## Keep Patterns Small and Focused

A pattern should represent one atomic aspect of a model, not an entire complex model.

Avoid creating large and complex patterns that are difficult to understand quickly.

Guideline: 

* Do not create a pattern for an entire model.
* Create patterns for individual modeling aspects.

If a model is complex:

* Break it down into smaller conceptual pieces.
* Create separate patterns for each piece.

This improves: readability, maintainability, educational value

## Turtle Representation Size

Use turtle as serialization.

As a rule of thumb:

* The Turtle representation of a pattern should fit on a single screen.
* Recommended size: ~20–30 lines of Turtle code

This is not always possible, but it should be the target whenever feasible.

Keeping patterns small helps readers understand the pattern quickly.



## Example Data

Each pattern should include example data written in Turtle.

The example data should be:

* human-readable
* simple
* illustrative

**Prefixes**

Readable prefixes should be used for all resources. 
Create a prefix for **each** class and property. Name the prefix nicely, so it is readable. 

This significantly improves readability.

```turtle
@prefix ex: <http://example.org/> .
@prefix has_specified_input: <http://purl.obolibrary.org/obo/OBI_0000293> .
@prefix has_specified_output: <http://purl.obolibrary.org/obo/OBI_0000299> .
@prefix computing_process: <https://w3id.org/pmd/co/PMD_0000583> .

ex:process_1 a computing_process: ;
    has_specified_input: ex:data_1 ;
    has_specified_output: ex:data_2 .
```
Be explicit about special modeling details or assumptions.


## Creating Turtle Files

It is recommended to manually create Turtle files using a **text** editor.

Reasons:

* Better readability
	* Tools such as Protégé may generate Turtle that is difficult for humans to read.
For example:
	* unclear prefixes
	* overly compact formatting
* Better understanding
	* Writing Turtle manually helps developers learn and understand RDF modeling better.

	
	
## SHACL Shapes

When creating SHACL shapes for patterns, consider the following guidelines.

### Unique Identifier

* Each SHACL shape should have a unique IRI: Currently we have no strict organization scheme, so simply choose a reasonable unique identifier.
* Author Information: Author information can optionally be included, for example:
author name, contact, organization

This can be helpful but is not mandatory.

* Open vs Closed Shapes: Be explicit about whether a shape is: open (additional properties allowed), closed (only specified properties allowed)

Understanding this distinction is important when designing validation patterns.

## Reasoning

Reasoning is often required for correct validation.

Consider the following example.

Ontology hierarchy

```
Process
  └── ManufacturingProcess
        └── AssemblingProcess
```

The SHACL shape states:

```
ManufacturingProcess
  min 1 hasInput
  min 1 hasOutput
```

Example data

```
process_1 a AssemblingProcess .
process_1 hasInput data_1 .
process_1 hasOutput data_2 .
```

**Problem**

Without reasoning, SHACL may not recognize that:

```
AssemblingProcess ⊆ ManufacturingProcess
```

Therefore the validator may fail to apply the shape correctly.

**Solution**

Before validation, materialize inferred triples:

```
process_1 a ManufacturingProcess .
```

This ensures the shape is applied properly.

Best Practice: Always perform reasoning before SHACL validation.


## Ignored Properties

When reasoning is applied, additional triples may be inferred.
For example: sub-properties, transitive properties, etc.

These may create additional triples that introduce new properties or violate cardinality constraints.

For example, a sub-property may infer a super-property that was not explicitly present in the data.

If this causes validation problems, consider adding those properties to the ignored properties list in SHACL.


## Validation Workflow

The current validation workflow is as follows:

1 Merge ontology with the data
2 Run reasoning to materialize inferred triples
3 Run SHACL validation using pySHACL

```
Data + Ontology
        ↓
Reasoning / Inference
        ↓
Materialized Graph
        ↓
SHACL Validation (pySHACL)
```

Other workflows are of course possible, but this approach works well for most use cases.
