#!/bin/bash

PYYAML_VERSION=PyYAML-5.3.1
URL=http://pyyaml.org/download/pyyaml/${PYYAML_VERSION}.tar.gz

/srv/jobbergate-cli-venv/bin/python3 -m pip install $URL
