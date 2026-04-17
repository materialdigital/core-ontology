- **Purpose**: Description on how to represent the chemical composition of a (typical metallic) material
- **Description**: The shape illustrates how to describe the chemical composition of a (metallic) object which at the same time is a portion of matter. This matter has a quality, the chemical composition. The chemical composition quality is quantified by a generically dependent "chemical composition specification", a complex information content entity that has several scalar value specifications as parts. Those scalar value specifications (expressing mass fraction, mol fraction, volume fraction) in turn quantify the relational property between a portion of (pure) substance and the material which is the sum of such portions.

## Design Rationale and Restrictions

### Why proportions are qualities of the material, not of the element portions

Mass proportions (e.g. `mass ratio`, PMD_0020102) are modeled in PMDco as subtypes of `composition` (PMD_0025001), which is an **intensive quality** — a quality of the material as a whole. This has a direct consequence for how proportions connect to the element portions they describe.

`quality_of` (RO_0000080) is a **FunctionalObjectProperty** (inherited from `characteristic_of`, RO_0000052): a quality can inhere in exactly **one** independent continuant. It is therefore impossible to assert `mass_proportion quality_of some_iron` AND `mass_proportion quality_of material` simultaneously — a reasoner would infer `some_iron owl:sameAs material`, causing an inconsistency.

Because the proportions are subtypes of composition (an intensive quality of the whole), the correct bearer is the **material**. The element portions are connected to the material via `part_of`, not directly to the proportion.

### Why `has_characteristic` / `has_quality` cannot be used from the element side

Using `some_iron has_quality mass_proportion` would infer (via `InverseObjectProperties(quality_of, has_quality)`) that `mass_proportion quality_of some_iron`. Combined with `mass_proportion quality_of material`, the reasoner again infers `some_iron owl:sameAs material`. The same problem holds for all RO quality-bearer properties — they all ultimately inherit the functional constraint of `characteristic_of` (RO_0000052).

This is a **fundamental BFO/RO design decision**: non-relational qualities (BFO_0000019) are single-bearer. The multi-bearer pattern was intentionally reserved for **relational qualities** (BFO_0000145). PMD_0020102 is currently modeled as a composition (intensive quality), not a relational quality, which makes this single-bearer restriction apply.

### Implications for data consumers

- **Proportions are permanently detached from element portions** at the property-assertion level. There is no direct RDF triple linking a proportion instance to the specific element portion it describes.
- **Navigation from element to proportion is indirect**: `some_iron → part_of → material → inverse(quality_of) → mass_proportion`. This pattern is encoded in the SHACL shape for `pure_substance_chemical_element` using a property path and `sh:qualifiedMinCount`.
- **The binding between a proportion and its element** is only expressed through the fraction value specification chain: `mass_proportion → specified_by_value → fraction_spec`, where the fraction spec is the shared information artifact that links the quantity to the element.
- **Querying "what is the iron fraction?"** requires navigating the specification chain, not a direct proportion→element triple.

### What this means if the model should be changed

If the intent is to formally express that a proportion simultaneously describes the material and its element portion, `mass ratio` (PMD_0020102) would need to be reclassified as a **relational quality** (`SubClassOf BFO_0000145`). This would allow use of `relational_quality_of` (PMD_0025999, domain=BFO_0000145) for both connections without violating the functional constraint, since relational qualities are explicitly designed for multi-bearer dependency. That change requires modifying the ontology, not the pattern.

alternative Visualization using [visgraph](https://thhanke.github.io/visgraph/?rdfUrl=https://raw.githubusercontent.com/materialdigital/core-ontology/main/patterns/chemical%20composition/shape-data.ttl)
