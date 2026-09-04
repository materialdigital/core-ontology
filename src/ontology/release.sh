VERSION=3.1.1
PRIOR_VERSION=3.1.0
ONTBASE=https://w3id.org/pmd/co/
ANNOTATE_ONTOLOGY_VERSION="annotate -V $ONTBASE$VERSION/\$@ --annotation owl:versionInfo $VERSION"


sh run.sh make clean

sh run.sh make VERSION=$VERSION ONTBASE=$ONTBASE ANNOTATE_ONTOLOGY_VERSION="$ANNOTATE_ONTOLOGY_VERSION" prepare_release

sh run.sh make VERSION=$VERSION PRIOR_VERSION=$PRIOR_VERSION update-ontology-annotations

sh utils/generate-auto-shapes.sh

# refresh imports etc. 
sh run.sh make -B 