# The PMD Core Ontology Patterns

How to document patterns?

1. Create a sketch of a pattern in the [miro board](https://miro.com/app/board/uXjVNOTPrFo=/). Discuss and develop the pattern with the community.
2. Create a folder here with a short name describing the pattern. 
3. Create some example A-Box data and store it in a file called `shape-data.ttl`
4. Create the shacl shape and store it in a file called `shape.ttl`
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