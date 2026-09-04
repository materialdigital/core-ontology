# retrieve recent konclude binary from here und unzip it:
# https://github.com/konclude/Konclude/releases

# specify your local path to the binary, e.g.:
KONCLUDE_BIN=../../../../../../konclude/Konclude-v0.7.0-1138-OSX-x64-Clang-Static-Qt5.12.10/Binaries/Konclude

# retrieve recent koncludix script
if [ ! -f koncludix.py ]
then
	wget https://raw.githubusercontent.com/ISE-FIZKarlsruhe/Koncludix/refs/heads/main/koncludix.py
fi

ROBOT="java -jar $HOME/robot.jar"

echo "merging pmdco"
$ROBOT merge --catalog ../src/ontology/catalog-v001.xml --input ../../pmdco-edit.owl --output merged-pmdco.ttl

python koncludix.py $KONCLUDE_BIN merged-pmdco.ttl inferences.owl

echo "merging with inferences"

## merge and reduce 
$ROBOT merge --input ../../pmdco-edit.owl --input inferences.owl reduce --reasoner ELK --output reasoned.owl
