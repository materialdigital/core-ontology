# Repository structure

The main kinds of files in the repository:

1. Release files
2. Imports
3. [Components](#components)

## Release files
Release file are the file that are considered part of the official ontology release and to be used by the community. A detailed description of the release artefacts can be found [here](https://github.com/INCATools/ontology-development-kit/blob/master/docs/ReleaseArtefacts.md).

## Imports
Imports are subsets of external ontologies that contain terms and axioms you would like to re-use in your ontology. These are considered "external", like dependencies in software development, and are not included in your "base" product, which is the [release artefact](https://github.com/INCATools/ontology-development-kit/blob/master/docs/ReleaseArtefacts.md) which contains only those axioms that you personally maintain.

These are the current imports in PMDCO

| Import | URL | Type |
| ------ | --- | ---- |
| bfo | https://raw.githubusercontent.com/BFO-ontology/BFO-2020/release-2024-01-29/src/owl/bfo-core.ttl | mirror |
| iao | http://purl.obolibrary.org/obo/iao.owl | custom |
| obi | http://purl.obolibrary.org/obo/obi.owl | custom |
| chebi | https://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi_lite.obo | custom |
## Components
Components, in contrast to imports, are considered full members of the ontology. This means that any axiom in a component is also included in the ontology base - which means it is considered _native_ to the ontology. While this sounds complicated, consider this: conceptually, no component should be part of more than one ontology. If that seems to be the case, we are most likely talking about an import. Components are often not needed for ontologies, but there are some use cases:

1. There is an automated process that generates and re-generates a part of the ontology
2. A part of the ontology is managed in ROBOT templates
3. The expressivity of the component is higher than the format of the edit file. For example, people still choose to manage their ontology in OBO format (they should not) missing out on a lot of owl features. They may choose to manage logic that is beyond OBO in a specific OWL component.

These are the components in PMDCO

| Filename | URL |
| -------- | --- |
| imports-edit.owl | None |
| pmdco-shared.owl | None |
| pmdco-axioms-shared.owl | None |
| pmdco-qualities.owl | None |
| pmdco-materials.owl | None |
| pmdco-manufacturing.owl | None |
| pmdco-logistics.owl | None |
| pmdco-devices.owl | None |
| pmdco-datatransformation.owl | None |
| pmdco-characterization.owl | None |
