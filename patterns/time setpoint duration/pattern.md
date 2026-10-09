**Purpose**: Represent the specified duration of a specific type of process and mention that the provenance of the value is a plan specification.

The present pattern is different from the other ones because it does not talk about the entity of interest directly. We talk about a value that "could be about" one (or several) entities.   
The first step for this is to create a plan specification and as part of it a specification datum `ex:specification_datum_1`. As a second step we create a subclass of `obi:value specification`. This subclass encapsulates some specific type requirements of specified value. In its `owl:equivalentClass` it specifies that it `iao:is about` the entity type that we are interested in. In our case the entity type that we are interested in is a `bfo:temporal interval` `bfo:during_which_exists` a process of specific type. We then instantiate this class and assign it unit and value in the usual manner. Additionally we can link it using `iao:is about` to instances, if we have known instances in our graph.
The RDF representation may be hard to read. In Manchester syntax:
```
Class: ex:class_process_duration_specification

    EquivalentTo:
        iao:is_about some (bfo:temporal_interval and (bfo:during_which_exists some bfo:process))

    SubClassOf:
        obi:value_specification
```
