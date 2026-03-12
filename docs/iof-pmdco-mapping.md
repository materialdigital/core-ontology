# IOF Qualities ↔ PMDco Mapping Documentation

## Purpose

This document maps concepts between the IOF Qualities Library and PMDco to guide the migration of IOF quality hierarchies into the PMDco ontology. PMDco already exported a number of terms into IOF (annotated with `iof-av:adaptedFrom`). Now we want to sync the other way: adopting IOF's cleaner hierarchical groupers and new terms back into PMDco, while handling the ontology stack differences carefully.

---

## 1. Ontology Stack Differences

### BFO Version

| Aspect | IOF Qualities | PMDco |
|--------|--------------|-------|
| BFO version | BFO 2020 | BFO 2020 (no-time) |
| BFO namespace | `http://purl.obolibrary.org/obo/BFO_...` | `http://purl.obolibrary.org/obo/BFO_...` (same) |

**Note:** Both use BFO 2020 with the same IRIs — no BFO mismatch. The earlier concern about "BFO2 vs BFO2020" does not apply to IRIs, but IOF uses additional IOF Core wrapper classes.

### Property Mapping

| IOF Property | IRI | PMDco Equivalent | IRI | Notes |
|---|---|---|---|---|
| has quality | `iof-core:hasQuality` | has quality | `RO_0000086` | IOF Core wraps RO; same semantics |
| quality of | `iof-core:qualityOf` | quality of | `RO_0000080` | inverse of has quality |
| has process characteristic | `iof-core:hasProcessCharacteristic` | has process attribute | `pmdco:PMD_0000009` | PMDco uses "attribute"; IOF uses "characteristic" |
| process characteristic of | `iof-core:processCharacteristicOf` | process attribute of | `pmdco:PMD_0025006` | inverse |
| has participant | `obo:BFO_0000057` | has participant | `RO_0000057` | same OBO IRI — direct match |
| has realization | `obo:BFO_0000054` | has realization | `obo:BFO_0000054` | same OBO IRI — direct match |
| realizes | `obo:BFO_0000055` | realizes | `obo:BFO_0000055` | same OBO IRI — direct match |
| part of | `obo:BFO_0000050` | part of | `obo:BFO_0000050` | same OBO IRI — direct match |

### Annotation Property Mapping

| IOF Annotation | IRI | PMDco Equivalent | IRI | Notes |
|---|---|---|---|---|
| natural language definition | `iof-av:naturalLanguageDefinition` | definition | `obo:IAO_0000115` | Use IAO_0000115 in PMDco |
| adapted from | `iof-av:adaptedFrom` | definition source | `obo:IAO_0000119` | Different semantics: adaptedFrom = attribution; IAO_0000119 = source citation. Use IAO_0000119 for the link back to IOF |
| is primitive | `iof-av:isPrimitive` | editor note | `obo:IAO_0000116` | No direct PMDco equivalent; annotate primitives with editor note |
| first order logic definition | `iof-av:firstOrderLogicDefinition` | editor note | `obo:IAO_0000116` | No direct equivalent; include in editor note if desired |
| maturity | `iof-av:maturity` | — | — | No equivalent in PMDco |
| skos:example | `skos:example` | skos:example | `skos:example` | Direct match |
| skos:altLabel | `skos:altLabel` | skos:altLabel | `skos:altLabel` | Direct match |

---

## 2. Key IOF Classes Not Present in PMDco (Candidates for Migration)

### 2.1 From `Qualities.rdf` (IOF Base Qualities)

| IOF Class | IRI | Parent in IOF | PMDco Status | Migration Action |
|---|---|---|---|---|
| DimensionQuality | `...Qualities/DimensionQuality` | `BFO_0000019` (Quality) | Missing | **Add** as new quality grouper |
| SpatialRelationalQuality | `...Qualities/SpatialRelationalQuality` | `BFO_0000145` (Relational Quality) | Missing | **Add** as relational quality subtype |
| Action | `...Qualities/Action` | `BFO_0000015` (Process) | Partial match: PMD_0000950 (StimulatingProcess) | **Evaluate** — PMDco's StimulatingProcess has different axioms; needs comparison |
| Reaction | `...Qualities/Reaction` | `BFO_0000015` (Process) | Missing | **Add** if adopting Action; linked via `triggers/isTriggeredBy` |

### 2.2 From `Qualities-Physical.rdf` — Grouper Classes

These are the **organizational root classes** of the IOF physical quality hierarchy. PMDco has corresponding *disposition* hierarchies (under Material Property) but lacks these quality groupers.

| IOF Class | IRI | Parent in IOF | PMDco Disposition Analog | PMDco Quality Status |
|---|---|---|---|---|
| PhysicalQuality | `...Qualities-Physical/PhysicalQuality` | `BFO_0000019` | (none — disposition root is PMD_0000005) | **Add** as top quality grouper |
| ThermoDynamicQuality | `...Qualities-Physical/ThermoDynamicQuality` | PhysicalQuality | PMD_0000967 (Temperature, leaf) | **Add** as grouper |
| AcousticQuality | `...Qualities-Physical/AcousticQuality` | PhysicalQuality | PMD_0000506 (Acoustic Property, disposition) | **Add** — distinct from disposition |
| ElectricalQuality | `...Qualities-Physical/ElectricalQuality` | PhysicalQuality | PMD_0000621 (Electrical Property, disposition) | **Add** — distinct from disposition |
| MagneticQuality | `...Qualities-Physical/MagneticQuality` | PhysicalQuality | PMD_0000825 (Magnetic Property, disposition) | **Add** — distinct from disposition |
| MechanicalQuality | `...Qualities-Physical/MechanicalQuality` | PhysicalQuality | PMD_0000848 (Mechanical Property, disposition) | **Add** — distinct from disposition |
| OpticalQuality | `...Qualities-Physical/OpticalQuality` | PhysicalQuality | PMD_0000877 (Optical Property, disposition) | **Add** — distinct from disposition |
| FluidDynamicQuality | `...Qualities-Physical/FluidDynamicQuality` | PhysicalQuality | (none) | **Add** |
| OlfactoricQuantity | `...Qualities-Physical/OlfactoricQuantity` | PhysicalQuality | (none) | **Add** (low priority) |
| RadiologicQuality | `...Qualities-Physical/RadiologicQuality` | PhysicalQuality | (none) | **Add** (low priority) |
| SurfaceRoughness | `...Qualities-Physical/SurfaceRoughness` | PhysicalQuality | (none as quality) | **Add** |

### 2.3 From `Qualities-Physical.rdf` — PhysicalProcessCharacteristic Sub-tree

IOF introduces `PhysicalProcessCharacteristic` as a subclass of `iof-core:ProcessCharacteristic`. PMDco uses "process attribute" (`PMD_0000009`) as a *relation*, not as a *class*.

| IOF Class | IRI | Parent | PMDco Equivalent | Action |
|---|---|---|---|---|
| PhysicalProcessCharacteristic | `...Qualities-Physical/PhysicalProcessCharacteristic` | `iof-core:ProcessCharacteristic` | Missing class | **Add** — introduce ProcessCharacteristic concept in PMDco |
| ElectricCurrent | `...Qualities-Physical/ElectricCurrent` | PhysicalProcessCharacteristic | (none as process char.) | **Add** |
| ForceRate | `...Qualities-Physical/ForceRate` | PhysicalProcessCharacteristic | (none) | **Add** |
| Frequency | `...Qualities-Physical/Frequency` | PhysicalProcessCharacteristic | (none) | **Add** |
| MassFlowRate | `...Qualities-Physical/MassFlowRate` | PhysicalProcessCharacteristic | (none) | **Add** |
| MechanicalImpulse | `...Qualities-Physical/MechanicalImpulse` | PhysicalProcessCharacteristic | (none) | **Add** |
| RadiantEnergyFlux | `...Qualities-Physical/RadiantEnergyFlux` | PhysicalProcessCharacteristic | (none) | **Add** |
| Speed | `...Qualities-Physical/Speed` | PhysicalProcessCharacteristic | (none as process char.) | **Add** |
| TemperatureProfile | `...Qualities-Physical/TemperatureProfile` | PhysicalProcessCharacteristic | (none) | **Add** |

### 2.4 From `Qualities-MeasurementPerformance.rdf`

| IOF Class | IRI | Parent | PMDco Equivalent | Action |
|---|---|---|---|---|
| PerformanceQuality | `...MeasurementPerformance/PerformanceQuality` | `BFO_0000019` | (none) | **Add** |
| MeasurementRelationalQuality | `...MeasurementPerformance/MeasurementRelationalQuality` | `BFO_0000145` | (none) | **Add** |
| DynamicRange | `...MeasurementPerformance/DynamicRange` | MeasurementRelationalQuality | (none) | **Add** |
| WorkingRange | `...MeasurementPerformance/WorkingRange` | DynamicRange | (none) | **Add** |
| CalibrationRange | `...MeasurementPerformance/CalibrationRange` | DynamicRange | (none) | **Add** |
| Precision | `...MeasurementPerformance/Precision` | MeasurementRelationalQuality | (none) | **Add** |
| DataAcquisitionRate | `...MeasurementPerformance/DataAcquisitionRate` | `iof-core:ProcessCharacteristic` | (none) | **Add** |

---

## 3. IOF Terms Adapted From PMDco (Already in PMDco — Reverse Mapping)

These IOF terms were derived from PMDco and already exist there. The goal is to ensure the PMDco terms are placed under the correct IOF grouper when adopted.

### From `Qualities-Physical.rdf` (33 terms)

| IOF Label | IOF IRI | PMDco IRI | PMDco Parent (current) | Target IOF Grouper |
|---|---|---|---|---|
| acoustic absorption coefficient | `...Physical/AcousticAbsorptionCoefficient` | PMD_0000505 | PMD_0000506 (Acoustic Property / disposition) | AcousticQuality |
| activity (thermodynamic) | `...Physical/ActivityThermodynamic` | PMD_0020161 | BFO_0000145 (Relational Quality) | ThermoDynamicQuality |
| aggregate state | `...Physical/AggregateState` | PMD_0000512 | BFO_0000019 (Quality) | ThermoDynamicQuality |
| band gap | `...Physical/BandGap` | PMD_0090002 | PMD_0000621 (Electrical Property) | ElectricalQuality |
| boiling point | `...Physical/BoilingPoint` | PMD_0000535 | BFO_0000145 (Relational Quality) | ThermoDynamicQuality |
| Brinell hardness | `...Physical/BrinellHardness` | PMD_0000537 | PMD_0000789 (Indentation Hardness) | MechanicalQuality |
| chemical potential | `...Physical/ChemicalPotential` | PMD_0000553 | BFO_0000145 (Relational Quality) | ThermoDynamicQuality |
| density | `...Physical/Density` | PMD_0000597 | PMD_0020131 (Intensive Quality) | PhysicalQuality (or MechanicalQuality) |
| dielectric constant | `...Physical/DielectricConstant` | PMD_0000604 | PMD_0000621 (Electrical Property) | ElectricalQuality |
| dispersion | `...Physical/Dispersion` | PMD_0020247 | PMD_0000877 (Optical Property) | OpticalQuality |
| driving force of phase in system | `...Physical/DrivingForceOfPhaseInSystem` | PMD_0020130 | BFO_0000145 (Relational Quality) | ThermoDynamicQuality |
| elastic modulus | `...Physical/ElasticModulus` | PMD_0000618 | PMD_0000848 (Mechanical Property) | MechanicalQuality |
| electrical conductivity | `...Physical/ElectricalConductivity` | PMD_0000620 | PMD_0000621 (Electrical Property) | ElectricalQuality |
| energy | `...Physical/Energy` | PMD_0020142 | PMD_0020148 (Extensive Quality) | ThermoDynamicQuality |
| hardenable | `...Physical/Hardenable` | PMD_0010013 | (capability-like) | — (disposition, not quality) |
| heat capacity | `...Physical/HeatCapacity` | PMD_0000777 | PMD_0000981 (Thermal Property) | ThermoDynamicQuality |
| interatomic interaction energy | `...Physical/InteratomicInteractionEnergy` | PMD_0020155 | PMD_0020148 (Extensive Quality) | ThermoDynamicQuality |
| internal energy | `...Physical/InternalEnergy` | PMD_0020151 | PMD_0020148 (Extensive Quality) | ThermoDynamicQuality |
| melting point | `...Physical/MeltingPoint` | PMD_0000851 | BFO_0000145 (Relational Quality) | ThermoDynamicQuality |
| Mohs hardness | `...Physical/MohsHardness` | PMD_0000861 | PMD_0000924 (Scratch Hardness) | MechanicalQuality |
| pressure | `...Physical/Pressure` | PMD_0000896 | PMD_0020131 (Intensive Quality) | MechanicalQuality or ThermoDynamicQuality |
| rebound hardness | `...Physical/ReboundHardness` | PMD_0000910 | PMD_0000773 (Hardness) | MechanicalQuality |
| reflectivity | `...Physical/Reflectivity` | PMD_0000911 | PMD_0000877 (Optical Property) | OpticalQuality |
| refraction | `...Physical/Refraction` | PMD_0000790 | PMD_0000877 (Optical Property) | OpticalQuality |
| semiconductivity | `...Physical/Semiconductivity` | PMD_0090001 | PMD_0000621 (Electrical Property) | ElectricalQuality |
| specific surface area | `...Physical/SpecificSurfaceArea` | PMD_0000942 | PMD_0020131 (Intensive Quality) | PhysicalQuality |
| speed of sound | `...Physical/SpeedOfSound` | PMD_0000947 | PMD_0000506 (Acoustic Property) | AcousticQuality |
| stiffness | `...Physical/Stiffness` | PMD_0000949 | PMD_0000848 (Mechanical Property) | MechanicalQuality |
| strength | `...Physical/Strength` | PMD_0000952 | PMD_0000848 (Mechanical Property) | MechanicalQuality |
| sublimation point | `...Physical/SublimationPoint` | PMD_0000961 | BFO_0000145 (Relational Quality) | ThermoDynamicQuality |
| superconducting | `...Physical/Superconducting` | PMD_0000111 | (capability-like) | — (disposition, not quality) |
| thermal conductivity | `...Physical/ThermalConductivity` | PMD_0000978 | PMD_0000981 (Thermal Property) | ThermoDynamicQuality |
| triple point | `...Physical/TriplePoint` | PMD_0000996 | BFO_0000145 (Relational Quality) | ThermoDynamicQuality |

### From `Qualities-MaterialStructure.rdf` (11 quality terms + 3 capability terms)

| IOF Label | IOF IRI | PMDco IRI | PMDco Parent (current) | Notes |
|---|---|---|---|---|
| crystal structure | `...MaterialStructure/CrystalStructure` | PMD_0000591 | PMD_0020131 (Intensive Quality) | already in PMDco correctly |
| crystallographic texture | `...MaterialStructure/CrystallographicTexture` | PMD_0000853 | PMD_0020131 (Intensive Quality) | already correct |
| defect density | `...MaterialStructure/DefectDensity` | PMD_0000595 | PMD_0020131 (Intensive Quality) | already correct |
| grain size | `...MaterialStructure/GrainSize` | PMD_0020243 | PMD_0020131 (Intensive Quality) | already correct |
| ASTM grain size | `...MaterialStructure/ASTMGrainSize` | PMD_0000503 | PMD_0020131 (Intensive Quality) | already correct |
| grain size distribution | `...MaterialStructure/GrainSizeDistribution` | PMD_0020112 | PMD_0020131 (Intensive Quality) | already correct |
| metallic grain structure | `...MaterialStructure/MetallicGrainStructure` | PMD_0025003 | PMD_0020131 (Intensive Quality) | already correct |
| order scale | `...MaterialStructure/OrderScale` | PMD_0020220 | PMD_0020131 (Intensive Quality) | already correct |
| angle of misalignment | `...MaterialStructure/AngleOfMisalignment` | PMD_0020241 | PMD_0020131 (Intensive Quality) | already correct |
| Burgers vector | `...MaterialStructure/BurgersVector` | PMD_0020237 | PMD_0020131 (Intensive Quality) | already correct |
| polymorphism of crystal | `...MaterialStructure/PolymorphismOfCrystal` | PMD_0020212 | PMD_0000016 (Disposition) | capability in IOF |
| allotropy of elemental crystal | `...MaterialStructure/AllotropyOfAnElementalCrystal` | PMD_0020211 | PMD_0000016 (Disposition) | capability in IOF |
| disposition of a phase to transform | `...MaterialStructure/DispositionOfAPhaseToTransform` | PMD_0020165 | PMD_0000016 (Disposition) | capability in IOF |

---

## 4. Critical Design Decision: Quality vs. Disposition

The most important structural difference between IOF and PMDco:

**IOF** classifies many quantifiable material attributes (hardness, conductivity, modulus) directly as **qualities** (`BFO_0000019`), within `PhysicalQuality > MechanicalQuality`, etc.

**PMDco** currently classifies these as **dispositions** (`BFO_0000016`) under `MaterialProperty (PMD_0000005)`, where:
- `MaterialProperty` = "disposition realized in compatible process, grounded in intensive qualities"
- This is intentional: the *property* is the material's *tendency* to exhibit behavior, not the measurement result

**Consequence:**
- `PMD_0000505` (Acoustic Absorption Coefficient) is a subclass of `PMD_0000506` (Acoustic Property) which is a subclass of `BFO_0000016` (Disposition)
- IOF's `AcousticAbsorptionCoefficient` is a subclass of `AcousticQuality` which is a subclass of `BFO_0000019` (Quality)

**Resolution Options:**

**Option A — Strict separation (recommended):** Introduce IOF quality groupers as NEW classes alongside existing disposition hierarchy. The groupers (`PhysicalQuality`, `AcousticQuality`, etc.) serve as quality-level anchors. Existing PMDco terms under MaterialProperty STAY as dispositions. New QUALITY versions of those concepts (when needed) go under the new groupers. Cross-reference with `obo:IAO_0000119`.

**Option B — Relocation:** Move existing PMDco terms that are genuinely qualities (not just dispositions) out from under MaterialProperty and under the new IOF quality groupers. This is a breaking change but more ontologically correct.

**Option C — Multiple inheritance:** Make existing PMDco disposition terms ALSO subclasses of the appropriate IOF quality grouper where they genuinely represent both. This is permissible in OWL but risks confusion.

The recommendation is **Option A** for now, with a clear annotation pointing from each new quality grouper to the related disposition class in PMDco notes.

---

## 5. ProcessCharacteristic: A New Concept for PMDco

IOF Core defines `ProcessCharacteristic` as a **Continuant** that summarizes an attribute of a process over its entire duration. PMDco currently lacks this class — it has a *relation* `PMD_0000009` (has process attribute) but no corresponding *class* for the attribute itself.

**Mapping:**

| IOF | PMDco (proposed) | Notes |
|---|---|---|
| `iof-core:ProcessCharacteristic` | New class `PMD_NEW` (ProcessCharacteristic) | subClassOf BFO_0000002 (Continuant) — analogous to IOF |
| `iof-core:hasProcessCharacteristic` | `PMD_0000009` (has process attribute) | Already exists — use as equivalent; annotate |
| `iof-core:processCharacteristicOf` | `PMD_0025006` (process attribute of) | Already exists |
| `PhysicalProcessCharacteristic` | New class `PMD_NEW` | subClassOf new ProcessCharacteristic |

---

## 6. Proposed Migration Hierarchy for PMDco

```
BFO_0000019 (Quality)
└── [NEW] PhysicalQuality  (adopted from IOF)
    ├── DimensionQuality  (adopted from IOF Qualities base)
    │   └── Length  (adopted from IOF)
    ├── ThermoDynamicQuality  (adopted from IOF)
    │   ├── PMD_0000512 (Aggregate State) — relocate from direct BFO_0000019
    │   ├── PMD_0000967 (Temperature) — relocate from IntensiveQuality
    │   ├── PMD_0000851 (Melting Point) — relocate from BFO_0000145
    │   ├── PMD_0000535 (Boiling Point) — relocate from BFO_0000145
    │   ├── PMD_0000961 (Sublimation Point) — relocate from BFO_0000145
    │   ├── PMD_0000996 (Triple Point) — relocate from BFO_0000145
    │   ├── PMD_0000553 (Chemical Potential) — relocate from BFO_0000145
    │   ├── PMD_0020130 (Driving Force of Phase) — relocate from BFO_0000145
    │   ├── PMD_0020161 (Activity Thermodynamic) — stays under relational quality
    │   ├── PMD_0000777 (Heat Capacity) — relocate from Thermal Property
    │   ├── PMD_0000978 (Thermal Conductivity) — relocate from Thermal Property
    │   ├── PMD_0020142 (Energy) — relocate from ExtensiveQuality
    │   ├── PMD_0020151 (Internal Energy) — stays under ExtensiveQuality
    │   └── PMD_0020155 (Interatomic Interaction Energy) — stays under ExtensiveQuality
    ├── AcousticQuality  (adopted from IOF)
    │   ├── PMD_0000505 (Acoustic Absorption Coefficient) — CURRENTLY under disposition!
    │   └── PMD_0000947 (Speed of Sound) — CURRENTLY under disposition!
    ├── ElectricalQuality  (adopted from IOF)
    │   ├── PMD_0000620 (Electrical Conductivity) — CURRENTLY under disposition!
    │   ├── PMD_0000604 (Dielectric Constant) — CURRENTLY under disposition!
    │   ├── PMD_0090001 (Semiconductivity) — CURRENTLY under disposition!
    │   └── PMD_0090002 (Band Gap) — CURRENTLY under disposition!
    ├── MagneticQuality  (adopted from IOF)
    │   └── [existing PMD magnetic terms from PMD_0000825 subtree]
    ├── MechanicalQuality  (adopted from IOF)
    │   ├── PMD_0000618 (Elastic Modulus) — CURRENTLY under disposition!
    │   ├── PMD_0000949 (Stiffness) — CURRENTLY under disposition!
    │   ├── PMD_0000952 (Strength) — CURRENTLY under disposition!
    │   ├── PMD_0000773 (Hardness) — CURRENTLY under disposition!
    │   │   ├── PMD_0000789 (Indentation Hardness)
    │   │   │   └── PMD_0000537 (Brinell Hardness)
    │   │   ├── PMD_0000910 (Rebound Hardness)
    │   │   └── PMD_0000924 (Scratch Hardness)
    │   │       └── PMD_0000861 (Mohs Hardness)
    │   └── PMD_0000896 (Pressure) — CURRENTLY under IntensiveQuality
    ├── OpticalQuality  (adopted from IOF)
    │   ├── PMD_0000911 (Reflectivity) — CURRENTLY under disposition!
    │   ├── PMD_0000790 (Refraction) — CURRENTLY under disposition!
    │   └── PMD_0020247 (Dispersion) — CURRENTLY under disposition!
    ├── FluidDynamicQuality  (adopted from IOF, new)
    │   └── [Viscosity and subtypes — new from IOF]
    ├── SurfaceRoughness  (adopted from IOF, new)
    ├── PMD_0000597 (Density) — stays under IntensiveQuality or move here
    └── PMD_0000942 (Specific Surface Area) — stays under IntensiveQuality or move here

BFO_0000145 (Relational Quality)
├── [NEW] SpatialRelationalQuality  (adopted from IOF)
├── [NEW] MeasurementRelationalQuality  (adopted from IOF)
│   ├── [NEW] DynamicRange
│   │   ├── [NEW] WorkingRange
│   │   └── [NEW] CalibrationRange
│   └── [NEW] Precision
└── PMD_0025998 (has relational quality) — already exists as object property

BFO_0000002 (Continuant)
└── [NEW] ProcessCharacteristic  (concept adopted from IOF Core)
    └── [NEW] PhysicalProcessCharacteristic  (adopted from IOF)
        ├── [NEW] ElectricCurrent
        ├── [NEW] ForceRate
        ├── [NEW] Frequency
        ├── [NEW] MassFlowRate
        ├── [NEW] MechanicalImpulse
        ├── [NEW] RadiantEnergyFlux
        ├── [NEW] Speed
        └── [NEW] TemperatureProfile

BFO_0000019 (Quality)
└── [NEW] PerformanceQuality  (adopted from MeasurementPerformance, new)

PMD_0000005 (Material Property / Disposition) [KEEP AS IS]
├── PMD_0000506 (Acoustic Property) [KEEP]
├── PMD_0000621 (Electrical Property) [KEEP]
├── PMD_0000825 (Magnetic Property) [KEEP]
├── PMD_0000848 (Mechanical Property) [KEEP]
├── PMD_0000877 (Optical Property) [KEEP]
└── PMD_0000981 (Thermal Property) [KEEP]
```

**Terms marked "CURRENTLY under disposition!"** require the most careful migration decision (see Section 4, Option A/B/C).

---

## 7. Open Questions / Decisions Needed

1. **Quality vs. Disposition relocation** (Section 4): Which option? Relocating terms marked "CURRENTLY under disposition" is a breaking change. Option A (parallel hierarchies) is safer but creates redundancy.

2. **ProcessCharacteristic class**: Should PMDco introduce this as a new concept or reuse/rename the existing `PMD_0000009` object property's range? The IOF class is a Continuant subtype.

3. **Action/Reaction**: IOF's `Action` partially overlaps with PMDco's `PMD_0000950` (Stimulating Process) and `PMD_0001028/PMD_0001029` (in response to / responds with). Direct adoption or explicit cross-reference?

4. **IOF-only terms** (FluidDynamicQuality, Viscosity, OlfactoricQuantity, RadiologicQuality, MeasurementPerformance terms): These are entirely new — add all or prioritize MSE-relevant ones?

5. **IRI assignment**: New PMDco terms need fresh `PMD_XXXXXXX` IRIs. What number range to use? (Existing ranges: 0000xxx, 0010xxx, 0020xxx, 0025xxx, 004xxxx, 005xxxx, 009xxxx)

6. **Back-reference annotation**: When adopting an IOF term into PMDco, annotate with `obo:IAO_0000119` pointing to the IOF IRI? Or introduce a custom annotation like `adaptedFrom` mirroring IOF's approach?

---

## 8. IOF Terms in Physical Qualities Not Yet in PMDco (New Leaf Terms)

Beyond the groupers, these leaf terms appear in IOF Physical that are NOT in PMDco:

| IOF Label | IOF IRI | IOF Parent | Priority |
|---|---|---|---|
| length | `...Physical/Length` | DimensionQuality | High |
| surface roughness | `...Physical/SurfaceRoughness` | PhysicalQuality | High |
| viscosity | `...Physical/Viscosity` | FluidDynamicQuality | Medium |
| dynamic viscosity | `...Physical/DynamicViscosity` | Viscosity | Medium |
| glass transition temperature | `...Physical/GlassTransitionTemperature` | DuctileBrittleTransitionTemperature | High |
| ductile-brittle transition temperature | `...Physical/DuctileBrittleTransitionTemperature` | ThermoDynamicQuality | High |
| linear thermal expansion coefficient | `...Physical/LinearThermalExpansionCoefficient` | ThermalExpansionCoefficient | High |
| thermal expansion coefficient | `...Physical/ThermalExpansionCoefficient` | ThermoDynamicQuality | High |
| dynamic range | `...MeasurementPerformance/DynamicRange` | MeasurementRelationalQuality | Medium |
| precision | `...MeasurementPerformance/Precision` | MeasurementRelationalQuality | Medium |
| data acquisition rate | `...MeasurementPerformance/DataAcquisitionRate` | ProcessCharacteristic | Medium |

*(Full enumeration of all 261 Physical quality classes pending — only MSE-relevant subset shown here)*
