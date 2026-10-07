# Composition Relational Quality — Design Pattern

## Overview

A **composition relational quality** (composition RQ) is a `BFO_0000145` relational quality that specifically depends on two independent continuants — a **part** and a **whole** — and expresses how much of the whole the part makes up, measured by a physical quantity such as mass, volume, or mole amount.

This pattern covers two PMDCO terms:

| PMDCO term | IRI | Part quality | Whole quality | Example unit |
|---|---|---|---|---|
| mass proportion | `PMD_0020102` | mass | mass | %, kg/kg |
| mass concentration | `PMD_0080101` | mass | **volume** | g/L, kg/m³ |

Both terms follow **identical axiom design logic**. The only difference is which quality type the whole entity bears. All design variants, verification results, and the `quantifies` property proposal apply to both.

Related subtypes (same pattern, not yet formalized in PMDCO):
- molar proportion (`PMD_0020103`) — part: mole amount, whole: mole amount
- volume proportion (`PMD_0020104`) — part: volume, whole: volume

---

## Shared design context

**Property chain in PMDCO:**
`relational_quality_of ∘ part_of → relational_quality_of`
→ if `RQ relational_quality_of part` and `part part_of whole`, the reasoner infers `RQ relational_quality_of whole`.

**Note:** `RO_0000086` (has quality) must be declared `owl:inverseOf RO_0000080` — pmdco-base.ttl omits this. Included in both shape-data files.

**Files:**
- [`shape-data-mass-proportion.ttl`](shape-data-mass-proportion.ttl) — mass proportion (`PMD_0020102`); imports `pmdco-full` from `main`
- [`shape-data-mass-concentration.ttl`](shape-data-mass-concentration.ttl) — mass concentration (`PMD_0080101`); imports `pmdco-full` from branch `119-pattern-for-time-and-duration-representations` which defines `PMD_0080101`

---

## Axiom design variants

Four variants are documented. All are represented as named TBox classes in the shape-data files so a single `materialize` run demonstrates all of them.

### Variant A — SubClassOf (necessary condition) ✅ ADOPTED for both terms

Classification is **asserted** by the modeller; the axiom guards consistency and fires the property chain to infer the second bearer.

**Mass proportion:**
```manchester
'mass proportion' SubClassOf:
    'proportion'
    and ('relational quality of' some
        (entity and ('has quality' some mass)
         and ('part of' some (entity and ('has quality' some mass)))))
```

**Mass concentration:**
```manchester
'mass concentration' SubClassOf:
    'physical relational quality'
    and ('relational quality of' some
        (entity and ('has quality' some mass)
         and ('part of' some (entity and ('has quality' some volume)))))
```

The whole bears **mass** for mass proportion and **volume** for mass concentration — that is the only structural difference.

---

### Variant B — EquivalentTo entity-centric ❌ REJECTED for both terms

**Why rejected:** Every material entity physically has both mass and volume. The condition "bearer has mass, whole has mass/volume" is not a safe sufficient condition — any RQ between material entities satisfies it once those quality types are asserted. This is a logical necessity, not a user modelling assumption. Verified with Konclude: mole fraction and volume fraction RQs between the same entity pairs are falsely classified.

---

### Variant C — EquivalentTo with value specification ✅ SAFE, pending unit classes

Add a discriminating unit constraint via the value specification:

**Mass proportion:**
```manchester
'mass proportion' EquivalentTo: ... and
    ('specified by value' some
        ('fraction value specification'
         and ('has measurement unit label' some 'mass fraction unit')))
```

**Mass concentration:**
```manchester
'mass concentration' EquivalentTo: ... and
    ('specified by value' some
        ('fraction value specification'
         and ('has measurement unit label' some 'mass concentration unit')))
```

Requires two new unit classes in PMDCO/QUDT:
- `mass fraction unit` — covering %, kg/kg, g/g …
- `mass concentration unit` — covering g/L, kg/m³, mg/mL …

Local placeholder classes (`ex:MassFractionUnit`, `ex:MassConcentrationUnit`) used in the shape-data files.

---

### Variant D — EquivalentTo with `quantifies` 🏆 PROPOSED (logically ideal)

#### The gap

No property in OWL/BFO/RO/IAO/PMDCO connects a relational quality to the **specific quality instance it measures**. Variants B and C use the bearer entity as a proxy, losing the direct connection. Closest candidates checked and ruled out:

| Property | Why it does not fit |
|---|---|
| `IAO_0000221` is quality measurement of | domain: measurement datum (not RQ) |
| `RO_0009006` assay measures characteristic | domain: assay (process, not RQ) |
| `RO_0000080` quality of | wrong direction; quality → bearer entity |

IAO explicitly noted this gap in `IAO_0000221`: *"There are other kinds of measurements that are not of qualities … we will add these as separate properties for the moment"* — never resolved.

#### Proposed property

```turtle
pmd:quantifies  a owl:ObjectProperty ;
    rdfs:label  "quantifies" ;
    rdfs:domain obo:BFO_0000145 ;   # relational quality
    rdfs:range  obo:BFO_0000019 .   # quality
```

#### TBox definitions enabled

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

Clean, uniform, no false positives, no unit classes needed.

#### ABox usage

```turtle
ex:massFractionRQ    ex:quantifies  ex:massOfSugar .      # mass → mass proportion fires ✓
ex:massConcRQ        ex:quantifies  ex:massOfNaCl .       # mass + volume → mass conc fires ✓
ex:massConcRQ        ex:quantifies  ex:volumeOfSolution .
ex:moleFractionRQ    ex:quantifies  ex:moleOfIron .       # mole → no mass proportion fire ✓
ex:volumeFractionRQ  ex:quantifies  ex:volumeOfFibre .    # volume → no mass proportion fire ✓
```

#### Note on cardinality

One entity has exactly one mass quality and one volume quality (physically correct). OWL `has_quality exactly 1 mass` expresses this precisely. However, cardinality-1 alone does not solve discrimination — a mole fraction RQ's bearer entity also has exactly one mass quality. The `quantifies` property provides the direct quality-to-RQ connection that cardinality cannot.

---

## Verification summary

### Mass proportion (pmdco-full from main)

| Individual | B (EntityEquiv) | C (ValueEquiv) | D (Quantifies) |
|---|---|---|---|
| `massFractionRQ` | ✅ | ✅ | ✅ |
| `moleFractionRQ` | ❌ **false positive** | ✅ safe | ✅ safe |
| `volumeFractionRQ` | ❌ **false positive** | ✅ safe | ✅ safe |

### Mass concentration (pmdco-full from branch 119)

| Individual | D (Quantifies) |
|---|---|
| `naclMassConcRQ` (mass + volume) | ✅ classified |
| `sugarMassFractionRQ` (mass only) | ✅ not classified |

Property chain fires for all scenarios — second bearer inferred.

---

## Ontosphere

Both files carry `owl:imports` — Ontosphere follows the import chain automatically. Load with a single `rdfUrl` parameter:

**Mass proportion:**
[Open in Ontosphere](https://thhanke.github.io/ontosphere/?rdfUrl=https://raw.githubusercontent.com/materialdigital/core-ontology/feat/mass-fraction-relational-quality-pattern/patterns/composition%20relational%20quality/shape-data-mass-proportion.ttl)

**Mass concentration** (loads branch 119 pmdco-full via import):
[Open in Ontosphere](https://thhanke.github.io/ontosphere/?rdfUrl=https://raw.githubusercontent.com/materialdigital/core-ontology/feat/mass-fraction-relational-quality-pattern/patterns/composition%20relational%20quality/shape-data-mass-concentration.ttl)

---

## What needs to change in PMDCO

| Change | Enables |
|---|---|
| Add Variant A SubClassOf to `PMD_0020102` and `PMD_0080101` | Consistency checking + chain |
| Declare `RO_0000086 owl:inverseOf RO_0000080` in pmdco-base.ttl | has_quality inference from quality_of |
| Merge `PMD_0080101` from branch 119 to main | Mass concentration term availability |
| Add `mass fraction unit` class (%, kg/kg, g/g) | Variant C for mass proportion |
| Add `mass concentration unit` class (g/L, kg/m³) | Variant C for mass concentration |
| Adopt `quantifies` property (domain: RQ, range: quality) | Variant D — logically ideal; unifies all subtypes |
