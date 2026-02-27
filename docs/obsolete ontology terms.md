# Obsoleting and deprecating ontology terms
<!--@Document_indicator: Text,links -->

Ontologies evolve, terms are revised, split into more detailed terms or deprecated. For proper reusablity of the ontology and traceability of the reason why it was deleted and what is a possible replacement term that should be used instead, the following obsoletion procedure should be followed.
*(These steps are largely based on the [GO](https://wiki.geneontology.org/index.php/Obsoleting_an_Existing_Ontology_Term) and [ODK](https://ontology-development-kit.readthedocs.io/en/latest/ObsoleteTerm.html) pages for term obsoletion but adopted for the PMDco.)*

## Check for the PMDco deprecation profile
1. Navigate to your local Protégé installation folder and further to '..\conf\deprecation\'
2. Check whether the file `PMDco.yaml` is present
	- if not, download it from [here](https://raw.githubusercontent.com/materialdigital/core-ontology/refs/heads/main/src/ontology/PMDco.yaml) and move it into the Protégé installation folder

<!--- In the future this should be done without the need for users to manually copy files on their machines. The PMDco deprecation profile may be added to the official protege release or be moved into the respective folder when editing the core or application ontologies. For now this shoould suffice.--->
	

## Check the usage of the term
1. Check where in the ontology the term is used
	- In Protégé, navigate to the term you want to obsolete, go to the `Usage` tab to see if that ID is used elsewhere.
	- If the term is a parent term or used in logical definitions, **create a substitute term** that replaces the obsolete term.
	- Is the obsolete term itself is the replacement or in consideration for other obsoleted terms, update these (with a substitute term) or delete them.
2. Navigate to the term you want to obsolete again
3. Right-click on the term and select `Deprecate...` **or** click the `Edit`-tab → `Deprecrate entity...`
4. Choose the PMDco deprecation profile from the dropdown menu → continue
	- If no PMDco deprecation profile is present, the `PMDco.yaml` is missing from your Protégé installation folder. Checkout the previous section, then return here.
6. Give a reason for deprecation from the list below → continue 
7. (If applicable) Search the substitute term you created earlier, else continue
8. If no substitute term was defined, give one or more terms that can be used as an alternative when possible (if applicable) → continue → finish

## Reasons for deprecation
Copy&paste these into the corresponding dialog during the obsoletion procedure.

- original meaning has split and more specific terms were created
- outside of the scope of the ontology
- an equivalent term was adopted from a different ontology
- term was moved to a different ontology
- unnecessary grouping term
- vague meaning or unclear definition
- overly specific term
- such an entity does not exist
- added in error
- not used

## Reasons when no deprecation procedure is needed
- terms created for testing purposes, confined to local machine (not pushed to github)
- terms created in the development version (and pushed to github), that only saw limited use by the creators of the term, so that consensus between the contributors over deprecation can be easily reached/assumed

> ❗Attention❗
> 
> Once a term is part of a release, the proper deprecation procedure **must** be followed.
