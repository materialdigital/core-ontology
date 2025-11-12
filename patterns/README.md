# The PMD Core Ontology Patterns

This folder hosts a set of patterns and shapes that illustrate how the PMDco ontology can be applied in concrete modelling scenarios.

## Purpose & scope

This pattern collection is dedicated to reusable modelling templates: standardized patterns for how to represent processes, experiments, workflows, temporal/structural relationships, data flows, etc. These patterns enable ontology users to follow best-practice modelling schemas rather than starting from scratch.

By providing SHACL shapes, examples and pattern guidance, the folder supports users in shaping their data, aligning semantic models, and ensuring interoperability.

You can also find some examples in the documentation: [https://materialdigital.github.io/core-ontology/docs/patterns/](https://materialdigital.github.io/core-ontology/docs/patterns/)

## Contents & usage

Within this folder you will find modules, example files, perhaps SHACL shapes, RDF/OWL skeletons that demonstrate how to instantiate certain concepts of the ontology in realistic use-cases.

Users of the ontology—developers, data engineers, domain scientists—can pick a pattern from this folder as a starting point, adapt it to their scenario, and thereby ensure that they remain consistent with the ontology’s design, semantics and interoperability goals.

## Why it’s valuable

Patterns lower the barrier to adoption: instead of designing from first principles, you can use a vetted template aligned with PMDco’s semantics.

They promote consistency: multiple users modelling data in different domains but using PMDco can follow the same patterns, facilitating integration and reuse.

They support documentation & education: having examples and shapes makes the ontology more accessible for domain practitioners who are less familiar with ontology engineering.

They advance FAIR principles: by providing reusable modelling patterns, the repository helps make data more Findable, Accessible, Interoperable and Re-usable in the MSE context and beyond. This aligns with the ontology’s aims. 

## Automated processing of patterns

Whenever a commit or pull request is made, a workflow is triggered (via GitHub Actions) to perform validation of the ontology and its patterns.

see: [.github/workflows/shacl.yaml](https://github.com/materialdigital/core-ontology/blob/main/.github/workflows/shacl.yaml)

The workflow executes SHACL validation steps: it runs a SHACL validator against the shapes and data files to check that the modelling patterns conform to the constraints.

If the validation passes, the build continues; if it fails, the workflow reports errors and the commit/PR is flagged so the authors can fix modelling issues.

Thus the workflow automates quality control of the patterns-folder: ensuring that changes do not break the defined SHACL shapes and that the ontology remains consistent with the modelling patterns.

To include patterns in this automated workflow the documentation of the patterns have to meet the following requirements.

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