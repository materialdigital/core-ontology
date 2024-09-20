#####################################################
# Add missing isDefinedBy annotation to each module #
#####################################################

# to be executed within this directory (with robot.jar present)


# for each module:
# 	extract all PMD resource IRIs which are not annotated with isDefinedBy 
# 	for each IRI: add isDefinedBy triple at end of module file

java -jar robot.jar verify --input ../pmdco-characterization.ttl --queries ../../.github/workflow_resources/qc-queries/isdefinedby-missing.sparql  
cat isdefinedby-missing.csv | tr -d '\r' |awk 'NR>1 {print "<" $1 "> rdfs:isDefinedBy <https://w3id.org/pmd/co/characterization> ."}'  >> ../pmdco-characterization.ttl

java -jar robot.jar verify --input ../pmdco-datatransformation.ttl --queries ../../.github/workflow_resources/qc-queries/isdefinedby-missing.sparql  
cat isdefinedby-missing.csv | tr -d '\r' |awk 'NR>1 {print "<" $1 "> rdfs:isDefinedBy <https://w3id.org/pmd/co/datatransformation> ."}'  >> ../pmdco-datatransformation.ttl

java -jar robot.jar verify --input ../pmdco-devices.ttl --queries ../../.github/workflow_resources/qc-queries/isdefinedby-missing.sparql  
cat isdefinedby-missing.csv | tr -d '\r' |awk 'NR>1 {print "<" $1 "> rdfs:isDefinedBy <https://w3id.org/pmd/co/devices> ."}'  >> ../pmdco-devices.ttl

java -jar robot.jar verify --input ../pmdco-logistics.ttl --queries ../../.github/workflow_resources/qc-queries/isdefinedby-missing.sparql  
cat isdefinedby-missing.csv | tr -d '\r' |awk 'NR>1 {print "<" $1 "> rdfs:isDefinedBy <https://w3id.org/pmd/co/logistics> ."}'  >> ../pmdco-logistics.ttl

java -jar robot.jar verify --input ../pmdco-manufacturing.ttl --queries ../../.github/workflow_resources/qc-queries/isdefinedby-missing.sparql  
cat isdefinedby-missing.csv | tr -d '\r' |awk 'NR>1 {print "<" $1 "> rdfs:isDefinedBy <https://w3id.org/pmd/co/manufacturing> ."}'  >> ../pmdco-manufacturing.ttl

java -jar robot.jar verify --input ../pmdco-materials.ttl --queries ../../.github/workflow_resources/qc-queries/isdefinedby-missing.sparql  
cat isdefinedby-missing.csv | tr -d '\r' |awk 'NR>1 {print "<" $1 "> rdfs:isDefinedBy <https://w3id.org/pmd/co/materials> ."}'  >> ../pmdco-materials.ttl

java -jar robot.jar verify --input ../pmdco-qualities.ttl --queries ../../.github/workflow_resources/qc-queries/isdefinedby-missing.sparql  
cat isdefinedby-missing.csv | tr -d '\r' |awk 'NR>1 {print "<" $1 "> rdfs:isDefinedBy <https://w3id.org/pmd/co/qualities> ."}'  >> ../pmdco-qualities.ttl
