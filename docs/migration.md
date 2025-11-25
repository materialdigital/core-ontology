# Migraton from Version 2.x


Because PMDco 3.x is based on BFO, the migration is not a simple translation but a re-modeling of the class hierarchy. The safest approach is to relocate each major conceptual block of the old ontology into the appropriate BFO branch and then check whether PMDco 3.x already provides an equivalent class or modeling pattern.

**Before you start:**

* Familiarize yourself with the BFO class hierarchy (PMDco 3.x is built on top of it). (PMDco is using the [atemporal variant of BFO 2020](https://github.com/BFO-ontology/BFO-2020/tree/master/21838-2/owl/profiles/atemporal). This variant does not include the BFO2020 temporalized relations.)
* Consult the BFO classifier ([link](https://keet.wordpress.com/2023/06/29/improved-the-bfo-classifier/)).
* Review the PROV–BFO mapping ([link](https://www.nature.com/articles/s41597-025-04580-1)).
* Understand the most relevant imported ontologies: [RO (Relation Ontology)](https://obofoundry.org/ontology/ro.html), [IAO (Information Artifact Ontology)](https://github.com/information-artifact-ontology/IAO/).

## Migration Guidelines

### 1. prov:Activity based classes → bfo:process

In PMDco 2.0.8, many classes modeled under `prov:Activity` represent processes, workflows, computational steps, material operations, or data transformations.
In BFO, all such happenings belong under `bfo:process.`

Move these classes into the `bfo:process` / `bfo:occurrent` branch. Anything that “unfolds”, “occurs”, or “executes” in time should be treated as a process.

### 2. prov:Agents (humans, organizations) → bfo:independent continuants

Agents are no longer modeled as activity performers (as in PROV-O).
In PMDco 3.x they become `bfo:independent continuants`:

Human agents → subclass of `Homo sapiens` (NCBITaxon_9606), under `bfo:material entity` .

Organizations → subclass of `obi:organization`, under `bfo:material entity`.

Exception:
Software agents are not `bfo:independent continuants`; they are information artifacts and should be modeled as subclasses of `iao:information content entity` (below `bfo:generically dependent continuant`). 

### 3. Objects, Samples, Devices → bfo:independent continuants (bfo:material entities)

Any entity with physical existence — devices, instruments, materials, equipment, objects — belongs to the `bfo:material entity` branch.

Place each of those under the most specific material entity class available in PMDco 3.x. Review object-related properties, since physical entities typically carry qualities, roles, realizable entities which may need adjustment during migration (see ValueObjects below).


### 4. ValueScope, DigitalEntity, and data-like conceptual classes → iao:information content entities (ICE)
 
PMDco 3.0 consolidates informational and conceptual constructs under the `iao:information content entities` (ICE) hierarchy.

Classes such as ValueScope, DigitalEntity, and general metadata belong here. Anything that describes or represents information **about** something (instead of being the thing itself) is an `iao:information content entity`.

### 5. ValueObjects → split across bfo:qualities, bfo:realizable entities, and ICE

This is one of the most significant conceptual changes.

Many ValueObject classes in 2.0.8 combine:

- qualities (mass, color, resolution, etc.),

- realizable entities (roles, functions, capabilities, etc.),

- information content (identifiers, names, codes, descriptions, specifications, etc.).

In BFO, these must be separated.

**Guidelines:**

* If the ValueObject describes an inherent property of an entity
	→ classify under `bfo:quality` or `pmd:behavioral material property` (e.g., size, precision, temperature range).

* If it describes a capability, role, or function
→ classify under `bfo:disposition`, `bfo:function`, `bfo:role`.

* If it represents data, codes, or symbolic values
→ classify under `iao:information content entity`.

A single old class may need to be split into two or three new ones.
PMDco 3.x with BFO enforces distinctions that PROV-O did not.


### 6. Relation Migration (common replacements)

* subordinate process → `bfo:has part`
* previous process → `bfo:preceded by`
* has characteristic → select one of `ro:characteristic of` subproperty (`ro:has role`, `ro:has quality`, `ro:has function`, `ro:has disposition`)
* composed of → `bfo:has part`
* component → `bfo: has part`
* executes → `ro:participates` in (do not confuse with `stato:executes`)
* has role → `bfo:has role`
* relates to → often replaced by `iao:is about` (if the subject is an ICE)

--
These recommendations are not exhaustive, and some cases will not have a clean one-to-one transformation. When in doubt, do not hesitate to contact the PMDco development team — discussing specific modeling questions is often the fastest and safest route to a consistent migration.