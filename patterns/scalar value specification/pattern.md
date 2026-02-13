- **Purpose**: Represents scalar physical quantities, combining a numerical value and a unit.
- **Core Properties**: 
  - `obi:hasSpecifiedNumericValue`
  - `iao:hasMeasurementUnitLabel`
  - `iao:MeasurementUnitLabel`

- **Example Use Case**: The example describes a scalar value specification, ex:scalar_value_specification_X, which is assigned a numeric value of 135.0 and linked to a measurement unit represented by the individual ex:unit_X. The numeric value is provided via the OBI property has_specified_numeric_value, while the unit is associated through the IAO property has_measurement_unit_label. The unit individual ex:unit_X is typed as a measurement unit label, but in practice this placeholder unit could be replaced by a formally defined unit from established ontologies such as UO (Units of Measurement Ontology) or QUDT (Quantities, Units, Dimensions, and Types). Together, the triples express that a value of 135.0 is specified in some unit, whether a custom one like ex:unit_X or a standard unit drawn from UO or QUDT.
