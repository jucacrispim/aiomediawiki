#!/bin/bash

pylint aiomediawiki
srcout=$?

flake8 --select F tests

testsout=$?

if [ $srcout != "0" ]
then
    exit 1
fi

if [ $testsout != "0" ]
then
    exit 1
fi

exit 0
