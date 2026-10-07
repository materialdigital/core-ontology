# Mass Concentration Relational Quality — Design Pattern

## Purpose

Express that a relational quality connecting a part entity (bearing a mass quality) and a whole entity (bearing a volume quality) is a mass concentration (`pmd:PMD_0080101` "Massenkonzentration"). The pattern parallels the mass fraction pattern and shares the same design variants and the same `quantifies` property proposal.

---

## Background

`PMD_0080101` (mass concentration / "Massenkonzentration") is a physical relational quality that expresses the mass of a dissolved or dispersed component per unit volume of the mixture (e.g. 9 g/L for saline). It is available in branch `119-pattern-for-time-and-duration-representations`.

The PMDCO term note explicitly states: *"Necessary and sufficient conditions for 'mass concentration' have not yet been formalized."* This pattern formalizes them.

Key terms:

| IRI | Label | Role |
|---|---|---|
| `PMD_0080069` | physical relational quality | superclass of mass concentration |
| `PMD_0080101` | mass concentration | the class to be defined |
| `PMD_0020133` | mass | quality borne by the part entity |
| `PMD_0020150` | volume | quality borne by the whole entity |
| `PMD_0025999` | relational quality of | connects RQ → part entity |
| `BFO_0000050` | part of | parthood |
| `RO_0000086` | has quality | entity → quality |

**Key difference from mass proportion (PMD_0020102):**

| | mass proportion | mass concentration |
|---|---|---|
| Part quality | mass | mass |
| Whole quality | **mass** | **volume** |
| Unit example | % (mass/mass) | g/L (mass/volume) |

---

## Variant A — SubClassOf (necessary condition) ✅ ADOPTED

### TBox

```manchester
'mass concentration' SubClassOf:
    'physical relational quality'
    and ('relational quality of' some
        (entity and ('has quality' some mass)
         and ('part of' some (entity and ('has quality' some volume)))))
```

### ABox example

```turtle
ex:naclMassConcRQ  a pmd:PMD_0080101 .
ex:naclMassConcRQ  pmd:PMD_0025999  ex:naclPortion .
ex:naclPortion     obo:BFO_0000050  ex:salineSolution .
ex:naclPortion     obo:RO_0000086   ex:massOfNaCl .       # mass quality
ex:salineSolution  obo:RO_0000086   ex:volumeOfSolution . # volume quality ← key difference
```

---

## Variant B — EquivalentTo entity-centric ❌ REJECTED (same false positive risk as mass fraction)

Logically: all material entities have both mass AND volume as physical properties. The EquivalentTo condition (bearer has mass, whole has volume) is not a safe discriminator — any RQ between material entities where someone happens to assert both quality types would falsely classify. The argument is identical to mass fraction Variant B: it is not a user modelling assumption but a physical necessity.

---

## Variant C — EquivalentTo with value specification ✅ SAFE, pending unit class

### TBox

```manchester
'mass concentration' EquivalentTo:
    'physical relational quality'
    and ('relational quality of' some
        (entity and ('has quality' some mass)
         and ('part of' some (entity and ('has quality' some volume)))))
    and ('specified by value' some
        ('fraction value specification'
         and ('has measurement unit label' some 'mass concentration unit')))
```

Requires a class `mass concentration unit` covering g/L, kg/m³, mg/mL, … Pending PMDCO/QUDT addition.

---

## Variant D — EquivalentTo with `quantifies` 🏆 PROPOSED (logically ideal)

### Proposed property

```turtle
ex:quantifies  a owl:ObjectProperty ;
    rdfs:label  "quantifies" ;
    rdfs:domain obo:BFO_0000145 ;   # relational quality
    rdfs:range  obo:BFO_0000019 .   # quality
```

See mass fraction pattern.md for full justification and gap analysis in RO/IAO/PMDCO.

### TBox

```manchester
'mass concentration' EquivalentTo:
    'physical relational quality'
    and (quantifies some mass)
    and (quantifies some volume)
```

The RQ must quantify a mass quality AND a volume quality. A mass proportion RQ only quantifies mass — it does not fire. A molar RQ only quantifies mole amount — it does not fire.

### ABox example

```turtle
ex:naclMassConcRQ   ex:quantifies  ex:massOfNaCl .        # mass quality
ex:naclMassConcRQ   ex:quantifies  ex:volumeOfSolution .  # volume quality → fires ✓
ex:sugarMassFracRQ  ex:quantifies  ex:massOfSugar .       # mass only → does NOT fire ✓
```

### Contrast with mass proportion

```manchester
# mass proportion:
'mass proportion' EquivalentTo: 'proportion' and (quantifies some mass)

# mass concentration:
'mass concentration' EquivalentTo:
    'physical relational quality'
    and (quantifies some mass)
    and (quantifies some volume)
```

Mass proportion quantifies one mass quality. Mass concentration quantifies one mass AND one volume quality. The `quantifies` property gives each RQ type a clean, non-overlapping identity.

---

## Verification (Konclude WASM + pmdco-full branch 119)

Tested with branch `119-pattern-for-time-and-duration-representations` which defines `PMD_0080101`.

| Individual | Variant A (SubClassOf) | Variant D (Quantifies) |
|---|---|---|
| `naclMassConcRQ` (PMD_0080101, mass+volume) | consistency ✅ | ✅ classified |
| `sugarMassFractionRQ` (PMD_0020102, mass+mass) | — | ✅ not classified |

Property chain fires: `naclMassConcRQ relational_quality_of salineSolution` inferred.

**Ontosphere**: `shape-data.ttl` declares `owl:imports` for the branch pmdco-full. Load directly:

[Open in Ontosphere](https://thhanke.github.io/ontosphere/?rdfUrl=https://raw.githubusercontent.com/materialdigital/core-ontology/feat/mass-fraction-relational-quality-pattern/patterns/mass%20concentration%20relational%20quality/shape-data.ttl)

Ontosphere follows the import and fetches `PMD_0080101` from branch 119 automatically.

**CLI reproduction**:
```bash
curl -s https://raw.githubusercontent.com/materialdigital/core-ontology/119-pattern-for-time-and-duration-representations/pmdco-full.ttl \
  -o /tmp/pmdco-full-branch.ttl
python3 -c "
import rdflib
g = rdflib.ConjunctiveGraph()
g.parse('/tmp/pmdco-full-branch.ttl', format='turtle')
g.parse('shape-data.ttl', format='turtle')
g.serialize('/tmp/merged.nt', format='nt')
"
node /path/to/rdf-reasoner-konclude/dist/cli.js -i /tmp/merged.nt -m materialize -f nt \
  | grep "massconcentration#"
```

---

## What needs to change in PMDCO

1. **Merge `PMD_0080101`** from branch `119-pattern-for-time-and-duration-representations`.
2. **Add Variant A SubClassOf axiom** to `PMD_0080101`.
3. **Add `mass concentration unit` class** (g/L, kg/m³, mg/mL …) → enables Variant C.
4. **Adopt `quantifies` property** (domain: relational quality, range: quality) → enables Variant D. See mass fraction pattern for full proposal.
