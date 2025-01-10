# Examples and Use Cases

TODO (Ideas):
> - **Scenarios**: Demonstrate how the ontology can be applied in real-world scenarios.
> - **Sample Data**: Include sample datasets and their representation in the ontology.
> - **Applications**: Highlight applications where the ontology has been or can be used.

## Scenario: Tensile Testing

Tensile testing is a fundamental and widely used technique in materials science and engineering (MSE) to evaluate the mechanical properties of metallic materials. It involves subjecting a specimen to uniaxial tension until failure which provides data on mechanical properties such as strength, ductility, and elasticity. This scenario refers to how the tensile test ontology (TTO) can be applied to transform classic tensile test data - originally stored in varied formats - into semantically enriched RDF data to ensure data interoperability, transparency, and reproducibility. The TTO was designed on the basis of the PMDco and can be found in a [repository dedicated to TTO version 3.0](https://github.com/materialdigital/tensile-test-ontology).

### Scenario Description: Tensile Testing of Metallic Materials
In this scenario, a series of tensile tests is performed on metallic materials to determine their mechanical properties such as tensile strength, yield strength, and elongation. The tests are conducted in accordance with the ISO 6892-1 test standard, which specifies the method for tensile testing at room temperature.

### Steps Involved
1. **Preparation of Test Specimens**: Metallic specimens are prepared according to the test standard specifications.
2. **Conducting the Tensile Test**: The specimens are subjected to axial tensile loads until failure, and the resulting deformation is measured.
3. **Data Collection**: Raw data (primary data), including time, force, and elongation, are collected during the test.
4. **Data Transformation**: The ***primary data*** are used to obtain characteristic values of the specimen material. Furthermore, ***metadata*** (test machine specifications, environmental conditions) are regarded. Data are transformed into RDF format using the TTO, ensuring that they are semantically enriched and machine-actionable.
5. **Additional Data Analysis**: The RDF data may be queried and further analyzed to extract key mechanical properties. Thereby, advanced querying and interoperability across datasets is enabled.

### Sample Data

The tensile testing scenario utilized sample data available in an [open access Zenodo repository](https://doi.org/10.5281/zenodo.6778335). 
This dataset includes:
- **Raw test data**: Force-displacement curves and stress-strain data.
- **Metadata**: Machine configurations, sample dimensions, and test conditions.
- **Derived data**: Mechanical properties like yield strength, ultimate tensile strength, and elongation at fracture.

Example RDF snippet representing some aspects of tensile test data (in TTL format):
```turtle
@prefix tto: <https://w3id.org/pmd/tto/>.
@prefix pmdco: <https://w3id.org/pmd/co/>.
@prefix obo: <http://purl.obolibrary.org/obo/>.

:pmdao-tto-tt-S355-6_maximumForce_Fm a tto:MaximumForce ;
    obo:IAO_0000417 tto:pmdao-tto-tt-S355-6_maximumForce_Fm_scalar_measurement_datum .

:pmdao-tto-tt-S355-6_maximumForce_Fm_scalar_measurement_datum a obo:IAO_0000032 ;
    obo:IAO_0000136 <https://w3id.org/pmd/demodata/tensiletest_S355/testpiece/Zy2> ;
    obo:OBI_0001938 
    tto:pmdao-tto-tt-S355-6_maximumForce_Fm_value_specification .

:tto-tt-S355-6_process a obo:OBI_0000011,
        tto:TensileTest ;
    obo:BFO_0000055 prefix:pmdao-tto-tt-S355-6_process_plan ;
    obo:OBI_0000293 <https://w3id.org/pmd/demodata/tensiletest_S355/testpiece/Zy2> ;
    obo:OBI_0000299        tto:pmdao-tto-tt-S355-6_maximumForce_Fm_scalar_measurement_datum .
```

### Applications

#### Current Applications
- **Data Integration**: TTO is already applied to unify disparate tensile test datasets, ensuring standardized descriptions and facilitating cross-institutional collaborations. A demonstration of the combination of different test data stemming from various sources (test methods) is provided by the [PMD Orowan Demonstrator](https://github.com/materialdigital/demo-orowan).
- **Advanced Querying**: Researchers use the ontology to perform detailed queries about tensile properties across large datasets.
- **Educational Tools**: TTO serves as a teaching tool for demonstrating the benefits of semantic data representation in MSE.

#### Possible Future Applications
- **Materials Informatics**: By coupling TTO with machine learning algorithms, predictive models for material performance could be developed.
- **Digital Twins**: The ontology can be a foundation for creating digital representations of testing setups for simulation purposes.

### Contributions of PMDco
The PMD Core Ontology (PMDco) underpins the TTO by:

1. **Providing a Semantic Framework**: The robust mid-level semantic structure of PMDco bridges domain-specific concepts with universal ontological standards.
2. **Facilitating Interoperability**: By reusing and extending PMDco concepts, TTO ensures compatibility with other MSE ontologies.
3. **Anchoring Ontological Classes**: Core concepts such as pmd:TestingMachine and pmd:Process serve as templates, reducing duplication and aligning TTO with broader MSE semantic ecosystems.

By leveraging [PMDco](https://w3id.org/pmd/co), [TTO](https://w3id.org/pmd/tto) effectively encapsulates tensile testing knowledge while maintaining interoperability with broader MSE frameworks which enhances data integration and long-term usability.