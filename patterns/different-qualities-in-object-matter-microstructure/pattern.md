# Pattern: Different qualities in object, matter and microstructure

**Issue:** [PMDco #394](https://github.com/materialdigital/core-ontology/issues/394)
**Related PR:** [#426](https://github.com/materialdigital/core-ontology/pull/426)
**Status:** Proposed pattern for discussion; PH/KZ consensus and full repository OWL/SHACL validation remain outstanding.

## Purpose

Demonstrate that an object made of ceramic can bear **global** material qualities while its **bulk and surface** bear **different local qualities and microstructural fractions**. The example uses one physical pellet and already established BFO and PMDco classes and relations. It **does not** introduce a spatially qualified continuant (SQC) class.

## Diagram and source of truth

A simplified ABox schematic is attached to the [Issue #394 discussion](https://github.com/materialdigital/core-ontology/issues/394). It illustrates the pellet, global composition, distinct bulk and surface bearers, and their fraction specifications. It is intentionally a **selective presentation**, not the complete RDF graph.

**`shape-data.ttl` is the authoritative full example.** The percentage values `5.0` and `80.0` are `xsd:double` RDF literals on specification individuals, not separate ABox individuals. Their percentages are also included in `rdfs:label` for presentation; the typed literals remain authoritative.

## Core modelling choice: correct bearers

* The **pellet** is a *single individual*, simultaneously typed as `BFO_0000030` (`object`) and `PMD_0000546` (`ceramic`), carrying its **global** mass and chemical composition. The graph does not create a second co-located pellet/portion individual, and does not add a new SQC class.
* Its `O_bulk` and `O_surface` are distinct **fiat object parts** typed with the PMDco `bulk` (`PMD_0000538`) and `surface layer` (`PMD_0000965`) classes, respectively. Each is a local bearer of its own volume and hardness property. There is **no direct assertion** that the whole's chemical composition or hardness belongs to either part.
* Each region contains a population of B-type crystallites modelled as a `BFO_0000027` **object aggregate**. This is the **numerator bearer**, not an individual crystallite. Each population is linked to **one asserted representative** `PMD_0000663` crystallite with `RO_0002351` (`has member`), retaining an explicit microstructure scale. An aggregate is used because 5 or 80 volume percent refers to the total B-grain population, not the volume of one grain. The example does not formally define the B-phase crystallography; 'B' is the specimen-level interpretation.

## Volume-fraction pattern: explicit RDF semantics

For each region, `ex:volume_proportion_of_B_crystal_in_*` is a `PMD_0020104` **volume fraction**, a relational property linking (using `PMD_0025999`, *relational property of*) the B-grain population to that region. Current PMDco also axiomatises a volume fraction using exactly one `PMD_0020256` **has numerator** and one `PMD_0020257` **has denominator**, whose bearers have volume qualities. This example asserts both relations and their four `PMD_0020150` (`volume`) qualities explicitly.

The *information entity* `ex:B_Crys_Vol_fraction_in_*` is a `PMD_0025997` **concentration value specification** (older pattern name: *fraction value specification*). It relates to its volume-fraction property through `OBI_0001927` **specifies value of**. It stores:

| Region | `OBI_0001937` has specified numeric value | `IAO_0000039` unit | Fractions interpreted as |
| --- | --- | --- | --- |
| Bulk | `"5.0"^^xsd:double` | `UO_0000165` | total volume of B-type grains / bulk volume × 100 |
| Surface | `"80.0"^^xsd:double` | `UO_0000165` | total volume of B-type grains / surface volume × 100 |

The values and units are **not** ontological qualities, part relations, or additional data individuals. They are literal/IRI objects of triples about each value-specification individual.

## Minimal competency questions

1. Which region is the **denominator** and which B population is the **numerator** of each volume fraction?
2. What numerical percentage and unit specify the surface and bulk fractions?
3. Does the pellet bear global composition while the two local regions bear distinct hardness and volume-fraction properties?
4. Is there any *asserted* rule or triple that transfers surface or bulk hardness to the pellet? (**No**, in this ABox. Check the imported ontology and inferred closure separately before claiming no entailment.)

## Interpretative limits and PH/KZ discussion

The PH–KR discussion concerned the attachment of specifically dependent continuants (SDCs) to a whole versus parts, possible unwanted propagation, and an exploratory SQC approach. KZ suggested that assigning SDCs to **appropriate bearers** using existing PMDco/BFO relations could suffice. This version implements that minimal strategy. **Neither this file nor a generic OWL consistency check establishes that PH and KZ approved this particular revision.** Confirm it with both reviewers before describing the modelling question as closed.

* Mere `has part` does **not**, by itself, imply unrestricted inheritance of every quality. **However**, inferred propagation can depend on additional imported PMDco property-chain axioms; always inspect a reasoned closure with the exact PMDco version used for the repository build.
* The example asserts separate hardness properties with labels 'harder' and 'softer'. It does **not** formalize an order comparison or prove a causal dependence of hardness on B-phase percentage.
* The pellet is explicitly classified as `BFO_0000030` (*object*) and `PMD_0000546` (*ceramic*). In the current PMDco hierarchy, ceramic is a subclass of material (`PMD_0000000`), which is a subclass of portion of matter (`PMD_0000001`); the latter is therefore inferred rather than asserted separately. Whether the dual classification resolves the broader identity concern requires reviewer confirmation.
* Synthetic process placeholders (typed `BFO_0000015`) and generic crystallite qualities (typed `BFO_0000019`) preserve the earlier PR's technical SHACL fillers; they are not claims about measured processes.
* This is an **ABox illustration**, not a universal OWL rule that all ceramic regions have the indicated proportions.

## Composition retrieval discussed with KZ

Two application-level approaches were discussed: (1) query composition asserted for the bulk/surface first, and if unavailable retrieve the *whole pellet's* composition by following the part-whole relation; or (2) use SPARQL `CONSTRUCT` to materialize clearly qualified derived information. **Neither implies that every part inherits the pellet's composition quality through OWL.** A fallback result must be identified as a whole-material value rather than a measured local composition.

## Validation and status

This Turtle parses to **94 asserted triples**, with an explicit `xsd:double` percentage value and `UO_0000165` unit for each specification. These basic structural checks do not establish full OWL consistency or SHACL compliance. **Full repository-level OWL reasoning and the complete SHACL/autoshape tests remain outstanding**. The previous 63-triple Ontosphere results do not validate this newer population and numerator/denominator pattern.

The only files intended for this review commit are `shape-data.ttl` and `pattern.md`. The explanatory ABox schematic is attached to the GitHub issue discussion, not referenced as a missing local file.
