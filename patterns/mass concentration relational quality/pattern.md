- **Purpose**: Express that a relational quality connecting a part entity and a whole entity — where the part bears a mass quality and the whole bears a volume quality — is a mass concentration (`pmd:PMD_0080101`).

- **PMDCO term**: `PMD_0080101` "mass concentration" / "Massenkonzentration"
  - Available in branch `119-pattern-for-time-and-duration-representations`
  - `subClassOf PMD_0080069` (physical relational quality → BFO_0000145 relational quality)
  - The term note explicitly states: *"Necessary and sufficient conditions for 'mass concentration' have not yet been formalized."* — this pattern formalizes them.

- **Description**: A mass concentration RQ (PMD_0080101) is a physical relational quality that specifically depends on two independent continuants: a part whose mass is measured, and a whole whose volume is measured. The axiom encodes this as both a **necessary condition** (SubClassOf, Variant A) and a **sufficient condition** (EquivalentTo, Variant B).

  The formal necessary-condition axiom (Manchester syntax):
  ```
  'mass concentration' SubClassOf:
      'physical relational quality'
      and ('relational quality of' some
          (entity
           and ('has quality' some mass)
           and ('part of' some
               (entity
                and ('has quality' some volume)))))
  ```

  The RQ attaches to the **part entity** (an independent continuant). The second bearer (the whole) is covered by the PMDCO property chain `relational_quality_of ∘ part_of → relational_quality_of`.

- **Key difference from mass proportion (PMD_0020102)**:

  | | mass proportion | mass concentration |
  |---|---|---|
  | Part quality | mass | mass |
  | Whole quality | **mass** | **volume** |
  | Unit (example) | % (mass/mass) | g/L (mass/volume) |
  | OWL sufficient condition safe? | No — mass universal | **Yes — volume not universal** |

  Because not all material entities bear a volume quality (volume is asserted explicitly), the EquivalentTo design does **not** produce false positives here. A mass proportion RQ over the same part-whole pair would have a whole that bears a mass quality, not a volume quality — the axiom does not fire.

- **Preferred variant**: **Variant B (EquivalentTo)** is the recommended design for mass concentration. Unlike mass proportion, volume quality is not universally borne by all material entities, so the sufficient condition is discriminating. Classification of instances is therefore **automatic from the data** once the entity–quality–parthood structure is asserted.

- **Verification**:

  Tested with Konclude WASM + pmdco-full from branch `119-pattern-for-time-and-duration-representations`:

  | Individual | Expected | Result |
  |---|---|---|
  | `naclMassConcRQ` (asserted PMD_0080101) | `rdf:type MassConcentrationRQ_Equiv` | ✅ inferred |
  | `naclMassConcRQ relational_quality_of salineSolution` | inferred via chain | ✅ inferred |
  | `sugarMassFractionRQ` (whole has mass quality) | NOT `MassConcentrationRQ_Equiv` | ✅ not classified |

  To reproduce:
  ```bash
  # Download branch pmdco-full
  curl -s https://raw.githubusercontent.com/materialdigital/core-ontology/119-pattern-for-time-and-duration-representations/pmdco-full.ttl -o /tmp/pmdco-full-branch.ttl
  # Merge with shape-data.ttl
  python3 -c "
  import rdflib
  g = rdflib.ConjunctiveGraph()
  g.parse('/tmp/pmdco-full-branch.ttl', format='turtle')
  g.parse('shape-data.ttl', format='turtle')
  g.serialize('/tmp/mass-conc-merged.nt', format='nt')
  "
  node /path/to/rdf-reasoner-konclude/dist/cli.js -i /tmp/mass-conc-merged.nt -m materialize -f nt \
    | grep "massconcentration#"
  ```

- **What needs to change in pmdco**:

  1. **Merge `PMD_0080101`** from branch `119-pattern-for-time-and-duration-representations` into the release branch.
  2. **Add the SubClassOf axiom** on `PMD_0080101` (Variant A — conservative approach matching PMD_0020102 pattern style).
  3. **Optionally promote to EquivalentTo** (Variant B — safe because volume quality is not universal). This enables automatic classification.
  4. **Declare `RO_0000086` as inverse of `RO_0000080`** if not already present in the target pmdco-full.

- **Ontosphere visualization**:
  Load `shape-data.ttl` together with pmdco-full from branch `119-pattern-for-time-and-duration-representations`.
