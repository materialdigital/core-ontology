- **Purpose**: Express that a relational quality connecting a part entity and a whole entity — both having a mass quality — is a mass proportion (`pmd:PMD_0020102`).

- **Description**: A mass proportion (PMD_0020102) is a relational quality (BFO_0000145 via proportion PMD_0020101) that specifically depends on two independent continuants: a part and a whole, both of which bear a mass quality. The pattern encodes this as a **necessary condition** (SubClassOf) on mass proportion. Classification of instances as mass proportion is **asserted explicitly**, not inferred from scratch.

  The formal necessary-condition axiom (Manchester syntax):
  ```
  'mass proportion' SubClassOf:
      'proportion'
      and ('relational quality of' some
          (entity
           and ('has quality' some mass)
           and ('part of' some
               (entity
                and ('has quality' some mass)))))
  ```

  The RQ attaches to the **part entity** (an independent continuant), not to the mass quality. The second bearer (the whole) is covered by the PMDCO property chain `relational_quality_of ∘ part_of → relational_quality_of`.

- **Design decisions and rationale**:

  Three axiom designs were considered and rejected before reaching the current form:

  **1. Quality-centric approach (rejected: BFO domain/range violation)**

  Initial idea: anchor the axiom on the mass quality rather than the entity:
  ```
  'relational quality of' some
      (mass and ('quality of' some (entity and ('part of' some ...))))
  ```
  Problem: `relational quality of` (PMD_0025999) has range `independent continuant` in BFO/RO. Connecting it to a quality instance violates the domain/range constraint and produces inconsistency when loading full PMDCO with BFO and RO axioms.

  **2. Entity-centric EquivalentTo with single bearer (rejected: logically weak)**

  Anchor on the part entity, use EquivalentTo (sufficient condition):
  ```
  'mass proportion' EquivalentTo:
      'proportion'
      and ('relational quality of' some
          (entity and 'has quality' some mass
           and 'part of' some (entity and 'has quality' some mass)))
  ```
  Advantage: correct BFO usage, Konclude classifies `massFractionRQ` as PMD_0020102 (verified).
  Problem: **false positives**. Under OWL open-world assumption, a mole fraction RQ between the same part-whole pair satisfies all conditions — any material entity has mass. The axiom checks that bearers *have* mass, not that the RQ *quantifies* the ratio of those masses.

  **3. Two-bearer + mass quality (rejected: same false positive)**

  Intuition: BFO requires a relational quality to specifically depend on exactly two entities. If both bearers have mass quality, is that enough to uniquely identify a mass proportion?

  Counterexample:
  ```
  ex:moleFractionRQ  a proportion ;
      relational_quality_of  ex:ironPortion .    # ironPortion has mass ✓
  # chain infers: relational_quality_of ex:steelMaterial  # steelMaterial has mass ✓
  ex:ironPortion part_of ex:steelMaterial .
  ```
  → `moleFractionRQ` falsely classified as mass proportion, even with two bearers both having mass. The entities having mass does not bind the RQ to *measuring* those masses. A mole fraction and a mass fraction can coexist between the same part-whole pair.

  **4. Current approach: SubClassOf (necessary condition only)**

  Use the entity-centric axiom as a necessary condition only. This lets the reasoner:
  - Verify consistency: if something is asserted as mass proportion, it must satisfy the pattern
  - Entail expected role assertions (second bearer via chain, etc.)

  Classification stays **asserted**: when data is created, the modeller explicitly types the RQ as `pmd:PMD_0020102`. The axiom guards against incorrect assertions but does not classify from scratch.

  **What would make EquivalentTo safe**: A tight sufficient condition requires linking the RQ to the *value* it quantifies — a fraction value specification with a mass/mass unit. This is achievable via the fraction value specification pattern already in PMDCO but is not yet modelled here.

- **What needs to change in pmdco-base.ttl**:

  1. **Add the SubClassOf axiom** on `pmd:PMD_0020102` (the Turtle in `shape-data.ttl` can be merged in).

  2. **Declare `RO_0000086` as inverse of `RO_0000080`** — pmdco-base.ttl currently only declares `obo:RO_0000086 rdf:type owl:ObjectProperty` without the inverse, so the reasoner cannot infer `has quality` from `quality of` assertions:
     ```turtle
     obo:RO_0000086 owl:inverseOf obo:RO_0000080 .
     ```

- **Verification results**:

  Tested with the entity-centric EquivalentTo design (design 2 above) to confirm the reasoner fires correctly when conditions are met:

  | Reasoner | Mode | `massFractionRQ rdf:type PMD_0020102` |
  |---|---|---|
  | Konclude WASM (rdf-reasoner-konclude CLI) | materialize | ✅ inferred |
  | Konclude native (Docker `konclude/konclude`) | realization | ✅ inferred |
  | HermiT via ROBOT `reason` | TBox only | ➖ not applicable (TBox-only mode) |
  | ELK via ROBOT `reason` | TBox only | ➖ not applicable (EL profile) |

  The current SubClassOf design can be verified for consistency (no false positives on the example) but does not infer PMD_0020102 from scratch — that is by design.

  To reproduce EquivalentTo verification with Konclude WASM:
  ```bash
  # merge pmdco-base.ttl + shape-data.ttl into NTriples, then:
  node dist/cli.js -i merged.nt -m materialize -f nt | grep "massFractionRQ"
  # → <…massFractionRQ> rdf:type <…PMD_0020102>
  ```

alternative Visualization using [Ontosphere](https://thhanke.github.io/ontosphere/?rdfUrl=https://raw.githubusercontent.com/materialdigital/core-ontology/feat/mass-fraction-relational-quality-pattern/patterns/mass%20fraction%20relational%20quality/shape-data.ttl&ontologies=pmdco)
