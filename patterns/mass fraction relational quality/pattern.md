- **Purpose**: Express that a relational quality connecting two mass qualities — one of a part and one of a whole — is a mass proportion (`pmd:PMD_0020102`).

- **Description**: A mass proportion is a relational quality (`BFO_0000145`) that links the mass quality of a part to the mass quality of the whole that contains it. The pattern anchors the axiom on the part's mass quality: the relational quality is `relational quality of` (PMD_0025999) some mass quality, whose bearer (`quality of`, RO_0000080) is `part of` (BFO_0000050) some independent continuant that itself `has quality` (RO_0000086) some mass quality.

  The formal equivalence axiom (Manchester syntax):
  ```
  'mass proportion' EquivalentTo:
      'proportion'
      and ('relational quality of' some
          (mass
           and ('quality of' some
               (entity
                and ('part of' some
                    (entity
                     and ('has quality' some mass)))))))
  ```

  The example encodes:
  - `sugarPortion` part of `sugarSolution`
  - `massOfSugar` (mass quality) quality of `sugarPortion`
  - `massOfSolution` (mass quality) quality of `sugarSolution`
  - `massFractionRQ` relational quality of `massOfSugar`

  After reasoning, `massFractionRQ` is classified as `pmd:PMD_0020102` (mass proportion).

  Verified with Konclude (WASM via rdf-reasoner-konclude CLI, materialize mode).

- **What needs to change in pmdco-base.ttl**:

  1. **Add the equivalence axiom** on `pmd:PMD_0020102`. Currently it only has `rdfs:subClassOf pmd:PMD_0020101`. The OWL file must add:
     ```turtle
     pmd:PMD_0020102 owl:equivalentClass [
         a owl:Class ;
         owl:intersectionOf (
             pmd:PMD_0020101
             [ a owl:Restriction ;
               owl:onProperty pmd:PMD_0025999 ;
               owl:someValuesFrom [
                   a owl:Class ;
                   owl:intersectionOf (
                       pmd:PMD_0020133
                       [ a owl:Restriction ;
                         owl:onProperty obo:RO_0000080 ;
                         owl:someValuesFrom [
                             a owl:Class ;
                             owl:intersectionOf (
                                 obo:BFO_0000004
                                 [ a owl:Restriction ;
                                   owl:onProperty obo:BFO_0000050 ;
                                   owl:someValuesFrom [
                                       a owl:Class ;
                                       owl:intersectionOf (
                                           obo:BFO_0000004
                                           [ a owl:Restriction ;
                                             owl:onProperty obo:RO_0000086 ;
                                             owl:someValuesFrom pmd:PMD_0020133 ]
                                       ) ] ] ) ] ] ]
         )
     ] .
     ```

  2. **Declare `RO_0000086` as inverse of `RO_0000080`** (if not already present). pmdco-base.ttl currently only declares `obo:RO_0000086 rdf:type owl:ObjectProperty` without the inverse, so the reasoner cannot infer `has quality` from `quality of` assertions. Add:
     ```turtle
     obo:RO_0000086 owl:inverseOf obo:RO_0000080 .
     ```
     This is needed so that ABox assertions of the form `massQuality quality_of entity` entail `entity has_quality massQuality`, which the restriction at the end of the chain requires.

- **Note on OWL expressivity**: The axiom uses nested existential restrictions with object property chains. ELK (EL profile reasoner) does not classify the individual correctly; Konclude (OWL 2 DL) and HermiT do handle the TBox correctly. For ABox individual classification use Konclude or HermiT in materialize/full-ABox mode, not ROBOT `reason` (which only adds TBox inferences by default).

alternative Visualization using [visgraph](https://thhanke.github.io/visgraph/?rdfUrl=https://raw.githubusercontent.com/materialdigital/core-ontology/feat/mass-fraction-relational-quality-pattern/patterns/mass%20fraction%20relational%20quality/shape-data.ttl)
