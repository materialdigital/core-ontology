- **Purpose**: Specifying the boundaries of a process on the time axis. 
- **Description**: This graph describes a set of temporal relationships among processes, temporal regions, and continuant entities. The graph models how different kinds of entities relate to time and duration through their association with temporal regions and instants.
Within this model, there are two processes — (ex:process_1) and (ex:process_2) — each representing an occurrence or event that unfolds over time. Both processes are linked to distinct one-dimensional temporal regions (ex:period_1, ex:period_2), via the occupies_temporal_region property. This expresses that each process extends through a particular temporal duration.
The temporal structure is further refined through hierarchical and boundary definitions. The region (ex:period_1) is described as a proper_temporal_part_of (ex:period_2), indicating that the first period is entirely contained within the second, but not identical to it. The larger region (ex:period_2) has defined temporal boundaries: it has_first_instant (ex:start) and has_last_instant (ex:end), both of which are represented as zero-dimensional temporal regions, signifying discrete points in time marking the beginning and end of that duration.
In addition to the processes and periods, the model includes a continuant entity, (ex:object_1), which exists_at a particular temporal region, (ex:some_time). This denotes that the continuant maintains existence at or during a specific time interval, emphasizing persistence or presence within the temporal framework. 

```d2
direction: up

classes: {
  bfoclazz: {
    style: {
      fill: "#dd42f5"
      shadow: true
      border-radius: 5
      font-color: white
    }
  }
  individual: {
    style: {
      fill: "lightgrey"
    }
  }
}
tbox.bfo*.class: bfoclazz
tbox.label: ""
tbox: {
  "bfo:occurrent" -> "bfo:entity": "rdfs:subClassOf"
  "bfo:continuant" -> "bfo:entity": "rdfs:subClassOf"
  "bfo:process" -> "bfo:occurrent": "rdfs:subClassOf"
  "bfo:temporal region" -> "bfo:occurrent": "rdfs:subClassOf"
  "bfo:one dimensional t.r." -> "bfo:temporal region": "rdfs:subClassOf"
  "bfo:zero dimensional t.r." -> "bfo:temporal region": "rdfs:subClassOf"
}

tbox.style.stroke: transparent
tbox.style.fill: transparent

abox.ex*.class: individual
abox.label: "___________________________________________________________________________"
abox: {
  "ex:process 1" -> "ex:period 1": "bfo:occupies_temporal_region"
  "ex:process 2" -> "ex:period 2": "bfo:occupies_remporal_region"
  "ex:period 2" -> "ex:start": "bfo:has_first_instant"
  "ex:period 2" -> "ex:end": "bfo:has_last_instant"
  "ex:period 1" -> "ex:period 2": "bfo:proper_temporal_part_of"
  "ex:object 1" -> "ex:some time": "bfo:existsAt"
}
abox.style.stroke: transparent
abox.style.fill: transparent

abox."ex:process 1" -> tbox."bfo:process": "rdf:type"
abox."ex:process 2" -> tbox."bfo:process": "rdf:type"
abox."ex:period 1" -> tbox."bfo:one dimensional t.r.": "rdf:type"
abox."ex:period 2" -> tbox."bfo:one dimensional t.r.": "rdf:type"
abox."ex:some time" -> tbox."bfo:temporal region": "rdf:type"
abox."ex:object 1" -> tbox."bfo:continuant": "rdf:type"
abox."ex:start" -> tbox."bfo:zero dimensional t.r.": "rdf:type"
abox."ex:end" -> tbox."bfo:zero dimensional t.r.": "rdf:type"

```
