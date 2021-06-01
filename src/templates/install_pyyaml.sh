#!/bin/bash

PYYAML_VERSION=PyYAML-5.3.1

PWD=`pwd`

wget http://pyyaml.org/download/pyyaml/${PYYAML_VERSION}.tar.gz
tar -xzvf ${PYYAML_VERSION}.tar.gz -C /tmp/
cd /tmp/${PYYAML_VERSION}
/srv/jobbergate-cli-venv/bin/python3 setup.py install
cd ${PWD}
rm -rf /tmp/${PYYAML_VERSION}