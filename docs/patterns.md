# Usage Patterns

In ontology development and usage, **usage patterns** play a critical role in addressing recurring modeling requirements. These patterns provide standardized, reusable semantic snippets that facilitate consistent representation of relationships between instances and entities. Furthermore, such patterns may be used to create SHACL shapes to include constraints in a knowledge representation. By following usage patterns, ontology users and developers can ensure uniformity, clarity, and reusability in their models.

The sections below illustrate how to read and apply these patterns. Each pattern includes its purpose, description, relevant properties, visualization, and examples. In particular, patterns are given in more detail in the [pattern section of the PMDco repository](https://github.com/materialdigital/core-ontology/tree/develop-3.0.0/patterns). Although these patterns are already documented separately, they are referenced here as a guide for understanding their structure and applicability.

---

## Example Patterns

### Pattern 1: Input and Output of Processes
**Purpose**: Describes how to represent inputs and outputs for planned processes.

- **Core Properties**: 
  - `has_specified_input` (`OBI:0000293`)
  - `has_specified_output` (`OBI:0000299`)
- **Key Insight**: A planned process can have multiple inputs and outputs, typically involving material entities or information-bearing entities.
- **How to Interpret**: Inputs and outputs are linked to processes using the above properties to indicate participation.

![Visualization of Pattern 1](https://github.com/materialdigital/core-ontology/blob/develop-3.0.0/patterns/pattern1.png?raw=true)

[Explore Example Data, Pattern 1](https://github.com/materialdigital/core-ontology/blob/develop-3.0.0/shapes/shape1-data.ttl)

---

### Pattern 2: Scalar Value Specification with Value and Unit
**Purpose**: Represents scalar physical quantities, combining a numerical value and a unit.

- **Core Idea**: Use a BNode for scalar quantities, ensuring each quantity has exactly one value and one unit.
- **Example Use Case**: Specifying measurements like length, mass, or time with standard units.

![Visualization of Pattern 2](https://raw.githubusercontent.com/materialdigital/core-ontology/develop-3.0.0/patterns/pattern2.png)

[Explore Example Data, Pattern 2](https://github.com/materialdigital/core-ontology/blob/develop-3.0.0/shapes/shape2-data1.ttl)

---

### Pattern 6: Device Identifier
**Purpose**: Ensures every device has at least one identifier for unambiguous identification.

- **Description**: A device is associated with an identifier (`IAO:0020000`) or symbol (`IAO:0000028`), along with a value specification.
- **Relevance**: Useful for tracking devices in systems where precise identification is crucial.

![Visualization of Pattern 6](https://raw.githubusercontent.com/materialdigital/core-ontology/develop-3.0.0/patterns/pattern6.png)

[Explore Example Data, Pattern 6](https://github.com/materialdigital/core-ontology/blob/develop-3.0.0/shapes/shape6-data.ttl)
