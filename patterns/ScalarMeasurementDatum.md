# Pattern 1: measurement datum composed of two parts, a numeral and a unit
## Purpose
Description on how to represent measurements made.

## Description
Scalar Measurement Datum is typically used to represent measurements made. Any object can have a measurement made about its quality.
Measurement is specified using scalar value specification which has a numeral and an associated unit.
To specify the object, it is recommended to use the property: 

```
is_about (IAO:0000136)
```
To specify the quality which is being measured, it is recommended to use the property:

```
is_quality_measured_as (IAO:0000417)
```
To specify the numerical value and associated unit, it is recommended to use the property:

```
has_value_specification (OBI:0001938)
```

Measurement can also have temporal aspects specified using the property:

```
has_part (BAO:0090004)
```

Measurement also can optionally have the confidence interval specified using the property:

```
has_time (time:hasTime)
```


## Visualization
The following image shows some manufacturing process with multiple inputs and outputs.

<img src="https://github.com/materialdigital/core-ontology/blob/develop-3.0.0/patterns/ScalarMeasurementDatum-Example.png?raw=true" alt="ScalarMeasurementDatum image" width="750"/>

## Shapes and example data
[../shapes/ScalarMeasurementDatum-data.ttl](../shapes/ScalarMeasurementDatum-data.ttl)

[../shapes/ScalarMeasurementDatum.ttl](../shapes/ScalarMeasurementDatum.ttl)

## Interactive Playground
Auto-generated webeditor to create valid instances: [OO-LD Playground](https://oo-ld.github.io/playground-yaml/?data=N4Ig9gDgLglmB2BnEAuUMDGCA2MBGqIAZglAIYDuApomALZUCsIANOHgFZUZQD62ZAJ5gArlELwwAJzplsrEIgwALKrNSgAAlnhQqAD3FpwFeShDKoUCCgD0tio4B0FAMxPpAc1sAmAAx%2BPrZ%2BAOy2YKYAxApSACZEhJbWdg7Obh5S3gCMAJx5wUE%2BPgC0cUTFiIK6ZPrFSNFs%2BnRmFlY29o4ULu5etgAaALIAMra5OQActvBkDIgQZBhUCvqIsYltKZ3dGd7%2Bfln9wwDKKmpkDSBlyOZJ7ald6b17fsEHZRWnshdgeDAaIJoYGsbht7BARFJsB48GBcHgpGQpIIduEYbYAPIAIQAkrwFJoIFIqEQYPpUFApCIqABfNgQOixLDrayITauIEo%2BmxWxYWz4vBkRBLEEstkc3pcnlgWx6RBQPlsKCCCDCgFKlUKIGEQFrNgweDgoxaLXmH4wFABAI%2BHKufHq1U6kC08BiQ3%2FR2m34Wy3WnJ25UOrXU50AEiwdAYukIJ1UsgABCQpHGyHGuVgUAMyPAREQFlAIfrPAAFKRgRaIZCKmBQbCqktlmiVkD2wg%2FLg8GJUACOIhgROBAG1mwHNbqQPq3WxRNYxCAALp00sqqSwGj%2FFvGWA11UAFRHbFiNAwUhg0Dg8EIe5VcbjYCIcagyhgiDj%2BrlWcWCg3igphc7ZFidF4GwQRyUpKgD2JMgRGwIwQDTMAMyzHM8wLeBi1LctkGdE1QC3WtCGxAARL8R3MOUT3QhRD1zGC4MJBsKyyJ09QNWdN2rAjzGxNjxEVMiQERBFQLYRNZDgoVax4HxNT0OhrjwgSKL%2FNgw3oSM4J4uMiTkOMKGkbBYmTCAIFwDAyFgBAX0fMAhVvThuCgPTREMuM8CoOM6DAQ9sFrIzBTjRARBhByeFvJMiCoKBTiMohSzoB9VDjABrSRTCoWJPA8zwEQgZQFCobM6FQIc20c5ip1CqAZMq9soFtOdnTofVsTk64sjYER4BgHsqFatRrgpKlINo2CSvYOqKomxyZMaqdXXYxSNXMIShAUMSLMISSZtkgb1041V0QWpyACUaFEKRy1I5af0ozwCqK8ayp4LI%2FAUZ6oCyKaPqyWampatrUA6kAup6ql%2BvksDhpAGjoLGlBSqq1752DZ1EGUCJeCoKRSyka5x10bG83PL9Y1VGEwCgCiyAgAAWBQyA4GooYgkBkqoKgIF4BAqDvXgADc5Cpa5c2wIVnQ4WgL03ASEKQ7Ncx4NCMMYpsTXgzDGymid2MRyb3qq2b5pnIw9fKt7GupIA%3D%3D%3D) (see also [OO-LD Schema](https://github.com/OO-LD/schema))
