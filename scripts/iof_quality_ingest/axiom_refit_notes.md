# Axiom Refit Notes — IOF → PMDco Migration

Date: 2026-03-12
Status: **RESOLVED** — 0 unsatisfiable classes after fixes below.

These are manual axiom adjustments made to `pmdco-qualities.owl` after merging the
migration output. Each fix resolves a BFO branch conflict introduced by the migration
re-parenting existing PMDco terms into the new IOF-derived grouper hierarchy.

---

## Background

The migration emits `SubClassOf(existing_pmd new_grouper)` for EXISTS terms. Some
existing PMDco terms had parents in a BFO branch disjoint from the new grouper's branch.
BFO2020 disjointness relevant here:

- `BFO_0000015` (process/occurrent) ⊥ `BFO_0000019` (quality/continuant)
- `BFO_0000016` (realizable entity) ⊥ `BFO_0000019` (quality)
- `BFO_0000017` (realizable entity subtype) ⊥ `BFO_0000019` (quality)
- `BFO_0000019` (quality, intrinsic) ⊥ `BFO_0000145` (relational quality) — disjoint siblings in BFO2020

---

## Conflict A — Phase transition points (4 terms)

**Terms:** boiling point `PMD_0000535`, melting point `PMD_0000851`,
sublimation point `PMD_0000961`, triple point `PMD_0000996`

**Conflict:**
- Old parent: `PMD_0020164` (state of matter boundary → `PMD_0000882` → `BFO_0000017` realizable)
- Migration added: `SubClassOf → PMD_0080005` (thermodynamische Qualität → `BFO_0000019`)
- BFO_0000017 ⊥ BFO_0000019 → unsatisfiable

**Fix applied:** Replaced `SubClassOf(PMD_XXXX PMD_0020164)` with
`SubClassOf(PMD_XXXX PMD_0080005)` in the pre-existing section.

**Ontological rationale:** These are characteristic temperatures of a material — measurable
properties that inhere in the material. Classifying them as thermodynamic qualities
(BFO_0000019) is more appropriate than as realizable/disposition-like state-of-matter
boundaries. The old PMDco classification as "state of matter boundary" was a modelling
choice that the IOF alignment supersedes.

**TODO:** Review whether `PMD_0020164` (state of matter boundary) and `PMD_0000882`
(phase boundary realization) are still needed, or whether they have become orphaned
groupers with no children. If orphaned, consider deprecating them.

---

## Conflict B — Force (PMD_0020200)

**Term:** force `PMD_0020200`

**Conflict:**
- Old parent: `BFO_0000017` (realizable entity — force as a capacity/disposition)
- Migration added: `SubClassOf → PMD_0080069` (physical relational quality → `BFO_0000145`)
- BFO_0000017 ⊥ BFO_0000019/BFO_0000145 → unsatisfiable

**Fix applied:** Replaced `SubClassOf(PMD_0020200 BFO_0000017)` with
`SubClassOf(PMD_0020200 PMD_0080069)` in the pre-existing section.

**Ontological rationale:** Force as a relational quality (BFO_0000145) captures that it is
a quantity describing a reciprocal interaction between two objects — it cannot be
attributed to one object alone. The IOF/BFO2020 relational quality classification is
preferred. The old PMDco definition text already described force as a "reciprocal
interaction", consistent with relational quality.

**TODO:** Update the definition of `PMD_0020200` to remove the word "realizable entity"
from its `skos:definition` text (currently reads: "A force is a realizable entity that
consists of...").

---

## Conflict C — Density and Pressure (2 terms)

**Terms:** density `PMD_0000597`, pressure `PMD_0000896`

**Conflict:**
- Old parent: `PMD_0020131` (intensive quality → `BFO_0000019`)
- Migration added: `SubClassOf → PMD_0080069` (physical relational quality → `BFO_0000145`)
- BFO_0000019 ⊥ BFO_0000145 (disjoint siblings in BFO2020) → unsatisfiable
- Cascade: mass spectrometry `PMD_0000836` (has `ObjectSomeValuesFrom(RO_0009006 PMD_0000597)`)
  became unsatisfiable because density was empty/⊥

**Fix applied:** Replaced `SubClassOf(PMD_0000597 PMD_0020131)` and
`SubClassOf(PMD_0000896 PMD_0020131)` with `SubClassOf → PMD_0080069` in the
pre-existing section.

**Ontological rationale:** Pressure (force/area) and density (mass/volume) are both
ratios involving two material quantities. In BFO2020, quantities that relate properties
of multiple entities or are defined as ratios belong under relational quality (BFO_0000145)
rather than intrinsic quality (BFO_0000019).

**TODO:** Review whether the `DisjointClasses` list on the intensive quality siblings
(which included PMD_0000597 and PMD_0000896) needs updating now that they have moved
to the relational quality branch. The DisjointClasses axiom itself is harmless but
logically refers to terms that are no longer siblings under PMD_0020131.

---

## Conflict D — Deformation and Strain (PMD_0000596 + PMD_0080029)

**Terms:** deformation `PMD_0000596`, strain `PMD_0080029`

**Conflict:**
- Old parent of deformation: `BFO_0000015` (process — deformation is an occurrent)
- Migration added: `SubClassOf(PMD_0000596 PMD_0080003)` (mechanische Qualität → `BFO_0000019`)
- BFO_0000015 ⊥ BFO_0000019 → unsatisfiable
- Cascade: stiffness `PMD_0000949` has `ObjectSomeValuesFrom(PMD_0001029 PMD_0000596)` and
  became unsatisfiable because deformation was ⊥, pulling down all moduli
  (PMD_0000539, PMD_0000618, PMD_0080166, PMD_0080167, PMD_0080168) and strain subtypes

**Fix applied:**
1. Removed `SubClassOf(PMD_0000596 PMD_0080003)` from the migration section —
   deformation remains a process (`BFO_0000015`), not a quality.
2. Changed `SubClassOf(PMD_0080029 PMD_0000596)` → `SubClassOf(PMD_0080029 PMD_0080003)` —
   strain (Dehnung) is placed directly under mechanische Qualität, not under deformation.

**Ontological rationale:** Deformation (the act/process of deforming) and strain (the
measurable ratio/quality describing the magnitude of shape change) are distinct. The IOF
hierarchy placed strain under deformation, conflating the process with its measure. In
BFO terms, deformation is correctly a process (BFO_0000015) and strain is a quality
(BFO_0000019). Separating them preserves both classifications.

**TODO:** Review whether the new strain subtypes (PMD_0080030 through PMD_0080035 —
creep strain, elastic deformation, engineering strain, plastic strain, fracture elongation,
true strain) make more ontological sense as direct children of `PMD_0080003`
(mechanische Qualität) rather than as children of `PMD_0080029` (Dehnung/strain). The
current structure places them under strain which is reasonable (strain types), but
confirm this is intentional.

---

## Conflict E — Specific Strength (PMD_0010029)

**Term:** specific strength `PMD_0010029`

**Conflict:**
- Old parent: `BFO_0000019` (quality — direct, overly general)
- Migration added: `SubClassOf(PMD_0010029 PMD_0000952)` (strength → material property → `BFO_0000016`)
- BFO_0000016 ⊥ BFO_0000019 → unsatisfiable

**Fix applied:** Replaced `SubClassOf(PMD_0010029 BFO_0000019)` with
`SubClassOf(PMD_0010029 PMD_0000952)` in the pre-existing section.

**Ontological rationale:** The direct `BFO_0000019` parent was a placeholder/overly
general axiom. Specific strength is a kind of strength (strength per unit density), so
being under `PMD_0000952` (strength → material property → BFO_0000016) is semantically
correct. The definition text refers to it as "a quality that inheres in a material entity"
which should be updated to reflect its classification as a material property/capability.

**TODO:** Update the `skos:definition` of `PMD_0010029` to replace "is a quality" with
"is a material property" (or similar) to align with its new BFO branch.

---

## Summary of TODOs

1. Check if `PMD_0020164` (state of matter boundary) and `PMD_0000882` (phase boundary
   realization) are now orphaned — if so, deprecate or repurpose.
2. Update `skos:definition` of `PMD_0020200` (force) — remove "realizable entity".
3. Review the intensive quality DisjointClasses list — density and pressure have moved.
4. Confirm strain subtypes (PMD_0080030–35) placement under Dehnung is intentional.
5. Update `skos:definition` of `PMD_0010029` (specific strength) — "quality" → "material property".
