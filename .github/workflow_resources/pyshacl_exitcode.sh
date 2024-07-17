#!/bin/bash
## Treat the exit codes from pyshacl to assure that gitlab-ci is still continuing if the graph is non conformant.
## USAGE: python3 -m pyshacl ... ; bash pyshacl_exitcode.sh $?
##
## pyshacl can terminate using four different exit codes
##  0: DataGraph is Conformant
##  1: DataGraph is Non-Conformant
##  2: The validator encountered a RuntimeError (check stderr output for details)
##  3: Not-Implemented; The validator encountered a SHACL feature that is not yet implemented.
## This script writes the meaning of each exit code to stdout and terminates with 0 in case pyshacl
## terminated with 0 or 1 or with 1 if pyshacl terminated with 2 or 3 (or if anything else was passed
## as argument)
if [ $1 -eq 0 ]
then
    echo "pyshacl exited with exit code 0: DataGraph is Conformant"
    exit 0
fi
if [ $1 -eq 1 ]
then
    echo "pyshacl exited with exit code 1: DataGraph is Non-Conformant"
    exit 0
fi
if [ $1 -eq 2 ]
then
    echo "pyshacl exited with exit code 2: The validator encountered a RuntimeError (check stderr output for details)"
    exit 1
fi
if [ $1 -eq 3 ]
then
    echo "pyshacl exited with exit code 3: Not-Implemented; The validator encountered a SHACL feature that is not yet implemented."
    exit 1
fi
echo "Encountered unknown pyshacl exit code."
exit 1