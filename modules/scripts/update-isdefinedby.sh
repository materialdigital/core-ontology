#####################################################
# Add missing isDefinedBy annotation to each module #
#####################################################

# to be executed within this directory (with robot.jar present)


# for each module:
# 	extract all PMD resource IRIs which are not annotated with isDefinedBy 
# 	for each IRI: add isDefinedBy triple at end of module file

java -jar robot.jar remove --select imports --input ../pmdco-characterization.ttl verify  --queries ../../.github/workflow_resources/qc-queries/isdefinedby-missing.sparql  
cat isdefinedby-missing.csv | tr -d '\r' |awk 'NR>1 {print "<" $1 "> rdfs:isDefinedBy <https://w3id.org/pmd/co/characterization> ."}'  >> ../pmdco-characterization.ttl

java -jar robot.jar remove --select imports --input ../pmdco-datatransformation.ttl verify --queries ../../.github/workflow_resources/qc-queries/isdefinedby-missing.sparql  
cat isdefinedby-missing.csv | tr -d '\r' |awk 'NR>1 {print "<" $1 "> rdfs:isDefinedBy <https://w3id.org/pmd/co/datatransformation> ."}'  >> ../pmdco-datatransformation.ttl

java -jar robot.jar remove --select imports --input ../pmdco-devices.ttl  verify --queries ../../.github/workflow_resources/qc-queries/isdefinedby-missing.sparql  
cat isdefinedby-missing.csv | tr -d '\r' |awk 'NR>1 {print "<" $1 "> rdfs:isDefinedBy <https://w3id.org/pmd/co/devices> ."}'  >> ../pmdco-devices.ttl

java -jar robot.jar remove --select imports --input ../pmdco-logistics.ttl  verify --queries ../../.github/workflow_resources/qc-queries/isdefinedby-missing.sparql  
cat isdefinedby-missing.csv | tr -d '\r' |awk 'NR>1 {print "<" $1 "> rdfs:isDefinedBy <https://w3id.org/pmd/co/logistics> ."}'  >> ../pmdco-logistics.ttl

java -jar robot.jar remove --select imports --input ../pmdco-manufacturing.ttl verify --queries ../../.github/workflow_resources/qc-queries/isdefinedby-missing.sparql  
cat isdefinedby-missing.csv | tr -d '\r' |awk 'NR>1 {print "<" $1 "> rdfs:isDefinedBy <https://w3id.org/pmd/co/manufacturing> ."}'  >> ../pmdco-manufacturing.ttl

java -jar robot.jar remove --select imports  --input ../pmdco-materials.ttl verify --queries ../../.github/workflow_resources/qc-queries/isdefinedby-missing.sparql  
cat isdefinedby-missing.csv | tr -d '\r' |awk 'NR>1 {print "<" $1 "> rdfs:isDefinedBy <https://w3id.org/pmd/co/materials> ."}'  >> ../pmdco-materials.ttl

java -jar robot.jar remove --select imports  --input ../pmdco-qualities.ttl verify --queries ../../.github/workflow_resources/qc-queries/isdefinedby-missing.sparql  
cat isdefinedby-missing.csv | tr -d '\r' |awk 'NR>1 {print "<" $1 "> rdfs:isDefinedBy <https://w3id.org/pmd/co/qualities> ."}'  >> ../pmdco-qualities.ttl
