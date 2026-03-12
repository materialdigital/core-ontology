# IOF → PMDco Migration Report

Status legend
- **NEW** — fresh term; PMD IRI just assigned, not yet in ontology
- **PENDING** — PMD IRI assigned in a previous run but not yet merged into ontology
- **MERGED** — term was already merged into the ontology (skipped in output)
- **EXISTS** — mapped to a pre-existing PMDco/BFO IRI (never re-emitted)

---

## acoustic quality
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/AcousticQuality`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000019`
- Note: Grouper for acoustic qualities

### Hierarchy

- **acoustic quality** `PMD_0080000` [PENDING]
  - **sound reflection coefficient** `PMD_0080021` [PENDING]

## electrical quality
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/ElectricalQuality`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000019`
- Note: Grouper for electrical qualities

### Hierarchy

- **electrical quality** `PMD_0080001` [PENDING]
  - **band gap** `PMD_0090002` [EXISTS]
  - **dielectric strength** `PMD_0080024` [PENDING]
  - **electric charge** `PMD_0080022` [PENDING]
  - **electric field strength** `PMD_0080023` [PENDING]

## magnetic quality
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/MagneticQuality`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000019`
- Note: Grouper for magnetic qualities

### Hierarchy

- **magnetic quality** `PMD_0080002` [PENDING]
  - **coercivity** `PMD_0080027` [PENDING]
  - **magnetic flux** `PMD_0080025` [PENDING]
  - **magnetic permeability** `PMD_0080026` [PENDING]

## mechanical quality
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/MechanicalQuality`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000019`
- Note: Grouper for mechanical qualities

### Hierarchy

- **mechanical quality** `PMD_0080003` [PENDING]
  - **deformation** `PMD_0080028` [PENDING]
    - **strain** `PMD_0080029` [PENDING]
      - **creep strain** `PMD_0080031` [PENDING]
      - **elastic strain** `PMD_0080034` [PENDING]
      - **engineering strain** `PMD_0080030` [PENDING]
      - **plastic strain** `PMD_0080035` [PENDING]
      - **strain at break** `PMD_0080033` [PENDING]
      - **true strain** `PMD_0080032` [PENDING]

## optical quality
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/OpticalQuality`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000019`
- Note: Grouper for optical qualities

### Hierarchy

- **optical quality** `PMD_0080004` [PENDING]
  - **exposure** `PMD_0080037` [PENDING]
  - **luminous intensity** `PMD_0080036` [PENDING]

## thermo dynamic quality
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/ThermoDynamicQuality`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000019`
- Note: Grouper for thermodynamic qualities

### Hierarchy

- **thermo dynamic quality** `PMD_0080005` [PENDING]
  - **activity (thermodynamic)** `PMD_0020161` [EXISTS]
  - **aggregate state** `PMD_0000512` [EXISTS]
  - **auto-ignition temperature** `PMD_0080055` [PENDING]
  - **boiling point** `PMD_0000535` [EXISTS]
  - **chemical potential** `PMD_0000553` [EXISTS]
  - **critical pressure** `PMD_0080041` [PENDING]
  - **critical temperature** `PMD_0080042` [PENDING]
  - **Curie temperature** `PMD_0080038` [PENDING]
  - **driving force of phase in system** `PMD_0020130` [EXISTS]
  - **ductile-brittle transition temperature** `PMD_0080048` [PENDING]
    - **glass transition temperature** `PMD_0080049` [PENDING]
  - **energy** `PMD_0020142` [EXISTS]
    - **enthalpy** `PMD_0080052` [PENDING]
      - **heat of fusion** `PMD_0080053` [PENDING]
      - **heat of vaporization** `PMD_0080054` [PENDING]
    - **entropy** `PMD_0080050` [PENDING]
    - **interatomic interaction energy** `PMD_0020155` [EXISTS]
    - **internal energy** `PMD_0020151` [EXISTS]
    - **surface energy** `PMD_0080051` [PENDING]
  - **eutectic point** `PMD_0080040` [PENDING]
  - **flash point** `PMD_0080047` [PENDING]
  - **melting point** `PMD_0000851` [EXISTS]
  - **specific heat capacity** `PMD_0080039` [PENDING]
  - **sublimation point** `PMD_0000961` [EXISTS]
  - **temperature** `PMD_0080043` [PENDING]
    - **aging temperature** `PMD_0080044` [PENDING]
    - **environmental temperature** `PMD_0080045` [PENDING]
  - **triple point** `PMD_0000996` [EXISTS]
  - **vapor pressure** `PMD_0080046` [PENDING]

## fluid dynamic quality
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/FluidDynamicQuality`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000019`
- Note: Grouper for fluid dynamic qualities

### Hierarchy

- **fluid dynamic quality** `PMD_0080006` [PENDING]
  - **Reynolds number** `PMD_0080056` [PENDING]

## radiologic quality
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/RadiologicQuality`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000019`
- Note: Grouper for radiologic qualities

### Hierarchy

- **radiologic quality** `PMD_0080007` [PENDING]

## olfactoric quality
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/OlfactoricQuantity`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000019`
- Note: Grouper for olfactoric qualities

### Hierarchy

- **olfactoric quality** `PMD_0080008` [PENDING]
  - **odor** `PMD_0080057` [PENDING]
    - **odorless** `PMD_0080058` [PENDING]
    - **odorous** `PMD_0080059` [PENDING]

## dimension quality
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities/DimensionQuality`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000019`
- Note: Spatial extent quality subtree; excluding AnteriorPosteriorDiameter and DendriticFieldSize

### Hierarchy

- **dimension quality** `PMD_0080009` [PENDING]
  - **area** `PMD_0080019` [PENDING]
  - **length** `PMD_0080020` [PENDING]
    - **depth** `PMD_0080064` [PENDING]
    - **diameter** `PMD_0080063` [PENDING]
    - **height** `PMD_0080066` [PENDING]
    - **perimeter** `PMD_0080067` [PENDING]
      - **circumference** `PMD_0080068` [PENDING]
    - **radius** `PMD_0080061` [PENDING]
    - **thickness** `PMD_0080060` [PENDING]
    - **wavelength** `PMD_0080065` [PENDING]
    - **width** `PMD_0080062` [PENDING]
  - **volume** `PMD_0080018` [PENDING]

## spatial relational quality
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities/SpatialRelationalQuality`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000145`
- Note: Relational quality by virtue of spatial relation to other entities

### Hierarchy

- **spatial relational quality** `PMD_0080010` [PENDING]

## physical relational quality
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/PhysicalRelationalQuality`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000145`
- Note: Physical relational qualities: density

### Hierarchy

- **physical relational quality** `PMD_0080069` [PENDING]
  - **birefringence** `PMD_0080093` [PENDING]
  - **coefficient of friction** `PMD_0080082` [PENDING]
  - **contact angle** `PMD_0080095` [PENDING]
  - **density** `PMD_0000597` [EXISTS]
    - **electric flux density** `PMD_0080092` [PENDING]
    - **number density** `PMD_0080090` [PENDING]
      - **pixel density** `PMD_0080091` [PENDING]
    - **radiant energy density** `PMD_0080089` [PENDING]
  - **dose equivalent** `PMD_0080088` [PENDING]
  - **fluid permeability** `PMD_0080121` [PENDING]
  - **force** `PMD_0080084` [PENDING]
    - **friction** `PMD_0080086` [PENDING]
    - **thrust** `PMD_0080087` [PENDING]
    - **weight** `PMD_0080085` [PENDING]
  - **heat transfer coefficient** `PMD_0080119` [PENDING]
  - **inductance** `PMD_0080083` [PENDING]
  - **magnetic susceptibility** `PMD_0080120` [PENDING]
  - **material composition** `PMD_0080096` [PENDING]
    - **mass concentration** `PMD_0080101` [PENDING]
    - **mass ratio** `PMD_0080097` [PENDING]
      - **dry mass** `PMD_0080099` [PENDING]
      - **mass fraction** `PMD_0080100` [PENDING]
      - **mass mix ratio** `PMD_0080098` [PENDING]
    - **volume ratio** `PMD_0080102` [PENDING]
      - **volume concentration** `PMD_0080103` [PENDING]
      - **volume fraction** `PMD_0080104` [PENDING]
      - **volume mix ratio** `PMD_0080105` [PENDING]
  - **physical rate quality** `PMD_0080070` [PENDING]
    - **electromotive force** `PMD_0080078` [PENDING]
    - **emissivity** `PMD_0080071` [PENDING]
    - **humidity** `PMD_0080079` [PENDING]
    - **luminous efficacy** `PMD_0080073` [PENDING]
    - **mass diffusivity** `PMD_0080076` [PENDING]
    - **optical absorptance** `PMD_0080074` [PENDING]
    - **optical reflectance** `PMD_0080077` [PENDING]
    - **optical transmittance** `PMD_0080075` [PENDING]
    - **relative isotopic mass** `PMD_0080072` [PENDING]
    - **thermal diffusivity** `PMD_0080080` [PENDING]
    - **work hardening coefficient** `PMD_0080081` [PENDING]
  - **piezoelectric coefficient** `PMD_0080106` [PENDING]
  - **potential** `PMD_0080116` [PENDING]
    - **electric potential** `PMD_0080117` [PENDING]
    - **mass potential** `PMD_0080118` [PENDING]
  - **pressure** `PMD_0000896` [EXISTS]
    - **adhesion** `PMD_0080112` [PENDING]
      - **surface tension** `PMD_0080113` [PENDING]
    - **clamping pressure** `PMD_0080107` [PENDING]
    - **stress** `PMD_0080108` [PENDING]
      - **creep stress** `PMD_0080111` [PENDING]
      - **engineering stress** `PMD_0080109` [PENDING]
      - **true stress** `PMD_0080110` [PENDING]
  - **refractive index** `PMD_0080114` [PENDING]
    - **extinction coefficient** `PMD_0080115` [PENDING]
  - **stress relaxation** `PMD_0080094` [PENDING]

## speed
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/Speed`
- Target parent in PMDco: `https://w3id.org/pmd/co/PMD_0000008`
- Note: Process attribute: rate of change of position

### Hierarchy

- **speed** `PMD_0080011` [PENDING]
  - **deformation speed** `PMD_0080123` [PENDING]
  - **phase velocity** `PMD_0080122` [PENDING]

## electric current
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/ElectricCurrent`
- Target parent in PMDco: `https://w3id.org/pmd/co/PMD_0000008`
- Note: Process attribute: flow of electric charge per unit time

### Hierarchy

- **electric current** `PMD_0080012` [PENDING]

## force rate
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/ForceRate`
- Target parent in PMDco: `https://w3id.org/pmd/co/PMD_0000008`
- Note: Process attribute: rate of change of force

### Hierarchy

- **force rate** `PMD_0080013` [PENDING]

## mass flow rate
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/MassFlowRate`
- Target parent in PMDco: `https://w3id.org/pmd/co/PMD_0020226`
- Note: Process attribute: mass flow rate; placed under existing PMD_0020226 (flow)

### Hierarchy

- **mass flow rate** `PMD_0080014` [PENDING]

## mechanical impulse
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/MechanicalImpulse`
- Target parent in PMDco: `https://w3id.org/pmd/co/PMD_0000008`
- Note: Process attribute: mechanical impulse

### Hierarchy

- **mechanical impulse** `PMD_0080015` [PENDING]

## radiant energy flux
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/RadiantEnergyFlux`
- Target parent in PMDco: `https://w3id.org/pmd/co/PMD_0020244`
- Note: Process attribute: radiant energy flux; placed under existing PMD_0020244 (flux)

### Hierarchy

- **radiant energy flux** `PMD_0080016` [PENDING]

## temperature profile
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/TemperatureProfile`
- Target parent in PMDco: `https://w3id.org/pmd/co/PMD_0000008`
- Note: Process attribute: temperature profile over process duration

### Hierarchy

- **temperature profile** `PMD_0080017` [PENDING]

## acoustic capability
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/AcousticCapability`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000016`
- Note: Acoustic capability grouper

### Hierarchy

- **acoustic capability** `PMD_0080124` [PENDING]
  - **acoustic absorption coefficient** `PMD_0000505` [EXISTS]
  - **sound insulation index** `PMD_0080125` [PENDING]
  - **speed of sound** `PMD_0000947` [EXISTS]

## electrical capability
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/ElectricalCapability`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000016`
- Note: Electrical capability grouper

### Hierarchy

- **electrical capability** `PMD_0080126` [PENDING]
  - **dielectric constant** `PMD_0000604` [EXISTS]
  - **electrical capacitance** `PMD_0080127` [PENDING]
  - **electrical conductance** `PMD_0080129` [PENDING]
  - **electrical conductivity** `PMD_0000620` [EXISTS]
  - **electrical resistance** `PMD_0080128` [PENDING]
  - **semiconductivity** `PMD_0090001` [EXISTS]
  - **superconducting** `PMD_0000111` [EXISTS]

## magnetic capability
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/MagneticCapability`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000016`
- Note: Magnetic capability grouper

### Hierarchy

- **magnetic capability** `PMD_0080130` [PENDING]
  - **saturation magnetization** `PMD_0080131` [PENDING]

## mechanical capability
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/MechanicalCapability`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000016`
- Note: Mechanical capability grouper; includes Strength/Hardness/Elasticity subtree

### Hierarchy

- **mechanical capability** `PMD_0080132` [PENDING]
  - **brittleness** `PMD_0080180` [PENDING]
  - **ductility** `PMD_0080181` [PENDING]
    - **malleability** `PMD_0080182` [PENDING]
  - **durability** `PMD_0080133` [PENDING]
    - **creep resistance** `PMD_0080135` [PENDING]
    - **wear resistance** `PMD_0080134` [PENDING]
  - **hardenable** `PMD_0010013` [EXISTS]
  - **impact energy** `PMD_0080139` [PENDING]
  - **load cell capacity** `PMD_0080183` [PENDING]
  - **material fatigue** `PMD_0080138` [PENDING]
  - **poisson effect** `PMD_0080136` [PENDING]
    - **poisson's ratio** `PMD_0080137` [PENDING]
  - **resilience** `PMD_0080184` [PENDING]
  - **strength** `PMD_0000952` [EXISTS]
    - **adhesion strength** `PMD_0080169` [PENDING]
    - **elasticity** `PMD_0080164` [PENDING]
      - **stiffness** `PMD_0000949` [EXISTS]
        - **bulk modulus** `PMD_0080165` [PENDING]
        - **elastic modulus** `PMD_0000618` [EXISTS]
        - **flexural modulus** `PMD_0080168` [PENDING]
        - **shear modulus** `PMD_0080166` [PENDING]
        - **specific elastic modulus** `PMD_0080167` [PENDING]
    - **fatigue strength** `PMD_0080163` [PENDING]
    - **hardness** `PMD_0080140` [PENDING]
      - **indentation hardness** `PMD_0080141` [PENDING]
        - **Brinell hardness** `PMD_0000537` [EXISTS]
      - **rebound hardness** `PMD_0000910` [EXISTS]
      - **scratch hardness** `PMD_0080142` [PENDING]
        - **Mohs hardness** `PMD_0000861` [EXISTS]
    - **mechanical strength** `PMD_0080161` [PENDING]
      - **proof strength** `PMD_0080162` [PENDING]
    - **operational strength** `PMD_0080158` [PENDING]
      - **weathering resistance** `PMD_0080159` [PENDING]
    - **plasticity** `PMD_0080170` [PENDING]
      - **viscosity** `PMD_0080174` [PENDING]
        - **dynamic viscosity** `PMD_0080178` [PENDING]
        - **extentional viscosity** `PMD_0080175` [PENDING]
        - **kinematic viscosity** `PMD_0080177` [PENDING]
        - **shear viscosity** `PMD_0080176` [PENDING]
        - **volume viscosity** `PMD_0080179` [PENDING]
      - **yield strength** `PMD_0080171` [PENDING]
        - **lower yield strength** `PMD_0080172` [PENDING]
        - **upper yield strength** `PMD_0080173` [PENDING]
    - **specific strength** `PMD_0080160` [PENDING]
    - **toughness** `PMD_0080150` [PENDING]
      - **breaking strength** `PMD_0080153` [PENDING]
        - **compressive strength** `PMD_0080155` [PENDING]
        - **flexural strength** `PMD_0080156` [PENDING]
        - **shear strength** `PMD_0080157` [PENDING]
        - **tensile strength** `PMD_0080154` [PENDING]
      - **fracture toughness** `PMD_0080151` [PENDING]
      - **impact strength** `PMD_0080152` [PENDING]
    - **viscoelasticity** `PMD_0080143` [PENDING]
      - **complex modulus** `PMD_0080145` [PENDING]
        - **dynamic modulus** `PMD_0080147` [PENDING]
          - **loss tangent** `PMD_0080148` [PENDING]
        - **loss modulus** `PMD_0080146` [PENDING]
        - **storage modulus** `PMD_0080149` [PENDING]
      - **creep modulus** `PMD_0080144` [PENDING]
    - **weathering resistance** `PMD_0080159` [PENDING]

## optical capability
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/OpticalCapability`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000016`
- Note: Optical capability grouper

### Hierarchy

- **optical capability** `PMD_0080185` [PENDING]
  - **dispersion** `PMD_0020247` [EXISTS]
  - **radiation absorption capability** `PMD_0080187` [PENDING]
  - **radiation emitter** `PMD_0080188` [PENDING]
  - **radiation reflection capability** `PMD_0080186` [PENDING]
  - **radiation transmission capability** `PMD_0080189` [PENDING]
  - **reflectivity** `PMD_0000911` [EXISTS]
  - **refraction** `PMD_0000790` [EXISTS]

## thermal capability
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/ThermalCapability`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000016`
- Note: Thermal capability grouper

### Hierarchy

- **thermal capability** `PMD_0080190` [PENDING]
  - **cooling capability** `PMD_0080199` [PENDING]
  - **flame resistance** `PMD_0080200` [PENDING]
  - **flammability** `PMD_0080192` [PENDING]
  - **heat capacity** `PMD_0000777` [EXISTS]
  - **heating capability** `PMD_0080193` [PENDING]
  - **radiant energy** `PMD_0080195` [PENDING]
  - **thermal capacity** `PMD_0080191` [PENDING]
  - **thermal conductance** `PMD_0080201` [PENDING]
  - **thermal conductivity** `PMD_0000978` [EXISTS]
  - **thermal expansion coefficient** `PMD_0080196` [PENDING]
    - **linear thermal expansion coefficient** `PMD_0080198` [PENDING]
    - **volumetric thermal expansion coefficient** `PMD_0080197` [PENDING]
  - **thermal insulation** `PMD_0080194` [PENDING]
  - **thermal shock resistance** `PMD_0080202` [PENDING]

## radiation emission capability
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/RadiationEmissonCapability`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000016`
- Note: Radiation emission capability

### Hierarchy

- **radiation emission capability** `PMD_0080203` [PENDING]

## water absorption
- IOF source: `https://spec.industrialontologies.org/ontology/qualities/Qualities-Physical/WaterAbsorption`
- Target parent in PMDco: `http://purl.obolibrary.org/obo/BFO_0000016`
- Note: Water absorption capability

### Hierarchy

- **water absorption** `PMD_0080204` [PENDING]

---

## Summary

| Status | Count |
|--------|-------|
| NEW (output this run) | 0 |
| PENDING (output, not yet merged) | 206 |
| MERGED (skipped, already in ontology) | 0 |
| EXISTS (pre-existing PMDco term) | 32 |
