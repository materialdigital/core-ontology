# Mass Fraction Relational Quality — Design Pattern

## Purpose

Express that a relational quality connecting a part entity and a whole entity — both bearing a mass quality — is a mass proportion (`pmd:PMD_0020102`). Four axiom design variants are documented and tested. The pattern also proposes a new property `quantifies` as the logically sound long-term solution.

---

## Background

`PMD_0020102` (mass proportion / "Massenanteil") is a `BFO_0000145` relational quality that specifically depends on two independent continuants: a **part** whose mass is measured and a **whole** whose mass is the reference. The mass of the part divided by the mass of the whole gives a dimensionless ratio (%, kg/kg, g/g …).

Key PMDCO terms used:

| IRI | Label | Role |
|---|---|---|
| `PMD_0020101` | proportion | superclass of mass proportion |
| `PMD_0020102` | mass proportion | the class to be defined |
| `PMD_0020133` | mass | quality borne by both entities |
| `PMD_0020150` | volume | quality for contrast (mass concentration) |
| `PMD_0025999` | relational quality of | connects RQ → part entity |
| `PMD_0025998` | has relational quality | inverse; inferred by chain |
| `PMD_0000077` | specified by value | connects RQ → value spec |
| `PMD_0025997` | fraction value specification | value spec class |
| `BFO_0000050` | part of | parthood |
| `RO_0000086` | has quality | entity → quality |
| `RO_0000080` | quality of | quality → entity (inverse) |

**Property chain in PMDCO:**
`relational_quality_of ∘ part_of → relational_quality_of`
→ if `RQ relational_quality_of part` and `part part_of whole`, the reasoner infers `RQ relational_quality_of whole`.

**Note:** `RO_0000086` (has quality) must be declared `owl:inverseOf RO_0000080` in the working file — pmdco-base.ttl omits this. Included in `shape-data.ttl`.

---

## Variant A — SubClassOf (necessary condition) ✅ ADOPTED

### TBox

```turtle
pmd:PMD_0020102 rdfs:subClassOf [
    owl:intersectionOf (
        pmd:PMD_0020101
        [ owl:onProperty pmd:PMD_0025999 ;
          owl:someValuesFrom [
              owl:intersectionOf (
                  obo:BFO_0000004
                  [ owl:onProperty obo:RO_0000086 ; owl:someValuesFrom pmd:PMD_0020133 ]
                  [ owl:onProperty obo:BFO_0000050 ;
                    owl:someValuesFrom [
                        owl:intersectionOf (
                            obo:BFO_0000004
                            [ owl:onProperty obo:RO_0000086 ; owl:someValuesFrom pmd:PMD_0020133 ]
                        ) ] ] ) ] ]
    )
] .
```

Manchester syntax:
```
'mass proportion' SubClassOf:
    'proportion'
    and ('relational quality of' some
        (entity and ('has quality' some mass)
         and ('part of' some (entity and ('has quality' some mass)))))
```

### Semantics

Necessary condition only. If something is asserted as `PMD_0020102`, it **must** satisfy the pattern (consistency check). The reasoner **cannot** infer PMD_0020102 from scratch — classification is asserted by the modeller.

### ABox example

```turtle
ex:massFractionRQ  a pmd:PMD_0020102 .                  # asserted
ex:massFractionRQ  pmd:PMD_0025999  ex:sugarPortion .
ex:sugarPortion    obo:BFO_0000050  ex:sugarSolution .
ex:sugarPortion    obo:RO_0000086   ex:massOfSugar .     # mass quality
ex:sugarSolution   obo:RO_0000086   ex:massOfSolution .  # mass quality
```

### Inferred

```
massFractionRQ  pmd:PMD_0025999  sugarSolution   (property chain)
massFractionRQ  rdf:type         PMD_0020101     (superclass)
massFractionRQ  rdf:type         BFO_0000145     (superclass)
```

### Verdict

Safe. No false positives. Use until Variant D property is adopted in PMDCO.

---

## Variant B — EquivalentTo entity-centric ❌ REJECTED (false positives)

### TBox

```turtle
ex:MassFractionRQ_EntityEquiv owl:equivalentClass [
    owl:intersectionOf (
        pmd:PMD_0020101
        [ owl:onProperty pmd:PMD_0025999 ;
          owl:someValuesFrom [
              owl:intersectionOf (
                  obo:BFO_0000004
                  [ owl:onProperty obo:RO_0000086 ; owl:someValuesFrom pmd:PMD_0020133 ]
                  [ owl:onProperty obo:BFO_0000050 ;
                    owl:someValuesFrom [
                        owl:intersectionOf (
                            obo:BFO_0000004
                            [ owl:onProperty obo:RO_0000086 ; owl:someValuesFrom pmd:PMD_0020133 ]
                        ) ] ] ) ] ]
    )
] .
```

### Problem

Any proportion RQ between two material entities — including mole fraction, volume fraction — satisfies all conditions, because every material entity physically has mass. This is not a user data modelling assumption; it is a necessary physical truth. The EquivalentTo fires for the wrong individuals.

### ABox counterexample

```turtle
ex:moleFractionRQ  a pmd:PMD_0020101 .
ex:moleFractionRQ  pmd:PMD_0025999  ex:ironPortion .
ex:ironPortion     obo:BFO_0000050  ex:steelBlock .
ex:ironPortion     obo:RO_0000086   ex:massOfIron .   # mass — always present
ex:steelBlock      obo:RO_0000086   ex:massOfSteel .  # mass — always present
```

### Inferred (verified with Konclude)

```
moleFractionRQ  rdf:type  MassFractionRQ_EntityEquiv   ← FALSE POSITIVE
```

---

## Variant C — EquivalentTo with value specification ✅ SAFE, pending unit class

### TBox

```manchester
'mass proportion' EquivalentTo:
    'proportion'
    and ('relational quality of' some
        (entity and ('has quality' some mass)
         and ('part of' some (entity and ('has quality' some mass)))))
    and ('specified by value' some
        ('fraction value specification'
         and ('has measurement unit label' some 'mass fraction unit')))
```

### ABox example

```turtle
ex:massFractionRQ  pmd:PMD_0000077  ex:sugarMassFractionSpec .
ex:sugarMassFractionSpec  a  pmd:PMD_0025997 .
ex:sugarMassFractionSpec  obo:IAO_0000039  obo:UO_0000163 .  # mass percentage unit
```

### What is needed

A class `mass fraction unit` covering all mass/mass ratio units (%, kg/kg, g/g …). `UO_0000163` (mass percentage) is one instance. Local placeholder `ex:MassFractionUnit` used in `shape-data.ttl`. Once this class exists in PMDCO or QUDT, this variant can replace Variant A.

### Verdict

Safe — unit discrimination is a logically sound sufficient condition. Blocked only on the missing unit class.

---

## Variant D — EquivalentTo with `quantifies` 🏆 PROPOSED (logically ideal)

### Motivation

Variants B and C work around a deeper gap: there is no property in OWL/BFO/RO/PMDCO connecting a relational quality to the **specific quality instance it measures**. Variants B and C use the bearer entity as a proxy, which loses information. The correct model is:

> A mass proportion RQ **quantifies** a mass quality of the part, and the chain infers it also relates to a mass quality of the whole.

### Proposed property

```turtle
ex:quantifies  a owl:ObjectProperty ;
    rdfs:label  "quantifies" ;
    rdfs:domain obo:BFO_0000145 ;   # relational quality
    rdfs:range  obo:BFO_0000019 .   # quality
```

No equivalent property exists in RO, IAO, or PMDCO. Closest candidates checked and ruled out:

| Property | Why it does not fit |
|---|---|
| `IAO_0000221` is quality measurement of | domain: measurement datum (not RQ); connects data output → quality |
| `RO_0009006` assay measures characteristic | domain: assay (process, not RQ) |
| `RO_0000080` quality of | inverse direction; connects quality → bearer entity |

IAO explicitly noted this gap in the annotation on `IAO_0000221`: *"There are other kinds of measurements that are not of qualities … we will add these as separate properties for the moment"* — never followed through.

### TBox

```turtle
ex:MassFractionRQ_Quantifies owl:equivalentClass [
    owl:intersectionOf (
        pmd:PMD_0020101
        [ owl:onProperty ex:quantifies ; owl:someValuesFrom pmd:PMD_0020133 ]
    )
] .
```

Manchester syntax:
```
'mass proportion' EquivalentTo:
    'proportion'
    and (quantifies some mass)
```

### ABox example

```turtle
ex:massFractionRQ  ex:quantifies  ex:massOfSugar .      # mass quality → fires ✓
ex:moleFractionRQ  ex:quantifies  ex:moleOfIron .       # mole quality → no fire ✓
ex:volumeFractionRQ ex:quantifies ex:volumeOfFibre .    # volume quality → no fire ✓
```

### Why this is correct

The RQ connects directly to the quality instance it measures. A mole fraction RQ quantifies a mole amount quality — not a mass quality. No ambiguity, no cardinality restrictions needed, no unit class needed.

Note on cardinality: one entity has exactly one mass quality and one volume quality (physically true). This is why cardinality-1 restrictions on quality types are physically correct. However, cardinality alone does not solve discrimination at the ABox level — a mole fraction RQ's bearer entity also has exactly one mass quality. The discrimination requires the **direct quality-to-RQ connection** that `quantifies` provides.

### Parallel definitions enabled by `quantifies`

```manchester
'mass proportion' EquivalentTo:
    'proportion' and (quantifies some mass)

'mass concentration' EquivalentTo:
    'physical relational quality'
    and (quantifies some mass)
    and (quantifies some volume)

'molar proportion' EquivalentTo:
    'proportion' and (quantifies some 'amount of substance')

'volume proportion' EquivalentTo:
    'proportion' and (quantifies some volume)
```

Clean, uniform, no false positives, no auxiliary classes needed.

### Verdict

Logically ideal. Requires adopting `quantifies` as a new PMDCO (or RO) property.

---

## Verification (Konclude WASM + pmdco-full)

All four variants tested in one `materialize` step. Expected vs actual results:

| Individual | Variant A (SubClassOf) | Variant B (EntityEquiv) | Variant C (ValueEquiv) | Variant D (Quantifies) |
|---|---|---|---|---|
| `massFractionRQ` (PMD_0020102 + mass% spec + quantifies mass) | consistency ✅ | ✅ classified | ✅ classified | ✅ classified |
| `moleFractionRQ` (PMD_0020101 + quantifies mole) | — | ❌ **FALSE POSITIVE** | ✅ not classified | ✅ not classified |
| `volumeFractionRQ` (PMD_0020101 + quantifies volume) | — | ❌ **FALSE POSITIVE** | ✅ not classified | ✅ not classified |

Property chain fires for all three: second bearer inferred via `relational_quality_of ∘ part_of`.

To reproduce:
```bash
curl -s https://raw.githubusercontent.com/materialdigital/core-ontology/main/pmdco-full.ttl -o /tmp/pmdco-full.ttl
python3 -c "
import rdflib
g = rdflib.ConjunctiveGraph()
g.parse('/tmp/pmdco-full.ttl', format='turtle')
g.parse('shape-data.ttl', format='turtle')
g.serialize('/tmp/merged.nt', format='nt')
"
node /path/to/rdf-reasoner-konclude/dist/cli.js -i /tmp/merged.nt -m materialize -f nt \
  | grep "massfraction#.*type.*MassFraction"
```

---

## What needs to change in PMDCO

1. **Add Variant A axiom to `PMD_0020102`** — the SubClassOf from this file.
2. **Declare `RO_0000086 owl:inverseOf RO_0000080`** in pmdco-base.ttl.
3. **Add `mass fraction unit` class** (covering %, kg/kg, g/g) → enables Variant C EquivalentTo on PMD_0020102.
4. **Adopt `quantifies` property** (domain: relational quality, range: quality) → enables Variant D, the logically ideal definition. Submit as PMDCO or RO proposal.

---

## Ontosphere visualization

`shape-data.ttl` includes `owl:imports pmdco-full.ttl` — Ontosphere follows imports automatically. Load the pattern file directly:

[Open in Ontosphere](https://thhanke.github.io/ontosphere/?rdfUrl=https://raw.githubusercontent.com/materialdigital/core-ontology/feat/mass-fraction-relational-quality-pattern/patterns/mass%20fraction%20relational%20quality/shape-data.ttl)

Ontosphere will fetch pmdco-full from main, then load shape-data.ttl on top and run OWL reasoning. All four variant classes and ABox individuals will appear in the graph.
