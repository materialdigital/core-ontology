## Customize Makefile settings for pmdco
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile


$(ONTOLOGYTERMS): $(SRCMERGED)
	$(ROBOT) query -f csv -i $< --query pmdco_terms.sparql $@


# we dont want the "curation status annotation" and not the "data item"
# we dont want RO
$(IMPORTDIR)/obi_import.owl: $(MIRRORDIR)/obi.owl $(IMPORTDIR)/obi_terms.txt
	if [ $(IMP) = true ]; then $(ROBOT) query -i $< --update ../sparql/preprocess-module.ru \
		remove --term "IAO:0000114" --term "IAO:0000027" --select "self descendants" \
		extract -T $(IMPORTDIR)/obi_terms.txt --force true --copy-ontology-annotations false --individuals exclude --method BOT \
		remove --select "RO:*"  \
		$(ANNOTATE_CONVERT_FILE); fi

$(IMPORTDIR)/iao_import.owl: $(MIRRORDIR)/iao.owl $(IMPORTDIR)/iao_terms.txt
	if [ $(IMP) = true ]; then $(ROBOT) query -i $< --update ../sparql/preprocess-module.ru \
		extract -T $(IMPORTDIR)/iao_terms.txt --force true --copy-ontology-annotations true --individuals exclude --method BOT \
		query --update ../sparql/inject-subset-declaration.ru --update ../sparql/inject-synonymtype-declaration.ru --update ../sparql/postprocess-module.ru \
 		remove --term http://www.w3.org/2002/07/owl#Nothing  --term http://purl.obolibrary.org/obo/PATO_0000001\
 		remove --select "RO:*"  \
		$(ANNOTATE_CONVERT_FILE); fi

$(IMPORTDIR)/chebi_import.owl: $(MIRRORDIR)/chebi.owl
	if [ $(IMP) = true ]; then $(ROBOT) query -i $< --update ../sparql/preprocess-module.ru \
		extract --upper-term http://purl.obolibrary.org/obo/CHEBI_24431 --lower-terms $(IMPORTDIR)/chebi_terms.txt --copy-ontology-annotations true --individuals exclude --intermediates none --method MIREOT \
		query --update ../sparql/inject-subset-declaration.ru --update ../sparql/inject-synonymtype-declaration.ru --update ../sparql/postprocess-module.ru \
		$(ANNOTATE_CONVERT_FILE); fi

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




CITATION="'PMDco: Platform Material Digital Ontology. Version $(VERSION), https://w3id.org/pmd/co/'"


ALL_ANNOTATIONS=--annotate-defined-by true \
	--ontology-iri https://w3id.org/pmd/co/ -V https://w3id.org/pmd/co/$(VERSION) \
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
	$(ROBOT) annotate --input ../../pmdco-base.ttl $(ALL_ANNOTATIONS) --output ../../pmdco-base.ttl 




