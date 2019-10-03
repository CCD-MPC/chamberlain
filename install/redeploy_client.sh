#!/bin/bash

oc delete cm swift-auth
oc delete cm dataverse-auth

python3 install_script.py --swift=True --dv=True --client_install=True