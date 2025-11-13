# Pattern: Process sequence with TQC and changing qualities 
## Purpose
Detailed examples of process sequence with temporally qualified continuants as well as changing qualities over time.

### Creation of a bronze alloy

The scenario describes a sequence of processes involved in the formation of a bronze alloy. The process begins with two pieces of raw materials: copper and tin. At first, each material exists in its solid state, represented by different amounts of copper and tin at various points in time. These materials change their properties as they move through the different stages of the process.

The first stage is melting, which takes place separately for copper and tin. Copper is melted in one furnace, and tin in another. Each furnace performs its specific melting function, heating the metals until they become liquid. Once the tin and copper have been molten, they are ready to be combined.

The next stage is mixing the molten metals. The molten copper and tin are poured together into a mold, where they mix thoroughly to form liquid bronze. This mixing process serves as a bridge between melting and the next phase of production.

After the metals have been mixed, solidification occurs. The molten bronze cools and hardens inside the mold, producing the final solid bronze alloy. The mold itself plays a key role in this step, enabling the cooling and shaping of the metal as it transitions from liquid to solid form.

Overall, these steps — melting, mixing, and solidifying — come together to form a continuous and coordinated process. The production begins with raw materials, transforms them through heat and combination, and ends with a new material: bronze.

Throughout this sequence, the scenario captures not only what happens to the materials but also how the different tools and stages are connected over time.

## Description

In summary, the pattern models a coherent sequence of metallurgical activities:

- Melting copper and tin separately,
- Mixing the molten metals to form a bronze melt, and
- Solidifying the mixture to produce the final bronze alloy.

The pattern describes a sequence of processes involved in the formation of a bronze alloy. The process begins with two materials: copper and tin. Initially, certain amounts of tin (some_tin) and copper (some_cu) exist before the melting process starts. These materials are associated with their respective temporal states (e.g., :some_cu_at_t1, :some_tin_at_t1), which are modeled as instances of [temporally qualified continuant](https://w3id.org/pmd/co/PMD_0000068) and as bearers of particular qualities (such as [aggregate state](https://w3id.org/pmd/co/PMD_0000512)), reflecting how the materials change over time.

The melting phase involves separate activities for copper and tin. The melting_copper process, classified as an instance of [melting process](https://w3id.org/pmd/co/PMD_0000053) and has furnace_1 as participant. Similarly, melting_tin is another instance of the same process type; it operates with furnace_2 on some_tin_at_t1 and subsequently produces some_tin_at_t3. Both furnace_1 and furnace_2 are represented as instances of [furnace](https://w3id.org/pmd/co/PMD_0000655), and both melting processes realize the furnaces’ [melting function](https://w3id.org/pmd/co/PMD_0000057)s.

After both metals have been melted, the next stage is the mixing of the molten metals. This is represented by the mixing_melts process, an instance of [material combination](https://w3id.org/pmd/co/PMD_0000778). During this phase, some_cu_at_t2 and some_tin_at_t3 are combined to form bronze_at_t4. The mixing occurs within a [mold device](https://w3id.org/pmd/co/PMD_0000075), and the mixing_melts process directly contributes to the larger bronze_alloy_formation process, as indicated by several relationships ([has part](http://purl.obolibrary.org/obo/BFO_0000051), [starts with](http://purl.obolibrary.org/obo/RO_0002224), [ends with](http://purl.obolibrary.org/obo/RO_0002230), etc.).

Once the molten bronze has been formed, solidification takes place. This process acts on bronze_at_t4, producing bronze_at_t5 as the solidified output. The solidification step is part of the same overall alloy formation sequence and follows the mixing phase in temporal order ([precedes](http://purl.obolibrary.org/obo/BFO_0000063)). Bronze_at_t5 is explicitly described as occurring after solidification, further clarifying the sequence of events. This process also realizes the mold’s [cooling function](https://w3id.org/pmd/co/PMD_0000055) (f3).

The overarching process, bronze_alloy_formation, integrates all of these sub-processes — melting_copper, melting_tin, mixing_melts, and solidification — each linked through specific dependencies represented by the special relations. The alloy formation process uses the anchor instances :some_cu and :some_tin as input materials and produces :some_bronze as its final output.

 
## Example data
Example data:
[shape-data.ttl](shape-data.ttl)

