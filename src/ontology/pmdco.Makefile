## Customize Makefile settings for pmdco
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile


#$(IMPORTSEED): $(PRESEED) | $(TMPDIR)
#	echo "" > $@


$(ONTOLOGYTERMS): $(SRCMERGED)
	$(ROBOT) query -f csv -i $< --query pmdco_terms.sparql $@



$(IMPORTDIR)/stato_import.owl: $(MIRRORDIR)/stato.owl $(IMPORTDIR)/stato_terms.txt \
			    | all_robot_plugins
	$(ROBOT) annotate --input $< --remove-annotations \
		 odk:normalize --add-source true \
		 extract --term-file $(IMPORTDIR)/stato_terms.txt\
		         --force true --copy-ontology-annotations true \
		         --individuals include \
		         --method SUBSET \
		 remove $(foreach p, $(ANNOTATION_PROPERTIES), --term $(p)) \
		        --term-file $(IMPORTDIR)/stato_terms.txt $(T_IMPORTSEED) \
		        --select complement --select annotation-properties \
		 odk:normalize --base-iri https://w3id.org/pmd \
		               --subset-decls true --synonym-decls true \
		 repair --merge-axiom-annotations true \
		 $(ANNOTATE_CONVERT_FILE)


$(IMPORTDIR)/obi_import.owl: $(MIRRORDIR)/obi.owl $(IMPORTDIR)/obi_terms.txt \
			   $(IMPORTSEED) | all_robot_plugins
	$(ROBOT) annotate --input $< --remove-annotations \
		 odk:normalize --add-source true \
		 extract --term-file $(IMPORTDIR)/obi_terms.txt $(T_IMPORTSEED) \
		         --force true --copy-ontology-annotations true \
		         --individuals exclude \
		         --method SUBSET \
		 remove --term IAO:0000416 \
		 remove --term CHEBI:33375 \
		 remove --term CHEBI:33359 \
		 remove --term CHEBI:30682 \
		 remove --term CHEBI:33376 \
		 remove --term-file $(IMPORTDIR)/unwanted.txt  \
		 remove $(foreach p, $(ANNOTATION_PROPERTIES), --term $(p)) \
		        --term-file $(IMPORTDIR)/obi_terms.txt $(T_IMPORTSEED) \
		        --select complement --select annotation-properties \
		 odk:normalize --base-iri https://w3id.org/pmd \
		               --subset-decls true --synonym-decls true \
		 repair --merge-axiom-annotations true \
		 $(ANNOTATE_CONVERT_FILE)


$(IMPORTDIR)/cob_import.owl: $(MIRRORDIR)/cob.owl $(IMPORTDIR)/cob_terms.txt | all_robot_plugins
	$(ROBOT) annotate --input $< --remove-annotations \
		 odk:normalize --add-source true \
		 extract --term-file $(IMPORTDIR)/cob_terms.txt $(T_IMPORTSEED) \
		         --force true --copy-ontology-annotations true \
		         --individuals exclude \
		         --method SUBSET \
		 remove $(foreach p, $(ANNOTATION_PROPERTIES), --term $(p)) \
		        --term-file $(IMPORTDIR)/cob_terms.txt $(T_IMPORTSEED) \
		        --select complement --select annotation-properties \
		 odk:normalize --base-iri https://w3id.org/pmd \
		               --subset-decls true --synonym-decls true \
		 repair --merge-axiom-annotations true \
		 $(ANNOTATE_CONVERT_FILE)

## Default module type (slme)
$(IMPORTDIR)/ro_import.owl: $(MIRRORDIR)/ro.owl $(IMPORTDIR)/ro_terms.txt \
			   $(IMPORTSEED) | all_robot_plugins
	$(ROBOT) annotate --input $< --remove-annotations \
	     remove --select "RO:*" --select complement --select "classes"  --axioms annotation \
		 odk:normalize --add-source true \
		 extract --term-file $(IMPORTDIR)/ro_terms.txt  \
		         --force true --copy-ontology-annotations true \
		         --individuals exclude \
		         --method SUBSET \
		 remove $(foreach p, $(ANNOTATION_PROPERTIES), --term $(p)) \
		        --term-file $(IMPORTDIR)/ro_terms.txt \
		        --select complement --select annotation-properties \
		 remove --term-file $(IMPORTDIR)/unwanted.txt  \
		 odk:normalize --base-iri https://w3id.org/pmd \
		               --subset-decls true --synonym-decls true \
		 $(ANNOTATE_CONVERT_FILE)


$(IMPORTDIR)/iao_import.owl: $(MIRRORDIR)/iao.owl $(IMPORTDIR)/iao_terms.txt
	if [ $(IMP) = true ]; then $(ROBOT) query -i $< --update ../sparql/preprocess-module.ru \
		remove --select "IAO:*" --select complement --select "classes object-properties data-properties"  --axioms annotation \
		extract --term-file $(IMPORTDIR)/iao_terms.txt  --force true --copy-ontology-annotations true --individuals exclude --intermediates none --method BOT \
		query --update ../sparql/inject-subset-declaration.ru --update ../sparql/inject-synonymtype-declaration.ru --update ../sparql/postprocess-module.ru \
 		remove --term IAO:0000032 --axioms subclass \
 		rename --mapping OBI:0000011 COB:0000035 	\
 		remove --term-file $(IMPORTDIR)/unwanted.txt  \
 		remove $(foreach p, $(ANNOTATION_PROPERTIES), --term $(p)) \
			  --term-file $(IMPORTDIR)/iao_terms.txt \
		      --select complement --select annotation-properties \
		$(ANNOTATE_CONVERT_FILE); fi


$(IMPORTDIR)/bfo_import.owl: $(MIRRORDIR)/bfo.owl $(IMPORTDIR)/bfo_terms.txt
	if [ $(IMP) = true ]; then $(ROBOT) query -i $< --update ../sparql/preprocess-module.ru \
		extract -T $(IMPORTDIR)/bfo_terms.txt --force true --copy-ontology-annotations true --method SUBSET \
		query --update ../sparql/inject-subset-declaration.ru --update ../sparql/inject-synonymtype-declaration.ru --update ../sparql/postprocess-module.ru \
 		remove $(foreach p, $(ANNOTATION_PROPERTIES), --term $(p)) \
			  --term-file $(IMPORTDIR)/bfo_terms.txt \
		      --select complement --select annotation-properties \
		$(ANNOTATE_CONVERT_FILE); fi		


$(IMPORTDIR)/chebi_import.owl: #$(MIRRORDIR)/chebi.owl
	if [ $(IMP) = true ]; then $(ROBOT) query -i $< --update ../sparql/preprocess-module.ru \
		filter --term-file $(IMPORTDIR)/chebi_terms.txt --select "self annotations" reduce --reasoner ELK \
		query --update ../sparql/inject-subset-declaration.ru --update ../sparql/inject-synonymtype-declaration.ru --update ../sparql/postprocess-module.ru \
 		remove $(foreach p, $(ANNOTATION_PROPERTIES), --term $(p)) \
			  --term-file $(IMPORTDIR)/chebi_terms.txt \
		      --select complement --select annotation-properties \
		$(ANNOTATE_CONVERT_FILE); fi


$(IMPORTDIR)/uo_import.owl: $(MIRRORDIR)/uo.owl $(IMPORTDIR)/uo_terms.txt 
	$(ROBOT) filter --input mirror/uo.owl --term-file imports/uo_terms.txt --allow-punning true --select "annotations self parents" \
		 $(ANNOTATE_CONVERT_FILE)


$(TEMPLATEDIR)/materials-listing.tsv:
	curl -L "https://docs.google.com/spreadsheets/d/e/2PACX-1vQmflWvRYJEO0K_k9EtLHDTkyIcntG0jW-i9ZNlURUxQET8N9eadI2HdI94hrNMWBcDQAKzE9KWVY6b/pub?gid=0&single=true&output=tsv" -o $@

.PHONY: autoshapes
autoshapes: 
	echo "please run manually: sh utils/generate-auto-shapes.sh"


## we import the BFO entirely
#$(IMPORTDIR)/bfo_import.owl: $(MIRRORDIR)/bfo.owl
# if [ $(IMP) = true ]; then cp $(MIRRORDIR)/bfo.owl $(IMPORTDIR)/bfo_import.owl; fi


$(ONT)-base.owl: $(EDIT_PREPROCESSED) $(OTHER_SRC) $(IMPORT_FILES)
	$(ROBOT_RELEASE_IMPORT_MODE) \
	reason --reasoner ELK --equivalent-classes-allowed asserted-only --exclude-tautologies structural --annotate-inferred-axioms False \
	relax \
	reduce -r ELK \
	remove --base-iri $(URIBASE)/ --axioms external --preserve-structure false --trim false \
	$(SHARED_ROBOT_COMMANDS) \
	annotate --link-annotation http://purl.org/dc/elements/1.1/type http://purl.obolibrary.org/obo/IAO_8000001 \
		--ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
		--output $@.tmp.owl && mv $@.tmp.owl $@


$(ONT)-minimal.owl: 
	$(ROBOT)  query --input $(ONT).owl --query ../sparql/select-minimal-profile.sparql $(TMPDIR)/minimal_profile.txt && \
	$(ROBOT)  extract --input $(ONT).owl --term-file $(TMPDIR)/minimal_profile.txt --method BOT --intermediates minimal --output $@


CITATION="'PMDco: Platform Material Digital Ontology. Version $(VERSION), https://w3id.org/pmd/co/'"


#ALL_ANNOTATIONS=--annotate-defined-by true \

ALL_ANNOTATIONS=--ontology-iri https://w3id.org/pmd/co/ -V https://w3id.org/pmd/co/$(VERSION) \
	--annotation http://purl.org/dc/terms/created "$(TODAY)" \
	--annotation owl:versionInfo "$(VERSION)" \
	--annotation http://purl.org/dc/terms/bibliographicCitation "$(CITATION)"  \
	--link-annotation owl:priorVersion https://w3id.org/pmd/co/$(PRIOR_VERSION) \

update-ontology-annotations: 
	$(ROBOT) annotate --input ../../pmdco.owl $(ALL_ANNOTATIONS) --output ../../pmdco.owl && \
	$(ROBOT) annotate --input ../../pmdco.ttl $(ALL_ANNOTATIONS) --output ../../pmdco.ttl && \
	$(ROBOT) annotate --input ../../pmdco-simple.owl $(ALL_ANNOTATIONS) --output ../../pmdco-simple.owl && \
	$(ROBOT) annotate --input ../../pmdco-simple.ttl $(ALL_ANNOTATIONS) --output ../../pmdco-simple.ttl && \
	$(ROBOT) annotate --input ../../pmdco-full.owl $(ALL_ANNOTATIONS) --output ../../pmdco-full.owl && \
	$(ROBOT) annotate --input ../../pmdco-full.ttl $(ALL_ANNOTATIONS) --output ../../pmdco-full.ttl && \
	$(ROBOT) annotate --input ../../pmdco-base.owl $(ALL_ANNOTATIONS) --output ../../pmdco-base.owl && \
	$(ROBOT) annotate --input ../../pmdco-base.ttl $(ALL_ANNOTATIONS) --output ../../pmdco-base.ttl && \
	$(ROBOT) annotate --input ../../pmdco-minimal.owl $(ALL_ANNOTATIONS) --output ../../pmdco-minimal.owl && \
	$(ROBOT) annotate --input ../../pmdco-minimal.ttl $(ALL_ANNOTATIONS) --output ../../pmdco-minimal.ttl 





