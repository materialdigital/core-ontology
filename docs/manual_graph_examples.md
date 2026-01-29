# Manual Diagram Examples
<!--@Document_indicator: Text, Diagrams, Examples -->

This page demonstrates the manual diagram embedding feature for PMDco documentation. Use these examples as templates for creating your own diagrams using `@Graphviz_renderer_manual` and `@Mermaid_renderer_manual` tags.

## Quick Reference

### Graphviz (DOT) Syntax

To embed a Graphviz diagram, use this format:

```text
<​!--@Graphviz_renderer_manual: Your Diagram Title -->
```​dot
digraph G {
    // Your DOT code here
}
```​
```

### Mermaid Syntax

To embed a Mermaid diagram, use this format:

```text
<​!--@Mermaid_renderer_manual: Your Diagram Title -->
```​mermaid
graph TD
    // Your Mermaid code here
```​
```

---

## Basic Examples

### Simple Class Hierarchy (Graphviz)

A minimal example showing class inheritance with color-coded ontology prefixes:

<!--@Graphviz_renderer_manual: Simple Class Hierarchy -->
```dot
digraph SimpleHierarchy {
    rankdir=TB;
    node [shape=box, style="rounded,filled", fontname="Arial", fontsize=11];
    edge [fontname="Arial", fontsize=10];

    // BFO classes (blue)
    Entity [label="bfo:Entity", fillcolor="#E3F2FD"];
    Continuant [label="bfo:Continuant", fillcolor="#E3F2FD"];
    Occurrent [label="bfo:Occurrent", fillcolor="#E3F2FD"];

    // PMD classes (green)
    Material [label="pmd:Material", fillcolor="#E8F5E9"];
    Process [label="pmd:Process", fillcolor="#E8F5E9"];

    // Relationships
    Entity -> Continuant [label="subClassOf"];
    Entity -> Occurrent [label="subClassOf"];
    Continuant -> Material [label="subClassOf"];
    Occurrent -> Process [label="subClassOf"];
}
```

### Simple Flowchart (Mermaid)

A basic flowchart showing a linear process:

<!--@Mermaid_renderer_manual: Simple Flowchart -->
```mermaid
flowchart LR
    A[Start] --> B[Process]
    B --> C[End]

    style A fill:#E8F5E9
    style B fill:#E3F2FD
    style C fill:#FFF3E0
```

---

## Intermediate Examples

### PMDco Class Hierarchy with Properties

This example shows class relationships with object properties:

<!--@Graphviz_renderer_manual: PMDco Class Hierarchy with Properties -->
```dot
digraph PMDcoHierarchy {
    rankdir=TB;
    node [shape=box, style="rounded,filled", fontname="Arial", fontsize=11];
    edge [fontname="Arial", fontsize=10];

    // BFO classes (blue)
    Entity [label="bfo:Entity", fillcolor="#E3F2FD"];
    Continuant [label="bfo:Continuant", fillcolor="#E3F2FD"];
    Occurrent [label="bfo:Occurrent", fillcolor="#E3F2FD"];
    Process [label="bfo:Process", fillcolor="#E3F2FD"];

    // PMD classes (green)
    MaterialEntity [label="pmd:MaterialEntity", fillcolor="#E8F5E9"];
    ProcessingStep [label="pmd:ProcessingStep", fillcolor="#E8F5E9"];
    Measurement [label="pmd:Measurement", fillcolor="#E8F5E9"];

    // Subclass relationships (solid)
    Entity -> Continuant [label="rdfs:subClassOf"];
    Entity -> Occurrent [label="rdfs:subClassOf"];
    Continuant -> MaterialEntity [label="rdfs:subClassOf"];
    Occurrent -> Process [label="rdfs:subClassOf"];
    Process -> ProcessingStep [label="rdfs:subClassOf"];
    Process -> Measurement [label="rdfs:subClassOf"];

    // Object properties (dashed blue)
    ProcessingStep -> MaterialEntity [label="has_input", style=dashed, color="#1565C0"];
    ProcessingStep -> MaterialEntity [label="has_output", style=dashed, color="#1565C0"];
    Measurement -> MaterialEntity [label="measures", style=dashed, color="#1565C0"];
}
```

### Data Processing Workflow (Mermaid)

A workflow diagram with subgraphs and conditional logic:

<!--@Mermaid_renderer_manual: Data Processing Workflow -->
```mermaid
flowchart LR
    subgraph Input["Input Stage"]
        A[Raw Material] --> B[Sample Preparation]
    end

    subgraph Processing["Processing Stage"]
        B --> C{Quality Check}
        C -->|Pass| D[Main Process]
        C -->|Fail| E[Reprocess]
        E --> C
    end

    subgraph Output["Output Stage"]
        D --> F[Measurement]
        F --> G[Data Recording]
        G --> H[(Database)]
    end

    style A fill:#E8F5E9,stroke:#2E7D32
    style D fill:#E3F2FD,stroke:#1565C0
    style H fill:#FFF3E0,stroke:#E65100
```

### Ontology Concept Relationships (Mermaid)

Entity relationship diagram style:

<!--@Mermaid_renderer_manual: Ontology Concept Relationships -->
```mermaid
graph TD
    subgraph Entities["Material Entities"]
        ME[Material Entity]
        SP[Specimen]
        EQ[Equipment]
    end

    subgraph Processes["Processes"]
        PR[Process]
        MS[Measurement]
        TR[Transformation]
    end

    subgraph Information["Information"]
        DT[Data Item]
        MD[Metadata]
        RS[Result Set]
    end

    ME --> SP
    ME --> EQ
    PR --> MS
    PR --> TR

    MS -.->|produces| DT
    TR -.->|transforms| ME
    DT --> RS
    MD --> RS

    style ME fill:#C8E6C9
    style PR fill:#BBDEFB
    style DT fill:#FFE0B2
```

---

## Complex Examples

### Full Ontology Pattern: Temporal Regions

This complex example shows temporal relationships in BFO:

<!--@Graphviz_renderer_manual: BFO Temporal Region Pattern -->
```dot
digraph TemporalRegion {
    rankdir=TB;
    compound=true;
    node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10];
    edge [fontname="Arial", fontsize=9];

    // TBox (Classes) - Purple
    subgraph cluster_tbox {
        label="TBox (Classes)";
        style=dashed;
        color="#9C27B0";
        bgcolor="#F3E5F5";

        Entity [label="bfo:entity", fillcolor="#CE93D8"];
        Occurrent [label="bfo:occurrent", fillcolor="#CE93D8"];
        Continuant [label="bfo:continuant", fillcolor="#CE93D8"];
        Process [label="bfo:process", fillcolor="#CE93D8"];
        TemporalRegion [label="bfo:temporal_region", fillcolor="#CE93D8"];
        OneDimTR [label="bfo:one_dimensional_t.r.", fillcolor="#CE93D8"];
        ZeroDimTR [label="bfo:zero_dimensional_t.r.", fillcolor="#CE93D8"];
    }

    // ABox (Individuals) - Grey
    subgraph cluster_abox {
        label="ABox (Individuals)";
        style=dashed;
        color="#607D8B";
        bgcolor="#ECEFF1";

        process1 [label="ex:process_1", fillcolor="#CFD8DC", shape=ellipse];
        process2 [label="ex:process_2", fillcolor="#CFD8DC", shape=ellipse];
        period1 [label="ex:period_1", fillcolor="#CFD8DC", shape=ellipse];
        period2 [label="ex:period_2", fillcolor="#CFD8DC", shape=ellipse];
        start [label="ex:start", fillcolor="#CFD8DC", shape=ellipse];
        end [label="ex:end", fillcolor="#CFD8DC", shape=ellipse];
        object1 [label="ex:object_1", fillcolor="#CFD8DC", shape=ellipse];
        sometime [label="ex:some_time", fillcolor="#CFD8DC", shape=ellipse];
    }

    // Class hierarchy
    Entity -> Occurrent [label="subClassOf"];
    Entity -> Continuant [label="subClassOf"];
    Occurrent -> Process [label="subClassOf"];
    Occurrent -> TemporalRegion [label="subClassOf"];
    TemporalRegion -> OneDimTR [label="subClassOf"];
    TemporalRegion -> ZeroDimTR [label="subClassOf"];

    // Type relationships (dashed)
    process1 -> Process [style=dashed, label="rdf:type"];
    process2 -> Process [style=dashed, label="rdf:type"];
    period1 -> OneDimTR [style=dashed, label="rdf:type"];
    period2 -> OneDimTR [style=dashed, label="rdf:type"];
    start -> ZeroDimTR [style=dashed, label="rdf:type"];
    end -> ZeroDimTR [style=dashed, label="rdf:type"];
    object1 -> Continuant [style=dashed, label="rdf:type"];
    sometime -> TemporalRegion [style=dashed, label="rdf:type"];

    // Object properties
    process1 -> period1 [label="occupies_temporal_region", color="#1565C0"];
    process2 -> period2 [label="occupies_temporal_region", color="#1565C0"];
    period2 -> start [label="has_first_instant", color="#1565C0"];
    period2 -> end [label="has_last_instant", color="#1565C0"];
    period1 -> period2 [label="proper_temporal_part_of", color="#1565C0"];
    object1 -> sometime [label="exists_at", color="#1565C0"];
}
```

### Process Chain Pattern

A complex process with parallel and sequential steps:

<!--@Graphviz_renderer_manual: Process Chain Pattern -->
```dot
digraph ProcessChain {
    rankdir=LR;
    node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10];
    edge [fontname="Arial", fontsize=9];

    // Processes
    parent [label="ex:process_parent\n(Parent Process)", fillcolor="#BBDEFB"];
    step1 [label="ex:process_step1\n(Initial Step)", fillcolor="#C8E6C9"];
    step2a [label="ex:process_step2a\n(Parallel A)", fillcolor="#FFF9C4"];
    step2b [label="ex:process_step2b\n(Parallel B)", fillcolor="#FFF9C4"];
    step3 [label="ex:process_step3\n(Final Step)", fillcolor="#FFCCBC"];

    // Structural relationships
    parent -> step1 [label="starts_with", color="#2E7D32", style=bold];
    parent -> step3 [label="ends_with", color="#C62828", style=bold];

    // Has part relationships
    parent -> step1 [label="has_part", style=dashed];
    parent -> step2a [label="has_part", style=dashed];
    parent -> step2b [label="has_part", style=dashed];
    parent -> step3 [label="has_part", style=dashed];

    // Temporal relationships
    step1 -> step2a [label="precedes", color="#1565C0"];
    step1 -> step2b [label="precedes", color="#1565C0"];
    step2a -> step3 [label="precedes", color="#1565C0"];
    step2b -> step3 [label="precedes", color="#1565C0"];

    // Simultaneity
    step2a -> step2b [label="simultaneous_with", color="#7B1FA2", style=bold, dir=both];
}
```

### Measurement Pattern (Mermaid)

A comprehensive measurement workflow:

<!--@Mermaid_renderer_manual: Measurement Workflow Pattern -->
```mermaid
flowchart TB
    subgraph Assay["obi:Assay Process"]
        direction TB
        A[my_assay]
    end

    subgraph Roles["Roles & Objectives"]
        R[evaluant_role]
        O[my_objective]
    end

    subgraph Entity["Material Entity"]
        E[my_evaluated_entity]
        Q1[my_entities_quality]
        Q2[preexisting_quality]
    end

    subgraph Output["Output Data"]
        D[measurement_datum]
        V[value_specification]
    end

    A -->|realizes| R
    A -->|has_specified_input| E
    A -->|has_specified_output| D
    A -->|achieves_planned_objective| O

    O -.->|is_about| E
    R -->|realized_in| A
    E -->|has_role| R
    E -->|has_quality| Q1
    E -->|has_quality| Q2

    Q1 -->|quality_is_specified_as| D
    D -->|is_about| E
    D -->|is_quality_measurement_of| Q1
    D -->|has_value_specification| V
    V -->|specifies_value_of| Q1
    V -->|is_about| E

    style A fill:#BBDEFB,stroke:#1565C0
    style E fill:#C8E6C9,stroke:#2E7D32
    style D fill:#FFF9C4,stroke:#F9A825
    style V fill:#FFCCBC,stroke:#E64A19
```

### Input/Output with Role Patterns

Complex pattern showing inputs, outputs, and role realization:

<!--@Graphviz_renderer_manual: Process Input Output with Roles -->
```dot
digraph InputOutputRoles {
    rankdir=TB;
    node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10];
    edge [fontname="Arial", fontsize=9];

    // Classes (rounded boxes)
    subgraph cluster_classes {
        label="Classes";
        style=invis;

        PlannedProcess [label="obi:planned_process", fillcolor="#FFCDD2"];
        ManufProcess [label="pmd:manufacturing_process", fillcolor="#E8F5E9"];
        CoatingProcess [label="pmd:coating_process", fillcolor="#E8F5E9"];
        BFOObject [label="bfo:object", fillcolor="#E3F2FD"];
    }

    // Individuals (ellipses)
    subgraph cluster_individuals {
        label="Individuals";
        style=invis;

        process1 [label="ex:process_1", fillcolor="#CFD8DC", shape=ellipse];
        process2 [label="ex:process_2", fillcolor="#CFD8DC", shape=ellipse];
        object1 [label="ex:object1\n(input)", fillcolor="#C8E6C9", shape=ellipse];
        object2 [label="ex:object2\n(intermediate)", fillcolor="#FFF9C4", shape=ellipse];
        object3 [label="ex:object3\n(output)", fillcolor="#FFCCBC", shape=ellipse];
    }

    // Class hierarchy
    ManufProcess -> PlannedProcess [label="subClassOf"];
    CoatingProcess -> ManufProcess [label="subClassOf"];

    // Type relationships
    process1 -> ManufProcess [style=dashed, label="rdf:type"];
    process2 -> CoatingProcess [style=dashed, label="rdf:type"];
    object1 -> BFOObject [style=dashed, label="rdf:type"];
    object2 -> BFOObject [style=dashed, label="rdf:type"];
    object3 -> BFOObject [style=dashed, label="rdf:type"];

    // Input/Output relationships
    process1 -> object1 [label="has_specified_input", color="#2E7D32", style=bold];
    process1 -> object2 [label="has_specified_output", color="#C62828", style=bold];
    process2 -> object2 [label="has_specified_input", color="#2E7D32", style=bold];
    process2 -> object3 [label="has_specified_output", color="#C62828", style=bold];
}
```

---

## Edge Cases and Special Examples

### Unicode and Special Characters

Testing special characters in labels:

<!--@Graphviz_renderer_manual: Unicode and Special Characters -->
```dot
digraph UnicodeTest {
    rankdir=LR;
    node [shape=box, style="rounded,filled", fontname="Arial", fontsize=11, fillcolor="#E3F2FD"];

    // Greek letters
    alpha [label="Temperature (T)\n\u03B1 coefficient"];
    beta [label="Pressure (P)\n\u03B2 factor"];

    // Subscripts/superscripts (using text)
    h2o [label="H2O\n(Water)"];
    co2 [label="CO2\n(Carbon Dioxide)"];

    // Units
    celsius [label="Temperature\n100 \u00B0C"];
    pascal [label="Pressure\n101.3 kPa"];

    // Arrows
    alpha -> h2o [label="affects"];
    beta -> co2 [label="influences"];
    h2o -> celsius [label="measured at"];
    co2 -> pascal [label="measured at"];
}
```

### Complex Mermaid State Diagram

State machine for material processing:

<!--@Mermaid_renderer_manual: Material Processing State Machine -->
```mermaid
stateDiagram-v2
    [*] --> RawMaterial: Receive

    RawMaterial --> Inspection: Quality Control

    state Inspection {
        [*] --> VisualCheck
        VisualCheck --> DimensionalCheck
        DimensionalCheck --> ChemicalAnalysis
        ChemicalAnalysis --> [*]
    }

    Inspection --> Approved: Pass
    Inspection --> Rejected: Fail

    Rejected --> Disposal: Scrap
    Rejected --> Rework: Salvageable
    Rework --> Inspection: Re-inspect

    Approved --> Processing

    state Processing {
        [*] --> HeatTreatment
        HeatTreatment --> Machining
        Machining --> SurfaceTreatment
        SurfaceTreatment --> [*]
    }

    Processing --> FinalInspection
    FinalInspection --> Shipped: Approved
    FinalInspection --> Rework: Defects

    Shipped --> [*]
    Disposal --> [*]
```

### Sequence Diagram for Measurement Process

<!--@Mermaid_renderer_manual: Measurement Process Sequence -->
```mermaid
sequenceDiagram
    participant O as Operator
    participant S as Specimen
    participant I as Instrument
    participant D as Database

    O->>S: Prepare specimen
    activate S
    O->>I: Configure instrument
    activate I

    O->>I: Start measurement
    I->>S: Apply stimulus
    S-->>I: Response signal

    loop Data Acquisition
        I->>I: Record data point
    end

    I->>D: Store raw data
    deactivate I
    deactivate S

    D->>D: Process data
    D-->>O: Results & analysis

    Note over O,D: Measurement complete
```

### Large Graph with Clusters

Demonstrating graph organization with subgraphs:

<!--@Graphviz_renderer_manual: Clustered Ontology Overview -->
```dot
digraph ClusteredOntology {
    rankdir=TB;
    compound=true;
    node [shape=box, style="rounded,filled", fontname="Arial", fontsize=9];
    edge [fontname="Arial", fontsize=8];

    // BFO Core
    subgraph cluster_bfo {
        label="BFO Core";
        style=filled;
        color="#E3F2FD";
        fillcolor="#E3F2FD";

        Entity [label="Entity", fillcolor="#BBDEFB"];
        Continuant [label="Continuant", fillcolor="#BBDEFB"];
        Occurrent [label="Occurrent", fillcolor="#BBDEFB"];

        Entity -> Continuant;
        Entity -> Occurrent;
    }

    // Material Entities
    subgraph cluster_material {
        label="Material Domain";
        style=filled;
        color="#E8F5E9";
        fillcolor="#E8F5E9";

        MaterialEntity [label="Material Entity", fillcolor="#C8E6C9"];
        Object [label="Object", fillcolor="#C8E6C9"];
        Material [label="Material", fillcolor="#C8E6C9"];
        Specimen [label="Specimen", fillcolor="#C8E6C9"];

        MaterialEntity -> Object;
        MaterialEntity -> Material;
        Object -> Specimen;
    }

    // Processes
    subgraph cluster_process {
        label="Process Domain";
        style=filled;
        color="#FFF3E0";
        fillcolor="#FFF3E0";

        Process [label="Process", fillcolor="#FFE0B2"];
        PlannedProcess [label="Planned Process", fillcolor="#FFE0B2"];
        Measurement [label="Measurement", fillcolor="#FFE0B2"];
        Manufacturing [label="Manufacturing", fillcolor="#FFE0B2"];

        Process -> PlannedProcess;
        PlannedProcess -> Measurement;
        PlannedProcess -> Manufacturing;
    }

    // Information
    subgraph cluster_info {
        label="Information Domain";
        style=filled;
        color="#F3E5F5";
        fillcolor="#F3E5F5";

        ICE [label="Information\nContent Entity", fillcolor="#E1BEE7"];
        DataItem [label="Data Item", fillcolor="#E1BEE7"];
        ValueSpec [label="Value\nSpecification", fillcolor="#E1BEE7"];

        ICE -> DataItem;
        ICE -> ValueSpec;
    }

    // Cross-cluster relationships
    Continuant -> MaterialEntity [lhead=cluster_material, ltail=cluster_bfo];
    Occurrent -> Process [lhead=cluster_process, ltail=cluster_bfo];

    Measurement -> Specimen [label="has_input", color="#1565C0"];
    Measurement -> DataItem [label="has_output", color="#C62828"];
    DataItem -> ValueSpec [label="has_value_spec"];
}
```

### Class Diagram Style (Mermaid)

UML-style class diagram:

<!--@Mermaid_renderer_manual: UML Class Diagram Style -->
```mermaid
classDiagram
    class Entity {
        <<BFO>>
    }

    class Continuant {
        <<BFO>>
    }

    class Occurrent {
        <<BFO>>
    }

    class MaterialEntity {
        <<PMD>>
        +uri: IRI
        +label: string
        +has_quality()
        +participates_in()
    }

    class Process {
        <<PMD>>
        +uri: IRI
        +label: string
        +has_input()
        +has_output()
        +precedes()
    }

    class Quality {
        <<BFO>>
        +uri: IRI
        +value: any
        +inheres_in()
    }

    class ValueSpecification {
        <<OBI>>
        +numeric_value: float
        +unit: Unit
        +specifies_value_of()
    }

    Entity <|-- Continuant
    Entity <|-- Occurrent
    Continuant <|-- MaterialEntity
    Continuant <|-- Quality
    Occurrent <|-- Process

    MaterialEntity "1" --> "*" Quality : has_quality
    Process "1" --> "*" MaterialEntity : has_input
    Process "1" --> "*" MaterialEntity : has_output
    Quality "1" --> "0..1" ValueSpecification : specified_by
```

---

## Styling Reference

### Graphviz Color Palette

Use these colors for consistent ontology visualization:

| Ontology | Fill Color | Hex Code |
|----------|------------|----------|
| BFO | Light Blue | `#E3F2FD` |
| PMD | Light Green | `#E8F5E9` |
| OBI | Light Red | `#FFEBEE` |
| IAO | Light Purple | `#F3E5F5` |
| Individual | Light Grey | `#CFD8DC` |

### Common Graphviz Node Styles

```dot
// Class node (box)
Node [shape=box, style="rounded,filled", fillcolor="#E3F2FD"];

// Individual node (ellipse)
Node [shape=ellipse, style=filled, fillcolor="#CFD8DC"];

// Literal/Value node (note shape)
Node [shape=note, style=filled, fillcolor="#FFF9C4"];
```

### Common Edge Styles

```dot
// Subclass relationship (solid)
A -> B [label="rdfs:subClassOf"];

// Type relationship (dashed)
A -> B [style=dashed, label="rdf:type"];

// Object property (colored)
A -> B [label="has_part", color="#1565C0"];

// Bidirectional
A -> B [dir=both, label="related_to"];
```

---

## Tips and Best Practices

1. **Use meaningful IDs**: Diagram IDs are generated from titles, so use descriptive titles
2. **Keep diagrams focused**: One concept per diagram is easier to understand
3. **Use consistent colors**: Stick to the ontology color palette above
4. **Add labels**: Always label edges with property names
5. **Use clusters**: Group related nodes in subgraphs for complex diagrams
6. **Test rendering**: Build the page locally to verify diagram rendering
7. **Escape special characters**: Use `\n` for newlines in labels

### Common Issues

- **Diagram not rendering**: Check that the code block language is `dot` or `mermaid`
- **Missing title**: Ensure the tag has a title after the colon
- **Broken layout**: Try adjusting `rankdir` (TB, BT, LR, RL)
- **Text overflow**: Use `\n` to break long labels into multiple lines
