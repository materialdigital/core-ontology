**Purpose**: Represent the timepoint of start of a specific type of process and mention that the provenance of the value is a plan specification.

The present pattern is different from the other ones because it does not talk about the entity of interest directly. We talk about a value that "could be about" one (or several) entities.   
The first step for this is to create a plan specification and as part of it a specification datum `ex:specification_datum_1`. As a second step we create a subclass of `pmd:timepoint`. This subclass encapsulates some specific type requirements of specified value. In its `owl:equivalentClass` it specifies that it `iao:is about` the entity type that we are interested in. In our case the entity type that we are interested in is a `bfo:temporal instant` which is `bfo:first instant of` a `bfo:temporal interval` that is occupied by a process of specific type. We then instantiate this (subclass of timepoint) class and assign it unit and value in the usual manner. Additionally we can link it using `iao:is about` to instances, if we have known instances in our graph. In the example we have a known instance identified by `ex:process_one` with its associated `ex:process_ones_temporal_startpoint`

Note: the specification class is defined in the "A-box" here.

The RDF representation may be hard to read. In Manchester syntax:
```
Class: ex:class_process_duration_specification

    EquivalentTo:
        is_about: some 
            (temporal_instant:
             and (first_instant_of: some 
                (temporal_interval:
                and ( inverse (occupies_temporal_region:) some process:))))

    SubClassOf:
        pmd:timepoint
```
